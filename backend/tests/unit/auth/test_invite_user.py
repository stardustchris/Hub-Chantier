"""Tests unitaires pour InviteUserUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from modules.auth.domain.entities.user import User
from modules.auth.domain.value_objects.password_hash import PasswordHash
from modules.auth.domain.repositories.user_repository import UserRepository
from modules.auth.application.use_cases.invite_user import (
    InviteUserUseCase,
    InviteUserDTO,
    EmailAlreadyExistsError,
)
from shared.infrastructure.email_service import EmailService


class TestInviteUserUseCase:
    """Tests pour le use case d'invitation d'un utilisateur."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Arrange - Mocks des dépendances
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_email_service = Mock(spec=EmailService)

        # Use case à tester
        self.use_case = InviteUserUseCase(
            user_repo=self.mock_user_repo,
            email_service=self.mock_email_service,
        )

    def test_invite_user_success(self):
        """Test: invitation d'utilisateur réussie."""
        # Arrange
        self.mock_user_repo.find_by_email.return_value = None  # Email disponible
        self.mock_email_service.send_invitation_email.return_value = True

        dto = InviteUserDTO(
            email="newuser@example.com",
            nom="Nouveau",
            prenom="User",
            role="employe",
            invited_by_user_id=1,
            invited_by_name="Admin User"
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result is not None
        assert result.email == "newuser@example.com"
        assert result.nom == "Nouveau"
        assert result.prenom == "User"
        assert result.role == "employe"
        assert result.is_active is False  # Pas encore activé

        self.mock_user_repo.find_by_email.assert_called_once_with("newuser@example.com")
        self.mock_user_repo.save.assert_called_once()

        # Vérifier que le token d'invitation a été généré
        saved_user = self.mock_user_repo.save.call_args[0][0]
        assert saved_user.invitation_token is not None
        assert saved_user.invitation_expires_at is not None
        assert saved_user.invitation_expires_at > datetime.now()

        # Vérifier que l'email a été envoyé
        self.mock_email_service.send_invitation_email.assert_called_once()
        call_args = self.mock_email_service.send_invitation_email.call_args
        assert call_args[1]['to'] == "newuser@example.com"
        assert 'token' in call_args[1]
        assert call_args[1]['user_name'] == "User Nouveau"
        assert call_args[1]['inviter_name'] == "Admin User"

    def test_invite_user_email_already_exists(self):
        """Test: échec si email déjà utilisé."""
        # Arrange
        existing_user = User(
            id=2,
            email="existing@example.com",
            nom="Existing",
            prenom="User",
            password_hash=PasswordHash("$2b$12$hash"),
            role="employe",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.mock_user_repo.find_by_email.return_value = existing_user

        dto = InviteUserDTO(
            email="existing@example.com",
            nom="New",
            prenom="User",
            role="employe",
            invited_by_user_id=1,
            invited_by_name="Admin User"
        )

        # Act & Assert
        with pytest.raises(EmailAlreadyExistsError, match="Cet email est déjà utilisé"):
            self.use_case.execute(dto)

        self.mock_user_repo.save.assert_not_called()
        self.mock_email_service.send_invitation_email.assert_not_called()

    def test_invite_user_token_expiration(self):
        """Test: le token d'invitation expire après 7 jours."""
        # Arrange
        self.mock_user_repo.find_by_email.return_value = None
        self.mock_email_service.send_invitation_email.return_value = True

        dto = InviteUserDTO(
            email="newuser@example.com",
            nom="Nouveau",
            prenom="User",
            role="employe",
            invited_by_user_id=1,
            invited_by_name="Admin User"
        )

        # Act
        self.use_case.execute(dto)

        # Assert
        saved_user = self.mock_user_repo.save.call_args[0][0]
        time_diff = saved_user.invitation_expires_at - datetime.now()

        # Le token doit expirer dans ~7 jours (avec marge de 1 heure)
        assert timedelta(days=6, hours=23) < time_diff < timedelta(days=7, hours=1)

    def test_invite_user_default_role(self):
        """Test: rôle par défaut est 'employe'."""
        # Arrange
        self.mock_user_repo.find_by_email.return_value = None
        self.mock_email_service.send_invitation_email.return_value = True

        dto = InviteUserDTO(
            email="newuser@example.com",
            nom="Nouveau",
            prenom="User",
            role=None,  # Pas de rôle spécifié
            invited_by_user_id=1,
            invited_by_name="Admin User"
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.role == "employe"  # Rôle par défaut

    def test_invite_user_admin_role(self):
        """Test: peut inviter un administrateur."""
        # Arrange
        self.mock_user_repo.find_by_email.return_value = None
        self.mock_email_service.send_invitation_email.return_value = True

        dto = InviteUserDTO(
            email="admin@example.com",
            nom="Admin",
            prenom="User",
            role="admin",
            invited_by_user_id=1,
            invited_by_name="Super Admin"
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.role == "admin"
        saved_user = self.mock_user_repo.save.call_args[0][0]
        assert saved_user.role == "admin"

    def test_invite_user_email_failure(self):
        """Test: échec si envoi email échoue."""
        # Arrange
        self.mock_user_repo.find_by_email.return_value = None
        self.mock_email_service.send_invitation_email.return_value = False  # Échec

        dto = InviteUserDTO(
            email="newuser@example.com",
            nom="Nouveau",
            prenom="User",
            role="employe",
            invited_by_user_id=1,
            invited_by_name="Admin User"
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result is not None  # L'utilisateur est quand même créé
        self.mock_user_repo.save.assert_called_once()
        # Note: dans une vraie implémentation, on pourrait vouloir logger l'échec

    def test_invite_user_creates_inactive_account(self):
        """Test: le compte créé est inactif jusqu'à acceptation de l'invitation."""
        # Arrange
        self.mock_user_repo.find_by_email.return_value = None
        self.mock_email_service.send_invitation_email.return_value = True

        dto = InviteUserDTO(
            email="newuser@example.com",
            nom="Nouveau",
            prenom="User",
            role="employe",
            invited_by_user_id=1,
            invited_by_name="Admin User"
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.is_active is False
        saved_user = self.mock_user_repo.save.call_args[0][0]
        assert saved_user.is_active is False
        assert saved_user.password_hash is None  # Pas encore de mot de passe
