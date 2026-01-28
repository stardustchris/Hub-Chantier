"""Shared test fixtures for infrastructure tests."""

import pytest
from unittest.mock import Mock, AsyncMock
from sqlalchemy.orm import Session

from shared.infrastructure.event_bus.event_bus import EventBus
from shared.infrastructure.event_bus.domain_event import DomainEvent


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = Mock(spec=Session)
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.query = Mock(return_value=session)
    session.filter = Mock(return_value=session)
    session.filter_by = Mock(return_value=session)
    session.first = Mock(return_value=None)
    session.all = Mock(return_value=[])
    session.scalar = Mock(return_value=None)
    session.close = Mock()
    return session


@pytest.fixture
def event_bus_spy():
    """Create an EventBus with spying capabilities."""
    bus = EventBus()
    bus.published_events = []

    original_publish = bus.publish

    async def spy_publish(event: DomainEvent):
        bus.published_events.append(event)
        await original_publish(event)

    bus.publish = spy_publish
    return bus


@pytest.fixture
def mock_event_bus():
    """Create a mock EventBus for testing."""
    mock_bus = Mock()
    mock_bus.publish = AsyncMock()
    mock_bus.published_events = []

    async def track_publish(event):
        mock_bus.published_events.append(event)

    mock_bus.publish.side_effect = track_publish
    return mock_bus
