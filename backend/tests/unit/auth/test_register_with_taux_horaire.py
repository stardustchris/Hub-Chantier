"""Tests unitaires pour RegisterUseCase avec taux_horaire."""

import pytest
from decimal import Decimal
from unittest.mock import Mock

from modules.auth.domain.entities import User
from modules.auth.domain.repositories import UserRepository
from modules.auth.domain.services import PasswordService
from modules.auth.domain.value_objects import Email, PasswordHash, Role
from modules.auth.application.use_cases.register import RegisterUseCase
from modules.auth.application.dtos import RegisterDTO
from modules.auth.application.ports import TokenService


class TestRegisterWithTauxHoraire:
    """Tests pour l'inscription avec taux_horaire."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Mocks
        self.mock_user_repo = Mock(spec=UserRepository)
        self.mock_password_service = Mock(spec=PasswordService)
        self.mock_token_service = Mock(spec=TokenService)

        # Use case
        self.use_case = RegisterUseCase(
            user_repo=self.mock_user_repo,
            password_service=self.mock_password_service,
            token_service=self.mock_token_service,
        )

        # Configuration des mocks par défaut
        self.mock_user_repo.exists_by_email.return_value = False
        self.mock_user_repo.exists_by_code.return_value = False
        self.mock_password_service.validate_strength.return_value = True
        self.mock_password_service.hash.return_value = PasswordHash("$2b$12$hashed")
        self.mock_token_service.generate.return_value = "mock_jwt_token"

    def test_register_with_taux_horaire_success(self):
        """Test: inscription avec taux_horaire réussie."""
        # Arrange
        dto = RegisterDTO(
            email="test@example.com",
            password="SecurePass123!",
            nom="Dupont",
            prenom="Jean",
            telephone="0612345678",
            metiers=["Maçon"],
            taux_horaire=Decimal("25.50"),
        )

        # Mock du user sauvegardé
        def save_user(user):
            user.id = 1
            return user

        self.mock_user_repo.save.side_effect = save_user

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result is not None
        assert result.user.taux_horaire == Decimal("25.50")
        assert result.user.metiers == ["Maçon"]
        assert result.token.access_token == "mock_jwt_token"

        # Vérifier que save a été appelé avec un user ayant taux_horaire
        self.mock_user_repo.save.assert_called_once()
        saved_user = self.mock_user_repo.save.call_args[0][0]
        assert saved_user.taux_horaire == Decimal("25.50")

    def test_register_without_taux_horaire_success(self):
        """Test: inscription sans taux_horaire (None par défaut)."""
        # Arrange
        dto = RegisterDTO(
            email="test@example.com",
            password="SecurePass123!",
            nom="Dupont",
            prenom="Jean",
        )

        # Mock du user sauvegardé
        def save_user(user):
            user.id = 1
            return user

        self.mock_user_repo.save.side_effect = save_user

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result is not None
        assert result.user.taux_horaire is None

        # Vérifier que save a été appelé avec un user sans taux_horaire
        self.mock_user_repo.save.assert_called_once()
        saved_user = self.mock_user_repo.save.call_args[0][0]
        assert saved_user.taux_horaire is None

    def test_register_with_zero_taux_horaire(self):
        """Test: inscription avec taux_horaire zéro lève ValueError (SMIC)."""
        # Arrange
        dto = RegisterDTO(
            email="test@example.com",
            password="SecurePass123!",
            nom="Dupont",
            prenom="Jean",
            taux_horaire=Decimal("0.00"),
        )

        def save_user(user):
            user.id = 1
            return user

        self.mock_user_repo.save.side_effect = save_user

        # Act & Assert
        with pytest.raises(ValueError, match="SMIC"):
            self.use_case.execute(dto)

    def test_register_with_high_taux_horaire(self):
        """Test: inscription avec taux_horaire élevé."""
        # Arrange
        dto = RegisterDTO(
            email="test@example.com",
            password="SecurePass123!",
            nom="Dupont",
            prenom="Jean",
            taux_horaire=Decimal("150.00"),
        )

        # Mock du user sauvegardé
        def save_user(user):
            user.id = 1
            return user

        self.mock_user_repo.save.side_effect = save_user

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result is not None
        assert result.user.taux_horaire == Decimal("150.00")

    def test_register_with_precise_taux_horaire(self):
        """Test: inscription avec taux_horaire haute précision lève ValueError."""
        # Arrange
        dto = RegisterDTO(
            email="test@example.com",
            password="SecurePass123!",
            nom="Dupont",
            prenom="Jean",
            taux_horaire=Decimal("35.7538"),
        )

        def save_user(user):
            user.id = 1
            return user

        self.mock_user_repo.save.side_effect = save_user

        # Act & Assert
        with pytest.raises(ValueError, match="décimales"):
            self.use_case.execute(dto)

    def test_register_with_all_fields_including_taux_horaire(self):
        """Test: inscription avec tous les champs y compris taux_horaire."""
        # Arrange
        dto = RegisterDTO(
            email="test@example.com",
            password="SecurePass123!",
            nom="Dupont",
            prenom="Jean",
            telephone="0612345678",
            metiers=["Maçon", "Carreleur"],
            taux_horaire=Decimal("28.75"),
            code_utilisateur="EMP001",
            type_utilisateur="employe",
            couleur="#FF5733",
        )

        # Mock du user sauvegardé
        def save_user(user):
            user.id = 1
            return user

        self.mock_user_repo.save.side_effect = save_user

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result is not None
        assert result.user.taux_horaire == Decimal("28.75")
        assert result.user.metiers == ["Maçon", "Carreleur"]
        assert result.user.telephone == "0612345678"
        assert result.user.code_utilisateur == "EMP001"

        # Vérifier le user sauvegardé
        saved_user = self.mock_user_repo.save.call_args[0][0]
        assert saved_user.taux_horaire == Decimal("28.75")
        assert saved_user.metiers == ["Maçon", "Carreleur"]
        assert saved_user.role == Role.COMPAGNON  # Toujours COMPAGNON en self-registration

    def test_register_taux_horaire_preserved_through_save(self):
        """Test: taux_horaire préservé lors de la sauvegarde."""
        # Arrange
        dto = RegisterDTO(
            email="test@example.com",
            password="SecurePass123!",
            nom="Dupont",
            prenom="Jean",
            taux_horaire=Decimal("42.50"),
        )

        saved_user_reference = None

        def save_and_capture(user):
            nonlocal saved_user_reference
            user.id = 1
            saved_user_reference = user
            return user

        self.mock_user_repo.save.side_effect = save_and_capture

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert saved_user_reference is not None
        assert saved_user_reference.taux_horaire == Decimal("42.50")
        assert result.user.taux_horaire == Decimal("42.50")
