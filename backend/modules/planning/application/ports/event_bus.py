"""Interface EventBus - Port pour la publication d'evenements."""

from abc import ABC, abstractmethod
from typing import Any, List


class EventBus(ABC):
    """
    Interface abstraite pour la publication d'evenements de domaine.

    L'implementation concrete se trouve dans la couche Infrastructure.
    Permet la communication asynchrone entre modules sans couplage direct.

    Note:
        L'Application ne connait pas l'implementation concrete (Redis, etc.).

    Example:
        >>> event_bus.publish(AffectationCreatedEvent(affectation_id=1, ...))
    """

    @abstractmethod
    def publish(self, event: Any) -> None:
        """
        Publie un evenement de domaine.

        L'evenement sera distribue a tous les handlers abonnes.

        Args:
            event: L'evenement a publier (Domain Event).

        Example:
            >>> event_bus.publish(AffectationCreatedEvent(
            ...     affectation_id=1,
            ...     utilisateur_id=2,
            ...     chantier_id=3,
            ... ))
        """
        pass

    @abstractmethod
    def publish_many(self, events: List[Any]) -> None:
        """
        Publie plusieurs evenements de domaine.

        Utile pour les operations en masse (ex: duplication).

        Args:
            events: Liste d'evenements a publier.

        Example:
            >>> event_bus.publish_many([event1, event2, event3])
        """
        pass


class NullEventBus(EventBus):
    """
    Implementation nulle de l'EventBus.

    Utilise pour les tests ou quand la publication d'evenements
    n'est pas necessaire. Ne fait rien.

    Example:
        >>> bus = NullEventBus()
        >>> bus.publish(some_event)  # Ne fait rien
    """

    def publish(self, event: Any) -> None:
        """Ne publie rien (implementation nulle)."""
        pass

    def publish_many(self, events: List[Any]) -> None:
        """Ne publie rien (implementation nulle)."""
        pass
