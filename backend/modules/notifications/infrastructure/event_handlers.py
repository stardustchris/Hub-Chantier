"""Event handlers pour creer des notifications automatiquement."""

import re
import logging
from typing import List, Optional

from shared.infrastructure.event_bus import event_handler, EventBus
from shared.infrastructure.database import SessionLocal
from shared.application.ports import EntityInfoService
from shared.infrastructure.entity_info_impl import SQLAlchemyEntityInfoService
from modules.dashboard.domain.events import CommentAddedEvent, LikeAddedEvent
from ..domain.entities import Notification
from ..domain.value_objects import NotificationType
from .persistence import SQLAlchemyNotificationRepository

logger = logging.getLogger(__name__)


def parse_mentions(content: str) -> List[str]:
    """
    Parse les mentions @ dans un contenu.

    Args:
        content: Le texte du commentaire.

    Returns:
        Liste des usernames mentionnes (sans le @).
    """
    # Pattern pour @username (lettres, chiffres, tirets, underscores)
    pattern = r"@([a-zA-Z0-9_-]+)"
    return re.findall(pattern, content)


def get_user_id_by_email_or_name(db, identifier: str) -> int | None:
    """
    Trouve l'ID d'un utilisateur par son email ou nom.

    Args:
        db: Session de base de donnees.
        identifier: Email ou nom d'utilisateur.

    Returns:
        ID de l'utilisateur ou None.
    """
    from modules.auth.infrastructure.persistence import UserModel

    # Chercher par email complet ou partiel
    user = db.query(UserModel).filter(
        (UserModel.email.ilike(f"{identifier}%")) |
        (UserModel.nom.ilike(f"%{identifier}%")) |
        (UserModel.prenom.ilike(f"%{identifier}%"))
    ).first()

    return user.id if user else None


def get_user_name(db, user_id: int) -> str:
    """Recupere le nom complet d'un utilisateur via EntityInfoService."""
    entity_info = SQLAlchemyEntityInfoService(db)
    user_info = entity_info.get_user_info(user_id)
    return user_info.nom if user_info else "Utilisateur"


def get_comment_content(db, comment_id: int) -> str | None:
    """Recupere le contenu d'un commentaire."""
    from modules.dashboard.infrastructure.persistence import CommentModel

    comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    return comment.content if comment else None


@event_handler(CommentAddedEvent)
def handle_comment_added(event: CommentAddedEvent) -> None:
    """
    Gere l'evenement CommentAddedEvent.

    - Cree une notification pour l'auteur du post (si different du commentateur)
    - Parse les mentions @ et cree des notifications pour les utilisateurs mentionnes
    """
    logger.info(f"Handling CommentAddedEvent: comment_id={event.comment_id}, post_id={event.post_id}")

    db = SessionLocal()
    try:
        repo = SQLAlchemyNotificationRepository(db)
        author_name = get_user_name(db, event.author_id)
        comment_content = get_comment_content(db, event.comment_id)

        # 1. Notifier l'auteur du post (sauf s'il commente son propre post)
        if event.post_author_id != event.author_id:
            notification = Notification(
                user_id=event.post_author_id,
                type=NotificationType.COMMENT_ADDED,
                title="Nouveau commentaire",
                message=f"{author_name} a commente votre publication",
                related_post_id=event.post_id,
                related_comment_id=event.comment_id,
                triggered_by_user_id=event.author_id,
            )
            repo.save(notification)
            logger.info(f"Created notification for post author {event.post_author_id}")

        # 2. Parser les mentions @ dans le commentaire
        if comment_content:
            mentions = parse_mentions(comment_content)
            for mention in mentions:
                mentioned_user_id = get_user_id_by_email_or_name(db, mention)
                if mentioned_user_id and mentioned_user_id != event.author_id:
                    # Ne pas notifier l'auteur du commentaire s'il se mentionne lui-meme
                    notification = Notification(
                        user_id=mentioned_user_id,
                        type=NotificationType.MENTION,
                        title="Vous avez ete mentionne",
                        message=f"{author_name} vous a mentionne dans un commentaire",
                        related_post_id=event.post_id,
                        related_comment_id=event.comment_id,
                        triggered_by_user_id=event.author_id,
                    )
                    repo.save(notification)
                    logger.info(f"Created mention notification for user {mentioned_user_id}")

    except Exception as e:
        logger.error(f"Error handling CommentAddedEvent: {e}")
    finally:
        db.close()


@event_handler(LikeAddedEvent)
def handle_like_added(event: LikeAddedEvent) -> None:
    """
    Gere l'evenement LikeAddedEvent.

    Cree une notification pour l'auteur du post (si different du likeur).
    """
    logger.info(f"Handling LikeAddedEvent: like_id={event.like_id}, post_id={event.post_id}")

    # Ne pas notifier si l'utilisateur like son propre post
    if event.post_author_id == event.user_id:
        return

    db = SessionLocal()
    try:
        repo = SQLAlchemyNotificationRepository(db)
        liker_name = get_user_name(db, event.user_id)

        notification = Notification(
            user_id=event.post_author_id,
            type=NotificationType.LIKE_ADDED,
            title="Nouveau like",
            message=f"{liker_name} a aime votre publication",
            related_post_id=event.post_id,
            triggered_by_user_id=event.user_id,
        )
        repo.save(notification)
        logger.info(f"Created like notification for post author {event.post_author_id}")

    except Exception as e:
        logger.error(f"Error handling LikeAddedEvent: {e}")
    finally:
        db.close()


def register_notification_handlers() -> None:
    """
    Enregistre tous les handlers de notifications.

    Cette fonction est appelee au demarrage de l'application.
    Les decorateurs @event_handler font l'enregistrement automatiquement,
    mais cette fonction force leur import.
    """
    logger.info("Notification event handlers registered")
