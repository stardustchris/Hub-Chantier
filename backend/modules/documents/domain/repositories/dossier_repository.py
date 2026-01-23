"""Interface DossierRepository - Abstraction pour la persistance des dossiers."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import Dossier
from ..value_objects import DossierType


class DossierRepository(ABC):
    """
    Interface abstraite pour la persistance des dossiers.

    Cette interface définit le contrat pour l'accès aux données dossiers.
    L'implémentation concrète se trouve dans la couche Infrastructure.
    """

    @abstractmethod
    def find_by_id(self, dossier_id: int) -> Optional[Dossier]:
        """
        Trouve un dossier par son ID.

        Args:
            dossier_id: L'identifiant unique du dossier.

        Returns:
            Le dossier trouvé ou None.
        """
        pass

    @abstractmethod
    def save(self, dossier: Dossier) -> Dossier:
        """
        Persiste un dossier (création ou mise à jour).

        Args:
            dossier: Le dossier à sauvegarder.

        Returns:
            Le dossier sauvegardé (avec ID si création).
        """
        pass

    @abstractmethod
    def delete(self, dossier_id: int) -> bool:
        """
        Supprime un dossier.

        Args:
            dossier_id: L'identifiant du dossier à supprimer.

        Returns:
            True si supprimé, False si non trouvé.
        """
        pass

    @abstractmethod
    def find_by_chantier(
        self, chantier_id: int, parent_id: Optional[int] = None
    ) -> List[Dossier]:
        """
        Récupère les dossiers d'un chantier.

        Args:
            chantier_id: ID du chantier.
            parent_id: ID du dossier parent (None pour la racine).

        Returns:
            Liste des dossiers.
        """
        pass

    @abstractmethod
    def find_children(self, dossier_id: int) -> List[Dossier]:
        """
        Récupère les sous-dossiers d'un dossier.

        Args:
            dossier_id: ID du dossier parent.

        Returns:
            Liste des sous-dossiers.
        """
        pass

    @abstractmethod
    def count_by_chantier(self, chantier_id: int) -> int:
        """
        Compte le nombre de dossiers d'un chantier.

        Args:
            chantier_id: ID du chantier.

        Returns:
            Nombre de dossiers.
        """
        pass

    @abstractmethod
    def exists_by_nom_in_parent(
        self, nom: str, chantier_id: int, parent_id: Optional[int] = None
    ) -> bool:
        """
        Vérifie si un dossier avec ce nom existe dans le parent.

        Args:
            nom: Nom du dossier.
            chantier_id: ID du chantier.
            parent_id: ID du dossier parent (None pour racine).

        Returns:
            True si le nom existe déjà.
        """
        pass

    @abstractmethod
    def find_by_type(
        self, chantier_id: int, type_dossier: DossierType
    ) -> Optional[Dossier]:
        """
        Trouve un dossier par son type dans un chantier.

        Args:
            chantier_id: ID du chantier.
            type_dossier: Type de dossier à chercher.

        Returns:
            Le dossier trouvé ou None.
        """
        pass

    @abstractmethod
    def get_arborescence(self, chantier_id: int) -> List[Dossier]:
        """
        Récupère toute l'arborescence des dossiers d'un chantier.

        Args:
            chantier_id: ID du chantier.

        Returns:
            Liste de tous les dossiers (à organiser en arbre côté appelant).
        """
        pass

    @abstractmethod
    def has_documents(self, dossier_id: int) -> bool:
        """
        Vérifie si un dossier contient des documents.

        Args:
            dossier_id: ID du dossier.

        Returns:
            True si le dossier contient des documents.
        """
        pass

    @abstractmethod
    def has_children(self, dossier_id: int) -> bool:
        """
        Vérifie si un dossier a des sous-dossiers.

        Args:
            dossier_id: ID du dossier.

        Returns:
            True si le dossier a des sous-dossiers.
        """
        pass
