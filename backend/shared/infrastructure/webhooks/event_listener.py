"""Listener d'événements pour déclencher les webhooks."""

import asyncio
import logging
from typing import Any

from shared.infrastructure.event_bus.domain_event import DomainEvent
from shared.infrastructure.database import SessionLocal
from shared.infrastructure.webhooks.webhook_service import WebhookDeliveryService

logger = logging.getLogger(__name__)


async def webhook_event_handler(event: DomainEvent) -> None:
    """
    Handler déclenché pour chaque événement de domaine.

    S'abonne à TOUS les événements via event_bus.subscribe_all().
    Pour chaque événement, lance la livraison asynchrone aux webhooks actifs
    qui matchent le pattern d'événement.

    Les erreurs sont loggées mais ne bloquent pas le reste du système.

    Args:
        event: L'événement de domaine publié.

    Note:
        Cette fonction est asynchrone et peut être appelée en parallèle
        avec d'autres handlers par le event bus.
    """
    logger.debug(f"Événement reçu: {event.event_type}")

    db = SessionLocal()
    try:
        webhook_service = WebhookDeliveryService(db)
        await webhook_service.deliver_all(event)
    except Exception as e:
        logger.error(
            f"Erreur déclenchement webhooks pour {event.event_type}: {e}",
            exc_info=True
        )
    finally:
        db.close()


# Log pour confirmer que le handler a été défini
logger.info("Webhook event handler créé et prêt pour enregistrement")
