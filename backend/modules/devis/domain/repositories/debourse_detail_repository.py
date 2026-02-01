"""Interface du repository pour les debourses detailles.

DEV-05: Detail debourses avances - CRUD des sous-details par ligne.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional

from ..entities import DebourseDetail
from ..value_objects import TypeDebourse


class DebourseDetailRepository(ABC):
    """Interface abstraite pour la persistence des debourses detailles."""

    @abstractmethod
    def save(self, debourse: DebourseDetail) -> DebourseDetail:
        """Persiste un debourse detaille (creation ou mise a jour).

        Args:
            debourse: Le debourse a persister.

        Returns:
            Le debourse avec son ID attribue.
        """
        pass

    @abstractmethod
    def find_by_id(self, debourse_id: int) -> Optional[DebourseDetail]:
        """Recherche un debourse par son ID.

        Args:
            debourse_id: L'ID du debourse.

        Returns:
            Le debourse ou None si non trouve.
        """
        pass

    @abstractmethod
    def find_by_ligne(self, ligne_devis_id: int) -> List[DebourseDetail]:
        """Liste les debourses d'une ligne de devis.

        Args:
            ligne_devis_id: L'ID de la ligne.

        Returns:
            Liste des debourses.
        """
        pass

    @abstractmethod
    def find_by_ligne_and_type(
        self,
        ligne_devis_id: int,
        type_debourse: TypeDebourse,
    ) -> List[DebourseDetail]:
        """Liste les debourses d'une ligne par type.

        Args:
            ligne_devis_id: L'ID de la ligne.
            type_debourse: Le type de debourse.

        Returns:
            Liste des debourses du type specifie.
        """
        pass

    @abstractmethod
    def somme_by_ligne(self, ligne_devis_id: int) -> Decimal:
        """Calcule la somme des debourses d'une ligne (debourse sec).

        Args:
            ligne_devis_id: L'ID de la ligne.

        Returns:
            La somme des debourses.
        """
        pass

    @abstractmethod
    def somme_by_ligne_and_type(
        self,
        ligne_devis_id: int,
        type_debourse: TypeDebourse,
    ) -> Decimal:
        """Calcule la somme des debourses d'une ligne par type.

        Args:
            ligne_devis_id: L'ID de la ligne.
            type_debourse: Le type de debourse.

        Returns:
            La somme des debourses du type specifie.
        """
        pass

    @abstractmethod
    def delete(self, debourse_id: int) -> bool:
        """Supprime un debourse (suppression physique).

        Args:
            debourse_id: L'ID du debourse a supprimer.

        Returns:
            True si supprime, False si non trouve.
        """
        pass

    @abstractmethod
    def delete_by_ligne(self, ligne_devis_id: int) -> int:
        """Supprime tous les debourses d'une ligne.

        Args:
            ligne_devis_id: L'ID de la ligne.

        Returns:
            Le nombre de debourses supprimes.
        """
        pass
