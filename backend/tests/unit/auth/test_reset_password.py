"""Tests unitaires pour ResetPasswordUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from modules.auth.domain.entities.user import User
from modules.auth.domain.value_objects.password_hash import PasswordHash
from modules.auth.domain.repositories.user_repository import UserRepository
from modules.auth.application.use_cases.reset_password import ResetPasswordUseCase
from modules.auth.domain.exceptions import InvalidResetTokenError, WeakPasswordError
from shared.infrastructure.password_hasher import PasswordHasher


class TestResetPasswordUseCase:
    """Tests pour le use case de réinitialisation de mot de passe."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_password_hasher = Mock(spec=PasswordHasher)

        self.use_case = ResetPasswordUseCase(
            user_repository=self.mock_user_repo,
            password_hasher=self.mock_password_hasher,
        )

    def test_reset_password_success(self):
        """Test: réinitialisation de mot de passe réussie."""
        user = User(
            id=1,
            email="user@example.com",
            nom="Doe",
            prenom="John",
            password_hash=PasswordHash("$2b$12$oldhash"),
            role="employe",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        user.set_password_reset_token("validtoken123", datetime.now() + timedelta(hours=1))

        self.mock_user_repo.find_by_password_reset_token.return_value = user
        self.mock_password_hasher.hash.return_value = "$2b$12$newhash"

        # Act
        self.use_case.execute(token="validtoken123", new_password="NewSecurePass123!")

        # Assert
        self.mock_user_repo.find_by_password_reset_token.assert_called_once_with("validtoken123")
        self.mock_password_hasher.hash.assert_called_once_with("NewSecurePass123!")
        self.mock_user_repo.save.assert_called_once()

    def test_reset_password_token_not_found(self):
        """Test: échec si token non trouvé."""
        self.mock_user_repo.find_by_password_reset_token.return_value = None

        with pytest.raises(InvalidResetTokenError):
            self.use_case.execute(token="invalidtoken", new_password="NewSecurePass123!")

        self.mock_password_hasher.hash.assert_not_called()
        self.mock_user_repo.save.assert_not_called()

    def test_reset_password_token_expired(self):
        """Test: échec si token expiré."""
        user = User(
            id=1,
            email="user@example.com",
            nom="Doe",
            prenom="John",
            password_hash=PasswordHash("$2b$12$oldhash"),
            role="employe",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        user.set_password_reset_token("expiredtoken", datetime.now() - timedelta(hours=2))

        self.mock_user_repo.find_by_password_reset_token.return_value = user

        with pytest.raises(InvalidResetTokenError):
            self.use_case.execute(token="expiredtoken", new_password="NewSecurePass123!")

        self.mock_password_hasher.hash.assert_not_called()
        self.mock_user_repo.save.assert_not_called()

    def test_reset_password_weak_password(self):
        """Test: échec si mot de passe trop faible."""
        user = User(
            id=1,
            email="user@example.com",
            nom="Doe",
            prenom="John",
            password_hash=PasswordHash("$2b$12$oldhash"),
            role="employe",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        user.set_password_reset_token("validtoken", datetime.now() + timedelta(hours=1))

        self.mock_user_repo.find_by_password_reset_token.return_value = user

        with pytest.raises(WeakPasswordError):
            self.use_case.execute(token="validtoken", new_password="weak")

        self.mock_user_repo.save.assert_not_called()
