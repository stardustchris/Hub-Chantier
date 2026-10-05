"""Tests de la synchronisation des heures validees vers la paie externe."""

from datetime import date, time
from typing import Optional
from unittest.mock import Mock

import pytest

from modules.pointages.application.ports import ClientPaieExternePort, ErreurPaieExterne
from modules.pointages.application.use_cases.synchroniser_heures_paie import (
    SynchroniserHeuresPaieUseCase,
)
from modules.pointages.domain.entities import (
    Pointage,
    SynchronisationPaie,
    StatutSynchronisation,
)
from modules.pointages.domain.repositories import (
    CorrespondanceExterneRepository,
    SynchronisationPaieRepository,
)
from modules.pointages.domain.services import HorairesReference
from modules.pointages.domain.value_objects import Duree, StatutPointage

HORAIRES = HorairesReference(time(8, 0), time(12, 0), time(13, 0))
UTILISATEUR, CHANTIER = "utilisateur", "chantier"


# --- Doublures ---------------------------------------------------------------

class SuivisEnMemoire(SynchronisationPaieRepository):
    def __init__(self):
        self.suivis: dict[int, SynchronisationPaie] = {}

    def find_by_pointage_id(self, pointage_id: int) -> Optional[SynchronisationPaie]:
        return self.suivis.get(pointage_id)

    def save(self, synchronisation: SynchronisationPaie) -> SynchronisationPaie:
        self.suivis[synchronisation.pointage_id] = synchronisation
        return synchronisation

    def find_by_statuts(self, statuts):
        return [s for s in self.suivis.values() if s.statut in statuts]


class CorrespondancesEnMemoire(CorrespondanceExterneRepository):
    def __init__(self, correspondances: dict):
        self.correspondances = correspondances

    def get_identifiant_externe(self, type_entite, entite_id):
        return self.correspondances.get((type_entite, entite_id))

    def definir(self, type_entite, entite_id, identifiant_externe):
        self.correspondances[(type_entite, entite_id)] = identifiant_externe

    def supprimer(self, type_entite, entite_id):
        self.correspondances.pop((type_entite, entite_id), None)

    def lister(self):
        return [(t, i, e) for (t, i), e in self.correspondances.items()]


class ClientFactice(ClientPaieExternePort):
    """Enregistre les appels ; peut echouer au n-ieme appel de creation (une fois)."""

    def __init__(self, echec_a_la_creation: Optional[int] = None):
        self.creations: list[dict] = []
        self.suppressions: list[str] = []
        self.echec_a_la_creation = echec_a_la_creation
        self.appels_creation = 0

    def creer_saisie_travail(self, utilisateur_externe_id, chantier_externe_id, jour, debut, fin, notes):
        self.appels_creation += 1
        if self.appels_creation == self.echec_a_la_creation:
            raise ErreurPaieExterne("Costructor injoignable")
        self.creations.append(
            {"user": utilisateur_externe_id, "project": chantier_externe_id, "day": jour,
             "start": debut.strftime("%H:%M"), "end": fin.strftime("%H:%M"), "notes": notes}
        )
        return f"tse_{len(self.creations)}"

    def supprimer_saisie(self, saisie_id):
        self.suppressions.append(saisie_id)


# --- Fabrique ------------------------------------------------------------------

def _pointage(pid=10, heures=Duree(7, 0), sup=Duree(0, 0), statut=StatutPointage.VALIDE,
              utilisateur_id=1, chantier_id=5):
    return Pointage(
        id=pid, utilisateur_id=utilisateur_id, chantier_id=chantier_id,
        date_pointage=date(2026, 10, 5), heures_normales=heures,
        heures_supplementaires=sup, statut=statut,
    )


@pytest.fixture
def contexte():
    pointages = {}
    pointage_repo = Mock()
    pointage_repo.find_by_id.side_effect = lambda pid: pointages.get(pid)
    suivis = SuivisEnMemoire()
    correspondances = CorrespondancesEnMemoire(
        {(UTILISATEUR, 1): "usr_christophe", (CHANTIER, 5): "pj_brides"}
    )
    client = ClientFactice()

    def construire(client_utilise=None):
        return SynchroniserHeuresPaieUseCase(
            pointage_repo, suivis, correspondances, client_utilise or client, HORAIRES
        )

    return pointages, suivis, correspondances, client, construire


# --- Tests -----------------------------------------------------------------------

class TestEnvoi:
    def test_journee_de_7h_envoyee_en_deux_creneaux(self, contexte):
        pointages, suivis, _, client, construire = contexte
        pointages[10] = _pointage()

        rapport = construire().execute([10])

        assert rapport.envoyes == [10]
        assert [(c["start"], c["end"]) for c in client.creations] == [
            ("08:00", "12:00"), ("13:00", "16:00"),
        ]
        assert all(c["user"] == "usr_christophe" and c["project"] == "pj_brides"
                   for c in client.creations)
        suivi = suivis.find_by_pointage_id(10)
        assert suivi.statut == StatutSynchronisation.ENVOYE
        assert suivi.saisies_externes == ["tse_1", "tse_2"]

    def test_heures_sup_incluses_dans_le_total_sans_etre_qualifiees(self, contexte):
        """Les heures sup se declenchent au-dela de 35h/semaine : c'est a la paie de
        les calculer, une journee ne doit donc pas etre etiquetee « sup »."""
        pointages, _, _, client, construire = contexte
        pointages[10] = _pointage(heures=Duree(7, 0), sup=Duree(1, 30))

        construire().execute([10])

        assert client.creations[-1]["end"] == "17:30"  # 8h30 au total
        assert "sup" not in client.creations[0]["notes"]

    def test_note_identifie_le_pointage(self, contexte):
        pointages, _, _, client, construire = contexte
        pointages[10] = _pointage()

        construire().execute([10])

        assert "Hub Chantier" in client.creations[0]["notes"]
        assert "#10" in client.creations[0]["notes"]


class TestAntiDoublon:
    def test_pointage_deja_envoye_n_est_jamais_renvoye(self, contexte):
        pointages, _, _, client, construire = contexte
        pointages[10] = _pointage()
        use_case = construire()

        use_case.execute([10])
        rapport = use_case.execute([10])

        assert rapport.deja_envoyes == [10]
        assert len(client.creations) == 2  # pas de second envoi

    def test_envoi_partiel_nettoye_avant_relance(self, contexte):
        """Echec au 2e creneau : le 1er est supprime avant le nouvel envoi."""
        pointages, suivis, _, _, construire = contexte
        pointages[10] = _pointage()
        client_en_panne = ClientFactice(echec_a_la_creation=2)

        rapport = construire(client_en_panne).execute([10])

        assert rapport.erreurs == [10]
        suivi = suivis.find_by_pointage_id(10)
        assert suivi.statut == StatutSynchronisation.ERREUR
        assert suivi.saisies_externes == ["tse_1"]  # creee avant la panne

        client_retabli = ClientFactice()
        rapport = construire(client_retabli).execute([10])

        assert client_retabli.suppressions == ["tse_1"]
        assert rapport.envoyes == [10]
        assert suivis.find_by_pointage_id(10).tentatives == 2


class TestCasIgnores:
    def test_pointage_non_valide_n_est_pas_envoye(self, contexte):
        pointages, suivis, _, client, construire = contexte
        pointages[10] = _pointage(statut=StatutPointage.SOUMIS)

        rapport = construire().execute([10])

        assert rapport.non_valides == [10]
        assert client.creations == []
        assert suivis.find_by_pointage_id(10) is None

    def test_compagnon_sans_correspondance_ignore(self, contexte):
        pointages, suivis, _, client, construire = contexte
        pointages[10] = _pointage(utilisateur_id=99)

        rapport = construire().execute([10])

        assert rapport.ignores == [10]
        assert client.creations == []
        assert "compagnon" in suivis.find_by_pointage_id(10).message

    def test_chantier_sans_correspondance_ignore(self, contexte):
        pointages, suivis, _, _, construire = contexte
        pointages[10] = _pointage(chantier_id=99)

        construire().execute([10])

        assert "chantier" in suivis.find_by_pointage_id(10).message

    def test_journee_sans_heures_ignoree(self, contexte):
        pointages, _, _, client, construire = contexte
        pointages[10] = _pointage(heures=Duree(0, 0))

        rapport = construire().execute([10])

        assert rapport.ignores == [10]
        assert client.creations == []

    def test_duree_impossible_a_placer_ignoree(self, contexte):
        pointages, suivis, _, client, construire = contexte
        pointages[10] = _pointage(heures=Duree(16, 0))

        rapport = construire().execute([10])

        assert rapport.ignores == [10]
        assert client.creations == []
        assert "minuit" in suivis.find_by_pointage_id(10).message


class TestRelance:
    def test_relance_les_erreurs_et_les_ignores(self, contexte):
        pointages, _, correspondances, _, construire = contexte
        pointages[10] = _pointage(utilisateur_id=99)  # ignore : correspondance manquante
        construire().execute([10])

        correspondances.definir(UTILISATEUR, 99, "usr_nouveau")
        client = ClientFactice()
        rapport = construire(client).relancer()

        assert rapport.envoyes == [10]
        assert client.creations[0]["user"] == "usr_nouveau"

    def test_un_echec_n_interrompt_pas_le_lot(self, contexte):
        pointages, _, _, _, construire = contexte
        pointages[10] = _pointage(pid=10)
        pointages[11] = _pointage(pid=11)
        client = ClientFactice(echec_a_la_creation=1)

        rapport = construire(client).execute([10, 11])

        assert rapport.erreurs == [10]
        assert rapport.envoyes == [11]
