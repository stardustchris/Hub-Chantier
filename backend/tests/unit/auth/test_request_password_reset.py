"""Tests unitaires pour RequestPasswordResetUseCase."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from modules.auth.domain.entities.user import User
from modules.auth.domain.value_objects import Email, PasswordHash
from modules.auth.domain.repositories.user_repository import UserRepository
from modules.auth.application.use_cases.request_password_reset import RequestPasswordResetUseCase


class TestRequestPasswordResetUseCase:
    """Tests pour le use case de demande de réinitialisation de mot de passe."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_email_service = Mock()
        self.use_case = RequestPasswordResetUseCase(
            user_repository=self.mock_user_repo,
            email_service=self.mock_email_service,
        )

    def test_request_password_reset_success(self):
        """Test: demande de réinitialisation réussie."""
        user = User(
            id=1,
            email=Email("user@example.com"),
            nom="Doe",
            prenom="John",
            password_hash=PasswordHash("$2b$12$hash"),
            role="admin",
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
        self.mock_user_repo.save.assert_called_once()
        self.mock_email_service.send_password_reset_email.assert_called_once()

    def test_request_password_reset_user_not_found_returns_true(self):
        """Test: retourne True même si utilisateur non trouvé (anti-énumération)."""
        self.mock_user_repo.find_by_email.return_value = None

        result = self.use_case.execute(email="nonexistent@example.com")

        assert result is True
        self.mock_user_repo.save.assert_not_called()
        self.mock_email_service.send_password_reset_email.assert_not_called()
