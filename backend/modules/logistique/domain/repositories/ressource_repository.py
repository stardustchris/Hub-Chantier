"""Interface du repository pour les ressources.

LOG-01: Référentiel matériel - CRUD des ressources.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import Ressource
from ..value_objects import CategorieRessource


class RessourceRepository(ABC):
    """Interface abstraite pour la persistence des ressources."""

    @abstractmethod
    def save(self, ressource: Ressource) -> Ressource:
        """Persiste une ressource (création ou mise à jour).

        Args:
            ressource: La ressource à persister

        Returns:
            La ressource avec son ID attribué
        """
        pass

    @abstractmethod
    def find_by_id(self, ressource_id: int) -> Optional[Ressource]:
        """Recherche une ressource par son ID.

        Args:
            ressource_id: L'ID de la ressource

        Returns:
            La ressource ou None si non trouvée
        """
        pass

    @abstractmethod
    def find_by_code(self, code: str) -> Optional[Ressource]:
        """Recherche une ressource par son code.

        Args:
            code: Le code unique de la ressource

        Returns:
            La ressource ou None si non trouvée
        """
        pass

    @abstractmethod
    def find_all(
        self,
        categorie: Optional[CategorieRessource] = None,
        actif_seulement: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Ressource]:
        """Liste les ressources avec filtres optionnels.

        Args:
            categorie: Filtrer par catégorie
            actif_seulement: Ne retourner que les ressources actives
            limit: Nombre maximum de résultats
            offset: Décalage pour pagination

        Returns:
            Liste des ressources correspondantes
        """
        pass

    @abstractmethod
    def count(
        self,
        categorie: Optional[CategorieRessource] = None,
        actif_seulement: bool = True,
    ) -> int:
        """Compte le nombre de ressources.

        Args:
            categorie: Filtrer par catégorie
            actif_seulement: Ne compter que les ressources actives

        Returns:
            Le nombre de ressources
        """
        pass

    @abstractmethod
    def delete(self, ressource_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime une ressource (soft delete - H10).

        Args:
            ressource_id: L'ID de la ressource à supprimer
            deleted_by: L'ID de l'utilisateur qui supprime (optionnel)

        Returns:
            True si supprimée, False si non trouvée
        """
        pass

    @abstractmethod
    def find_by_categorie(self, categorie: CategorieRessource) -> List[Ressource]:
        """Liste les ressources d'une catégorie.

        Args:
            categorie: La catégorie à filtrer

        Returns:
            Liste des ressources de cette catégorie
        """
        pass
