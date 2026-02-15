"""Interface EscaladeRepository - Persistance de l'historique des escalades (SIG-17)."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import EscaladeHistorique


class EscaladeRepository(ABC):
    """
    Interface abstraite pour la persistance des escalades.

    Utilisée pour enregistrer l'historique des escalades de signalements.
    """

    @abstractmethod
    def save(self, escalade: EscaladeHistorique) -> EscaladeHistorique:
        """Persiste une escalade."""
        pass

    @abstractmethod
    def find_by_signalement(
        self,
        signalement_id: int,
    ) -> List[EscaladeHistorique]:
        """Récupère l'historique des escalades d'un signalement."""
        pass

    @abstractmethod
    def find_last_by_signalement(
        self,
        signalement_id: int,
    ) -> Optional[EscaladeHistorique]:
        """Récupère la dernière escalade d'un signalement."""
        pass

    @abstractmethod
    def count_by_signalement(self, signalement_id: int) -> int:
        """Compte le nombre d'escalades d'un signalement."""
        pass
