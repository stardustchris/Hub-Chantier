"""Interface RelanceDevisRepository - Abstraction pour la persistence des relances.

DEV-24: Relances automatiques de devis.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from ..entities.relance_devis import RelanceDevis


class RelanceDevisRepository(ABC):
    """Interface abstraite pour la persistence des relances de devis.

    Note:
        Le Domain ne connait pas l'implementation.
        L'infrastructure fournit l'implementation concrete (SQLAlchemy).
    """

    @abstractmethod
    def find_by_id(self, relance_id: int) -> Optional[RelanceDevis]:
        """Trouve une relance par son ID.

        Args:
            relance_id: L'ID de la relance.

        Returns:
            La relance ou None si non trouvee.
        """
        pass

    @abstractmethod
    def find_by_devis_id(self, devis_id: int) -> List[RelanceDevis]:
        """Trouve toutes les relances d'un devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            Liste des relances triees par numero_relance.
        """
        pass

    @abstractmethod
    def find_planifiees_avant(self, date_limite: datetime) -> List[RelanceDevis]:
        """Trouve les relances planifiees dont la date prevue est arrivee.

        Utilise par le batch job ExecuterRelancesUseCase.

        Args:
            date_limite: Date limite (incluse).

        Returns:
            Liste des relances planifiees a envoyer.
        """
        pass

    @abstractmethod
    def find_planifiees_by_devis_id(self, devis_id: int) -> List[RelanceDevis]:
        """Trouve les relances planifiees (non envoyees, non annulees) d'un devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            Liste des relances en attente.
        """
        pass

    @abstractmethod
    def save(self, relance: RelanceDevis) -> RelanceDevis:
        """Persiste une relance (creation ou mise a jour).

        Args:
            relance: La relance a persister.

        Returns:
            La relance avec son ID attribue.
        """
        pass

    @abstractmethod
    def save_batch(self, relances: List[RelanceDevis]) -> List[RelanceDevis]:
        """Persiste plusieurs relances en batch.

        Args:
            relances: Les relances a persister.

        Returns:
            Les relances avec leurs IDs attribues.
        """
        pass

    @abstractmethod
    def delete(self, relance_id: int) -> bool:
        """Supprime une relance.

        Args:
            relance_id: L'ID de la relance a supprimer.

        Returns:
            True si supprimee, False si non trouvee.
        """
        pass
