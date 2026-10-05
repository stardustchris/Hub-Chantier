"""Tests des routes d'administration de la synchronisation paie externe."""

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from modules.pointages.application.use_cases import RapportSynchronisation
from modules.pointages.domain.entities import StatutSynchronisation, SynchronisationPaie
from modules.pointages.infrastructure.paie_externe import synchronisation
from modules.pointages.infrastructure.persistence import (
    CorrespondancePaieExterneModel,
    SQLAlchemySynchronisationPaieRepository,
    SynchronisationPaieModel,
)
from modules.pointages.infrastructure.web import paie_externe_routes as routes
from shared.infrastructure.database_base import Base


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[SynchronisationPaieModel.__table__, CorrespondancePaieExterneModel.__table__],
    )
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def _activer(monkeypatch, actif=True):
    monkeypatch.setattr(synchronisation, "synchronisation_active", lambda: actif)


class TestControleDesRoles:
    @pytest.mark.parametrize("role", ["compagnon", "chef_chantier"])
    def test_statut_et_envois_reserves_admin_conducteur(self, role, db):
        for appel in (
            lambda: routes.statut_synchronisation(user_role=role),
            lambda: routes.lister_synchronisations(statut=None, user_role=role, db=db),
            lambda: routes.relancer_synchronisations(user_role=role),
            lambda: routes.envoyer_pointages(
                request=routes.EnvoiRequest(pointage_ids=[1]), user_role=role
            ),
        ):
            with pytest.raises(HTTPException) as exc:
                appel()
            assert exc.value.status_code == 403

    @pytest.mark.parametrize("role", ["conducteur", "chef_chantier", "compagnon"])
    def test_correspondances_reservees_admin(self, role, db):
        requete = routes.CorrespondanceRequest(
            type_entite="utilisateur", entite_id=1, identifiant_externe="usr_1"
        )
        for appel in (
            lambda: routes.lister_correspondances(user_role=role, db=db),
            lambda: routes.definir_correspondance(request=requete, user_role=role, db=db),
            lambda: routes.supprimer_correspondance(
                type_entite="utilisateur", entite_id=1, user_role=role, db=db
            ),
        ):
            with pytest.raises(HTTPException) as exc:
                appel()
            assert exc.value.status_code == 403


class TestStatutEtSuivis:
    def test_statut_sans_exposer_la_cle(self, monkeypatch):
        _activer(monkeypatch)

        reponse = routes.statut_synchronisation(user_role="conducteur")

        assert reponse["active"] is True
        assert reponse["horaires"]["pause_debut"]
        assert "cle" not in str(reponse).lower() and "key" not in str(reponse).lower()

    def test_lister_et_filtrer_les_suivis(self, db):
        repo = SQLAlchemySynchronisationPaieRepository(db)
        for pid, statut in ((1, StatutSynchronisation.ENVOYE), (2, StatutSynchronisation.ERREUR)):
            suivi = SynchronisationPaie(pointage_id=pid, statut=statut)
            suivi.enregistrer_tentative(statut, ["tse_x"] if pid == 1 else [], "panne" if pid == 2 else None)
            repo.save(suivi)

        tous = routes.lister_synchronisations(statut=None, user_role="admin", db=db)
        erreurs = routes.lister_synchronisations(statut="erreur", user_role="admin", db=db)

        assert [s["pointage_id"] for s in tous] == [1, 2]
        assert erreurs == [{
            "pointage_id": 2, "statut": "erreur", "saisies_externes": [],
            "message": "panne", "tentatives": 1,
            "derniere_tentative": erreurs[0]["derniere_tentative"],
        }]


class TestEnvois:
    def test_relance_refusee_si_synchronisation_inactive(self, monkeypatch):
        _activer(monkeypatch, actif=False)

        with pytest.raises(HTTPException) as exc:
            routes.relancer_synchronisations(user_role="admin")
        assert exc.value.status_code == 409

    def test_envoi_refuse_si_synchronisation_inactive(self, monkeypatch):
        _activer(monkeypatch, actif=False)

        with pytest.raises(HTTPException) as exc:
            routes.envoyer_pointages(request=routes.EnvoiRequest(pointage_ids=[1]), user_role="admin")
        assert exc.value.status_code == 409

    def test_relance_renvoie_le_bilan(self, monkeypatch):
        _activer(monkeypatch)
        appels = []
        monkeypatch.setattr(
            synchronisation, "synchroniser",
            lambda ids: appels.append(ids) or RapportSynchronisation(envoyes=[3], ignores=[4]),
        )

        bilan = routes.relancer_synchronisations(user_role="conducteur")

        assert appels == [None]  # None = relancer erreurs et ignores
        assert bilan["envoyes"] == [3] and bilan["ignores"] == [4]

    def test_envoi_explicite_des_pointages_donnes(self, monkeypatch):
        _activer(monkeypatch)
        appels = []
        monkeypatch.setattr(
            synchronisation, "synchroniser",
            lambda ids: appels.append(ids) or RapportSynchronisation(deja_envoyes=ids),
        )

        bilan = routes.envoyer_pointages(
            request=routes.EnvoiRequest(pointage_ids=[7, 8]), user_role="admin"
        )

        assert appels == [[7, 8]]
        assert bilan["deja_envoyes"] == [7, 8]

    def test_liste_vide_refusee(self):
        with pytest.raises(ValueError):
            routes.EnvoiRequest(pointage_ids=[])


class TestCorrespondances:
    def test_definir_lister_supprimer(self, db):
        requete = routes.CorrespondanceRequest(
            type_entite="chantier", entite_id=5, identifiant_externe="  pj_brides  "
        )

        routes.definir_correspondance(request=requete, user_role="admin", db=db)
        assert routes.lister_correspondances(user_role="admin", db=db) == [
            {"type_entite": "chantier", "entite_id": 5, "identifiant_externe": "pj_brides"}
        ]

        routes.supprimer_correspondance(type_entite="chantier", entite_id=5, user_role="admin", db=db)
        assert routes.lister_correspondances(user_role="admin", db=db) == []

    def test_type_d_entite_inconnu_refuse(self):
        with pytest.raises(ValueError):
            routes.CorrespondanceRequest(type_entite="materiel", entite_id=1, identifiant_externe="x")
