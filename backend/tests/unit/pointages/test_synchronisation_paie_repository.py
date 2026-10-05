"""Tests aller-retour des depots de synchronisation paie (SQLite en memoire)."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from modules.pointages.domain.entities import SynchronisationPaie, StatutSynchronisation
from modules.pointages.infrastructure.persistence import (
    CorrespondancePaieExterneModel,
    SQLAlchemyCorrespondanceExterneRepository,
    SQLAlchemySynchronisationPaieRepository,
    SynchronisationPaieModel,
)
from shared.infrastructure.database_base import Base


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[SynchronisationPaieModel.__table__, CorrespondancePaieExterneModel.__table__],
    )
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


class TestSuiviDesEnvois:
    def test_aller_retour_avec_les_saisies_externes(self, session):
        repo = SQLAlchemySynchronisationPaieRepository(session)
        suivi = SynchronisationPaie(pointage_id=10, statut=StatutSynchronisation.ERREUR)
        suivi.enregistrer_tentative(StatutSynchronisation.ENVOYE, ["tse_1", "tse_2"])

        repo.save(suivi)
        relu = repo.find_by_pointage_id(10)

        assert relu.statut == StatutSynchronisation.ENVOYE
        assert relu.saisies_externes == ["tse_1", "tse_2"]
        assert relu.tentatives == 1
        assert relu.derniere_tentative is not None

    def test_un_seul_suivi_par_pointage(self, session):
        repo = SQLAlchemySynchronisationPaieRepository(session)
        suivi = SynchronisationPaie(pointage_id=10, statut=StatutSynchronisation.ERREUR)
        suivi.enregistrer_tentative(StatutSynchronisation.ERREUR, ["tse_1"], "panne")
        repo.save(suivi)

        suivi.enregistrer_tentative(StatutSynchronisation.ENVOYE, ["tse_3", "tse_4"])
        repo.save(suivi)

        assert session.query(SynchronisationPaieModel).count() == 1
        relu = repo.find_by_pointage_id(10)
        assert relu.saisies_externes == ["tse_3", "tse_4"]
        assert relu.tentatives == 2

    def test_pointage_jamais_envoye(self, session):
        assert SQLAlchemySynchronisationPaieRepository(session).find_by_pointage_id(99) is None

    def test_filtre_par_statut(self, session):
        repo = SQLAlchemySynchronisationPaieRepository(session)
        for pid, statut in ((1, StatutSynchronisation.ENVOYE), (2, StatutSynchronisation.ERREUR),
                            (3, StatutSynchronisation.IGNORE)):
            suivi = SynchronisationPaie(pointage_id=pid, statut=statut)
            suivi.enregistrer_tentative(statut, [])
            repo.save(suivi)

        a_relancer = repo.find_by_statuts(
            [StatutSynchronisation.ERREUR, StatutSynchronisation.IGNORE]
        )
        assert [s.pointage_id for s in a_relancer] == [2, 3]


class TestCorrespondances:
    def test_definir_lire_remplacer_supprimer(self, session):
        repo = SQLAlchemyCorrespondanceExterneRepository(session)

        repo.definir("utilisateur", 1, "usr_ancien")
        repo.definir("utilisateur", 1, "usr_nouveau")
        assert repo.get_identifiant_externe("utilisateur", 1) == "usr_nouveau"
        assert session.query(CorrespondancePaieExterneModel).count() == 1

        repo.supprimer("utilisateur", 1)
        assert repo.get_identifiant_externe("utilisateur", 1) is None

    def test_utilisateur_et_chantier_de_meme_id_distincts(self, session):
        repo = SQLAlchemyCorrespondanceExterneRepository(session)
        repo.definir("utilisateur", 5, "usr_5")
        repo.definir("chantier", 5, "pj_5")

        assert repo.get_identifiant_externe("utilisateur", 5) == "usr_5"
        assert repo.get_identifiant_externe("chantier", 5) == "pj_5"
        assert repo.lister() == [("chantier", 5, "pj_5"), ("utilisateur", 5, "usr_5")]

    def test_systemes_isoles(self, session):
        """Une correspondance Graneet ne doit pas servir pour Costructor."""
        SQLAlchemyCorrespondanceExterneRepository(session, systeme="graneet").definir(
            "utilisateur", 1, "graneet_1"
        )
        costructor = SQLAlchemyCorrespondanceExterneRepository(session)
        assert costructor.get_identifiant_externe("utilisateur", 1) is None
