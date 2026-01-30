"""Tests unitaires pour ChangePasswordUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.auth.domain.entities.user import User
from modules.auth.domain.value_objects.password_hash import PasswordHash
from modules.auth.domain.repositories.user_repository import UserRepository
from modules.auth.application.use_cases.change_password import (
    ChangePasswordUseCase,
    ChangePasswordDTO,
    InvalidPasswordError,
    UserNotFoundError,
)
from modules.auth.domain.services.password_service import PasswordService


class TestChangePasswordUseCase:
    """Tests pour le use case de changement de mot de passe."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Arrange - Mocks des dépendances
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_password_service = Mock(spec=PasswordService)

        # Use case à tester
        self.use_case = ChangePasswordUseCase(
            user_repo=self.mock_user_repo,
            password_service=self.mock_password_service,
        )

    def test_change_password_success(self):
        """Test: changement de mot de passe réussi."""
        # Arrange
        old_password_hash = PasswordHash("$2b$12$oldhash")
        user = User(
            id=1,
            email="user@example.com",
            nom="Doe",
            prenom="John",
            password_hash=old_password_hash,
            role="employe",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.mock_user_repo.find_by_id.return_value = user
        self.mock_password_service.verify_password.return_value = True
        new_hash = PasswordHash("$2b$12$newhash")
        self.mock_password_service.hash_password.return_value = new_hash

        dto = ChangePasswordDTO(
            user_id=1,
            old_password="OldPass123!",
            new_password="NewPass456!"
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result is True
        self.mock_user_repo.find_by_id.assert_called_once_with(1)
        self.mock_password_service.verify_password.assert_called_once_with(
            "OldPass123!", old_password_hash
        )
        self.mock_password_service.hash_password.assert_called_once_with("NewPass456!")
        self.mock_user_repo.save.assert_called_once()

        # Vérifier que le hash a été mis à jour
        saved_user = self.mock_user_repo.save.call_args[0][0]
        assert saved_user.password_hash == new_hash

    def test_change_password_user_not_found(self):
        """Test: échec si utilisateur non trouvé."""
        # Arrange
        self.mock_user_repo.find_by_id.return_value = None

        dto = ChangePasswordDTO(
            user_id=999,
            old_password="OldPass123!",
            new_password="NewPass456!"
        )

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            self.use_case.execute(dto)

        self.mock_user_repo.find_by_id.assert_called_once_with(999)
        self.mock_password_service.verify_password.assert_not_called()

    def test_change_password_incorrect_old_password(self):
        """Test: échec si ancien mot de passe incorrect."""
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

        self.mock_user_repo.find_by_id.return_value = user
        self.mock_password_service.verify_password.return_value = False

        dto = ChangePasswordDTO(
            user_id=1,
            old_password="WrongPassword",
            new_password="NewPass456!"
        )

        # Act & Assert
        with pytest.raises(InvalidPasswordError, match="Ancien mot de passe incorrect"):
            self.use_case.execute(dto)

        self.mock_password_service.hash_password.assert_not_called()
        self.mock_user_repo.save.assert_not_called()

    def test_change_password_weak_new_password(self):
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

        self.mock_user_repo.find_by_id.return_value = user
        self.mock_password_service.verify_password.return_value = True
        self.mock_password_service.hash_password.side_effect = ValueError("Mot de passe trop faible")

        dto = ChangePasswordDTO(
            user_id=1,
            old_password="OldPass123!",
            new_password="weak"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Mot de passe trop faible"):
            self.use_case.execute(dto)

        self.mock_user_repo.save.assert_not_called()

    def test_change_password_same_as_old(self):
        """Test: échec si nouveau mot de passe identique à l'ancien."""
        # Arrange
        user = User(
            id=1,
            email="user@example.com",
            nom="Doe",
            prenom="John",
            password_hash=PasswordHash("$2b$12$samehash"),
            role="employe",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.mock_user_repo.find_by_id.return_value = user
        # Vérifie l'ancien ET le nouveau (identiques)
        self.mock_password_service.verify_password.return_value = True

        dto = ChangePasswordDTO(
            user_id=1,
            old_password="SamePass123!",
            new_password="SamePass123!"
        )

        # Act & Assert
        with pytest.raises(InvalidPasswordError, match="Le nouveau mot de passe doit être différent"):
            self.use_case.execute(dto)

        self.mock_password_service.hash_password.assert_not_called()
        self.mock_user_repo.save.assert_not_called()
