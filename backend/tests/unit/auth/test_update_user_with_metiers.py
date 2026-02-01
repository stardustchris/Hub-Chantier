"""Tests unitaires pour UpdateUserUseCase avec metiers array."""

import pytest
from unittest.mock import Mock

from modules.auth.domain.entities import User
from modules.auth.domain.value_objects import Email, PasswordHash, Role
from modules.auth.domain.repositories import UserRepository
from modules.auth.application.use_cases import UpdateUserUseCase
from modules.auth.application.use_cases.update_user import UserNotFoundError
from modules.auth.application.dtos import UpdateUserDTO


class TestUpdateUserUseCaseWithMetiers:
    """Tests pour UpdateUserUseCase avec le champ metiers."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Mock
        self.mock_user_repo = Mock(spec=UserRepository)

        # Use case
        self.use_case = UpdateUserUseCase(user_repo=self.mock_user_repo)

        # User par defaut
        self.existing_user = User(
            id=1,
            email=Email("existing@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            metiers=["macon"],
        )

    def test_update_user_add_metiers(self):
        """Test: ajout de metiers a un utilisateur."""
        # Arrange
        self.mock_user_repo.find_by_id.return_value = self.existing_user
        self.mock_user_repo.save.return_value = self.existing_user

        dto = UpdateUserDTO(metiers=["macon", "coffreur"])

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.metiers == ["macon", "coffreur"]
        self.mock_user_repo.save.assert_called_once()

    def test_update_user_replace_metiers(self):
        """Test: remplacement complet des metiers."""
        # Arrange
        self.existing_user.metiers = ["macon", "coffreur"]
        self.mock_user_repo.find_by_id.return_value = self.existing_user
        self.mock_user_repo.save.return_value = self.existing_user

        dto = UpdateUserDTO(metiers=["electricien", "plombier"])

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.metiers == ["electricien", "plombier"]
        assert "macon" not in result.metiers
        assert "coffreur" not in result.metiers

    def test_update_user_remove_all_metiers(self):
        """Test: suppression de tous les metiers (liste vide)."""
        # Arrange
        self.existing_user.metiers = ["macon", "coffreur"]
        self.mock_user_repo.find_by_id.return_value = self.existing_user
        self.mock_user_repo.save.return_value = self.existing_user

        dto = UpdateUserDTO(metiers=[])

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.metiers == []

    def test_update_user_set_metiers_to_none(self):
        """Test: suppression des metiers via liste vide."""
        # Arrange
        self.existing_user.metiers = ["macon"]
        self.mock_user_repo.find_by_id.return_value = self.existing_user
        self.mock_user_repo.save.return_value = self.existing_user

        # Note: la logique "if metiers is not None" ne permet pas de setter à None.
        # Pour vider, on passe une liste vide.
        dto = UpdateUserDTO(metiers=[])

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.metiers == []

    def test_update_user_keeps_metiers_if_not_provided(self):
        """Test: metiers inchanges si non fournis dans le DTO."""
        # Arrange
        self.existing_user.metiers = ["macon", "coffreur"]
        self.mock_user_repo.find_by_id.return_value = self.existing_user
        self.mock_user_repo.save.return_value = self.existing_user

        dto = UpdateUserDTO(telephone="+33612345678")

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.metiers == ["macon", "coffreur"]
        assert result.telephone == "+33612345678"

    def test_update_user_with_multiple_fields_including_metiers(self):
        """Test: mise a jour de plusieurs champs incluant metiers."""
        # Arrange
        self.mock_user_repo.find_by_id.return_value = self.existing_user
        self.mock_user_repo.save.return_value = self.existing_user

        dto = UpdateUserDTO(
            nom="MARTIN",
            prenom="Pierre",
            telephone="+33612345678",
            metiers=["electricien", "plombier", "macon"],
            couleur="#E74C3C",
        )

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.nom == "MARTIN"
        assert result.prenom == "Pierre"
        assert result.telephone == "+33612345678"
        assert result.metiers == ["electricien", "plombier", "macon"]
        assert result.couleur == "#E74C3C"

    def test_update_user_from_no_metiers_to_metiers(self):
        """Test: ajout de metiers a un utilisateur qui n'en avait pas."""
        # Arrange
        self.existing_user.metiers = None
        self.mock_user_repo.find_by_id.return_value = self.existing_user
        self.mock_user_repo.save.return_value = self.existing_user

        dto = UpdateUserDTO(metiers=["macon", "coffreur"])

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.metiers == ["macon", "coffreur"]

    def test_update_user_metiers_order_preserved(self):
        """Test: l'ordre des metiers est preserve lors de la mise a jour."""
        # Arrange
        self.mock_user_repo.find_by_id.return_value = self.existing_user
        self.mock_user_repo.save.return_value = self.existing_user

        dto = UpdateUserDTO(metiers=["terrassier", "grutier", "charpentier"])

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.metiers[0] == "terrassier"
        assert result.metiers[1] == "grutier"
        assert result.metiers[2] == "charpentier"

    def test_update_user_not_found(self):
        """Test: echec si utilisateur non trouve."""
        # Arrange
        self.mock_user_repo.find_by_id.return_value = None

        dto = UpdateUserDTO(metiers=["macon"])

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            self.use_case.execute(user_id=999, dto=dto)

    def test_update_user_metiers_with_role_change(self):
        """Test: mise a jour metiers + changement de role."""
        # Arrange
        self.mock_user_repo.find_by_id.return_value = self.existing_user
        self.mock_user_repo.save.return_value = self.existing_user

        dto = UpdateUserDTO(role="chef_chantier", metiers=["electricien"])

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.role == "chef_chantier"
        assert result.metiers == ["electricien"]

    def test_update_user_metiers_publishes_event(self):
        """Test: l'event UserUpdated est publie."""
        # Arrange
        mock_publisher = Mock()
        use_case_with_events = UpdateUserUseCase(
            user_repo=self.mock_user_repo, event_publisher=mock_publisher
        )

        self.mock_user_repo.find_by_id.return_value = self.existing_user
        self.mock_user_repo.save.return_value = self.existing_user

        dto = UpdateUserDTO(metiers=["electricien"])

        # Act
        use_case_with_events.execute(user_id=1, dto=dto)

        # Assert
        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.user_id == 1
        # Note: UserUpdatedEvent ne contient pas metiers pour l'instant

    def test_update_user_empty_dto_preserves_metiers(self):
        """Test: DTO vide preserve tous les champs dont metiers."""
        # Arrange
        self.existing_user.metiers = ["macon", "coffreur"]
        self.existing_user.telephone = "+33612345678"
        self.mock_user_repo.find_by_id.return_value = self.existing_user
        self.mock_user_repo.save.return_value = self.existing_user

        dto = UpdateUserDTO()  # Tous les champs None

        # Act
        result = self.use_case.execute(user_id=1, dto=dto)

        # Assert
        assert result.metiers == ["macon", "coffreur"]
        assert result.telephone == "+33612345678"
