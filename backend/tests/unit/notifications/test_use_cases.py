"""Tests unitaires pour les use cases notifications."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.notifications.application.use_cases.delete_notification import DeleteNotificationUseCase
from modules.notifications.application.use_cases.mark_as_read import MarkAsReadUseCase
from modules.notifications.application.use_cases.get_notifications import GetNotificationsUseCase
from modules.notifications.application.use_cases.create_notification import CreateNotificationUseCase
from modules.notifications.domain.value_objects import NotificationType


class TestDeleteNotificationUseCase:
    """Tests de DeleteNotificationUseCase."""

    def test_delete_all_notifications(self):
        """Test suppression toutes notifications."""
        mock_repo = Mock()
        mock_repo.delete_all_for_user.return_value = 5

        use_case = DeleteNotificationUseCase(repository=mock_repo)
        result = use_case.execute(user_id=1, notification_id=None)

        assert result == 5
        mock_repo.delete_all_for_user.assert_called_once_with(1)

    def test_delete_specific_notification_success(self):
        """Test suppression notification spécifique."""
        mock_repo = Mock()
        mock_notification = Mock()
        mock_notification.user_id = 1
        mock_repo.find_by_id.return_value = mock_notification
        mock_repo.delete.return_value = True

        use_case = DeleteNotificationUseCase(repository=mock_repo)
        result = use_case.execute(user_id=1, notification_id=10)

        assert result == 1
        mock_repo.delete.assert_called_once_with(10)

    def test_delete_notification_not_found(self):
        """Test suppression notification inexistante."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        use_case = DeleteNotificationUseCase(repository=mock_repo)
        result = use_case.execute(user_id=1, notification_id=999)

        assert result == 0
        mock_repo.delete.assert_not_called()

    def test_delete_notification_wrong_user(self):
        """Test suppression notification d'un autre utilisateur."""
        mock_repo = Mock()
        mock_notification = Mock()
        mock_notification.user_id = 2  # Appartient à user 2
        mock_repo.find_by_id.return_value = mock_notification

        use_case = DeleteNotificationUseCase(repository=mock_repo)

        with pytest.raises(ValueError, match="ne vous appartient pas"):
            use_case.execute(user_id=1, notification_id=10)


class TestMarkAsReadUseCase:
    """Tests de MarkAsReadUseCase."""

    def test_mark_all_as_read(self):
        """Test marquer toutes comme lues."""
        mock_repo = Mock()
        mock_repo.mark_all_as_read.return_value = 3

        use_case = MarkAsReadUseCase(repository=mock_repo)
        result = use_case.execute(user_id=1, notification_ids=None)

        assert result == 3
        mock_repo.mark_all_as_read.assert_called_once_with(1)

    def test_mark_specific_notifications_as_read(self):
        """Test marquer notifications spécifiques comme lues."""
        mock_repo = Mock()
        mock_notif1 = Mock()
        mock_notif1.user_id = 1
        mock_notif1.is_read = False
        mock_notif2 = Mock()
        mock_notif2.user_id = 1
        mock_notif2.is_read = False

        mock_repo.find_by_id.side_effect = [mock_notif1, mock_notif2]

        use_case = MarkAsReadUseCase(repository=mock_repo)
        result = use_case.execute(user_id=1, notification_ids=[10, 20])

        assert result == 2
        assert mock_repo.save.call_count == 2

    def test_mark_as_read_skip_wrong_user(self):
        """Test ignore les notifications d'autres utilisateurs."""
        mock_repo = Mock()
        mock_notif1 = Mock()
        mock_notif1.user_id = 1
        mock_notif1.is_read = False
        mock_notif2 = Mock()
        mock_notif2.user_id = 2  # Autre utilisateur

        mock_repo.find_by_id.side_effect = [mock_notif1, mock_notif2]

        use_case = MarkAsReadUseCase(repository=mock_repo)
        result = use_case.execute(user_id=1, notification_ids=[10, 20])

        assert result == 1  # Seule la première est marquée

    def test_mark_as_read_skip_already_read(self):
        """Test ignore les notifications déjà lues."""
        mock_repo = Mock()
        mock_notif = Mock()
        mock_notif.user_id = 1
        mock_notif.is_read = True  # Déjà lue

        mock_repo.find_by_id.return_value = mock_notif

        use_case = MarkAsReadUseCase(repository=mock_repo)
        result = use_case.execute(user_id=1, notification_ids=[10])

        assert result == 0
        mock_repo.save.assert_not_called()

    def test_mark_as_read_skip_not_found(self):
        """Test ignore les notifications non trouvées."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        use_case = MarkAsReadUseCase(repository=mock_repo)
        result = use_case.execute(user_id=1, notification_ids=[999])

        assert result == 0


class TestGetNotificationsUseCase:
    """Tests de GetNotificationsUseCase."""

    def test_get_notifications_basic(self):
        """Test récupération basique."""
        mock_repo = Mock()
        now = datetime.now()
        mock_notif = Mock()
        mock_notif.id = 1
        mock_notif.user_id = 1
        mock_notif.type = NotificationType.SYSTEM
        mock_notif.title = "Title"
        mock_notif.message = "Message"
        mock_notif.is_read = False
        mock_notif.read_at = None
        mock_notif.related_post_id = None
        mock_notif.related_comment_id = None
        mock_notif.related_chantier_id = None
        mock_notif.related_document_id = None
        mock_notif.triggered_by_user_id = None
        mock_notif.metadata = {}
        mock_notif.created_at = now

        mock_repo.find_by_user.return_value = [mock_notif]
        mock_repo.count_unread.return_value = 1

        use_case = GetNotificationsUseCase(repository=mock_repo)
        result = use_case.execute(user_id=1)

        assert len(result.notifications) == 1
        assert result.unread_count == 1

    def test_get_notifications_with_pagination(self):
        """Test récupération avec pagination."""
        mock_repo = Mock()
        mock_repo.find_by_user.return_value = []
        mock_repo.count_unread.return_value = 0

        use_case = GetNotificationsUseCase(repository=mock_repo)
        use_case.execute(user_id=1, skip=10, limit=20)

        mock_repo.find_by_user.assert_called_once_with(
            user_id=1,
            unread_only=False,
            skip=10,
            limit=20,
        )

    def test_get_notifications_unread_only(self):
        """Test récupération non lues seulement."""
        mock_repo = Mock()
        mock_repo.find_by_user.return_value = []
        mock_repo.count_unread.return_value = 0

        use_case = GetNotificationsUseCase(repository=mock_repo)
        use_case.execute(user_id=1, unread_only=True)

        mock_repo.find_by_user.assert_called_once_with(
            user_id=1,
            unread_only=True,
            skip=0,
            limit=50,
        )


class TestCreateNotificationUseCase:
    """Tests de CreateNotificationUseCase."""

    def test_create_single_notification(self):
        """Test création notification unique."""
        mock_repo = Mock()
        now = datetime.now()
        mock_saved_notif = Mock()
        mock_saved_notif.id = 1
        mock_saved_notif.user_id = 1
        mock_saved_notif.type = NotificationType.SYSTEM
        mock_saved_notif.title = "Test Title"
        mock_saved_notif.message = "Test message"
        mock_saved_notif.is_read = False
        mock_saved_notif.read_at = None
        mock_saved_notif.related_post_id = None
        mock_saved_notif.related_comment_id = None
        mock_saved_notif.related_chantier_id = None
        mock_saved_notif.related_document_id = None
        mock_saved_notif.triggered_by_user_id = None
        mock_saved_notif.metadata = {}
        mock_saved_notif.created_at = now
        mock_repo.save.return_value = mock_saved_notif

        use_case = CreateNotificationUseCase(repository=mock_repo)
        result = use_case.execute(
            user_id=1,
            notification_type=NotificationType.SYSTEM,
            title="Test Title",
            message="Test message",
        )

        assert result.id == 1
        mock_repo.save.assert_called_once()

    def test_create_notifications_for_multiple_users_batch(self):
        """Test création notifications pour plusieurs utilisateurs via execute_batch."""
        mock_repo = Mock()
        now = datetime.now()

        mock_notif1 = Mock()
        mock_notif1.id = 1
        mock_notif1.user_id = 1
        mock_notif1.type = NotificationType.SIGNALEMENT_CREATED
        mock_notif1.title = "Warning Title"
        mock_notif1.message = "Warning message"
        mock_notif1.is_read = False
        mock_notif1.read_at = None
        mock_notif1.related_post_id = None
        mock_notif1.related_comment_id = None
        mock_notif1.related_chantier_id = None
        mock_notif1.related_document_id = None
        mock_notif1.triggered_by_user_id = None
        mock_notif1.metadata = {}
        mock_notif1.created_at = now

        mock_notif2 = Mock()
        mock_notif2.id = 2
        mock_notif2.user_id = 2
        mock_notif2.type = NotificationType.SIGNALEMENT_CREATED
        mock_notif2.title = "Warning Title"
        mock_notif2.message = "Warning message"
        mock_notif2.is_read = False
        mock_notif2.read_at = None
        mock_notif2.related_post_id = None
        mock_notif2.related_comment_id = None
        mock_notif2.related_chantier_id = None
        mock_notif2.related_document_id = None
        mock_notif2.triggered_by_user_id = None
        mock_notif2.metadata = {}
        mock_notif2.created_at = now

        mock_repo.save_many.return_value = [mock_notif1, mock_notif2]

        use_case = CreateNotificationUseCase(repository=mock_repo)
        result = use_case.execute_batch(
            user_ids=[1, 2],
            notification_type=NotificationType.SIGNALEMENT_CREATED,
            title="Warning Title",
            message="Warning message",
        )

        assert len(result) == 2
        mock_repo.save_many.assert_called_once()

    def test_create_notification_with_related_ids(self):
        """Test création avec IDs liés."""
        mock_repo = Mock()
        now = datetime.now()
        mock_saved_notif = Mock()
        mock_saved_notif.id = 1
        mock_saved_notif.user_id = 1
        mock_saved_notif.type = NotificationType.SYSTEM
        mock_saved_notif.title = "Title"
        mock_saved_notif.message = "Message"
        mock_saved_notif.is_read = False
        mock_saved_notif.read_at = None
        mock_saved_notif.related_post_id = 10
        mock_saved_notif.related_comment_id = None
        mock_saved_notif.related_chantier_id = 20
        mock_saved_notif.related_document_id = None
        mock_saved_notif.triggered_by_user_id = 5
        mock_saved_notif.metadata = {}
        mock_saved_notif.created_at = now
        mock_repo.save.return_value = mock_saved_notif

        use_case = CreateNotificationUseCase(repository=mock_repo)
        result = use_case.execute(
            user_id=1,
            notification_type=NotificationType.SYSTEM,
            title="Title",
            message="Message",
            related_post_id=10,
            related_chantier_id=20,
            triggered_by_user_id=5,
        )

        assert result.id == 1
        # Vérifie que la notification créée a les bons IDs
        call_args = mock_repo.save.call_args[0][0]
        assert call_args.related_post_id == 10
        assert call_args.related_chantier_id == 20
        assert call_args.triggered_by_user_id == 5

    def test_create_notification_with_metadata(self):
        """Test création avec metadata."""
        mock_repo = Mock()
        now = datetime.now()
        mock_saved_notif = Mock()
        mock_saved_notif.id = 1
        mock_saved_notif.user_id = 1
        mock_saved_notif.type = NotificationType.SYSTEM
        mock_saved_notif.title = "Title"
        mock_saved_notif.message = "Message"
        mock_saved_notif.is_read = False
        mock_saved_notif.read_at = None
        mock_saved_notif.related_post_id = None
        mock_saved_notif.related_comment_id = None
        mock_saved_notif.related_chantier_id = None
        mock_saved_notif.related_document_id = None
        mock_saved_notif.triggered_by_user_id = None
        mock_saved_notif.metadata = {"custom": "data"}
        mock_saved_notif.created_at = now
        mock_repo.save.return_value = mock_saved_notif

        use_case = CreateNotificationUseCase(repository=mock_repo)
        result = use_case.execute(
            user_id=1,
            notification_type=NotificationType.SYSTEM,
            title="Title",
            message="Message",
            metadata={"custom": "data"},
        )

        call_args = mock_repo.save.call_args[0][0]
        assert call_args.metadata == {"custom": "data"}
