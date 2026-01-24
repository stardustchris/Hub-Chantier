"""Interface VariablePaieRepository - Abstraction pour la persistence des variables de paie."""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date

from ..entities import VariablePaie
from ..value_objects import TypeVariablePaie


class VariablePaieRepository(ABC):
    """
    Interface abstraite pour la persistence des variables de paie.

    Cette interface définit le contrat pour l'accès aux données des variables de paie.
    L'implémentation concrète se trouve dans la couche Infrastructure.
    """

    @abstractmethod
    def find_by_id(self, variable_id: int) -> Optional[VariablePaie]:
        """
        Trouve une variable de paie par son ID.

        Args:
            variable_id: L'identifiant unique de la variable.

        Returns:
            La variable trouvée ou None.
        """
        pass

    @abstractmethod
    def save(self, variable: VariablePaie) -> VariablePaie:
        """
        Persiste une variable de paie (création ou mise à jour).

        Args:
            variable: La variable à sauvegarder.

        Returns:
            La variable sauvegardée (avec ID si création).
        """
        pass

    @abstractmethod
    def delete(self, variable_id: int) -> bool:
        """
        Supprime une variable de paie.

        Args:
            variable_id: L'identifiant de la variable à supprimer.

        Returns:
            True si supprimée, False si non trouvée.
        """
        pass

    @abstractmethod
    def find_by_pointage(self, pointage_id: int) -> List[VariablePaie]:
        """
        Trouve toutes les variables de paie d'un pointage.

        Args:
            pointage_id: ID du pointage.

        Returns:
            Liste des variables.
        """
        pass

    @abstractmethod
    def find_by_type_and_periode(
        self,
        type_variable: TypeVariablePaie,
        date_debut: date,
        date_fin: date,
        utilisateur_id: Optional[int] = None,
    ) -> List[VariablePaie]:
        """
        Trouve les variables d'un type sur une période.

        Args:
            type_variable: Le type de variable.
            date_debut: Date de début.
            date_fin: Date de fin.
            utilisateur_id: Filtrer par utilisateur (optionnel).

        Returns:
            Liste des variables.
        """
        pass

    @abstractmethod
    def find_by_utilisateur_and_periode(
        self,
        utilisateur_id: int,
        date_debut: date,
        date_fin: date,
    ) -> List[VariablePaie]:
        """
        Trouve toutes les variables d'un utilisateur sur une période.

        Args:
            utilisateur_id: ID de l'utilisateur.
            date_debut: Date de début.
            date_fin: Date de fin.

        Returns:
            Liste des variables.
        """
        pass

    @abstractmethod
    def bulk_save(self, variables: List[VariablePaie]) -> List[VariablePaie]:
        """
        Sauvegarde plusieurs variables en une seule transaction.

        Args:
            variables: Liste des variables à sauvegarder.

        Returns:
            Liste des variables sauvegardées.
        """
        pass

    @abstractmethod
    def delete_by_pointage(self, pointage_id: int) -> int:
        """
        Supprime toutes les variables d'un pointage.

        Args:
            pointage_id: ID du pointage.

        Returns:
            Nombre de variables supprimées.
        """
        pass
