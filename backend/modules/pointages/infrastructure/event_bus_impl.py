"""Implémentation de l'EventBus pour le module pointages."""

import logging
from typing import Any, List, Optional

from ..application.ports import EventBus

logger = logging.getLogger(__name__)


class EventBusImpl(EventBus):
    """
    Implémentation de l'EventBus qui délègue au bus partagé.

    Permet la communication inter-modules via des événements de domaine.
    """

    def __init__(self, core_event_bus: Optional[type] = None):
        """
        Initialise l'implémentation.

        Args:
            core_event_bus: Le bus d'événements partagé (optionnel).
        """
        self._bus = core_event_bus

    def publish(self, event: Any) -> None:
        """
        Publie un événement de domaine.

        Args:
            event: L'événement à publier.
        """
        logger.debug(f"Publishing event: {type(event).__name__}")
        if self._bus:
            self._bus.publish(event)

    def publish_many(self, events: List[Any]) -> None:
        """
        Publie plusieurs événements.

        Args:
            events: Liste des événements à publier.
        """
        for event in events:
            self.publish(event)


def get_event_bus() -> EventBusImpl:
    """
    Factory pour créer l'EventBus.

    Tente d'utiliser le bus partagé s'il est disponible.

    Returns:
        Une instance d'EventBusImpl.
    """
    try:
        from shared.infrastructure.event_bus import EventBus as CoreEventBus
        return EventBusImpl(CoreEventBus)
    except ImportError:
        logger.warning("Core EventBus not available, using standalone mode")
        return EventBusImpl(None)
