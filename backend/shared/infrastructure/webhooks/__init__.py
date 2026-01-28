"""Webhooks - Intégrations temps réel pour Hub Chantier.

Ce module implémente un système de webhooks permettant aux utilisateurs de recevoir
des événements en temps réel via des HTTP callbacks.

Caractéristiques:
- Livraison automatique des événements de domaine
- Signatures HMAC-SHA256 pour sécurité
- Retry exponentiel (2, 4, 8 secondes)
- Désactivation automatique après 10 échecs
- Pattern matching des événements (wildcards)
- Historique complet des tentatives
- Nettoyage automatique des deliveries anciennes (GDPR)

Architecture:
- models.py: SQLAlchemy ORM models (WebhookModel, WebhookDeliveryModel)
- webhook_service.py: Service de livraison avec retry logic
- event_listener.py: Hook dans l'event bus pour déclencher les webhooks
- routes.py: API REST pour la gestion des webhooks
- cleanup_scheduler.py: Nettoyage automatique GDPR (90 jours rétention)
"""

from .models import WebhookModel, WebhookDeliveryModel
from .webhook_service import WebhookDeliveryService
from .event_listener import webhook_event_handler
from .routes import router
from .cleanup_scheduler import start_cleanup_scheduler, stop_cleanup_scheduler, run_cleanup_now

__all__ = [
    'WebhookModel',
    'WebhookDeliveryModel',
    'WebhookDeliveryService',
    'webhook_event_handler',
    'router',
    'start_cleanup_scheduler',
    'stop_cleanup_scheduler',
    'run_cleanup_now',
]
