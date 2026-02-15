"""Handler de notifications pour les events du planning.

PLN-23 : Notification push nouvelle affectation planning.
"""

import logging
from typing import TYPE_CHECKING

from ..notification_service import NotificationPayload, get_notification_service

if TYPE_CHECKING:
    from shared.domain.events.domain_event import DomainEvent

logger = logging.getLogger(__name__)


class PlanningNotificationHandler:
    """Handler des notifications push pour les affectations planning.

    Appelé par l'EventBus quand une nouvelle affectation est créée.
    Notifie l'utilisateur affecté.
    """

    def __init__(self):
        self._notification_service = get_notification_service()

    async def handle_affectation_created(self, event: "DomainEvent") -> None:
        """Gère la création d'une affectation (PLN-23).

        Envoie une notification push à l'utilisateur nouvellement affecté.

        Args:
            event: Événement de création d'affectation
                   (event_type: 'planning.affectation_created').
        """
        data = event.data
        user_id = data.get("user_id")
        chantier_nom = data.get("chantier_nom", "")
        date_affectation = data.get("date", "")
        heure_debut = data.get("heure_debut", "")
        heure_fin = data.get("heure_fin", "")

        if not user_id:
            logger.warning("Affectation sans user_id, notification non envoyée")
            return

        # Construire le body
        body_parts = [chantier_nom]
        if date_affectation:
            body_parts.append(f"le {date_affectation}")
        if heure_debut and heure_fin:
            body_parts.append(f"de {heure_debut} à {heure_fin}")
        elif heure_debut:
            body_parts.append(f"à partir de {heure_debut}")

        body = " ".join(body_parts)

        payload = NotificationPayload(
            title="Nouvelle affectation planning",
            body=body,
            data={
                "type": "planning_affectation",
                "affectation_id": str(data.get("affectation_id", "")),
                "chantier_id": str(data.get("chantier_id", "")),
                "user_id": str(user_id),
                "date": str(date_affectation),
            },
            click_action="/planning",
        )

        # Envoyer au topic de l'utilisateur
        topic = f"user_{user_id}"
        success = self._notification_service.send_to_topic(topic, payload)

        if success:
            logger.info(
                f"Notification affectation envoyée: user #{user_id} -> {chantier_nom}"
            )
        else:
            logger.warning(
                f"Échec notification affectation pour user #{user_id}"
            )


def create_planning_notification_handler():
    """Factory pour créer le handler."""
    return PlanningNotificationHandler()
