"""Job de rappel J-1 pour les réservations.

LOG-15 : Rappel J-1 - Notification veille de réservation

Ce job s'exécute chaque jour à 18h00 et envoie un rappel
aux utilisateurs ayant une réservation confirmée pour le lendemain.
"""

import logging
from datetime import date, timedelta
from typing import TYPE_CHECKING

from shared.infrastructure.notifications import NotificationPayload, get_notification_service

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class RappelReservationJob:
    """Job de rappel des réservations pour J+1.

    Fonctionnement :
    1. Récupère toutes les réservations validées pour demain
    2. Pour chaque réservation, envoie un push au demandeur
    3. Log les résultats
    """

    JOB_ID = "rappel_reservation_j1"
    DEFAULT_HOUR = 18  # Exécution à 18h
    DEFAULT_MINUTE = 0

    def __init__(self, db_session_factory):
        """Initialise le job.

        Args:
            db_session_factory: Factory pour créer des sessions DB
        """
        self._db_session_factory = db_session_factory
        self._notification_service = get_notification_service()

    def execute(self) -> dict:
        """Exécute le job de rappel.

        Returns:
            Dict avec statistiques d'exécution
        """
        logger.info("Début du job rappel réservations J-1")

        demain = date.today() + timedelta(days=1)
        stats = {
            "date_cible": demain.isoformat(),
            "reservations_trouvees": 0,
            "notifications_envoyees": 0,
            "erreurs": 0,
        }

        try:
            # Créer une session DB
            session = self._db_session_factory()

            try:
                # Import ici pour éviter imports circulaires
                from modules.logistique.infrastructure.persistence.models import (
                    ReservationModel,
                    RessourceModel,
                )

                # Récupérer les réservations validées pour demain
                reservations = (
                    session.query(ReservationModel)
                    .join(RessourceModel)
                    .filter(
                        ReservationModel.date_reservation == demain,
                        ReservationModel.statut == "validee",
                        ReservationModel.deleted_at.is_(None),
                    )
                    .all()
                )

                stats["reservations_trouvees"] = len(reservations)
                logger.info(f"Réservations pour demain: {len(reservations)}")

                # Envoyer les notifications
                for reservation in reservations:
                    try:
                        success = self._send_rappel(reservation, session)
                        if success:
                            stats["notifications_envoyees"] += 1
                        else:
                            stats["erreurs"] += 1
                    except Exception as e:
                        logger.error(f"Erreur rappel réservation {reservation.id}: {e}")
                        stats["erreurs"] += 1

            finally:
                session.close()

        except Exception as e:
            logger.error(f"Erreur job rappel: {e}")
            stats["erreurs"] += 1

        logger.info(
            f"Fin job rappel: {stats['notifications_envoyees']}/{stats['reservations_trouvees']} "
            f"notifications envoyées, {stats['erreurs']} erreurs"
        )

        return stats

    def _send_rappel(self, reservation, session) -> bool:
        """Envoie un rappel pour une réservation.

        Args:
            reservation: ReservationModel
            session: Session DB

        Returns:
            True si envoyé
        """
        # Récupérer le token push de l'utilisateur
        from modules.auth.infrastructure.persistence import UserModel

        user = session.query(UserModel).filter(
            UserModel.id == reservation.demandeur_id
        ).first()

        if not user:
            logger.warning(f"Utilisateur {reservation.demandeur_id} non trouvé")
            return False

        # Vérifier si l'utilisateur a un token push
        push_token = getattr(user, 'push_token', None)

        # Construire le message
        ressource = reservation.ressource
        payload = NotificationPayload(
            title="Rappel réservation demain",
            body=f"{ressource.nom} réservé de {reservation.heure_debut.strftime('%H:%M')} "
                 f"à {reservation.heure_fin.strftime('%H:%M')}",
            data={
                "type": "rappel_reservation",
                "reservation_id": str(reservation.id),
                "ressource_id": str(reservation.ressource_id),
                "date": reservation.date_reservation.isoformat(),
            },
            click_action=f"/logistique/reservations/{reservation.id}",
        )

        if push_token:
            return self._notification_service.send_to_token(push_token, payload)
        else:
            # En mode dev, simuler l'envoi
            logger.info(
                f"[SIMULATED] Rappel → User {user.id}: {payload.title} - {payload.body}"
            )
            return True

    @classmethod
    def register(cls, scheduler, db_session_factory) -> None:
        """Enregistre le job dans le scheduler.

        Args:
            scheduler: SchedulerService
            db_session_factory: Factory pour sessions DB
        """
        job = cls(db_session_factory)

        scheduler.add_cron_job(
            func=job.execute,
            job_id=cls.JOB_ID,
            hour=cls.DEFAULT_HOUR,
            minute=cls.DEFAULT_MINUTE,
            day_of_week="mon-sun",  # Tous les jours
        )

        logger.info(
            f"Job '{cls.JOB_ID}' enregistré: tous les jours à "
            f"{cls.DEFAULT_HOUR:02d}:{cls.DEFAULT_MINUTE:02d}"
        )
