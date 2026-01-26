"""Tests unitaires pour SQLAlchemySignalementRepository."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from modules.signalements.infrastructure.persistence.sqlalchemy_signalement_repository import (
    SQLAlchemySignalementRepository,
)
from modules.signalements.domain.entities import Signalement
from modules.signalements.domain.value_objects import Priorite, StatutSignalement


class TestSQLAlchemySignalementRepository:
    """Tests pour SQLAlchemySignalementRepository."""

    @pytest.fixture
    def mock_session(self):
        """Session SQLAlchemy mock."""
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        session.first.return_value = None
        session.all.return_value = []
        session.count.return_value = 0
        return session

    @pytest.fixture
    def repository(self, mock_session):
        """Instance du repository."""
        return SQLAlchemySignalementRepository(mock_session)


class TestFindById:
    """Tests pour find_by_id."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemySignalementRepository(mock_session)

    def test_trouve_signalement_existant(self, repository, mock_session):
        """Trouve un signalement existant par ID."""
        mock_model = Mock()
        mock_model.id = 1
        mock_model.chantier_id = 10
        mock_model.titre = "Probleme securite"
        mock_model.description = "Description du probleme"
        mock_model.priorite = "haute"
        mock_model.statut = "ouvert"
        mock_model.cree_par = 5
        mock_model.assigne_a = 6
        mock_model.date_resolution_souhaitee = datetime.now() + timedelta(days=2)
        mock_model.date_traitement = None
        mock_model.date_cloture = None
        mock_model.commentaire_traitement = None
        mock_model.photo_url = None
        mock_model.localisation = "Zone A"
        mock_model.nb_escalades = 0
        mock_model.derniere_escalade_at = None
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        mock_session.first.return_value = mock_model

        result = repository.find_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.titre == "Probleme securite"
        assert result.priorite == Priorite.HAUTE
        assert result.statut == StatutSignalement.OUVERT

    def test_retourne_none_si_non_trouve(self, repository, mock_session):
        """Retourne None si signalement non trouve."""
        mock_session.first.return_value = None

        result = repository.find_by_id(999)
        assert result is None


class TestSave:
    """Tests pour save."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemySignalementRepository(mock_session)

    def test_cree_nouveau_signalement(self, repository, mock_session):
        """Cree un nouveau signalement."""
        signalement = Signalement(
            id=None,
            chantier_id=10,
            titre="Nouveau signalement",
            description="Description",
            priorite=Priorite.MOYENNE,
            statut=StatutSignalement.OUVERT,
            cree_par=5,
        )

        mock_model = Mock()
        mock_model.id = 42

        def refresh_side_effect(model):
            signalement.id = 42

        mock_session.refresh = refresh_side_effect

        with patch(
            "modules.signalements.infrastructure.persistence.sqlalchemy_signalement_repository.SignalementModel"
        ) as MockModel:
            MockModel.return_value = mock_model
            result = repository.save(signalement)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_met_a_jour_signalement_existant(self, repository, mock_session):
        """Met a jour un signalement existant."""
        signalement = Signalement(
            id=42,
            chantier_id=10,
            titre="Signalement mis a jour",
            description="Nouvelle description",
            priorite=Priorite.HAUTE,
            statut=StatutSignalement.EN_COURS,
            cree_par=5,
            assigne_a=6,
        )

        mock_model = Mock()
        mock_model.id = 42

        mock_session.first.return_value = mock_model

        result = repository.save(signalement)

        mock_session.commit.assert_called_once()
        assert mock_model.titre == "Signalement mis a jour"
        assert mock_model.priorite == "haute"
        assert mock_model.statut == "en_cours"


class TestDelete:
    """Tests pour delete."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemySignalementRepository(mock_session)

    def test_supprime_signalement_existant(self, repository, mock_session):
        """Supprime un signalement existant."""
        mock_session.delete.return_value = 1

        result = repository.delete(1)

        assert result is True
        mock_session.commit.assert_called_once()

    def test_retourne_false_si_non_trouve(self, repository, mock_session):
        """Retourne False si signalement non trouve."""
        mock_session.delete.return_value = 0

        result = repository.delete(999)

        assert result is False


class TestFindByChantier:
    """Tests pour find_by_chantier."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        session.order_by.return_value = session
        session.offset.return_value = session
        session.limit.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemySignalementRepository(mock_session)

    def test_trouve_signalements_chantier(self, repository, mock_session):
        """Trouve les signalements d'un chantier."""
        mock_model = Mock()
        mock_model.id = 1
        mock_model.chantier_id = 10
        mock_model.titre = "Test"
        mock_model.description = "Desc"
        mock_model.priorite = "moyenne"
        mock_model.statut = "ouvert"
        mock_model.cree_par = 5
        mock_model.assigne_a = None
        mock_model.date_resolution_souhaitee = None
        mock_model.date_traitement = None
        mock_model.date_cloture = None
        mock_model.commentaire_traitement = None
        mock_model.photo_url = None
        mock_model.localisation = None
        mock_model.nb_escalades = 0
        mock_model.derniere_escalade_at = None
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        mock_session.all.return_value = [mock_model]

        result = repository.find_by_chantier(10)

        assert len(result) == 1

    def test_filtre_par_statut(self, repository, mock_session):
        """Filtre par statut."""
        mock_session.all.return_value = []

        result = repository.find_by_chantier(10, statut=StatutSignalement.EN_COURS)

        # Verifie que le filtre est applique
        mock_session.filter.assert_called()

    def test_filtre_par_priorite(self, repository, mock_session):
        """Filtre par priorite."""
        mock_session.all.return_value = []

        result = repository.find_by_chantier(10, priorite=Priorite.CRITIQUE)

        mock_session.filter.assert_called()

    def test_pagination(self, repository, mock_session):
        """Gere la pagination."""
        mock_session.all.return_value = []

        result = repository.find_by_chantier(10, skip=20, limit=10)

        mock_session.offset.assert_called_with(20)
        mock_session.limit.assert_called_with(10)


class TestFindAll:
    """Tests pour find_all."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        session.order_by.return_value = session
        session.offset.return_value = session
        session.limit.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemySignalementRepository(mock_session)

    def test_trouve_tous_signalements(self, repository, mock_session):
        """Trouve tous les signalements avec total."""
        mock_session.count.return_value = 50
        mock_session.all.return_value = []

        signalements, total = repository.find_all()

        assert total == 50

    def test_filtre_par_chantier_ids(self, repository, mock_session):
        """Filtre par liste de chantier_ids."""
        mock_session.count.return_value = 10
        mock_session.all.return_value = []

        signalements, total = repository.find_all(chantier_ids=[1, 2, 3])

        mock_session.filter.assert_called()

    def test_filtre_par_dates(self, repository, mock_session):
        """Filtre par plage de dates."""
        mock_session.count.return_value = 5
        mock_session.all.return_value = []

        date_debut = datetime.now() - timedelta(days=30)
        date_fin = datetime.now()

        signalements, total = repository.find_all(
            date_debut=date_debut, date_fin=date_fin
        )

        assert mock_session.filter.call_count >= 1


class TestFindByCreateur:
    """Tests pour find_by_createur."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        session.order_by.return_value = session
        session.offset.return_value = session
        session.limit.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemySignalementRepository(mock_session)

    def test_trouve_signalements_createur(self, repository, mock_session):
        """Trouve les signalements crees par un utilisateur."""
        mock_session.all.return_value = []

        result = repository.find_by_createur(5)

        # Le filtre cree_par est applique
        mock_session.filter.assert_called()


class TestFindAssignesA:
    """Tests pour find_assignes_a."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        session.order_by.return_value = session
        session.offset.return_value = session
        session.limit.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemySignalementRepository(mock_session)

    def test_trouve_signalements_assignes(self, repository, mock_session):
        """Trouve les signalements assignes a un utilisateur."""
        mock_session.all.return_value = []

        result = repository.find_assignes_a(6)

        mock_session.filter.assert_called()


class TestCountByChantier:
    """Tests pour count_by_chantier."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemySignalementRepository(mock_session)

    def test_compte_signalements_chantier(self, repository, mock_session):
        """Compte les signalements d'un chantier."""
        mock_session.scalar.return_value = 15

        result = repository.count_by_chantier(10)

        assert result == 15

    def test_compte_avec_filtres(self, repository, mock_session):
        """Compte avec filtres statut et priorite."""
        mock_session.scalar.return_value = 3

        result = repository.count_by_chantier(
            10, statut=StatutSignalement.OUVERT, priorite=Priorite.HAUTE
        )

        assert result == 3


class TestCountByStatut:
    """Tests pour count_by_statut."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        session.group_by.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemySignalementRepository(mock_session)

    def test_compte_par_statut(self, repository, mock_session):
        """Compte les signalements par statut."""
        mock_session.all.return_value = [
            ("ouvert", 10),
            ("en_cours", 5),
            ("traite", 20),
        ]

        result = repository.count_by_statut()

        assert result["ouvert"] == 10
        assert result["en_cours"] == 5
        assert result["traite"] == 20

    def test_compte_par_statut_chantier(self, repository, mock_session):
        """Compte par statut pour un chantier specifique."""
        mock_session.all.return_value = [("ouvert", 3)]

        result = repository.count_by_statut(chantier_id=10)

        assert result["ouvert"] == 3
        mock_session.filter.assert_called()


class TestCountByPriorite:
    """Tests pour count_by_priorite."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        session.group_by.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemySignalementRepository(mock_session)

    def test_compte_par_priorite(self, repository, mock_session):
        """Compte les signalements par priorite."""
        mock_session.all.return_value = [
            ("critique", 2),
            ("haute", 5),
            ("moyenne", 15),
            ("basse", 8),
        ]

        result = repository.count_by_priorite()

        assert result["critique"] == 2
        assert result["haute"] == 5
        assert result["moyenne"] == 15
        assert result["basse"] == 8


class TestFindEnRetard:
    """Tests pour find_en_retard."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        session.order_by.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemySignalementRepository(mock_session)

    def test_trouve_signalements_en_retard(self, repository, mock_session):
        """Trouve les signalements en retard."""
        mock_model = Mock()
        mock_model.id = 1
        mock_model.chantier_id = 10
        mock_model.titre = "Test"
        mock_model.description = "Desc"
        mock_model.priorite = "haute"
        mock_model.statut = "ouvert"
        mock_model.cree_par = 5
        mock_model.assigne_a = None
        mock_model.date_resolution_souhaitee = datetime.now() - timedelta(days=1)  # Passe
        mock_model.date_traitement = None
        mock_model.date_cloture = None
        mock_model.commentaire_traitement = None
        mock_model.photo_url = None
        mock_model.localisation = None
        mock_model.nb_escalades = 0
        mock_model.derniere_escalade_at = None
        mock_model.created_at = datetime.now() - timedelta(days=5)
        mock_model.updated_at = datetime.now()

        mock_session.all.return_value = [mock_model]

        # Mock est_en_retard sur l'entite
        with patch.object(Signalement, "est_en_retard", True):
            result = repository.find_en_retard(chantier_id=10)

        # Le filtre statut in est applique
        mock_session.filter.assert_called()


class TestFindAEscalader:
    """Tests pour find_a_escalader."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemySignalementRepository(mock_session)

    def test_trouve_signalements_a_escalader(self, repository, mock_session):
        """Trouve les signalements necessitant escalade."""
        mock_model = Mock()
        mock_model.id = 1
        mock_model.chantier_id = 10
        mock_model.titre = "Test"
        mock_model.description = "Desc"
        mock_model.priorite = "haute"
        mock_model.statut = "ouvert"
        mock_model.cree_par = 5
        mock_model.assigne_a = None
        mock_model.date_resolution_souhaitee = datetime.now() - timedelta(hours=2)
        mock_model.date_traitement = None
        mock_model.date_cloture = None
        mock_model.commentaire_traitement = None
        mock_model.photo_url = None
        mock_model.localisation = None
        mock_model.nb_escalades = 0
        mock_model.derniere_escalade_at = None
        mock_model.created_at = datetime.now() - timedelta(hours=10)
        mock_model.updated_at = datetime.now()

        mock_session.all.return_value = [mock_model]

        with patch.object(Signalement, "pourcentage_temps_ecoule", 60.0):
            result = repository.find_a_escalader(seuil_pourcentage=50.0)

        mock_session.filter.assert_called()


class TestSearch:
    """Tests pour search."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        session.order_by.return_value = session
        session.offset.return_value = session
        session.limit.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemySignalementRepository(mock_session)

    def test_recherche_par_texte(self, repository, mock_session):
        """Recherche par texte dans titre, description, localisation."""
        mock_session.count.return_value = 5
        mock_session.all.return_value = []

        signalements, total = repository.search("securite")

        assert total == 5
        mock_session.filter.assert_called()

    def test_recherche_avec_chantier_id(self, repository, mock_session):
        """Recherche limitee a un chantier."""
        mock_session.count.return_value = 2
        mock_session.all.return_value = []

        signalements, total = repository.search("panne", chantier_id=10)

        assert total == 2


class TestGetStatistiques:
    """Tests pour get_statistiques."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemySignalementRepository(mock_session)

    def test_calcule_statistiques(self, repository, mock_session):
        """Calcule les statistiques des signalements."""
        mock_model1 = Mock()
        mock_model1.statut = "ouvert"
        mock_model1.priorite = "haute"
        mock_model1.date_traitement = None
        mock_model1.created_at = datetime.now() - timedelta(days=1)
        mock_model1.id = 1
        mock_model1.chantier_id = 10
        mock_model1.titre = "Test1"
        mock_model1.description = "Desc"
        mock_model1.cree_par = 5
        mock_model1.assigne_a = None
        mock_model1.date_resolution_souhaitee = datetime.now() - timedelta(hours=1)
        mock_model1.date_cloture = None
        mock_model1.commentaire_traitement = None
        mock_model1.photo_url = None
        mock_model1.localisation = None
        mock_model1.nb_escalades = 0
        mock_model1.derniere_escalade_at = None
        mock_model1.updated_at = datetime.now()

        mock_model2 = Mock()
        mock_model2.statut = "traite"
        mock_model2.priorite = "moyenne"
        mock_model2.date_traitement = datetime.now()
        mock_model2.created_at = datetime.now() - timedelta(days=2)
        mock_model2.id = 2
        mock_model2.chantier_id = 10
        mock_model2.titre = "Test2"
        mock_model2.description = "Desc"
        mock_model2.cree_par = 5
        mock_model2.assigne_a = None
        mock_model2.date_resolution_souhaitee = datetime.now() + timedelta(days=1)
        mock_model2.date_cloture = None
        mock_model2.commentaire_traitement = None
        mock_model2.photo_url = None
        mock_model2.localisation = None
        mock_model2.nb_escalades = 0
        mock_model2.derniere_escalade_at = None
        mock_model2.updated_at = datetime.now()

        mock_session.all.return_value = [mock_model1, mock_model2]

        with patch.object(Signalement, "est_en_retard", True):
            stats = repository.get_statistiques(chantier_id=10)

        assert stats["total"] == 2
        assert "par_statut" in stats
        assert "par_priorite" in stats
        assert "taux_resolution" in stats

    def test_statistiques_vides(self, repository, mock_session):
        """Statistiques pour liste vide."""
        mock_session.all.return_value = []

        stats = repository.get_statistiques()

        assert stats["total"] == 0
        assert stats["taux_resolution"] == 0.0
