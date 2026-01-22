"""Entité Like - Représente une réaction j'aime sur un post."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Like:
    """
    Entité représentant une réaction j'aime sur un post.

    Selon CDC Section 2 - FEED-04: Réactions likes.

    Attributes:
        id: Identifiant unique (None si non persisté).
        post_id: ID du post liké.
        user_id: ID de l'utilisateur qui a liké.
        created_at: Date du like.
    """

    post_id: int
    user_id: int
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __eq__(self, other: object) -> bool:
        """Égalité basée sur l'ID (entité)."""
        if not isinstance(other, Like):
            return False
        if self.id is None or other.id is None:
            # Si pas d'ID, égalité sur post_id + user_id (unicité métier)
            return self.post_id == other.post_id and self.user_id == other.user_id
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur post_id et user_id (unicité métier)."""
        return hash((self.post_id, self.user_id))
