"""Tests unitaires pour ResetPasswordUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from modules.auth.domain.entities.user import User
from modules.auth.domain.value_objects.password_hash import PasswordHash
from modules.auth.domain.repositories.user_repository import UserRepository
from modules.auth.application.use_cases.reset_password import (
    ResetPasswordUseCase,
    ResetPasswordDTO,
    InvalidResetTokenError,
)
from modules.auth.domain.services.password_service import PasswordService


class TestResetPasswordUseCase:
    """Tests pour le use case de réinitialisation de mot de passe."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Arrange - Mocks des dépendances
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_password_service = Mock(spec=PasswordService)

        # Use case à tester
        self.use_case = ResetPasswordUseCase(
            user_repo=self.mock_user_repo,
            password_service=self.mock_password_service,
        )

    def test_reset_password_success(self):
        """Test: réinitialisation de mot de passe réussie."""
        # Arrange
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

        # Token valide
        user.set_password_reset_token("validtoken123", datetime.now() + timedelta(hours=1))

        self.mock_user_repo.find_by_password_reset_token.return_value = user
        new_hash = PasswordHash("$2b$12$newhash")
        self.mock_password_service.hash_password.return_value = new_hash

        dto = ResetPasswordDTO(
            token="validtoken123",
            new_password="NewSecurePass123!"
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result is True
        self.mock_user_repo.find_by_password_reset_token.assert_called_once_with("validtoken123")
        self.mock_password_service.hash_password.assert_called_once_with("NewSecurePass123!")
        self.mock_user_repo.save.assert_called_once()

        # Vérifier que le mot de passe a été mis à jour et le token effacé
        saved_user = self.mock_user_repo.save.call_args[0][0]
        assert saved_user.password_hash == new_hash
        assert saved_user.password_reset_token is None
        assert saved_user.password_reset_expires_at is None

    def test_reset_password_token_not_found(self):
        """Test: échec si token non trouvé."""
        # Arrange
        self.mock_user_repo.find_by_password_reset_token.return_value = None

        dto = ResetPasswordDTO(
            token="invalidtoken",
            new_password="NewSecurePass123!"
        )

        # Act & Assert
        with pytest.raises(InvalidResetTokenError, match="Token invalide ou expiré"):
            self.use_case.execute(dto)

        self.mock_password_service.hash_password.assert_not_called()
        self.mock_user_repo.save.assert_not_called()

    def test_reset_password_token_expired(self):
        """Test: échec si token expiré."""
        # Arrange
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

        # Token expiré (il y a 2 heures)
        user.set_password_reset_token("expiredtoken123", datetime.now() - timedelta(hours=2))

        self.mock_user_repo.find_by_password_reset_token.return_value = user

        dto = ResetPasswordDTO(
            token="expiredtoken123",
            new_password="NewSecurePass123!"
        )

        # Act & Assert
        with pytest.raises(InvalidResetTokenError, match="Token invalide ou expiré"):
            self.use_case.execute(dto)

        self.mock_password_service.hash_password.assert_not_called()
        self.mock_user_repo.save.assert_not_called()

    def test_reset_password_weak_password(self):
        """Test: échec si nouveau mot de passe trop faible."""
        # Arrange
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
        self.mock_password_service.hash_password.side_effect = ValueError("Mot de passe trop faible")

        dto = ResetPasswordDTO(
            token="validtoken123",
            new_password="weak"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Mot de passe trop faible"):
            self.use_case.execute(dto)

        self.mock_user_repo.save.assert_not_called()

    def test_reset_password_inactive_user(self):
        """Test: peut réinitialiser même si utilisateur inactif."""
        # Arrange
        user = User(
            id=1,
            email="user@example.com",
            nom="Doe",
            prenom="John",
            password_hash=PasswordHash("$2b$12$oldhash"),
            role="employe",
            is_active=False,  # Inactif
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        user.set_password_reset_token("validtoken123", datetime.now() + timedelta(hours=1))

        self.mock_user_repo.find_by_password_reset_token.return_value = user
        new_hash = PasswordHash("$2b$12$newhash")
        self.mock_password_service.hash_password.return_value = new_hash

        dto = ResetPasswordDTO(
            token="validtoken123",
            new_password="NewSecurePass123!"
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result is True  # Permet la réinitialisation même si inactif
        self.mock_user_repo.save.assert_called_once()

    def test_reset_password_token_single_use(self):
        """Test: le token est effacé après utilisation."""
        # Arrange
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
        new_hash = PasswordHash("$2b$12$newhash")
        self.mock_password_service.hash_password.return_value = new_hash

        dto = ResetPasswordDTO(
            token="validtoken123",
            new_password="NewSecurePass123!"
        )

        # Act
        self.use_case.execute(dto)

        # Assert
        saved_user = self.mock_user_repo.save.call_args[0][0]
        assert saved_user.password_reset_token is None
        assert saved_user.password_reset_expires_at is None

        # Une 2ème tentative avec le même token devrait échouer
        self.mock_user_repo.find_by_password_reset_token.return_value = None

        with pytest.raises(InvalidResetTokenError):
            self.use_case.execute(dto)
