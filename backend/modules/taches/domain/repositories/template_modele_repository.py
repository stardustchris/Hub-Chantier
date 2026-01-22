"""Interface TemplateModeleRepository - Abstraction pour la persistence des modeles."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import TemplateModele


class TemplateModeleRepository(ABC):
    """
    Interface abstraite pour la persistence des templates de taches.

    Cette interface definit le contrat pour l'acces aux modeles (TAC-04).
    """

    @abstractmethod
    def find_by_id(self, template_id: int) -> Optional[TemplateModele]:
        """
        Trouve un template par son ID.

        Args:
            template_id: L'identifiant unique du template.

        Returns:
            Le template trouve ou None.
        """
        pass

    @abstractmethod
    def find_all(
        self,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TemplateModele]:
        """
        Recupere tous les templates.

        Args:
            active_only: Filtrer les actifs uniquement.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des templates.
        """
        pass

    @abstractmethod
    def find_by_categorie(
        self,
        categorie: str,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TemplateModele]:
        """
        Trouve les templates par categorie.

        Args:
            categorie: La categorie a filtrer.
            active_only: Filtrer les actifs uniquement.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des templates de la categorie.
        """
        pass

    @abstractmethod
    def save(self, template: TemplateModele) -> TemplateModele:
        """
        Persiste un template (creation ou mise a jour).

        Args:
            template: Le template a sauvegarder.

        Returns:
            Le template sauvegarde (avec ID si creation).
        """
        pass

    @abstractmethod
    def delete(self, template_id: int) -> bool:
        """
        Supprime un template.

        Args:
            template_id: L'identifiant du template a supprimer.

        Returns:
            True si supprime, False si non trouve.
        """
        pass

    @abstractmethod
    def count(self, active_only: bool = True) -> int:
        """
        Compte le nombre total de templates.

        Args:
            active_only: Compter uniquement les actifs.

        Returns:
            Nombre total de templates.
        """
        pass

    @abstractmethod
    def search(
        self,
        query: Optional[str] = None,
        categorie: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[TemplateModele], int]:
        """
        Recherche des templates avec filtres.

        Args:
            query: Texte a rechercher dans le nom/description.
            categorie: Filtrer par categorie.
            active_only: Filtrer les actifs uniquement.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Tuple (liste des templates, total count).
        """
        pass

    @abstractmethod
    def get_categories(self) -> List[str]:
        """
        Retourne la liste des categories distinctes.

        Returns:
            Liste des categories.
        """
        pass

    @abstractmethod
    def exists_by_nom(self, nom: str) -> bool:
        """
        Verifie si un template avec ce nom existe.

        Args:
            nom: Le nom a verifier.

        Returns:
            True si existe.
        """
        pass
