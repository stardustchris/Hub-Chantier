"""Interface EventBus pour publier les evenements domaine."""

from abc import ABC, abstractmethod
from typing import Any


class EventBus(ABC):
    """
    Interface abstraite pour le bus d'evenements.

    Permet de decouple le domaine de l'infrastructure de messaging.
    """

    @abstractmethod
    def publish(self, event: Any) -> None:
        """
        Publie un evenement domaine.

        Args:
            event: L'evenement a publier.
        """
        pass
