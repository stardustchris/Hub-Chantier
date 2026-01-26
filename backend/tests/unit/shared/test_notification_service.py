"""Tests unitaires pour NotificationService."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import logging
import sys

from shared.infrastructure.notifications.notification_service import (
    NotificationService,
    NotificationPayload,
    get_notification_service,
)


class TestNotificationPayload:
    """Tests du payload de notification."""

    def test_payload_basic(self):
        """Test creation de payload basique."""
        payload = NotificationPayload(
            title="Test Title",
            body="Test Body"
        )

        assert payload.title == "Test Title"
        assert payload.body == "Test Body"
        assert payload.data == {}
        assert payload.image_url is None
        assert payload.click_action is None

    def test_payload_with_all_fields(self):
        """Test payload avec tous les champs."""
        payload = NotificationPayload(
            title="Alert",
            body="New message",
            data={"type": "message", "id": "123"},
            image_url="https://example.com/image.jpg",
            click_action="/messages/123"
        )

        assert payload.data == {"type": "message", "id": "123"}
        assert payload.image_url == "https://example.com/image.jpg"
        assert payload.click_action == "/messages/123"

    def test_to_fcm_message_basic(self):
        """Test conversion en message FCM basique."""
        payload = NotificationPayload(
            title="Test",
            body="Body"
        )

        fcm_message = payload.to_fcm_message()

        assert fcm_message["notification"]["title"] == "Test"
        assert fcm_message["notification"]["body"] == "Body"
        assert fcm_message["data"] == {}

    def test_to_fcm_message_with_image(self):
        """Test message FCM avec image."""
        payload = NotificationPayload(
            title="Test",
            body="Body",
            image_url="https://example.com/img.jpg"
        )

        fcm_message = payload.to_fcm_message()

        assert fcm_message["notification"]["image"] == "https://example.com/img.jpg"

    def test_to_fcm_message_with_click_action(self):
        """Test message FCM avec action au clic."""
        payload = NotificationPayload(
            title="Test",
            body="Body",
            click_action="/route/123"
        )

        fcm_message = payload.to_fcm_message()

        assert "webpush" in fcm_message
        assert fcm_message["webpush"]["fcm_options"]["link"] == "/route/123"


class TestNotificationServiceInit:
    """Tests d'initialisation du service."""

    def test_init_without_firebase(self):
        """Test init sans Firebase installe."""
        with patch.dict("sys.modules", {"firebase_admin": None}):
            with patch("shared.infrastructure.notifications.notification_service.NotificationService._init_firebase") as mock_init:
                service = NotificationService()
                mock_init.assert_called_once()

    @patch("shared.infrastructure.notifications.notification_service.os.environ.get")
    def test_init_without_credentials(self, mock_env):
        """Test init sans credentials Firebase."""
        mock_env.return_value = None

        service = NotificationService()

        assert service._initialized is False

    @patch("shared.infrastructure.notifications.notification_service.os.environ.get")
    @patch("shared.infrastructure.notifications.notification_service.os.path.exists")
    def test_init_with_nonexistent_credentials_file(self, mock_exists, mock_env):
        """Test init avec fichier credentials inexistant."""
        mock_env.return_value = "/path/to/credentials.json"
        mock_exists.return_value = False

        service = NotificationService()

        assert service._initialized is False


class TestNotificationServiceSendToToken:
    """Tests d'envoi de notification a un token."""

    @pytest.fixture
    def service(self):
        """Service non initialise (mode simulation)."""
        service = NotificationService()
        service._initialized = False
        return service

    @pytest.fixture
    def payload(self):
        return NotificationPayload(
            title="Test Notification",
            body="Test Body"
        )

    def test_send_to_token_simulated(self, service, payload):
        """Test envoi simule (sans Firebase)."""
        result = service.send_to_token("fake_token_12345", payload)

        assert result is True

    def test_send_to_token_logs_simulated(self, service, payload, caplog):
        """Test que l'envoi simule est logge."""
        with caplog.at_level(logging.INFO):
            service.send_to_token("fake_token_12345", payload)

        assert "SIMULATED" in caplog.text
        assert "Test Notification" in caplog.text

    def test_send_to_token_with_firebase(self):
        """Test envoi reel avec Firebase."""
        # Mock firebase_admin.messaging dans sys.modules
        mock_messaging = MagicMock()
        mock_messaging.Message = Mock(return_value=Mock())
        mock_messaging.Notification = Mock(return_value=Mock())
        mock_messaging.WebpushConfig = Mock(return_value=Mock())
        mock_messaging.WebpushFCMOptions = Mock(return_value=Mock())
        mock_messaging.send.return_value = "message_id_123"

        with patch.dict(sys.modules, {"firebase_admin.messaging": mock_messaging}):
            service = NotificationService()
            service._initialized = True

            payload = NotificationPayload(title="Test", body="Body")
            result = service.send_to_token("real_token", payload)

            assert result is True
            mock_messaging.send.assert_called_once()

    def test_send_to_token_firebase_error(self):
        """Test gestion erreur Firebase."""
        mock_messaging = MagicMock()
        mock_messaging.Message = Mock(return_value=Mock())
        mock_messaging.Notification = Mock(return_value=Mock())
        mock_messaging.send.side_effect = Exception("Firebase error")

        with patch.dict(sys.modules, {"firebase_admin.messaging": mock_messaging}):
            service = NotificationService()
            service._initialized = True

            payload = NotificationPayload(title="Test", body="Body")
            result = service.send_to_token("token", payload)

            assert result is False


class TestNotificationServiceSendToTokens:
    """Tests d'envoi a plusieurs tokens."""

    @pytest.fixture
    def service(self):
        service = NotificationService()
        service._initialized = False
        return service

    @pytest.fixture
    def payload(self):
        return NotificationPayload(
            title="Broadcast",
            body="Message to all"
        )

    def test_send_to_empty_tokens_list(self, service, payload):
        """Test envoi a liste vide."""
        result = service.send_to_tokens([], payload)
        assert result == {}

    def test_send_to_multiple_tokens_simulated(self, service, payload):
        """Test envoi simule a plusieurs tokens."""
        tokens = ["token1", "token2", "token3"]
        result = service.send_to_tokens(tokens, payload)

        assert len(result) == 3
        assert all(success for success in result.values())

    def test_send_to_tokens_with_firebase(self):
        """Test envoi reel a plusieurs tokens."""
        mock_messaging = MagicMock()
        mock_messaging.MulticastMessage = Mock(return_value=Mock())
        mock_messaging.Notification = Mock(return_value=Mock())

        # Mock la reponse multicast
        mock_response = Mock()
        mock_response.success_count = 2
        mock_response.responses = [
            Mock(success=True),
            Mock(success=True),
            Mock(success=False),
        ]
        mock_messaging.send_multicast.return_value = mock_response

        with patch.dict(sys.modules, {"firebase_admin.messaging": mock_messaging}):
            service = NotificationService()
            service._initialized = True

            payload = NotificationPayload(title="Test", body="Body")
            tokens = ["token1", "token2", "token3"]
            result = service.send_to_tokens(tokens, payload)

            assert result["token1"] is True
            assert result["token2"] is True
            assert result["token3"] is False

    def test_send_to_tokens_firebase_error(self):
        """Test gestion erreur Firebase multicast."""
        mock_messaging = MagicMock()
        mock_messaging.MulticastMessage = Mock(return_value=Mock())
        mock_messaging.Notification = Mock(return_value=Mock())
        mock_messaging.send_multicast.side_effect = Exception("Multicast error")

        with patch.dict(sys.modules, {"firebase_admin.messaging": mock_messaging}):
            service = NotificationService()
            service._initialized = True

            payload = NotificationPayload(title="Test", body="Body")
            tokens = ["token1", "token2"]
            result = service.send_to_tokens(tokens, payload)

            assert all(not success for success in result.values())


class TestNotificationServiceSendToTopic:
    """Tests d'envoi a un topic."""

    @pytest.fixture
    def service(self):
        service = NotificationService()
        service._initialized = False
        return service

    @pytest.fixture
    def payload(self):
        return NotificationPayload(
            title="Topic Alert",
            body="Message for topic subscribers"
        )

    def test_send_to_topic_simulated(self, service, payload):
        """Test envoi simule a un topic."""
        result = service.send_to_topic("chantier_123", payload)
        assert result is True

    def test_send_to_topic_logs_simulated(self, service, payload, caplog):
        """Test que l'envoi topic simule est logge."""
        with caplog.at_level(logging.INFO):
            service.send_to_topic("conducteurs", payload)

        assert "SIMULATED" in caplog.text
        assert "conducteurs" in caplog.text

    def test_send_to_topic_with_firebase(self):
        """Test envoi reel a un topic."""
        mock_messaging = MagicMock()
        mock_messaging.Message = Mock(return_value=Mock())
        mock_messaging.Notification = Mock(return_value=Mock())
        mock_messaging.send.return_value = "topic_message_id"

        with patch.dict(sys.modules, {"firebase_admin.messaging": mock_messaging}):
            service = NotificationService()
            service._initialized = True

            payload = NotificationPayload(title="Test", body="Body")
            result = service.send_to_topic("all_users", payload)

            assert result is True

    def test_send_to_topic_firebase_error(self):
        """Test gestion erreur Firebase topic."""
        mock_messaging = MagicMock()
        mock_messaging.Message = Mock(return_value=Mock())
        mock_messaging.Notification = Mock(return_value=Mock())
        mock_messaging.send.side_effect = Exception("Topic error")

        with patch.dict(sys.modules, {"firebase_admin.messaging": mock_messaging}):
            service = NotificationService()
            service._initialized = True

            payload = NotificationPayload(title="Test", body="Body")
            result = service.send_to_topic("topic", payload)

            assert result is False


class TestNotificationServiceIsAvailable:
    """Tests de la propriete is_available."""

    def test_is_available_when_initialized(self):
        """Test is_available quand initialise."""
        service = NotificationService()
        service._initialized = True
        assert service.is_available is True

    def test_is_available_when_not_initialized(self):
        """Test is_available quand non initialise."""
        service = NotificationService()
        service._initialized = False
        assert service.is_available is False


class TestGetNotificationService:
    """Tests de la factory singleton."""

    def test_returns_singleton(self):
        """Test que la factory retourne un singleton."""
        # Reset le singleton
        import shared.infrastructure.notifications.notification_service as ns
        ns._notification_service = None

        service1 = get_notification_service()
        service2 = get_notification_service()

        assert service1 is service2

    def test_creates_instance_if_none(self):
        """Test creation d'instance si None."""
        import shared.infrastructure.notifications.notification_service as ns
        ns._notification_service = None

        service = get_notification_service()

        assert service is not None
        assert isinstance(service, NotificationService)
