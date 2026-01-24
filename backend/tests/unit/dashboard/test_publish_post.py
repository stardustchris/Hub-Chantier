"""Tests unitaires pour PublishPostUseCase."""

import pytest
from unittest.mock import Mock

from modules.dashboard.domain.repositories import PostRepository, PostMediaRepository
from modules.dashboard.application.use_cases import (
    PublishPostUseCase,
    PostContentEmptyError,
)
from modules.dashboard.application.dtos import CreatePostDTO


class TestPublishPostUseCase:
    """Tests pour le use case de publication de post."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Mocks
        self.mock_post_repo = Mock(spec=PostRepository)
        self.mock_media_repo = Mock(spec=PostMediaRepository)

        # Use case à tester
        self.use_case = PublishPostUseCase(
            post_repo=self.mock_post_repo,
            media_repo=self.mock_media_repo,
        )

        # Configuration du mock save
        def save_post(post):
            post.id = 1
            return post

        self.mock_post_repo.save.side_effect = save_post

    def test_publish_post_success(self):
        """Test: publication réussie d'un post."""
        # Arrange
        dto = CreatePostDTO(
            content="Bonjour à tous!",
            target_type="everyone",
        )

        # Act
        result = self.use_case.execute(dto, author_id=1)

        # Assert
        assert result.id == 1
        assert result.author_id == 1
        assert result.content == "Bonjour à tous!"
        assert result.target_type == "everyone"
        assert result.is_urgent is False
        self.mock_post_repo.save.assert_called_once()

    def test_publish_post_empty_content(self):
        """Test: échec si contenu vide."""
        dto = CreatePostDTO(content="", target_type="everyone")

        with pytest.raises(PostContentEmptyError):
            self.use_case.execute(dto, author_id=1)

    def test_publish_post_whitespace_content(self):
        """Test: échec si contenu ne contient que des espaces."""
        dto = CreatePostDTO(content="   ", target_type="everyone")

        with pytest.raises(PostContentEmptyError):
            self.use_case.execute(dto, author_id=1)

    def test_publish_urgent_post(self):
        """Test: publication d'un post urgent (épinglé)."""
        # Arrange
        dto = CreatePostDTO(
            content="Message urgent!",
            target_type="everyone",
            is_urgent=True,
        )

        # Act
        result = self.use_case.execute(dto, author_id=1)

        # Assert
        assert result.is_urgent is True
        assert result.is_pinned is True
        assert result.status == "pinned"

    def test_publish_post_targeting_chantiers(self):
        """Test: publication ciblant des chantiers spécifiques."""
        # Arrange
        dto = CreatePostDTO(
            content="Info chantier",
            target_type="specific_chantiers",
            chantier_ids=[1, 2, 3],
        )

        # Act
        result = self.use_case.execute(dto, author_id=1)

        # Assert
        assert result.target_type == "specific_chantiers"
        assert result.chantier_ids == (1, 2, 3)

    def test_publish_post_targeting_users(self):
        """Test: publication ciblant des utilisateurs spécifiques."""
        # Arrange
        dto = CreatePostDTO(
            content="Message privé",
            target_type="specific_people",
            user_ids=[5, 10],
        )

        # Act
        result = self.use_case.execute(dto, author_id=1)

        # Assert
        assert result.target_type == "specific_people"
        assert result.user_ids == (5, 10)

    def test_publish_post_targeting_chantiers_without_ids(self):
        """Test: échec si ciblage chantiers sans IDs."""
        dto = CreatePostDTO(
            content="Info",
            target_type="specific_chantiers",
            chantier_ids=None,
        )

        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(dto, author_id=1)

        assert "chantier" in str(exc_info.value).lower()

    def test_publish_post_targeting_users_without_ids(self):
        """Test: échec si ciblage utilisateurs sans IDs."""
        dto = CreatePostDTO(
            content="Info",
            target_type="specific_people",
            user_ids=None,
        )

        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(dto, author_id=1)

        assert "utilisateur" in str(exc_info.value).lower()

    def test_publish_post_publishes_event(self):
        """Test: publication d'un event après création."""
        # Arrange
        mock_publisher = Mock()
        use_case_with_events = PublishPostUseCase(
            post_repo=self.mock_post_repo,
            media_repo=self.mock_media_repo,
            event_publisher=mock_publisher,
        )

        dto = CreatePostDTO(content="Test event", target_type="everyone")

        # Act
        use_case_with_events.execute(dto, author_id=1)

        # Assert
        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.post_id == 1
        assert event.author_id == 1
