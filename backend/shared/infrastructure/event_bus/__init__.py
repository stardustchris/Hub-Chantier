"""Event Bus - Architecture événementielle pour Hub Chantier."""

from .domain_event import DomainEvent
from .event_bus import EventBus as EventBusImpl, event_bus
from .dependencies import get_event_bus

from typing import Callable, Dict, List, Type
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class EventBus:
    """
    Interface statique class-level pour le bus d'événements.

    API synchrone utilisée par le code applicatif et les tests unitaires.
    Subscribe par type de classe d'événement (pas par string).

    API:
        EventBus.subscribe(EventType, handler)
        EventBus.unsubscribe(EventType, handler)
        EventBus.publish(event)
        EventBus.clear()
        EventBus.enable() / EventBus.disable()
    """

    # Subscribers par type d'événement (class -> list[handler])
    _subscribers: Dict[Type, List[Callable]] = defaultdict(list)

    # Activation/désactivation globale
    _enabled: bool = True

    @classmethod
    def subscribe(cls, event_type: Type, handler: Callable) -> None:
        """Enregistre un handler pour un type d'événement.

        Déduplique : un handler n'est ajouté qu'une seule fois par type.

        Args:
            event_type: Classe de l'événement.
            handler: Fonction à appeler (synchrone).
        """
        if handler not in cls._subscribers[event_type]:
            cls._subscribers[event_type].append(handler)

    @classmethod
    def unsubscribe(cls, event_type: Type, handler: Callable) -> None:
        """Retire un handler pour un type d'événement.

        Ne lève pas d'erreur si le handler n'est pas trouvé.

        Args:
            event_type: Classe de l'événement.
            handler: Handler à retirer.
        """
        handlers = cls._subscribers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    @classmethod
    def publish(cls, event) -> None:
        """Publie un événement à tous les subscribers du type correspondant.

        Exécution synchrone. Si un handler lève une exception, les autres
        continuent d'être appelés. L'erreur est loguée.

        Args:
            event: Instance de l'événement à publier.
        """
        if not cls._enabled:
            return

        event_type = type(event)
        handlers = cls._subscribers.get(event_type, [])

        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                handler_name = getattr(handler, '__name__', repr(handler))
                logger.error(
                    f"Error in handler {handler_name} for {event_type.__name__}: {e}",
                    exc_info=True,
                )

    @classmethod
    def clear(cls) -> None:
        """Supprime tous les subscribers. Utile pour l'isolation des tests."""
        cls._subscribers.clear()

    @classmethod
    def enable(cls) -> None:
        """Active la publication d'événements."""
        cls._enabled = True

    @classmethod
    def disable(cls) -> None:
        """Désactive la publication d'événements (utile pour les tests)."""
        cls._enabled = False


def event_handler(event_type: Type):
    """Décorateur pour enregistrer un handler via EventBus.subscribe.

    Args:
        event_type: Classe de l'événement.

    Returns:
        Le décorateur.

    Example:
        >>> @event_handler(ChantierCreated)
        >>> def handle_creation(event):
        ...     pass
    """
    def decorator(func: Callable):
        EventBus.subscribe(event_type, func)
        return func
    return decorator


__all__ = [
    'DomainEvent',
    'EventBus',
    'event_bus',
    'EventBusImpl',
    'event_handler',
    'get_event_bus',
]
