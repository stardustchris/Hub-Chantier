"""Tests unitaires pour SQLAlchemyPointageRepository."""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from modules.pointages.infrastructure.persistence.sqlalchemy_pointage_repository import (
    SQLAlchemyPointageRepository,
)
from modules.pointages.domain.entities import Pointage
from modules.pointages.domain.value_objects import StatutPointage, Duree


class TestSQLAlchemyPointageRepository:
    """Tests pour SQLAlchemyPointageRepository."""

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
        return SQLAlchemyPointageRepository(mock_session)

    @pytest.fixture
    def sample_pointage(self):
        """Pointage de test."""
        return Pointage(
            id=None,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2024, 1, 15),
            heures_normales=Duree.from_hours(8),
            heures_supplementaires=Duree.from_hours(0),
            statut=StatutPointage.BROUILLON,
        )


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
        return SQLAlchemyPointageRepository(mock_session)

    def test_trouve_pointage_existant(self, repository, mock_session):
        """Trouve un pointage existant par ID."""
        mock_model = Mock()
        mock_model.id = 1
        mock_model.utilisateur_id = 10
        mock_model.chantier_id = 100
        mock_model.date_pointage = date(2024, 1, 15)
        mock_model.heures_normales_minutes = 480
        mock_model.heures_supplementaires_minutes = 60
        mock_model.statut = "brouillon"
        mock_model.commentaire = "Test"
        mock_model.signature_utilisateur = None
        mock_model.signature_date = None
        mock_model.validateur_id = None
        mock_model.validation_date = None
        mock_model.motif_rejet = None
        mock_model.affectation_id = None
        mock_model.created_by = 1
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        mock_session.first.return_value = mock_model

        result = repository.find_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.utilisateur_id == 10
        assert result.heures_normales.total_minutes == 480

    def test_retourne_none_si_non_trouve(self, repository, mock_session):
        """Retourne None si pointage non trouve."""
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
        return SQLAlchemyPointageRepository(mock_session)

    def test_cree_nouveau_pointage(self, repository, mock_session):
        """Cree un nouveau pointage."""
        pointage = Pointage(
            id=None,  # Nouveau
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2024, 1, 15),
            heures_normales=Duree.from_minutes(480),  # 8h
            heures_supplementaires=Duree.from_minutes(0),
            statut=StatutPointage.BROUILLON,
        )

        mock_model = Mock()
        mock_model.id = 42
        mock_model.utilisateur_id = 1
        mock_model.chantier_id = 10
        mock_model.date_pointage = date(2024, 1, 15)
        mock_model.heures_normales_minutes = 480
        mock_model.heures_supplementaires_minutes = 0
        mock_model.statut = "brouillon"
        mock_model.commentaire = None
        mock_model.signature_utilisateur = None
        mock_model.signature_date = None
        mock_model.validateur_id = None
        mock_model.validation_date = None
        mock_model.motif_rejet = None
        mock_model.affectation_id = None
        mock_model.created_by = None
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        # Mock pour que refresh retourne le model avec l'ID
        def refresh_side_effect(model):
            model.id = 42

        mock_session.refresh.side_effect = lambda m: None

        with patch(
            "modules.pointages.infrastructure.persistence.sqlalchemy_pointage_repository.PointageModel"
        ) as MockModel:
            MockModel.return_value = mock_model
            result = repository.save(pointage)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_met_a_jour_pointage_existant(self, repository, mock_session):
        """Met a jour un pointage existant."""
        pointage = Pointage(
            id=42,  # Existant
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2024, 1, 15),
            heures_normales=Duree.from_minutes(540),  # 9h
            heures_supplementaires=Duree.from_minutes(60),  # 1h
            statut=StatutPointage.SOUMIS,
        )

        mock_model = Mock()
        mock_model.id = 42
        mock_model.utilisateur_id = 1
        mock_model.chantier_id = 10
        mock_model.date_pointage = date(2024, 1, 15)
        mock_model.heures_normales_minutes = 480
        mock_model.heures_supplementaires_minutes = 0
        mock_model.statut = "brouillon"
        mock_model.commentaire = None
        mock_model.signature_utilisateur = None
        mock_model.signature_date = None
        mock_model.validateur_id = None
        mock_model.validation_date = None
        mock_model.motif_rejet = None
        mock_model.affectation_id = None
        mock_model.created_by = None
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        mock_session.first.return_value = mock_model

        result = repository.save(pointage)

        mock_session.commit.assert_called_once()
        # Verifie que les valeurs sont mises a jour
        assert mock_model.heures_normales_minutes == 540  # 9h
        assert mock_model.heures_supplementaires_minutes == 60  # 1h
        assert mock_model.statut == "soumis"


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
        return SQLAlchemyPointageRepository(mock_session)

    def test_supprime_pointage_existant(self, repository, mock_session):
        """Supprime un pointage existant."""
        mock_model = Mock()
        mock_session.first.return_value = mock_model

        result = repository.delete(1)

        assert result is True
        mock_session.delete.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()

    def test_retourne_false_si_non_trouve(self, repository, mock_session):
        """Retourne False si pointage non trouve."""
        mock_session.first.return_value = None

        result = repository.delete(999)

        assert result is False
        mock_session.delete.assert_not_called()


class TestFindByUtilisateurAndDate:
    """Tests pour find_by_utilisateur_and_date."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyPointageRepository(mock_session)

    def test_trouve_pointages_utilisateur_date(self, repository, mock_session):
        """Trouve les pointages d'un utilisateur pour une date."""
        mock_model = Mock()
        mock_model.id = 1
        mock_model.utilisateur_id = 10
        mock_model.chantier_id = 100
        mock_model.date_pointage = date(2024, 1, 15)
        mock_model.heures_normales_minutes = 480
        mock_model.heures_supplementaires_minutes = 0
        mock_model.statut = "brouillon"
        mock_model.commentaire = None
        mock_model.signature_utilisateur = None
        mock_model.signature_date = None
        mock_model.validateur_id = None
        mock_model.validation_date = None
        mock_model.motif_rejet = None
        mock_model.affectation_id = None
        mock_model.created_by = None
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        mock_session.all.return_value = [mock_model]

        result = repository.find_by_utilisateur_and_date(10, date(2024, 1, 15))

        assert len(result) == 1
        assert result[0].utilisateur_id == 10

    def test_retourne_liste_vide_si_rien(self, repository, mock_session):
        """Retourne liste vide si aucun pointage."""
        mock_session.all.return_value = []

        result = repository.find_by_utilisateur_and_date(10, date(2024, 1, 15))

        assert result == []


class TestFindByUtilisateurAndSemaine:
    """Tests pour find_by_utilisateur_and_semaine."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        session.order_by.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyPointageRepository(mock_session)

    def test_trouve_pointages_semaine(self, repository, mock_session):
        """Trouve les pointages d'une semaine."""
        mock_session.all.return_value = []

        result = repository.find_by_utilisateur_and_semaine(10, date(2024, 1, 15))

        assert result == []
        # Verifie que le filtre de semaine est applique (6 jours)
        mock_session.filter.assert_called()


class TestFindByChantierAndDate:
    """Tests pour find_by_chantier_and_date."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyPointageRepository(mock_session)

    def test_trouve_pointages_chantier_date(self, repository, mock_session):
        """Trouve les pointages d'un chantier pour une date."""
        mock_session.all.return_value = []

        result = repository.find_by_chantier_and_date(100, date(2024, 1, 15))

        assert result == []


class TestFindByAffectation:
    """Tests pour find_by_affectation."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyPointageRepository(mock_session)

    def test_trouve_par_affectation(self, repository, mock_session):
        """Trouve un pointage par son affectation."""
        mock_model = Mock()
        mock_model.id = 1
        mock_model.utilisateur_id = 10
        mock_model.chantier_id = 100
        mock_model.date_pointage = date(2024, 1, 15)
        mock_model.heures_normales_minutes = 480
        mock_model.heures_supplementaires_minutes = 0
        mock_model.statut = "brouillon"
        mock_model.commentaire = None
        mock_model.signature_utilisateur = None
        mock_model.signature_date = None
        mock_model.validateur_id = None
        mock_model.validation_date = None
        mock_model.motif_rejet = None
        mock_model.affectation_id = 55
        mock_model.created_by = None
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        mock_session.first.return_value = mock_model

        result = repository.find_by_affectation(55)

        assert result is not None
        assert result.affectation_id == 55

    def test_retourne_none_si_non_trouve(self, repository, mock_session):
        """Retourne None si pas de pointage pour l'affectation."""
        mock_session.first.return_value = None

        result = repository.find_by_affectation(999)
        assert result is None


class TestFindPendingValidation:
    """Tests pour find_pending_validation."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        session.offset.return_value = session
        session.limit.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyPointageRepository(mock_session)

    def test_trouve_pointages_en_attente(self, repository, mock_session):
        """Trouve les pointages en attente de validation."""
        mock_session.count.return_value = 2
        mock_session.all.return_value = []

        pointages, total = repository.find_pending_validation()

        assert total == 2
        assert pointages == []

    def test_pagination(self, repository, mock_session):
        """Gere la pagination."""
        mock_session.count.return_value = 100
        mock_session.all.return_value = []

        pointages, total = repository.find_pending_validation(skip=20, limit=10)

        mock_session.offset.assert_called_with(20)
        mock_session.limit.assert_called_with(10)


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
        return SQLAlchemyPointageRepository(mock_session)

    def test_recherche_avec_filtres(self, repository, mock_session):
        """Recherche avec filtres appliques."""
        mock_session.count.return_value = 5
        mock_session.all.return_value = []

        pointages, total = repository.search(
            utilisateur_id=10,
            chantier_id=100,
            date_debut=date(2024, 1, 1),
            date_fin=date(2024, 1, 31),
            statut=StatutPointage.SOUMIS,
        )

        assert total == 5
        # Les filtres sont appliques
        assert mock_session.filter.call_count >= 1


class TestBulkSave:
    """Tests pour bulk_save."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyPointageRepository(mock_session)

    def test_sauvegarde_plusieurs_pointages(self, repository, mock_session):
        """Sauvegarde plusieurs pointages en une fois."""
        pointages = [
            Pointage(
                id=None,
                utilisateur_id=1,
                chantier_id=10,
                date_pointage=date(2024, 1, 15),
                heures_normales=Duree.from_minutes(480),  # 8h
                heures_supplementaires=Duree.from_minutes(0),
                statut=StatutPointage.BROUILLON,
            ),
            Pointage(
                id=None,
                utilisateur_id=2,
                chantier_id=10,
                date_pointage=date(2024, 1, 15),
                heures_normales=Duree.from_minutes(420),  # 7h
                heures_supplementaires=Duree.from_minutes(60),  # 1h
                statut=StatutPointage.BROUILLON,
            ),
        ]

        mock_model1 = Mock()
        mock_model1.id = 1
        mock_model1.utilisateur_id = 1
        mock_model1.chantier_id = 10
        mock_model1.date_pointage = date(2024, 1, 15)
        mock_model1.heures_normales_minutes = 480
        mock_model1.heures_supplementaires_minutes = 0
        mock_model1.statut = "brouillon"
        mock_model1.commentaire = None
        mock_model1.signature_utilisateur = None
        mock_model1.signature_date = None
        mock_model1.validateur_id = None
        mock_model1.validation_date = None
        mock_model1.motif_rejet = None
        mock_model1.affectation_id = None
        mock_model1.created_by = None
        mock_model1.created_at = datetime.now()
        mock_model1.updated_at = datetime.now()

        mock_model2 = Mock()
        mock_model2.id = 2
        mock_model2.utilisateur_id = 2
        mock_model2.chantier_id = 10
        mock_model2.date_pointage = date(2024, 1, 15)
        mock_model2.heures_normales_minutes = 420
        mock_model2.heures_supplementaires_minutes = 60
        mock_model2.statut = "brouillon"
        mock_model2.commentaire = None
        mock_model2.signature_utilisateur = None
        mock_model2.signature_date = None
        mock_model2.validateur_id = None
        mock_model2.validation_date = None
        mock_model2.motif_rejet = None
        mock_model2.affectation_id = None
        mock_model2.created_by = None
        mock_model2.created_at = datetime.now()
        mock_model2.updated_at = datetime.now()

        with patch(
            "modules.pointages.infrastructure.persistence.sqlalchemy_pointage_repository.PointageModel"
        ) as MockModel:
            MockModel.side_effect = [mock_model1, mock_model2]
            result = repository.bulk_save(pointages)

        assert mock_session.add.call_count == 2
        mock_session.commit.assert_called_once()


class TestCountByUtilisateurSemaine:
    """Tests pour count_by_utilisateur_semaine."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.query.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def repository(self, mock_session):
        return SQLAlchemyPointageRepository(mock_session)

    def test_compte_pointages_semaine(self, repository, mock_session):
        """Compte les pointages d'une semaine."""
        mock_session.count.return_value = 5

        result = repository.count_by_utilisateur_semaine(10, date(2024, 1, 15))

        assert result == 5
