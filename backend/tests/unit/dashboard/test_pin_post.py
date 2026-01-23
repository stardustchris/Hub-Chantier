"""Tests unitaires pour PinPostUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.dashboard.domain.entities import Post
from modules.dashboard.domain.repositories import PostRepository
from modules.dashboard.application.use_cases.pin_post import PinPostUseCase
from modules.dashboard.application.use_cases.get_post import PostNotFoundError
from modules.dashboard.application.use_cases.delete_post import NotAuthorizedError


class TestPinPostUseCase:
    """Tests pour le use case d'épinglage de post."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_post_repo = Mock(spec=PostRepository)
        self.use_case = PinPostUseCase(post_repo=self.mock_post_repo)

        self.test_post = Post(
            id=1,
            content="Contenu du post test",
            author_id=10,
            created_at=datetime.now(),
        )

    def test_pin_post_by_author_success(self):
        """Test: épinglage réussi par l'auteur."""
        self.mock_post_repo.find_by_id.return_value = self.test_post

        result = self.use_case.execute(post_id=1, user_id=10)

        assert result is True
        self.mock_post_repo.save.assert_called_once()

    def test_pin_post_by_moderator_success(self):
        """Test: épinglage réussi par un modérateur."""
        self.mock_post_repo.find_by_id.return_value = self.test_post

        result = self.use_case.execute(post_id=1, user_id=99, is_moderator=True)

        assert result is True

    def test_pin_post_not_found(self):
        """Test: échec si post non trouvé."""
        self.mock_post_repo.find_by_id.return_value = None

        with pytest.raises(PostNotFoundError):
            self.use_case.execute(post_id=999, user_id=10)

    def test_pin_post_unauthorized(self):
        """Test: échec si utilisateur non autorisé."""
        self.mock_post_repo.find_by_id.return_value = self.test_post

        with pytest.raises(NotAuthorizedError):
            self.use_case.execute(post_id=1, user_id=99, is_moderator=False)

    def test_pin_post_with_duration(self):
        """Test: épinglage avec durée personnalisée."""
        self.mock_post_repo.find_by_id.return_value = self.test_post

        result = self.use_case.execute(post_id=1, user_id=10, duration_hours=24)

        assert result is True

    def test_pin_post_publishes_event(self):
        """Test: publication d'un event après épinglage."""
        mock_publisher = Mock()
        use_case = PinPostUseCase(
            post_repo=self.mock_post_repo,
            event_publisher=mock_publisher,
        )

        self.mock_post_repo.find_by_id.return_value = self.test_post

        use_case.execute(post_id=1, user_id=10)

        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.post_id == 1

    def test_unpin_post_success(self):
        """Test: désépinglage réussi."""
        self.mock_post_repo.find_by_id.return_value = self.test_post

        result = self.use_case.unpin(post_id=1, user_id=10)

        assert result is True
        self.mock_post_repo.save.assert_called_once()

    def test_unpin_post_not_found(self):
        """Test: échec désépinglage si post non trouvé."""
        self.mock_post_repo.find_by_id.return_value = None

        with pytest.raises(PostNotFoundError):
            self.use_case.unpin(post_id=999, user_id=10)

    def test_unpin_post_unauthorized(self):
        """Test: échec désépinglage si non autorisé."""
        self.mock_post_repo.find_by_id.return_value = self.test_post

        with pytest.raises(NotAuthorizedError):
            self.use_case.unpin(post_id=1, user_id=99, is_moderator=False)
