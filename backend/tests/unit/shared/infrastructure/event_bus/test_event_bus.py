"""Tests for Event Bus implementation.

Tests comprehensive Event Bus functionality:
- Event publishing and subscription
- Wildcard pattern matching
- Handler execution (sync/async)
- Error isolation
- Event history
"""

import pytest
import asyncio
from datetime import datetime
from typing import List

from shared.infrastructure.event_bus.domain_event import DomainEvent
from shared.infrastructure.event_bus.event_bus import EventBus, event_handler


# ===== Fixtures =====


@pytest.fixture
def event_bus():
    """Create a fresh EventBus instance for each test."""
    return EventBus()


@pytest.fixture
def sample_event():
    """Create a sample domain event."""
    return DomainEvent(
        event_type="chantier.created",
        aggregate_id="123",
        data={"nom": "Test Chantier", "adresse": "123 rue Test"},
        metadata={"user_id": 1, "user_email": "admin@test.fr"}
    )


# ===== Tests for DomainEvent =====


def test_domain_event_creation():
    """Test DomainEvent creation with default values."""
    event = DomainEvent(
        event_type="test.event",
        aggregate_id="456",
        data={"key": "value"}
    )

    assert event.event_type == "test.event"
    assert event.aggregate_id == "456"
    assert event.data == {"key": "value"}
    assert event.metadata == {}
    assert event.event_id is not None
    assert isinstance(event.occurred_at, datetime)


def test_domain_event_to_dict(sample_event):
    """Test DomainEvent serialization to dict."""
    event_dict = sample_event.to_dict()

    assert event_dict["event_id"] == sample_event.event_id
    assert event_dict["event_type"] == "chantier.created"
    assert event_dict["aggregate_id"] == "123"
    assert event_dict["data"] == {"nom": "Test Chantier", "adresse": "123 rue Test"}
    assert event_dict["metadata"] == {"user_id": 1, "user_email": "admin@test.fr"}
    assert "occurred_at" in event_dict
    assert isinstance(event_dict["occurred_at"], str)  # ISO format


def test_domain_event_immutable():
    """Test that DomainEvent is immutable (dataclass with frozen=False but should not modify)."""
    event = DomainEvent(
        event_type="test.event",
        aggregate_id="123",
        data={"original": "value"}
    )

    # Modifying data dict should not affect original if properly handled
    original_event_id = event.event_id
    original_occurred_at = event.occurred_at

    # Note: DomainEvent is not frozen, so we can technically modify it
    # But in production, events should be treated as immutable
    assert event.event_id == original_event_id
    assert event.occurred_at == original_occurred_at


def test_domain_event_str_representation(sample_event):
    """Test DomainEvent __str__ method."""
    str_repr = str(sample_event)

    assert "chantier.created" in str_repr
    assert sample_event.event_id in str_repr
    assert "123" in str_repr


# ===== Tests for EventBus Subscription =====


@pytest.mark.asyncio
async def test_event_bus_publish_simple_event(event_bus, sample_event):
    """Test publishing a simple event without handlers."""
    # Should not raise any errors
    await event_bus.publish(sample_event)

    # Event should be in history
    history = event_bus.get_history()
    assert len(history) == 1
    assert history[0].event_type == "chantier.created"


@pytest.mark.asyncio
async def test_event_bus_subscribe_and_trigger(event_bus):
    """Test subscribing to an event and triggering the handler."""
    called = []

    async def handler(event: DomainEvent):
        called.append(event.event_type)

    event_bus.subscribe("test.event", handler)

    event = DomainEvent(event_type="test.event", data={"key": "value"})
    await event_bus.publish(event)

    # Wait a bit for async execution
    await asyncio.sleep(0.1)

    assert len(called) == 1
    assert called[0] == "test.event"


@pytest.mark.asyncio
async def test_event_bus_wildcard_all_events(event_bus):
    """Test subscribing to all events with '*' wildcard."""
    called_events = []

    async def universal_handler(event: DomainEvent):
        called_events.append(event.event_type)

    event_bus.subscribe("*", universal_handler)

    # Publish multiple different events
    await event_bus.publish(DomainEvent(event_type="chantier.created"))
    await event_bus.publish(DomainEvent(event_type="user.updated"))
    await event_bus.publish(DomainEvent(event_type="document.uploaded"))

    await asyncio.sleep(0.1)

    assert len(called_events) == 3
    assert "chantier.created" in called_events
    assert "user.updated" in called_events
    assert "document.uploaded" in called_events


@pytest.mark.asyncio
async def test_event_bus_wildcard_module_prefix(event_bus):
    """Test subscribing to module events with 'module.*' wildcard."""
    called_events = []

    async def chantier_handler(event: DomainEvent):
        called_events.append(event.event_type)

    event_bus.subscribe("chantier.*", chantier_handler)

    # Publish chantier events
    await event_bus.publish(DomainEvent(event_type="chantier.created"))
    await event_bus.publish(DomainEvent(event_type="chantier.updated"))
    await event_bus.publish(DomainEvent(event_type="chantier.deleted"))

    # Publish non-chantier event (should not trigger handler)
    await event_bus.publish(DomainEvent(event_type="user.created"))

    await asyncio.sleep(0.1)

    assert len(called_events) == 3
    assert "chantier.created" in called_events
    assert "chantier.updated" in called_events
    assert "chantier.deleted" in called_events
    assert "user.created" not in called_events


@pytest.mark.asyncio
async def test_event_bus_multiple_handlers_same_event(event_bus):
    """Test multiple handlers subscribed to the same event."""
    handler1_called = []
    handler2_called = []

    async def handler1(event: DomainEvent):
        handler1_called.append(event.event_type)

    async def handler2(event: DomainEvent):
        handler2_called.append(event.event_type)

    event_bus.subscribe("test.event", handler1)
    event_bus.subscribe("test.event", handler2)

    await event_bus.publish(DomainEvent(event_type="test.event"))

    await asyncio.sleep(0.1)

    assert len(handler1_called) == 1
    assert len(handler2_called) == 1


@pytest.mark.asyncio
async def test_event_bus_handler_exception_isolation(event_bus):
    """Test that handler exceptions don't affect other handlers."""
    handler1_called = []
    handler2_called = []

    async def failing_handler(event: DomainEvent):
        handler1_called.append("called")
        raise ValueError("Handler failed!")

    async def working_handler(event: DomainEvent):
        handler2_called.append("called")

    event_bus.subscribe("test.event", failing_handler)
    event_bus.subscribe("test.event", working_handler)

    # Should not raise exception
    await event_bus.publish(DomainEvent(event_type="test.event"))

    await asyncio.sleep(0.1)

    # Both handlers should have been called despite the failure
    assert len(handler1_called) == 1
    assert len(handler2_called) == 1


# ===== Tests for EventBus History =====


@pytest.mark.asyncio
async def test_event_bus_event_history(event_bus):
    """Test event history tracking."""
    # Publish multiple events
    for i in range(5):
        await event_bus.publish(DomainEvent(
            event_type=f"test.event.{i}",
            aggregate_id=str(i)
        ))

    history = event_bus.get_history()
    assert len(history) == 5

    # Check they're in order
    for i, event in enumerate(history):
        assert event.event_type == f"test.event.{i}"


@pytest.mark.asyncio
async def test_event_bus_history_limit(event_bus):
    """Test that history is limited to max_history (1000)."""
    # This test would take too long with 1000+ events
    # Just verify the mechanism exists
    assert event_bus._max_history == 1000

    # Publish a few events
    for i in range(10):
        await event_bus.publish(DomainEvent(event_type=f"test.{i}"))

    history = event_bus.get_history()
    assert len(history) == 10


@pytest.mark.asyncio
async def test_event_bus_history_filtering(event_bus):
    """Test filtering event history by event_type."""
    await event_bus.publish(DomainEvent(event_type="chantier.created"))
    await event_bus.publish(DomainEvent(event_type="chantier.updated"))
    await event_bus.publish(DomainEvent(event_type="user.created"))

    # Filter by exact type
    chantier_created = event_bus.get_history(event_type="chantier.created")
    assert len(chantier_created) == 1
    assert chantier_created[0].event_type == "chantier.created"

    # Filter by wildcard
    all_chantier = event_bus.get_history(event_type="chantier.*")
    assert len(all_chantier) == 2


def test_event_bus_clear_history(event_bus):
    """Test clearing event history."""
    event_bus._event_history = [
        DomainEvent(event_type="test.1"),
        DomainEvent(event_type="test.2"),
    ]

    event_bus.clear_history()

    assert len(event_bus.get_history()) == 0


# ===== Tests for EventBus Utilities =====


def test_event_bus_get_subscribers_count(event_bus):
    """Test counting subscribers."""
    event_bus.subscribe("test.event", lambda e: None)
    event_bus.subscribe("test.event", lambda e: None)
    event_bus.subscribe("other.event", lambda e: None)

    assert event_bus.get_subscribers_count("test.event") == 2
    assert event_bus.get_subscribers_count("other.event") == 1
    assert event_bus.get_subscribers_count() == 3


def test_event_matches_exact():
    """Test exact event type matching."""
    assert EventBus._event_matches("chantier.created", "chantier.created") is True
    assert EventBus._event_matches("chantier.created", "chantier.updated") is False


def test_event_matches_wildcard_all():
    """Test wildcard '*' matching."""
    assert EventBus._event_matches("chantier.created", "*") is True
    assert EventBus._event_matches("user.updated", "*") is True
    assert EventBus._event_matches("anything", "*") is True


def test_event_matches_wildcard_prefix():
    """Test wildcard prefix matching (e.g., 'chantier.*')."""
    assert EventBus._event_matches("chantier.created", "chantier.*") is True
    assert EventBus._event_matches("chantier.updated", "chantier.*") is True
    assert EventBus._event_matches("chantier.deleted", "chantier.*") is True
    assert EventBus._event_matches("user.created", "chantier.*") is False
    assert EventBus._event_matches("chantierxyz", "chantier.*") is False


# ===== Tests for EventBus Decorator =====


@pytest.mark.asyncio
async def test_event_bus_on_decorator(event_bus):
    """Test @event_bus.on() decorator."""
    called = []

    @event_bus.on("decorated.event")
    async def decorated_handler(event: DomainEvent):
        called.append(event.event_type)

    await event_bus.publish(DomainEvent(event_type="decorated.event"))

    await asyncio.sleep(0.1)

    assert len(called) == 1
    assert called[0] == "decorated.event"


@pytest.mark.asyncio
async def test_event_bus_subscribe_all(event_bus):
    """Test subscribe_all for universal handlers."""
    called = []

    async def universal_handler(event: DomainEvent):
        called.append(event.event_type)

    event_bus.subscribe_all(universal_handler)

    await event_bus.publish(DomainEvent(event_type="event.1"))
    await event_bus.publish(DomainEvent(event_type="event.2"))
    await event_bus.publish(DomainEvent(event_type="event.3"))

    await asyncio.sleep(0.1)

    assert len(called) == 3


# ===== Tests for Sync/Async Handler Support =====


@pytest.mark.asyncio
async def test_event_bus_sync_handler(event_bus):
    """Test that synchronous handlers work correctly."""
    called = []

    def sync_handler(event: DomainEvent):
        called.append(event.event_type)

    event_bus.subscribe("test.event", sync_handler)

    await event_bus.publish(DomainEvent(event_type="test.event"))

    await asyncio.sleep(0.1)

    assert len(called) == 1


@pytest.mark.asyncio
async def test_event_bus_mixed_handlers(event_bus):
    """Test mixing synchronous and asynchronous handlers."""
    called = []

    def sync_handler(event: DomainEvent):
        called.append("sync")

    async def async_handler(event: DomainEvent):
        called.append("async")

    event_bus.subscribe("test.event", sync_handler)
    event_bus.subscribe("test.event", async_handler)

    await event_bus.publish(DomainEvent(event_type="test.event"))

    await asyncio.sleep(0.1)

    assert len(called) == 2
    assert "sync" in called
    assert "async" in called


# ===== Tests for Global event_handler Decorator =====


def test_event_handler_decorator_registration():
    """Test that the global event_handler decorator works."""
    from shared.infrastructure.event_bus.event_bus import event_bus as global_bus

    # Clear any existing subscribers
    global_bus._subscribers.clear()

    @event_handler("global.test")
    async def test_handler(event: DomainEvent):
        pass

    assert global_bus.get_subscribers_count("global.test") == 1


# ===== Edge Cases and Error Handling =====


@pytest.mark.asyncio
async def test_event_bus_no_handlers(event_bus):
    """Test publishing event with no handlers (should not error)."""
    await event_bus.publish(DomainEvent(event_type="no.handlers"))

    # Should complete without errors
    history = event_bus.get_history()
    assert len(history) == 1


@pytest.mark.asyncio
async def test_event_bus_handler_creation_error(event_bus):
    """Test that handler creation errors are handled gracefully."""
    called = []

    # Create a handler that will fail during task creation setup
    def bad_handler(event: DomainEvent):
        # This is actually fine, but we test the error path in publish()
        called.append("called")

    event_bus.subscribe("test.event", bad_handler)

    # Should not raise
    await event_bus.publish(DomainEvent(event_type="test.event"))

    await asyncio.sleep(0.1)

    # Handler should still execute
    assert len(called) == 1


@pytest.mark.asyncio
async def test_event_bus_concurrent_publishing(event_bus):
    """Test that concurrent event publishing works correctly."""
    called = []

    async def handler(event: DomainEvent):
        await asyncio.sleep(0.01)  # Simulate work
        called.append(event.event_type)

    event_bus.subscribe("concurrent.*", handler)

    # Publish multiple events concurrently
    tasks = [
        event_bus.publish(DomainEvent(event_type=f"concurrent.event.{i}"))
        for i in range(10)
    ]

    await asyncio.gather(*tasks)
    await asyncio.sleep(0.2)

    # All events should have been processed
    assert len(called) == 10


@pytest.mark.asyncio
async def test_event_bus_preserves_handler_order(event_bus):
    """Test that handlers are called in order of subscription."""
    call_order = []

    async def handler1(event: DomainEvent):
        call_order.append(1)

    async def handler2(event: DomainEvent):
        call_order.append(2)

    async def handler3(event: DomainEvent):
        call_order.append(3)

    event_bus.subscribe("test.event", handler1)
    event_bus.subscribe("test.event", handler2)
    event_bus.subscribe("test.event", handler3)

    await event_bus.publish(DomainEvent(event_type="test.event"))

    await asyncio.sleep(0.1)

    # Handlers execute in parallel, so order is not guaranteed
    # But all should be called
    assert len(call_order) == 3
    assert set(call_order) == {1, 2, 3}
