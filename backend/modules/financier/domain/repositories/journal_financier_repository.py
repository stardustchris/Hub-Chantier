"""Interface du repository pour le journal financier.

Traçabilité des opérations financières (audit trail).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class JournalEntry:
    """Entrée du journal financier (audit trail).

    Enregistre chaque opération financière pour traçabilité.
    """

    id: Optional[int] = None
    entite_type: str = ""
    entite_id: int = 0
    chantier_id: Optional[int] = None
    action: str = ""
    details: Optional[str] = None
    auteur_id: int = 0
    created_at: Optional[datetime] = None


class JournalFinancierRepository(ABC):
    """Interface abstraite pour la persistence du journal financier."""

    @abstractmethod
    def save(self, entry: JournalEntry) -> JournalEntry:
        """Persiste une entrée du journal.

        Args:
            entry: L'entrée à persister.

        Returns:
            L'entrée avec son ID attribué.
        """
        pass

    @abstractmethod
    def find_by_entite(
        self,
        entite_type: str,
        entite_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[JournalEntry]:
        """Liste les entrées du journal pour une entité.

        Args:
            entite_type: Type de l'entité (fournisseur, budget, achat, etc.).
            entite_id: ID de l'entité.
            limit: Nombre maximum de résultats.
            offset: Décalage pour pagination.

        Returns:
            Liste des entrées du journal.
        """
        pass

    @abstractmethod
    def find_by_auteur(
        self,
        auteur_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[JournalEntry]:
        """Liste les entrées du journal d'un auteur.

        Args:
            auteur_id: ID de l'auteur.
            limit: Nombre maximum de résultats.
            offset: Décalage pour pagination.

        Returns:
            Liste des entrées du journal.
        """
        pass

    @abstractmethod
    def find_by_chantier(
        self,
        chantier_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[JournalEntry]:
        """Liste les entrées du journal d'un chantier.

        Args:
            chantier_id: ID du chantier.
            limit: Nombre maximum de résultats.
            offset: Décalage pour pagination.

        Returns:
            Liste des entrées du journal.
        """
        pass

    @abstractmethod
    def count_by_entite(self, entite_type: str, entite_id: int) -> int:
        """Compte les entrées du journal pour une entité.

        Args:
            entite_type: Type de l'entité.
            entite_id: ID de l'entité.

        Returns:
            Le nombre d'entrées.
        """
        pass
