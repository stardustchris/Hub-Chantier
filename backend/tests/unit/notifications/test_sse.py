"""Tests unitaires pour le SSE Manager et l'endpoint SSE."""

import asyncio
import pytest
from unittest.mock import patch

from modules.notifications.infrastructure.web.sse import SSEManager
from shared.domain.events.domain_event import DomainEvent


@pytest.fixture
def sse_manager():
    """Crée un SSEManager frais pour chaque test."""
    return SSEManager()


class TestSSEManagerConnect:
    """Tests de connexion SSE."""

    def test_connect_returns_queue(self, sse_manager):
        queue = sse_manager.connect(user_id=1)
        assert isinstance(queue, asyncio.Queue)

    def test_connect_tracks_user(self, sse_manager):
        sse_manager.connect(user_id=1)
        assert sse_manager.connected_users_count == 1

    def test_connect_multiple_tabs(self, sse_manager):
        """Un utilisateur peut avoir plusieurs connexions (multi-onglet)."""
        q1 = sse_manager.connect(user_id=1)
        q2 = sse_manager.connect(user_id=1)
        assert q1 is not q2
        assert sse_manager.connected_users_count == 1

    def test_connect_multiple_users(self, sse_manager):
        sse_manager.connect(user_id=1)
        sse_manager.connect(user_id=2)
        assert sse_manager.connected_users_count == 2


class TestSSEManagerDisconnect:
    """Tests de déconnexion SSE."""

    def test_disconnect_removes_queue(self, sse_manager):
        queue = sse_manager.connect(user_id=1)
        sse_manager.disconnect(user_id=1, queue=queue)
        assert sse_manager.connected_users_count == 0

    def test_disconnect_one_tab_keeps_others(self, sse_manager):
        q1 = sse_manager.connect(user_id=1)
        q2 = sse_manager.connect(user_id=1)
        sse_manager.disconnect(user_id=1, queue=q1)
        assert sse_manager.connected_users_count == 1

    def test_disconnect_nonexistent_queue(self, sse_manager):
        """Disconnect d'une queue inconnue ne plante pas."""
        sse_manager.connect(user_id=1)
        fake_queue = asyncio.Queue()
        sse_manager.disconnect(user_id=1, queue=fake_queue)
        assert sse_manager.connected_users_count == 1


class TestSSEManagerSend:
    """Tests d'envoi de messages SSE."""

    def test_send_to_user(self, sse_manager):
        queue = sse_manager.connect(user_id=1)
        asyncio.get_event_loop().run_until_complete(
            sse_manager.send_to_user(1, "notification.created", {"id": 42})
        )
        event = queue.get_nowait()
        assert event["event"] == "notification.created"
        assert event["data"]["id"] == 42

    def test_send_to_nonexistent_user(self, sse_manager):
        """Envoyer à un user non connecté ne plante pas."""
        asyncio.get_event_loop().run_until_complete(
            sse_manager.send_to_user(999, "test", {"x": 1})
        )

    def test_send_to_multiple_tabs(self, sse_manager):
        q1 = sse_manager.connect(user_id=1)
        q2 = sse_manager.connect(user_id=1)
        asyncio.get_event_loop().run_until_complete(
            sse_manager.send_to_user(1, "test", {"val": 1})
        )
        assert q1.get_nowait()["event"] == "test"
        assert q2.get_nowait()["event"] == "test"

    def test_broadcast_to_all_users(self, sse_manager):
        q1 = sse_manager.connect(user_id=1)
        q2 = sse_manager.connect(user_id=2)
        asyncio.get_event_loop().run_until_complete(
            sse_manager.broadcast("system.alert", {"msg": "hello"})
        )
        assert q1.get_nowait()["event"] == "system.alert"
        assert q2.get_nowait()["event"] == "system.alert"

    def test_queue_full_does_not_crash(self, sse_manager):
        """Queue pleine (maxsize=100) ne bloque pas l'envoi."""
        queue = sse_manager.connect(user_id=1)
        for i in range(100):
            queue.put_nowait({"event": "fill", "data": {"i": i}})
        # L'envoi suivant ne doit pas lever d'exception
        asyncio.get_event_loop().run_until_complete(
            sse_manager.send_to_user(1, "overflow", {"x": 1})
        )


class TestSSEManagerDomainEvents:
    """Tests d'intégration avec le bus d'événements."""

    def test_handle_targeted_event(self, sse_manager):
        """Un événement avec user_id est envoyé à cet utilisateur."""
        q1 = sse_manager.connect(user_id=1)
        q2 = sse_manager.connect(user_id=2)

        event = DomainEvent(
            event_type="notification.created",
            aggregate_id="42",
            data={"user_id": 1, "title": "Test"},
        )
        asyncio.get_event_loop().run_until_complete(
            sse_manager._handle_domain_event(event)
        )

        assert not q1.empty()
        assert q2.empty()

    def test_handle_broadcast_event(self, sse_manager):
        """Un événement sans target_user_id est broadcasté."""
        q1 = sse_manager.connect(user_id=1)
        q2 = sse_manager.connect(user_id=2)

        event = DomainEvent(
            event_type="chantier.created",
            aggregate_id="99",
            data={"nom": "Test"},
        )
        asyncio.get_event_loop().run_until_complete(
            sse_manager._handle_domain_event(event)
        )

        assert not q1.empty()
        assert not q2.empty()

    def test_handle_event_extracts_target_user_id(self, sse_manager):
        """Supporte aussi la clé target_user_id."""
        q1 = sse_manager.connect(user_id=5)

        event = DomainEvent(
            event_type="tache.assigned",
            aggregate_id="10",
            data={"target_user_id": 5, "tache": "Coffrage"},
        )
        asyncio.get_event_loop().run_until_complete(
            sse_manager._handle_domain_event(event)
        )

        msg = q1.get_nowait()
        assert msg["event"] == "tache.assigned"

    def test_event_data_format(self, sse_manager):
        """Les données envoyées contiennent event_type, aggregate_id, occurred_at."""
        queue = sse_manager.connect(user_id=1)

        event = DomainEvent(
            event_type="test.event",
            aggregate_id="7",
            data={"user_id": 1},
        )
        asyncio.get_event_loop().run_until_complete(
            sse_manager._handle_domain_event(event)
        )

        msg = queue.get_nowait()
        assert "event_type" in msg["data"]
        assert "aggregate_id" in msg["data"]
        assert "occurred_at" in msg["data"]
        assert msg["data"]["event_type"] == "test.event"
        assert msg["data"]["aggregate_id"] == "7"


class TestSSEManagerInitialize:
    """Tests d'initialisation du manager."""

    def test_initialize_subscribes_once(self, sse_manager):
        with patch("modules.notifications.infrastructure.web.sse.event_bus") as mock_bus:
            sse_manager.initialize()
            sse_manager.initialize()  # Deuxième appel = no-op
            assert mock_bus.subscribe_all.call_count == 1

    def test_not_initialized_by_default(self, sse_manager):
        assert sse_manager._initialized is False
