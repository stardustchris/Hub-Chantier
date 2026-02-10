"""Interface LikeRepository - Contrat pour la persistance des likes."""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import Like


class LikeRepository(ABC):
    """
    Interface définissant le contrat pour la persistance des likes.
    """

    @abstractmethod
    def save(self, like: Like) -> Like:
        """
        Persiste un like.

        Args:
            like: Le like à persister.

        Returns:
            Le like avec son ID assigné.
        """
        pass

    @abstractmethod
    def find_by_id(self, like_id: int) -> Optional[Like]:
        """
        Trouve un like par son ID.

        Args:
            like_id: L'ID du like.

        Returns:
            Le like trouvé ou None.
        """
        pass

    @abstractmethod
    def find_by_post_and_user(
        self,
        post_id: int,
        user_id: int,
    ) -> Optional[Like]:
        """
        Trouve un like par post et utilisateur.

        Args:
            post_id: ID du post.
            user_id: ID de l'utilisateur.

        Returns:
            Le like trouvé ou None.
        """
        pass

    @abstractmethod
    def find_by_post(self, post_id: int) -> List[Like]:
        """
        Récupère tous les likes d'un post.

        Args:
            post_id: ID du post.

        Returns:
            Liste des likes du post.
        """
        pass

    @abstractmethod
    def find_user_ids_by_post(self, post_id: int) -> List[int]:
        """
        Récupère les IDs des utilisateurs ayant liké un post.

        Args:
            post_id: ID du post.

        Returns:
            Liste des IDs d'utilisateurs.
        """
        pass

    @abstractmethod
    def count_by_post(self, post_id: int) -> int:
        """
        Compte les likes d'un post.

        Args:
            post_id: ID du post.

        Returns:
            Nombre de likes.
        """
        pass

    @abstractmethod
    def delete(self, like_id: int) -> bool:
        """
        Supprime un like.

        Args:
            like_id: ID du like.

        Returns:
            True si supprimé, False sinon.
        """
        pass

    @abstractmethod
    def delete_by_post_and_user(self, post_id: int, user_id: int) -> bool:
        """
        Supprime un like par post et utilisateur.

        Args:
            post_id: ID du post.
            user_id: ID de l'utilisateur.

        Returns:
            True si supprimé, False sinon.
        """
        pass

    @abstractmethod
    def find_by_user(self, user_id: int) -> List[Like]:
        """
        Récupère tous les likes d'un utilisateur.

        Utilisé pour l'export RGPD (Article 20 - Portabilité des données).

        Args:
            user_id: ID de l'utilisateur.

        Returns:
            Liste des likes de l'utilisateur.
        """
        pass
