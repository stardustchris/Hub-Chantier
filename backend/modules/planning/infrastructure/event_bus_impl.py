"""Implementation de l'EventBus pour le module planning."""

from typing import Any, List, Optional
import logging

from shared.infrastructure.event_bus import EventBus as CoreEventBus
from ..application.ports.event_bus import EventBus

logger = logging.getLogger(__name__)


class EventBusImpl(EventBus):
    """
    Implementation de l'interface EventBus du module planning.

    Cette implementation delegue au CoreEventBus de l'infrastructure partagee.
    Si aucun bus n'est fourni, les evenements sont simplement logges (mode test).

    Attributes:
        _bus: L'EventBus partage optionnel.

    Example:
        >>> bus = EventBusImpl(CoreEventBus)
        >>> bus.publish(AffectationCreatedEvent(...))
    """

    def __init__(self, core_event_bus: Optional[type] = None):
        """
        Initialise l'EventBusImpl.

        Args:
            core_event_bus: La classe CoreEventBus (optionnelle).
                           Si None, les evenements sont logges mais non publies.
        """
        self._bus = core_event_bus

    def publish(self, event: Any) -> None:
        """
        Publie un evenement de domaine.

        L'evenement sera distribue a tous les handlers abonnes via le CoreEventBus.

        Args:
            event: L'evenement a publier (Domain Event).

        Example:
            >>> event_bus.publish(AffectationCreatedEvent(
            ...     affectation_id=1,
            ...     utilisateur_id=2,
            ...     chantier_id=3,
            ... ))
        """
        event_type = type(event).__name__
        logger.debug(f"Publishing event: {event_type}")

        if self._bus is not None:
            try:
                self._bus.publish(event)
                logger.info(f"Event {event_type} published successfully")
            except Exception as e:
                logger.error(f"Error publishing event {event_type}: {e}")
        else:
            logger.debug(f"Event {event_type} not published (no bus configured)")

    def publish_many(self, events: List[Any]) -> None:
        """
        Publie plusieurs evenements de domaine.

        Utile pour les operations en masse (ex: duplication d'affectations).

        Args:
            events: Liste d'evenements a publier.

        Example:
            >>> event_bus.publish_many([event1, event2, event3])
        """
        logger.debug(f"Publishing {len(events)} events")

        for event in events:
            self.publish(event)

        logger.info(f"Batch of {len(events)} events processed")


class NoOpEventBus(EventBus):
    """
    Implementation nulle de l'EventBus.

    Utilise pour les tests ou quand la publication d'evenements
    n'est pas necessaire. Ne fait rien.

    Example:
        >>> bus = NoOpEventBus()
        >>> bus.publish(some_event)  # Ne fait rien
    """

    def publish(self, event: Any) -> None:
        """Ne publie rien (implementation nulle)."""
        pass

    def publish_many(self, events: List[Any]) -> None:
        """Ne publie rien (implementation nulle)."""
        pass
