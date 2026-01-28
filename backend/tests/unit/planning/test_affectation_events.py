"""Tests unitaires pour les Domain Events du module Planning.

Ce fichier teste :
- AffectationCreatedEvent
- AffectationUpdatedEvent
- AffectationDeletedEvent
- AffectationBulkCreatedEvent
- AffectationBulkDeletedEvent

Chaque event est teste pour :
- Creation avec valeurs valides
- Methode to_dict()
"""

import pytest
from datetime import date, datetime

from modules.planning.domain.events.affectation_events import (
    AffectationCreatedEvent,
    AffectationUpdatedEvent,
    AffectationDeletedEvent,
    AffectationBulkCreatedEvent,
    AffectationBulkDeletedEvent,
)


# =============================================================================
# Tests AffectationCreatedEvent
# =============================================================================

class TestAffectationCreatedEvent:
    """Tests pour l'event AffectationCreatedEvent."""

    def test_should_create_event_with_required_fields(self):
        """Test: creation avec tous les champs requis."""
        event = AffectationCreatedEvent(
            affectation_id=1,
            utilisateur_id=5,
            chantier_id=10,
            date=date(2026, 1, 22),
            created_by=3,
        )

        assert event.affectation_id == 1
        assert event.utilisateur_id == 5
        assert event.chantier_id == 10
        assert event.date == date(2026, 1, 22)
        assert event.created_by == 3

    def test_should_set_timestamp_automatically(self):
        """Test: timestamp initialise automatiquement."""
        before = datetime.now()
        event = AffectationCreatedEvent(
            affectation_id=1,
            utilisateur_id=5,
            chantier_id=10,
            date=date(2026, 1, 22),
            created_by=3,
        )
        after = datetime.now()

        assert before <= event.timestamp <= after

    def test_should_convert_to_dict(self):
        """Test: conversion en dictionnaire."""
        event = AffectationCreatedEvent(
            affectation_id=1,
            utilisateur_id=5,
            chantier_id=10,
            date=date(2026, 1, 22),
            created_by=3,
        )

        result = event.to_dict()

        assert result["event_type"] == "AffectationCreated"
        assert result["affectation_id"] == 1
        assert result["utilisateur_id"] == 5
        assert result["chantier_id"] == 10
        assert result["date"] == "2026-01-22"
        assert result["created_by"] == 3
        assert "timestamp" in result

    def test_should_be_immutable(self):
        """Test: event est immutable (frozen dataclass)."""
        event = AffectationCreatedEvent(
            affectation_id=1,
            utilisateur_id=5,
            chantier_id=10,
            date=date(2026, 1, 22),
            created_by=3,
        )

        with pytest.raises(AttributeError):
            event.affectation_id = 2


# =============================================================================
# Tests AffectationUpdatedEvent
# =============================================================================

class TestAffectationUpdatedEvent:
    """Tests pour l'event AffectationUpdatedEvent."""

    def test_should_create_event_with_changes(self):
        """Test: creation avec dictionnaire de changements."""
        changes = {"heure_debut": "09:00", "heure_fin": "18:00"}

        event = AffectationUpdatedEvent(
            affectation_id=1,
            utilisateur_id=5,
            chantier_id=10,
            changes=changes,
            updated_by=3,
        )

        assert event.affectation_id == 1
        assert event.changes == changes
        assert event.updated_by == 3

    def test_should_convert_to_dict(self):
        """Test: conversion en dictionnaire."""
        changes = {"note": "Nouvelle note"}

        event = AffectationUpdatedEvent(
            affectation_id=1,
            utilisateur_id=5,
            chantier_id=10,
            changes=changes,
            updated_by=3,
        )

        result = event.to_dict()

        assert result["event_type"] == "AffectationUpdated"
        assert result["affectation_id"] == 1
        assert result["changes"] == {"note": "Nouvelle note"}
        assert result["updated_by"] == 3

    def test_should_return_changed_fields(self):
        """Test: liste des champs modifies."""
        changes = {"heure_debut": "09:00", "note": "Note"}

        event = AffectationUpdatedEvent(
            affectation_id=1,
            utilisateur_id=5,
            chantier_id=10,
            changes=changes,
            updated_by=3,
        )

        assert "heure_debut" in event.changed_fields
        assert "note" in event.changed_fields
        assert len(event.changed_fields) == 2

    def test_should_check_if_field_changed(self):
        """Test: verification si un champ specifique a change."""
        changes = {"heure_debut": "09:00"}

        event = AffectationUpdatedEvent(
            affectation_id=1,
            utilisateur_id=5,
            chantier_id=10,
            changes=changes,
            updated_by=3,
        )

        assert event.has_changed("heure_debut") is True
        assert event.has_changed("heure_fin") is False
        assert event.has_changed("note") is False

    def test_should_be_immutable(self):
        """Test: event est immutable."""
        event = AffectationUpdatedEvent(
            affectation_id=1,
            utilisateur_id=5,
            chantier_id=10,
            changes={},
            updated_by=3,
        )

        with pytest.raises(AttributeError):
            event.affectation_id = 2


# =============================================================================
# Tests AffectationDeletedEvent
# =============================================================================

class TestAffectationDeletedEvent:
    """Tests pour l'event AffectationDeletedEvent."""

    def test_should_create_event_with_required_fields(self):
        """Test: creation avec tous les champs requis."""
        event = AffectationDeletedEvent(
            affectation_id=1,
            utilisateur_id=5,
            chantier_id=10,
            date=date(2026, 1, 22),
            deleted_by=3,
        )

        assert event.affectation_id == 1
        assert event.utilisateur_id == 5
        assert event.chantier_id == 10
        assert event.date == date(2026, 1, 22)
        assert event.deleted_by == 3

    def test_should_convert_to_dict(self):
        """Test: conversion en dictionnaire."""
        event = AffectationDeletedEvent(
            affectation_id=1,
            utilisateur_id=5,
            chantier_id=10,
            date=date(2026, 1, 22),
            deleted_by=3,
        )

        result = event.to_dict()

        assert result["event_type"] == "AffectationDeleted"
        assert result["affectation_id"] == 1
        assert result["utilisateur_id"] == 5
        assert result["chantier_id"] == 10
        assert result["date"] == "2026-01-22"
        assert result["deleted_by"] == 3

    def test_should_be_immutable(self):
        """Test: event est immutable."""
        event = AffectationDeletedEvent(
            affectation_id=1,
            utilisateur_id=5,
            chantier_id=10,
            date=date(2026, 1, 22),
            deleted_by=3,
        )

        with pytest.raises(AttributeError):
            event.affectation_id = 2


# =============================================================================
# Tests AffectationBulkCreatedEvent
# =============================================================================

class TestAffectationBulkCreatedEvent:
    """Tests pour l'event AffectationBulkCreatedEvent."""

    def test_should_create_event_with_multiple_ids(self):
        """Test: creation avec plusieurs IDs d'affectations."""
        event = AffectationBulkCreatedEvent(
            affectation_ids=(1, 2, 3, 4, 5),
            utilisateur_id=5,
            chantier_id=10,
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 24),
            created_by=3,
            count=5,
        )

        assert event.affectation_ids == (1, 2, 3, 4, 5)
        assert event.utilisateur_id == 5
        assert event.chantier_id == 10
        assert event.date_debut == date(2026, 1, 20)
        assert event.date_fin == date(2026, 1, 24)
        assert event.created_by == 3
        assert event.count == 5

    def test_should_convert_to_dict(self):
        """Test: conversion en dictionnaire."""
        event = AffectationBulkCreatedEvent(
            affectation_ids=(1, 2, 3),
            utilisateur_id=5,
            chantier_id=10,
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 22),
            created_by=3,
            count=3,
        )

        result = event.to_dict()

        assert result["event_type"] == "AffectationBulkCreated"
        assert result["affectation_ids"] == [1, 2, 3]  # Converti en liste
        assert result["utilisateur_id"] == 5
        assert result["chantier_id"] == 10
        assert result["date_debut"] == "2026-01-20"
        assert result["date_fin"] == "2026-01-22"
        assert result["created_by"] == 3
        assert result["count"] == 3

    def test_should_use_tuple_for_immutability(self):
        """Test: utilisation de tuple pour les IDs (immutable)."""
        event = AffectationBulkCreatedEvent(
            affectation_ids=(1, 2, 3),
            utilisateur_id=5,
            chantier_id=10,
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 22),
            created_by=3,
            count=3,
        )

        assert isinstance(event.affectation_ids, tuple)


# =============================================================================
# Tests AffectationBulkDeletedEvent
# =============================================================================

class TestAffectationBulkDeletedEvent:
    """Tests pour l'event AffectationBulkDeletedEvent."""

    def test_should_create_event_with_count(self):
        """Test: creation avec nombre d'affectations supprimees."""
        event = AffectationBulkDeletedEvent(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 24),
            deleted_by=3,
            count=10,
        )

        assert event.date_debut == date(2026, 1, 20)
        assert event.date_fin == date(2026, 1, 24)
        assert event.deleted_by == 3
        assert event.count == 10

    def test_should_create_event_with_optional_filters(self):
        """Test: creation avec filtres optionnels."""
        event = AffectationBulkDeletedEvent(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 24),
            deleted_by=3,
            count=5,
            utilisateur_id=5,
            chantier_id=10,
        )

        assert event.utilisateur_id == 5
        assert event.chantier_id == 10

    def test_should_have_none_optional_filters_by_default(self):
        """Test: filtres optionnels None par defaut."""
        event = AffectationBulkDeletedEvent(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 24),
            deleted_by=3,
            count=10,
        )

        assert event.utilisateur_id is None
        assert event.chantier_id is None

    def test_should_convert_to_dict(self):
        """Test: conversion en dictionnaire."""
        event = AffectationBulkDeletedEvent(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 24),
            deleted_by=3,
            count=10,
            utilisateur_id=5,
        )

        result = event.to_dict()

        assert result["event_type"] == "AffectationBulkDeleted"
        assert result["date_debut"] == "2026-01-20"
        assert result["date_fin"] == "2026-01-24"
        assert result["deleted_by"] == 3
        assert result["count"] == 10
        assert result["utilisateur_id"] == 5
        assert result["chantier_id"] is None


# =============================================================================
# Tests AffectationCancelledEvent
# =============================================================================

class TestAffectationCancelledEvent:
    """Tests pour l'event AffectationCancelledEvent."""

    def test_should_create_event_with_required_fields(self):
        """Test: création avec tous les champs requis."""
        from modules.planning.domain.events.affectation_cancelled import AffectationCancelledEvent

        event = AffectationCancelledEvent(
            affectation_id=42,
            user_id=5,
            chantier_id=10,
            date_affectation=date(2026, 1, 30),
            cancelled_by=3,
        )

        assert event.aggregate_id == "42"
        assert event.event_type == "affectation.cancelled"
        assert event.data["affectation_id"] == 42
        assert event.data["user_id"] == 5
        assert event.data["chantier_id"] == 10
        assert event.data["cancelled_by"] == 3
        assert event.data["date_affectation"] == "2026-01-30"

    def test_should_create_event_with_optional_raison(self):
        """Test: création avec raison d'annulation optionnelle."""
        from modules.planning.domain.events.affectation_cancelled import AffectationCancelledEvent

        event = AffectationCancelledEvent(
            affectation_id=42,
            user_id=5,
            chantier_id=10,
            date_affectation=date(2026, 1, 30),
            cancelled_by=3,
            raison="Intempéries",
        )

        assert event.data["raison"] == "Intempéries"

    def test_should_have_none_raison_by_default(self):
        """Test: raison est None par défaut."""
        from modules.planning.domain.events.affectation_cancelled import AffectationCancelledEvent

        event = AffectationCancelledEvent(
            affectation_id=42,
            user_id=5,
            chantier_id=10,
            date_affectation=date(2026, 1, 30),
            cancelled_by=3,
        )

        assert event.data["raison"] is None

    def test_should_convert_to_dict(self):
        """Test: conversion en dictionnaire."""
        from modules.planning.domain.events.affectation_cancelled import AffectationCancelledEvent

        event = AffectationCancelledEvent(
            affectation_id=42,
            user_id=5,
            chantier_id=10,
            date_affectation=date(2026, 1, 30),
            cancelled_by=3,
            raison="Test",
        )

        result = event.to_dict()

        assert result["event_type"] == "affectation.cancelled"
        assert result["aggregate_id"] == "42"
        assert "data" in result
        assert result["data"]["affectation_id"] == 42
        assert result["data"]["user_id"] == 5
        assert result["data"]["chantier_id"] == 10
        assert result["data"]["cancelled_by"] == 3
        assert result["data"]["raison"] == "Test"
        assert "occurred_at" in result

    def test_should_be_immutable(self):
        """Test: event est immutable (frozen dataclass)."""
        from modules.planning.domain.events.affectation_cancelled import AffectationCancelledEvent

        event = AffectationCancelledEvent(
            affectation_id=42,
            user_id=5,
            chantier_id=10,
            date_affectation=date(2026, 1, 30),
            cancelled_by=3,
        )

        # Tentative de modification doit lever FrozenInstanceError
        with pytest.raises(Exception):  # FrozenInstanceError est une sous-classe de AttributeError
            event.event_type = "modified"

    def test_should_format_date_as_iso(self):
        """Test: date formatée en ISO dans data."""
        from modules.planning.domain.events.affectation_cancelled import AffectationCancelledEvent

        event = AffectationCancelledEvent(
            affectation_id=42,
            user_id=5,
            chantier_id=10,
            date_affectation=date(2026, 1, 30),
            cancelled_by=3,
        )

        # La date doit être formatée en ISO string dans data
        assert event.data["date_affectation"] == "2026-01-30"

    def test_should_handle_metadata(self):
        """Test: gestion des métadonnées."""
        from modules.planning.domain.events.affectation_cancelled import AffectationCancelledEvent

        metadata = {"ip_address": "192.168.1.1", "user_agent": "Test"}

        event = AffectationCancelledEvent(
            affectation_id=42,
            user_id=5,
            chantier_id=10,
            date_affectation=date(2026, 1, 30),
            cancelled_by=3,
            metadata=metadata,
        )

        assert event.metadata == metadata
        assert event.metadata["ip_address"] == "192.168.1.1"
