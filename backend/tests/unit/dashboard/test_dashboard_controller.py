"""Tests unitaires pour DashboardController."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from modules.dashboard.adapters.controllers.dashboard_controller import DashboardController


class TestGetFeed:
    """Tests de get_feed."""

    def test_get_feed_basic(self):
        """Test récupération du feed basique."""
        mock_post_repo = Mock()
        mock_like_repo = Mock()
        mock_comment_repo = Mock()
        mock_media_repo = Mock()

        # Mock le use case
        with patch(
            "modules.dashboard.adapters.controllers.dashboard_controller.GetFeedUseCase"
        ) as MockUseCase:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = {
                "posts": [],
                "total": 0,
                "has_more": False,
            }
            MockUseCase.return_value = mock_use_case

            controller = DashboardController(
                post_repo=mock_post_repo,
                like_repo=mock_like_repo,
                comment_repo=mock_comment_repo,
                media_repo=mock_media_repo,
            )

            result = controller.get_feed(user_id=1)

            assert result["posts"] == []
            assert result["total"] == 0
            mock_use_case.execute.assert_called_once()

    def test_get_feed_with_filters(self):
        """Test récupération du feed avec filtres."""
        mock_post_repo = Mock()
        mock_like_repo = Mock()
        mock_comment_repo = Mock()
        mock_media_repo = Mock()

        with patch(
            "modules.dashboard.adapters.controllers.dashboard_controller.GetFeedUseCase"
        ) as MockUseCase:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = {"posts": [], "total": 0}
            MockUseCase.return_value = mock_use_case

            controller = DashboardController(
                post_repo=mock_post_repo,
                like_repo=mock_like_repo,
                comment_repo=mock_comment_repo,
                media_repo=mock_media_repo,
            )

            controller.get_feed(
                user_id=1,
                user_chantier_ids=[1, 2, 3],
                limit=50,
                offset=10,
                include_archived=True,
            )

            mock_use_case.execute.assert_called_once_with(
                user_id=1,
                user_chantier_ids=[1, 2, 3],
                limit=50,
                offset=10,
                include_archived=True,
            )


class TestCreatePost:
    """Tests de create_post."""

    def test_create_post_basic(self):
        """Test création d'un post basique."""
        mock_post_repo = Mock()
        mock_like_repo = Mock()
        mock_comment_repo = Mock()
        mock_media_repo = Mock()

        with patch(
            "modules.dashboard.adapters.controllers.dashboard_controller.PublishPostUseCase"
        ) as MockUseCase:
            mock_post_dto = Mock()
            mock_post_dto.id = 1
            mock_post_dto.content = "Test post"
            mock_use_case = Mock()
            mock_use_case.execute.return_value = mock_post_dto
            MockUseCase.return_value = mock_use_case

            controller = DashboardController(
                post_repo=mock_post_repo,
                like_repo=mock_like_repo,
                comment_repo=mock_comment_repo,
                media_repo=mock_media_repo,
            )

            result = controller.create_post(
                content="Test post",
                author_id=1,
            )

            assert result.content == "Test post"
            mock_use_case.execute.assert_called_once()

    def test_create_post_with_targeting(self):
        """Test création d'un post avec ciblage."""
        mock_post_repo = Mock()
        mock_like_repo = Mock()
        mock_comment_repo = Mock()
        mock_media_repo = Mock()

        with patch(
            "modules.dashboard.adapters.controllers.dashboard_controller.PublishPostUseCase"
        ) as MockUseCase:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = Mock()
            MockUseCase.return_value = mock_use_case

            controller = DashboardController(
                post_repo=mock_post_repo,
                like_repo=mock_like_repo,
                comment_repo=mock_comment_repo,
                media_repo=mock_media_repo,
            )

            controller.create_post(
                content="Urgent post",
                author_id=1,
                target_type="specific_chantiers",
                chantier_ids=[1, 2],
                is_urgent=True,
            )

            call_args = mock_use_case.execute.call_args
            dto = call_args[0][0]
            assert dto.content == "Urgent post"
            assert dto.target_type == "specific_chantiers"
            assert dto.chantier_ids == [1, 2]
            assert dto.is_urgent is True

    def test_create_post_with_user_targeting(self):
        """Test création d'un post ciblant des utilisateurs."""
        mock_post_repo = Mock()
        mock_like_repo = Mock()
        mock_comment_repo = Mock()
        mock_media_repo = Mock()

        with patch(
            "modules.dashboard.adapters.controllers.dashboard_controller.PublishPostUseCase"
        ) as MockUseCase:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = Mock()
            MockUseCase.return_value = mock_use_case

            controller = DashboardController(
                post_repo=mock_post_repo,
                like_repo=mock_like_repo,
                comment_repo=mock_comment_repo,
                media_repo=mock_media_repo,
            )

            controller.create_post(
                content="Private post",
                author_id=1,
                target_type="specific_people",
                user_ids=[5, 6, 7],
            )

            call_args = mock_use_case.execute.call_args
            dto = call_args[0][0]
            assert dto.target_type == "specific_people"
            assert dto.user_ids == [5, 6, 7]


class TestGetPost:
    """Tests de get_post."""

    def test_get_post_success(self):
        """Test récupération d'un post."""
        mock_post_repo = Mock()
        mock_like_repo = Mock()
        mock_comment_repo = Mock()
        mock_media_repo = Mock()

        with patch(
            "modules.dashboard.adapters.controllers.dashboard_controller.GetPostUseCase"
        ) as MockUseCase:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = {
                "post": Mock(),
                "medias": [],
                "comments": [],
                "likes_count": 5,
            }
            MockUseCase.return_value = mock_use_case

            controller = DashboardController(
                post_repo=mock_post_repo,
                like_repo=mock_like_repo,
                comment_repo=mock_comment_repo,
                media_repo=mock_media_repo,
            )

            result = controller.get_post(post_id=1, user_id=2)

            assert result["likes_count"] == 5
            mock_use_case.execute.assert_called_once_with(post_id=1, user_id=2)


class TestDeletePost:
    """Tests de delete_post."""

    def test_delete_post_success(self):
        """Test suppression d'un post."""
        mock_post_repo = Mock()
        mock_like_repo = Mock()
        mock_comment_repo = Mock()
        mock_media_repo = Mock()

        with patch(
            "modules.dashboard.adapters.controllers.dashboard_controller.DeletePostUseCase"
        ) as MockUseCase:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = None
            MockUseCase.return_value = mock_use_case

            controller = DashboardController(
                post_repo=mock_post_repo,
                like_repo=mock_like_repo,
                comment_repo=mock_comment_repo,
                media_repo=mock_media_repo,
            )

            result = controller.delete_post(post_id=1, user_id=2)

            assert result is True
            mock_use_case.execute.assert_called_once_with(
                post_id=1, user_id=2, is_moderator=False
            )

    def test_delete_post_as_moderator(self):
        """Test suppression d'un post par modérateur."""
        mock_post_repo = Mock()
        mock_like_repo = Mock()
        mock_comment_repo = Mock()
        mock_media_repo = Mock()

        with patch(
            "modules.dashboard.adapters.controllers.dashboard_controller.DeletePostUseCase"
        ) as MockUseCase:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = None
            MockUseCase.return_value = mock_use_case

            controller = DashboardController(
                post_repo=mock_post_repo,
                like_repo=mock_like_repo,
                comment_repo=mock_comment_repo,
                media_repo=mock_media_repo,
            )

            result = controller.delete_post(post_id=1, user_id=2, is_moderator=True)

            assert result is True
            mock_use_case.execute.assert_called_once_with(
                post_id=1, user_id=2, is_moderator=True
            )


class TestAddComment:
    """Tests de add_comment."""

    def test_add_comment_success(self):
        """Test ajout d'un commentaire."""
        mock_post_repo = Mock()
        mock_like_repo = Mock()
        mock_comment_repo = Mock()
        mock_media_repo = Mock()

        with patch(
            "modules.dashboard.adapters.controllers.dashboard_controller.AddCommentUseCase"
        ) as MockUseCase:
            mock_comment_dto = {"id": 1, "content": "Great post!"}
            mock_use_case = Mock()
            mock_use_case.execute.return_value = mock_comment_dto
            MockUseCase.return_value = mock_use_case

            controller = DashboardController(
                post_repo=mock_post_repo,
                like_repo=mock_like_repo,
                comment_repo=mock_comment_repo,
                media_repo=mock_media_repo,
            )

            result = controller.add_comment(
                post_id=1,
                content="Great post!",
                author_id=2,
            )

            assert result["content"] == "Great post!"
            call_args = mock_use_case.execute.call_args
            dto = call_args[0][0]
            assert dto.post_id == 1
            assert dto.content == "Great post!"


class TestAddLike:
    """Tests de add_like."""

    def test_add_like_success(self):
        """Test ajout d'un like."""
        mock_post_repo = Mock()
        mock_like_repo = Mock()
        mock_comment_repo = Mock()
        mock_media_repo = Mock()

        with patch(
            "modules.dashboard.adapters.controllers.dashboard_controller.AddLikeUseCase"
        ) as MockUseCase:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = None
            MockUseCase.return_value = mock_use_case

            controller = DashboardController(
                post_repo=mock_post_repo,
                like_repo=mock_like_repo,
                comment_repo=mock_comment_repo,
                media_repo=mock_media_repo,
            )

            result = controller.add_like(post_id=1, user_id=2)

            assert result is True
            mock_use_case.execute.assert_called_once_with(post_id=1, user_id=2)


class TestRemoveLike:
    """Tests de remove_like."""

    def test_remove_like_success(self):
        """Test suppression d'un like."""
        mock_post_repo = Mock()
        mock_like_repo = Mock()
        mock_comment_repo = Mock()
        mock_media_repo = Mock()

        with patch(
            "modules.dashboard.adapters.controllers.dashboard_controller.RemoveLikeUseCase"
        ) as MockUseCase:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = None
            MockUseCase.return_value = mock_use_case

            controller = DashboardController(
                post_repo=mock_post_repo,
                like_repo=mock_like_repo,
                comment_repo=mock_comment_repo,
                media_repo=mock_media_repo,
            )

            result = controller.remove_like(post_id=1, user_id=2)

            assert result is True
            mock_use_case.execute.assert_called_once_with(post_id=1, user_id=2)


class TestControllerInstantiation:
    """Tests d'instanciation du controller."""

    def test_controller_is_dataclass(self):
        """Test que le controller est une dataclass."""
        mock_post_repo = Mock()
        mock_like_repo = Mock()
        mock_comment_repo = Mock()
        mock_media_repo = Mock()

        controller = DashboardController(
            post_repo=mock_post_repo,
            like_repo=mock_like_repo,
            comment_repo=mock_comment_repo,
            media_repo=mock_media_repo,
        )

        assert controller.post_repo == mock_post_repo
        assert controller.like_repo == mock_like_repo
        assert controller.comment_repo == mock_comment_repo
        assert controller.media_repo == mock_media_repo
