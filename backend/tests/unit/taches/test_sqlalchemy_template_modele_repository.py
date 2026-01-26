"""Tests unitaires pour SQLAlchemyTemplateModeleRepository."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from modules.taches.infrastructure.persistence.sqlalchemy_template_modele_repository import (
    SQLAlchemyTemplateModeleRepository,
)


class TestFindById:
    """Tests de find_by_id."""

    def test_find_by_id_returns_entity_when_found(self):
        """Test retourne l'entite quand trouvee."""
        mock_session = Mock()
        mock_model = Mock()
        mock_entity = Mock()
        mock_model.to_entity.return_value = mock_entity
        mock_session.query.return_value.filter.return_value.first.return_value = mock_model

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        result = repo.find_by_id(1)

        assert result == mock_entity
        mock_model.to_entity.assert_called_once()

    def test_find_by_id_returns_none_when_not_found(self):
        """Test retourne None quand non trouvee."""
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = None

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        result = repo.find_by_id(999)

        assert result is None


class TestFindAll:
    """Tests de find_all."""

    def test_find_all_active_only(self):
        """Test recuperation templates actifs seulement."""
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

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        result = repo.find_all(active_only=True)

        assert len(result) == 2
        mock_query.filter.assert_called_once()

    def test_find_all_include_inactive(self):
        """Test recuperation tous les templates."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        result = repo.find_all(active_only=False)

        mock_query.filter.assert_not_called()

    def test_find_all_with_pagination(self):
        """Test avec pagination."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        repo.find_all(skip=20, limit=10)

        mock_query.offset.assert_called_with(20)
        mock_query.limit.assert_called_with(10)


class TestFindByCategorie:
    """Tests de find_by_categorie."""

    def test_find_by_categorie_active_only(self):
        """Test recherche par categorie actifs seulement."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        repo.find_by_categorie("maconnerie", active_only=True)

        # Deux filtres: categorie et is_active
        assert mock_query.filter.call_count == 2

    def test_find_by_categorie_include_inactive(self):
        """Test recherche par categorie incluant inactifs."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        repo.find_by_categorie("maconnerie", active_only=False)

        # Un seul filtre: categorie
        assert mock_query.filter.call_count == 1


class TestSave:
    """Tests de save."""

    def test_save_new_template(self):
        """Test sauvegarde nouveau template."""
        mock_session = Mock()
        mock_template = Mock()
        mock_template.id = None
        mock_template.sous_taches = []
        mock_model = Mock()
        mock_model.to_entity.return_value = mock_template

        with patch(
            "modules.taches.infrastructure.persistence.sqlalchemy_template_modele_repository.TemplateModeleModel"
        ) as MockModel:
            MockModel.from_entity.return_value = mock_model

            repo = SQLAlchemyTemplateModeleRepository(mock_session)
            result = repo.save(mock_template)

            mock_session.add.assert_called_once_with(mock_model)
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(mock_model)

    def test_save_existing_template(self):
        """Test mise a jour template existant."""
        mock_session = Mock()
        mock_template = Mock()
        mock_template.id = 1
        mock_template.nom = "Template Test"
        mock_template.description = "Description"
        mock_template.categorie = "maconnerie"
        mock_template.unite_mesure = Mock(value="m2")
        mock_template.heures_estimees_defaut = 8.0
        mock_template.is_active = True
        mock_template.updated_at = datetime.now()
        mock_template.sous_taches = []

        mock_existing_model = MagicMock()
        mock_existing_model.to_entity.return_value = mock_template

        # Configuration des queries
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_existing_model
        mock_query.delete.return_value = None

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        result = repo.save(mock_template)

        # Verifie que les attributs sont mis a jour
        mock_session.commit.assert_called_once()


class TestDelete:
    """Tests de delete."""

    def test_delete_existing(self):
        """Test suppression template existant."""
        mock_session = Mock()
        mock_model = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_model

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        result = repo.delete(1)

        assert result is True
        mock_session.delete.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()

    def test_delete_non_existing(self):
        """Test suppression template inexistant."""
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = None

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        result = repo.delete(999)

        assert result is False
        mock_session.delete.assert_not_called()


class TestCount:
    """Tests de count."""

    def test_count_active_only(self):
        """Test comptage actifs seulement."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 10

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        result = repo.count(active_only=True)

        assert result == 10
        mock_query.filter.assert_called_once()

    def test_count_all(self):
        """Test comptage tous les templates."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.scalar.return_value = 15

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        result = repo.count(active_only=False)

        assert result == 15
        mock_query.filter.assert_not_called()


class TestSearch:
    """Tests de search."""

    def test_search_basic(self):
        """Test recherche basique."""
        mock_session = Mock()
        mock_model = Mock()
        mock_entity = Mock()
        mock_model.to_entity.return_value = mock_entity

        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_model]
        mock_query.count.return_value = 1

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        results, total = repo.search(active_only=True)

        assert len(results) == 1
        assert total == 1

    def test_search_with_query(self):
        """Test recherche avec terme."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.count.return_value = 0

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        results, total = repo.search(query="test")

        # Filtre active_only + filtre query (ilike)
        assert mock_query.filter.call_count >= 2

    def test_search_with_categorie(self):
        """Test recherche avec filtre categorie."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.count.return_value = 0

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        results, total = repo.search(categorie="maconnerie")

        assert mock_query.filter.call_count >= 2

    def test_search_with_pagination(self):
        """Test recherche avec pagination."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.count.return_value = 100

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        results, total = repo.search(skip=50, limit=25)

        mock_query.offset.assert_called_with(50)
        mock_query.limit.assert_called_with(25)
        assert total == 100


class TestGetCategories:
    """Tests de get_categories."""

    def test_get_categories(self):
        """Test recuperation des categories distinctes."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.distinct.return_value = mock_query
        mock_query.all.return_value = [("maconnerie",), ("electricite",), ("plomberie",)]

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        result = repo.get_categories()

        assert len(result) == 3
        assert "maconnerie" in result
        assert "electricite" in result
        assert "plomberie" in result

    def test_get_categories_empty(self):
        """Test recuperation categories vide."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.distinct.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        result = repo.get_categories()

        assert result == []

    def test_get_categories_filters_none_values(self):
        """Test que les valeurs None sont filtrees."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.distinct.return_value = mock_query
        mock_query.all.return_value = [("maconnerie",), (None,), ("electricite",)]

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        result = repo.get_categories()

        assert len(result) == 2
        assert None not in result


class TestExistsByNom:
    """Tests de exists_by_nom."""

    def test_exists_by_nom_true(self):
        """Test nom existe."""
        mock_session = Mock()
        mock_model = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_model

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        result = repo.exists_by_nom("Template Test")

        assert result is True

    def test_exists_by_nom_false(self):
        """Test nom n'existe pas."""
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = None

        repo = SQLAlchemyTemplateModeleRepository(mock_session)
        result = repo.exists_by_nom("Template Inexistant")

        assert result is False
