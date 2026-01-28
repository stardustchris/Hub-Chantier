"""
Scheduleur automatique pour le nettoyage des webhook deliveries.

Utilise APScheduler pour exécuter le nettoyage automatiquement tous les jours à 3h du matin.
À activer dans main.py au démarrage de l'application.

Usage:
    from shared.infrastructure.webhooks.cleanup_scheduler import start_cleanup_scheduler

    # Au démarrage de l'app
    start_cleanup_scheduler()
"""

import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from shared.infrastructure.database import SessionLocal
from shared.infrastructure.webhooks.models import WebhookDeliveryModel

logger = logging.getLogger(__name__)

# Configuration
RETENTION_DAYS = 90
SCHEDULE_HOUR = 3  # 3h du matin
SCHEDULE_MINUTE = 0

# Instance globale du scheduler
_scheduler = None


def cleanup_old_deliveries_job():
    """
    Job de nettoyage des anciennes deliveries.

    Supprime les webhook_deliveries plus anciennes que RETENTION_DAYS jours.
    Appelé automatiquement par APScheduler.
    """
    db = SessionLocal()

    try:
        cutoff_date = datetime.utcnow() - timedelta(days=RETENTION_DAYS)

        logger.info(
            f"[Cleanup Job] Début du nettoyage des deliveries > {RETENTION_DAYS} jours "
            f"(avant {cutoff_date.date()})"
        )

        # Compter et supprimer
        delete_query = db.query(WebhookDeliveryModel).filter(
            WebhookDeliveryModel.delivered_at < cutoff_date
        )
        count = delete_query.count()

        if count == 0:
            logger.info("[Cleanup Job] Aucune delivery à nettoyer")
            return

        deleted_count = delete_query.delete(synchronize_session=False)
        db.commit()

        logger.info(
            f"[Cleanup Job] ✅ Nettoyage terminé: {deleted_count} deliveries supprimées "
            f"(cutoff: {cutoff_date.date()})"
        )

    except Exception as e:
        logger.error(f"[Cleanup Job] ❌ Erreur lors du nettoyage: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def start_cleanup_scheduler():
    """
    Démarre le scheduler de nettoyage automatique.

    Le job s'exécute tous les jours à SCHEDULE_HOUR:SCHEDULE_MINUTE.
    Utilise APScheduler avec BackgroundScheduler.

    Returns:
        BackgroundScheduler: Instance du scheduler démarré
    """
    global _scheduler

    if _scheduler is not None:
        logger.warning("[Cleanup Scheduler] Scheduler déjà démarré")
        return _scheduler

    _scheduler = BackgroundScheduler()

    # Ajouter le job avec cron trigger (tous les jours à 3h)
    trigger = CronTrigger(hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE)

    _scheduler.add_job(
        cleanup_old_deliveries_job,
        trigger=trigger,
        id='webhook_deliveries_cleanup',
        name='Cleanup Webhook Deliveries (GDPR)',
        replace_existing=True,
        max_instances=1,  # Ne pas lancer en parallèle
    )

    _scheduler.start()

    logger.info(
        f"[Cleanup Scheduler] ✅ Scheduler démarré - Nettoyage automatique chaque jour à "
        f"{SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d} (rétention: {RETENTION_DAYS} jours)"
    )

    return _scheduler


def stop_cleanup_scheduler():
    """
    Arrête le scheduler de nettoyage.

    À appeler lors du shutdown de l'application.
    """
    global _scheduler

    if _scheduler is None:
        logger.warning("[Cleanup Scheduler] Scheduler non démarré")
        return

    _scheduler.shutdown(wait=True)
    _scheduler = None

    logger.info("[Cleanup Scheduler] Scheduler arrêté")


def run_cleanup_now():
    """
    Exécute le nettoyage immédiatement (utile pour debug/tests).

    Returns:
        None
    """
    logger.info("[Cleanup Scheduler] Exécution manuelle du nettoyage...")
    cleanup_old_deliveries_job()


# Configuration pour l'intégration dans main.py
"""
Dans backend/main.py, ajouter:

from shared.infrastructure.webhooks.cleanup_scheduler import start_cleanup_scheduler, stop_cleanup_scheduler
import atexit

# Au démarrage
@app.on_event("startup")
async def startup_event():
    start_cleanup_scheduler()

# Au shutdown
@app.on_event("shutdown")
async def shutdown_event():
    stop_cleanup_scheduler()
"""
