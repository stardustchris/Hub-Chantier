"""Interface EventBus - Port pour la publication d'événements."""

from abc import ABC, abstractmethod
from typing import Any, List


class EventBus(ABC):
    """Interface abstraite pour la publication d'événements de domaine."""

    @abstractmethod
    def publish(self, event: Any) -> None:
        """Publie un événement de domaine."""
        pass

    @abstractmethod
    def publish_many(self, events: List[Any]) -> None:
        """Publie plusieurs événements de domaine."""
        pass


class NoOpEventBus(EventBus):
    """Implémentation nulle de l'EventBus pour les tests."""

    def publish(self, event: Any) -> None:
        """Ne publie rien."""
        pass

    def publish_many(self, events: List[Any]) -> None:
        """Ne publie rien."""
        pass
