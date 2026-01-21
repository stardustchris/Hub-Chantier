"""EventBus pour la communication inter-modules."""

from typing import Dict, List, Callable, Type, Any
import logging

logger = logging.getLogger(__name__)


class EventBus:
    """
    Bus d'événements pour la communication découplée entre modules.

    Permet aux modules de publier des événements et de s'y abonner
    sans créer de dépendances directes.

    Usage:
        # Publier un événement
        EventBus.publish(UserCreatedEvent(user_id=1, email="test@test.com"))

        # S'abonner à un événement
        EventBus.subscribe(UserCreatedEvent, handle_user_created)

    Note:
        Cette implémentation est synchrone et in-process.
        Pour une application distribuée, utiliser un message broker.
    """

    _subscribers: Dict[Type, List[Callable]] = {}
    _enabled: bool = True

    @classmethod
    def subscribe(cls, event_type: Type, handler: Callable) -> None:
        """
        Abonne un handler à un type d'événement.

        Args:
            event_type: Le type d'événement à écouter.
            handler: La fonction à appeler quand l'événement est publié.
        """
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []

        if handler not in cls._subscribers[event_type]:
            cls._subscribers[event_type].append(handler)
            logger.debug(f"Handler {handler.__name__} subscribed to {event_type.__name__}")

    @classmethod
    def unsubscribe(cls, event_type: Type, handler: Callable) -> None:
        """
        Désabonne un handler d'un type d'événement.

        Args:
            event_type: Le type d'événement.
            handler: Le handler à retirer.
        """
        if event_type in cls._subscribers and handler in cls._subscribers[event_type]:
            cls._subscribers[event_type].remove(handler)
            logger.debug(f"Handler {handler.__name__} unsubscribed from {event_type.__name__}")

    @classmethod
    def publish(cls, event: Any) -> None:
        """
        Publie un événement à tous les handlers abonnés.

        Args:
            event: L'événement à publier.
        """
        if not cls._enabled:
            return

        event_type = type(event)
        handlers = cls._subscribers.get(event_type, [])

        logger.debug(f"Publishing {event_type.__name__} to {len(handlers)} handlers")

        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    f"Error in handler {handler.__name__} for {event_type.__name__}: {e}"
                )

    @classmethod
    def clear(cls) -> None:
        """Supprime tous les abonnements (utile pour les tests)."""
        cls._subscribers.clear()

    @classmethod
    def disable(cls) -> None:
        """Désactive la publication d'événements."""
        cls._enabled = False

    @classmethod
    def enable(cls) -> None:
        """Active la publication d'événements."""
        cls._enabled = True


def event_handler(event_type: Type):
    """
    Décorateur pour enregistrer un handler d'événement.

    Usage:
        @event_handler(UserCreatedEvent)
        def handle_user_created(event: UserCreatedEvent):
            print(f"User {event.user_id} created")

    Args:
        event_type: Le type d'événement à écouter.

    Returns:
        Le décorateur.
    """
    def decorator(handler: Callable) -> Callable:
        EventBus.subscribe(event_type, handler)
        return handler
    return decorator
