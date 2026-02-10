"""Interface du repository pour les factures client.

FIN-08: Facturation client - CRUD et workflow.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.facture_client import FactureClient


class FactureRepository(ABC):
    """Interface abstraite pour la persistence des factures client."""

    @abstractmethod
    def save(self, facture: FactureClient) -> FactureClient:
        """Persiste une facture (creation ou mise a jour).

        Args:
            facture: La facture a persister.

        Returns:
            La facture avec son ID attribue.
        """
        pass

    @abstractmethod
    def find_by_id(self, facture_id: int) -> Optional[FactureClient]:
        """Recherche une facture par son ID (exclut les supprimees).

        Args:
            facture_id: L'ID de la facture.

        Returns:
            La facture ou None si non trouvee.
        """
        pass

    @abstractmethod
    def find_by_chantier_id(
        self, chantier_id: int, include_deleted: bool = False
    ) -> List[FactureClient]:
        """Liste les factures d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            include_deleted: Inclure les factures supprimees.

        Returns:
            Liste des factures du chantier.
        """
        pass

    @abstractmethod
    def find_by_situation_id(
        self, situation_id: int
    ) -> Optional[FactureClient]:
        """Recherche une facture par son ID de situation.

        Args:
            situation_id: L'ID de la situation.

        Returns:
            La facture ou None si non trouvee.
        """
        pass

    @abstractmethod
    def count_factures_year(self, year: int) -> int:
        """Compte le nombre de factures pour une annee (non supprimees).

        Args:
            year: L'annee.

        Returns:
            Le nombre de factures.
        """
        pass

    @abstractmethod
    def next_numero_facture(self, year: int) -> int:
        """Retourne le prochain numero de facture pour l'annee donnee (atomique).

        Cette methode DOIT etre atomique (SELECT FOR UPDATE ou equivalent)
        pour eviter les doublons en cas d'acces concurrent.

        Args:
            year: L'annee pour laquelle generer le numero.

        Returns:
            Le prochain numero sequentiel.
        """
        ...

    @abstractmethod
    def delete(self, facture_id: int, deleted_by: int) -> None:
        """Supprime une facture (soft delete - H10).

        Args:
            facture_id: L'ID de la facture a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.
        """
        pass
