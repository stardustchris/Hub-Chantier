"""Interface CommentRepository - Contrat pour la persistance des commentaires."""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import Comment


class CommentRepository(ABC):
    """
    Interface définissant le contrat pour la persistance des commentaires.
    """

    @abstractmethod
    def save(self, comment: Comment) -> Comment:
        """
        Persiste un commentaire.

        Args:
            comment: Le commentaire à persister.

        Returns:
            Le commentaire avec son ID assigné.
        """
        pass

    @abstractmethod
    def find_by_id(self, comment_id: int) -> Optional[Comment]:
        """
        Trouve un commentaire par son ID.

        Args:
            comment_id: L'ID du commentaire.

        Returns:
            Le commentaire trouvé ou None.
        """
        pass

    @abstractmethod
    def find_by_post(
        self,
        post_id: int,
        include_deleted: bool = False,
    ) -> List[Comment]:
        """
        Récupère les commentaires d'un post.

        Args:
            post_id: ID du post.
            include_deleted: Inclure les commentaires supprimés.

        Returns:
            Liste des commentaires du post.
        """
        pass

    @abstractmethod
    def find_by_author(self, author_id: int) -> List[Comment]:
        """
        Récupère les commentaires d'un auteur.

        Args:
            author_id: ID de l'auteur.

        Returns:
            Liste des commentaires de l'auteur.
        """
        pass

    @abstractmethod
    def count_by_post(self, post_id: int) -> int:
        """
        Compte les commentaires d'un post.

        Args:
            post_id: ID du post.

        Returns:
            Nombre de commentaires.
        """
        pass

    @abstractmethod
    def delete(self, comment_id: int) -> bool:
        """
        Supprime physiquement un commentaire.

        Args:
            comment_id: ID du commentaire.

        Returns:
            True si supprimé, False sinon.
        """
        pass
