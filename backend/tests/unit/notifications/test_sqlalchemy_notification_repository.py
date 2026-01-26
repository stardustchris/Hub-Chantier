"""Tests unitaires pour SQLAlchemyNotificationRepository."""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from modules.notifications.infrastructure.persistence.sqlalchemy_notification_repository import (
    SQLAlchemyNotificationRepository,
)
from modules.notifications.domain.value_objects import NotificationType


class TestFindById:
    """Tests de find_by_id."""

    def test_find_by_id_returns_entity_when_found(self):
        """Test retourne l'entité quand trouvée."""
        mock_db = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.user_id = 2
        mock_model.type = "system"
        mock_model.title = "Test Title"
        mock_model.message = "Test message"
        mock_model.is_read = False
        mock_model.read_at = None
        mock_model.related_post_id = None
        mock_model.related_comment_id = None
        mock_model.related_chantier_id = None
        mock_model.related_document_id = None
        mock_model.triggered_by_user_id = None
        mock_model.extra_data = None
        mock_model.created_at = datetime.now()

        mock_db.query.return_value.filter.return_value.first.return_value = mock_model

        repo = SQLAlchemyNotificationRepository(mock_db)
        result = repo.find_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.title == "Test Title"

    def test_find_by_id_returns_none_when_not_found(self):
        """Test retourne None quand non trouvé."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        repo = SQLAlchemyNotificationRepository(mock_db)
        result = repo.find_by_id(999)

        assert result is None


class TestFindByUser:
    """Tests de find_by_user."""

    def test_find_by_user_returns_all_notifications(self):
        """Test retourne toutes les notifications."""
        mock_db = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.user_id = 5
        mock_model.type = "system"
        mock_model.title = "Notif"
        mock_model.message = "Message"
        mock_model.is_read = False
        mock_model.read_at = None
        mock_model.related_post_id = None
        mock_model.related_comment_id = None
        mock_model.related_chantier_id = None
        mock_model.related_document_id = None
        mock_model.triggered_by_user_id = None
        mock_model.extra_data = None
        mock_model.created_at = datetime.now()

        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_model]

        repo = SQLAlchemyNotificationRepository(mock_db)
        result = repo.find_by_user(user_id=5)

        assert len(result) == 1
        assert result[0].user_id == 5

    def test_find_by_user_unread_only(self):
        """Test filtre les non lues seulement."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyNotificationRepository(mock_db)
        repo.find_by_user(user_id=5, unread_only=True)

        # Deux appels à filter: user_id et is_read
        assert mock_query.filter.call_count >= 2

    def test_find_by_user_with_pagination(self):
        """Test avec pagination."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyNotificationRepository(mock_db)
        repo.find_by_user(user_id=5, skip=10, limit=20)

        mock_query.offset.assert_called_with(10)
        mock_query.limit.assert_called_with(20)


class TestCountUnread:
    """Tests de count_unread."""

    def test_count_unread_returns_count(self):
        """Test retourne le nombre de non lues."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 7

        repo = SQLAlchemyNotificationRepository(mock_db)
        result = repo.count_unread(user_id=5)

        assert result == 7


class TestSave:
    """Tests de save."""

    def test_save_new_notification(self):
        """Test sauvegarde nouvelle notification."""
        mock_db = Mock()
        mock_notification = Mock()
        mock_notification.id = None
        mock_notification.user_id = 1
        mock_notification.type = NotificationType.SYSTEM
        mock_notification.title = "New"
        mock_notification.message = "New message"
        mock_notification.is_read = False
        mock_notification.read_at = None
        mock_notification.related_post_id = None
        mock_notification.related_comment_id = None
        mock_notification.related_chantier_id = None
        mock_notification.related_document_id = None
        mock_notification.triggered_by_user_id = None
        mock_notification.metadata = {}
        mock_notification.created_at = datetime.now()

        mock_model = Mock()
        mock_model.id = 1
        mock_model.user_id = 1
        mock_model.type = "system"
        mock_model.title = "New"
        mock_model.message = "New message"
        mock_model.is_read = False
        mock_model.read_at = None
        mock_model.related_post_id = None
        mock_model.related_comment_id = None
        mock_model.related_chantier_id = None
        mock_model.related_document_id = None
        mock_model.triggered_by_user_id = None
        mock_model.extra_data = None
        mock_model.created_at = datetime.now()

        def refresh_side_effect(m):
            pass

        mock_db.refresh.side_effect = refresh_side_effect

        repo = SQLAlchemyNotificationRepository(mock_db)
        # Test _to_model
        model = repo._to_model(mock_notification)

        assert model.title == "New"
        mock_db.add.assert_not_called()  # Pas encore appelé

    def test_save_existing_notification(self):
        """Test mise à jour notification existante."""
        mock_db = Mock()
        mock_notification = Mock()
        mock_notification.id = 1
        mock_notification.user_id = 1
        mock_notification.type = NotificationType.SYSTEM
        mock_notification.title = "Updated"
        mock_notification.message = "Updated message"
        mock_notification.is_read = True
        mock_notification.read_at = datetime.now()
        mock_notification.related_post_id = None
        mock_notification.related_comment_id = None
        mock_notification.related_chantier_id = None
        mock_notification.related_document_id = None
        mock_notification.triggered_by_user_id = None
        mock_notification.metadata = {}
        mock_notification.created_at = datetime.now()

        mock_model = Mock()
        mock_model.id = 1
        mock_model.user_id = 1
        mock_model.type = "system"
        mock_model.title = "Original"
        mock_model.message = "Original"
        mock_model.is_read = False
        mock_model.read_at = None
        mock_model.related_post_id = None
        mock_model.related_comment_id = None
        mock_model.related_chantier_id = None
        mock_model.related_document_id = None
        mock_model.triggered_by_user_id = None
        mock_model.extra_data = None
        mock_model.created_at = datetime.now()

        mock_db.query.return_value.filter.return_value.first.return_value = mock_model

        repo = SQLAlchemyNotificationRepository(mock_db)
        result = repo.save(mock_notification)

        mock_db.commit.assert_called()


class TestSaveMany:
    """Tests de save_many."""

    def test_save_many_notifications(self):
        """Test sauvegarde plusieurs notifications."""
        mock_db = Mock()
        mock_notif1 = Mock()
        mock_notif1.id = None
        mock_notif1.user_id = 1
        mock_notif1.type = NotificationType.SYSTEM
        mock_notif1.title = "Notif 1"
        mock_notif1.message = "Message 1"
        mock_notif1.is_read = False
        mock_notif1.read_at = None
        mock_notif1.related_post_id = None
        mock_notif1.related_comment_id = None
        mock_notif1.related_chantier_id = None
        mock_notif1.related_document_id = None
        mock_notif1.triggered_by_user_id = None
        mock_notif1.metadata = {}
        mock_notif1.created_at = datetime.now()

        mock_notif2 = Mock()
        mock_notif2.id = None
        mock_notif2.user_id = 2
        mock_notif2.type = NotificationType.SIGNALEMENT_CREATED
        mock_notif2.title = "Notif 2"
        mock_notif2.message = "Message 2"
        mock_notif2.is_read = False
        mock_notif2.read_at = None
        mock_notif2.related_post_id = None
        mock_notif2.related_comment_id = None
        mock_notif2.related_chantier_id = None
        mock_notif2.related_document_id = None
        mock_notif2.triggered_by_user_id = None
        mock_notif2.metadata = {}
        mock_notif2.created_at = datetime.now()

        repo = SQLAlchemyNotificationRepository(mock_db)
        repo.save_many([mock_notif1, mock_notif2])

        mock_db.add_all.assert_called_once()
        mock_db.commit.assert_called_once()


class TestDelete:
    """Tests de delete."""

    def test_delete_existing_notification(self):
        """Test suppression notification existante."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.delete.return_value = 1

        repo = SQLAlchemyNotificationRepository(mock_db)
        result = repo.delete(1)

        assert result is True
        mock_db.commit.assert_called_once()

    def test_delete_non_existing_notification(self):
        """Test suppression notification inexistante."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.delete.return_value = 0

        repo = SQLAlchemyNotificationRepository(mock_db)
        result = repo.delete(999)

        assert result is False


class TestDeleteAllForUser:
    """Tests de delete_all_for_user."""

    def test_delete_all_for_user(self):
        """Test suppression toutes notifications d'un utilisateur."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.delete.return_value = 5

        repo = SQLAlchemyNotificationRepository(mock_db)
        result = repo.delete_all_for_user(user_id=1)

        assert result == 5
        mock_db.commit.assert_called_once()


class TestMarkAllAsRead:
    """Tests de mark_all_as_read."""

    def test_mark_all_as_read(self):
        """Test marque toutes comme lues."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.update.return_value = 3

        repo = SQLAlchemyNotificationRepository(mock_db)
        result = repo.mark_all_as_read(user_id=1)

        assert result == 3
        mock_db.commit.assert_called_once()


class TestFindByType:
    """Tests de find_by_type."""

    def test_find_by_type_returns_filtered_notifications(self):
        """Test retourne notifications filtrées par type."""
        mock_db = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.user_id = 5
        mock_model.type = "signalement_created"
        mock_model.title = "Warning"
        mock_model.message = "Warning message"
        mock_model.is_read = False
        mock_model.read_at = None
        mock_model.related_post_id = None
        mock_model.related_comment_id = None
        mock_model.related_chantier_id = None
        mock_model.related_document_id = None
        mock_model.triggered_by_user_id = None
        mock_model.extra_data = None
        mock_model.created_at = datetime.now()

        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_model]

        repo = SQLAlchemyNotificationRepository(mock_db)
        result = repo.find_by_type(
            user_id=5,
            notification_type=NotificationType.SIGNALEMENT_CREATED,
        )

        assert len(result) == 1
        assert result[0].type == NotificationType.SIGNALEMENT_CREATED


class TestToEntity:
    """Tests de _to_entity."""

    def test_to_entity_with_full_data(self):
        """Test conversion avec données complètes."""
        mock_db = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.user_id = 2
        mock_model.type = "system"
        mock_model.title = "Full Title"
        mock_model.message = "Full message"
        mock_model.is_read = True
        mock_model.read_at = datetime.now()
        mock_model.related_post_id = 10
        mock_model.related_comment_id = 20
        mock_model.related_chantier_id = 30
        mock_model.related_document_id = 40
        mock_model.triggered_by_user_id = 50
        mock_model.extra_data = {"key": "value"}
        mock_model.created_at = datetime.now()

        repo = SQLAlchemyNotificationRepository(mock_db)
        result = repo._to_entity(mock_model)

        assert result.id == 1
        assert result.related_post_id == 10
        assert result.metadata == {"key": "value"}

    def test_to_entity_with_minimal_data(self):
        """Test conversion avec données minimales."""
        mock_db = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.user_id = 2
        mock_model.type = "system"
        mock_model.title = "Title"
        mock_model.message = "Message"
        mock_model.is_read = False
        mock_model.read_at = None
        mock_model.related_post_id = None
        mock_model.related_comment_id = None
        mock_model.related_chantier_id = None
        mock_model.related_document_id = None
        mock_model.triggered_by_user_id = None
        mock_model.extra_data = None
        mock_model.created_at = datetime.now()

        repo = SQLAlchemyNotificationRepository(mock_db)
        result = repo._to_entity(mock_model)

        assert result.id == 1
        assert result.metadata == {}


class TestToModel:
    """Tests de _to_model."""

    def test_to_model_with_metadata(self):
        """Test conversion avec metadata."""
        mock_db = Mock()
        mock_entity = Mock()
        mock_entity.id = 1
        mock_entity.user_id = 2
        mock_entity.type = NotificationType.SYSTEM
        mock_entity.title = "Title"
        mock_entity.message = "Message"
        mock_entity.is_read = False
        mock_entity.read_at = None
        mock_entity.related_post_id = None
        mock_entity.related_comment_id = None
        mock_entity.related_chantier_id = None
        mock_entity.related_document_id = None
        mock_entity.triggered_by_user_id = None
        mock_entity.metadata = {"data": "value"}
        mock_entity.created_at = datetime.now()

        repo = SQLAlchemyNotificationRepository(mock_db)
        result = repo._to_model(mock_entity)

        assert result.extra_data == {"data": "value"}

    def test_to_model_without_metadata(self):
        """Test conversion sans metadata."""
        mock_db = Mock()
        mock_entity = Mock()
        mock_entity.id = 1
        mock_entity.user_id = 2
        mock_entity.type = NotificationType.SYSTEM
        mock_entity.title = "Title"
        mock_entity.message = "Message"
        mock_entity.is_read = False
        mock_entity.read_at = None
        mock_entity.related_post_id = None
        mock_entity.related_comment_id = None
        mock_entity.related_chantier_id = None
        mock_entity.related_document_id = None
        mock_entity.triggered_by_user_id = None
        mock_entity.metadata = {}
        mock_entity.created_at = datetime.now()

        repo = SQLAlchemyNotificationRepository(mock_db)
        result = repo._to_model(mock_entity)

        assert result.extra_data is None


class TestUpdateModel:
    """Tests de _update_model."""

    def test_update_model(self):
        """Test mise à jour du modèle."""
        mock_db = Mock()
        mock_model = Mock()
        mock_entity = Mock()
        mock_entity.is_read = True
        mock_entity.read_at = datetime.now()
        mock_entity.title = "Updated Title"
        mock_entity.message = "Updated Message"
        mock_entity.metadata = {"updated": True}

        repo = SQLAlchemyNotificationRepository(mock_db)
        repo._update_model(mock_model, mock_entity)

        assert mock_model.is_read == True
        assert mock_model.title == "Updated Title"
        assert mock_model.extra_data == {"updated": True}

    def test_update_model_empty_metadata(self):
        """Test mise à jour avec metadata vide."""
        mock_db = Mock()
        mock_model = Mock()
        mock_entity = Mock()
        mock_entity.is_read = False
        mock_entity.read_at = None
        mock_entity.title = "Title"
        mock_entity.message = "Message"
        mock_entity.metadata = {}

        repo = SQLAlchemyNotificationRepository(mock_db)
        repo._update_model(mock_model, mock_entity)

        assert mock_model.extra_data is None
