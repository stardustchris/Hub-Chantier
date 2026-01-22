"""Tests unitaires pour GetFeedUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.dashboard.domain.entities import Post
from modules.dashboard.domain.repositories import PostRepository, LikeRepository, CommentRepository
from modules.dashboard.domain.value_objects import PostTargeting, PostStatus
from modules.dashboard.application.use_cases import GetFeedUseCase


class TestGetFeedUseCase:
    """Tests pour le use case de récupération du feed."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Mocks
        self.mock_post_repo = Mock(spec=PostRepository)
        self.mock_like_repo = Mock(spec=LikeRepository)
        self.mock_comment_repo = Mock(spec=CommentRepository)

        # Use case à tester
        self.use_case = GetFeedUseCase(
            post_repo=self.mock_post_repo,
            like_repo=self.mock_like_repo,
            comment_repo=self.mock_comment_repo,
        )

        # Posts de test
        self.test_posts = [
            Post(
                id=1,
                author_id=1,
                content="Premier post",
                targeting=PostTargeting.everyone(),
                created_at=datetime(2026, 1, 22, 10, 0),
            ),
            Post(
                id=2,
                author_id=2,
                content="Deuxième post",
                targeting=PostTargeting.everyone(),
                created_at=datetime(2026, 1, 22, 9, 0),
            ),
        ]

    def test_get_feed_success(self):
        """Test: récupération du feed réussie."""
        # Arrange
        self.mock_post_repo.find_feed.return_value = self.test_posts
        self.mock_like_repo.count_by_post.return_value = 5
        self.mock_comment_repo.count_by_post.return_value = 2

        # Act
        result = self.use_case.execute(user_id=1, limit=20, offset=0)

        # Assert
        assert len(result.posts) == 2
        assert result.posts[0].id == 1
        assert result.posts[0].likes_count == 5
        assert result.posts[0].comments_count == 2
        assert result.offset == 0
        assert result.limit == 20

    def test_get_feed_empty(self):
        """Test: feed vide."""
        # Arrange
        self.mock_post_repo.find_feed.return_value = []

        # Act
        result = self.use_case.execute(user_id=1)

        # Assert
        assert len(result.posts) == 0
        assert result.total == 0

    def test_get_feed_with_chantiers(self):
        """Test: feed filtré par chantiers."""
        # Arrange
        self.mock_post_repo.find_feed.return_value = self.test_posts

        # Act
        result = self.use_case.execute(
            user_id=1,
            user_chantier_ids=[1, 2],
        )

        # Assert
        self.mock_post_repo.find_feed.assert_called_once_with(
            user_id=1,
            user_chantier_ids=[1, 2],
            limit=20,
            offset=0,
            include_archived=False,
        )

    def test_get_feed_pagination(self):
        """Test: pagination du feed."""
        # Arrange
        self.mock_post_repo.find_feed.return_value = self.test_posts

        # Act
        result = self.use_case.execute(
            user_id=1,
            limit=10,
            offset=20,
        )

        # Assert
        self.mock_post_repo.find_feed.assert_called_once_with(
            user_id=1,
            user_chantier_ids=None,
            limit=10,
            offset=20,
            include_archived=False,
        )
        assert result.offset == 20
        assert result.limit == 10

    def test_get_feed_include_archived(self):
        """Test: feed incluant les posts archivés."""
        # Arrange
        self.mock_post_repo.find_feed.return_value = []

        # Act
        result = self.use_case.execute(
            user_id=1,
            include_archived=True,
        )

        # Assert
        self.mock_post_repo.find_feed.assert_called_once_with(
            user_id=1,
            user_chantier_ids=None,
            limit=20,
            offset=0,
            include_archived=True,
        )

    def test_get_feed_has_next(self):
        """Test: indication qu'il y a une page suivante."""
        # Arrange - Retourne exactement 'limit' posts
        posts_full_page = [
            Post(
                id=i,
                author_id=1,
                content=f"Post {i}",
                targeting=PostTargeting.everyone(),
            )
            for i in range(20)
        ]
        self.mock_post_repo.find_feed.return_value = posts_full_page

        # Act
        result = self.use_case.execute(user_id=1, limit=20)

        # Assert
        assert result.has_next is True

    def test_get_feed_no_next(self):
        """Test: pas de page suivante."""
        # Arrange - Retourne moins que 'limit' posts
        self.mock_post_repo.find_feed.return_value = self.test_posts  # 2 posts

        # Act
        result = self.use_case.execute(user_id=1, limit=20)

        # Assert
        assert result.has_next is False
