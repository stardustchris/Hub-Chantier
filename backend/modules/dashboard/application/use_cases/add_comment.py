"""Use Case AddComment - Ajout d'un commentaire sur un post."""

from typing import Callable, Optional

from ...domain.entities import Comment
from ...domain.repositories import PostRepository, CommentRepository
from ...domain.events import CommentAddedEvent
from ..dtos import CreateCommentDTO, CommentDTO
from .get_post import PostNotFoundError


class CommentContentEmptyError(Exception):
    """Exception levée quand le contenu du commentaire est vide."""

    def __init__(self):
        self.message = "Le contenu du commentaire ne peut pas être vide"
        super().__init__(self.message)


class AddCommentUseCase:
    """
    Cas d'utilisation : Ajout d'un commentaire sur un post.

    Selon CDC Section 2 - FEED-05: Commentaires sur posts.
    """

    def __init__(
        self,
        post_repo: PostRepository,
        comment_repo: CommentRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            post_repo: Repository posts (interface).
            comment_repo: Repository commentaires (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.post_repo = post_repo
        self.comment_repo = comment_repo
        self.event_publisher = event_publisher

    def execute(self, dto: CreateCommentDTO, author_id: int) -> CommentDTO:
        """
        Ajoute un commentaire sur un post.

        Args:
            dto: Les données du commentaire.
            author_id: ID de l'auteur du commentaire.

        Returns:
            CommentDTO du commentaire créé.

        Raises:
            PostNotFoundError: Si le post n'existe pas.
            CommentContentEmptyError: Si le contenu est vide.
        """
        # Vérifier que le post existe
        post = self.post_repo.find_by_id(dto.post_id)
        if not post:
            raise PostNotFoundError(dto.post_id)

        # Valider le contenu
        if not dto.content or not dto.content.strip():
            raise CommentContentEmptyError()

        # Créer le commentaire
        comment = Comment(
            post_id=dto.post_id,
            author_id=author_id,
            content=dto.content,
        )

        # Sauvegarder
        comment = self.comment_repo.save(comment)

        # Publier l'event (pour notification à l'auteur du post)
        if self.event_publisher:
            event = CommentAddedEvent(
                comment_id=comment.id,
                post_id=post.id,
                author_id=author_id,
                post_author_id=post.author_id,
            )
            self.event_publisher(event)

        return CommentDTO.from_entity(comment)
