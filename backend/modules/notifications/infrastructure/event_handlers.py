"""Event handlers pour creer des notifications automatiquement."""

import re
import logging
from typing import List, Optional

from shared.infrastructure.event_bus import event_handler
from shared.infrastructure.database import SessionLocal
from shared.infrastructure.entity_info_impl import SQLAlchemyEntityInfoService
from modules.dashboard.domain.events import CommentAddedEvent, LikeAddedEvent
from modules.pointages.domain.events.heures_validated import HeuresValidatedEvent
from modules.pointages.domain.events import (
    PointageSubmittedEvent,
    PointageRejectedEvent,
)
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

    Uses shared user_queries helper to avoid importing UserModel from auth module.

    Args:
        db: Session de base de donnees.
        identifier: Email ou nom d'utilisateur.

    Returns:
        ID de l'utilisateur ou None.
    """
    from shared.infrastructure.user_queries import find_user_id_by_email_or_name

    return find_user_id_by_email_or_name(db, identifier)


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


@event_handler('heures.validated')
def handle_heures_validated(event) -> None:
    """
    Gere l'evenement HeuresValidatedEvent.

    Notifie le compagnon que ses heures ont ete validees et journalise
    l'evenement pour le systeme de paie.
    """
    data = event.data if hasattr(event, 'data') and isinstance(event.data, dict) else {}
    user_id = data.get('user_id')
    validated_by = data.get('validated_by')
    heures = data.get('heures_travaillees', 0)
    heures_sup = data.get('heures_supplementaires', 0)
    chantier_id = data.get('chantier_id')
    date_str = data.get('date', '')

    if not user_id or not validated_by:
        logger.warning(f"HeuresValidatedEvent sans user_id ou validated_by: {data}")
        return

    # Ne pas notifier le validateur s'il valide ses propres heures
    if user_id == validated_by:
        logger.info(f"Auto-validation heures user_id={user_id}, pas de notification")
        return

    logger.info(f"Handling heures.validated: user_id={user_id}, validated_by={validated_by}")

    db = SessionLocal()
    try:
        repo = SQLAlchemyNotificationRepository(db)
        validator_name = get_user_name(db, validated_by)

        total_heures = heures + heures_sup
        message = f"{validator_name} a valide vos heures du {date_str} ({total_heures}h)"

        notification = Notification(
            user_id=user_id,
            type=NotificationType.SYSTEM,
            title="Heures validees",
            message=message,
            related_chantier_id=chantier_id,
            triggered_by_user_id=validated_by,
        )
        repo.save(notification)
        logger.info(f"Created heures validated notification for user {user_id}")

    except Exception as e:
        logger.error(f"Error handling heures.validated: {e}")
    finally:
        db.close()


def _get_chantier_users(db, chantier_id: int) -> list[int]:
    """Recupere les IDs des utilisateurs affectes a un chantier (conducteurs + chefs)."""
    from modules.chantiers.infrastructure.persistence import (
        ChantierConducteurModel,
        ChantierChefModel,
    )

    user_ids = set()

    conducteurs = (
        db.query(ChantierConducteurModel.user_id)
        .filter(ChantierConducteurModel.chantier_id == chantier_id)
        .all()
    )
    for (uid,) in conducteurs:
        user_ids.add(uid)

    chefs = (
        db.query(ChantierChefModel.user_id)
        .filter(ChantierChefModel.chantier_id == chantier_id)
        .all()
    )
    for (uid,) in chefs:
        user_ids.add(uid)

    return list(user_ids)


@event_handler('chantier.created')
def handle_chantier_created(event) -> None:
    """Notifie les conducteurs et chefs assignes lors de la creation d'un chantier."""
    data = event.data if hasattr(event, 'data') and isinstance(event.data, dict) else {}
    chantier_id = data.get('chantier_id') or getattr(event, 'chantier_id', None)
    nom = data.get('nom') or getattr(event, 'nom', 'Nouveau chantier')
    metadata = event.metadata if hasattr(event, 'metadata') and isinstance(event.metadata, dict) else {}
    created_by = metadata.get('created_by', 0)

    logger.info(f"Handling chantier.created: chantier_id={chantier_id}, nom={nom}")

    db = SessionLocal()
    try:
        repo = SQLAlchemyNotificationRepository(db)
        creator_name = get_user_name(db, created_by) if created_by else "Le systeme"

        # Notifier les conducteurs et chefs listes dans les metadata
        conducteur_ids = metadata.get('conducteur_ids', [])
        chef_ids = metadata.get('chef_chantier_ids', [])
        destinataires = set(conducteur_ids + chef_ids) - {created_by}

        for user_id in destinataires:
            notification = Notification(
                user_id=user_id,
                type=NotificationType.CHANTIER_ASSIGNMENT,
                title="Nouveau chantier",
                message=f"{creator_name} vous a assigne au chantier {nom}",
                related_chantier_id=chantier_id,
                triggered_by_user_id=created_by if created_by else None,
            )
            repo.save(notification)
            logger.info(f"Created chantier assignment notification for user {user_id}")

    except Exception as e:
        logger.error(f"Error handling chantier.created: {e}")
    finally:
        db.close()


@event_handler('chantier.statut_changed')
def handle_chantier_statut_changed(event) -> None:
    """Notifie l'equipe du chantier lors d'un changement de statut."""
    from modules.chantiers.domain.value_objects.statut_chantier import StatutChantier

    data = event.data if hasattr(event, 'data') and isinstance(event.data, dict) else {}
    chantier_id = data.get('chantier_id') or getattr(event, 'chantier_id', None)
    nouveau_statut = data.get('nouveau_statut') or getattr(event, 'nouveau_statut', '')
    metadata = event.metadata if hasattr(event, 'metadata') and isinstance(event.metadata, dict) else {}
    changed_by = metadata.get('changed_by', 0)

    if not chantier_id:
        return

    logger.info(f"Handling chantier.statut_changed: chantier_id={chantier_id}, nouveau_statut={nouveau_statut}")

    db = SessionLocal()
    try:
        repo = SQLAlchemyNotificationRepository(db)
        changer_name = get_user_name(db, changed_by) if changed_by else "Le systeme"
        destinataires = set(_get_chantier_users(db, chantier_id)) - {changed_by}

        # Utilise le value object pour le label d'affichage (pas de dict duplique)
        try:
            label = StatutChantier.from_string(nouveau_statut).display_name
        except ValueError:
            label = nouveau_statut

        for user_id in destinataires:
            notification = Notification(
                user_id=user_id,
                type=NotificationType.SYSTEM,
                title="Changement de statut chantier",
                message=f"{changer_name} a change le statut du chantier en {label}",
                related_chantier_id=chantier_id,
                triggered_by_user_id=changed_by if changed_by else None,
            )
            repo.save(notification)

    except Exception as e:
        logger.error(f"Error handling chantier.statut_changed: {e}")
    finally:
        db.close()


@event_handler(PointageSubmittedEvent)
def handle_pointage_submitted(event: PointageSubmittedEvent) -> None:
    """
    Gere l'evenement PointageSubmittedEvent (GAP-FDH-007).

    Notifie le chef de chantier ou conducteur de travaux qu'un compagnon
    a soumis ses heures pour validation.
    """
    logger.info(
        f"Handling PointageSubmittedEvent: pointage_id={event.pointage_id}, "
        f"utilisateur_id={event.utilisateur_id}, chantier_id={event.chantier_id}"
    )

    db = SessionLocal()
    try:
        repo = SQLAlchemyNotificationRepository(db)
        compagnon_name = get_user_name(db, event.utilisateur_id)

        # Recupere les chefs et conducteurs du chantier
        destinataires = _get_chantier_users(db, event.chantier_id)

        # Ne pas notifier le compagnon lui-meme si jamais il est aussi chef
        destinataires = [uid for uid in destinataires if uid != event.utilisateur_id]

        date_str = event.date_pointage.strftime("%d/%m/%Y")

        for user_id in destinataires:
            notification = Notification(
                user_id=user_id,
                type=NotificationType.SYSTEM,
                title="Heures soumises pour validation",
                message=f"{compagnon_name} a soumis ses heures du {date_str}",
                related_chantier_id=event.chantier_id,
                triggered_by_user_id=event.utilisateur_id,
            )
            repo.save(notification)
            logger.info(f"Created pointage submitted notification for user {user_id}")

    except Exception as e:
        logger.error(f"Error handling PointageSubmittedEvent: {e}")
    finally:
        db.close()


@event_handler(PointageRejectedEvent)
def handle_pointage_rejected(event: PointageRejectedEvent) -> None:
    """
    Gere l'evenement PointageRejectedEvent (GAP-FDH-007).

    Notifie le compagnon que ses heures ont ete rejetees avec le motif.
    """
    logger.info(
        f"Handling PointageRejectedEvent: pointage_id={event.pointage_id}, "
        f"utilisateur_id={event.utilisateur_id}, validateur_id={event.validateur_id}"
    )

    # Ne pas notifier si le compagnon rejette ses propres heures
    if event.utilisateur_id == event.validateur_id:
        logger.info(f"Auto-rejet heures user_id={event.utilisateur_id}, pas de notification")
        return

    db = SessionLocal()
    try:
        repo = SQLAlchemyNotificationRepository(db)
        validator_name = get_user_name(db, event.validateur_id)
        date_str = event.date_pointage.strftime("%d/%m/%Y")

        message = f"{validator_name} a rejete vos heures du {date_str}. Motif: {event.motif}"

        notification = Notification(
            user_id=event.utilisateur_id,
            type=NotificationType.SYSTEM,
            title="Heures rejetees",
            message=message,
            related_chantier_id=event.chantier_id,
            triggered_by_user_id=event.validateur_id,
        )
        repo.save(notification)
        logger.info(f"Created pointage rejected notification for user {event.utilisateur_id}")

    except Exception as e:
        logger.error(f"Error handling PointageRejectedEvent: {e}")
    finally:
        db.close()


def register_notification_handlers() -> None:
    """
    Enregistre tous les handlers de notifications.

    Cette fonction est appelee au demarrage de l'application.
    Les decorateurs @event_handler font l'enregistrement automatiquement,
    mais cette fonction force leur import.
    """
    logger.info(
        "Notification event handlers registered "
        "(comment, like, heures.validated, pointage.submitted, pointage.rejected, "
        "chantier.created, chantier.statut_changed)"
    )
