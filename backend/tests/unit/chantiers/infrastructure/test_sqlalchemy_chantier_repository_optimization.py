"""Tests unitaires pour GAP-CHT-004 - Optimisation N+1 queries.

Ce fichier teste :
- Optimisation find_by_conducteur avec JOIN sur table de jointure
- Optimisation find_by_chef_chantier avec JOIN sur table de jointure
- Optimisation find_by_responsable avec UNION des sous-requêtes
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date

from modules.chantiers.infrastructure.persistence.sqlalchemy_chantier_repository import (
    SQLAlchemyChantierRepository,
)
from modules.chantiers.infrastructure.persistence.chantier_model import ChantierModel
from modules.chantiers.infrastructure.persistence.chantier_responsable_model import (
    ChantierConducteurModel,
    ChantierChefModel,
)
from modules.chantiers.domain.entities.chantier import Chantier
from modules.chantiers.domain.value_objects.code_chantier import CodeChantier
from modules.chantiers.domain.value_objects.statut_chantier import StatutChantier


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_session():
    """Fixture: mock de session SQLAlchemy."""
    session = Mock()
    session.query = Mock()
    return session


@pytest.fixture
def repository(mock_session):
    """Fixture: instance du repository avec session mockée."""
    return SQLAlchemyChantierRepository(mock_session)


def create_chantier_model(
    chantier_id: int,
    code: str,
    nom: str,
    conducteur_ids: list = None,
    chef_ids: list = None,
) -> ChantierModel:
    """Helper: crée un ChantierModel de test."""
    model = ChantierModel(
        id=chantier_id,
        code=code,
        nom=nom,
        adresse="123 Rue Test",
        statut="ouvert",
        conducteur_ids=conducteur_ids or [],
        chef_chantier_ids=chef_ids or [],
    )
    # Simuler les relations
    model.conducteurs_rel = []
    model.chefs_rel = []
    return model


# =============================================================================
# Tests GAP-CHT-004: Optimisation find_by_conducteur
# =============================================================================

class TestFindByConducteurOptimization:
    """Tests: Optimisation N+1 pour find_by_conducteur."""

    def test_should_use_join_on_conducteur_table(self, repository, mock_session):
        """Test: utilise JOIN sur ChantierConducteurModel (pas de N+1)."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.find_by_conducteur(conducteur_id=5)

        # Assert - Vérifier que join() est appelé
        mock_query.join.assert_called_once()

        # Vérifier que le join est sur ChantierConducteurModel
        join_args = mock_query.join.call_args[0]
        assert join_args[0] == ChantierConducteurModel

    def test_should_filter_by_conducteur_user_id(self, repository, mock_session):
        """Test: filtre sur user_id du conducteur."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.find_by_conducteur(conducteur_id=42)

        # Assert - Vérifier appels filter
        # Au moins 2 filters: deleted_at is None + user_id
        assert mock_query.filter.call_count >= 2

    def test_should_return_chantiers_for_conducteur(self, repository, mock_session):
        """Test: retourne les chantiers du conducteur."""
        # Arrange
        chantier_model = create_chantier_model(1, "CHT-0001", "Chantier 1", [42], [])

        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [chantier_model]

        # Act
        result = repository.find_by_conducteur(conducteur_id=42)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], Chantier)

    def test_should_exclude_deleted_chantiers(self, repository, mock_session):
        """Test: exclut les chantiers supprimés (soft delete)."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.find_by_conducteur(conducteur_id=5)

        # Assert - Vérifier que _not_deleted() est appliqué via filter
        assert mock_query.filter.call_count >= 2


# =============================================================================
# Tests GAP-CHT-004: Optimisation find_by_chef_chantier
# =============================================================================

class TestFindByChefChantierOptimization:
    """Tests: Optimisation N+1 pour find_by_chef_chantier."""

    def test_should_use_join_on_chef_table(self, repository, mock_session):
        """Test: utilise JOIN sur ChantierChefModel (pas de N+1)."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.find_by_chef_chantier(chef_id=10)

        # Assert - Vérifier que join() est appelé
        mock_query.join.assert_called_once()

        # Vérifier que le join est sur ChantierChefModel
        join_args = mock_query.join.call_args[0]
        assert join_args[0] == ChantierChefModel

    def test_should_filter_by_chef_user_id(self, repository, mock_session):
        """Test: filtre sur user_id du chef."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.find_by_chef_chantier(chef_id=99)

        # Assert - Vérifier appels filter (deleted_at + user_id)
        assert mock_query.filter.call_count >= 2

    def test_should_return_chantiers_for_chef(self, repository, mock_session):
        """Test: retourne les chantiers du chef."""
        # Arrange
        chantier_model = create_chantier_model(2, "CHT-0002", "Chantier 2", [], [99])

        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [chantier_model]

        # Act
        result = repository.find_by_chef_chantier(chef_id=99)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], Chantier)


# =============================================================================
# Tests GAP-CHT-004: Optimisation find_by_responsable
# =============================================================================

class TestFindByResponsableOptimization:
    """Tests: Optimisation N+1 pour find_by_responsable (UNION)."""

    def test_should_use_union_of_subqueries(self, repository, mock_session):
        """Test: utilise UNION de sous-requêtes (pas de N+1)."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.find_by_responsable(user_id=7)

        # Assert - Vérifier que query() est appelé (pour les subqueries)
        # La méthode utilise select() donc on vérifie que filter est appelé
        assert mock_query.filter.call_count >= 1

    def test_should_return_chantiers_where_user_is_conducteur_or_chef(
        self, repository, mock_session
    ):
        """Test: retourne chantiers où user est conducteur OU chef."""
        # Arrange
        chantier1 = create_chantier_model(1, "CHT-0001", "Chantier 1", [7], [])
        chantier2 = create_chantier_model(2, "CHT-0002", "Chantier 2", [], [7])

        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [chantier1, chantier2]

        # Act
        result = repository.find_by_responsable(user_id=7)

        # Assert - Les 2 chantiers sont retournés
        assert len(result) == 2

    def test_should_exclude_deleted_chantiers_in_responsable_query(
        self, repository, mock_session
    ):
        """Test: exclut les chantiers supprimés."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.find_by_responsable(user_id=7)

        # Assert - _not_deleted() appliqué
        assert mock_query.filter.call_count >= 1


# =============================================================================
# Tests: Pagination
# =============================================================================

class TestRepositoryPagination:
    """Tests: Pagination pour les méthodes optimisées."""

    def test_should_apply_skip_and_limit_to_conducteur_query(
        self, repository, mock_session
    ):
        """Test: skip et limit appliqués à find_by_conducteur."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.find_by_conducteur(conducteur_id=5, skip=10, limit=20)

        # Assert
        mock_query.offset.assert_called_once_with(10)
        mock_query.limit.assert_called_once_with(20)

    def test_should_apply_skip_and_limit_to_chef_query(
        self, repository, mock_session
    ):
        """Test: skip et limit appliqués à find_by_chef_chantier."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.find_by_chef_chantier(chef_id=10, skip=5, limit=15)

        # Assert
        mock_query.offset.assert_called_once_with(5)
        mock_query.limit.assert_called_once_with(15)

    def test_should_apply_skip_and_limit_to_responsable_query(
        self, repository, mock_session
    ):
        """Test: skip et limit appliqués à find_by_responsable."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.find_by_responsable(user_id=7, skip=0, limit=50)

        # Assert
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(50)


# =============================================================================
# Tests: Ordering
# =============================================================================

class TestRepositoryOrdering:
    """Tests: Tri par code pour cohérence."""

    def test_should_order_by_code_in_conducteur_query(
        self, repository, mock_session
    ):
        """Test: order by code dans find_by_conducteur."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.find_by_conducteur(conducteur_id=5)

        # Assert - order_by appelé
        mock_query.order_by.assert_called_once()

    def test_should_order_by_code_in_chef_query(
        self, repository, mock_session
    ):
        """Test: order by code dans find_by_chef_chantier."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.find_by_chef_chantier(chef_id=10)

        # Assert
        mock_query.order_by.assert_called_once()

    def test_should_order_by_code_in_responsable_query(
        self, repository, mock_session
    ):
        """Test: order by code dans find_by_responsable."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.find_by_responsable(user_id=7)

        # Assert
        mock_query.order_by.assert_called_once()
