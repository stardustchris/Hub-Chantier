"""Interface du repository pour le journal de devis.

DEV-18: Historique modifications - CRUD du journal d'audit.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from ..entities import JournalDevis


class JournalDevisRepository(ABC):
    """Interface abstraite pour la persistence du journal de devis.

    Table append-only : seules les operations de creation et lecture
    sont supportees.
    """

    @abstractmethod
    def save(self, entry: JournalDevis) -> JournalDevis:
        """Persiste une entree de journal (creation uniquement).

        Args:
            entry: L'entree de journal a persister.

        Returns:
            L'entree avec son ID attribue.
        """
        pass

    @abstractmethod
    def find_by_devis(
        self,
        devis_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[JournalDevis]:
        """Liste les entrees de journal d'un devis.

        Args:
            devis_id: L'ID du devis.
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des entrees ordonnee par date decroissante.
        """
        pass

    @abstractmethod
    def find_by_auteur(
        self,
        auteur_id: int,
        date_min: Optional[date] = None,
        date_max: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[JournalDevis]:
        """Liste les entrees de journal d'un auteur.

        Args:
            auteur_id: L'ID de l'auteur.
            date_min: Date minimale (optionnel).
            date_max: Date maximale (optionnel).
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des entrees ordonnee par date decroissante.
        """
        pass

    @abstractmethod
    def count_by_devis(self, devis_id: int) -> int:
        """Compte le nombre d'entrees de journal d'un devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            Le nombre d'entrees.
        """
        pass
