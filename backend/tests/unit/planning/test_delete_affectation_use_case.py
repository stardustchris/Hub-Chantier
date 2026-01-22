"""Tests unitaires pour le use case DeleteAffectation.

Ce fichier teste :
- Suppression reussie
- Affectation non trouvee -> exception
- Publication des events
"""

import pytest
from unittest.mock import Mock
from datetime import date

from modules.planning.domain.entities.affectation import Affectation
from modules.planning.domain.repositories.affectation_repository import AffectationRepository
from modules.planning.domain.value_objects.heure_affectation import HeureAffectation
from modules.planning.domain.events.affectation_events import AffectationDeletedEvent
from modules.planning.application.use_cases.delete_affectation import (
    DeleteAffectationUseCase,
    AffectationNotFoundError,
)
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
    return DeleteAffectationUseCase(
        affectation_repo=mock_affectation_repository,
        event_bus=mock_event_bus,
    )


@pytest.fixture
def use_case_without_event_bus(mock_affectation_repository):
    """Fixture: use case sans event bus."""
    return DeleteAffectationUseCase(
        affectation_repo=mock_affectation_repository,
        event_bus=None,
    )


@pytest.fixture
def existing_affectation():
    """Fixture: affectation existante."""
    return Affectation(
        id=1,
        utilisateur_id=5,
        chantier_id=10,
        date=date(2026, 1, 22),
        created_by=3,
    )


@pytest.fixture
def existing_affectation_with_details():
    """Fixture: affectation existante avec horaires et note."""
    return Affectation(
        id=1,
        utilisateur_id=5,
        chantier_id=10,
        date=date(2026, 1, 22),
        heure_debut=HeureAffectation(8, 0),
        heure_fin=HeureAffectation(17, 0),
        note="Note importante",
        created_by=3,
    )


# =============================================================================
# Tests Affectation Non Trouvee
# =============================================================================

class TestDeleteAffectationNotFound:
    """Tests pour le cas ou l'affectation n'existe pas."""

    def test_should_raise_when_affectation_not_found(
        self, use_case, mock_affectation_repository
    ):
        """Test: echec si affectation non trouvee."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(AffectationNotFoundError) as exc_info:
            use_case.execute(affectation_id=999, deleted_by=1)

        assert exc_info.value.affectation_id == 999
        assert "999" in str(exc_info.value)

    def test_should_not_delete_when_not_found(
        self, use_case, mock_affectation_repository
    ):
        """Test: pas de suppression si affectation non trouvee."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = None

        # Act
        with pytest.raises(AffectationNotFoundError):
            use_case.execute(affectation_id=999, deleted_by=1)

        # Assert
        mock_affectation_repository.delete.assert_not_called()


# =============================================================================
# Tests Suppression Reussie
# =============================================================================

class TestDeleteAffectationSuccess:
    """Tests pour la suppression reussie."""

    def test_should_delete_affectation(
        self, use_case, mock_affectation_repository, existing_affectation
    ):
        """Test: suppression reussie."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.delete.return_value = True

        # Act
        result = use_case.execute(affectation_id=1, deleted_by=2)

        # Assert
        assert result is True

    def test_should_call_repository_delete(
        self, use_case, mock_affectation_repository, existing_affectation
    ):
        """Test: appel de delete sur le repository."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.delete.return_value = True

        # Act
        use_case.execute(affectation_id=1, deleted_by=2)

        # Assert
        mock_affectation_repository.delete.assert_called_once_with(1)

    def test_should_find_affectation_before_delete(
        self, use_case, mock_affectation_repository, existing_affectation
    ):
        """Test: recuperation de l'affectation avant suppression."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.delete.return_value = True

        # Act
        use_case.execute(affectation_id=1, deleted_by=2)

        # Assert
        mock_affectation_repository.find_by_id.assert_called_once_with(1)

    def test_should_return_false_when_delete_fails(
        self, use_case, mock_affectation_repository, existing_affectation
    ):
        """Test: retourne False si suppression echoue."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.delete.return_value = False

        # Act
        result = use_case.execute(affectation_id=1, deleted_by=2)

        # Assert
        assert result is False


# =============================================================================
# Tests Publication Events
# =============================================================================

class TestDeleteAffectationEvents:
    """Tests pour la publication des events."""

    def test_should_publish_deleted_event(
        self, use_case, mock_affectation_repository, mock_event_bus, existing_affectation
    ):
        """Test: publication de l'event apres suppression."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.delete.return_value = True

        # Act
        use_case.execute(affectation_id=1, deleted_by=2)

        # Assert
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert isinstance(event, AffectationDeletedEvent)
        assert event.affectation_id == 1
        assert event.utilisateur_id == 5
        assert event.chantier_id == 10
        assert event.date == date(2026, 1, 22)
        assert event.deleted_by == 2

    def test_should_not_publish_when_no_event_bus(
        self, use_case_without_event_bus, mock_affectation_repository, existing_affectation
    ):
        """Test: pas de publication si event bus absent."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.delete.return_value = True

        # Act - should not raise
        result = use_case_without_event_bus.execute(affectation_id=1, deleted_by=2)

        # Assert
        assert result is True

    def test_should_not_publish_when_delete_fails(
        self, use_case, mock_affectation_repository, mock_event_bus, existing_affectation
    ):
        """Test: pas de publication si suppression echoue."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.delete.return_value = False

        # Act
        use_case.execute(affectation_id=1, deleted_by=2)

        # Assert
        mock_event_bus.publish.assert_not_called()

    def test_should_not_publish_when_not_found(
        self, use_case, mock_affectation_repository, mock_event_bus
    ):
        """Test: pas de publication si affectation non trouvee."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = None

        # Act
        with pytest.raises(AffectationNotFoundError):
            use_case.execute(affectation_id=999, deleted_by=2)

        # Assert
        mock_event_bus.publish.assert_not_called()


# =============================================================================
# Tests Preservation des Donnees pour l'Event
# =============================================================================

class TestDeleteAffectationEventData:
    """Tests pour verifier que les donnees sont preservees pour l'event."""

    def test_should_preserve_affectation_data_for_event(
        self, use_case, mock_affectation_repository, mock_event_bus,
        existing_affectation_with_details
    ):
        """Test: les donnees de l'affectation sont preservees pour l'event."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = (
            existing_affectation_with_details
        )
        mock_affectation_repository.delete.return_value = True

        # Act
        use_case.execute(affectation_id=1, deleted_by=2)

        # Assert
        event = mock_event_bus.publish.call_args[0][0]
        # Les infos de l'affectation supprimee sont dans l'event
        assert event.utilisateur_id == 5
        assert event.chantier_id == 10
        assert event.date == date(2026, 1, 22)


# =============================================================================
# Tests Edge Cases
# =============================================================================

class TestDeleteAffectationEdgeCases:
    """Tests pour les cas limites."""

    def test_should_handle_different_deleted_by(
        self, use_case, mock_affectation_repository, mock_event_bus, existing_affectation
    ):
        """Test: gestion de differents utilisateurs qui suppriment."""
        # Arrange
        mock_affectation_repository.find_by_id.return_value = existing_affectation
        mock_affectation_repository.delete.return_value = True

        # Act
        use_case.execute(affectation_id=1, deleted_by=99)

        # Assert
        event = mock_event_bus.publish.call_args[0][0]
        assert event.deleted_by == 99

    def test_should_work_with_minimal_affectation(
        self, use_case, mock_affectation_repository
    ):
        """Test: suppression d'une affectation minimale."""
        # Arrange
        minimal_affectation = Affectation(
            id=1,
            utilisateur_id=1,
            chantier_id=1,
            date=date(2026, 1, 1),
            created_by=1,
        )
        mock_affectation_repository.find_by_id.return_value = minimal_affectation
        mock_affectation_repository.delete.return_value = True

        # Act
        result = use_case.execute(affectation_id=1, deleted_by=1)

        # Assert
        assert result is True
