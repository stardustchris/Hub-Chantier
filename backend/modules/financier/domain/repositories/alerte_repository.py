"""Interface du repository pour les alertes de depassement budgetaire.

FIN-12: Alertes depassements - CRUD et acquittement.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.alerte_depassement import AlerteDepassement


class AlerteRepository(ABC):
    """Interface abstraite pour la persistence des alertes de depassement."""

    @abstractmethod
    def save(self, alerte: AlerteDepassement) -> AlerteDepassement:
        """Persiste une alerte (creation ou mise a jour).

        Args:
            alerte: L'alerte a persister.

        Returns:
            L'alerte avec son ID attribue.
        """
        pass

    @abstractmethod
    def find_by_id(self, alerte_id: int) -> Optional[AlerteDepassement]:
        """Recherche une alerte par son ID.

        Args:
            alerte_id: L'ID de l'alerte.

        Returns:
            L'alerte ou None si non trouvee.
        """
        pass

    @abstractmethod
    def find_by_chantier_id(
        self, chantier_id: int
    ) -> List[AlerteDepassement]:
        """Liste les alertes d'un chantier.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Liste des alertes du chantier.
        """
        pass

    @abstractmethod
    def find_non_acquittees(
        self, chantier_id: int
    ) -> List[AlerteDepassement]:
        """Liste les alertes non acquittees d'un chantier.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Liste des alertes non acquittees.
        """
        pass

    @abstractmethod
    def acquitter(self, alerte_id: int, user_id: int) -> None:
        """Acquitte une alerte.

        Args:
            alerte_id: L'ID de l'alerte a acquitter.
            user_id: L'ID de l'utilisateur qui acquitte.
        """
        pass
