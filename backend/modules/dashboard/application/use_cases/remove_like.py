"""Use Case RemoveLike - Retrait d'un like sur un post."""

from typing import Callable, Optional

from ...domain.repositories import LikeRepository
from ...domain.events import LikeRemovedEvent


class LikeNotFoundError(Exception):
    """Exception levée quand le like n'existe pas."""

    def __init__(self, post_id: int, user_id: int):
        self.post_id = post_id
        self.user_id = user_id
        self.message = f"Vous n'avez pas liké le post {post_id}"
        super().__init__(self.message)


class RemoveLikeUseCase:
    """
    Cas d'utilisation : Retrait d'un like sur un post.

    Permet à un utilisateur de retirer son like.
    """

    def __init__(
        self,
        like_repo: LikeRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            like_repo: Repository likes (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.like_repo = like_repo
        self.event_publisher = event_publisher

    def execute(self, post_id: int, user_id: int) -> bool:
        """
        Retire un like d'un post.

        Args:
            post_id: ID du post.
            user_id: ID de l'utilisateur.

        Returns:
            True si le like a été retiré.

        Raises:
            LikeNotFoundError: Si le like n'existe pas.
        """
        # Vérifier que le like existe
        existing_like = self.like_repo.find_by_post_and_user(post_id, user_id)
        if not existing_like:
            raise LikeNotFoundError(post_id, user_id)

        # Supprimer
        self.like_repo.delete_by_post_and_user(post_id, user_id)

        # Publier l'event
        if self.event_publisher:
            event = LikeRemovedEvent(
                post_id=post_id,
                user_id=user_id,
            )
            self.event_publisher(event)

        return True
