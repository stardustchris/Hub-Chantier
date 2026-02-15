"""Tests unitaires pour les handlers de notifications push (SIG-13, FEED-17, PLN-23)."""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

from shared.domain.events.domain_event import DomainEvent
from shared.infrastructure.notifications.handlers.signalement_notification_handler import (
    SignalementNotificationHandler,
)
from shared.infrastructure.notifications.handlers.feed_notification_handler import (
    FeedNotificationHandler,
)
from shared.infrastructure.notifications.handlers.planning_notification_handler import (
    PlanningNotificationHandler,
)


@pytest.fixture
def mock_notification_service():
    """Mock du service de notifications."""
    with patch(
        "shared.infrastructure.notifications.handlers.signalement_notification_handler.get_notification_service"
    ) as mock_sig, patch(
        "shared.infrastructure.notifications.handlers.feed_notification_handler.get_notification_service"
    ) as mock_feed, patch(
        "shared.infrastructure.notifications.handlers.planning_notification_handler.get_notification_service"
    ) as mock_plan:
        service = MagicMock()
        service.send_to_topic.return_value = True
        service.send_to_token.return_value = True
        mock_sig.return_value = service
        mock_feed.return_value = service
        mock_plan.return_value = service
        yield service


class TestSignalementNotificationHandler:
    """Tests pour le handler SIG-13 (création signalement)."""

    def test_handle_signalement_created(self, mock_notification_service):
        """Test: notification envoyée lors de la création d'un signalement."""
        handler = SignalementNotificationHandler()

        event = DomainEvent(
            event_type="signalement.created",
            aggregate_id="1",
            data={
                "signalement_id": 1,
                "chantier_id": 5,
                "titre": "Fissure mur porteur",
                "gravite": "critique",
            },
        )

        asyncio.get_event_loop().run_until_complete(
            handler.handle_signalement_created(event)
        )

        assert mock_notification_service.send_to_topic.call_count == 2
        calls = mock_notification_service.send_to_topic.call_args_list

        # Chef + Conducteur du chantier
        topics = [call.args[0] for call in calls]
        assert "chef_chantier_5" in topics
        assert "conducteur_chantier_5" in topics

    def test_handle_signalement_escaladed(self, mock_notification_service):
        """Test: notification envoyée lors d'une escalade (SIG-17)."""
        handler = SignalementNotificationHandler()

        event = DomainEvent(
            event_type="signalement.escaladed",
            aggregate_id="1",
            data={
                "signalement_id": 1,
                "chantier_id": 5,
                "niveau": "conducteur",
                "pourcentage_temps": 105.0,
                "titre": "Fissure mur porteur",
                "priorite": "critique",
            },
        )

        asyncio.get_event_loop().run_until_complete(
            handler.handle_signalement_escaladed(event)
        )

        mock_notification_service.send_to_topic.assert_called_once()
        call_args = mock_notification_service.send_to_topic.call_args
        assert call_args.args[0] == "conducteur_chantier_5"

    def test_handle_escalade_admin_topic(self, mock_notification_service):
        """Test: escalade admin utilise le topic 'admin'."""
        handler = SignalementNotificationHandler()

        event = DomainEvent(
            event_type="signalement.escaladed",
            aggregate_id="1",
            data={
                "signalement_id": 1,
                "chantier_id": 5,
                "niveau": "admin",
                "pourcentage_temps": 210.0,
                "titre": "Test",
                "priorite": "critique",
            },
        )

        asyncio.get_event_loop().run_until_complete(
            handler.handle_signalement_escaladed(event)
        )

        call_args = mock_notification_service.send_to_topic.call_args
        assert call_args.args[0] == "admin"


class TestFeedNotificationHandler:
    """Tests pour le handler FEED-17 (publication feed)."""

    def test_handle_post_global(self, mock_notification_service):
        """Test: notification pour publication globale."""
        handler = FeedNotificationHandler()

        event = DomainEvent(
            event_type="feed.post_published",
            aggregate_id="1",
            data={
                "post_id": 42,
                "auteur_nom": "Jean Dupont",
                "contenu": "Rappel: réunion de chantier demain",
                "ciblage_type": "tous",
            },
        )

        asyncio.get_event_loop().run_until_complete(
            handler.handle_post_published(event)
        )

        mock_notification_service.send_to_topic.assert_called_once()
        topic = mock_notification_service.send_to_topic.call_args.args[0]
        assert topic == "feed_global"

    def test_handle_post_chantier_ciblage(self, mock_notification_service):
        """Test: notification pour publication ciblée chantier."""
        handler = FeedNotificationHandler()

        event = DomainEvent(
            event_type="feed.post_published",
            aggregate_id="1",
            data={
                "post_id": 43,
                "auteur_nom": "Marie Martin",
                "contenu": "Livraison béton demain 8h",
                "ciblage_type": "chantiers",
                "chantier_ids": [1, 3],
            },
        )

        asyncio.get_event_loop().run_until_complete(
            handler.handle_post_published(event)
        )

        assert mock_notification_service.send_to_topic.call_count == 2
        topics = [
            call.args[0]
            for call in mock_notification_service.send_to_topic.call_args_list
        ]
        assert "chantier_1" in topics
        assert "chantier_3" in topics

    def test_handle_post_truncated_body(self, mock_notification_service):
        """Test: contenu tronqué à 100 caractères."""
        handler = FeedNotificationHandler()

        long_content = "A" * 200
        event = DomainEvent(
            event_type="feed.post_published",
            aggregate_id="1",
            data={
                "post_id": 44,
                "auteur_nom": "Test",
                "contenu": long_content,
                "ciblage_type": "tous",
            },
        )

        asyncio.get_event_loop().run_until_complete(
            handler.handle_post_published(event)
        )

        payload = mock_notification_service.send_to_topic.call_args.args[1]
        assert len(payload.body) == 103  # 100 chars + "..."


class TestPlanningNotificationHandler:
    """Tests pour le handler PLN-23 (affectation planning)."""

    def test_handle_affectation_created(self, mock_notification_service):
        """Test: notification envoyée à l'utilisateur affecté."""
        handler = PlanningNotificationHandler()

        event = DomainEvent(
            event_type="planning.affectation_created",
            aggregate_id="1",
            data={
                "affectation_id": 10,
                "user_id": 5,
                "chantier_id": 3,
                "chantier_nom": "Résidence Les Lilas",
                "date": "15/02/2026",
                "heure_debut": "08:00",
                "heure_fin": "17:00",
            },
        )

        asyncio.get_event_loop().run_until_complete(
            handler.handle_affectation_created(event)
        )

        mock_notification_service.send_to_topic.assert_called_once()
        topic = mock_notification_service.send_to_topic.call_args.args[0]
        assert topic == "user_5"

        payload = mock_notification_service.send_to_topic.call_args.args[1]
        assert "Résidence Les Lilas" in payload.body
        assert "08:00" in payload.body

    def test_handle_affectation_no_user_id(self, mock_notification_service):
        """Test: pas de notification si user_id manquant."""
        handler = PlanningNotificationHandler()

        event = DomainEvent(
            event_type="planning.affectation_created",
            aggregate_id="1",
            data={
                "affectation_id": 10,
                "chantier_nom": "Test",
            },
        )

        asyncio.get_event_loop().run_until_complete(
            handler.handle_affectation_created(event)
        )

        mock_notification_service.send_to_topic.assert_not_called()
