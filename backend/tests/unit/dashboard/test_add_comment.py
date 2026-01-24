"""Tests unitaires pour AddCommentUseCase."""

import pytest
from unittest.mock import Mock

from modules.dashboard.domain.entities import Post
from modules.dashboard.domain.repositories import PostRepository, CommentRepository
from modules.dashboard.domain.value_objects import PostTargeting
from modules.dashboard.application.use_cases import AddCommentUseCase
from modules.dashboard.application.use_cases.add_comment import CommentContentEmptyError
from modules.dashboard.application.use_cases.get_post import PostNotFoundError
from modules.dashboard.application.dtos import CreateCommentDTO


class TestAddCommentUseCase:
    """Tests pour le use case d'ajout de commentaire."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Mocks
        self.mock_post_repo = Mock(spec=PostRepository)
        self.mock_comment_repo = Mock(spec=CommentRepository)

        # Use case à tester
        self.use_case = AddCommentUseCase(
            post_repo=self.mock_post_repo,
            comment_repo=self.mock_comment_repo,
        )

        # Post de test
        self.test_post = Post(
            id=1,
            author_id=1,
            content="Test post",
            targeting=PostTargeting.everyone(),
        )

        # Configuration du mock save
        def save_comment(comment):
            comment.id = 1
            return comment

        self.mock_comment_repo.save.side_effect = save_comment

    def test_add_comment_success(self):
        """Test: ajout de commentaire réussi."""
        # Arrange
        self.mock_post_repo.find_by_id.return_value = self.test_post
        dto = CreateCommentDTO(post_id=1, content="Super post!")

        # Act
        result = self.use_case.execute(dto, author_id=5)

        # Assert
        assert result.id == 1
        assert result.post_id == 1
        assert result.author_id == 5
        assert result.content == "Super post!"
        self.mock_comment_repo.save.assert_called_once()

    def test_add_comment_post_not_found(self):
        """Test: échec si post n'existe pas."""
        # Arrange
        self.mock_post_repo.find_by_id.return_value = None
        dto = CreateCommentDTO(post_id=999, content="Test")

        # Act & Assert
        with pytest.raises(PostNotFoundError):
            self.use_case.execute(dto, author_id=1)

    def test_add_comment_empty_content(self):
        """Test: échec si contenu vide."""
        # Arrange
        self.mock_post_repo.find_by_id.return_value = self.test_post
        dto = CreateCommentDTO(post_id=1, content="")

        # Act & Assert
        with pytest.raises(CommentContentEmptyError):
            self.use_case.execute(dto, author_id=1)

    def test_add_comment_whitespace_content(self):
        """Test: échec si contenu ne contient que des espaces."""
        # Arrange
        self.mock_post_repo.find_by_id.return_value = self.test_post
        dto = CreateCommentDTO(post_id=1, content="   ")

        # Act & Assert
        with pytest.raises(CommentContentEmptyError):
            self.use_case.execute(dto, author_id=1)

    def test_add_comment_with_emoji(self):
        """Test: commentaire avec emoji (FEED-10)."""
        # Arrange
        self.mock_post_repo.find_by_id.return_value = self.test_post
        dto = CreateCommentDTO(post_id=1, content="Super! 👍🎉")

        # Act
        result = self.use_case.execute(dto, author_id=5)

        # Assert
        assert "👍" in result.content
        assert "🎉" in result.content

    def test_add_comment_publishes_event(self):
        """Test: publication d'un event après commentaire."""
        # Arrange
        mock_publisher = Mock()
        use_case_with_events = AddCommentUseCase(
            post_repo=self.mock_post_repo,
            comment_repo=self.mock_comment_repo,
            event_publisher=mock_publisher,
        )

        self.mock_post_repo.find_by_id.return_value = self.test_post
        dto = CreateCommentDTO(post_id=1, content="Test event")

        # Act
        use_case_with_events.execute(dto, author_id=5)

        # Assert
        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.post_id == 1
        assert event.author_id == 5
        assert event.post_author_id == 1  # L'auteur du post
