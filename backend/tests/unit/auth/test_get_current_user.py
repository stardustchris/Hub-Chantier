"""Tests unitaires pour GetCurrentUserUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.auth.domain.entities import User
from modules.auth.domain.value_objects import Email, PasswordHash, Role
from modules.auth.domain.repositories import UserRepository
from modules.auth.application.ports import TokenService
from modules.auth.application.use_cases.get_current_user import (
    GetCurrentUserUseCase,
    InvalidTokenError,
    UserNotFoundError,
)


class TestGetCurrentUserUseCase:
    """Tests pour le use case de récupération utilisateur courant."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_token_service = Mock(spec=TokenService)
        self.use_case = GetCurrentUserUseCase(
            user_repo=self.mock_user_repo,
            token_service=self.mock_token_service,
        )

        self.test_user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed_password"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def test_get_current_user_success(self):
        """Test: récupération réussie avec token valide."""
        self.mock_token_service.get_user_id.return_value = 1
        self.mock_user_repo.find_by_id.return_value = self.test_user

        result = self.use_case.execute("valid_jwt_token")

        assert result.id == 1
        assert result.email == "test@example.com"
        self.mock_token_service.get_user_id.assert_called_once_with("valid_jwt_token")
        self.mock_user_repo.find_by_id.assert_called_once_with(1)

    def test_get_current_user_invalid_token(self):
        """Test: échec si token invalide."""
        self.mock_token_service.get_user_id.return_value = None

        with pytest.raises(InvalidTokenError):
            self.use_case.execute("invalid_token")

    def test_get_current_user_not_found(self):
        """Test: échec si utilisateur n'existe plus."""
        self.mock_token_service.get_user_id.return_value = 999
        self.mock_user_repo.find_by_id.return_value = None

        with pytest.raises(UserNotFoundError) as exc_info:
            self.use_case.execute("token_for_deleted_user")

        assert exc_info.value.user_id == 999

    def test_get_current_user_inactive(self):
        """Test: échec si compte désactivé."""
        inactive_user = User(
            id=2,
            email=Email("inactive@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="MARTIN",
            prenom="Marie",
            role=Role.COMPAGNON,
            is_active=False,
        )
        self.mock_token_service.get_user_id.return_value = 2
        self.mock_user_repo.find_by_id.return_value = inactive_user

        with pytest.raises(InvalidTokenError) as exc_info:
            self.use_case.execute("token_for_inactive_user")

        assert "désactivé" in str(exc_info.value.message)

    def test_execute_from_id_success(self):
        """Test: récupération par ID directement."""
        self.mock_user_repo.find_by_id.return_value = self.test_user

        result = self.use_case.execute_from_id(1)

        assert result.id == 1
        self.mock_user_repo.find_by_id.assert_called_once_with(1)

    def test_execute_from_id_not_found(self):
        """Test: échec si utilisateur non trouvé par ID."""
        self.mock_user_repo.find_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            self.use_case.execute_from_id(999)
