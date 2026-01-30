"""Event handlers pour le module Chantiers.

Écoute les événements domaine du module Chantiers et crée les notifications
correspondantes via le module Notifications.
"""

import logging

from shared.infrastructure.event_bus import event_handler
from shared.infrastructure.database import SessionLocal
from shared.infrastructure.entity_info_impl import SQLAlchemyEntityInfoService
from modules.notifications.domain.entities import Notification
from modules.notifications.domain.value_objects import NotificationType
from modules.notifications.infrastructure.persistence import SQLAlchemyNotificationRepository

logger = logging.getLogger(__name__)


def _get_user_name(db, user_id: int) -> str:
    """Récupère le nom complet d'un utilisateur."""
    entity_info = SQLAlchemyEntityInfoService(db)
    user_info = entity_info.get_user_info(user_id)
    return user_info.nom if user_info else "Utilisateur"


def _get_chantier_users(db, chantier_id: int) -> list[int]:
    """Récupère les IDs des utilisateurs affectés à un chantier (conducteurs + chefs)."""
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
    """Notifie les conducteurs et chefs assignés lors de la création d'un chantier."""
    data = event.data if hasattr(event, 'data') and isinstance(event.data, dict) else {}
    chantier_id = data.get('chantier_id') or getattr(event, 'chantier_id', None)
    nom = data.get('nom') or getattr(event, 'nom', 'Nouveau chantier')
    metadata = event.metadata if hasattr(event, 'metadata') and isinstance(event.metadata, dict) else {}
    created_by = metadata.get('created_by', 0)

    logger.info(f"Handling chantier.created: chantier_id={chantier_id}, nom={nom}")

    db = SessionLocal()
    try:
        repo = SQLAlchemyNotificationRepository(db)
        creator_name = _get_user_name(db, created_by) if created_by else "Le système"

        # Notifier les conducteurs et chefs listés dans les metadata
        conducteur_ids = metadata.get('conducteur_ids', [])
        chef_ids = metadata.get('chef_chantier_ids', [])
        destinataires = set(conducteur_ids + chef_ids) - {created_by}

        for user_id in destinataires:
            notification = Notification(
                user_id=user_id,
                type=NotificationType.CHANTIER_ASSIGNMENT,
                title="Nouveau chantier",
                message=f"{creator_name} vous a assigné au chantier {nom}",
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
    """Notifie l'équipe du chantier lors d'un changement de statut."""
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
        changer_name = _get_user_name(db, changed_by) if changed_by else "Le système"
        destinataires = set(_get_chantier_users(db, chantier_id)) - {changed_by}

        statut_labels = {
            "ouvert": "Ouvert",
            "en_cours": "En cours",
            "receptionne": "Réceptionné",
            "ferme": "Fermé",
        }
        label = statut_labels.get(nouveau_statut, nouveau_statut)

        for user_id in destinataires:
            notification = Notification(
                user_id=user_id,
                type=NotificationType.SYSTEM,
                title="Changement de statut chantier",
                message=f"{changer_name} a changé le statut du chantier en {label}",
                related_chantier_id=chantier_id,
                triggered_by_user_id=changed_by if changed_by else None,
            )
            repo.save(notification)

    except Exception as e:
        logger.error(f"Error handling chantier.statut_changed: {e}")
    finally:
        db.close()


def register_chantier_handlers() -> None:
    """Enregistre les handlers d'événements chantier.

    Les décorateurs @event_handler font l'enregistrement automatiquement,
    mais cette fonction force leur import au démarrage.
    """
    logger.info("Chantier event handlers registered (chantier.created, chantier.statut_changed)")
