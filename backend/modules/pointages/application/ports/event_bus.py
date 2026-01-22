"""Port EventBus - Interface pour la publication d'événements."""

from abc import ABC, abstractmethod
from typing import Any, List


class EventBus(ABC):
    """
    Interface abstraite pour la publication d'événements de domaine.

    Permet le découplage entre les modules via des événements.
    L'implémentation concrète se trouve dans la couche Infrastructure.
    """

    @abstractmethod
    def publish(self, event: Any) -> None:
        """
        Publie un événement de domaine.

        Args:
            event: L'événement à publier.
        """
        pass

    @abstractmethod
    def publish_many(self, events: List[Any]) -> None:
        """
        Publie plusieurs événements.

        Args:
            events: Liste des événements à publier.
        """
        pass


class NullEventBus(EventBus):
    """
    Implémentation No-Op pour les tests.

    Ne publie rien, utile pour les tests unitaires.
    """

    def publish(self, event: Any) -> None:
        """Ne fait rien."""
        pass

    def publish_many(self, events: List[Any]) -> None:
        """Ne fait rien."""
        pass
