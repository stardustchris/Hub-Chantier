"""Tests unitaires pour ListUsersUseCase et GetUserByIdUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.auth.domain.entities import User
from modules.auth.domain.value_objects import Email, PasswordHash, Role, TypeUtilisateur
from modules.auth.domain.repositories import UserRepository
from modules.auth.application.use_cases.list_users import (
    ListUsersUseCase,
    GetUserByIdUseCase,
)


class TestListUsersUseCase:
    """Tests pour le use case de liste des utilisateurs."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_user_repo = Mock(spec=UserRepository)
        self.use_case = ListUsersUseCase(user_repo=self.mock_user_repo)

        self.users = [
            User(
                id=1,
                email=Email("user1@example.com"),
                password_hash=PasswordHash("hashed"),
                nom="DUPONT",
                prenom="Jean",
                role=Role.COMPAGNON,
                is_active=True,
            ),
            User(
                id=2,
                email=Email("user2@example.com"),
                password_hash=PasswordHash("hashed"),
                nom="MARTIN",
                prenom="Marie",
                role=Role.CHEF_CHANTIER,
                is_active=True,
            ),
        ]

    def test_list_users_success(self):
        """Test: liste paginée des utilisateurs."""
        self.mock_user_repo.search.return_value = (self.users, 2)

        result = self.use_case.execute(skip=0, limit=20)

        assert len(result.users) == 2
        assert result.total == 2
        assert result.skip == 0
        assert result.limit == 20
        self.mock_user_repo.search.assert_called_once()

    def test_list_users_with_role_filter(self):
        """Test: filtre par rôle."""
        self.mock_user_repo.search.return_value = ([self.users[1]], 1)

        result = self.use_case.execute(role="chef_chantier")

        assert len(result.users) == 1
        call_kwargs = self.mock_user_repo.search.call_args[1]
        assert call_kwargs["role"] == Role.CHEF_CHANTIER

    def test_list_users_with_type_filter(self):
        """Test: filtre par type utilisateur."""
        self.mock_user_repo.search.return_value = ([], 0)

        result = self.use_case.execute(type_utilisateur="sous_traitant")

        call_kwargs = self.mock_user_repo.search.call_args[1]
        assert call_kwargs["type_utilisateur"] == TypeUtilisateur.SOUS_TRAITANT

    def test_list_users_active_only(self):
        """Test: filtre actifs uniquement."""
        self.mock_user_repo.search.return_value = (self.users, 2)

        result = self.use_case.execute(active_only=True)

        call_kwargs = self.mock_user_repo.search.call_args[1]
        assert call_kwargs["active_only"] is True

    def test_list_users_with_search(self):
        """Test: recherche textuelle."""
        self.mock_user_repo.search.return_value = ([self.users[0]], 1)

        result = self.use_case.execute(search="DUPONT")

        call_kwargs = self.mock_user_repo.search.call_args[1]
        assert call_kwargs["query"] == "DUPONT"

    def test_list_users_pagination(self):
        """Test: pagination."""
        self.mock_user_repo.search.return_value = (self.users, 100)

        result = self.use_case.execute(skip=20, limit=10)

        assert result.skip == 20
        assert result.limit == 10
        call_kwargs = self.mock_user_repo.search.call_args[1]
        assert call_kwargs["skip"] == 20
        assert call_kwargs["limit"] == 10


class TestGetUserByIdUseCase:
    """Tests pour le use case de récupération par ID."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_user_repo = Mock(spec=UserRepository)
        self.use_case = GetUserByIdUseCase(user_repo=self.mock_user_repo)

        self.test_user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            is_active=True,
        )

    def test_get_user_by_id_success(self):
        """Test: récupération réussie."""
        self.mock_user_repo.find_by_id.return_value = self.test_user

        result = self.use_case.execute(1)

        assert result is not None
        assert result.id == 1
        assert result.email == "test@example.com"
        self.mock_user_repo.find_by_id.assert_called_once_with(1)

    def test_get_user_by_id_not_found(self):
        """Test: retourne None si non trouvé."""
        self.mock_user_repo.find_by_id.return_value = None

        result = self.use_case.execute(999)

        assert result is None
