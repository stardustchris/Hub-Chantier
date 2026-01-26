"""Tests unitaires pour ReservationNotificationHandler."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date
import logging

from shared.infrastructure.notifications.handlers.reservation_notification_handler import (
    ReservationNotificationHandler,
    create_reservation_notification_handler,
)


class MockReservationCreatedEvent:
    """Mock event de creation de reservation."""

    def __init__(
        self,
        reservation_id: int = 1,
        ressource_id: int = 10,
        ressource_nom: str = "Grue mobile",
        demandeur_id: int = 5,
        chantier_id: int = 100,
        date_reservation: date = date(2024, 1, 15),
        validation_requise: bool = True,
    ):
        self.reservation_id = reservation_id
        self.ressource_id = ressource_id
        self.ressource_nom = ressource_nom
        self.demandeur_id = demandeur_id
        self.chantier_id = chantier_id
        self.date_reservation = date_reservation
        self.validation_requise = validation_requise


class MockReservationValideeEvent:
    """Mock event de validation de reservation."""

    def __init__(
        self,
        reservation_id: int = 1,
        ressource_id: int = 10,
        ressource_nom: str = "Grue mobile",
        demandeur_id: int = 5,
        date_reservation: date = date(2024, 1, 15),
    ):
        self.reservation_id = reservation_id
        self.ressource_id = ressource_id
        self.ressource_nom = ressource_nom
        self.demandeur_id = demandeur_id
        self.date_reservation = date_reservation


class MockReservationRefuseeEvent:
    """Mock event de refus de reservation."""

    def __init__(
        self,
        reservation_id: int = 1,
        ressource_id: int = 10,
        ressource_nom: str = "Grue mobile",
        demandeur_id: int = 5,
        date_reservation: date = date(2024, 1, 15),
        motif: str = None,
    ):
        self.reservation_id = reservation_id
        self.ressource_id = ressource_id
        self.ressource_nom = ressource_nom
        self.demandeur_id = demandeur_id
        self.date_reservation = date_reservation
        self.motif = motif


class TestHandleReservationCreated:
    """Tests de handle_reservation_created."""

    @patch("shared.infrastructure.notifications.handlers.reservation_notification_handler.get_notification_service")
    def test_sends_notification_when_validation_required(self, mock_get_service):
        """Test envoie notification si validation requise."""
        mock_service = Mock()
        mock_service.send_to_topic.return_value = True
        mock_get_service.return_value = mock_service

        handler = ReservationNotificationHandler()
        event = MockReservationCreatedEvent(validation_requise=True, chantier_id=100)

        handler.handle_reservation_created(event)

        mock_service.send_to_topic.assert_called_once()
        args = mock_service.send_to_topic.call_args
        assert args[0][0] == "valideurs_chantier_100"

    @patch("shared.infrastructure.notifications.handlers.reservation_notification_handler.get_notification_service")
    def test_does_not_send_when_no_validation_required(self, mock_get_service):
        """Test n'envoie pas si validation non requise."""
        mock_service = Mock()
        mock_get_service.return_value = mock_service

        handler = ReservationNotificationHandler()
        event = MockReservationCreatedEvent(validation_requise=False)

        handler.handle_reservation_created(event)

        mock_service.send_to_topic.assert_not_called()

    @patch("shared.infrastructure.notifications.handlers.reservation_notification_handler.get_notification_service")
    def test_notification_payload_content(self, mock_get_service):
        """Test contenu du payload de notification."""
        mock_service = Mock()
        mock_service.send_to_topic.return_value = True
        mock_get_service.return_value = mock_service

        handler = ReservationNotificationHandler()
        event = MockReservationCreatedEvent(
            reservation_id=42,
            ressource_nom="Camion benne",
            date_reservation=date(2024, 3, 20),
        )

        handler.handle_reservation_created(event)

        args = mock_service.send_to_topic.call_args
        payload = args[0][1]
        assert "Nouvelle demande de réservation" in payload.title
        assert "Camion benne" in payload.body
        assert "20/03" in payload.body
        assert payload.data["type"] == "reservation_demande"
        assert payload.data["reservation_id"] == "42"

    @patch("shared.infrastructure.notifications.handlers.reservation_notification_handler.get_notification_service")
    def test_logs_warning_on_failure(self, mock_get_service, caplog):
        """Test log warning si echec envoi."""
        mock_service = Mock()
        mock_service.send_to_topic.return_value = False
        mock_get_service.return_value = mock_service

        handler = ReservationNotificationHandler()
        event = MockReservationCreatedEvent()

        with caplog.at_level(logging.WARNING):
            handler.handle_reservation_created(event)

        assert "Échec" in caplog.text


class TestHandleReservationValidee:
    """Tests de handle_reservation_validee."""

    @patch("shared.infrastructure.notifications.handlers.reservation_notification_handler.get_notification_service")
    def test_sends_notification_to_user_with_token(self, mock_get_service):
        """Test envoie notification avec token utilisateur."""
        mock_service = Mock()
        mock_service.send_to_token.return_value = True
        mock_get_service.return_value = mock_service

        mock_user = Mock()
        mock_user.push_token = "user_push_token_123"
        mock_user_repo = Mock()
        mock_user_repo.find_by_id.return_value = mock_user

        handler = ReservationNotificationHandler(user_repository=mock_user_repo)
        event = MockReservationValideeEvent(demandeur_id=5)

        handler.handle_reservation_validee(event)

        mock_service.send_to_token.assert_called_once()
        args = mock_service.send_to_token.call_args
        assert args[0][0] == "user_push_token_123"

    @patch("shared.infrastructure.notifications.handlers.reservation_notification_handler.get_notification_service")
    def test_simulates_notification_without_token(self, mock_get_service, caplog):
        """Test simule notification sans token."""
        mock_service = Mock()
        mock_get_service.return_value = mock_service

        handler = ReservationNotificationHandler(user_repository=None)
        event = MockReservationValideeEvent()

        with caplog.at_level(logging.INFO):
            handler.handle_reservation_validee(event)

        mock_service.send_to_token.assert_not_called()
        assert "SIMULATED" in caplog.text

    @patch("shared.infrastructure.notifications.handlers.reservation_notification_handler.get_notification_service")
    def test_notification_payload_content(self, mock_get_service):
        """Test contenu du payload de validation."""
        mock_service = Mock()
        mock_service.send_to_token.return_value = True
        mock_get_service.return_value = mock_service

        mock_user = Mock()
        mock_user.push_token = "token"
        mock_user_repo = Mock()
        mock_user_repo.find_by_id.return_value = mock_user

        handler = ReservationNotificationHandler(user_repository=mock_user_repo)
        event = MockReservationValideeEvent(
            reservation_id=99,
            ressource_nom="Mini-pelle",
            date_reservation=date(2024, 5, 10),
        )

        handler.handle_reservation_validee(event)

        args = mock_service.send_to_token.call_args
        payload = args[0][1]
        assert "confirmée" in payload.title
        assert "Mini-pelle" in payload.body
        assert payload.data["type"] == "reservation_validee"


class TestHandleReservationRefusee:
    """Tests de handle_reservation_refusee."""

    @patch("shared.infrastructure.notifications.handlers.reservation_notification_handler.get_notification_service")
    def test_sends_notification_with_motif(self, mock_get_service):
        """Test envoie notification avec motif de refus."""
        mock_service = Mock()
        mock_service.send_to_token.return_value = True
        mock_get_service.return_value = mock_service

        mock_user = Mock()
        mock_user.push_token = "token"
        mock_user_repo = Mock()
        mock_user_repo.find_by_id.return_value = mock_user

        handler = ReservationNotificationHandler(user_repository=mock_user_repo)
        event = MockReservationRefuseeEvent(
            ressource_nom="Chargeuse",
            motif="Ressource déjà réservée",
        )

        handler.handle_reservation_refusee(event)

        args = mock_service.send_to_token.call_args
        payload = args[0][1]
        assert "refusée" in payload.title
        assert "Chargeuse" in payload.body
        assert "Ressource déjà réservée" in payload.body

    @patch("shared.infrastructure.notifications.handlers.reservation_notification_handler.get_notification_service")
    def test_sends_notification_without_motif(self, mock_get_service):
        """Test envoie notification sans motif."""
        mock_service = Mock()
        mock_service.send_to_token.return_value = True
        mock_get_service.return_value = mock_service

        mock_user = Mock()
        mock_user.push_token = "token"
        mock_user_repo = Mock()
        mock_user_repo.find_by_id.return_value = mock_user

        handler = ReservationNotificationHandler(user_repository=mock_user_repo)
        event = MockReservationRefuseeEvent(motif=None)

        handler.handle_reservation_refusee(event)

        args = mock_service.send_to_token.call_args
        payload = args[0][1]
        assert "Motif" not in payload.body
        assert payload.data["motif"] == ""

    @patch("shared.infrastructure.notifications.handlers.reservation_notification_handler.get_notification_service")
    def test_simulates_notification_without_token(self, mock_get_service, caplog):
        """Test simule notification sans token."""
        mock_service = Mock()
        mock_get_service.return_value = mock_service

        handler = ReservationNotificationHandler()
        event = MockReservationRefuseeEvent()

        with caplog.at_level(logging.INFO):
            handler.handle_reservation_refusee(event)

        assert "SIMULATED" in caplog.text


class TestGetUserPushToken:
    """Tests de _get_user_push_token."""

    @patch("shared.infrastructure.notifications.handlers.reservation_notification_handler.get_notification_service")
    def test_returns_token_when_user_has_it(self, mock_get_service):
        """Test retourne token si utilisateur l'a."""
        mock_user = Mock()
        mock_user.push_token = "valid_token"
        mock_user_repo = Mock()
        mock_user_repo.find_by_id.return_value = mock_user

        handler = ReservationNotificationHandler(user_repository=mock_user_repo)
        result = handler._get_user_push_token(5)

        assert result == "valid_token"
        mock_user_repo.find_by_id.assert_called_once_with(5)

    @patch("shared.infrastructure.notifications.handlers.reservation_notification_handler.get_notification_service")
    def test_returns_none_when_user_not_found(self, mock_get_service):
        """Test retourne None si utilisateur non trouve."""
        mock_user_repo = Mock()
        mock_user_repo.find_by_id.return_value = None

        handler = ReservationNotificationHandler(user_repository=mock_user_repo)
        result = handler._get_user_push_token(999)

        assert result is None

    @patch("shared.infrastructure.notifications.handlers.reservation_notification_handler.get_notification_service")
    def test_returns_none_without_user_repository(self, mock_get_service):
        """Test retourne None sans repository."""
        handler = ReservationNotificationHandler(user_repository=None)
        result = handler._get_user_push_token(5)

        assert result is None

    @patch("shared.infrastructure.notifications.handlers.reservation_notification_handler.get_notification_service")
    def test_returns_none_when_user_has_no_token(self, mock_get_service):
        """Test retourne None si utilisateur sans token."""
        mock_user = Mock(spec=[])  # Pas d'attribut push_token
        mock_user_repo = Mock()
        mock_user_repo.find_by_id.return_value = mock_user

        handler = ReservationNotificationHandler(user_repository=mock_user_repo)
        result = handler._get_user_push_token(5)

        assert result is None


class TestCreateReservationNotificationHandler:
    """Tests de la factory create_reservation_notification_handler."""

    @patch("shared.infrastructure.notifications.handlers.reservation_notification_handler.get_notification_service")
    def test_creates_handler_without_repository(self, mock_get_service):
        """Test cree handler sans repository."""
        handler = create_reservation_notification_handler()

        assert isinstance(handler, ReservationNotificationHandler)
        assert handler._user_repository is None

    @patch("shared.infrastructure.notifications.handlers.reservation_notification_handler.get_notification_service")
    def test_creates_handler_with_repository(self, mock_get_service):
        """Test cree handler avec repository."""
        mock_repo = Mock()
        handler = create_reservation_notification_handler(user_repository=mock_repo)

        assert isinstance(handler, ReservationNotificationHandler)
        assert handler._user_repository == mock_repo
