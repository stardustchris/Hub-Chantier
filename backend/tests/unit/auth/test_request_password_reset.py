"""Tests unitaires pour RequestPasswordResetUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from modules.auth.domain.entities.user import User
from modules.auth.domain.value_objects.password_hash import PasswordHash
from modules.auth.domain.repositories.user_repository import UserRepository
from modules.auth.application.use_cases.request_password_reset import (
    RequestPasswordResetUseCase,
)
from shared.infrastructure.email_service import EmailService


class TestRequestPasswordResetUseCase:
    """Tests pour le use case de demande de réinitialisation de mot de passe."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Arrange - Mocks des dépendances
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_email_service = Mock(spec=EmailService)

        # Use case à tester
        self.use_case = RequestPasswordResetUseCase(
            user_repo=self.mock_user_repo,
            email_service=self.mock_email_service,
        )

    def test_request_password_reset_success(self):
        """Test: demande de réinitialisation réussie."""
        # Arrange
        user = User(
            id=1,
            email="user@example.com",
            nom="Doe",
            prenom="John",
            password_hash=PasswordHash("$2b$12$hash"),
            role="employe",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.mock_user_repo.find_by_email.return_value = user
        self.mock_email_service.send_password_reset_email.return_value = True

        # Act
        result = self.use_case.execute(email="user@example.com")

        # Assert
        assert result is True
        self.mock_user_repo.find_by_email.assert_called_once_with("user@example.com")
        self.mock_user_repo.save.assert_called_once()

        # Vérifier que le token a été généré
        saved_user = self.mock_user_repo.save.call_args[0][0]
        assert saved_user.password_reset_token is not None
        assert saved_user.password_reset_expires_at is not None
        assert saved_user.password_reset_expires_at > datetime.now()

        # Vérifier que l'email a été envoyé
        self.mock_email_service.send_password_reset_email.assert_called_once()
        call_args = self.mock_email_service.send_password_reset_email.call_args
        assert call_args[1]['to'] == "user@example.com"
        assert 'token' in call_args[1]
        assert call_args[1]['user_name'] == "John Doe"

    def test_request_password_reset_user_not_found_returns_true(self):
        """Test: retourne True même si utilisateur non trouvé (anti-énumération)."""
        # Arrange
        self.mock_user_repo.find_by_email.return_value = None

        # Act
        result = self.use_case.execute(email="nonexistent@example.com")

        # Assert
        assert result is True  # Ne révèle pas l'existence de l'utilisateur
        self.mock_user_repo.find_by_email.assert_called_once_with("nonexistent@example.com")
        self.mock_user_repo.save.assert_not_called()
        self.mock_email_service.send_password_reset_email.assert_not_called()

    def test_request_password_reset_inactive_user_returns_true(self):
        """Test: retourne True même si utilisateur inactif (anti-énumération)."""
        # Arrange
        user = User(
            id=1,
            email="inactive@example.com",
            nom="Inactive",
            prenom="User",
            password_hash=PasswordHash("$2b$12$hash"),
            role="employe",
            is_active=False,  # Inactif
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.mock_user_repo.find_by_email.return_value = user

        # Act
        result = self.use_case.execute(email="inactive@example.com")

        # Assert
        assert result is True  # Ne révèle pas l'état de l'utilisateur
        self.mock_user_repo.save.assert_not_called()
        self.mock_email_service.send_password_reset_email.assert_not_called()

    def test_request_password_reset_email_failure_returns_true(self):
        """Test: retourne True même si envoi email échoue (anti-énumération)."""
        # Arrange
        user = User(
            id=1,
            email="user@example.com",
            nom="Doe",
            prenom="John",
            password_hash=PasswordHash("$2b$12$hash"),
            role="employe",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.mock_user_repo.find_by_email.return_value = user
        self.mock_email_service.send_password_reset_email.return_value = False  # Échec

        # Act
        result = self.use_case.execute(email="user@example.com")

        # Assert
        assert result is True  # Toujours True pour l'utilisateur
        self.mock_user_repo.save.assert_called_once()  # Token quand même sauvegardé

    def test_request_password_reset_token_expiration(self):
        """Test: le token expire après 1 heure."""
        # Arrange
        user = User(
            id=1,
            email="user@example.com",
            nom="Doe",
            prenom="John",
            password_hash=PasswordHash("$2b$12$hash"),
            role="employe",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.mock_user_repo.find_by_email.return_value = user
        self.mock_email_service.send_password_reset_email.return_value = True

        # Act
        self.use_case.execute(email="user@example.com")

        # Assert
        saved_user = self.mock_user_repo.save.call_args[0][0]
        time_diff = saved_user.password_reset_expires_at - datetime.now()

        # Le token doit expirer dans ~1 heure (avec marge de 5 minutes)
        assert timedelta(minutes=55) < time_diff < timedelta(minutes=65)

    def test_request_password_reset_replaces_old_token(self):
        """Test: remplace un ancien token existant."""
        # Arrange
        user = User(
            id=1,
            email="user@example.com",
            nom="Doe",
            prenom="John",
            password_hash=PasswordHash("$2b$12$hash"),
            role="employe",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Ancien token existant
        user.set_password_reset_token("oldtoken123", datetime.now() + timedelta(hours=1))
        old_token = user.password_reset_token

        self.mock_user_repo.find_by_email.return_value = user
        self.mock_email_service.send_password_reset_email.return_value = True

        # Act
        self.use_case.execute(email="user@example.com")

        # Assert
        saved_user = self.mock_user_repo.save.call_args[0][0]
        assert saved_user.password_reset_token != old_token  # Token changé
        assert saved_user.password_reset_token is not None
