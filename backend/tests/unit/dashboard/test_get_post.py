"""Tests unitaires pour GetPostUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.dashboard.domain.entities import Post, Comment, PostMedia
from modules.dashboard.domain.repositories import (
    PostRepository,
    LikeRepository,
    CommentRepository,
    PostMediaRepository,
)
from modules.dashboard.application.use_cases.get_post import (
    GetPostUseCase,
    PostNotFoundError,
)


class TestGetPostUseCase:
    """Tests pour le use case de récupération de post."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_post_repo = Mock(spec=PostRepository)
        self.mock_like_repo = Mock(spec=LikeRepository)
        self.mock_comment_repo = Mock(spec=CommentRepository)
        self.mock_media_repo = Mock(spec=PostMediaRepository)

        self.use_case = GetPostUseCase(
            post_repo=self.mock_post_repo,
            like_repo=self.mock_like_repo,
            comment_repo=self.mock_comment_repo,
            media_repo=self.mock_media_repo,
        )

        self.test_post = Post(
            id=1,
            content="Contenu du post test",
            author_id=10,
            created_at=datetime.now(),
        )

    def test_get_post_success(self):
        """Test: récupération réussie d'un post."""
        self.mock_post_repo.find_by_id.return_value = self.test_post
        self.mock_like_repo.count_by_post.return_value = 5
        self.mock_comment_repo.count_by_post.return_value = 3
        self.mock_media_repo.count_by_post.return_value = 2
        self.mock_media_repo.find_by_post.return_value = []
        self.mock_comment_repo.find_by_post.return_value = []
        self.mock_like_repo.find_user_ids_by_post.return_value = [1, 2, 3]

        result = self.use_case.execute(post_id=1, user_id=10)

        assert result.post.id == 1
        assert result.post.content == "Contenu du post test"
        assert result.post.likes_count == 5
        assert result.post.comments_count == 3
        self.mock_post_repo.find_by_id.assert_called_once_with(1)

    def test_get_post_not_found(self):
        """Test: échec si post non trouvé."""
        self.mock_post_repo.find_by_id.return_value = None

        with pytest.raises(PostNotFoundError) as exc_info:
            self.use_case.execute(post_id=999, user_id=10)

        assert exc_info.value.post_id == 999

    def test_get_post_with_comments(self):
        """Test: récupération avec commentaires."""
        comment = Comment(
            id=1,
            post_id=1,
            author_id=20,
            content="Un commentaire",
            created_at=datetime.now(),
        )
        self.mock_post_repo.find_by_id.return_value = self.test_post
        self.mock_like_repo.count_by_post.return_value = 0
        self.mock_comment_repo.count_by_post.return_value = 1
        self.mock_media_repo.count_by_post.return_value = 0
        self.mock_media_repo.find_by_post.return_value = []
        self.mock_comment_repo.find_by_post.return_value = [comment]
        self.mock_like_repo.find_user_ids_by_post.return_value = []

        result = self.use_case.execute(post_id=1, user_id=10)

        assert len(result.comments) == 1

    def test_get_post_minimal_repos(self):
        """Test: récupération avec repos minimaux."""
        use_case = GetPostUseCase(post_repo=self.mock_post_repo)
        self.mock_post_repo.find_by_id.return_value = self.test_post

        result = use_case.execute(post_id=1, user_id=10)

        assert result.post.id == 1
        assert result.post.likes_count == 0
