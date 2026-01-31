"""Interfaces des repositories pour les situations de travaux.

FIN-07: Situations de travaux - CRUD et workflow.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.situation_travaux import SituationTravaux
from ..entities.ligne_situation import LigneSituation


class SituationRepository(ABC):
    """Interface abstraite pour la persistence des situations de travaux."""

    @abstractmethod
    def save(self, situation: SituationTravaux) -> SituationTravaux:
        """Persiste une situation (creation ou mise a jour).

        Args:
            situation: La situation a persister.

        Returns:
            La situation avec son ID attribue.
        """
        pass

    @abstractmethod
    def find_by_id(self, situation_id: int) -> Optional[SituationTravaux]:
        """Recherche une situation par son ID (exclut les supprimes).

        Args:
            situation_id: L'ID de la situation.

        Returns:
            La situation ou None si non trouvee.
        """
        pass

    @abstractmethod
    def find_by_chantier_id(
        self, chantier_id: int, include_deleted: bool = False
    ) -> List[SituationTravaux]:
        """Liste les situations d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            include_deleted: Inclure les situations supprimees.

        Returns:
            Liste des situations du chantier.
        """
        pass

    @abstractmethod
    def count_by_chantier_id(self, chantier_id: int) -> int:
        """Compte le nombre de situations pour un chantier (non supprimees).

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Le nombre de situations.
        """
        pass

    @abstractmethod
    def delete(self, situation_id: int, deleted_by: int) -> None:
        """Supprime une situation (soft delete - H10).

        Args:
            situation_id: L'ID de la situation a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.
        """
        pass

    @abstractmethod
    def find_derniere_situation(
        self, chantier_id: int
    ) -> Optional[SituationTravaux]:
        """Recherche la derniere situation d'un chantier (non supprimee).

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            La derniere situation ou None si aucune.
        """
        pass


class LigneSituationRepository(ABC):
    """Interface abstraite pour la persistence des lignes de situation."""

    @abstractmethod
    def save(self, ligne: LigneSituation) -> LigneSituation:
        """Persiste une ligne de situation (creation ou mise a jour).

        Args:
            ligne: La ligne a persister.

        Returns:
            La ligne avec son ID attribue.
        """
        pass

    @abstractmethod
    def save_all(self, lignes: List[LigneSituation]) -> List[LigneSituation]:
        """Persiste plusieurs lignes de situation.

        Args:
            lignes: Les lignes a persister.

        Returns:
            Les lignes avec leurs IDs attribues.
        """
        pass

    @abstractmethod
    def find_by_situation_id(
        self, situation_id: int
    ) -> List[LigneSituation]:
        """Liste les lignes d'une situation.

        Args:
            situation_id: L'ID de la situation.

        Returns:
            Liste des lignes de la situation.
        """
        pass

    @abstractmethod
    def delete_by_situation_id(self, situation_id: int) -> None:
        """Supprime toutes les lignes d'une situation.

        Args:
            situation_id: L'ID de la situation.
        """
        pass
