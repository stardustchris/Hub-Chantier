"""Tests unitaires pour l'entité Notification."""

import pytest
from datetime import datetime

from modules.notifications.domain.entities.notification import Notification
from modules.notifications.domain.value_objects import NotificationType


class TestNotificationCreation:
    """Tests de création de notification."""

    def test_create_basic_notification(self):
        """Test création notification basique."""
        notif = Notification(
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Test Title",
            message="Test message",
        )

        assert notif.user_id == 1
        assert notif.type == NotificationType.SYSTEM
        assert notif.title == "Test Title"
        assert notif.message == "Test message"
        assert notif.is_read is False
        assert notif.id is None

    def test_create_notification_with_all_fields(self):
        """Test création avec tous les champs."""
        now = datetime.now()
        notif = Notification(
            id=1,
            user_id=2,
            type=NotificationType.SIGNALEMENT_CREATED,
            title="Warning",
            message="Warning message",
            is_read=True,
            read_at=now,
            related_post_id=10,
            related_comment_id=20,
            related_chantier_id=30,
            related_document_id=40,
            triggered_by_user_id=50,
            metadata={"key": "value"},
            created_at=now,
        )

        assert notif.id == 1
        assert notif.related_post_id == 10
        assert notif.metadata == {"key": "value"}

    def test_create_notification_title_trimmed(self):
        """Test que le titre est trimé."""
        notif = Notification(
            user_id=1,
            type=NotificationType.SYSTEM,
            title="  Title with spaces  ",
            message="Message",
        )

        assert notif.title == "Title with spaces"

    def test_create_notification_message_trimmed(self):
        """Test que le message est trimé."""
        notif = Notification(
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Title",
            message="  Message with spaces  ",
        )

        assert notif.message == "Message with spaces"

    def test_create_notification_empty_title_raises_error(self):
        """Test erreur si titre vide."""
        with pytest.raises(ValueError, match="titre ne peut pas etre vide"):
            Notification(
                user_id=1,
                type=NotificationType.SYSTEM,
                title="",
                message="Message",
            )

    def test_create_notification_whitespace_title_raises_error(self):
        """Test erreur si titre uniquement espaces."""
        with pytest.raises(ValueError, match="titre ne peut pas etre vide"):
            Notification(
                user_id=1,
                type=NotificationType.SYSTEM,
                title="   ",
                message="Message",
            )

    def test_create_notification_empty_message_raises_error(self):
        """Test erreur si message vide."""
        with pytest.raises(ValueError, match="message ne peut pas etre vide"):
            Notification(
                user_id=1,
                type=NotificationType.SYSTEM,
                title="Title",
                message="",
            )

    def test_create_notification_whitespace_message_raises_error(self):
        """Test erreur si message uniquement espaces."""
        with pytest.raises(ValueError, match="message ne peut pas etre vide"):
            Notification(
                user_id=1,
                type=NotificationType.SYSTEM,
                title="Title",
                message="   ",
            )


class TestMarkAsRead:
    """Tests de mark_as_read."""

    def test_mark_as_read_unread_notification(self):
        """Test marquer comme lue une notification non lue."""
        notif = Notification(
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Title",
            message="Message",
        )

        notif.mark_as_read()

        assert notif.is_read is True
        assert notif.read_at is not None

    def test_mark_as_read_already_read_notification(self):
        """Test marquer comme lue une notification déjà lue."""
        notif = Notification(
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Title",
            message="Message",
            is_read=True,
            read_at=datetime.now(),
        )
        original_read_at = notif.read_at

        notif.mark_as_read()

        # Ne change pas read_at si déjà lue
        assert notif.read_at == original_read_at


class TestMarkAsUnread:
    """Tests de mark_as_unread."""

    def test_mark_as_unread(self):
        """Test marquer comme non lue."""
        notif = Notification(
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Title",
            message="Message",
            is_read=True,
            read_at=datetime.now(),
        )

        notif.mark_as_unread()

        assert notif.is_read is False
        assert notif.read_at is None


class TestIsUnread:
    """Tests de is_unread."""

    def test_is_unread_true_when_not_read(self):
        """Test is_unread retourne True si non lue."""
        notif = Notification(
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Title",
            message="Message",
        )

        assert notif.is_unread is True

    def test_is_unread_false_when_read(self):
        """Test is_unread retourne False si lue."""
        notif = Notification(
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Title",
            message="Message",
            is_read=True,
        )

        assert notif.is_unread is False


class TestEquality:
    """Tests d'égalité."""

    def test_equal_notifications_same_id(self):
        """Test égalité si même ID."""
        notif1 = Notification(
            id=1,
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Title 1",
            message="Message 1",
        )
        notif2 = Notification(
            id=1,
            user_id=2,
            type=NotificationType.SIGNALEMENT_CREATED,
            title="Title 2",
            message="Message 2",
        )

        assert notif1 == notif2

    def test_not_equal_different_ids(self):
        """Test inégalité si IDs différents."""
        notif1 = Notification(
            id=1,
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Title",
            message="Message",
        )
        notif2 = Notification(
            id=2,
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Title",
            message="Message",
        )

        assert notif1 != notif2

    def test_not_equal_none_ids(self):
        """Test inégalité si un ID est None."""
        notif1 = Notification(
            id=1,
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Title",
            message="Message",
        )
        notif2 = Notification(
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Title",
            message="Message",
        )

        assert notif1 != notif2

    def test_not_equal_both_none_ids(self):
        """Test inégalité si les deux IDs sont None."""
        notif1 = Notification(
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Title",
            message="Message",
        )
        notif2 = Notification(
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Title",
            message="Message",
        )

        assert notif1 != notif2

    def test_not_equal_different_type(self):
        """Test inégalité avec type différent."""
        notif = Notification(
            id=1,
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Title",
            message="Message",
        )

        assert notif != "not a notification"


class TestHash:
    """Tests de hash."""

    def test_hash_with_id(self):
        """Test hash avec ID."""
        notif = Notification(
            id=42,
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Title",
            message="Message",
        )

        assert hash(notif) == hash(42)

    def test_hash_without_id(self):
        """Test hash sans ID."""
        notif = Notification(
            user_id=1,
            type=NotificationType.SYSTEM,
            title="Title",
            message="Message",
        )

        # Hash basé sur l'identité de l'objet
        assert hash(notif) is not None
