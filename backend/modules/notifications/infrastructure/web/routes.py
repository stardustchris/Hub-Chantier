"""Routes API pour le module notifications."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from modules.auth.infrastructure.web.dependencies import get_current_user_id
from shared.infrastructure.database import get_db
from shared.infrastructure.config import settings
from ...application.dtos import NotificationListDTO, MarkAsReadDTO
from ...application.use_cases import (
    GetNotificationsUseCase,
    MarkAsReadUseCase,
    DeleteNotificationUseCase,
)
from .dependencies import (
    get_notifications_use_case,
    get_mark_as_read_use_case,
    get_delete_notification_use_case,
)
from ...domain.entities import Notification
from ...domain.value_objects import NotificationType
from ..persistence import SQLAlchemyNotificationRepository


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListDTO)
async def get_notifications(
    unread_only: bool = Query(False, description="Retourner uniquement les non lues"),
    skip: int = Query(0, ge=0, description="Nombre d'elements a sauter"),
    limit: int = Query(50, ge=1, le=100, description="Nombre maximum d'elements"),
    current_user_id: int = Depends(get_current_user_id),
    use_case: GetNotificationsUseCase = Depends(get_notifications_use_case),
):
    """
    Recupere les notifications de l'utilisateur connecte.

    - **unread_only**: Si true, retourne uniquement les notifications non lues
    - **skip**: Pagination - nombre d'elements a sauter
    - **limit**: Pagination - nombre maximum d'elements (max 100)
    """
    return use_case.execute(
        user_id=current_user_id,
        unread_only=unread_only,
        skip=skip,
        limit=limit,
    )


@router.get("/unread-count")
async def get_unread_count(
    current_user_id: int = Depends(get_current_user_id),
    use_case: GetNotificationsUseCase = Depends(get_notifications_use_case),
):
    """Retourne le nombre de notifications non lues."""
    result = use_case.execute(user_id=current_user_id, limit=0)
    return {"unread_count": result.unread_count}


@router.patch("/read")
async def mark_notifications_as_read(
    data: MarkAsReadDTO,
    current_user_id: int = Depends(get_current_user_id),
    use_case: MarkAsReadUseCase = Depends(get_mark_as_read_use_case),
):
    """
    Marque des notifications comme lues.

    - Si **notification_ids** est fourni, marque uniquement ces notifications
    - Si **notification_ids** est null/absent, marque TOUTES les notifications
    """
    count = use_case.execute(
        user_id=current_user_id,
        notification_ids=data.notification_ids,
    )
    return {"marked_count": count}


@router.patch("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user_id: int = Depends(get_current_user_id),
    use_case: MarkAsReadUseCase = Depends(get_mark_as_read_use_case),
):
    """Marque une notification specifique comme lue."""
    count = use_case.execute(
        user_id=current_user_id,
        notification_ids=[notification_id],
    )
    if count == 0:
        raise HTTPException(status_code=404, detail="Notification non trouvee")
    return {"success": True}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user_id: int = Depends(get_current_user_id),
    use_case: DeleteNotificationUseCase = Depends(get_delete_notification_use_case),
):
    """Supprime une notification."""
    try:
        count = use_case.execute(
            user_id=current_user_id,
            notification_id=notification_id,
        )
        if count == 0:
            raise HTTPException(status_code=404, detail="Notification non trouvee")
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("")
async def delete_all_notifications(
    current_user_id: int = Depends(get_current_user_id),
    use_case: DeleteNotificationUseCase = Depends(get_delete_notification_use_case),
):
    """Supprime toutes les notifications de l'utilisateur."""
    count = use_case.execute(user_id=current_user_id)
    return {"deleted_count": count}


@router.post("/debug/seed")
async def seed_test_notifications(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Cree des notifications de test pour l'utilisateur connecte.

    Disponible uniquement en mode DEBUG.
    """
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="Disponible uniquement en mode DEBUG")

    repo = SQLAlchemyNotificationRepository(db)

    test_notifications = [
        Notification(
            user_id=current_user_id,
            type=NotificationType.COMMENT_ADDED,
            title="Nouveau commentaire",
            message="Jean Dupont a commente votre publication sur le chantier Villa Duplex",
            related_post_id=1,
            triggered_by_user_id=2,
        ),
        Notification(
            user_id=current_user_id,
            type=NotificationType.MENTION,
            title="Vous avez ete mentionne",
            message="@admin Pierre Martin vous a mentionne dans un commentaire",
            related_post_id=1,
            related_comment_id=1,
            triggered_by_user_id=3,
        ),
        Notification(
            user_id=current_user_id,
            type=NotificationType.LIKE_ADDED,
            title="Nouveau like",
            message="Marie Durand a aime votre publication",
            related_post_id=2,
            triggered_by_user_id=4,
        ),
        Notification(
            user_id=current_user_id,
            type=NotificationType.DOCUMENT_ADDED,
            title="Nouveau document",
            message="Chantier Villa Duplex : Plan electrique v2 ajoute",
            related_chantier_id=1,
            related_document_id=1,
            triggered_by_user_id=2,
        ),
        Notification(
            user_id=current_user_id,
            type=NotificationType.DOCUMENT_ADDED,
            title="Nouveau document",
            message="Chantier Residence Les Pins : CCTP Plomberie mis a jour",
            related_chantier_id=2,
            related_document_id=2,
            triggered_by_user_id=3,
        ),
        Notification(
            user_id=current_user_id,
            type=NotificationType.CHANTIER_ASSIGNMENT,
            title="Nouvelle affectation",
            message="Vous avez ete affecte au chantier Residence Les Pins",
            related_chantier_id=2,
        ),
        Notification(
            user_id=current_user_id,
            type=NotificationType.SIGNALEMENT_CREATED,
            title="Nouveau signalement",
            message="Signalement securite sur le chantier Villa Duplex",
            related_chantier_id=1,
        ),
        Notification(
            user_id=current_user_id,
            type=NotificationType.TACHE_ASSIGNED,
            title="Nouvelle tache",
            message="Tache 'Pose des gaines electriques' vous a ete assignee",
            related_chantier_id=1,
        ),
    ]

    created = repo.save_many(test_notifications)
    return {"created_count": len(created), "message": "Notifications de test creees"}
