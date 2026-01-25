"""Implementation SQLAlchemy du NotificationRepository."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from .models import NotificationModel
from ...domain.entities import Notification
from ...domain.value_objects import NotificationType
from ...domain.repositories import NotificationRepository


class SQLAlchemyNotificationRepository(NotificationRepository):
    """Implementation SQLAlchemy du repository de notifications."""

    def __init__(self, db: Session):
        """
        Initialise le repository.

        Args:
            db: Session SQLAlchemy.
        """
        self._db = db

    def find_by_id(self, notification_id: int) -> Optional[Notification]:
        """Trouve une notification par son ID."""
        model = self._db.query(NotificationModel).filter(
            NotificationModel.id == notification_id
        ).first()
        return self._to_entity(model) if model else None

    def find_by_user(
        self,
        user_id: int,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Notification]:
        """Recupere les notifications d'un utilisateur."""
        query = self._db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id
        )

        if unread_only:
            query = query.filter(NotificationModel.is_read == False)  # noqa: E712

        query = query.order_by(NotificationModel.created_at.desc())
        query = query.offset(skip).limit(limit)

        return [self._to_entity(m) for m in query.all()]

    def count_unread(self, user_id: int) -> int:
        """Compte les notifications non lues d'un utilisateur."""
        return self._db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id,
            NotificationModel.is_read == False,  # noqa: E712
        ).count()

    def save(self, notification: Notification) -> Notification:
        """Persiste une notification."""
        if notification.id:
            # Mise a jour
            model = self._db.query(NotificationModel).filter(
                NotificationModel.id == notification.id
            ).first()
            if model:
                self._update_model(model, notification)
                self._db.commit()
                self._db.refresh(model)
                return self._to_entity(model)

        # Creation
        model = self._to_model(notification)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def save_many(self, notifications: List[Notification]) -> List[Notification]:
        """Persiste plusieurs notifications en une transaction."""
        models = [self._to_model(n) for n in notifications]
        self._db.add_all(models)
        self._db.commit()
        for model in models:
            self._db.refresh(model)
        return [self._to_entity(m) for m in models]

    def delete(self, notification_id: int) -> bool:
        """Supprime une notification."""
        result = self._db.query(NotificationModel).filter(
            NotificationModel.id == notification_id
        ).delete()
        self._db.commit()
        return result > 0

    def delete_all_for_user(self, user_id: int) -> int:
        """Supprime toutes les notifications d'un utilisateur."""
        result = self._db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id
        ).delete()
        self._db.commit()
        return result

    def mark_all_as_read(self, user_id: int) -> int:
        """Marque toutes les notifications d'un utilisateur comme lues."""
        now = datetime.now()
        result = self._db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id,
            NotificationModel.is_read == False,  # noqa: E712
        ).update({
            NotificationModel.is_read: True,
            NotificationModel.read_at: now,
        })
        self._db.commit()
        return result

    def find_by_type(
        self,
        user_id: int,
        notification_type: NotificationType,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Notification]:
        """Recupere les notifications d'un type specifique."""
        query = self._db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id,
            NotificationModel.type == notification_type.value,
        ).order_by(NotificationModel.created_at.desc())

        query = query.offset(skip).limit(limit)
        return [self._to_entity(m) for m in query.all()]

    def _to_entity(self, model: NotificationModel) -> Notification:
        """Convertit un modele en entite."""
        return Notification(
            id=model.id,
            user_id=model.user_id,
            type=NotificationType(model.type),
            title=model.title,
            message=model.message,
            is_read=model.is_read,
            read_at=model.read_at,
            related_post_id=model.related_post_id,
            related_comment_id=model.related_comment_id,
            related_chantier_id=model.related_chantier_id,
            related_document_id=model.related_document_id,
            triggered_by_user_id=model.triggered_by_user_id,
            metadata=model.extra_data or {},
            created_at=model.created_at,
        )

    def _to_model(self, entity: Notification) -> NotificationModel:
        """Convertit une entite en modele."""
        return NotificationModel(
            id=entity.id,
            user_id=entity.user_id,
            type=entity.type.value,
            title=entity.title,
            message=entity.message,
            is_read=entity.is_read,
            read_at=entity.read_at,
            related_post_id=entity.related_post_id,
            related_comment_id=entity.related_comment_id,
            related_chantier_id=entity.related_chantier_id,
            related_document_id=entity.related_document_id,
            triggered_by_user_id=entity.triggered_by_user_id,
            extra_data=entity.metadata if entity.metadata else None,
            created_at=entity.created_at,
        )

    def _update_model(self, model: NotificationModel, entity: Notification) -> None:
        """Met a jour un modele depuis une entite."""
        model.is_read = entity.is_read
        model.read_at = entity.read_at
        model.title = entity.title
        model.message = entity.message
        model.extra_data = entity.metadata if entity.metadata else None
