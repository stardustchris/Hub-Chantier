"""Tests unitaires pour SQLAlchemyChantierRepository."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from modules.chantiers.infrastructure.persistence.sqlalchemy_chantier_repository import (
    SQLAlchemyChantierRepository,
)
from modules.chantiers.domain.value_objects import CodeChantier, StatutChantier


class TestFindById:
    """Tests de find_by_id."""

    def test_find_by_id_returns_entity_when_found(self):
        """Test retourne l'entité quand trouvée."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.code = "A001"
        mock_model.nom = "Chantier Test"
        mock_model.adresse = "123 Rue Test"
        mock_model.description = None
        mock_model.statut = "ouvert"
        mock_model.couleur = "#3498DB"
        mock_model.latitude = 48.8566
        mock_model.longitude = 2.3522
        mock_model.photo_couverture = None
        mock_model.contact_nom = "Contact"
        mock_model.contact_telephone = "0612345678"
        mock_model.heures_estimees = 100
        mock_model.date_debut = None
        mock_model.date_fin = None
        mock_model.conducteur_ids = [1, 2]
        mock_model.chef_chantier_ids = [3]
        mock_model.conducteurs_rel = []
        mock_model.chefs_rel = []
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_model

        repo = SQLAlchemyChantierRepository(mock_session)
        result = repo.find_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.nom == "Chantier Test"

    def test_find_by_id_returns_none_when_not_found(self):
        """Test retourne None quand non trouvé."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        repo = SQLAlchemyChantierRepository(mock_session)
        result = repo.find_by_id(999)

        assert result is None


class TestFindByCode:
    """Tests de find_by_code."""

    def test_find_by_code_returns_entity_when_found(self):
        """Test trouve par code."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.code = "B002"
        mock_model.nom = "Chantier B"
        mock_model.adresse = "456 Avenue Test"
        mock_model.description = None
        mock_model.statut = "ouvert"
        mock_model.couleur = "#E74C3C"
        mock_model.latitude = None
        mock_model.longitude = None
        mock_model.photo_couverture = None
        mock_model.contact_nom = None
        mock_model.contact_telephone = None
        mock_model.heures_estimees = None
        mock_model.date_debut = None
        mock_model.date_fin = None
        mock_model.conducteur_ids = []
        mock_model.chef_chantier_ids = []
        mock_model.conducteurs_rel = []
        mock_model.chefs_rel = []
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_model

        repo = SQLAlchemyChantierRepository(mock_session)
        result = repo.find_by_code(CodeChantier("B002"))

        assert result is not None
        assert str(result.code) == "B002"


class TestDelete:
    """Tests de delete (soft delete)."""

    def test_delete_existing_chantier(self):
        """Test suppression chantier existant."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.deleted_at = None

        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_model

        repo = SQLAlchemyChantierRepository(mock_session)
        result = repo.delete(1)

        assert result is True
        assert mock_model.deleted_at is not None
        mock_session.commit.assert_called_once()

    def test_delete_non_existing_chantier(self):
        """Test suppression chantier inexistant."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        repo = SQLAlchemyChantierRepository(mock_session)
        result = repo.delete(999)

        assert result is False


class TestFindAll:
    """Tests de find_all."""

    def test_find_all_with_pagination(self):
        """Test find_all avec pagination."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyChantierRepository(mock_session)
        repo.find_all(skip=20, limit=10)

        mock_query.offset.assert_called_with(20)
        mock_query.limit.assert_called_with(10)


class TestCount:
    """Tests de count."""

    def test_count_returns_total(self):
        """Test count retourne le total."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 15

        repo = SQLAlchemyChantierRepository(mock_session)
        result = repo.count()

        assert result == 15


class TestFindByStatut:
    """Tests de find_by_statut."""

    def test_find_by_statut(self):
        """Test trouve par statut."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyChantierRepository(mock_session)
        repo.find_by_statut(StatutChantier.ouvert())

        assert mock_query.filter.call_count == 2  # statut + not_deleted


class TestFindActive:
    """Tests de find_active."""

    def test_find_active(self):
        """Test trouve chantiers actifs (non fermés)."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyChantierRepository(mock_session)
        repo.find_active()

        assert mock_query.filter.call_count == 2


class TestFindByConducteur:
    """Tests de find_by_conducteur."""

    def test_find_by_conducteur(self):
        """Test trouve chantiers d'un conducteur."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyChantierRepository(mock_session)
        repo.find_by_conducteur(conducteur_id=5)

        mock_query.join.assert_called_once()


class TestFindByChefChantier:
    """Tests de find_by_chef_chantier."""

    def test_find_by_chef_chantier(self):
        """Test trouve chantiers d'un chef de chantier."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyChantierRepository(mock_session)
        repo.find_by_chef_chantier(chef_id=3)

        mock_query.join.assert_called_once()


class TestSyncResponsables:
    """Tests de sync_responsables."""

    def test_sync_responsables_clears_and_adds(self):
        """Test sync supprime anciennes associations et ajoute nouvelles."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.delete.return_value = None

        repo = SQLAlchemyChantierRepository(mock_session)
        repo.sync_responsables(
            chantier_id=1,
            conducteur_ids=[10, 11],
            chef_ids=[20],
        )

        # Vérifie les suppressions
        assert mock_query.delete.call_count == 2

        # Vérifie les ajouts (2 conducteurs + 1 chef)
        assert mock_session.add.call_count == 3
        mock_session.flush.assert_called_once()


class TestExistsByCode:
    """Tests de exists_by_code."""

    def test_exists_by_code_true(self):
        """Test code existe."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = Mock()

        repo = SQLAlchemyChantierRepository(mock_session)
        result = repo.exists_by_code(CodeChantier("A001"))

        assert result is True

    def test_exists_by_code_false(self):
        """Test code n'existe pas."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        repo = SQLAlchemyChantierRepository(mock_session)
        result = repo.exists_by_code(CodeChantier("Z999"))

        assert result is False


class TestGetLastCode:
    """Tests de get_last_code."""

    def test_get_last_code_returns_code(self):
        """Test retourne le dernier code."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.code = "Z999"

        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = mock_model

        repo = SQLAlchemyChantierRepository(mock_session)
        result = repo.get_last_code()

        assert result == "Z999"

    def test_get_last_code_returns_none_when_empty(self):
        """Test retourne None si aucun chantier."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = None

        repo = SQLAlchemyChantierRepository(mock_session)
        result = repo.get_last_code()

        assert result is None


class TestSearch:
    """Tests de search."""

    def test_search_basic(self):
        """Test recherche basique."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyChantierRepository(mock_session)
        results = repo.search("test")

        assert results == []

    def test_search_with_statut_filter(self):
        """Test recherche avec filtre statut."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyChantierRepository(mock_session)
        results = repo.search("test", statut=StatutChantier.ouvert())

        # Vérifie que le filtre statut est appliqué
        assert mock_query.filter.call_count >= 2


class TestToEntity:
    """Tests de _to_entity."""

    def test_to_entity_with_full_data(self):
        """Test conversion avec données complètes."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.code = "A001"
        mock_model.nom = "Chantier Complet"
        mock_model.adresse = "123 Rue Test"
        mock_model.description = "Description"
        mock_model.statut = "ouvert"
        mock_model.couleur = "#E74C3C"
        mock_model.latitude = 48.8566
        mock_model.longitude = 2.3522
        mock_model.photo_couverture = "photo.jpg"
        mock_model.contact_nom = "Jean Dupont"
        mock_model.contact_telephone = "0612345678"
        mock_model.heures_estimees = 500
        mock_model.date_debut = datetime(2024, 1, 1)
        mock_model.date_fin = datetime(2024, 12, 31)
        mock_model.conducteur_ids = [1, 2]
        mock_model.chef_chantier_ids = [3]
        mock_model.conducteurs_rel = []
        mock_model.chefs_rel = []
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        repo = SQLAlchemyChantierRepository(mock_session)
        entity = repo._to_entity(mock_model)

        assert entity.id == 1
        assert str(entity.code) == "A001"
        assert entity.nom == "Chantier Complet"
        assert entity.coordonnees_gps is not None
        assert entity.contact is not None

    def test_to_entity_with_minimal_data(self):
        """Test conversion avec données minimales."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.id = 2
        mock_model.code = "B002"
        mock_model.nom = "Chantier Minimal"
        mock_model.adresse = "456 Avenue"
        mock_model.description = None
        mock_model.statut = "ouvert"
        mock_model.couleur = None
        mock_model.latitude = None
        mock_model.longitude = None
        mock_model.photo_couverture = None
        mock_model.contact_nom = None
        mock_model.contact_telephone = None
        mock_model.heures_estimees = None
        mock_model.date_debut = None
        mock_model.date_fin = None
        mock_model.conducteur_ids = []
        mock_model.chef_chantier_ids = []
        mock_model.conducteurs_rel = []
        mock_model.chefs_rel = []
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        repo = SQLAlchemyChantierRepository(mock_session)
        entity = repo._to_entity(mock_model)

        assert entity.id == 2
        assert entity.coordonnees_gps is None
        assert entity.contact is None
