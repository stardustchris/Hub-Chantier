"""Tests unitaires pour RegisterUseCase."""

import pytest
from unittest.mock import Mock

from modules.auth.domain.entities import User
from modules.auth.domain.value_objects import PasswordHash
from modules.auth.domain.repositories import UserRepository
from modules.auth.domain.services import PasswordService
from modules.auth.application.ports import TokenService
from modules.auth.application.use_cases import (
    RegisterUseCase,
    EmailAlreadyExistsError,
    CodeAlreadyExistsError,
    WeakPasswordError,
)
from modules.auth.application.dtos import RegisterDTO


class TestRegisterUseCase:
    """Tests pour le use case d'inscription."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Mocks
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_password_service = Mock(spec=PasswordService)
        self.mock_token_service = Mock(spec=TokenService)

        # Use case à tester
        self.use_case = RegisterUseCase(
            user_repo=self.mock_user_repo,
            password_service=self.mock_password_service,
            token_service=self.mock_token_service,
        )

        # Configurer les mocks par défaut
        self.mock_user_repo.exists_by_email.return_value = False
        self.mock_user_repo.exists_by_code.return_value = False
        self.mock_password_service.validate_strength.return_value = True
        self.mock_password_service.hash.return_value = PasswordHash("hashed_password")
        self.mock_token_service.generate.return_value = "jwt_token_123"

    def _create_saved_user(self, user: User) -> User:
        """Simule la sauvegarde en ajoutant un ID."""
        user.id = 1
        return user

    def test_register_success_basic(self):
        """Test: inscription réussie avec données minimales."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        dto = RegisterDTO(
            email="new@example.com",
            password="Password123!",
            nom="Dupont",
            prenom="Jean",
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.user.id == 1
        assert result.user.email == "new@example.com"
        assert result.user.nom == "DUPONT"
        assert result.user.prenom == "Jean"
        assert result.user.role == "compagnon"  # Défaut
        assert result.user.type_utilisateur == "employe"  # Défaut
        assert result.token.access_token == "jwt_token_123"

    def test_register_success_with_all_fields(self):
        """Test: inscription réussie avec tous les champs CDC.

        Le rôle n'est plus un champ du DTO — forcé côté serveur à COMPAGNON.
        """
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        dto = RegisterDTO(
            email="complet@example.com",
            password="Password123!",
            nom="Martin",
            prenom="Marie",
            type_utilisateur="employe",
            telephone="+33612345678",
            metier="Maçon",
            code_utilisateur="MAR001",
            couleur="#E74C3C",  # Rouge
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.user.email == "complet@example.com"
        assert result.user.role == "compagnon"  # Forced server-side
        assert result.user.type_utilisateur == "employe"
        assert result.user.telephone == "+33612345678"
        assert result.user.metier == "Maçon"
        assert result.user.code_utilisateur == "MAR001"
        assert result.user.couleur == "#E74C3C"

    def test_register_sous_traitant(self):
        """Test: inscription d'un sous-traitant."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        dto = RegisterDTO(
            email="soustraitant@example.com",
            password="Password123!",
            nom="Entreprise",
            prenom="Contact",
            type_utilisateur="sous_traitant",
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.user.type_utilisateur == "sous_traitant"

    def test_register_email_already_exists(self):
        """Test: échec si email déjà utilisé."""
        # Arrange
        self.mock_user_repo.exists_by_email.return_value = True

        dto = RegisterDTO(
            email="existing@example.com",
            password="Password123!",
            nom="Dupont",
            prenom="Jean",
        )

        # Act & Assert
        with pytest.raises(EmailAlreadyExistsError) as exc_info:
            self.use_case.execute(dto)
        assert "existing@example.com" in str(exc_info.value)

    def test_register_code_already_exists(self):
        """Test: échec si code utilisateur déjà utilisé."""
        # Arrange
        self.mock_user_repo.exists_by_code.return_value = True

        dto = RegisterDTO(
            email="new@example.com",
            password="Password123!",
            nom="Dupont",
            prenom="Jean",
            code_utilisateur="DUP001",
        )

        # Act & Assert
        with pytest.raises(CodeAlreadyExistsError) as exc_info:
            self.use_case.execute(dto)
        assert "DUP001" in str(exc_info.value)

    def test_register_weak_password(self):
        """Test: échec si mot de passe trop faible."""
        # Arrange
        self.mock_password_service.validate_strength.return_value = False

        dto = RegisterDTO(
            email="new@example.com",
            password="weak",
            nom="Dupont",
            prenom="Jean",
        )

        # Act & Assert
        with pytest.raises(WeakPasswordError):
            self.use_case.execute(dto)

    def test_register_invalid_email_format(self):
        """Test: échec si format email invalide."""
        dto = RegisterDTO(
            email="invalid-email",
            password="Password123!",
            nom="Dupont",
            prenom="Jean",
        )

        with pytest.raises(ValueError):
            self.use_case.execute(dto)

    def test_register_always_compagnon(self):
        """Test: le rôle est toujours COMPAGNON (pas de champ role dans DTO)."""
        self.mock_user_repo.save.side_effect = self._create_saved_user

        dto = RegisterDTO(
            email="new@example.com",
            password="Password123!",
            nom="Dupont",
            prenom="Jean",
        )

        result = self.use_case.execute(dto)
        assert result.user.role == "compagnon"

    def test_register_any_valid_hex_couleur(self):
        """Test: accepte toute couleur hexadécimale valide.

        Note: La validation stricte de palette a été retirée de shared.Couleur
        pour compatibilité inter-modules. Toute couleur hex valide est acceptée.
        """
        self.mock_user_repo.save.side_effect = self._create_saved_user

        dto = RegisterDTO(
            email="new@example.com",
            password="Password123!",
            nom="Dupont",
            prenom="Jean",
            couleur="#000000",  # Noir - accepté car hex valide
        )

        # Ne doit plus lever d'exception - toute couleur hex valide est acceptée
        result = self.use_case.execute(dto)
        assert result.user.couleur == "#000000"

    def test_register_publishes_event(self):
        """Test: publication d'un event après inscription réussie."""
        # Arrange
        mock_publisher = Mock()
        use_case_with_events = RegisterUseCase(
            user_repo=self.mock_user_repo,
            password_service=self.mock_password_service,
            token_service=self.mock_token_service,
            event_publisher=mock_publisher,
        )

        self.mock_user_repo.save.side_effect = self._create_saved_user

        dto = RegisterDTO(
            email="new@example.com",
            password="Password123!",
            nom="Dupont",
            prenom="Jean",
        )

        # Act
        use_case_with_events.execute(dto)

        # Assert
        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.user_id == 1
        assert event.email == "new@example.com"
        assert event.nom == "DUPONT"
        assert event.prenom == "Jean"

    def test_register_multiple_users_all_compagnon(self):
        """Test: toutes les inscriptions produisent le rôle compagnon."""
        emails = ["user1@example.com", "user2@example.com", "user3@example.com"]

        for email in emails:
            # Reset mock
            self.mock_user_repo.reset_mock()
            self.mock_user_repo.exists_by_email.return_value = False
            self.mock_user_repo.exists_by_code.return_value = False
            self.mock_user_repo.save.side_effect = self._create_saved_user

            dto = RegisterDTO(
                email=email,
                password="Password123!",
                nom="Test",
                prenom="User",
            )

            result = self.use_case.execute(dto)
            assert result.user.role == "compagnon"
