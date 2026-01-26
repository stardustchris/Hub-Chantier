"""Tests unitaires pour les event handlers de notifications."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from modules.notifications.infrastructure.event_handlers import (
    parse_mentions,
    register_notification_handlers,
)


class TestParseMentions:
    """Tests pour parse_mentions."""

    def test_parse_single_mention(self):
        """Test parsing d'une seule mention."""
        result = parse_mentions("Hello @john!")

        assert result == ["john"]

    def test_parse_multiple_mentions(self):
        """Test parsing de plusieurs mentions."""
        result = parse_mentions("@alice et @bob sont invités")

        assert result == ["alice", "bob"]

    def test_parse_mentions_with_underscore(self):
        """Test parsing de mentions avec underscore."""
        result = parse_mentions("Merci @jean_dupont")

        assert result == ["jean_dupont"]

    def test_parse_mentions_with_hyphen(self):
        """Test parsing de mentions avec tiret."""
        result = parse_mentions("Bonjour @marie-claire")

        assert result == ["marie-claire"]

    def test_parse_mentions_with_numbers(self):
        """Test parsing de mentions avec chiffres."""
        result = parse_mentions("Ping @user123")

        assert result == ["user123"]

    def test_parse_no_mentions(self):
        """Test texte sans mentions."""
        result = parse_mentions("Un commentaire normal sans mention")

        assert result == []

    def test_parse_mentions_at_start(self):
        """Test mention au début du texte."""
        result = parse_mentions("@admin voici le rapport")

        assert result == ["admin"]

    def test_parse_mentions_at_end(self):
        """Test mention à la fin du texte."""
        result = parse_mentions("Merci @supervisor")

        assert result == ["supervisor"]

    def test_parse_consecutive_mentions(self):
        """Test mentions consécutives."""
        result = parse_mentions("@alice @bob @charlie")

        assert result == ["alice", "bob", "charlie"]

    def test_parse_mixed_content(self):
        """Test contenu mixte."""
        result = parse_mentions("Hello @world! This is @test123 speaking.")

        assert result == ["world", "test123"]

    def test_parse_empty_string(self):
        """Test chaîne vide."""
        result = parse_mentions("")

        assert result == []

    def test_parse_only_at_symbol(self):
        """Test symbole @ seul."""
        result = parse_mentions("@")

        assert result == []

    def test_parse_at_with_space(self):
        """Test @ suivi d'espace."""
        result = parse_mentions("@ hello")

        assert result == []


class TestRegisterNotificationHandlers:
    """Tests pour register_notification_handlers."""

    def test_register_handlers_logs_message(self):
        """Test que la fonction log un message."""
        with patch("modules.notifications.infrastructure.event_handlers.logger") as mock_logger:
            register_notification_handlers()

            mock_logger.info.assert_called_with("Notification event handlers registered")

    def test_register_handlers_no_exception(self):
        """Test que la fonction ne lève pas d'exception."""
        # Ne devrait pas lever d'exception
        register_notification_handlers()


class TestHandleCommentAddedIntegration:
    """Tests d'intégration pour handle_comment_added."""

    @patch("modules.notifications.infrastructure.event_handlers.SessionLocal")
    @patch("modules.notifications.infrastructure.event_handlers.get_user_name")
    @patch("modules.notifications.infrastructure.event_handlers.get_comment_content")
    @patch("modules.notifications.infrastructure.event_handlers.SQLAlchemyNotificationRepository")
    def test_handle_comment_notifies_post_author(
        self, mock_repo_class, mock_get_content, mock_get_name, mock_session
    ):
        """Test notification à l'auteur du post."""
        from modules.notifications.infrastructure.event_handlers import handle_comment_added
        from modules.dashboard.domain.events import CommentAddedEvent

        mock_db = Mock()
        mock_session.return_value = mock_db
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_get_name.return_value = "Jean Dupont"
        mock_get_content.return_value = "Commentaire simple"

        event = CommentAddedEvent(
            comment_id=1,
            post_id=10,
            author_id=2,
            post_author_id=3,  # Différent de author_id
            timestamp=datetime.now(),
        )

        handle_comment_added(event)

        mock_repo.save.assert_called()
        mock_db.close.assert_called_once()

    @patch("modules.notifications.infrastructure.event_handlers.SessionLocal")
    @patch("modules.notifications.infrastructure.event_handlers.get_user_name")
    @patch("modules.notifications.infrastructure.event_handlers.get_comment_content")
    @patch("modules.notifications.infrastructure.event_handlers.SQLAlchemyNotificationRepository")
    def test_handle_comment_no_notification_for_own_post(
        self, mock_repo_class, mock_get_content, mock_get_name, mock_session
    ):
        """Test pas de notification si on commente son propre post."""
        from modules.notifications.infrastructure.event_handlers import handle_comment_added
        from modules.dashboard.domain.events import CommentAddedEvent

        mock_db = Mock()
        mock_session.return_value = mock_db
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_get_name.return_value = "Jean Dupont"
        mock_get_content.return_value = "Commentaire sans mention"

        event = CommentAddedEvent(
            comment_id=1,
            post_id=10,
            author_id=2,
            post_author_id=2,  # Même que author_id
            timestamp=datetime.now(),
        )

        handle_comment_added(event)

        # Pas de notification car pas de mention et auteur = post_author
        mock_db.close.assert_called_once()

    @patch("modules.notifications.infrastructure.event_handlers.SessionLocal")
    @patch("modules.notifications.infrastructure.event_handlers.get_user_name")
    @patch("modules.notifications.infrastructure.event_handlers.get_comment_content")
    @patch("modules.notifications.infrastructure.event_handlers.SQLAlchemyNotificationRepository")
    def test_handle_comment_error_handling(
        self, mock_repo_class, mock_get_content, mock_get_name, mock_session
    ):
        """Test gestion des erreurs."""
        from modules.notifications.infrastructure.event_handlers import handle_comment_added
        from modules.dashboard.domain.events import CommentAddedEvent

        mock_db = Mock()
        mock_session.return_value = mock_db
        mock_repo_class.side_effect = Exception("DB Error")

        event = CommentAddedEvent(
            comment_id=1,
            post_id=10,
            author_id=2,
            post_author_id=3,
            timestamp=datetime.now(),
        )

        # Ne doit pas lever d'exception
        handle_comment_added(event)

        mock_db.close.assert_called_once()


class TestHandleLikeAddedIntegration:
    """Tests d'intégration pour handle_like_added."""

    @patch("modules.notifications.infrastructure.event_handlers.SessionLocal")
    @patch("modules.notifications.infrastructure.event_handlers.get_user_name")
    @patch("modules.notifications.infrastructure.event_handlers.SQLAlchemyNotificationRepository")
    def test_handle_like_notifies_post_author(
        self, mock_repo_class, mock_get_name, mock_session
    ):
        """Test notification à l'auteur du post."""
        from modules.notifications.infrastructure.event_handlers import handle_like_added
        from modules.dashboard.domain.events import LikeAddedEvent

        mock_db = Mock()
        mock_session.return_value = mock_db
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_get_name.return_value = "Alice Martin"

        event = LikeAddedEvent(
            like_id=1,
            post_id=10,
            user_id=2,
            post_author_id=3,  # Différent de user_id
            timestamp=datetime.now(),
        )

        handle_like_added(event)

        mock_repo.save.assert_called_once()
        mock_db.close.assert_called_once()

    def test_handle_like_no_notification_for_own_post(self):
        """Test pas de notification si on like son propre post."""
        from modules.notifications.infrastructure.event_handlers import handle_like_added
        from modules.dashboard.domain.events import LikeAddedEvent

        event = LikeAddedEvent(
            like_id=1,
            post_id=10,
            user_id=2,
            post_author_id=2,  # Même que user_id
            timestamp=datetime.now(),
        )

        # Ne doit pas appeler SessionLocal car retourne immédiatement
        with patch("modules.notifications.infrastructure.event_handlers.SessionLocal") as mock_session:
            handle_like_added(event)
            mock_session.assert_not_called()

    @patch("modules.notifications.infrastructure.event_handlers.SessionLocal")
    @patch("modules.notifications.infrastructure.event_handlers.get_user_name")
    @patch("modules.notifications.infrastructure.event_handlers.SQLAlchemyNotificationRepository")
    def test_handle_like_error_handling(
        self, mock_repo_class, mock_get_name, mock_session
    ):
        """Test gestion des erreurs."""
        from modules.notifications.infrastructure.event_handlers import handle_like_added
        from modules.dashboard.domain.events import LikeAddedEvent

        mock_db = Mock()
        mock_session.return_value = mock_db
        mock_repo_class.side_effect = Exception("DB Error")

        event = LikeAddedEvent(
            like_id=1,
            post_id=10,
            user_id=2,
            post_author_id=3,
            timestamp=datetime.now(),
        )

        # Ne doit pas lever d'exception
        handle_like_added(event)

        mock_db.close.assert_called_once()
