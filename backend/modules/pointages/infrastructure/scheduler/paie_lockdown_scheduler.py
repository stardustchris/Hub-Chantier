"""Scheduler pour le verrouillage automatique des périodes de paie (GAP-FDH-009)."""

import logging
from datetime import datetime, date
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from shared.infrastructure.database import SessionLocal
from shared.infrastructure.event_bus import get_event_bus
from ...application.use_cases.lock_monthly_period import LockMonthlyPeriodUseCase
from ...application.dtos.lock_period_dtos import LockMonthlyPeriodDTO

logger = logging.getLogger(__name__)


class PaieLockdownScheduler:
    """
    Scheduler pour le verrouillage automatique des périodes de paie.

    Déclenche le verrouillage automatique le dernier vendredi du mois
    précédant la dernière semaine, à 23:59.

    Exemple pour janvier 2026:
    - Dernière semaine: Lun 26 → Dim 31
    - Vendredi précédent: Ven 23/01
    - Déclenchement: Vendredi 23/01 à 23:59

    Attributes:
        scheduler: Instance APScheduler.
        use_case: Use case de verrouillage.
    """

    def __init__(self, use_case: Optional[LockMonthlyPeriodUseCase] = None):
        """
        Initialise le scheduler.

        Args:
            use_case: Use case de verrouillage (optionnel, créé par défaut).
        """
        self.scheduler = BackgroundScheduler()
        self.use_case = use_case or self._create_use_case()

    def _create_use_case(self) -> LockMonthlyPeriodUseCase:
        """Crée une instance du use case avec dépendances injectées."""
        event_bus = get_event_bus()
        return LockMonthlyPeriodUseCase(event_bus=event_bus)

    def start(self) -> None:
        """
        Démarre le scheduler.

        Configure un job cron qui s'exécute tous les vendredis à 23:59.
        Le job vérifie si c'est le bon vendredi pour verrouiller le mois.
        """
        # Job qui s'exécute tous les vendredis à 23:59
        # day_of_week=4 → vendredi (0=lundi, 6=dimanche)
        trigger = CronTrigger(day_of_week=4, hour=23, minute=59)

        self.scheduler.add_job(
            func=self._check_and_lock_period,
            trigger=trigger,
            id="paie_lockdown_check",
            name="Vérification verrouillage période paie",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info("PaieLockdownScheduler démarré (vérification tous les vendredis à 23:59)")

    def stop(self) -> None:
        """Arrête le scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("PaieLockdownScheduler arrêté")

    def _check_and_lock_period(self) -> None:
        """
        Vérifie si aujourd'hui est le vendredi de verrouillage et déclenche si oui.

        Cette fonction est appelée tous les vendredis à 23:59.
        Elle calcule si c'est le bon vendredi (dernier vendredi avant la dernière
        semaine du mois) et si oui, déclenche le verrouillage.
        """
        today = date.today()
        logger.info(f"Vérification verrouillage paie pour {today.strftime('%d/%m/%Y')}")

        # Importe ici pour éviter import circulaire
        from ...domain.value_objects import PeriodePaie

        # Vérifie tous les mois récents (mois en cours et mois précédent)
        # pour gérer le cas où un mois se termine un dimanche et le vendredi
        # de verrouillage tombe en fait dans le mois suivant
        for month_offset in [0, -1]:
            check_date = today.replace(day=1)
            if month_offset == -1:
                if check_date.month == 1:
                    check_date = check_date.replace(year=check_date.year - 1, month=12)
                else:
                    check_date = check_date.replace(month=check_date.month - 1)

            year = check_date.year
            month = check_date.month

            # Calcule la date de verrouillage pour ce mois
            lockdown_date = PeriodePaie.get_lockdown_date(year, month)

            # Si aujourd'hui est le jour de verrouillage, déclenche
            if today == lockdown_date:
                logger.info(
                    f"Déclenchement verrouillage automatique pour {month:02d}/{year}"
                )
                self._lock_period(year, month)
                return

        logger.debug(f"Pas de verrouillage à déclencher pour {today.strftime('%d/%m/%Y')}")

    def _lock_period(self, year: int, month: int) -> None:
        """
        Déclenche le verrouillage d'une période.

        Args:
            year: Année.
            month: Mois.
        """
        try:
            dto = LockMonthlyPeriodDTO(year=year, month=month)
            result = self.use_case.execute(dto, auto_locked=True, locked_by=None)

            logger.info(
                f"Verrouillage automatique réussi pour {month:02d}/{year}. "
                f"Date de verrouillage: {result.lockdown_date}. "
                f"Utilisateurs notifiés: {len(result.notified_users)}"
            )

        except Exception as e:
            logger.error(f"Erreur lors du verrouillage automatique {month:02d}/{year}: {e}")


# Instance globale du scheduler (singleton)
_scheduler_instance: Optional[PaieLockdownScheduler] = None


def get_paie_lockdown_scheduler() -> PaieLockdownScheduler:
    """
    Retourne l'instance singleton du scheduler.

    Returns:
        Instance du scheduler.
    """
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = PaieLockdownScheduler()
    return _scheduler_instance


def start_paie_lockdown_scheduler() -> None:
    """
    Démarre le scheduler de verrouillage automatique.

    Cette fonction doit être appelée au démarrage de l'application.
    """
    scheduler = get_paie_lockdown_scheduler()
    if not scheduler.scheduler.running:
        scheduler.start()


def stop_paie_lockdown_scheduler() -> None:
    """
    Arrête le scheduler de verrouillage automatique.

    Cette fonction doit être appelée à l'arrêt de l'application.
    """
    global _scheduler_instance
    if _scheduler_instance is not None:
        _scheduler_instance.stop()
        _scheduler_instance = None
