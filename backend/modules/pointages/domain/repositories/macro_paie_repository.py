"""Interface MacroPaieRepository - Persistance des macros de paie (FDH-18)."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import MacroPaie
from ..entities.macro_paie import TypeMacroPaie


class MacroPaieRepository(ABC):
    """
    Interface abstraite pour la persistance des macros de paie.

    Les macros de paie sont des formules de calcul paramétrables
    appliquées automatiquement sur les feuilles d'heures.
    """

    @abstractmethod
    def find_by_id(self, macro_id: int) -> Optional[MacroPaie]:
        """Trouve une macro par son ID."""
        pass

    @abstractmethod
    def save(self, macro: MacroPaie) -> MacroPaie:
        """Persiste une macro (création ou mise à jour)."""
        pass

    @abstractmethod
    def delete(self, macro_id: int) -> bool:
        """Supprime une macro."""
        pass

    @abstractmethod
    def find_all(
        self,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[MacroPaie]:
        """Récupère toutes les macros."""
        pass

    @abstractmethod
    def find_by_type(
        self,
        type_macro: TypeMacroPaie,
        active_only: bool = True,
    ) -> List[MacroPaie]:
        """Récupère les macros d'un type donné."""
        pass

    @abstractmethod
    def count(self, active_only: bool = True) -> int:
        """Compte le nombre de macros."""
        pass
