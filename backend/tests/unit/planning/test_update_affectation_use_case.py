"""Tests unitaires pour le use case UpdateAffectation.

Ce fichier teste :
- Mise a jour des horaires
- Mise a jour de la note
- Mise a jour du chantier
- Affectation non trouvee -> exception
- Publication des events
"""

import pytest
from unittest.mock import Mock
from datetime import date

from modules.planning.domain.entities.affectation import Affectation
from modules.planning.domain.repositories.affectation_repository import AffectationRepository
from modules.planning.domain.value_objects.heure_affectation import HeureAffectation
from modules.planning.domain.events.affectation_events import AffectationUpdatedEvent
from modules.planning.application.use_cases.update_affectation import (
    UpdateAffectationUseCase,
    AffectationNotFoundError,
)
from modules.planning.application.dtos.update_affectation_dto import UpdateAffectationDTO
from modules.planning.application.ports.event_bus import EventBus


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_affectation_repository():
    """Fixture: mock du repository d'affectations."""
    return Mock(spec=AffectationRepository)


@pytest.fixture
def mock_event_bus():
    """Fixture: mock du bus d'evenements."""
    return Mock(spec=EventBus)


@pytest.fixture
def use_case(mock_affectation_repository, mock_event_bus):
    """Fixture: instance du use case avec mocks."""
    return UpdateAffectationUseCase(
        affectation_repo=mock_affectation_repository,
        event_bus=mock_event_bus,
    )


@pytest.fixture
def use_case_without_event_bus(mock_affectation_repository):
    """Fixture: use case sans event bus."""
    return UpdateAffectationUseCase(
        affectation_repo=mock_affectation_repository,
        event_bus=None,
    )


@pytest.fixture
def existing_affectation():
    """Fixture: affectation existante sans horaires."""
    return Affectation(
        id=1,
        utilisateur_id=5,
        chantier_id=10,
        date=date(2026, 1, 22),
        created_by=3,
    )


@pytest.fixture
def existing_affectation_with_horaires():
    """Fixture: affectation existante avec horaires."""
    return Affectation(
        id=1,
        utilisateur_id=5,
        chantier_id=10,
        date=date(2026, 1, 22),
        heure_debut=HeureAffectation(8, 0),
        heure_fin=HeureAffectation(17, 0),
        created_by=3,
    )


# =============================================================================
# Tests Affectation Non Trouvee
# =============================================================================

class TestUpdateAffectationNotFound:
    """Tests pour le cas ou l'affectation n'existe pas."""

    def test_should_raise_when_affectation_not_found(
        self, use_case, mock_affectation_repository
    ):
        """Test: echec si affectation non trouvee."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = None

        dto = UpdateAffectationDTO(heure_debut="09:00")

        # Act & Assert
        with pytest.raises(AffectationNotFoundError) as exc_info:
            use_case.execute(affectation_id=999, dto=dto, updated_by=1)

        assert exc_info.value.affectation_id == 999
        assert "999" in str(exc_info.value)

    def test_should_not_save_when_not_found(
        self, use_case, mock_affectation_repository
    ):
        """Test: pas de sauvegarde si affectation non trouvee."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = None

        dto = UpdateAffectationDTO(heure_debut="09:00")

        # Act
        with pytest.raises(AffectationNotFoundError):
            use_case.execute(affectation_id=999, dto=dto, updated_by=1)

        # Assert
        mock_affectation_repository.save.assert_not_called()


# =============================================================================
# Tests Mise a Jour Horaires
# =============================================================================

class TestUpdateAffectationHoraires:
    """Tests pour la mise a jour des horaires."""

    def test_should_update_heure_debut(
        self, use_case, mock_affectation_repository, existing_affectation_with_horaires
    ):
        """Test: mise a jour de l'heure de debut."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = (
            existing_affectation_with_horaires
        )
        mock_affectation_repository.save.side_effect = lambda a: a

        dto = UpdateAffectationDTO(heure_debut="09:00")

        # Act
        result = use_case.execute(affectation_id=1, dto=dto, updated_by=2)

        # Assert
        assert str(result.heure_debut) == "09:00"
        assert str(result.heure_fin) == "17:00"  # Inchange

    def test_should_update_heure_fin(
        self, use_case, mock_affectation_repository, existing_affectation_with_horaires
    ):
        """Test: mise a jour de l'heure de fin."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = (
            existing_affectation_with_horaires
        )
        mock_affectation_repository.save.side_effect = lambda a: a

        dto = UpdateAffectationDTO(heure_fin="18:00")

        # Act
        result = use_case.execute(affectation_id=1, dto=dto, updated_by=2)

        # Assert
        assert str(result.heure_debut) == "08:00"  # Inchange
        assert str(result.heure_fin) == "18:00"

    def test_should_update_both_horaires(
        self, use_case, mock_affectation_repository, existing_affectation_with_horaires
    ):
        """Test: mise a jour des deux horaires."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = (
            existing_affectation_with_horaires
        )
        mock_affectation_repository.save.side_effect = lambda a: a

        dto = UpdateAffectationDTO(heure_debut="07:00", heure_fin="16:00")

        # Act
        result = use_case.execute(affectation_id=1, dto=dto, updated_by=2)

        # Assert
        assert str(result.heure_debut) == "07:00"
        assert str(result.heure_fin) == "16:00"

    def test_should_add_horaires_to_affectation_without(
        self, use_case, mock_affectation_repository, existing_affectation
    ):
        """Test: ajout d'horaires a une affectation sans horaires."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.save.side_effect = lambda a: a

        dto = UpdateAffectationDTO(heure_debut="09:00", heure_fin="18:00")

        # Act
        result = use_case.execute(affectation_id=1, dto=dto, updated_by=2)

        # Assert
        assert str(result.heure_debut) == "09:00"
        assert str(result.heure_fin) == "18:00"

    def test_should_raise_when_invalid_horaires(
        self, use_case, mock_affectation_repository, existing_affectation_with_horaires
    ):
        """Test: echec si heure_fin <= heure_debut."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = (
            existing_affectation_with_horaires
        )

        dto = UpdateAffectationDTO(heure_debut="18:00", heure_fin="08:00")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            use_case.execute(affectation_id=1, dto=dto, updated_by=2)

        assert "heure de fin" in str(exc_info.value).lower()


# =============================================================================
# Tests Mise a Jour Note
# =============================================================================

class TestUpdateAffectationNote:
    """Tests pour la mise a jour de la note."""

    def test_should_update_note(
        self, use_case, mock_affectation_repository, existing_affectation
    ):
        """Test: mise a jour de la note."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.save.side_effect = lambda a: a

        dto = UpdateAffectationDTO(note="Nouvelle note importante")

        # Act
        result = use_case.execute(affectation_id=1, dto=dto, updated_by=2)

        # Assert
        assert result.note == "Nouvelle note importante"

    def test_should_remove_note_when_empty(
        self, use_case, mock_affectation_repository
    ):
        """Test: suppression de la note si vide."""
        # Arrange
        affectation = Affectation(
            id=1,
            utilisateur_id=5,
            chantier_id=10,
            date=date(2026, 1, 22),
            note="Note existante",
            created_by=3,
        )
        mock_affectation_repository.find_by_id.return_value = affectation
        mock_affectation_repository.save.side_effect = lambda a: a

        dto = UpdateAffectationDTO(note="   ")  # Note vide

        # Act
        result = use_case.execute(affectation_id=1, dto=dto, updated_by=2)

        # Assert
        assert result.note is None


# =============================================================================
# Tests Mise a Jour Chantier
# =============================================================================

class TestUpdateAffectationChantier:
    """Tests pour la mise a jour du chantier."""

    def test_should_update_chantier(
        self, use_case, mock_affectation_repository, existing_affectation
    ):
        """Test: mise a jour du chantier."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.save.side_effect = lambda a: a

        dto = UpdateAffectationDTO(chantier_id=99)

        # Act
        result = use_case.execute(affectation_id=1, dto=dto, updated_by=2)

        # Assert
        assert result.chantier_id == 99

    def test_should_raise_when_invalid_chantier_id(
        self, use_case, mock_affectation_repository, existing_affectation
    ):
        """Test: echec si chantier_id invalide (validation dans DTO)."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation

        # Act & Assert - ValueError est levee dans __post_init__ du DTO
        with pytest.raises(ValueError) as exc_info:
            UpdateAffectationDTO(chantier_id=0)

        assert "positif" in str(exc_info.value)


# =============================================================================
# Tests Sauvegarde
# =============================================================================

class TestUpdateAffectationSave:
    """Tests pour la sauvegarde."""

    def test_should_save_via_repository(
        self, use_case, mock_affectation_repository, existing_affectation
    ):
        """Test: sauvegarde via le repository."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.save.side_effect = lambda a: a

        dto = UpdateAffectationDTO(note="Update")

        # Act
        use_case.execute(affectation_id=1, dto=dto, updated_by=2)

        # Assert
        mock_affectation_repository.save.assert_called_once()

    def test_should_return_updated_affectation(
        self, use_case, mock_affectation_repository, existing_affectation
    ):
        """Test: retourne l'affectation mise a jour."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.save.side_effect = lambda a: a

        dto = UpdateAffectationDTO(note="Ma note")

        # Act
        result = use_case.execute(affectation_id=1, dto=dto, updated_by=2)

        # Assert
        assert result.id == 1
        assert result.note == "Ma note"


# =============================================================================
# Tests Publication Events
# =============================================================================

class TestUpdateAffectationEvents:
    """Tests pour la publication des events."""

    def test_should_publish_updated_event(
        self, use_case, mock_affectation_repository, mock_event_bus, existing_affectation
    ):
        """Test: publication de l'event apres mise a jour."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.save.side_effect = lambda a: a

        dto = UpdateAffectationDTO(note="Nouvelle note")

        # Act
        use_case.execute(affectation_id=1, dto=dto, updated_by=2)

        # Assert
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert isinstance(event, AffectationUpdatedEvent)
        assert event.affectation_id == 1
        assert event.updated_by == 2
        assert "note" in event.changes

    def test_should_include_all_changes_in_event(
        self, use_case, mock_affectation_repository, mock_event_bus,
        existing_affectation_with_horaires
    ):
        """Test: l'event contient tous les changements."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = (
            existing_affectation_with_horaires
        )
        mock_affectation_repository.save.side_effect = lambda a: a

        dto = UpdateAffectationDTO(
            heure_debut="09:00",
            heure_fin="18:00",
            note="Note",
        )

        # Act
        use_case.execute(affectation_id=1, dto=dto, updated_by=2)

        # Assert
        event = mock_event_bus.publish.call_args[0][0]
        assert "heure_debut" in event.changes
        assert "heure_fin" in event.changes
        assert "note" in event.changes

    def test_should_not_publish_when_no_event_bus(
        self, use_case_without_event_bus, mock_affectation_repository, existing_affectation
    ):
        """Test: pas de publication si event bus absent."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.save.side_effect = lambda a: a

        dto = UpdateAffectationDTO(note="Update")

        # Act - should not raise
        result = use_case_without_event_bus.execute(affectation_id=1, dto=dto, updated_by=2)

        # Assert
        assert result is not None

    def test_should_not_publish_when_no_changes(
        self, use_case, mock_affectation_repository, mock_event_bus, existing_affectation
    ):
        """Test: pas de publication si pas de modifications."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.save.side_effect = lambda a: a

        # DTO sans aucune modification
        dto = UpdateAffectationDTO()

        # Act
        use_case.execute(affectation_id=1, dto=dto, updated_by=2)

        # Assert - save est appele mais pas d'event
        mock_affectation_repository.save.assert_called_once()
        mock_event_bus.publish.assert_not_called()


# =============================================================================
# Tests Mise a Jour Multiple
# =============================================================================

class TestUpdateAffectationMultiple:
    """Tests pour les mises a jour multiples."""

    def test_should_update_multiple_fields(
        self, use_case, mock_affectation_repository, existing_affectation
    ):
        """Test: mise a jour de plusieurs champs en une fois."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.save.side_effect = lambda a: a

        dto = UpdateAffectationDTO(
            heure_debut="09:00",
            heure_fin="18:00",
            note="Note complete",
            chantier_id=99,
        )

        # Act
        result = use_case.execute(affectation_id=1, dto=dto, updated_by=2)

        # Assert
        assert str(result.heure_debut) == "09:00"
        assert str(result.heure_fin) == "18:00"
        assert result.note == "Note complete"
        assert result.chantier_id == 99


# =============================================================================
# Tests Validation DTO
# =============================================================================

class TestUpdateAffectationDTOValidation:
    """Tests pour la validation du DTO."""

    def test_should_raise_when_invalid_heure_format(self):
        """Test: echec si format d'heure invalide."""
        with pytest.raises(ValueError) as exc_info:
            UpdateAffectationDTO(heure_debut="invalid")

        assert "Format" in str(exc_info.value)

    def test_should_raise_when_invalid_chantier_id_in_dto(self):
        """Test: echec si chantier_id invalide dans le DTO."""
        with pytest.raises(ValueError):
            UpdateAffectationDTO(chantier_id=0)

    def test_should_create_dto_with_no_changes(self):
        """Test: DTO sans modifications est valide."""
        dto = UpdateAffectationDTO()

        assert dto.has_changes is False

    def test_should_detect_has_changes(self):
        """Test: has_changes detecte les modifications."""
        dto = UpdateAffectationDTO(note="test")

        assert dto.has_changes is True
