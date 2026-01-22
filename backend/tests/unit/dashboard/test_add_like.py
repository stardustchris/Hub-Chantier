"""Tests unitaires pour AddLikeUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.dashboard.domain.entities import Post, Like
from modules.dashboard.domain.repositories import PostRepository, LikeRepository
from modules.dashboard.domain.value_objects import PostTargeting
from modules.dashboard.application.use_cases import (
    AddLikeUseCase,
    AlreadyLikedError,
)
from modules.dashboard.application.use_cases.get_post import PostNotFoundError


class TestAddLikeUseCase:
    """Tests pour le use case d'ajout de like."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Mocks
        self.mock_post_repo = Mock(spec=PostRepository)
        self.mock_like_repo = Mock(spec=LikeRepository)

        # Use case à tester
        self.use_case = AddLikeUseCase(
            post_repo=self.mock_post_repo,
            like_repo=self.mock_like_repo,
        )

        # Post de test
        self.test_post = Post(
            id=1,
            author_id=1,
            content="Test post",
            targeting=PostTargeting.everyone(),
        )

        # Configuration du mock save
        def save_like(like):
            like.id = 1
            return like

        self.mock_like_repo.save.side_effect = save_like

    def test_add_like_success(self):
        """Test: ajout de like réussi."""
        # Arrange
        self.mock_post_repo.find_by_id.return_value = self.test_post
        self.mock_like_repo.find_by_post_and_user.return_value = None

        # Act
        result = self.use_case.execute(post_id=1, user_id=5)

        # Assert
        assert result.id == 1
        assert result.post_id == 1
        assert result.user_id == 5
        self.mock_like_repo.save.assert_called_once()

    def test_add_like_post_not_found(self):
        """Test: échec si post n'existe pas."""
        # Arrange
        self.mock_post_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(PostNotFoundError):
            self.use_case.execute(post_id=999, user_id=1)

    def test_add_like_already_liked(self):
        """Test: échec si déjà liké."""
        # Arrange
        self.mock_post_repo.find_by_id.return_value = self.test_post
        existing_like = Like(id=1, post_id=1, user_id=5)
        self.mock_like_repo.find_by_post_and_user.return_value = existing_like

        # Act & Assert
        with pytest.raises(AlreadyLikedError):
            self.use_case.execute(post_id=1, user_id=5)

    def test_add_like_publishes_event(self):
        """Test: publication d'un event après like."""
        # Arrange
        mock_publisher = Mock()
        use_case_with_events = AddLikeUseCase(
            post_repo=self.mock_post_repo,
            like_repo=self.mock_like_repo,
            event_publisher=mock_publisher,
        )

        self.mock_post_repo.find_by_id.return_value = self.test_post
        self.mock_like_repo.find_by_post_and_user.return_value = None

        # Act
        use_case_with_events.execute(post_id=1, user_id=5)

        # Assert
        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.post_id == 1
        assert event.user_id == 5
        assert event.post_author_id == 1  # L'auteur du post
