"""Tests unitaires pour RemoveLikeUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.dashboard.domain.entities import Like
from modules.dashboard.domain.repositories import LikeRepository
from modules.dashboard.application.use_cases.remove_like import (
    RemoveLikeUseCase,
    LikeNotFoundError,
)


class TestRemoveLikeUseCase:
    """Tests pour le use case de retrait de like."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_like_repo = Mock(spec=LikeRepository)
        self.use_case = RemoveLikeUseCase(like_repo=self.mock_like_repo)

        self.existing_like = Like(
            id=1,
            post_id=10,
            user_id=5,
            created_at=datetime.now(),
        )

    def test_remove_like_success(self):
        """Test: retrait réussi d'un like."""
        self.mock_like_repo.find_by_post_and_user.return_value = self.existing_like

        result = self.use_case.execute(post_id=10, user_id=5)

        assert result is True
        self.mock_like_repo.find_by_post_and_user.assert_called_once_with(10, 5)
        self.mock_like_repo.delete_by_post_and_user.assert_called_once_with(10, 5)

    def test_remove_like_not_found(self):
        """Test: échec si like n'existe pas."""
        self.mock_like_repo.find_by_post_and_user.return_value = None

        with pytest.raises(LikeNotFoundError) as exc_info:
            self.use_case.execute(post_id=10, user_id=5)

        assert exc_info.value.post_id == 10
        assert exc_info.value.user_id == 5

    def test_remove_like_publishes_event(self):
        """Test: publication d'un event après retrait."""
        mock_publisher = Mock()
        use_case = RemoveLikeUseCase(
            like_repo=self.mock_like_repo,
            event_publisher=mock_publisher,
        )

        self.mock_like_repo.find_by_post_and_user.return_value = self.existing_like

        use_case.execute(post_id=10, user_id=5)

        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.post_id == 10
        assert event.user_id == 5
