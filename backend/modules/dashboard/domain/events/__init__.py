"""Événements domaine du module Dashboard."""

from .post_events import (
    PostPublishedEvent,
    PostPinnedEvent,
    PostArchivedEvent,
    PostDeletedEvent,
    CommentAddedEvent,
    LikeAddedEvent,
    LikeRemovedEvent,
)

__all__ = [
    "PostPublishedEvent",
    "PostPinnedEvent",
    "PostArchivedEvent",
    "PostDeletedEvent",
    "CommentAddedEvent",
    "LikeAddedEvent",
    "LikeRemovedEvent",
]
