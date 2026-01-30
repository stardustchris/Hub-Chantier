"""Tests unitaires pour UpdateAffectationNoteUseCase."""

from datetime import date, datetime
from unittest.mock import Mock

import pytest

from modules.planning.application.use_cases import (
    UpdateAffectationNoteUseCase,
    AffectationNotFoundError,
)
from modules.planning.domain.entities import Affectation
from modules.planning.domain.value_objects import TypeAffectation
from modules.planning.domain.events import AffectationUpdatedEvent


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_affectation_repo():
    """Mock du repository d'affectations."""
    return Mock()


@pytest.fixture
def mock_event_bus():
    """Mock de l'EventBus."""
    return Mock()


@pytest.fixture
def use_case(mock_affectation_repo, mock_event_bus):
    """Instance du use case avec mocks."""
    return UpdateAffectationNoteUseCase(
        affectation_repo=mock_affectation_repo,
        event_bus=mock_event_bus,
    )


@pytest.fixture
def sample_affectation():
    """Affectation de test."""
    return Affectation(
        id=42,
        utilisateur_id=5,
        chantier_id=10,
        date=date(2026, 1, 22),
        heures_prevues=8.0,
        note="Note originale",
        type_affectation=TypeAffectation.UNIQUE,
        created_by=1,
    )


# =============================================================================
# Tests de modification de note
# =============================================================================


class TestUpdateAffectationNote:
    """Tests de mise a jour de note."""

    def test_should_update_note_when_provided(
        self,
        use_case,
        mock_affectation_repo,
        mock_event_bus,
        sample_affectation,
    ):
        """La note doit etre mise a jour quand fournie."""
        mock_affectation_repo.find_by_id.return_value = sample_affectation
        mock_affectation_repo.save.return_value = sample_affectation

        result = use_case.execute(
            affectation_id=42,
            note="Nouvelle note importante",
            modified_by=3,
        )

        assert result.note == "Nouvelle note importante"
        mock_affectation_repo.save.assert_called_once()

    def test_should_remove_note_when_none(
        self,
        use_case,
        mock_affectation_repo,
        sample_affectation,
    ):
        """La note doit etre supprimee quand None."""
        mock_affectation_repo.find_by_id.return_value = sample_affectation
        mock_affectation_repo.save.return_value = sample_affectation

        result = use_case.execute(
            affectation_id=42,
            note=None,
            modified_by=3,
        )

        assert result.note is None
        mock_affectation_repo.save.assert_called_once()

    def test_should_remove_note_when_empty_string(
        self,
        use_case,
        mock_affectation_repo,
        sample_affectation,
    ):
        """La note doit etre supprimee quand chaine vide."""
        mock_affectation_repo.find_by_id.return_value = sample_affectation
        mock_affectation_repo.save.return_value = sample_affectation

        result = use_case.execute(
            affectation_id=42,
            note="   ",
            modified_by=3,
        )

        assert result.note is None
        mock_affectation_repo.save.assert_called_once()

    def test_should_raise_when_affectation_not_found(
        self,
        use_case,
        mock_affectation_repo,
    ):
        """Doit lever une exception si affectation non trouvee."""
        mock_affectation_repo.find_by_id.return_value = None

        with pytest.raises(AffectationNotFoundError) as exc_info:
            use_case.execute(
                affectation_id=999,
                note="Note",
                modified_by=3,
            )

        assert exc_info.value.affectation_id == 999


# =============================================================================
# Tests des evenements
# =============================================================================


class TestUpdateAffectationNoteEvents:
    """Tests de publication d'evenements."""

    def test_should_publish_event_when_note_changed(
        self,
        use_case,
        mock_affectation_repo,
        mock_event_bus,
        sample_affectation,
    ):
        """Doit publier un evenement quand la note change."""
        mock_affectation_repo.find_by_id.return_value = sample_affectation
        mock_affectation_repo.save.return_value = sample_affectation

        use_case.execute(
            affectation_id=42,
            note="Nouvelle note",
            modified_by=3,
        )

        # Verifier qu'un evenement a ete publie
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert isinstance(event, AffectationUpdatedEvent)
        assert event.affectation_id == 42
        assert event.updated_by == 3
        assert "note" in event.changes
        assert event.changes["note"]["old"] == "Note originale"
        assert event.changes["note"]["new"] == "Nouvelle note"

    def test_should_not_publish_event_when_note_unchanged(
        self,
        use_case,
        mock_affectation_repo,
        mock_event_bus,
        sample_affectation,
    ):
        """Ne doit pas publier d'evenement si la note n'a pas change."""
        mock_affectation_repo.find_by_id.return_value = sample_affectation
        mock_affectation_repo.save.return_value = sample_affectation

        use_case.execute(
            affectation_id=42,
            note="Note originale",  # Meme note
            modified_by=3,
        )

        # Aucun evenement ne devrait etre publie
        mock_event_bus.publish.assert_not_called()

    def test_should_publish_event_when_note_removed(
        self,
        use_case,
        mock_affectation_repo,
        mock_event_bus,
        sample_affectation,
    ):
        """Doit publier un evenement quand la note est supprimee."""
        mock_affectation_repo.find_by_id.return_value = sample_affectation
        mock_affectation_repo.save.return_value = sample_affectation

        use_case.execute(
            affectation_id=42,
            note=None,
            modified_by=3,
        )

        # Verifier qu'un evenement a ete publie
        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert event.changes["note"]["old"] == "Note originale"
        assert event.changes["note"]["new"] is None
