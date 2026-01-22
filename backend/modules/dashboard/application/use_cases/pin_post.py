"""Use Case PinPost - Épingler un post urgent."""

from typing import Callable, Optional

from ...domain.repositories import PostRepository
from ...domain.events import PostPinnedEvent
from .get_post import PostNotFoundError
from .delete_post import NotAuthorizedError


class PinPostUseCase:
    """
    Cas d'utilisation : Épingler un post en haut du fil.

    Selon CDC Section 2 - FEED-08: Messages urgents épinglés 48h max.

    Seuls les utilisateurs avec droits de modération peuvent épingler.
    """

    DEFAULT_DURATION_HOURS = 48

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
        duration_hours: int = DEFAULT_DURATION_HOURS,
        is_moderator: bool = False,
    ) -> bool:
        """
        Épingle un post.

        Args:
            post_id: ID du post à épingler.
            user_id: ID de l'utilisateur.
            duration_hours: Durée d'épinglage (max 48h).
            is_moderator: True si l'utilisateur est modérateur.

        Returns:
            True si épinglé avec succès.

        Raises:
            PostNotFoundError: Si le post n'existe pas.
            NotAuthorizedError: Si l'utilisateur n'est pas autorisé.
        """
        # Récupérer le post
        post = self.post_repo.find_by_id(post_id)
        if not post:
            raise PostNotFoundError(post_id)

        # Vérifier les droits (auteur ou modérateur)
        if post.author_id != user_id and not is_moderator:
            raise NotAuthorizedError(
                "Seul l'auteur ou un modérateur peut épingler ce post"
            )

        # Épingler
        post.pin(duration_hours)
        self.post_repo.save(post)

        # Publier l'event
        if self.event_publisher:
            event = PostPinnedEvent(
                post_id=post_id,
                author_id=post.author_id,
                pinned_until=post.pinned_until,
            )
            self.event_publisher(event)

        return True

    def unpin(self, post_id: int, user_id: int, is_moderator: bool = False) -> bool:
        """
        Retire l'épinglage d'un post.

        Args:
            post_id: ID du post.
            user_id: ID de l'utilisateur.
            is_moderator: True si l'utilisateur est modérateur.

        Returns:
            True si désépinglé avec succès.
        """
        post = self.post_repo.find_by_id(post_id)
        if not post:
            raise PostNotFoundError(post_id)

        if post.author_id != user_id and not is_moderator:
            raise NotAuthorizedError(
                "Seul l'auteur ou un modérateur peut désépingler ce post"
            )

        post.unpin()
        self.post_repo.save(post)

        return True
