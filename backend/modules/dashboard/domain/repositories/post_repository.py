"""Interface PostRepository - Contrat pour la persistance des posts."""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import Post
from ..value_objects import PostStatus


class PostRepository(ABC):
    """
    Interface définissant le contrat pour la persistance des posts.

    Cette interface est implémentée par SQLAlchemyPostRepository
    dans la couche infrastructure.
    """

    @abstractmethod
    def save(self, post: Post) -> Post:
        """
        Persiste un post (création ou mise à jour).

        Args:
            post: Le post à persister.

        Returns:
            Le post avec son ID assigné.
        """
        pass

    @abstractmethod
    def find_by_id(self, post_id: int) -> Optional[Post]:
        """
        Trouve un post par son ID.

        Args:
            post_id: L'ID du post.

        Returns:
            Le post trouvé ou None.
        """
        pass

    @abstractmethod
    def find_feed(
        self,
        user_id: int,
        user_chantier_ids: Optional[List[int]] = None,
        limit: int = 20,
        offset: int = 0,
        include_archived: bool = False,
    ) -> List[Post]:
        """
        Récupère le fil d'actualités pour un utilisateur (FEED-09, FEED-18).

        Les posts sont filtrés selon le ciblage et triés par date décroissante.
        Les posts épinglés apparaissent en premier.

        Args:
            user_id: ID de l'utilisateur.
            user_chantier_ids: IDs des chantiers de l'utilisateur.
            limit: Nombre de posts à retourner (default 20).
            offset: Offset pour la pagination.
            include_archived: Inclure les posts archivés.

        Returns:
            Liste des posts visibles pour l'utilisateur.
        """
        pass

    @abstractmethod
    def find_by_author(
        self,
        author_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Post]:
        """
        Récupère les posts d'un auteur.

        Args:
            author_id: ID de l'auteur.
            limit: Nombre de posts à retourner.
            offset: Offset pour la pagination.

        Returns:
            Liste des posts de l'auteur.
        """
        pass

    @abstractmethod
    def find_by_status(self, status: PostStatus) -> List[Post]:
        """
        Récupère les posts par statut.

        Args:
            status: Le statut recherché.

        Returns:
            Liste des posts avec ce statut.
        """
        pass

    @abstractmethod
    def find_posts_to_archive(self) -> List[Post]:
        """
        Récupère les posts qui devraient être archivés (plus de 7 jours).

        Returns:
            Liste des posts à archiver.
        """
        pass

    @abstractmethod
    def find_expired_pins(self) -> List[Post]:
        """
        Récupère les posts épinglés dont la durée a expiré.

        Returns:
            Liste des posts dont l'épinglage a expiré.
        """
        pass

    @abstractmethod
    def count_by_author(self, author_id: int) -> int:
        """
        Compte le nombre de posts d'un auteur.

        Args:
            author_id: ID de l'auteur.

        Returns:
            Nombre de posts.
        """
        pass

    @abstractmethod
    def delete(self, post_id: int) -> bool:
        """
        Supprime physiquement un post.

        Note: Préférer post.delete() pour une suppression logique.

        Args:
            post_id: ID du post à supprimer.

        Returns:
            True si supprimé, False sinon.
        """
        pass
