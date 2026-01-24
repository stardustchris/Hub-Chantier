"""Interface du repository pour les ressources.

Clean Architecture: Interface dans Domain, implementation dans Infrastructure.
"""
from abc import ABC, abstractmethod
from typing import Optional

from ..entities import Ressource
from ..value_objects import TypeRessource


class RessourceRepository(ABC):
    """
    Interface abstraite pour le repository des ressources.

    Cette interface est definie dans le Domain pour respecter
    la regle de dependance de la Clean Architecture.
    L'implementation concrete est dans Infrastructure.
    """

    @abstractmethod
    async def get_by_id(self, ressource_id: int) -> Optional[Ressource]:
        """
        Recupere une ressource par son ID.

        Args:
            ressource_id: L'ID de la ressource.

        Returns:
            La ressource ou None si non trouvee.
        """
        pass

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[Ressource]:
        """
        Recupere une ressource par son code.

        Args:
            code: Le code unique de la ressource.

        Returns:
            La ressource ou None si non trouvee.
        """
        pass

    @abstractmethod
    async def list_all(
        self,
        type_ressource: Optional[TypeRessource] = None,
        is_active: Optional[bool] = None,
        include_deleted: bool = False,
    ) -> list[Ressource]:
        """
        Liste les ressources avec filtres optionnels.

        Args:
            type_ressource: Filtrer par type.
            is_active: Filtrer par statut actif.
            include_deleted: Inclure les ressources supprimees.

        Returns:
            Liste des ressources.
        """
        pass

    @abstractmethod
    async def save(self, ressource: Ressource) -> Ressource:
        """
        Sauvegarde une ressource (creation ou mise a jour).

        Args:
            ressource: La ressource a sauvegarder.

        Returns:
            La ressource sauvegardee avec son ID.
        """
        pass

    @abstractmethod
    async def delete(self, ressource_id: int, hard_delete: bool = False) -> bool:
        """
        Supprime une ressource.

        Args:
            ressource_id: L'ID de la ressource.
            hard_delete: Si True, suppression physique. Sinon soft delete.

        Returns:
            True si la suppression a reussi.
        """
        pass

    @abstractmethod
    async def code_exists(self, code: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifie si un code existe deja.

        Args:
            code: Le code a verifier.
            exclude_id: ID a exclure (pour mise a jour).

        Returns:
            True si le code existe.
        """
        pass
