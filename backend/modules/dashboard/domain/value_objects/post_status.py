"""Value Object PostStatus - Statut d'un post."""

from enum import Enum


class PostStatus(str, Enum):
    """
    Statut d'un post dans le fil d'actualités.

    Selon CDC Section 2:
    - PUBLISHED: Post publié et visible (FEED-01)
    - PINNED: Post épinglé en haut pendant 48h max (FEED-08)
    - ARCHIVED: Post archivé après 7 jours, toujours consultable (FEED-20)
    - DELETED: Post supprimé par modération (FEED-16)
    """

    PUBLISHED = "published"
    PINNED = "pinned"
    ARCHIVED = "archived"
    DELETED = "deleted"

    def __str__(self) -> str:
        return self.value

    def is_visible(self) -> bool:
        """Vérifie si le post est visible dans le fil."""
        return self in (PostStatus.PUBLISHED, PostStatus.PINNED)

    def is_consultable(self) -> bool:
        """Vérifie si le post peut être consulté (même archivé)."""
        return self != PostStatus.DELETED

    @classmethod
    def from_string(cls, value: str) -> "PostStatus":
        """Crée un PostStatus à partir d'une string."""
        try:
            return cls(value.lower())
        except ValueError:
            valid_statuses = [s.value for s in cls]
            raise ValueError(
                f"Statut invalide: {value}. Statuts valides: {valid_statuses}"
            )
