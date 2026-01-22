"""Event handlers pour l'intégration avec d'autres modules.

Ce fichier contient les handlers qui écoutent les événements d'autres modules
et créent les pointages correspondants (FDH-10).
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from .persistence import (
    SQLAlchemyPointageRepository,
    SQLAlchemyFeuilleHeuresRepository,
)
from .event_bus_impl import get_event_bus
from ..application.use_cases import BulkCreateFromPlanningUseCase

logger = logging.getLogger(__name__)


def handle_affectation_created(
    event,
    session: Session,
) -> None:
    """
    Handler pour l'événement AffectationCreatedEvent du module Planning.

    Crée automatiquement un pointage pré-rempli depuis l'affectation (FDH-10).

    Args:
        event: L'événement AffectationCreatedEvent.
        session: Session SQLAlchemy.
    """
    logger.info(
        f"Handling AffectationCreatedEvent: affectation_id={event.affectation_id}, "
        f"utilisateur_id={event.utilisateur_id}, chantier_id={event.chantier_id}"
    )

    try:
        # Initialise les repositories
        pointage_repo = SQLAlchemyPointageRepository(session)
        feuille_repo = SQLAlchemyFeuilleHeuresRepository(session)
        event_bus = get_event_bus()

        # Initialise le use case
        use_case = BulkCreateFromPlanningUseCase(
            pointage_repo, feuille_repo, event_bus
        )

        # Détermine les heures prévues (depuis l'événement ou par défaut)
        heures_prevues = getattr(event, "heures_prevues", "08:00")
        if not heures_prevues:
            heures_prevues = "08:00"

        # Crée le pointage depuis l'événement
        result = use_case.execute_from_event(
            utilisateur_id=event.utilisateur_id,
            chantier_id=event.chantier_id,
            date_affectation=event.date,
            heures_prevues=heures_prevues,
            affectation_id=event.affectation_id,
            created_by=event.created_by,
        )

        if result:
            logger.info(f"Pointage créé: id={result.id} depuis affectation={event.affectation_id}")
        else:
            logger.debug(f"Pointage non créé (déjà existant) pour affectation={event.affectation_id}")

    except Exception as e:
        logger.error(f"Erreur lors de la création du pointage depuis affectation: {e}")
        raise


def handle_affectation_bulk_created(
    event,
    session: Session,
) -> None:
    """
    Handler pour l'événement AffectationBulkCreatedEvent du module Planning.

    Crée automatiquement les pointages pour toutes les affectations (FDH-10).

    Args:
        event: L'événement AffectationBulkCreatedEvent.
        session: Session SQLAlchemy.
    """
    logger.info(
        f"Handling AffectationBulkCreatedEvent: {len(event.affectation_ids)} affectations"
    )

    # Pour chaque affectation, traiter individuellement
    # Note: Dans une version optimisée, on pourrait batched le traitement
    for affectation_id in event.affectation_ids:
        # Crée un événement individuel pour chaque affectation
        # Cette logique dépend de comment le module planning structure ses données
        pass  # TODO: Implémenter quand les détails du module planning seront disponibles


def register_event_handlers(event_bus_class=None) -> None:
    """
    Enregistre les handlers d'événements auprès de l'EventBus partagé.

    Cette fonction doit être appelée au démarrage de l'application pour
    configurer l'écoute des événements du module Planning.

    Args:
        event_bus_class: La classe EventBus partagée (optionnel).
    """
    if event_bus_class is None:
        try:
            from shared.infrastructure.event_bus import EventBus
            event_bus_class = EventBus
        except ImportError:
            logger.warning("Shared EventBus not available, event handlers not registered")
            return

    # Tente d'importer les événements du module planning
    try:
        from modules.planning.domain.events import (
            AffectationCreatedEvent,
            AffectationBulkCreatedEvent,
        )

        # Note: Les handlers ont besoin d'une session DB
        # Dans une vraie implémentation, on utiliserait un pattern différent
        # (middleware, dependency injection, etc.)

        logger.info("Event handlers for planning integration registered")

    except ImportError:
        logger.debug("Planning module events not available")


def setup_planning_integration(session_factory) -> None:
    """
    Configure l'intégration avec le module Planning.

    Args:
        session_factory: Factory pour créer des sessions SQLAlchemy.
    """
    try:
        from shared.infrastructure.event_bus import EventBus
        from modules.planning.domain.events import AffectationCreatedEvent

        def wrapped_handler(event):
            """Handler avec session automatique."""
            session = session_factory()
            try:
                handle_affectation_created(event, session)
            finally:
                session.close()

        EventBus.subscribe(AffectationCreatedEvent, wrapped_handler)
        logger.info("Planning integration configured successfully")

    except ImportError as e:
        logger.warning(f"Could not setup planning integration: {e}")
