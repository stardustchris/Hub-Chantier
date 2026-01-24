"""Tests unitaires pour UpdateUserUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.auth.domain.entities import User
from modules.auth.domain.value_objects import Email, PasswordHash, Role
from modules.auth.domain.repositories import UserRepository
from modules.auth.application.use_cases.update_user import (
    UpdateUserUseCase,
    UserNotFoundError,
    CodeAlreadyExistsError,
)
from modules.auth.application.dtos import UpdateUserDTO


class TestUpdateUserUseCase:
    """Tests pour le use case de mise à jour utilisateur."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_user_repo = Mock(spec=UserRepository)
        self.use_case = UpdateUserUseCase(user_repo=self.mock_user_repo)

        self.test_user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed_password"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            is_active=True,
            code_utilisateur="U001",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def test_update_user_success(self):
        """Test: mise à jour réussie du nom et prénom."""
        self.mock_user_repo.find_by_id.return_value = self.test_user
        self.mock_user_repo.save.return_value = self.test_user

        dto = UpdateUserDTO(nom="MARTIN", prenom="Pierre")

        result = self.use_case.execute(1, dto)

        assert result.id == 1
        self.mock_user_repo.find_by_id.assert_called_once_with(1)
        self.mock_user_repo.save.assert_called_once()

    def test_update_user_not_found(self):
        """Test: échec si utilisateur non trouvé."""
        self.mock_user_repo.find_by_id.return_value = None

        dto = UpdateUserDTO(nom="MARTIN")

        with pytest.raises(UserNotFoundError) as exc_info:
            self.use_case.execute(999, dto)

        assert exc_info.value.user_id == 999

    def test_update_user_code_already_exists(self):
        """Test: échec si nouveau code utilisateur déjà utilisé."""
        self.mock_user_repo.find_by_id.return_value = self.test_user
        self.mock_user_repo.exists_by_code.return_value = True

        dto = UpdateUserDTO(code_utilisateur="U999")

        with pytest.raises(CodeAlreadyExistsError) as exc_info:
            self.use_case.execute(1, dto)

        assert exc_info.value.code == "U999"

    def test_update_user_code_success(self):
        """Test: mise à jour réussie du code utilisateur."""
        self.mock_user_repo.find_by_id.return_value = self.test_user
        self.mock_user_repo.exists_by_code.return_value = False
        self.mock_user_repo.save.return_value = self.test_user

        dto = UpdateUserDTO(code_utilisateur="U999")

        self.use_case.execute(1, dto)

        self.mock_user_repo.exists_by_code.assert_called_once_with("U999")
        self.mock_user_repo.save.assert_called_once()

    def test_update_user_role(self):
        """Test: mise à jour du rôle."""
        self.mock_user_repo.find_by_id.return_value = self.test_user
        self.mock_user_repo.save.return_value = self.test_user

        dto = UpdateUserDTO(role="chef_chantier")

        self.use_case.execute(1, dto)

        self.mock_user_repo.save.assert_called_once()

    def test_update_user_type_utilisateur(self):
        """Test: mise à jour du type utilisateur."""
        self.mock_user_repo.find_by_id.return_value = self.test_user
        self.mock_user_repo.save.return_value = self.test_user

        dto = UpdateUserDTO(type_utilisateur="sous_traitant")

        self.use_case.execute(1, dto)

        self.mock_user_repo.save.assert_called_once()

    def test_update_user_contact_urgence(self):
        """Test: mise à jour du contact d'urgence."""
        self.mock_user_repo.find_by_id.return_value = self.test_user
        self.mock_user_repo.save.return_value = self.test_user

        dto = UpdateUserDTO(
            contact_urgence_nom="Marie DUPONT",
            contact_urgence_tel="0612345678",
        )

        self.use_case.execute(1, dto)

        self.mock_user_repo.save.assert_called_once()

    def test_update_user_publishes_event(self):
        """Test: publication d'un event après mise à jour."""
        mock_publisher = Mock()
        use_case = UpdateUserUseCase(
            user_repo=self.mock_user_repo,
            event_publisher=mock_publisher,
        )

        self.mock_user_repo.find_by_id.return_value = self.test_user
        self.mock_user_repo.save.return_value = self.test_user

        dto = UpdateUserDTO(nom="MARTIN")

        use_case.execute(1, dto)

        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.user_id == 1
