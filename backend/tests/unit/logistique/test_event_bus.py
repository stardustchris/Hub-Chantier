"""Tests unitaires pour l'EventBus du module Logistique.

H12: Amélioration de la couverture de tests à 85%.
"""

import pytest
from datetime import date, time, datetime
from unittest.mock import Mock, MagicMock, patch
import logging

from modules.logistique.infrastructure.event_bus_impl import (
    LogistiqueEventBus,
    NoOpEventBus,
)
from modules.logistique.domain.events import (
    RessourceCreatedEvent,
    RessourceUpdatedEvent,
    RessourceDeletedEvent,
    ReservationCreatedEvent,
    ReservationValideeEvent,
    ReservationRefuseeEvent,
    ReservationAnnuleeEvent,
    ReservationConflitEvent,
)


class TestLogistiqueEventBus:
    """Tests pour LogistiqueEventBus."""

    @pytest.fixture
    def mock_core_bus(self):
        """Mock du CoreEventBus."""
        return MagicMock()

    @pytest.fixture
    def event_bus_with_core(self, mock_core_bus):
        """EventBus avec CoreBus configuré."""
        return LogistiqueEventBus(mock_core_bus)

    @pytest.fixture
    def event_bus_without_core(self):
        """EventBus sans CoreBus."""
        return LogistiqueEventBus(None)

    def test_publish_with_core_bus(self, event_bus_with_core, mock_core_bus):
        """Test: publish délègue au CoreEventBus."""
        event = RessourceCreatedEvent(
            ressource_id=1,
            nom="Grue",
            code="GRU001",
            categorie="engin_levage",
            created_by=10,
        )

        event_bus_with_core.publish(event)

        mock_core_bus.publish.assert_called_once_with(event)

    def test_publish_without_core_bus_logs_only(self, event_bus_without_core, caplog):
        """Test: publish sans CoreBus log uniquement."""
        event = RessourceCreatedEvent(
            ressource_id=1,
            nom="Grue",
            code="GRU001",
            categorie="engin_levage",
            created_by=10,
        )

        with caplog.at_level(logging.DEBUG):
            event_bus_without_core.publish(event)

        assert "RessourceCreatedEvent" in caplog.text

    def test_publish_handles_core_bus_error(self, event_bus_with_core, mock_core_bus, caplog):
        """Test: publish gère les erreurs du CoreBus."""
        mock_core_bus.publish.side_effect = Exception("Test error")
        event = RessourceCreatedEvent(
            ressource_id=1,
            nom="Grue",
            code="GRU001",
            categorie="engin_levage",
            created_by=10,
        )

        with caplog.at_level(logging.ERROR):
            event_bus_with_core.publish(event)

        assert "Error publishing event" in caplog.text

    def test_publish_many_publishes_all_events(self, event_bus_with_core, mock_core_bus):
        """Test: publish_many publie tous les événements."""
        events = [
            RessourceCreatedEvent(
                ressource_id=i,
                nom=f"Grue {i}",
                code=f"GRU00{i}",
                categorie="engin_levage",
                created_by=10,
            )
            for i in range(3)
        ]

        event_bus_with_core.publish_many(events)

        assert mock_core_bus.publish.call_count == 3

    def test_log_event_for_audit_ressource_event(self, event_bus_with_core, caplog):
        """Test: audit log pour événement ressource."""
        event = RessourceCreatedEvent(
            ressource_id=1,
            nom="Grue",
            code="GRU001",
            categorie="engin_levage",
            created_by=10,
        )

        with caplog.at_level(logging.INFO):
            event_bus_with_core._log_event_for_audit(event)

        assert "[AUDIT][LOGISTIQUE]" in caplog.text
        assert "RessourceCreatedEvent" in caplog.text
        assert "ressource_id=1" in caplog.text

    def test_log_event_for_audit_reservation_event(self, event_bus_with_core, caplog):
        """Test: audit log pour événement réservation."""
        event = ReservationCreatedEvent(
            reservation_id=1,
            ressource_id=1,
            ressource_nom="Grue",
            chantier_id=100,
            demandeur_id=10,
            date_reservation=date.today(),
            heure_debut=time(8, 0),
            heure_fin=time(12, 0),
            validation_requise=True,
        )

        with caplog.at_level(logging.INFO):
            event_bus_with_core._log_event_for_audit(event)

        assert "[AUDIT][LOGISTIQUE]" in caplog.text
        assert "ReservationCreatedEvent" in caplog.text
        assert "reservation_id=1" in caplog.text

    def test_extract_event_details_ressource_created(self, event_bus_with_core):
        """Test: extraction détails RessourceCreatedEvent."""
        event = RessourceCreatedEvent(
            ressource_id=1,
            nom="Grue",
            code="GRU001",
            categorie="engin_levage",
            created_by=10,
        )

        details = event_bus_with_core._extract_event_details(event)

        assert "ressource_id=1" in details
        assert "code=GRU001" in details
        assert "created_by=10" in details

    def test_extract_event_details_ressource_updated(self, event_bus_with_core):
        """Test: extraction détails RessourceUpdatedEvent."""
        event = RessourceUpdatedEvent(
            ressource_id=1,
            nom="Grue modifiée",
            code="GRU001",
            updated_by=10,
        )

        details = event_bus_with_core._extract_event_details(event)

        assert "ressource_id=1" in details
        assert "updated_by=10" in details

    def test_extract_event_details_ressource_deleted(self, event_bus_with_core):
        """Test: extraction détails RessourceDeletedEvent."""
        event = RessourceDeletedEvent(
            ressource_id=1,
            deleted_by=10,
        )

        details = event_bus_with_core._extract_event_details(event)

        assert "ressource_id=1" in details
        assert "deleted_by=10" in details

    def test_extract_event_details_reservation_validee(self, event_bus_with_core):
        """Test: extraction détails ReservationValideeEvent."""
        event = ReservationValideeEvent(
            reservation_id=1,
            ressource_id=1,
            ressource_nom="Grue",
            demandeur_id=10,
            valideur_id=5,
            date_reservation=date.today(),
        )

        details = event_bus_with_core._extract_event_details(event)

        assert "reservation_id=1" in details
        assert "valideur_id=5" in details

    def test_extract_event_details_reservation_refusee_with_motif(self, event_bus_with_core):
        """Test: extraction détails ReservationRefuseeEvent avec motif."""
        event = ReservationRefuseeEvent(
            reservation_id=1,
            ressource_id=1,
            ressource_nom="Grue",
            demandeur_id=10,
            valideur_id=5,
            date_reservation=date.today(),
            motif="Ressource déjà réservée pour maintenance",
        )

        details = event_bus_with_core._extract_event_details(event)

        assert "reservation_id=1" in details
        assert "motif=" in details

    def test_extract_event_details_reservation_refusee_long_motif_truncated(
        self, event_bus_with_core
    ):
        """Test: motif long tronqué à 50 caractères."""
        long_motif = "A" * 100
        event = ReservationRefuseeEvent(
            reservation_id=1,
            ressource_id=1,
            ressource_nom="Grue",
            demandeur_id=10,
            valideur_id=5,
            date_reservation=date.today(),
            motif=long_motif,
        )

        details = event_bus_with_core._extract_event_details(event)

        # Motif devrait être tronqué avec "..."
        assert "..." in details

    def test_extract_event_details_unknown_event(self, event_bus_with_core):
        """Test: événement inconnu retourne 'no details'."""

        class UnknownEvent:
            pass

        event = UnknownEvent()

        details = event_bus_with_core._extract_event_details(event)

        assert details == "no details"


class TestNoOpEventBus:
    """Tests pour NoOpEventBus."""

    @pytest.fixture
    def event_bus(self):
        """NoOpEventBus pour tests."""
        return NoOpEventBus()

    def test_publish_does_nothing(self, event_bus):
        """Test: publish ne fait rien."""
        event = RessourceCreatedEvent(
            ressource_id=1,
            nom="Grue",
            code="GRU001",
            categorie="engin_levage",
            created_by=10,
        )

        # Should not raise
        event_bus.publish(event)

    def test_publish_many_does_nothing(self, event_bus):
        """Test: publish_many ne fait rien."""
        events = [
            RessourceCreatedEvent(
                ressource_id=i,
                nom=f"Grue {i}",
                code=f"GRU00{i}",
                categorie="engin_levage",
                created_by=10,
            )
            for i in range(3)
        ]

        # Should not raise
        event_bus.publish_many(events)
