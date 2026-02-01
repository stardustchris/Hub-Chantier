"""Tests unitaires pour UpdateUserUseCase avec taux_horaire."""

import pytest
from decimal import Decimal
from unittest.mock import Mock

from modules.auth.domain.entities import User
from modules.auth.domain.repositories import UserRepository
from modules.auth.domain.value_objects import Email, PasswordHash, Role
from modules.auth.application.use_cases.update_user import (
    UpdateUserUseCase,
    UserNotFoundError,
)
from modules.auth.application.dtos import UpdateUserDTO


class TestUpdateUserWithTauxHoraire:
    """Tests pour la mise à jour d'utilisateur avec taux_horaire."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Mock
        self.mock_user_repo = Mock(spec=UserRepository)

        # Use case
        self.use_case = UpdateUserUseCase(
            user_repo=self.mock_user_repo,
        )

    def test_update_user_with_taux_horaire_success(self):
        """Test: mise à jour du taux_horaire réussie."""
        # Arrange
        existing_user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("20.00"),
        )

        self.mock_user_repo.find_by_id.return_value = existing_user
        self.mock_user_repo.save.return_value = existing_user

        dto = UpdateUserDTO(taux_horaire=Decimal("30.00"))

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.taux_horaire == Decimal("30.00")
        self.mock_user_repo.save.assert_called_once()
        assert existing_user.taux_horaire == Decimal("30.00")

    def test_update_user_set_taux_horaire_from_none(self):
        """Test: définition du taux_horaire depuis None."""
        # Arrange
        existing_user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=None,
        )

        self.mock_user_repo.find_by_id.return_value = existing_user
        self.mock_user_repo.save.return_value = existing_user

        dto = UpdateUserDTO(taux_horaire=Decimal("25.50"))

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.taux_horaire == Decimal("25.50")
        assert existing_user.taux_horaire == Decimal("25.50")

    def test_update_user_remove_taux_horaire(self):
        """Test: suppression du taux_horaire (mise à None)."""
        # Arrange
        existing_user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("30.00"),
        )

        self.mock_user_repo.find_by_id.return_value = existing_user
        self.mock_user_repo.save.return_value = existing_user

        dto = UpdateUserDTO(taux_horaire=None)

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.taux_horaire is None
        assert existing_user.taux_horaire is None

    def test_update_user_without_taux_horaire_keeps_existing(self):
        """Test: ne pas passer taux_horaire conserve la valeur existante."""
        # Arrange
        existing_user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("35.00"),
        )

        self.mock_user_repo.find_by_id.return_value = existing_user
        self.mock_user_repo.save.return_value = existing_user

        dto = UpdateUserDTO(nom="MARTIN")

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.taux_horaire == Decimal("35.00")
        assert result.nom == "MARTIN"

    def test_update_user_taux_horaire_with_other_fields(self):
        """Test: mise à jour de taux_horaire avec d'autres champs."""
        # Arrange
        existing_user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            telephone="0612345678",
            metiers=["Maçon"],
            taux_horaire=Decimal("20.00"),
        )

        self.mock_user_repo.find_by_id.return_value = existing_user
        self.mock_user_repo.save.return_value = existing_user

        dto = UpdateUserDTO(
            telephone="0698765432",
            metiers=["Maçon", "Carreleur"],
            taux_horaire=Decimal("45.00"),
        )

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.telephone == "0698765432"
        assert result.metiers == ["Maçon", "Carreleur"]
        assert result.taux_horaire == Decimal("45.00")

    def test_update_user_zero_taux_horaire(self):
        """Test: mise à jour avec taux_horaire à zéro."""
        # Arrange
        existing_user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("25.00"),
        )

        self.mock_user_repo.find_by_id.return_value = existing_user
        self.mock_user_repo.save.return_value = existing_user

        dto = UpdateUserDTO(taux_horaire=Decimal("0.00"))

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.taux_horaire == Decimal("0.00")

    def test_update_user_high_precision_taux_horaire(self):
        """Test: mise à jour avec taux_horaire haute précision."""
        # Arrange
        existing_user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("20.00"),
        )

        self.mock_user_repo.find_by_id.return_value = existing_user
        self.mock_user_repo.save.return_value = existing_user

        dto = UpdateUserDTO(taux_horaire=Decimal("37.8945"))

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.taux_horaire == Decimal("37.8945")

    def test_update_user_taux_horaire_not_found(self):
        """Test: échec si utilisateur non trouvé."""
        # Arrange
        self.mock_user_repo.find_by_id.return_value = None

        dto = UpdateUserDTO(taux_horaire=Decimal("30.00"))

        # Act & Assert
        with pytest.raises(UserNotFoundError) as exc_info:
            self.use_case.execute(user_id=999, dto=dto)

        assert exc_info.value.user_id == 999

    def test_update_user_taux_horaire_with_role_change(self):
        """Test: mise à jour de taux_horaire avec changement de rôle."""
        # Arrange
        existing_user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("20.00"),
        )

        self.mock_user_repo.find_by_id.return_value = existing_user
        self.mock_user_repo.save.return_value = existing_user

        dto = UpdateUserDTO(
            role="chef_chantier",
            taux_horaire=Decimal("50.00"),
        )

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.role == "chef_chantier"
        assert result.taux_horaire == Decimal("50.00")
        assert existing_user.role == Role.CHEF_CHANTIER

    def test_update_user_all_fields_including_taux_horaire(self):
        """Test: mise à jour de tous les champs y compris taux_horaire."""
        # Arrange
        existing_user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("20.00"),
        )

        self.mock_user_repo.find_by_id.return_value = existing_user
        self.mock_user_repo.save.return_value = existing_user
        self.mock_user_repo.exists_by_code.return_value = False

        dto = UpdateUserDTO(
            nom="MARTIN",
            prenom="Pierre",
            telephone="0698765432",
            metiers=["Électricien"],
            taux_horaire=Decimal("55.00"),
            couleur="#FF0000",
            photo_profil="https://example.com/new.jpg",
            contact_urgence_nom="Martin Sophie",
            contact_urgence_tel="0611223344",
            role="conducteur",
            code_utilisateur="EMP999",
        )

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.nom == "MARTIN"
        assert result.prenom == "Pierre"
        assert result.telephone == "0698765432"
        assert result.metiers == ["Électricien"]
        assert result.taux_horaire == Decimal("55.00")
        assert result.role == "conducteur"
