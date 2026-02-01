"""Tests unitaires pour AcceptInvitationUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from modules.auth.domain.entities.user import User
from modules.auth.domain.value_objects.password_hash import PasswordHash
from modules.auth.domain.repositories.user_repository import UserRepository
from modules.auth.application.use_cases.accept_invitation import AcceptInvitationUseCase
from modules.auth.domain.exceptions import InvalidInvitationTokenError, WeakPasswordError
from shared.infrastructure.password_hasher import PasswordHasher


class TestAcceptInvitationUseCase:
    """Tests pour le use case d'acceptation d'invitation."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_password_hasher = Mock(spec=PasswordHasher)

        self.use_case = AcceptInvitationUseCase(
            user_repository=self.mock_user_repo,
            password_hasher=self.mock_password_hasher,
        )

    def test_accept_invitation_success(self):
        """Test: acceptation d'invitation réussie."""
        user = User(
            id=1,
            email="invited@example.com",
            nom="Invited",
            prenom="User",
            password_hash=None,
            role="employe",
            is_active=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        user.set_invitation_token("validtoken123", datetime.now() + timedelta(days=7))

        self.mock_user_repo.find_by_invitation_token.return_value = user
        self.mock_password_hasher.hash.return_value = "$2b$12$newhash"

        # Act
        self.use_case.execute(token="validtoken123", password="SecurePass123!")

        # Assert
        self.mock_user_repo.find_by_invitation_token.assert_called_once_with("validtoken123")
        self.mock_password_hasher.hash.assert_called_once_with("SecurePass123!")
        self.mock_user_repo.save.assert_called_once()

    def test_accept_invitation_token_not_found(self):
        """Test: échec si token non trouvé."""
        self.mock_user_repo.find_by_invitation_token.return_value = None

        with pytest.raises(InvalidInvitationTokenError, match="Token d'invitation invalide ou expiré"):
            self.use_case.execute(token="invalidtoken", password="SecurePass123!")

        self.mock_password_hasher.hash.assert_not_called()
        self.mock_user_repo.save.assert_not_called()

    def test_accept_invitation_token_expired(self):
        """Test: échec si token expiré."""
        user = User(
            id=1,
            email="invited@example.com",
            nom="Invited",
            prenom="User",
            password_hash=None,
            role="employe",
            is_active=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        user.set_invitation_token("expiredtoken123", datetime.now() - timedelta(days=8))

        self.mock_user_repo.find_by_invitation_token.return_value = user

        with pytest.raises(InvalidInvitationTokenError):
            self.use_case.execute(token="expiredtoken123", password="SecurePass123!")

        self.mock_password_hasher.hash.assert_not_called()
        self.mock_user_repo.save.assert_not_called()

    def test_accept_invitation_weak_password(self):
        """Test: échec si mot de passe trop faible."""
        user = User(
            id=1,
            email="invited@example.com",
            nom="Invited",
            prenom="User",
            password_hash=None,
            role="employe",
            is_active=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        user.set_invitation_token("validtoken123", datetime.now() + timedelta(days=7))

        self.mock_user_repo.find_by_invitation_token.return_value = user

        with pytest.raises(WeakPasswordError):
            self.use_case.execute(token="validtoken123", password="weak")

        self.mock_user_repo.save.assert_not_called()
