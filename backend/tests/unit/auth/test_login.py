"""Tests unitaires pour LoginUseCase."""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from modules.auth.domain.entities import User
from modules.auth.domain.value_objects import Email, PasswordHash, Role
from modules.auth.domain.repositories import UserRepository
from modules.auth.domain.services import PasswordService
from modules.auth.application.ports import TokenService
from modules.auth.application.use_cases import (
    LoginUseCase,
    InvalidCredentialsError,
    UserInactiveError,
)
from modules.auth.application.dtos import LoginDTO


class TestLoginUseCase:
    """Tests pour le use case de connexion."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Mocks
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_password_service = Mock(spec=PasswordService)
        self.mock_token_service = Mock(spec=TokenService)

        # Use case à tester
        self.use_case = LoginUseCase(
            user_repo=self.mock_user_repo,
            password_service=self.mock_password_service,
            token_service=self.mock_token_service,
        )

        # User de test
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

    def test_login_success(self):
        """Test: connexion réussie avec identifiants valides."""
        # Arrange
        self.mock_user_repo.find_by_email.return_value = self.test_user
        self.mock_password_service.verify.return_value = True
        self.mock_token_service.generate.return_value = "jwt_token_123"

        dto = LoginDTO(email="test@example.com", password="password123")

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.user.id == 1
        assert result.user.email == "test@example.com"
        assert result.token.access_token == "jwt_token_123"
        self.mock_user_repo.find_by_email.assert_called_once()
        self.mock_password_service.verify.assert_called_once()
        self.mock_token_service.generate.assert_called_once_with(self.test_user)

    def test_login_invalid_email(self):
        """Test: échec si email invalide."""
        dto = LoginDTO(email="invalid-email", password="password123")

        with pytest.raises(InvalidCredentialsError):
            self.use_case.execute(dto)

    def test_login_user_not_found(self):
        """Test: échec si utilisateur non trouvé."""
        self.mock_user_repo.find_by_email.return_value = None

        dto = LoginDTO(email="unknown@example.com", password="password123")

        with pytest.raises(InvalidCredentialsError):
            self.use_case.execute(dto)

    def test_login_wrong_password(self):
        """Test: échec si mot de passe incorrect."""
        self.mock_user_repo.find_by_email.return_value = self.test_user
        self.mock_password_service.verify.return_value = False

        dto = LoginDTO(email="test@example.com", password="wrong_password")

        with pytest.raises(InvalidCredentialsError):
            self.use_case.execute(dto)

    def test_login_inactive_user(self):
        """Test: échec si compte désactivé."""
        inactive_user = User(
            id=2,
            email=Email("inactive@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="MARTIN",
            prenom="Marie",
            role=Role.COMPAGNON,
            is_active=False,  # Compte désactivé
        )
        self.mock_user_repo.find_by_email.return_value = inactive_user

        dto = LoginDTO(email="inactive@example.com", password="password123")

        with pytest.raises(UserInactiveError):
            self.use_case.execute(dto)

    def test_login_publishes_event(self):
        """Test: publication d'un event après connexion réussie."""
        # Arrange
        mock_publisher = Mock()
        use_case_with_events = LoginUseCase(
            user_repo=self.mock_user_repo,
            password_service=self.mock_password_service,
            token_service=self.mock_token_service,
            event_publisher=mock_publisher,
        )

        self.mock_user_repo.find_by_email.return_value = self.test_user
        self.mock_password_service.verify.return_value = True
        self.mock_token_service.generate.return_value = "jwt_token"

        dto = LoginDTO(email="test@example.com", password="password123")

        # Act
        use_case_with_events.execute(dto)

        # Assert
        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.user_id == 1
        assert event.email == "test@example.com"
