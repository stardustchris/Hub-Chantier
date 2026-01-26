"""Tests unitaires pour les dependencies du module signalements."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from modules.signalements.infrastructure.web.dependencies import (
    get_current_user,
    get_user_name_resolver,
    get_signalement_controller,
)
from modules.signalements.adapters.controllers import SignalementController


class TestGetCurrentUser:
    """Tests de get_current_user."""

    def test_returns_dict_with_id_and_role(self):
        """Test retourne dict avec id et role."""
        result = get_current_user(user_id=42, user_role="admin")

        assert result == {"id": 42, "role": "admin"}

    def test_returns_compagnon_role(self):
        """Test avec role compagnon."""
        result = get_current_user(user_id=1, user_role="compagnon")

        assert result["id"] == 1
        assert result["role"] == "compagnon"

    def test_returns_conducteur_role(self):
        """Test avec role conducteur."""
        result = get_current_user(user_id=10, user_role="conducteur")

        assert result["id"] == 10
        assert result["role"] == "conducteur"


class TestGetUserNameResolver:
    """Tests de get_user_name_resolver."""

    @pytest.fixture
    def mock_db(self):
        """Session DB mock."""
        return Mock()

    @patch("modules.signalements.infrastructure.web.dependencies.get_user_repository")
    def test_resolver_returns_full_name(self, mock_get_repo, mock_db):
        """Test que le resolver retourne nom complet."""
        mock_user = Mock()
        mock_user.prenom = "Jean"
        mock_user.nom = "Dupont"

        mock_repo = Mock()
        mock_repo.find_by_id.return_value = mock_user
        mock_get_repo.return_value = mock_repo

        resolver = get_user_name_resolver(mock_db)
        result = resolver(42)

        assert result == "Jean Dupont"
        mock_repo.find_by_id.assert_called_once_with(42)

    @patch("modules.signalements.infrastructure.web.dependencies.get_user_repository")
    def test_resolver_returns_none_for_unknown_user(self, mock_get_repo, mock_db):
        """Test retourne None pour utilisateur inconnu."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None
        mock_get_repo.return_value = mock_repo

        resolver = get_user_name_resolver(mock_db)
        result = resolver(999)

        assert result is None

    @patch("modules.signalements.infrastructure.web.dependencies.get_user_repository")
    def test_resolver_uses_facade(self, mock_get_repo, mock_db):
        """Test que le resolver utilise la facade centralisee."""
        get_user_name_resolver(mock_db)

        mock_get_repo.assert_called_once_with(mock_db)


class TestGetSignalementController:
    """Tests de get_signalement_controller."""

    @pytest.fixture
    def mock_db(self):
        return Mock()

    @patch("modules.signalements.infrastructure.web.dependencies.SQLAlchemySignalementRepository")
    @patch("modules.signalements.infrastructure.web.dependencies.SQLAlchemyReponseRepository")
    @patch("modules.signalements.infrastructure.web.dependencies.get_user_name_resolver")
    def test_creates_controller(
        self, mock_resolver_factory, mock_reponse_repo, mock_signalement_repo, mock_db
    ):
        """Test creation du controller."""
        mock_sig_repo_instance = Mock()
        mock_rep_repo_instance = Mock()
        mock_resolver = Mock()

        mock_signalement_repo.return_value = mock_sig_repo_instance
        mock_reponse_repo.return_value = mock_rep_repo_instance
        mock_resolver_factory.return_value = mock_resolver

        controller = get_signalement_controller(db=mock_db)

        assert isinstance(controller, SignalementController)
        mock_signalement_repo.assert_called_once_with(mock_db)
        mock_reponse_repo.assert_called_once_with(mock_db)

    @patch("modules.signalements.infrastructure.web.dependencies.SQLAlchemySignalementRepository")
    @patch("modules.signalements.infrastructure.web.dependencies.SQLAlchemyReponseRepository")
    @patch("modules.signalements.infrastructure.web.dependencies.get_user_name_resolver")
    def test_controller_has_user_name_resolver(
        self, mock_resolver_factory, mock_reponse_repo, mock_signalement_repo, mock_db
    ):
        """Test que le controller a le resolver."""
        mock_resolver = Mock()
        mock_resolver_factory.return_value = mock_resolver

        controller = get_signalement_controller(db=mock_db)

        assert controller._get_user_name == mock_resolver

    @patch("modules.signalements.infrastructure.web.dependencies.SQLAlchemySignalementRepository")
    @patch("modules.signalements.infrastructure.web.dependencies.SQLAlchemyReponseRepository")
    @patch("modules.signalements.infrastructure.web.dependencies.get_user_name_resolver")
    def test_controller_repos_initialized(
        self, mock_resolver_factory, mock_reponse_repo, mock_signalement_repo, mock_db
    ):
        """Test que les repos sont initialises."""
        mock_sig_instance = Mock()
        mock_rep_instance = Mock()
        mock_signalement_repo.return_value = mock_sig_instance
        mock_reponse_repo.return_value = mock_rep_instance

        controller = get_signalement_controller(db=mock_db)

        assert controller._signalement_repo == mock_sig_instance
        assert controller._reponse_repo == mock_rep_instance
