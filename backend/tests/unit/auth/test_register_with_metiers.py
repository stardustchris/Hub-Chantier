"""Tests unitaires pour RegisterUseCase avec metiers array."""

import pytest
from unittest.mock import Mock

from modules.auth.domain.entities import User
from modules.auth.domain.value_objects import PasswordHash
from modules.auth.domain.repositories import UserRepository
from modules.auth.domain.services import PasswordService
from modules.auth.application.ports import TokenService
from modules.auth.application.use_cases import RegisterUseCase
from modules.auth.application.dtos import RegisterDTO


class TestRegisterUseCaseWithMetiers:
    """Tests pour RegisterUseCase avec le champ metiers."""

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

        # Configuration mocks par defaut
        self.mock_user_repo.exists_by_email.return_value = False
        self.mock_user_repo.exists_by_code.return_value = False
        self.mock_password_service.validate_strength.return_value = True
        self.mock_password_service.hash.return_value = PasswordHash("hashed_password")
        self.mock_token_service.generate.return_value = "jwt_token_123"

    def _create_saved_user(self, user: User) -> User:
        """Simule la sauvegarde en ajoutant un ID."""
        user.id = 1
        return user

    def test_register_with_single_metier(self):
        """Test: inscription avec un seul metier."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        dto = RegisterDTO(
            email="macon@example.com",
            password="Password123!",
            nom="Martin",
            prenom="Pierre",
            metiers=["macon"],
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.user.metiers == ["macon"]

    def test_register_with_multiple_metiers(self):
        """Test: inscription avec plusieurs metiers."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        dto = RegisterDTO(
            email="multi@example.com",
            password="Password123!",
            nom="Dupont",
            prenom="Jean",
            metiers=["macon", "coffreur", "ferrailleur"],
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.user.metiers == ["macon", "coffreur", "ferrailleur"]
        assert len(result.user.metiers) == 3

    def test_register_without_metiers(self):
        """Test: inscription sans metiers (None)."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        dto = RegisterDTO(
            email="nometier@example.com",
            password="Password123!",
            nom="Dupont",
            prenom="Jean",
            metiers=None,
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.user.metiers is None

    def test_register_with_empty_metiers_list(self):
        """Test: inscription avec liste vide de metiers."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        dto = RegisterDTO(
            email="empty@example.com",
            password="Password123!",
            nom="Dupont",
            prenom="Jean",
            metiers=[],
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.user.metiers == []

    def test_register_with_all_fields_including_metiers(self):
        """Test: inscription complete avec tous les champs CDC incluant metiers."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        dto = RegisterDTO(
            email="complet@example.com",
            password="Password123!",
            nom="Martin",
            prenom="Marie",
            type_utilisateur="employe",
            telephone="+33612345678",
            metiers=["electricien", "plombier"],
            code_utilisateur="MAR001",
            couleur="#E74C3C",
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.user.email == "complet@example.com"
        assert result.user.type_utilisateur == "employe"
        assert result.user.telephone == "+33612345678"
        assert result.user.metiers == ["electricien", "plombier"]
        assert result.user.code_utilisateur == "MAR001"
        assert result.user.couleur == "#E74C3C"

    def test_register_metiers_order_preserved(self):
        """Test: l'ordre des metiers est preserve lors de l'inscription."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        dto = RegisterDTO(
            email="order@example.com",
            password="Password123!",
            nom="Order",
            prenom="Test",
            metiers=["plombier", "electricien", "macon"],
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.user.metiers[0] == "plombier"
        assert result.user.metiers[1] == "electricien"
        assert result.user.metiers[2] == "macon"

    def test_register_metiers_persisted_correctly(self):
        """Test: les metiers sont bien sauvegardes via le repository."""
        # Arrange
        saved_user = None

        def capture_save(user: User) -> User:
            nonlocal saved_user
            saved_user = user
            user.id = 1
            return user

        self.mock_user_repo.save.side_effect = capture_save

        dto = RegisterDTO(
            email="persist@example.com",
            password="Password123!",
            nom="Persist",
            prenom="Test",
            metiers=["macon", "coffreur"],
        )

        # Act
        self.use_case.execute(dto)

        # Assert
        assert saved_user is not None
        assert saved_user.metiers == ["macon", "coffreur"]
        self.mock_user_repo.save.assert_called_once()

    def test_register_backward_compatibility_no_metiers_field(self):
        """Test: retrocompatibilite - DTO sans champ metiers."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        # DTO sans specifier metiers (utilise la valeur par defaut)
        dto = RegisterDTO(
            email="legacy@example.com",
            password="Password123!",
            nom="Legacy",
            prenom="Test",
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert - Doit fonctionner sans crash
        assert result.user.id == 1
        assert result.user.email == "legacy@example.com"
        # metiers peut etre None ou [] selon default du DTO

    def test_register_sous_traitant_with_metiers(self):
        """Test: inscription sous-traitant avec metiers."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        dto = RegisterDTO(
            email="soustraitant@example.com",
            password="Password123!",
            nom="ST Entreprise",
            prenom="Contact",
            type_utilisateur="sous_traitant",
            metiers=["grutier", "terrassier"],
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.user.type_utilisateur == "sous_traitant"
        assert result.user.metiers == ["grutier", "terrassier"]

    def test_register_publishes_event_with_metiers(self):
        """Test: l'event UserCreated contient les infos (sans metiers dans l'event actuel)."""
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
            email="event@example.com",
            password="Password123!",
            nom="Event",
            prenom="Test",
            metiers=["macon"],
        )

        # Act
        use_case_with_events.execute(dto)

        # Assert
        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.user_id == 1
        assert event.email == "event@example.com"
        # Note: UserCreatedEvent ne contient pas metiers pour l'instant
