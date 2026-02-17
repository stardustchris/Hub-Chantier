"""Tests unitaires pour InviteUserUseCase."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from modules.auth.domain.entities.user import User
from modules.auth.domain.value_objects import Email, Role, TypeUtilisateur, PasswordHash
from modules.auth.domain.repositories.user_repository import UserRepository
from modules.auth.application.use_cases.invite_user import InviteUserUseCase
from modules.auth.domain.exceptions import EmailAlreadyExistsError, CodeAlreadyExistsError


class TestInviteUserUseCase:
    """Tests pour le use case d'invitation utilisateur."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_email_service = Mock()
        self.use_case = InviteUserUseCase(
            user_repository=self.mock_user_repo,
            email_service=self.mock_email_service,
        )

    def test_invite_user_success(self):
        """Test: invitation réussie d'un nouvel utilisateur."""
        self.mock_user_repo.exists_by_email.return_value = False
        self.mock_user_repo.exists_by_code.return_value = False

        # Mock du save
        invited_user = User(
            id=1,
            email=Email("newuser@example.com"),
            password_hash=PasswordHash("TEMPORARY_HASH"),
            nom="Nouveau",
            prenom="User",
            role=Role.COMPAGNON,
            type_utilisateur=TypeUtilisateur.EMPLOYE,
            is_active=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_user_repo.save.return_value = invited_user

        # Act
        result = self.use_case.execute(
            email="newuser@example.com",
            nom="Nouveau",
            prenom="User",
            role=Role.COMPAGNON,
        )

        # Assert
        assert result is not None
        assert result.email.value == "newuser@example.com"
        assert result.is_active is False

        self.mock_user_repo.exists_by_email.assert_called_once()
        self.mock_user_repo.save.assert_called_once()
        self.mock_email_service.send_invitation_email.assert_called_once()

    def test_invite_user_email_already_exists(self):
        """Test: échec si l'email existe déjà."""
        self.mock_user_repo.exists_by_email.return_value = True

        with pytest.raises(EmailAlreadyExistsError):
            self.use_case.execute(
                email="existing@example.com",
                nom="Existing",
                prenom="User",
                role=Role.COMPAGNON,
            )

        self.mock_user_repo.save.assert_not_called()

    def test_invite_user_code_already_exists(self):
        """Test: échec si le code utilisateur existe déjà."""
        self.mock_user_repo.exists_by_email.return_value = False
        self.mock_user_repo.exists_by_code.return_value = True

        with pytest.raises(CodeAlreadyExistsError):
            self.use_case.execute(
                email="newuser@example.com",
                nom="New",
                prenom="User",
                role=Role.COMPAGNON,
                code_utilisateur="EMP001",
            )

        self.mock_user_repo.save.assert_not_called()
