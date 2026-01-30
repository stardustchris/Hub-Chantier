"""Tests unitaires pour AcceptInvitationUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from modules.auth.domain.entities.user import User
from modules.auth.domain.value_objects.password_hash import PasswordHash
from modules.auth.domain.repositories.user_repository import UserRepository
from modules.auth.application.use_cases.accept_invitation import (
    AcceptInvitationUseCase,
    AcceptInvitationDTO,
    InvalidInvitationTokenError,
)
from modules.auth.domain.services.password_service import PasswordService


class TestAcceptInvitationUseCase:
    """Tests pour le use case d'acceptation d'invitation."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Arrange - Mocks des dépendances
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_password_service = Mock(spec=PasswordService)

        # Use case à tester
        self.use_case = AcceptInvitationUseCase(
            user_repo=self.mock_user_repo,
            password_service=self.mock_password_service,
        )

    def test_accept_invitation_success(self):
        """Test: acceptation d'invitation réussie."""
        # Arrange
        user = User(
            id=1,
            email="invited@example.com",
            nom="Invited",
            prenom="User",
            password_hash=None,  # Pas encore de mot de passe
            role="employe",
            is_active=False,  # Pas encore activé
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Token d'invitation valide
        user.set_invitation_token("validtoken123", datetime.now() + timedelta(days=7))

        self.mock_user_repo.find_by_invitation_token.return_value = user
        new_hash = PasswordHash("$2b$12$newhash")
        self.mock_password_service.hash_password.return_value = new_hash

        dto = AcceptInvitationDTO(
            token="validtoken123",
            password="SecurePass123!"
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result is not None
        assert result.email == "invited@example.com"
        assert result.is_active is True  # Maintenant activé

        self.mock_user_repo.find_by_invitation_token.assert_called_once_with("validtoken123")
        self.mock_password_service.hash_password.assert_called_once_with("SecurePass123!")
        self.mock_user_repo.save.assert_called_once()

        # Vérifier que le compte a été activé et le token effacé
        saved_user = self.mock_user_repo.save.call_args[0][0]
        assert saved_user.password_hash == new_hash
        assert saved_user.is_active is True
        assert saved_user.invitation_token is None
        assert saved_user.invitation_expires_at is None

    def test_accept_invitation_token_not_found(self):
        """Test: échec si token non trouvé."""
        # Arrange
        self.mock_user_repo.find_by_invitation_token.return_value = None

        dto = AcceptInvitationDTO(
            token="invalidtoken",
            password="SecurePass123!"
        )

        # Act & Assert
        with pytest.raises(InvalidInvitationTokenError, match="Token d'invitation invalide ou expiré"):
            self.use_case.execute(dto)

        self.mock_password_service.hash_password.assert_not_called()
        self.mock_user_repo.save.assert_not_called()

    def test_accept_invitation_token_expired(self):
        """Test: échec si token expiré."""
        # Arrange
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

        # Token expiré (il y a 8 jours)
        user.set_invitation_token("expiredtoken123", datetime.now() - timedelta(days=8))

        self.mock_user_repo.find_by_invitation_token.return_value = user

        dto = AcceptInvitationDTO(
            token="expiredtoken123",
            password="SecurePass123!"
        )

        # Act & Assert
        with pytest.raises(InvalidInvitationTokenError, match="Token d'invitation invalide ou expiré"):
            self.use_case.execute(dto)

        self.mock_password_service.hash_password.assert_not_called()
        self.mock_user_repo.save.assert_not_called()

    def test_accept_invitation_weak_password(self):
        """Test: échec si mot de passe trop faible."""
        # Arrange
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
        self.mock_password_service.hash_password.side_effect = ValueError("Mot de passe trop faible")

        dto = AcceptInvitationDTO(
            token="validtoken123",
            password="weak"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Mot de passe trop faible"):
            self.use_case.execute(dto)

        self.mock_user_repo.save.assert_not_called()

    def test_accept_invitation_already_accepted(self):
        """Test: échec si invitation déjà acceptée (compte actif)."""
        # Arrange
        user = User(
            id=1,
            email="invited@example.com",
            nom="Invited",
            prenom="User",
            password_hash=PasswordHash("$2b$12$existinghash"),  # Déjà un mot de passe
            role="employe",
            is_active=True,  # Déjà activé
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Token existe encore (pas été nettoyé)
        user.set_invitation_token("usedtoken123", datetime.now() + timedelta(days=7))

        self.mock_user_repo.find_by_invitation_token.return_value = user

        dto = AcceptInvitationDTO(
            token="usedtoken123",
            password="SecurePass123!"
        )

        # Act & Assert
        with pytest.raises(InvalidInvitationTokenError, match="Cette invitation a déjà été acceptée"):
            self.use_case.execute(dto)

        self.mock_password_service.hash_password.assert_not_called()
        self.mock_user_repo.save.assert_not_called()

    def test_accept_invitation_sets_email_verified(self):
        """Test: accepter l'invitation vérifie automatiquement l'email."""
        # Arrange
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
        new_hash = PasswordHash("$2b$12$newhash")
        self.mock_password_service.hash_password.return_value = new_hash

        dto = AcceptInvitationDTO(
            token="validtoken123",
            password="SecurePass123!"
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        saved_user = self.mock_user_repo.save.call_args[0][0]
        assert saved_user.email_verified is True  # Email vérifié automatiquement
        assert saved_user.email_verified_at is not None

    def test_accept_invitation_token_single_use(self):
        """Test: le token est effacé après utilisation."""
        # Arrange
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
        new_hash = PasswordHash("$2b$12$newhash")
        self.mock_password_service.hash_password.return_value = new_hash

        dto = AcceptInvitationDTO(
            token="validtoken123",
            password="SecurePass123!"
        )

        # Act
        self.use_case.execute(dto)

        # Assert
        saved_user = self.mock_user_repo.save.call_args[0][0]
        assert saved_user.invitation_token is None
        assert saved_user.invitation_expires_at is None

        # Une 2ème tentative avec le même token devrait échouer
        self.mock_user_repo.find_by_invitation_token.return_value = None

        with pytest.raises(InvalidInvitationTokenError):
            self.use_case.execute(dto)

    def test_accept_invitation_role_preserved(self):
        """Test: le rôle défini lors de l'invitation est préservé."""
        # Arrange
        user = User(
            id=1,
            email="chef@example.com",
            nom="Chef",
            prenom="Chantier",
            password_hash=None,
            role="chef_chantier",  # Rôle spécial défini lors de l'invitation
            is_active=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        user.set_invitation_token("validtoken123", datetime.now() + timedelta(days=7))

        self.mock_user_repo.find_by_invitation_token.return_value = user
        new_hash = PasswordHash("$2b$12$newhash")
        self.mock_password_service.hash_password.return_value = new_hash

        dto = AcceptInvitationDTO(
            token="validtoken123",
            password="SecurePass123!"
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.role == "chef_chantier"  # Rôle préservé
        saved_user = self.mock_user_repo.save.call_args[0][0]
        assert saved_user.role == "chef_chantier"
