"""Interfaces des repositories du module Dashboard."""

from .post_repository import PostRepository
from .comment_repository import CommentRepository
from .like_repository import LikeRepository
from .post_media_repository import PostMediaRepository

__all__ = ["PostRepository", "CommentRepository", "LikeRepository", "PostMediaRepository"]
