"""Service de delivery des webhooks avec retry exponentiel et signatures HMAC."""

import asyncio
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime
from typing import Optional, List
from fnmatch import fnmatch

import httpx
from sqlalchemy.orm import Session

from shared.infrastructure.event_bus.domain_event import DomainEvent
from shared.infrastructure.webhooks.models import WebhookModel, WebhookDeliveryModel

logger = logging.getLogger(__name__)

# Constantes
WEBHOOK_TIMEOUT_SECONDS = 10
RESPONSE_BODY_MAX_LENGTH = 1000
FAILURE_THRESHOLD = 10  # Désactivation automatique après 10 échecs
MAX_CONCURRENT_DELIVERIES = 50  # Limite parallélisme pour éviter webhook bombing


class WebhookDeliveryService:
    """
    Service de livraison des webhooks.

    Responsabilités:
    - Livrer les événements aux webhooks actifs
    - Gérer les retries avec exponentiel backoff (2, 4, 8 secondes)
    - Signer les requêtes avec HMAC-SHA256
    - Tracker les tentatives et la disponibilité du webhook
    - Désactiver automatiquement après trop d'échecs

    Note:
        Cette implémentation utilise httpx.AsyncClient pour les appels HTTP.
        Tous les appels sont asynchrones (async/await).
    """

    def __init__(self, db: Session):
        """
        Initialise le service de delivery.

        Args:
            db: Session SQLAlchemy pour accès à la base de données.
        """
        self.db = db
        self._semaphore = asyncio.Semaphore(MAX_CONCURRENT_DELIVERIES)

    async def deliver_all(self, event: DomainEvent) -> None:
        """
        Livre l'événement à tous les webhooks qui le matchent.

        La livraison se fait en parallèle pour tous les webhooks actifs.
        Les erreurs sur un webhook n'affectent pas les autres.

        Args:
            event: L'événement de domaine à livrer.
        """
        logger.info(f"Livraison événement {event.event_type} à tous les webhooks")

        # Récupérer tous les webhooks actifs
        webhooks = self.db.query(WebhookModel).filter(
            WebhookModel.is_active == True
        ).all()

        if not webhooks:
            logger.debug("Aucun webhook actif trouvé")
            return

        # Lancer les livraisons en parallèle
        tasks = [
            self.deliver(webhook, event)
            for webhook in webhooks
            if self._event_matches(event.event_type, webhook.events)
        ]

        if tasks:
            logger.debug(f"Lancement {len(tasks)} tâches de livraison parallèles")
            await asyncio.gather(*tasks, return_exceptions=True)

    async def deliver(self, webhook: WebhookModel, event: DomainEvent, attempt: int = 1) -> None:
        """
        Livre un événement à un webhook spécifique.

        Gère les retries avec exponentiel backoff:
        - Tentative 1: immédiate
        - Tentative 2: après 2 secondes (2^1)
        - Tentative 3: après 4 secondes (2^2)
        - Tentative 4: après 8 secondes (2^3)

        Protection contre webhook bombing: Utilise un sémaphore pour limiter
        les livraisons concurrentes à MAX_CONCURRENT_DELIVERIES.

        Args:
            webhook: Le webhook cible.
            event: L'événement à livrer.
            attempt: Numéro de tentative (pour retry interne).
        """
        async with self._semaphore:
            if attempt > 1:
                # Exponentiel backoff pour les retries: 2^(attempt-1) secondes
                backoff_seconds = 2 ** (attempt - 1)
                logger.info(
                    f"Retry webhook {webhook.id} pour {event.event_type}, "
                    f"tentative {attempt}/{webhook.max_retries + 1}, "
                    f"attente {backoff_seconds}s"
                )
                await asyncio.sleep(backoff_seconds)

            try:
                # Préparer le payload
                payload = self._serialize_event(event)

                # Calculer la signature HMAC
                signature = self._compute_hmac(webhook.secret, payload)

                # Effectuer la livraison HTTP
                async with httpx.AsyncClient(
                    timeout=WEBHOOK_TIMEOUT_SECONDS,
                    follow_redirects=True,
                    max_redirects=3
                ) as client:
                    start_time = time.time()

                    response = await client.post(
                        webhook.url,
                        json=payload,
                        headers={
                            "User-Agent": "Hub-Chantier-Webhooks/1.0",
                            "X-Hub-Chantier-Signature": f"sha256={signature}",
                            "X-Hub-Chantier-Event": event.event_type,
                            "Content-Type": "application/json",
                        },
                    )

                    response_time_ms = int((time.time() - start_time) * 1000)

                # Enregistrer la tentative
                self._record_delivery(
                    webhook=webhook,
                    event=event,
                    attempt=attempt,
                    success=response.is_success,
                    status_code=response.status_code,
                    response_body=response.text[:RESPONSE_BODY_MAX_LENGTH] if response.text else None,
                    response_time_ms=response_time_ms,
                    error_message=None,
                )

                if response.is_success:
                    # Succès: mettre à jour le webhook
                    webhook.last_triggered_at = datetime.now()
                    webhook.consecutive_failures = 0
                    self.db.commit()
                    logger.info(f"Webhook {webhook.id} livré avec succès pour {event.event_type}")
                else:
                    # Échec HTTP: retry si possible
                    logger.warning(
                        f"Webhook {webhook.id} retourna {response.status_code} pour {event.event_type}"
                    )
                    await self._handle_delivery_failure(webhook, event, attempt)

            except asyncio.TimeoutError as e:
                logger.warning(f"Webhook {webhook.id} timeout après {WEBHOOK_TIMEOUT_SECONDS}s: {e}")
                self._record_delivery(
                    webhook=webhook,
                    event=event,
                    attempt=attempt,
                    success=False,
                    status_code=None,
                    response_body=None,
                    response_time_ms=None,
                    error_message=f"Timeout après {WEBHOOK_TIMEOUT_SECONDS}s",
                )
                await self._handle_delivery_failure(webhook, event, attempt)

            except httpx.ConnectError as e:
                logger.warning(f"Webhook {webhook.id} impossible à contacter: {e}")
                self._record_delivery(
                    webhook=webhook,
                    event=event,
                    attempt=attempt,
                    success=False,
                    status_code=None,
                    response_body=None,
                    response_time_ms=None,
                    error_message=f"Erreur de connexion: {str(e)[:500]}",
                )
                await self._handle_delivery_failure(webhook, event, attempt)

            except Exception as e:
                logger.error(
                    f"Erreur inattendue livrant webhook {webhook.id}: {e}",
                    exc_info=True
                )
                self._record_delivery(
                    webhook=webhook,
                    event=event,
                    attempt=attempt,
                    success=False,
                    status_code=None,
                    response_body=None,
                    response_time_ms=None,
                    error_message=f"Erreur: {str(e)[:500]}",
                )
                await self._handle_delivery_failure(webhook, event, attempt)

    async def _handle_delivery_failure(self, webhook: WebhookModel, event: DomainEvent, attempt: int) -> None:
        """
        Gère un échec de livraison.

        Incrmente le compteur d'échecs et décide si un retry est nécessaire.
        Désactive le webhook après trop d'échecs consécutifs.

        Args:
            webhook: Le webhook en échec.
            event: L'événement à livrer.
            attempt: Le numéro de tentative actuelle.
        """
        webhook.consecutive_failures += 1
        self.db.commit()

        # Vérifier les conditions de retry
        if webhook.retry_enabled and attempt < webhook.max_retries + 1:
            # Relancer un retry
            await self.deliver(webhook, event, attempt=attempt + 1)
        else:
            # Pas de retry: vérifier si désactivation
            if webhook.consecutive_failures >= FAILURE_THRESHOLD:
                logger.warning(
                    f"Webhook {webhook.id} désactivé après {webhook.consecutive_failures} "
                    f"échecs consécutifs"
                )
                webhook.is_active = False
                self.db.commit()

    def _record_delivery(
        self,
        webhook: WebhookModel,
        event: DomainEvent,
        attempt: int,
        success: bool,
        status_code: Optional[int],
        response_body: Optional[str],
        response_time_ms: Optional[int],
        error_message: Optional[str],
    ) -> None:
        """
        Enregistre une tentative de livraison en base de données.

        Args:
            webhook: Le webhook concerné.
            event: L'événement livré.
            attempt: Numéro de tentative.
            success: Si la livraison a réussi (HTTP 2xx).
            status_code: Code HTTP de réponse.
            response_body: Corps de la réponse HTTP.
            response_time_ms: Temps de réponse en millisecondes.
            error_message: Message d'erreur si applicable.
        """
        delivery = WebhookDeliveryModel(
            webhook_id=webhook.id,
            event_type=event.event_type,
            payload=self._serialize_event(event),
            status_code=status_code,
            response_body=response_body,
            success=success,
            error_message=error_message,
            response_time_ms=response_time_ms,
            attempt_number=attempt,
        )
        self.db.add(delivery)
        self.db.commit()

    @staticmethod
    def _event_matches(event_type: str, patterns: List[str]) -> bool:
        """
        Vérifie si un événement matche avec les patterns spécifiés.

        Supports les wildcards:
        - "chantier.*" matche "chantier.created", "chantier.updated", etc.
        - "*.created" matche "chantier.created", "user.created", etc.
        - "*" matche tous les événements

        Args:
            event_type: Le type d'événement (ex: "chantier.created")
            patterns: Liste de patterns à matcher (ex: ["chantier.*", "user.created"])

        Returns:
            True si l'événement matche au moins un pattern.
        """
        for pattern in patterns:
            if fnmatch(event_type, pattern):
                return True
        return False

    @staticmethod
    def _compute_hmac(secret: str, payload: str) -> str:
        """
        Calcule la signature HMAC-SHA256 du payload.

        La signature est utilisée pour vérifier l'authenticité du webhook côté client.
        Elle est envoyée dans le header X-Hub-Chantier-Signature.

        Args:
            secret: Le secret partagé du webhook.
            payload: Le payload JSON sérialisé.

        Returns:
            La signature hexadécimale (sans le préfixe "sha256=").

        Exemple:
            >>> service = WebhookDeliveryService(db)
            >>> sig = service._compute_hmac("my-secret", '{"data": "test"}')
            >>> sig
            'a1b2c3d4e5f6...'
        """
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    def _serialize_event(event: DomainEvent) -> str:
        """
        Sérialise un événement de domaine en JSON pour livraison.

        Ajoute des métadonnées comme timestamp et event_type.

        Args:
            event: L'événement de domaine.

        Returns:
            Le JSON sérialisé (string).
        """
        event_dict = {
            "event_type": event.event_type,
            "event_id": str(event.event_id),
            "timestamp": event.occurred_at.isoformat(),
            "data": event.to_dict() if hasattr(event, 'to_dict') else event.__dict__,
        }
        return json.dumps(event_dict, default=str)
