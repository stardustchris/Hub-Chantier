"""Use Case DeletePost - Suppression d'un post par modération."""

from typing import Callable, Optional

from ...domain.repositories import PostRepository
from ...domain.events import PostDeletedEvent
from .get_post import PostNotFoundError


class NotAuthorizedError(Exception):
    """Exception levée quand l'utilisateur n'est pas autorisé."""

    def __init__(self, message: str = "Vous n'êtes pas autorisé à effectuer cette action"):
        self.message = message
        super().__init__(self.message)


class DeletePostUseCase:
    """
    Cas d'utilisation : Suppression d'un post.

    Selon CDC Section 2 - FEED-16: Modération par la Direction.

    Seuls l'auteur du post ou les utilisateurs avec le rôle Admin/Conducteur
    peuvent supprimer un post.
    """

    def __init__(
        self,
        post_repo: PostRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            post_repo: Repository posts (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.post_repo = post_repo
        self.event_publisher = event_publisher

    def execute(
        self,
        post_id: int,
        user_id: int,
        is_moderator: bool = False,
    ) -> bool:
        """
        Supprime un post (suppression logique).

        Args:
            post_id: ID du post à supprimer.
            user_id: ID de l'utilisateur effectuant la suppression.
            is_moderator: True si l'utilisateur est modérateur (Admin/Conducteur).

        Returns:
            True si supprimé avec succès.

        Raises:
            PostNotFoundError: Si le post n'existe pas.
            NotAuthorizedError: Si l'utilisateur n'est pas autorisé.
        """
        # Récupérer le post
        post = self.post_repo.find_by_id(post_id)
        if not post:
            raise PostNotFoundError(post_id)

        # Vérifier les droits
        if post.author_id != user_id and not is_moderator:
            raise NotAuthorizedError(
                "Seul l'auteur ou un modérateur peut supprimer ce post"
            )

        # Supprimer (logiquement)
        post.delete()
        self.post_repo.save(post)

        # Publier l'event
        if self.event_publisher:
            event = PostDeletedEvent(
                post_id=post_id,
                deleted_by_user_id=user_id,
            )
            self.event_publisher(event)

        return True
