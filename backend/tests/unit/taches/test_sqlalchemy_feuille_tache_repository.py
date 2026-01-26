"""Tests unitaires pour SQLAlchemyFeuilleTacheRepository."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date, datetime

from modules.taches.infrastructure.persistence.sqlalchemy_feuille_tache_repository import (
    SQLAlchemyFeuilleTacheRepository,
)
from modules.taches.domain.entities.feuille_tache import StatutValidation


class TestFindById:
    """Tests de find_by_id."""

    def test_find_by_id_returns_entity_when_found(self):
        """Test retourne l'entite quand trouvee."""
        mock_session = Mock()
        mock_model = Mock()
        mock_entity = Mock()
        mock_model.to_entity.return_value = mock_entity
        mock_session.query.return_value.filter.return_value.first.return_value = mock_model

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        result = repo.find_by_id(1)

        assert result == mock_entity
        mock_model.to_entity.assert_called_once()

    def test_find_by_id_returns_none_when_not_found(self):
        """Test retourne None quand non trouvee."""
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = None

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        result = repo.find_by_id(999)

        assert result is None


class TestFindByTache:
    """Tests de find_by_tache."""

    def test_find_by_tache_returns_list(self):
        """Test retourne une liste de feuilles."""
        mock_session = Mock()
        mock_model1 = Mock()
        mock_model2 = Mock()
        mock_entity1 = Mock()
        mock_entity2 = Mock()
        mock_model1.to_entity.return_value = mock_entity1
        mock_model2.to_entity.return_value = mock_entity2

        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_model1, mock_model2]

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        result = repo.find_by_tache(tache_id=1)

        assert len(result) == 2
        assert result[0] == mock_entity1
        assert result[1] == mock_entity2

    def test_find_by_tache_with_pagination(self):
        """Test avec pagination."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        repo.find_by_tache(tache_id=1, skip=10, limit=5)

        mock_query.offset.assert_called_with(10)
        mock_query.limit.assert_called_with(5)


class TestFindByUtilisateur:
    """Tests de find_by_utilisateur."""

    def test_find_by_utilisateur_without_date_filters(self):
        """Test sans filtres de date."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        repo.find_by_utilisateur(utilisateur_id=1)

        # Verifie qu'un seul filtre est applique (utilisateur_id)
        assert mock_query.filter.call_count == 1

    def test_find_by_utilisateur_with_date_filters(self):
        """Test avec filtres de date."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        repo.find_by_utilisateur(
            utilisateur_id=1,
            date_debut=date(2024, 1, 1),
            date_fin=date(2024, 1, 31),
        )

        # Verifie que les filtres de date sont appliques
        assert mock_query.filter.call_count == 3


class TestFindByChantier:
    """Tests de find_by_chantier."""

    def test_find_by_chantier_basic(self):
        """Test recherche basique par chantier."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        repo.find_by_chantier(chantier_id=1)

        assert mock_query.filter.call_count == 1

    def test_find_by_chantier_with_statut(self):
        """Test avec filtre de statut."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        repo.find_by_chantier(chantier_id=1, statut=StatutValidation.VALIDEE)

        assert mock_query.filter.call_count == 2


class TestFindEnAttenteValidation:
    """Tests de find_en_attente_validation."""

    def test_find_en_attente_without_chantier(self):
        """Test sans filtre de chantier."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        repo.find_en_attente_validation()

        # Un seul filtre pour le statut
        assert mock_query.filter.call_count == 1

    def test_find_en_attente_with_chantier(self):
        """Test avec filtre de chantier."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        repo.find_en_attente_validation(chantier_id=1)

        # Deux filtres: statut et chantier
        assert mock_query.filter.call_count == 2


class TestSave:
    """Tests de save."""

    def test_save_new_feuille(self):
        """Test sauvegarde nouvelle feuille."""
        mock_session = Mock()
        mock_feuille = Mock()
        mock_feuille.id = None
        mock_model = Mock()
        mock_model.to_entity.return_value = mock_feuille

        with patch(
            "modules.taches.infrastructure.persistence.sqlalchemy_feuille_tache_repository.FeuilleTacheModel"
        ) as MockModel:
            MockModel.from_entity.return_value = mock_model

            repo = SQLAlchemyFeuilleTacheRepository(mock_session)
            result = repo.save(mock_feuille)

            mock_session.add.assert_called_once_with(mock_model)
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(mock_model)

    def test_save_existing_feuille(self):
        """Test mise a jour feuille existante."""
        mock_session = Mock()
        mock_feuille = Mock()
        mock_feuille.id = 1
        mock_feuille.heures_travaillees = 8.0
        mock_feuille.quantite_realisee = 10.0
        mock_feuille.commentaire = "Test"
        mock_feuille.statut_validation = StatutValidation.VALIDEE
        mock_feuille.validateur_id = 2
        mock_feuille.date_validation = datetime.now()
        mock_feuille.motif_rejet = None
        mock_feuille.updated_at = datetime.now()

        mock_existing_model = Mock()
        mock_existing_model.to_entity.return_value = mock_feuille
        mock_session.query.return_value.filter.return_value.first.return_value = mock_existing_model

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        result = repo.save(mock_feuille)

        assert mock_existing_model.heures_travaillees == mock_feuille.heures_travaillees
        mock_session.commit.assert_called_once()


class TestDelete:
    """Tests de delete."""

    def test_delete_existing(self):
        """Test suppression feuille existante."""
        mock_session = Mock()
        mock_model = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_model

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        result = repo.delete(1)

        assert result is True
        mock_session.delete.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()

    def test_delete_non_existing(self):
        """Test suppression feuille inexistante."""
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = None

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        result = repo.delete(999)

        assert result is False
        mock_session.delete.assert_not_called()


class TestCountByTache:
    """Tests de count_by_tache."""

    def test_count_by_tache(self):
        """Test comptage des feuilles par tache."""
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.scalar.return_value = 5

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        result = repo.count_by_tache(1)

        assert result == 5


class TestGetTotalHeuresTache:
    """Tests de get_total_heures_tache."""

    def test_get_total_heures_validees_only(self):
        """Test total heures avec validees seulement."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 24.5

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        result = repo.get_total_heures_tache(1, validees_only=True)

        assert result == 24.5
        assert mock_query.filter.call_count == 2  # tache_id + statut

    def test_get_total_heures_all(self):
        """Test total heures toutes feuilles."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 32.0

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        result = repo.get_total_heures_tache(1, validees_only=False)

        assert result == 32.0
        assert mock_query.filter.call_count == 1  # tache_id seulement

    def test_get_total_heures_returns_zero_on_none(self):
        """Test retourne 0 si aucune donnee."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = None

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        result = repo.get_total_heures_tache(1)

        assert result == 0.0


class TestGetTotalQuantiteTache:
    """Tests de get_total_quantite_tache."""

    def test_get_total_quantite(self):
        """Test total quantite."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 100.0

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        result = repo.get_total_quantite_tache(1)

        assert result == 100.0

    def test_get_total_quantite_returns_zero_on_none(self):
        """Test retourne 0 si aucune donnee."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = None

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        result = repo.get_total_quantite_tache(1)

        assert result == 0.0


class TestExistsForDate:
    """Tests de exists_for_date."""

    def test_exists_for_date_true(self):
        """Test existe pour cette date."""
        mock_session = Mock()
        mock_model = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_model

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        result = repo.exists_for_date(
            tache_id=1,
            utilisateur_id=2,
            date_travail=date(2024, 1, 15),
        )

        assert result is True

    def test_exists_for_date_false(self):
        """Test n'existe pas pour cette date."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        repo = SQLAlchemyFeuilleTacheRepository(mock_session)
        result = repo.exists_for_date(
            tache_id=1,
            utilisateur_id=2,
            date_travail=date(2024, 1, 15),
        )

        assert result is False
