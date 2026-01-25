"""Service de scheduling avec APScheduler.

Gère les jobs planifiés de l'application :
- LOG-15 : Rappel J-1 réservations
- SIG-16/17 : Escalade automatique signalements
- Autres jobs futurs
"""

import logging
from datetime import datetime
from typing import Callable, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Singleton scheduler
_scheduler: Optional["SchedulerService"] = None


class SchedulerService:
    """Service de gestion des jobs planifiés.

    Utilise APScheduler en mode BackgroundScheduler pour exécuter
    des tâches de manière asynchrone sans bloquer l'application.
    """

    def __init__(self):
        """Initialise le scheduler avec configuration par défaut."""
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(max_workers=5)
        }
        job_defaults = {
            'coalesce': True,  # Fusionner les exécutions manquées
            'max_instances': 1,  # Une seule instance par job
            'misfire_grace_time': 60 * 60,  # 1h de grâce pour les misfires
        }

        self._scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='Europe/Paris',
        )
        self._started = False

    def start(self) -> None:
        """Démarre le scheduler."""
        if not self._started:
            self._scheduler.start()
            self._started = True
            logger.info("Scheduler démarré")

    def shutdown(self, wait: bool = True) -> None:
        """Arrête le scheduler.

        Args:
            wait: Attendre la fin des jobs en cours
        """
        if self._started:
            self._scheduler.shutdown(wait=wait)
            self._started = False
            logger.info("Scheduler arrêté")

    def add_cron_job(
        self,
        func: Callable,
        job_id: str,
        hour: int = 8,
        minute: int = 0,
        day_of_week: str = "mon-fri",
        **kwargs
    ) -> None:
        """Ajoute un job cron (exécution à heure fixe).

        Args:
            func: Fonction à exécuter
            job_id: Identifiant unique du job
            hour: Heure d'exécution (0-23)
            minute: Minute d'exécution (0-59)
            day_of_week: Jours d'exécution (ex: "mon-fri", "mon,wed,fri")
            **kwargs: Arguments supplémentaires pour le job
        """
        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            day_of_week=day_of_week,
        )

        self._scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            **kwargs
        )
        logger.info(
            f"Job cron ajouté: {job_id} à {hour:02d}:{minute:02d} ({day_of_week})"
        )

    def add_interval_job(
        self,
        func: Callable,
        job_id: str,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        **kwargs
    ) -> None:
        """Ajoute un job intervalle (exécution périodique).

        Args:
            func: Fonction à exécuter
            job_id: Identifiant unique du job
            hours: Intervalle en heures
            minutes: Intervalle en minutes
            seconds: Intervalle en secondes
            **kwargs: Arguments supplémentaires pour le job
        """
        trigger = IntervalTrigger(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )

        self._scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            **kwargs
        )
        logger.info(
            f"Job intervalle ajouté: {job_id} toutes les {hours}h{minutes}m{seconds}s"
        )

    def remove_job(self, job_id: str) -> bool:
        """Supprime un job.

        Args:
            job_id: Identifiant du job

        Returns:
            True si supprimé, False sinon
        """
        try:
            self._scheduler.remove_job(job_id)
            logger.info(f"Job supprimé: {job_id}")
            return True
        except Exception as e:
            logger.warning(f"Job non trouvé: {job_id} - {e}")
            return False

    def get_jobs(self) -> list:
        """Retourne la liste des jobs actifs."""
        return self._scheduler.get_jobs()

    def run_job_now(self, job_id: str) -> bool:
        """Exécute un job immédiatement.

        Args:
            job_id: Identifiant du job

        Returns:
            True si déclenché, False sinon
        """
        job = self._scheduler.get_job(job_id)
        if job:
            job.modify(next_run_time=datetime.now())
            logger.info(f"Job déclenché manuellement: {job_id}")
            return True
        return False

    @property
    def is_running(self) -> bool:
        """Vérifie si le scheduler est en cours d'exécution."""
        return self._started and self._scheduler.running


def get_scheduler() -> SchedulerService:
    """Factory pour obtenir l'instance singleton du scheduler."""
    global _scheduler
    if _scheduler is None:
        _scheduler = SchedulerService()
    return _scheduler
