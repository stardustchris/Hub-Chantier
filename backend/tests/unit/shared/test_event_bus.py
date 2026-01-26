"""Tests unitaires pour EventBus."""

import pytest
from unittest.mock import Mock, patch
import logging

from shared.infrastructure.event_bus import EventBus, event_handler


class MockEvent:
    """Evenement mock pour les tests."""
    def __init__(self, data: str = "test"):
        self.data = data


class AnotherMockEvent:
    """Autre evenement mock."""
    def __init__(self, value: int = 0):
        self.value = value


class TestEventBusSubscribe:
    """Tests de subscribe."""

    def setup_method(self):
        """Reset EventBus avant chaque test."""
        EventBus.clear()
        EventBus.enable()

    def test_subscribe_adds_handler(self):
        """Test que subscribe ajoute un handler."""
        def handler(event): pass

        EventBus.subscribe(MockEvent, handler)

        assert handler in EventBus._subscribers[MockEvent]

    def test_subscribe_creates_list_for_new_event_type(self):
        """Test creation de liste pour nouveau type."""
        def handler(event): pass

        EventBus.subscribe(MockEvent, handler)

        assert MockEvent in EventBus._subscribers
        assert len(EventBus._subscribers[MockEvent]) == 1

    def test_subscribe_same_handler_twice_only_adds_once(self):
        """Test qu'un handler n'est ajoute qu'une fois."""
        def handler(event): pass

        EventBus.subscribe(MockEvent, handler)
        EventBus.subscribe(MockEvent, handler)

        assert EventBus._subscribers[MockEvent].count(handler) == 1

    def test_subscribe_multiple_handlers(self):
        """Test abonnement de plusieurs handlers."""
        def handler1(event): pass
        def handler2(event): pass

        EventBus.subscribe(MockEvent, handler1)
        EventBus.subscribe(MockEvent, handler2)

        assert len(EventBus._subscribers[MockEvent]) == 2


class TestEventBusUnsubscribe:
    """Tests de unsubscribe."""

    def setup_method(self):
        EventBus.clear()
        EventBus.enable()

    def test_unsubscribe_removes_handler(self):
        """Test que unsubscribe retire le handler."""
        def handler(event): pass
        EventBus.subscribe(MockEvent, handler)

        EventBus.unsubscribe(MockEvent, handler)

        assert handler not in EventBus._subscribers.get(MockEvent, [])

    def test_unsubscribe_nonexistent_handler_does_nothing(self):
        """Test unsubscribe d'un handler non abonne."""
        def handler(event): pass

        # Ne doit pas lever d'exception
        EventBus.unsubscribe(MockEvent, handler)

    def test_unsubscribe_nonexistent_event_type_does_nothing(self):
        """Test unsubscribe d'un type non enregistre."""
        def handler(event): pass

        # Ne doit pas lever d'exception
        EventBus.unsubscribe(MockEvent, handler)


class TestEventBusPublish:
    """Tests de publish."""

    def setup_method(self):
        EventBus.clear()
        EventBus.enable()

    def test_publish_calls_handler(self):
        """Test que publish appelle le handler."""
        results = []
        def handler(event):
            results.append(event)
        EventBus.subscribe(MockEvent, handler)

        event = MockEvent(data="test_data")
        EventBus.publish(event)

        assert len(results) == 1
        assert results[0] is event

    def test_publish_calls_all_handlers(self):
        """Test que publish appelle tous les handlers."""
        results1 = []
        results2 = []
        def handler1(event): results1.append(event)
        def handler2(event): results2.append(event)
        EventBus.subscribe(MockEvent, handler1)
        EventBus.subscribe(MockEvent, handler2)

        event = MockEvent()
        EventBus.publish(event)

        assert len(results1) == 1
        assert len(results2) == 1

    def test_publish_only_calls_matching_event_type_handlers(self):
        """Test que publish n'appelle que les handlers du bon type."""
        mock_results = []
        another_results = []
        def mock_handler(event): mock_results.append(event)
        def another_handler(event): another_results.append(event)
        EventBus.subscribe(MockEvent, mock_handler)
        EventBus.subscribe(AnotherMockEvent, another_handler)

        EventBus.publish(MockEvent())

        assert len(mock_results) == 1
        assert len(another_results) == 0

    def test_publish_does_nothing_if_disabled(self):
        """Test que publish ne fait rien si desactive."""
        results = []
        def handler(event): results.append(event)
        EventBus.subscribe(MockEvent, handler)
        EventBus.disable()

        EventBus.publish(MockEvent())

        assert len(results) == 0

    def test_publish_works_again_after_enable(self):
        """Test que publish fonctionne apres enable."""
        results = []
        def handler(event): results.append(event)
        EventBus.subscribe(MockEvent, handler)
        EventBus.disable()
        EventBus.enable()

        EventBus.publish(MockEvent())

        assert len(results) == 1

    def test_publish_continues_after_handler_error(self, caplog):
        """Test que publish continue apres erreur dans un handler."""
        def failing_handler(event):
            raise Exception("Handler error")
        results = []
        def succeeding_handler(event): results.append(event)
        EventBus.subscribe(MockEvent, failing_handler)
        EventBus.subscribe(MockEvent, succeeding_handler)

        with caplog.at_level(logging.ERROR):
            EventBus.publish(MockEvent())

        # Le second handler doit quand meme etre appele
        assert len(results) == 1
        # L'erreur doit etre logguee
        assert "Error in handler" in caplog.text

    def test_publish_with_no_subscribers(self):
        """Test publish sans abonnes."""
        # Ne doit pas lever d'exception
        EventBus.publish(MockEvent())


class TestEventBusClear:
    """Tests de clear."""

    def setup_method(self):
        EventBus.clear()
        EventBus.enable()

    def test_clear_removes_all_subscribers(self):
        """Test que clear retire tous les abonnes."""
        def handler1(event): pass
        def handler2(event): pass
        EventBus.subscribe(MockEvent, handler1)
        EventBus.subscribe(AnotherMockEvent, handler2)

        EventBus.clear()

        assert len(EventBus._subscribers) == 0


class TestEventBusEnableDisable:
    """Tests de enable/disable."""

    def setup_method(self):
        EventBus.clear()
        EventBus.enable()

    def test_disable_sets_enabled_false(self):
        """Test que disable met _enabled a False."""
        EventBus.disable()
        assert EventBus._enabled is False

    def test_enable_sets_enabled_true(self):
        """Test que enable met _enabled a True."""
        EventBus.disable()
        EventBus.enable()
        assert EventBus._enabled is True


class TestEventHandlerDecorator:
    """Tests du decorateur event_handler."""

    def setup_method(self):
        EventBus.clear()
        EventBus.enable()

    def test_decorator_subscribes_handler(self):
        """Test que le decorateur abonne le handler."""
        @event_handler(MockEvent)
        def my_handler(event):
            pass

        assert my_handler in EventBus._subscribers[MockEvent]

    def test_decorator_returns_original_function(self):
        """Test que le decorateur retourne la fonction originale."""
        def original_handler(event):
            return "result"

        decorated = event_handler(MockEvent)(original_handler)

        assert decorated is original_handler
        assert decorated(Mock()) == "result"

    def test_decorated_handler_is_called_on_publish(self):
        """Test que le handler decore est appele a la publication."""
        results = []

        @event_handler(MockEvent)
        def capture_handler(event):
            results.append(event.data)

        EventBus.publish(MockEvent(data="captured"))

        assert results == ["captured"]


class TestEventBusIsolation:
    """Tests d'isolation des types d'evenements."""

    def setup_method(self):
        EventBus.clear()
        EventBus.enable()

    def test_handlers_are_isolated_by_event_type(self):
        """Test que les handlers sont isoles par type."""
        mock_results = []
        another_results = []

        @event_handler(MockEvent)
        def mock_handler(event):
            mock_results.append(event.data)

        @event_handler(AnotherMockEvent)
        def another_handler(event):
            another_results.append(event.value)

        EventBus.publish(MockEvent(data="mock"))
        EventBus.publish(AnotherMockEvent(value=42))

        assert mock_results == ["mock"]
        assert another_results == [42]
