"""Use Case AddLike - Ajout d'un like sur un post."""

from typing import Callable, Optional

from ...domain.entities import Like
from ...domain.repositories import PostRepository, LikeRepository
from ...domain.events import LikeAddedEvent
from ..dtos import LikeDTO
from .get_post import PostNotFoundError


class AlreadyLikedError(Exception):
    """Exception levée quand l'utilisateur a déjà liké le post."""

    def __init__(self, post_id: int):
        self.post_id = post_id
        self.message = f"Vous avez déjà liké le post {post_id}"
        super().__init__(self.message)


class AddLikeUseCase:
    """
    Cas d'utilisation : Ajout d'un like sur un post.

    Selon CDC Section 2 - FEED-04: Réactions likes.
    """

    def __init__(
        self,
        post_repo: PostRepository,
        like_repo: LikeRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            post_repo: Repository posts (interface).
            like_repo: Repository likes (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.post_repo = post_repo
        self.like_repo = like_repo
        self.event_publisher = event_publisher

    def execute(self, post_id: int, user_id: int) -> LikeDTO:
        """
        Ajoute un like sur un post.

        Args:
            post_id: ID du post à liker.
            user_id: ID de l'utilisateur qui like.

        Returns:
            LikeDTO du like créé.

        Raises:
            PostNotFoundError: Si le post n'existe pas.
            AlreadyLikedError: Si l'utilisateur a déjà liké.
        """
        # Vérifier que le post existe
        post = self.post_repo.find_by_id(post_id)
        if not post:
            raise PostNotFoundError(post_id)

        # Vérifier si déjà liké
        existing_like = self.like_repo.find_by_post_and_user(post_id, user_id)
        if existing_like:
            raise AlreadyLikedError(post_id)

        # Créer le like
        like = Like(
            post_id=post_id,
            user_id=user_id,
        )

        # Sauvegarder
        like = self.like_repo.save(like)

        # Publier l'event (pour notification à l'auteur du post)
        if self.event_publisher:
            event = LikeAddedEvent(
                like_id=like.id,
                post_id=post_id,
                user_id=user_id,
                post_author_id=post.author_id,
            )
            self.event_publisher(event)

        return LikeDTO.from_entity(like)
