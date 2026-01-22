"""DTOs pour les likes."""

from dataclasses import dataclass
from datetime import datetime

from ...domain.entities import Like


@dataclass(frozen=True)
class LikeDTO:
    """
    Data Transfer Object pour un like.

    Selon CDC Section 2 - FEED-04: Réactions likes.
    """

    id: int
    post_id: int
    user_id: int
    created_at: datetime

    @classmethod
    def from_entity(cls, like: Like) -> "LikeDTO":
        """
        Crée un DTO à partir d'une entité Like.

        Args:
            like: L'entité Like source.

        Returns:
            Le DTO correspondant.
        """
        return cls(
            id=like.id,
            post_id=like.post_id,
            user_id=like.user_id,
            created_at=like.created_at,
        )
