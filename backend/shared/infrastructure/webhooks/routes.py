"""Routes API pour la gestion des webhooks."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from pydantic import BaseModel, HttpUrl, Field, field_validator
from sqlalchemy.orm import Session
import socket
import ipaddress
from urllib.parse import urlparse

from shared.infrastructure.web import get_current_user_id
from shared.infrastructure.database import get_db
from shared.infrastructure.rate_limiter import limiter
from shared.infrastructure.webhooks.models import WebhookModel, WebhookDeliveryModel
from shared.infrastructure.webhooks.webhook_service import WebhookDeliveryService
from shared.infrastructure.event_bus.domain_event import DomainEvent
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Configuration limits
MAX_WEBHOOKS_PER_USER = 20


# ============================================================================
# Pydantic Models
# ============================================================================

class WebhookCreate(BaseModel):
    """Modèle pour créer un webhook."""

    url: HttpUrl = Field(..., description="URL destination du webhook (HTTPS uniquement)")
    events: List[str] = Field(..., description="Patterns d'événements (ex: ['chantier.*', 'heures.validated'])")
    description: Optional[str] = Field(None, description="Description du webhook")

    @field_validator('url')
    @classmethod
    def enforce_https_and_validate_ssrf(cls, v):
        """Enforce HTTPS and validate against SSRF attacks."""
        # Enforce HTTPS only
        if v.scheme != 'https':
            raise ValueError('Webhook URLs must use HTTPS for security')

        # SSRF protection: Block private/internal IPs
        BLOCKED_NETWORKS = [
            ipaddress.ip_network('127.0.0.0/8'),    # localhost
            ipaddress.ip_network('10.0.0.0/8'),     # private
            ipaddress.ip_network('172.16.0.0/12'),  # private
            ipaddress.ip_network('192.168.0.0/16'), # private
            ipaddress.ip_network('169.254.0.0/16'), # link-local (AWS metadata)
            ipaddress.ip_network('::1/128'),        # IPv6 localhost
            ipaddress.ip_network('fc00::/7'),       # IPv6 private
        ]

        try:
            # Resolve hostname to IP
            hostname = v.host
            ip_str = socket.gethostbyname(hostname)
            ip = ipaddress.ip_address(ip_str)

            # Check if IP is in blocked networks
            for network in BLOCKED_NETWORKS:
                if ip in network:
                    raise ValueError(
                        f'Webhook URL resolves to private/internal IP ({ip}). '
                        'This is blocked for security (SSRF protection).'
                    )
        except socket.gaierror:
            raise ValueError(f'Cannot resolve hostname: {hostname}')
        except ValueError as e:
            if 'private/internal' in str(e):
                raise
            # Other ValueError (invalid IP format) - let it pass

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/webhooks/events",
                "events": ["chantier.*", "heures.validated"],
                "description": "Webhook intégration système X",
            }
        }


class WebhookResponse(BaseModel):
    """Modèle pour la réponse webhook (sans secret)."""

    id: UUID
    url: str
    events: List[str]
    description: Optional[str]
    is_active: bool
    last_triggered_at: Optional[str]
    consecutive_failures: int
    retry_enabled: bool
    max_retries: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

    @staticmethod
    def from_model(webhook: WebhookModel) -> "WebhookResponse":
        """Crée une réponse à partir d'un modèle."""
        return WebhookResponse(
            id=webhook.id,
            url=webhook.url,
            events=webhook.events,
            description=webhook.description,
            is_active=webhook.is_active,
            last_triggered_at=webhook.last_triggered_at.isoformat() if webhook.last_triggered_at else None,
            consecutive_failures=webhook.consecutive_failures,
            retry_enabled=webhook.retry_enabled,
            max_retries=webhook.max_retries,
            created_at=webhook.created_at.isoformat(),
            updated_at=webhook.updated_at.isoformat(),
        )


class WebhookCreatedResponse(BaseModel):
    """Réponse à la création d'un webhook (inclut le secret une fois)."""

    id: UUID
    url: str
    events: List[str]
    description: Optional[str]
    secret: str = Field(description="Secret HMAC - À CONSERVER ! Ce secret ne sera affiché qu'une seule fois")
    created_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "url": "https://example.com/webhooks",
                "events": ["chantier.*"],
                "description": "Mon webhook",
                "secret": "whsec_1234567890abcdef...",
                "created_at": "2026-01-28T12:34:56.789Z",
            }
        }


class WebhookDeliveryResponse(BaseModel):
    """Modèle pour une tentative de livraison."""

    id: UUID
    event_type: str
    success: Optional[bool]
    status_code: Optional[int]
    error_message: Optional[str]
    response_time_ms: Optional[int]
    attempt_number: int
    delivered_at: str

    class Config:
        from_attributes = True


class WebhookListResponse(BaseModel):
    """Modèle pour la liste des webhooks."""

    total: int
    webhooks: List[WebhookResponse]


class WebhookDeliveryListResponse(BaseModel):
    """Modèle pour la liste des tentatives de livraison."""

    total: int
    deliveries: List[WebhookDeliveryResponse]


# ============================================================================
# Routes
# ============================================================================

@router.post("", response_model=WebhookCreatedResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_webhook(
    request: Request,  # Required by slowapi
    data: WebhookCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> WebhookCreatedResponse:
    """
    Crée un nouveau webhook.

    Le secret retourné une seule fois - À CONSERVER ! Il ne sera plus affiché.

    **Limites**:
    - Rate limit: 10 webhooks par minute
    - Maximum: 20 webhooks actifs par utilisateur

    **Patterns d'événements** (fnmatch):
    - `chantier.*` - tous les événements liés aux chantiers
    - `*.created` - tous les événements de création
    - `*` - tous les événements

    Args:
        request: Request FastAPI (requis par slowapi)
        data: Données du webhook (url, events, description)
        current_user_id: ID de l'utilisateur connecté
        db: Session base de données

    Returns:
        Le webhook créé avec le secret (UNE FOIS SEULEMENT)

    Raises:
        HTTPException: 429 si rate limit dépassé, 400 si quota webhooks atteint
    """
    import secrets

    # Vérifier le quota de webhooks par utilisateur
    existing_webhooks_count = db.query(WebhookModel).filter(
        WebhookModel.user_id == current_user_id,
        WebhookModel.is_active == True
    ).count()

    if existing_webhooks_count >= MAX_WEBHOOKS_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_WEBHOOKS_PER_USER} webhooks actifs atteint. "
                   f"Supprimez un webhook existant avant d'en créer un nouveau."
        )

    # Générer un secret aléatoire
    secret = secrets.token_hex(32)  # 64 caractères hexadécimaux

    # Créer le webhook
    webhook = WebhookModel(
        user_id=current_user_id,
        url=str(data.url),
        events=data.events,
        secret=secret,
        description=data.description,
    )

    db.add(webhook)
    db.commit()
    db.refresh(webhook)

    logger.info(f"Webhook créé: {webhook.id} pour user {current_user_id}")

    return WebhookCreatedResponse(
        id=webhook.id,
        url=webhook.url,
        events=webhook.events,
        description=webhook.description,
        secret=secret,  # Retourner le secret UNE FOIS
        created_at=webhook.created_at.isoformat(),
    )


@router.get("", response_model=WebhookListResponse)
@limiter.limit("30/minute")
async def list_webhooks(
    request: Request,  # Required by slowapi
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(50, ge=1, le=100, description="Nombre max d'éléments"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> WebhookListResponse:
    """
    Liste les webhooks de l'utilisateur connecté.

    Args:
        skip: Pagination offset
        limit: Nombre max de résultats
        current_user_id: ID de l'utilisateur connecté
        db: Session base de données

    Returns:
        Liste des webhooks (sans secret)
    """
    query = db.query(WebhookModel).filter(WebhookModel.user_id == current_user_id)
    total = query.count()

    webhooks = query.offset(skip).limit(limit).all()

    return WebhookListResponse(
        total=total,
        webhooks=[WebhookResponse.from_model(w) for w in webhooks],
    )


@router.get("/{webhook_id}", response_model=WebhookResponse)
@limiter.limit("30/minute")
async def get_webhook(
    request: Request,  # Required by slowapi
    webhook_id: UUID,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> WebhookResponse:
    """
    Récupère les détails d'un webhook.

    Args:
        webhook_id: ID du webhook
        current_user_id: ID de l'utilisateur connecté
        db: Session base de données

    Returns:
        Les détails du webhook (sans secret)

    Raises:
        HTTPException: 404 si webhook non trouvé ou non propriétaire
    """
    webhook = db.query(WebhookModel).filter(
        WebhookModel.id == webhook_id,
        WebhookModel.user_id == current_user_id,
    ).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook non trouvé")

    return WebhookResponse.from_model(webhook)


@router.get("/{webhook_id}/deliveries", response_model=WebhookDeliveryListResponse)
@limiter.limit("30/minute")
async def get_webhook_deliveries(
    request: Request,  # Required by slowapi
    webhook_id: UUID,
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=100, description="Nombre max (max 100)"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> WebhookDeliveryListResponse:
    """
    Récupère l'historique des tentatives de livraison d'un webhook.

    Permet de déboguer les webhooks en consultant les dernières tentatives.

    Args:
        webhook_id: ID du webhook
        skip: Pagination offset
        limit: Nombre max de résultats
        current_user_id: ID de l'utilisateur connecté
        db: Session base de données

    Returns:
        Historique des livraisons (dernières d'abord)

    Raises:
        HTTPException: 404 si webhook non trouvé ou non propriétaire
    """
    # Vérifier que le webhook appartient à l'utilisateur
    webhook = db.query(WebhookModel).filter(
        WebhookModel.id == webhook_id,
        WebhookModel.user_id == current_user_id,
    ).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook non trouvé")

    # Récupérer les deliveries (les plus récentes d'abord)
    query = db.query(WebhookDeliveryModel).filter(
        WebhookDeliveryModel.webhook_id == webhook_id
    ).order_by(WebhookDeliveryModel.delivered_at.desc())

    total = query.count()
    deliveries = query.offset(skip).limit(limit).all()

    return WebhookDeliveryListResponse(
        total=total,
        deliveries=[
            WebhookDeliveryResponse(
                id=d.id,
                event_type=d.event_type,
                success=d.success,
                status_code=d.status_code,
                error_message=d.error_message,
                response_time_ms=d.response_time_ms,
                attempt_number=d.attempt_number,
                delivered_at=d.delivered_at.isoformat(),
            )
            for d in deliveries
        ],
    )


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
async def delete_webhook(
    request: Request,  # Required by slowapi
    webhook_id: UUID,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> None:
    """
    Désactive/supprime un webhook.

    Le webhook n'est pas supprimé de la base (conservation audit)
    mais est désactivé pour ne plus être appelé.

    Args:
        webhook_id: ID du webhook
        current_user_id: ID de l'utilisateur connecté
        db: Session base de données

    Raises:
        HTTPException: 404 si webhook non trouvé ou non propriétaire
    """
    webhook = db.query(WebhookModel).filter(
        WebhookModel.id == webhook_id,
        WebhookModel.user_id == current_user_id,
    ).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook non trouvé")

    webhook.is_active = False
    db.commit()

    logger.info(f"Webhook désactivé: {webhook_id}")


@router.post("/{webhook_id}/test", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("5/minute")
async def test_webhook(
    request: Request,  # Required by slowapi
    webhook_id: UUID,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> dict:
    """
    Envoie un événement de test au webhook.

    Permet de vérifier que le webhook est correctement configuré.
    La livraison se fait de manière asynchrone.

    Args:
        webhook_id: ID du webhook
        current_user_id: ID de l'utilisateur connecté
        db: Session base de données

    Returns:
        Statut de l'envoi de test

    Raises:
        HTTPException: 404 si webhook non trouvé ou non propriétaire
    """
    import asyncio

    webhook = db.query(WebhookModel).filter(
        WebhookModel.id == webhook_id,
        WebhookModel.user_id == current_user_id,
    ).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook non trouvé")

    # Créer un événement de test
    class TestEvent(DomainEvent):
        """Événement de test pour webhooks."""

        event_type = "webhook.test"

        def __init__(self):
            super().__init__()
            self.test_data = {
                "message": "Ceci est un événement de test pour votre webhook",
                "webhook_id": str(webhook_id),
            }

        def to_dict(self):
            return self.test_data

    test_event = TestEvent()

    # Lancer la livraison de test
    service = WebhookDeliveryService(db)

    # Lancer en tâche asynchrone pour ne pas bloquer la réponse
    try:
        asyncio.create_task(service.deliver(webhook, test_event))
    except RuntimeError:
        # En cas d'erreur avec event loop, on peut ignorer (la tâche n'est pas critique)
        logger.warning(f"Impossible de créer tâche async pour test webhook {webhook_id}")

    logger.info(f"Test webhook lancé pour {webhook_id} (user {current_user_id})")
    return {"status": "Test lancé", "webhook_id": str(webhook_id)}
