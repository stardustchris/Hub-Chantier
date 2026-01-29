"""Tests unitaires pour les dépendances du module Dashboard."""

from unittest.mock import Mock

from modules.dashboard.infrastructure.web.dependencies import (
    get_post_repository,
    get_comment_repository,
    get_like_repository,
    get_media_repository,
    get_publish_post_use_case,
    get_feed_use_case,
    get_post_use_case,
    get_delete_post_use_case,
    get_pin_post_use_case,
    get_add_comment_use_case,
    get_add_like_use_case,
    get_remove_like_use_case,
)
from modules.dashboard.infrastructure.persistence import (
    SQLAlchemyPostRepository,
    SQLAlchemyCommentRepository,
    SQLAlchemyLikeRepository,
    SQLAlchemyPostMediaRepository,
)
from modules.dashboard.application.use_cases import (
    PublishPostUseCase,
    GetFeedUseCase,
    GetPostUseCase,
    DeletePostUseCase,
    PinPostUseCase,
    AddCommentUseCase,
    AddLikeUseCase,
    RemoveLikeUseCase,
)


class TestRepositoryFactories:
    """Tests pour les factories de repositories."""

    def test_get_post_repository(self):
        result = get_post_repository(db=Mock())
        assert isinstance(result, SQLAlchemyPostRepository)

    def test_get_comment_repository(self):
        result = get_comment_repository(db=Mock())
        assert isinstance(result, SQLAlchemyCommentRepository)

    def test_get_like_repository(self):
        result = get_like_repository(db=Mock())
        assert isinstance(result, SQLAlchemyLikeRepository)

    def test_get_media_repository(self):
        result = get_media_repository(db=Mock())
        assert isinstance(result, SQLAlchemyPostMediaRepository)


class TestUseCaseFactories:
    """Tests pour les factories de use cases."""

    def setup_method(self):
        self.mock_db = Mock()
        self.post_repo = SQLAlchemyPostRepository(self.mock_db)
        self.comment_repo = SQLAlchemyCommentRepository(self.mock_db)
        self.like_repo = SQLAlchemyLikeRepository(self.mock_db)
        self.media_repo = SQLAlchemyPostMediaRepository(self.mock_db)

    def test_get_publish_post_use_case(self):
        result = get_publish_post_use_case(
            post_repo=self.post_repo,
            media_repo=self.media_repo,
        )
        assert isinstance(result, PublishPostUseCase)

    def test_get_feed_use_case(self):
        result = get_feed_use_case(
            post_repo=self.post_repo,
            like_repo=self.like_repo,
            comment_repo=self.comment_repo,
        )
        assert isinstance(result, GetFeedUseCase)

    def test_get_post_use_case(self):
        result = get_post_use_case(
            post_repo=self.post_repo,
            like_repo=self.like_repo,
            comment_repo=self.comment_repo,
            media_repo=self.media_repo,
        )
        assert isinstance(result, GetPostUseCase)

    def test_get_delete_post_use_case(self):
        result = get_delete_post_use_case(post_repo=self.post_repo)
        assert isinstance(result, DeletePostUseCase)

    def test_get_pin_post_use_case(self):
        result = get_pin_post_use_case(post_repo=self.post_repo)
        assert isinstance(result, PinPostUseCase)

    def test_get_add_comment_use_case(self):
        result = get_add_comment_use_case(
            post_repo=self.post_repo,
            comment_repo=self.comment_repo,
        )
        assert isinstance(result, AddCommentUseCase)

    def test_get_add_like_use_case(self):
        result = get_add_like_use_case(
            post_repo=self.post_repo,
            like_repo=self.like_repo,
        )
        assert isinstance(result, AddLikeUseCase)

    def test_get_remove_like_use_case(self):
        result = get_remove_like_use_case(like_repo=self.like_repo)
        assert isinstance(result, RemoveLikeUseCase)
