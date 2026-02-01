"""Tests unitaires pour ChangePasswordUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.auth.domain.entities.user import User
from modules.auth.domain.value_objects.password_hash import PasswordHash
from modules.auth.domain.repositories.user_repository import UserRepository
from modules.auth.application.use_cases.change_password import ChangePasswordUseCase
from modules.auth.domain.exceptions import (
    UserNotFoundError,
    InvalidCredentialsError,
    WeakPasswordError,
)
from shared.infrastructure.password_hasher import PasswordHasher


class TestChangePasswordUseCase:
    """Tests pour le use case de changement de mot de passe."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_password_hasher = Mock(spec=PasswordHasher)

        self.use_case = ChangePasswordUseCase(
            user_repository=self.mock_user_repo,
            password_hasher=self.mock_password_hasher,
        )

    def test_change_password_success(self):
        """Test: changement de mot de passe réussi."""
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
        self.mock_password_hasher.verify.return_value = True
        self.mock_password_hasher.hash.return_value = "$2b$12$newhash"

        # Act
        self.use_case.execute(
            user_id=1,
            old_password="OldPass123!",
            new_password="NewSecurePass123!",
        )

        # Assert
        self.mock_user_repo.find_by_id.assert_called_once_with(1)
        self.mock_password_hasher.verify.assert_called_once()
        self.mock_password_hasher.hash.assert_called_once_with("NewSecurePass123!")
        self.mock_user_repo.save.assert_called_once()

    def test_change_password_user_not_found(self):
        """Test: échec si utilisateur non trouvé."""
        self.mock_user_repo.find_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            self.use_case.execute(
                user_id=999,
                old_password="OldPass123!",
                new_password="NewSecurePass123!",
            )

        self.mock_password_hasher.verify.assert_not_called()
        self.mock_user_repo.save.assert_not_called()

    def test_change_password_incorrect_old_password(self):
        """Test: échec si ancien mot de passe incorrect."""
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
        self.mock_password_hasher.verify.return_value = False

        with pytest.raises(InvalidCredentialsError):
            self.use_case.execute(
                user_id=1,
                old_password="WrongPass123!",
                new_password="NewSecurePass123!",
            )

        self.mock_password_hasher.hash.assert_not_called()
        self.mock_user_repo.save.assert_not_called()

    def test_change_password_weak_new_password(self):
        """Test: échec si nouveau mot de passe trop faible."""
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
        self.mock_password_hasher.verify.return_value = True

        with pytest.raises(WeakPasswordError):
            self.use_case.execute(
                user_id=1,
                old_password="OldPass123!",
                new_password="weak",
            )

        self.mock_user_repo.save.assert_not_called()

    def test_change_password_same_as_old(self):
        """Test: échec si nouveau mot de passe identique à l'ancien."""
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
        self.mock_password_hasher.verify.return_value = True

        with pytest.raises(WeakPasswordError, match="doit être différent"):
            self.use_case.execute(
                user_id=1,
                old_password="SamePass123!",
                new_password="SamePass123!",
            )

        self.mock_user_repo.save.assert_not_called()
