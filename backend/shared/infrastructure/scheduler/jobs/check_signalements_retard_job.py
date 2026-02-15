"""Job de vérification des signalements en retard (SIG-16, SIG-17).

Exécuté toutes les 15 minutes pour :
- Détecter les signalements non traités dans les délais
- Déclencher les escalades hiérarchiques progressives
- Émettre les événements d'escalade pour notification push
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class CheckSignalementsRetardJob:
    """Job APScheduler pour la vérification des retards signalements.

    Fonctionnement :
    1. Récupère les signalements actifs dont le temps écoulé >= 50%
    2. Détermine les escalades nécessaires via EscaladeService
    3. Enregistre l'historique et émet les événements
    4. Log les résultats
    """

    JOB_ID = "check_signalements_retard"
    DEFAULT_INTERVAL_MINUTES = 15

    def __init__(self, db_session_factory):
        """Initialise le job.

        Args:
            db_session_factory: Factory pour créer des sessions DB.
        """
        self._db_session_factory = db_session_factory

    def execute(self) -> dict:
        """Exécute le job de vérification.

        Returns:
            Dict avec statistiques d'exécution.
        """
        logger.info("Début job vérification retards signalements (SIG-16/SIG-17)")

        stats = {
            "signalements_verifies": 0,
            "escalades_effectuees": 0,
            "erreurs": 0,
        }

        try:
            session = self._db_session_factory()

            try:
                # Import ici pour éviter imports circulaires
                from modules.signalements.infrastructure.persistence import (
                    SQLAlchemySignalementRepository,
                    SQLAlchemyEscaladeRepository,
                )
                from modules.signalements.application.use_cases import (
                    CheckSignalementsRetardUseCase,
                )

                signalement_repo = SQLAlchemySignalementRepository(session)
                escalade_repo = SQLAlchemyEscaladeRepository(session)

                use_case = CheckSignalementsRetardUseCase(
                    signalement_repository=signalement_repo,
                    escalade_repository=escalade_repo,
                )

                result = use_case.execute()

                stats["signalements_verifies"] = result.signalements_verifies
                stats["escalades_effectuees"] = result.escalades_effectuees
                stats["erreurs"] = result.erreurs

                # Émettre les événements d'escalade pour les notifications push
                if result.details:
                    self._emit_escalade_events(result.details, session)

            finally:
                session.close()

        except Exception as e:
            logger.error(f"Erreur job retards signalements: {e}", exc_info=True)
            stats["erreurs"] += 1

        logger.info(
            f"Fin job retards: {stats['signalements_verifies']} vérifiés, "
            f"{stats['escalades_effectuees']} escaladés, "
            f"{stats['erreurs']} erreurs"
        )

        return stats

    def _emit_escalade_events(self, details: list, session) -> None:
        """Émet les événements d'escalade pour le bus d'événements.

        Args:
            details: Liste des détails d'escalade.
            session: Session DB pour récupérer les infos.
        """
        try:
            from modules.signalements.infrastructure.persistence import (
                SQLAlchemySignalementRepository,
            )
            from modules.signalements.domain.events import EscaladeSignalementEvent
            from shared.infrastructure.event_bus import event_bus
            import asyncio

            signalement_repo = SQLAlchemySignalementRepository(session)

            for detail in details:
                sig = signalement_repo.find_by_id(detail["signalement_id"])
                if not sig:
                    continue

                event = EscaladeSignalementEvent(
                    signalement_id=sig.id,
                    chantier_id=sig.chantier_id,
                    niveau=detail["niveau"],
                    pourcentage_temps=detail["pourcentage_temps"],
                    titre=sig.titre,
                    priorite=sig.priorite.value,
                    destinataires_roles=[detail["niveau"]],
                )

                # Publier l'événement async depuis un contexte sync
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.ensure_future(event_bus.publish(event))
                    else:
                        loop.run_until_complete(event_bus.publish(event))
                except RuntimeError:
                    # Pas de boucle événementielle active
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(event_bus.publish(event))
                    loop.close()

                logger.info(
                    f"Événement escalade émis: signalement #{sig.id} "
                    f"niveau={detail['niveau']}"
                )

        except Exception as e:
            logger.error(f"Erreur émission événements escalade: {e}", exc_info=True)

    @classmethod
    def register(cls, scheduler, db_session_factory) -> None:
        """Enregistre le job dans le scheduler.

        Args:
            scheduler: SchedulerService.
            db_session_factory: Factory pour sessions DB.
        """
        job = cls(db_session_factory)

        scheduler.add_interval_job(
            func=job.execute,
            job_id=cls.JOB_ID,
            minutes=cls.DEFAULT_INTERVAL_MINUTES,
        )

        logger.info(
            f"Job '{cls.JOB_ID}' enregistré: toutes les "
            f"{cls.DEFAULT_INTERVAL_MINUTES} minutes"
        )
