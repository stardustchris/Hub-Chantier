"""Interface TemplateFormulaireRepository - Abstraction pour la persistence des templates."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import TemplateFormulaire
from ..value_objects import CategorieFormulaire


class TemplateFormulaireRepository(ABC):
    """
    Interface abstraite pour la persistence des templates de formulaire.

    Cette interface definit le contrat pour l'acces aux donnees.
    L'implementation concrete se trouve dans la couche Infrastructure.
    """

    @abstractmethod
    def find_by_id(self, template_id: int) -> Optional[TemplateFormulaire]:
        """
        Trouve un template par son ID.

        Args:
            template_id: L'identifiant unique du template.

        Returns:
            Le template trouve ou None.
        """
        pass

    @abstractmethod
    def find_by_nom(self, nom: str) -> Optional[TemplateFormulaire]:
        """
        Trouve un template par son nom.

        Args:
            nom: Le nom du template.

        Returns:
            Le template trouve ou None.
        """
        pass

    @abstractmethod
    def save(self, template: TemplateFormulaire) -> TemplateFormulaire:
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
    def find_all(self, skip: int = 0, limit: int = 100) -> List[TemplateFormulaire]:
        """
        Recupere tous les templates avec pagination.

        Args:
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum d'elements a retourner.

        Returns:
            Liste des templates.
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Compte le nombre total de templates.

        Returns:
            Nombre total de templates.
        """
        pass

    @abstractmethod
    def find_by_categorie(
        self,
        categorie: CategorieFormulaire,
        skip: int = 0,
        limit: int = 100
    ) -> List[TemplateFormulaire]:
        """
        Trouve les templates par categorie.

        Args:
            categorie: La categorie a filtrer.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des templates de cette categorie.
        """
        pass

    @abstractmethod
    def find_active(self, skip: int = 0, limit: int = 100) -> List[TemplateFormulaire]:
        """
        Trouve les templates actifs.

        Args:
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des templates actifs.
        """
        pass

    @abstractmethod
    def exists_by_nom(self, nom: str) -> bool:
        """
        Verifie si un nom de template est deja utilise.

        Args:
            nom: Le nom a verifier.

        Returns:
            True si le nom existe deja.
        """
        pass

    @abstractmethod
    def search(
        self,
        query: Optional[str] = None,
        categorie: Optional[CategorieFormulaire] = None,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[TemplateFormulaire], int]:
        """
        Recherche des templates avec filtres multiples.

        Args:
            query: Texte a rechercher dans nom, description.
            categorie: Filtrer par categorie (optionnel).
            active_only: Filtrer les actifs uniquement.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Tuple (liste des templates, total count).
        """
        pass
