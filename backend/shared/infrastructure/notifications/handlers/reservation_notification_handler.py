"""Handler de notifications pour les events de réservation.

LOG-13 : Notification demande - Push au valideur (chef/conducteur)
LOG-14 : Notification décision - Push au demandeur
"""

import logging
from typing import TYPE_CHECKING

from ..notification_service import NotificationPayload, get_notification_service

if TYPE_CHECKING:
    from modules.logistique.domain.events import (
        ReservationCreatedEvent,
        ReservationValideeEvent,
        ReservationRefuseeEvent,
    )

logger = logging.getLogger(__name__)


class ReservationNotificationHandler:
    """Handler des notifications pour les réservations de matériel.

    Ce handler est appelé par l'EventBus quand des events de réservation
    sont publiés. Il envoie les notifications push appropriées.
    """

    def __init__(self, user_repository=None):
        """Initialise le handler.

        Args:
            user_repository: Repository pour récupérer les tokens push des utilisateurs
        """
        self._notification_service = get_notification_service()
        self._user_repository = user_repository

    def handle_reservation_created(self, event: "ReservationCreatedEvent") -> None:
        """Gère l'event de création de réservation.

        LOG-13 : Envoie une notification au valideur si validation requise.

        Args:
            event: Event de création de réservation
        """
        if not event.validation_requise:
            logger.debug(f"Réservation {event.reservation_id} sans validation requise")
            return

        payload = NotificationPayload(
            title="Nouvelle demande de réservation",
            body=f"{event.ressource_nom} demandé pour le {event.date_reservation.strftime('%d/%m')}",
            data={
                "type": "reservation_demande",
                "reservation_id": str(event.reservation_id),
                "ressource_id": str(event.ressource_id),
                "demandeur_id": str(event.demandeur_id),
                "date": event.date_reservation.isoformat(),
            },
            click_action="/logistique/validations",
        )

        # Envoyer aux valideurs (chefs et conducteurs du chantier)
        # En mode simplifié, on envoie au topic des valideurs
        topic = f"valideurs_chantier_{event.chantier_id}"

        success = self._notification_service.send_to_topic(topic, payload)

        if success:
            logger.info(
                f"Notification demande envoyée pour réservation {event.reservation_id}"
            )
        else:
            logger.warning(
                f"Échec notification demande réservation {event.reservation_id}"
            )

    def handle_reservation_validee(self, event: "ReservationValideeEvent") -> None:
        """Gère l'event de validation de réservation.

        LOG-14 : Envoie une notification au demandeur.

        Args:
            event: Event de validation
        """
        payload = NotificationPayload(
            title="Réservation confirmée",
            body=f"{event.ressource_nom} validé pour le {event.date_reservation.strftime('%d/%m')}",
            data={
                "type": "reservation_validee",
                "reservation_id": str(event.reservation_id),
                "ressource_id": str(event.ressource_id),
                "date": event.date_reservation.isoformat(),
            },
            click_action=f"/logistique/reservations/{event.reservation_id}",
        )

        # Récupérer le token du demandeur
        token = self._get_user_push_token(event.demandeur_id)

        if token:
            success = self._notification_service.send_to_token(token, payload)
        else:
            # En mode dev/simulé, log seulement
            logger.info(
                f"[SIMULATED] Notification validation → User {event.demandeur_id}: "
                f"{payload.title}"
            )
            success = True

        if success:
            logger.info(
                f"Notification validation envoyée pour réservation {event.reservation_id}"
            )

    def handle_reservation_refusee(self, event: "ReservationRefuseeEvent") -> None:
        """Gère l'event de refus de réservation.

        LOG-14 : Envoie une notification au demandeur avec le motif.

        Args:
            event: Event de refus
        """
        body = f"{event.ressource_nom} refusé pour le {event.date_reservation.strftime('%d/%m')}"
        if event.motif:
            body += f"\nMotif : {event.motif}"

        payload = NotificationPayload(
            title="Réservation refusée",
            body=body,
            data={
                "type": "reservation_refusee",
                "reservation_id": str(event.reservation_id),
                "ressource_id": str(event.ressource_id),
                "date": event.date_reservation.isoformat(),
                "motif": event.motif or "",
            },
            click_action=f"/logistique/reservations/{event.reservation_id}",
        )

        token = self._get_user_push_token(event.demandeur_id)

        if token:
            success = self._notification_service.send_to_token(token, payload)
        else:
            logger.info(
                f"[SIMULATED] Notification refus → User {event.demandeur_id}: "
                f"{payload.title}"
            )
            success = True

        if success:
            logger.info(
                f"Notification refus envoyée pour réservation {event.reservation_id}"
            )

    def _get_user_push_token(self, user_id: int) -> str | None:
        """Récupère le token push d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Token push ou None
        """
        if self._user_repository:
            user = self._user_repository.find_by_id(user_id)
            if user:
                return getattr(user, 'push_token', None)
        return None


# Factory pour créer le handler avec les dépendances
def create_reservation_notification_handler(user_repository=None):
    """Crée une instance du handler avec les dépendances injectées."""
    return ReservationNotificationHandler(user_repository)
