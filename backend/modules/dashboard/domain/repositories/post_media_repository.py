"""Interface PostMediaRepository - Contrat pour la persistance des médias."""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import PostMedia


class PostMediaRepository(ABC):
    """
    Interface définissant le contrat pour la persistance des médias de posts.
    """

    @abstractmethod
    def save(self, media: PostMedia) -> PostMedia:
        """
        Persiste un média.

        Args:
            media: Le média à persister.

        Returns:
            Le média avec son ID assigné.
        """
        pass

    @abstractmethod
    def save_all(self, medias: List[PostMedia]) -> List[PostMedia]:
        """
        Persiste plusieurs médias.

        Args:
            medias: Les médias à persister.

        Returns:
            Les médias avec leurs IDs assignés.
        """
        pass

    @abstractmethod
    def find_by_id(self, media_id: int) -> Optional[PostMedia]:
        """
        Trouve un média par son ID.

        Args:
            media_id: L'ID du média.

        Returns:
            Le média trouvé ou None.
        """
        pass

    @abstractmethod
    def find_by_post(self, post_id: int) -> List[PostMedia]:
        """
        Récupère les médias d'un post ordonnés par position.

        Args:
            post_id: ID du post.

        Returns:
            Liste des médias du post.
        """
        pass

    @abstractmethod
    def count_by_post(self, post_id: int) -> int:
        """
        Compte les médias d'un post.

        Args:
            post_id: ID du post.

        Returns:
            Nombre de médias.
        """
        pass

    @abstractmethod
    def delete(self, media_id: int) -> bool:
        """
        Supprime un média.

        Args:
            media_id: ID du média.

        Returns:
            True si supprimé, False sinon.
        """
        pass

    @abstractmethod
    def delete_by_post(self, post_id: int) -> int:
        """
        Supprime tous les médias d'un post.

        Args:
            post_id: ID du post.

        Returns:
            Nombre de médias supprimés.
        """
        pass
