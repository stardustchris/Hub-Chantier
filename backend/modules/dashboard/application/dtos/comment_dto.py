"""DTOs pour les commentaires."""

from dataclasses import dataclass
from datetime import datetime

from ...domain.entities import Comment


@dataclass(frozen=True)
class CommentDTO:
    """
    Data Transfer Object pour un commentaire.

    Selon CDC Section 2 - FEED-05: Commentaires sur posts.
    """

    id: int
    post_id: int
    author_id: int
    content: str
    created_at: datetime

    @classmethod
    def from_entity(cls, comment: Comment) -> "CommentDTO":
        """
        Crée un DTO à partir d'une entité Comment.

        Args:
            comment: L'entité Comment source.

        Returns:
            Le DTO correspondant.
        """
        return cls(
            id=comment.id,
            post_id=comment.post_id,
            author_id=comment.author_id,
            content=comment.content,
            created_at=comment.created_at,
        )


@dataclass(frozen=True)
class CreateCommentDTO:
    """DTO pour la création d'un commentaire."""

    post_id: int
    content: str
