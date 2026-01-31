"""Event handlers pour l'intégration avec le module Chantiers.

Ce module écoute les événements du module chantiers et réagit en conséquence
pour maintenir la cohérence des données planning.

Gap: GAP-CHT-002 - Blocage affectations quand chantier fermé
"""

import logging
from datetime import date, timedelta

from shared.infrastructure.event_bus import event_handler
from shared.infrastructure.database import SessionLocal

logger = logging.getLogger(__name__)


@event_handler('chantier.statut_changed')
def handle_chantier_statut_changed_for_planning(event) -> None:
    """
    Bloque les affectations futures quand un chantier passe en statut 'ferme'.

    Règle métier RG-PLN-008: Un chantier fermé ne peut plus recevoir d'affectations.
    Cette fonction supprime toutes les affectations futures (date > aujourd'hui).

    Gap: GAP-CHT-002

    Args:
        event: ChantierStatutChangedEvent
    """
    # Extraction défensive (compatible DomainEvent et frozen dataclass)
    data = event.data if hasattr(event, 'data') and isinstance(event.data, dict) else {}
    chantier_id = data.get('chantier_id') or getattr(event, 'chantier_id', None)
    nouveau_statut = data.get('nouveau_statut') or getattr(event, 'nouveau_statut', '')

    # Traiter uniquement les fermetures
    if nouveau_statut != 'ferme':
        return

    if not chantier_id:
        logger.warning("ChantierStatutChangedEvent sans chantier_id, skip")
        return

    logger.info(
        f"Blocage affectations futures pour chantier #{chantier_id} (statut={nouveau_statut})"
    )

    db = SessionLocal()
    try:
        from modules.planning.infrastructure.persistence import SQLAlchemyAffectationRepository

        affectation_repo = SQLAlchemyAffectationRepository(db)
        aujourdhui = date.today()
        date_future = aujourdhui + timedelta(days=365)  # 1 an dans le futur

        # Récupérer affectations futures
        affectations = affectation_repo.find_by_chantier(
            chantier_id=chantier_id,
            date_debut=aujourdhui,
            date_fin=date_future
        )

        # Supprimer affectations futures
        count_deleted = 0
        for affectation in affectations:
            affectation_repo.delete(affectation.id)
            count_deleted += 1
            logger.debug(
                f"Affectation #{affectation.id} supprimée (user={affectation.utilisateur_id}, "
                f"date={affectation.date})"
            )

        db.commit()

        if count_deleted > 0:
            logger.info(
                f"{count_deleted} affectation(s) future(s) supprimée(s) pour chantier #{chantier_id}"
            )
        else:
            logger.debug(f"Aucune affectation future à supprimer pour chantier #{chantier_id}")

    except Exception as e:
        logger.error(f"Erreur lors du blocage des affectations: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def register_planning_event_handlers() -> None:
    """
    Enregistre les handlers de planning pour les événements Chantiers.

    Force l'import du module pour activer les décorateurs @event_handler.
    Appelé au démarrage de l'application dans main.py.
    """
    logger.info("Planning event handlers registered (chantier.statut_changed)")
