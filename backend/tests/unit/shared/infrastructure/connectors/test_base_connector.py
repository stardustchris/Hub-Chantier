"""Tests unitaires pour BaseConnector."""

import pytest
from datetime import datetime

from shared.infrastructure.event_bus.domain_event import DomainEvent
from shared.infrastructure.connectors.base_connector import (
    BaseConnector,
    ConnectorError,
)


class TestConnector(BaseConnector):
    """Connecteur de test pour valider BaseConnector."""

    def __init__(self):
        super().__init__(
            name="test",
            supported_events=["test.created", "test.updated"]
        )

    def format_data(self, event: DomainEvent) -> dict:
        """Formatter de test."""
        return {"formatted": True, "data": event.data}

    def get_api_endpoint(self, event_type: str) -> str:
        """Endpoint de test."""
        if event_type == "test.created":
            return "/test/create"
        elif event_type == "test.updated":
            return "/test/update"
        else:
            raise ConnectorError(
                "Endpoint non trouvé",
                connector_name=self.name,
                event_type=event_type
            )


class TestBaseConnector:
    """Tests pour la classe abstraite BaseConnector."""

    def test_initialization(self):
        """Test l'initialisation du connecteur."""
        connector = TestConnector()

        assert connector.name == "test"
        assert connector.supported_events == ["test.created", "test.updated"]

    def test_supports_event(self):
        """Test la méthode supports_event."""
        connector = TestConnector()

        assert connector.supports_event("test.created") is True
        assert connector.supports_event("test.updated") is True
        assert connector.supports_event("other.event") is False

    def test_transform_event_success(self):
        """Test la transformation d'un événement supporté."""
        connector = TestConnector()
        event = DomainEvent(
            event_type="test.created",
            aggregate_id="123",
            data={"foo": "bar"},
            occurred_at=datetime(2026, 1, 31, 12, 0, 0)
        )

        payload = connector.transform_event(event)

        assert payload["endpoint"] == "/test/create"
        assert payload["data"]["formatted"] is True
        assert payload["data"]["data"] == {"foo": "bar"}
        assert payload["metadata"]["source"] == "hub-chantier"
        assert payload["metadata"]["event_type"] == "test.created"
        assert payload["metadata"]["connector"] == "test"
        assert "event_id" in payload["metadata"]

    def test_transform_event_unsupported(self):
        """Test la transformation d'un événement non supporté."""
        connector = TestConnector()
        event = DomainEvent(
            event_type="unsupported.event",
            data={"foo": "bar"}
        )

        with pytest.raises(ConnectorError) as exc_info:
            connector.transform_event(event)

        assert "non supporté" in str(exc_info.value)
        assert "unsupported.event" in str(exc_info.value)

    def test_transform_event_formatter_error(self):
        """Test la gestion d'erreur du formatter."""
        class BrokenConnector(BaseConnector):
            def __init__(self):
                super().__init__(name="broken", supported_events=["test.event"])

            def format_data(self, event: DomainEvent) -> dict:
                raise ValueError("Formatter broken")

            def get_api_endpoint(self, event_type: str) -> str:
                return "/test"

        connector = BrokenConnector()
        event = DomainEvent(event_type="test.event", data={})

        with pytest.raises(ConnectorError) as exc_info:
            connector.transform_event(event)

        assert "Erreur de transformation" in str(exc_info.value)

    def test_connector_error_attributes(self):
        """Test les attributs de ConnectorError."""
        error = ConnectorError(
            "Test error",
            connector_name="test",
            event_type="test.event"
        )

        assert error.connector_name == "test"
        assert error.event_type == "test.event"
        assert "test" in str(error)
        assert "test.event" in str(error)
        assert "Test error" in str(error)

    def test_repr(self):
        """Test la représentation string du connecteur."""
        connector = TestConnector()
        repr_str = repr(connector)

        assert "TestConnector" in repr_str
        assert "name=test" in repr_str
        assert "events=2" in repr_str
