"""Tests unitaires pour DeletePostUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.dashboard.domain.entities import Post
from modules.dashboard.domain.repositories import PostRepository
from modules.dashboard.application.use_cases.delete_post import (
    DeletePostUseCase,
    NotAuthorizedError,
)
from modules.dashboard.application.use_cases.get_post import PostNotFoundError


class TestDeletePostUseCase:
    """Tests pour le use case de suppression de post."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_post_repo = Mock(spec=PostRepository)
        self.use_case = DeletePostUseCase(post_repo=self.mock_post_repo)

        self.test_post = Post(
            id=1,
            content="Contenu du post test",
            author_id=10,
            created_at=datetime.now(),
        )

    def test_delete_post_by_author_success(self):
        """Test: suppression réussie par l'auteur."""
        self.mock_post_repo.find_by_id.return_value = self.test_post

        result = self.use_case.execute(post_id=1, user_id=10)

        assert result is True
        self.mock_post_repo.find_by_id.assert_called_once_with(1)
        self.mock_post_repo.save.assert_called_once()

    def test_delete_post_by_moderator_success(self):
        """Test: suppression réussie par un modérateur."""
        self.mock_post_repo.find_by_id.return_value = self.test_post

        result = self.use_case.execute(post_id=1, user_id=99, is_moderator=True)

        assert result is True
        self.mock_post_repo.save.assert_called_once()

    def test_delete_post_not_found(self):
        """Test: échec si post non trouvé."""
        self.mock_post_repo.find_by_id.return_value = None

        with pytest.raises(PostNotFoundError) as exc_info:
            self.use_case.execute(post_id=999, user_id=10)

        assert exc_info.value.post_id == 999

    def test_delete_post_unauthorized(self):
        """Test: échec si utilisateur non autorisé."""
        self.mock_post_repo.find_by_id.return_value = self.test_post

        with pytest.raises(NotAuthorizedError):
            self.use_case.execute(post_id=1, user_id=99, is_moderator=False)

    def test_delete_post_publishes_event(self):
        """Test: publication d'un event après suppression."""
        mock_publisher = Mock()
        use_case = DeletePostUseCase(
            post_repo=self.mock_post_repo,
            event_publisher=mock_publisher,
        )

        self.mock_post_repo.find_by_id.return_value = self.test_post

        use_case.execute(post_id=1, user_id=10)

        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.post_id == 1
        assert event.deleted_by_user_id == 10
