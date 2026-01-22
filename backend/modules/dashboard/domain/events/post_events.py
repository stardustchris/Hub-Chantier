"""Événements domaine liés aux posts."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Tuple


@dataclass(frozen=True)
class PostPublishedEvent:
    """
    Événement émis lorsqu'un post est publié.

    Permet aux autres modules de réagir (ex: notifications).
    """

    post_id: int
    author_id: int
    target_type: str
    chantier_ids: Optional[Tuple[int, ...]] = None
    user_ids: Optional[Tuple[int, ...]] = None
    is_urgent: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class PostPinnedEvent:
    """Événement émis lorsqu'un post est épinglé."""

    post_id: int
    author_id: int
    pinned_until: datetime
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class PostArchivedEvent:
    """Événement émis lorsqu'un post est archivé."""

    post_id: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class PostDeletedEvent:
    """Événement émis lorsqu'un post est supprimé par modération."""

    post_id: int
    deleted_by_user_id: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class CommentAddedEvent:
    """
    Événement émis lorsqu'un commentaire est ajouté.

    Permet d'envoyer une notification à l'auteur du post.
    """

    comment_id: int
    post_id: int
    author_id: int
    post_author_id: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class LikeAddedEvent:
    """
    Événement émis lorsqu'un like est ajouté.

    Permet d'envoyer une notification à l'auteur du post.
    """

    like_id: int
    post_id: int
    user_id: int
    post_author_id: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class LikeRemovedEvent:
    """Événement émis lorsqu'un like est retiré."""

    post_id: int
    user_id: int
    timestamp: datetime = field(default_factory=datetime.now)
