"""Handler de notifications pour les events de signalements.

SIG-13 : Notification push à la création d'un signalement
         Notifie le chef de chantier + conducteur de travaux du chantier.
SIG-17 : Notification push lors des escalades
"""

import logging
from typing import TYPE_CHECKING

from ..notification_service import NotificationPayload, get_notification_service

if TYPE_CHECKING:
    from modules.signalements.domain.events.signalement_created import (
        SignalementCreatedEvent,
    )
    from modules.signalements.domain.events.escalade_signalement import (
        EscaladeSignalementEvent,
    )

logger = logging.getLogger(__name__)


class SignalementNotificationHandler:
    """Handler des notifications pour les signalements.

    Appelé par l'EventBus quand des événements signalement sont publiés.
    """

    def __init__(self):
        self._notification_service = get_notification_service()

    async def handle_signalement_created(self, event: "SignalementCreatedEvent") -> None:
        """Gère la création d'un signalement (SIG-13).

        Envoie une notification push au chef de chantier et au conducteur
        de travaux du chantier concerné.

        Args:
            event: Événement de création de signalement.
        """
        data = event.data
        chantier_id = data.get("chantier_id")
        titre = data.get("titre", "Nouveau signalement")
        gravite = data.get("gravite", "moyenne")

        # Construire le payload de notification
        payload = NotificationPayload(
            title=f"Nouveau signalement ({gravite})",
            body=titre,
            data={
                "type": "signalement_created",
                "signalement_id": str(data.get("signalement_id", "")),
                "chantier_id": str(chantier_id),
                "gravite": gravite,
            },
            click_action=f"/signalements/{data.get('signalement_id', '')}",
        )

        # Envoyer aux topics chef et conducteur du chantier
        topics = [
            f"chef_chantier_{chantier_id}",
            f"conducteur_chantier_{chantier_id}",
        ]

        for topic in topics:
            success = self._notification_service.send_to_topic(topic, payload)
            if success:
                logger.info(
                    f"Notification signalement créé envoyée au topic '{topic}'"
                )
            else:
                logger.warning(
                    f"Échec notification signalement créé au topic '{topic}'"
                )

    async def handle_signalement_escaladed(self, event: "EscaladeSignalementEvent") -> None:
        """Gère l'escalade d'un signalement (SIG-17).

        Envoie une notification push selon le niveau d'escalade.

        Args:
            event: Événement d'escalade.
        """
        data = event.data
        chantier_id = data.get("chantier_id")
        niveau = data.get("niveau", "")
        titre = data.get("titre", "Signalement escaladé")
        priorite = data.get("priorite", "")
        pourcentage = data.get("pourcentage_temps", 0)

        niveau_labels = {
            "chef_chantier": "Chef de Chantier",
            "conducteur": "Conducteur de Travaux",
            "admin": "Administrateur",
        }
        niveau_label = niveau_labels.get(niveau, niveau)

        payload = NotificationPayload(
            title=f"Escalade {niveau_label} - {priorite}",
            body=f"{titre} ({pourcentage:.0f}% du délai écoulé)",
            data={
                "type": "signalement_escalade",
                "signalement_id": str(data.get("signalement_id", "")),
                "chantier_id": str(chantier_id),
                "niveau": niveau,
                "pourcentage_temps": str(pourcentage),
            },
            click_action=f"/signalements/{data.get('signalement_id', '')}",
        )

        # Envoyer au topic correspondant au niveau d'escalade
        topic = f"{niveau}_chantier_{chantier_id}" if niveau != "admin" else "admin"
        success = self._notification_service.send_to_topic(topic, payload)

        if success:
            logger.info(
                f"Notification escalade ({niveau}) envoyée pour signalement "
                f"#{data.get('signalement_id')}"
            )
        else:
            logger.warning(
                f"Échec notification escalade ({niveau}) pour signalement "
                f"#{data.get('signalement_id')}"
            )


def create_signalement_notification_handler():
    """Factory pour créer le handler."""
    return SignalementNotificationHandler()
