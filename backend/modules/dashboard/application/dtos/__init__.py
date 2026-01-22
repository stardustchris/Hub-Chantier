"""DTOs du module Dashboard."""

from .post_dto import (
    PostDTO,
    PostListDTO,
    CreatePostDTO,
    UpdatePostDTO,
    PostDetailDTO,
)
from .comment_dto import (
    CommentDTO,
    CreateCommentDTO,
)
from .like_dto import LikeDTO
from .media_dto import MediaDTO, CreateMediaDTO

__all__ = [
    "PostDTO",
    "PostListDTO",
    "CreatePostDTO",
    "UpdatePostDTO",
    "PostDetailDTO",
    "CommentDTO",
    "CreateCommentDTO",
    "LikeDTO",
    "MediaDTO",
    "CreateMediaDTO",
]
