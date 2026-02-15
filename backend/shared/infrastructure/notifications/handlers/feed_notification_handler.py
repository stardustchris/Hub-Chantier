"""Handler de notifications pour les events du feed d'actualités.

FEED-17 : Notification push nouvelle publication dans le feed.
"""

import logging
from typing import TYPE_CHECKING

from ..notification_service import NotificationPayload, get_notification_service

if TYPE_CHECKING:
    from shared.domain.events.domain_event import DomainEvent

logger = logging.getLogger(__name__)


class FeedNotificationHandler:
    """Handler des notifications push pour les publications du feed.

    Appelé par l'EventBus quand un nouveau post est publié dans le feed.
    Envoie une notification push aux destinataires ciblés.
    """

    def __init__(self):
        self._notification_service = get_notification_service()

    async def handle_post_published(self, event: "DomainEvent") -> None:
        """Gère la publication d'un nouveau post (FEED-17).

        Envoie une notification push aux utilisateurs ciblés par le post.
        - Si ciblé "tout le monde" -> topic global
        - Si ciblé chantier(s) -> topics chantier
        - Si ciblé utilisateur(s) -> notification individuelle (topic user)

        Args:
            event: Événement de publication (event_type: 'feed.post_published').
        """
        data = event.data
        auteur_nom = data.get("auteur_nom", "Quelqu'un")
        contenu = data.get("contenu", "")
        ciblage_type = data.get("ciblage_type", "tous")
        post_id = data.get("post_id", "")

        # Tronquer le contenu pour la notification
        body = contenu[:100] + "..." if len(contenu) > 100 else contenu

        payload = NotificationPayload(
            title=f"Nouvelle publication de {auteur_nom}",
            body=body,
            data={
                "type": "feed_post",
                "post_id": str(post_id),
                "ciblage_type": ciblage_type,
            },
            click_action="/feed",
        )

        if ciblage_type == "tous":
            # Publication globale
            success = self._notification_service.send_to_topic("feed_global", payload)
            if success:
                logger.info(f"Notification feed global envoyée pour post #{post_id}")

        elif ciblage_type == "chantiers":
            # Publication ciblée chantier(s)
            chantier_ids = data.get("chantier_ids", [])
            for chantier_id in chantier_ids:
                topic = f"chantier_{chantier_id}"
                success = self._notification_service.send_to_topic(topic, payload)
                if success:
                    logger.info(
                        f"Notification feed chantier envoyée: "
                        f"post #{post_id} -> topic '{topic}'"
                    )

        elif ciblage_type == "utilisateurs":
            # Publication ciblée utilisateur(s)
            user_ids = data.get("user_ids", [])
            for user_id in user_ids:
                topic = f"user_{user_id}"
                success = self._notification_service.send_to_topic(topic, payload)
                if success:
                    logger.info(
                        f"Notification feed utilisateur envoyée: "
                        f"post #{post_id} -> user #{user_id}"
                    )

        else:
            logger.warning(f"Type de ciblage inconnu: {ciblage_type}")


def create_feed_notification_handler():
    """Factory pour créer le handler."""
    return FeedNotificationHandler()
