"""Dépendances FastAPI pour le module Dashboard."""

from fastapi import Depends
from sqlalchemy.orm import Session

from ...application.use_cases import (
    PublishPostUseCase,
    GetFeedUseCase,
    GetPostUseCase,
    DeletePostUseCase,
    PinPostUseCase,
    AddCommentUseCase,
    AddLikeUseCase,
    RemoveLikeUseCase,
)
from ..persistence import (
    SQLAlchemyPostRepository,
    SQLAlchemyCommentRepository,
    SQLAlchemyLikeRepository,
    SQLAlchemyPostMediaRepository,
)
from shared.infrastructure.database import get_db


def get_post_repository(db: Session = Depends(get_db)) -> SQLAlchemyPostRepository:
    """Retourne le repository posts."""
    return SQLAlchemyPostRepository(db)


def get_comment_repository(db: Session = Depends(get_db)) -> SQLAlchemyCommentRepository:
    """Retourne le repository commentaires."""
    return SQLAlchemyCommentRepository(db)


def get_like_repository(db: Session = Depends(get_db)) -> SQLAlchemyLikeRepository:
    """Retourne le repository likes."""
    return SQLAlchemyLikeRepository(db)


def get_media_repository(db: Session = Depends(get_db)) -> SQLAlchemyPostMediaRepository:
    """Retourne le repository médias."""
    return SQLAlchemyPostMediaRepository(db)


def get_publish_post_use_case(
    post_repo: SQLAlchemyPostRepository = Depends(get_post_repository),
    media_repo: SQLAlchemyPostMediaRepository = Depends(get_media_repository),
) -> PublishPostUseCase:
    """Retourne le use case de publication."""
    return PublishPostUseCase(
        post_repo=post_repo,
        media_repo=media_repo,
    )


def get_feed_use_case(
    post_repo: SQLAlchemyPostRepository = Depends(get_post_repository),
    like_repo: SQLAlchemyLikeRepository = Depends(get_like_repository),
    comment_repo: SQLAlchemyCommentRepository = Depends(get_comment_repository),
) -> GetFeedUseCase:
    """Retourne le use case du feed."""
    return GetFeedUseCase(
        post_repo=post_repo,
        like_repo=like_repo,
        comment_repo=comment_repo,
    )


def get_post_use_case(
    post_repo: SQLAlchemyPostRepository = Depends(get_post_repository),
    like_repo: SQLAlchemyLikeRepository = Depends(get_like_repository),
    comment_repo: SQLAlchemyCommentRepository = Depends(get_comment_repository),
    media_repo: SQLAlchemyPostMediaRepository = Depends(get_media_repository),
) -> GetPostUseCase:
    """Retourne le use case de récupération d'un post."""
    return GetPostUseCase(
        post_repo=post_repo,
        like_repo=like_repo,
        comment_repo=comment_repo,
        media_repo=media_repo,
    )


def get_delete_post_use_case(
    post_repo: SQLAlchemyPostRepository = Depends(get_post_repository),
) -> DeletePostUseCase:
    """Retourne le use case de suppression."""
    return DeletePostUseCase(post_repo=post_repo)


def get_pin_post_use_case(
    post_repo: SQLAlchemyPostRepository = Depends(get_post_repository),
) -> PinPostUseCase:
    """Retourne le use case d'épinglage."""
    return PinPostUseCase(post_repo=post_repo)


def get_add_comment_use_case(
    post_repo: SQLAlchemyPostRepository = Depends(get_post_repository),
    comment_repo: SQLAlchemyCommentRepository = Depends(get_comment_repository),
) -> AddCommentUseCase:
    """Retourne le use case d'ajout de commentaire."""
    return AddCommentUseCase(
        post_repo=post_repo,
        comment_repo=comment_repo,
    )


def get_add_like_use_case(
    post_repo: SQLAlchemyPostRepository = Depends(get_post_repository),
    like_repo: SQLAlchemyLikeRepository = Depends(get_like_repository),
) -> AddLikeUseCase:
    """Retourne le use case d'ajout de like."""
    return AddLikeUseCase(
        post_repo=post_repo,
        like_repo=like_repo,
    )


def get_remove_like_use_case(
    like_repo: SQLAlchemyLikeRepository = Depends(get_like_repository),
) -> RemoveLikeUseCase:
    """Retourne le use case de retrait de like."""
    return RemoveLikeUseCase(like_repo=like_repo)
