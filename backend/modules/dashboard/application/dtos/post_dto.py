"""DTOs pour les posts."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Tuple

from ...domain.entities import Post
from ...domain.value_objects import TargetType


@dataclass(frozen=True)
class PostDTO:
    """
    Data Transfer Object pour un post.

    Utilisé pour transférer les données de post entre les couches.
    Selon CDC Section 2 - Tableau de Bord (FEED-01 à FEED-20).
    """

    id: int
    author_id: int
    content: str
    status: str
    is_urgent: bool
    is_pinned: bool
    target_type: str
    target_display: str
    chantier_ids: Optional[Tuple[int, ...]]
    user_ids: Optional[Tuple[int, ...]]
    created_at: datetime
    likes_count: int = 0
    comments_count: int = 0
    medias_count: int = 0

    @classmethod
    def from_entity(
        cls,
        post: Post,
        likes_count: int = 0,
        comments_count: int = 0,
        medias_count: int = 0,
    ) -> "PostDTO":
        """
        Crée un DTO à partir d'une entité Post.

        Args:
            post: L'entité Post source.
            likes_count: Nombre de likes.
            comments_count: Nombre de commentaires.
            medias_count: Nombre de médias.

        Returns:
            Le DTO correspondant.
        """
        return cls(
            id=post.id,
            author_id=post.author_id,
            content=post.content,
            status=post.status.value,
            is_urgent=post.is_urgent,
            is_pinned=post.is_pinned,
            target_type=post.targeting.target_type.value,
            target_display=post.target_display,
            chantier_ids=post.targeting.chantier_ids,
            user_ids=post.targeting.user_ids,
            created_at=post.created_at,
            likes_count=likes_count,
            comments_count=comments_count,
            medias_count=medias_count,
        )


@dataclass(frozen=True)
class PostListDTO:
    """DTO pour une liste paginée de posts (FEED-18)."""

    posts: List[PostDTO]
    total: int
    offset: int
    limit: int

    @property
    def has_next(self) -> bool:
        """Indique s'il y a une page suivante."""
        return self.offset + self.limit < self.total

    @property
    def has_previous(self) -> bool:
        """Indique s'il y a une page précédente."""
        return self.offset > 0


@dataclass(frozen=True)
class CreatePostDTO:
    """
    DTO pour la création d'un post.

    Selon CDC Section 2 - FEED-01 à FEED-03.
    """

    content: str
    target_type: str = "everyone"  # everyone, specific_chantiers, specific_people
    chantier_ids: Optional[List[int]] = None
    user_ids: Optional[List[int]] = None
    is_urgent: bool = False


@dataclass(frozen=True)
class UpdatePostDTO:
    """DTO pour la mise à jour d'un post."""

    content: Optional[str] = None
    is_urgent: Optional[bool] = None


@dataclass(frozen=True)
class PostDetailDTO:
    """
    DTO pour les détails complets d'un post avec ses relations.

    Inclut les médias, likes et commentaires.
    """

    post: PostDTO
    medias: List["MediaDTO"] = None
    comments: List["CommentDTO"] = None
    liked_by_user_ids: List[int] = None

    def __post_init__(self):
        # Workaround pour les listes mutables dans frozen dataclass
        object.__setattr__(self, "medias", self.medias or [])
        object.__setattr__(self, "comments", self.comments or [])
        object.__setattr__(self, "liked_by_user_ids", self.liked_by_user_ids or [])


# Forward references pour éviter les imports circulaires
from .media_dto import MediaDTO
from .comment_dto import CommentDTO
