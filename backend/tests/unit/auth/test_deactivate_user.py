"""Tests unitaires pour DeactivateUserUseCase et ActivateUserUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.auth.domain.entities import User
from modules.auth.domain.value_objects import Email, PasswordHash, Role
from modules.auth.domain.repositories import UserRepository
from modules.auth.application.use_cases.deactivate_user import (
    DeactivateUserUseCase,
    ActivateUserUseCase,
    UserNotFoundError,
)


class TestDeactivateUserUseCase:
    """Tests pour le use case de désactivation utilisateur."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_user_repo = Mock(spec=UserRepository)
        self.use_case = DeactivateUserUseCase(user_repo=self.mock_user_repo)

        self.test_user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed_password"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def test_deactivate_user_success(self):
        """Test: désactivation réussie."""
        self.mock_user_repo.find_by_id.return_value = self.test_user
        self.mock_user_repo.save.return_value = self.test_user

        result = self.use_case.execute(1)

        assert result.id == 1
        self.mock_user_repo.find_by_id.assert_called_once_with(1)
        self.mock_user_repo.save.assert_called_once()

    def test_deactivate_user_not_found(self):
        """Test: échec si utilisateur non trouvé."""
        self.mock_user_repo.find_by_id.return_value = None

        with pytest.raises(UserNotFoundError) as exc_info:
            self.use_case.execute(999)

        assert exc_info.value.user_id == 999

    def test_deactivate_user_publishes_event(self):
        """Test: publication d'un event après désactivation."""
        mock_publisher = Mock()
        use_case = DeactivateUserUseCase(
            user_repo=self.mock_user_repo,
            event_publisher=mock_publisher,
        )

        self.mock_user_repo.find_by_id.return_value = self.test_user
        self.mock_user_repo.save.return_value = self.test_user

        use_case.execute(1)

        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.user_id == 1
        assert event.email == "test@example.com"


class TestActivateUserUseCase:
    """Tests pour le use case d'activation utilisateur."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_user_repo = Mock(spec=UserRepository)
        self.use_case = ActivateUserUseCase(user_repo=self.mock_user_repo)

        self.inactive_user = User(
            id=2,
            email=Email("inactive@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="MARTIN",
            prenom="Marie",
            role=Role.COMPAGNON,
            is_active=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def test_activate_user_success(self):
        """Test: activation réussie."""
        self.mock_user_repo.find_by_id.return_value = self.inactive_user
        self.mock_user_repo.save.return_value = self.inactive_user

        result = self.use_case.execute(2)

        assert result.id == 2
        self.mock_user_repo.find_by_id.assert_called_once_with(2)
        self.mock_user_repo.save.assert_called_once()

    def test_activate_user_not_found(self):
        """Test: échec si utilisateur non trouvé."""
        self.mock_user_repo.find_by_id.return_value = None

        with pytest.raises(UserNotFoundError) as exc_info:
            self.use_case.execute(999)

        assert exc_info.value.user_id == 999

    def test_activate_user_publishes_event(self):
        """Test: publication d'un event après activation."""
        mock_publisher = Mock()
        use_case = ActivateUserUseCase(
            user_repo=self.mock_user_repo,
            event_publisher=mock_publisher,
        )

        self.mock_user_repo.find_by_id.return_value = self.inactive_user
        self.mock_user_repo.save.return_value = self.inactive_user

        use_case.execute(2)

        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.user_id == 2
