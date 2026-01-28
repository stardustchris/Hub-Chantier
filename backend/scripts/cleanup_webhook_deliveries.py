#!/usr/bin/env python3
"""
Script de nettoyage des webhook deliveries (GDPR Compliance).

Supprime les webhook_deliveries plus anciennes que RETENTION_DAYS jours.
Peut être exécuté via cron ou APScheduler.

Usage:
    python scripts/cleanup_webhook_deliveries.py [--retention-days 90] [--dry-run]

Cron example:
    0 3 * * * cd /app && python scripts/cleanup_webhook_deliveries.py >> /var/log/cleanup.log 2>&1
"""

import sys
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import func
from shared.infrastructure.database import SessionLocal
from shared.infrastructure.webhooks.models import WebhookDeliveryModel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DEFAULT_RETENTION_DAYS = 90


def cleanup_old_deliveries(retention_days: int = DEFAULT_RETENTION_DAYS, dry_run: bool = False) -> dict:
    """
    Nettoie les webhook_deliveries plus anciennes que retention_days jours.

    Args:
        retention_days: Nombre de jours de rétention (défaut: 90)
        dry_run: Si True, affiche seulement le nombre sans supprimer

    Returns:
        dict: Statistiques du nettoyage {deleted: int, cutoff_date: str}
    """
    db = SessionLocal()

    try:
        # Calculer la date de cutoff
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        logger.info(f"Début du nettoyage des deliveries > {retention_days} jours (avant {cutoff_date.date()})")

        # Compter les deliveries à supprimer
        count_query = db.query(func.count(WebhookDeliveryModel.id)).filter(
            WebhookDeliveryModel.delivered_at < cutoff_date
        )
        count = count_query.scalar()

        if count == 0:
            logger.info("Aucune delivery à nettoyer")
            return {
                'deleted': 0,
                'cutoff_date': cutoff_date.isoformat(),
                'dry_run': dry_run
            }

        logger.info(f"Nombre de deliveries à supprimer: {count}")

        if dry_run:
            logger.info("DRY RUN: Aucune suppression effectuée")
            return {
                'deleted': 0,
                'would_delete': count,
                'cutoff_date': cutoff_date.isoformat(),
                'dry_run': True
            }

        # Supprimer les anciennes deliveries
        delete_query = db.query(WebhookDeliveryModel).filter(
            WebhookDeliveryModel.delivered_at < cutoff_date
        )
        deleted_count = delete_query.delete(synchronize_session=False)
        db.commit()

        logger.info(f"✅ Nettoyage terminé: {deleted_count} deliveries supprimées")

        return {
            'deleted': deleted_count,
            'cutoff_date': cutoff_date.isoformat(),
            'dry_run': False
        }

    except Exception as e:
        logger.error(f"❌ Erreur lors du nettoyage: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Nettoie les webhook deliveries anciennes (GDPR compliance)'
    )
    parser.add_argument(
        '--retention-days',
        type=int,
        default=DEFAULT_RETENTION_DAYS,
        help=f'Nombre de jours de rétention (défaut: {DEFAULT_RETENTION_DAYS})'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Affiche seulement le nombre sans supprimer'
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Cleanup Webhook Deliveries - GDPR Compliance")
    logger.info("=" * 60)

    result = cleanup_old_deliveries(
        retention_days=args.retention_days,
        dry_run=args.dry_run
    )

    logger.info(f"Résultat: {result}")
    logger.info("=" * 60)

    return 0


if __name__ == '__main__':
    sys.exit(main())
