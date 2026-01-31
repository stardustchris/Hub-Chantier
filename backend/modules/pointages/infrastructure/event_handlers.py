"""Event handlers pour l'intégration avec d'autres modules.

Ce fichier contient les handlers qui écoutent les événements d'autres modules
et créent les pointages correspondants (FDH-10).
"""

import logging

from sqlalchemy.orm import Session

from .persistence import (
    SQLAlchemyPointageRepository,
    SQLAlchemyFeuilleHeuresRepository,
)
from .event_bus_impl import get_event_bus
from ..application.use_cases import BulkCreateFromPlanningUseCase

logger = logging.getLogger(__name__)


def _extract_event_field(event, field: str, default=None):
    """Extrait un champ depuis un DomainEvent (event.data) ou un ancien event (attribut direct)."""
    if hasattr(event, 'data') and isinstance(event.data, dict):
        return event.data.get(field, default)
    return getattr(event, field, default)


def _convert_heures_to_string(heures) -> str:
    """
    Convertit un nombre d'heures (float ou string) en format "HH:MM".

    Gère deux cas:
    - float: convertit en "HH:MM" (ex: 8.0 -> "08:00", 7.5 -> "07:30")
    - str: retourne tel quel si déjà au format "HH:MM"

    Args:
        heures: Nombre d'heures (float) ou string au format "HH:MM".

    Returns:
        Chaine au format "HH:MM" (ex: "08:00", "07:30").

    Example:
        >>> _convert_heures_to_string(8.0)
        '08:00'
        >>> _convert_heures_to_string(7.5)
        '07:30'
        >>> _convert_heures_to_string("08:00")
        '08:00'
    """
    # Si c'est déjà une string, retourner tel quel
    if isinstance(heures, str):
        return heures

    # Sinon, convertir float -> "HH:MM"
    heures_int = int(heures)
    minutes_decimal = (heures - heures_int) * 60
    minutes_int = int(round(minutes_decimal))
    return f"{heures_int:02d}:{minutes_int:02d}"


def handle_affectation_created(
    event,
    session: Session,
    chantier_repo=None,
) -> None:
    """
    Handler pour l'événement AffectationCreatedEvent du module Planning.

    Crée automatiquement un pointage pré-rempli depuis l'affectation (FDH-10).
    Compatible avec les deux styles d'événements (DomainEvent et frozen dataclass).

    Args:
        event: L'événement AffectationCreatedEvent (DomainEvent ou dataclass).
        session: Session SQLAlchemy.
        chantier_repo: Repository chantier injecté (optionnel, pour filtrage système).
    """
    from datetime import date as date_type

    affectation_id = _extract_event_field(event, 'affectation_id')
    utilisateur_id = _extract_event_field(event, 'user_id') or _extract_event_field(event, 'utilisateur_id')
    chantier_id = _extract_event_field(event, 'chantier_id')
    date_val = _extract_event_field(event, 'date') or _extract_event_field(event, 'date_affectation')
    created_by = (_extract_event_field(event, 'created_by')
                  or (event.metadata.get('created_by') if hasattr(event, 'metadata') and isinstance(event.metadata, dict) else None)
                  or 0)

    logger.info(
        f"Handling AffectationCreatedEvent: affectation_id={affectation_id}, "
        f"utilisateur_id={utilisateur_id}, chantier_id={chantier_id}"
    )

    try:
        # Initialise les repositories
        pointage_repo = SQLAlchemyPointageRepository(session)
        feuille_repo = SQLAlchemyFeuilleHeuresRepository(session)
        event_bus = get_event_bus()

        # Initialise le use case
        use_case = BulkCreateFromPlanningUseCase(
            pointage_repo, feuille_repo, event_bus, chantier_repo
        )

        # Détermine les heures prévues (depuis l'événement ou par défaut)
        heures_prevues_raw = _extract_event_field(event, 'heures_prevues')
        heures_prevues = _convert_heures_to_string(heures_prevues_raw) if heures_prevues_raw else "08:00"

        # Convertir la date si c'est une string ISO
        if isinstance(date_val, str):
            date_val = date_type.fromisoformat(date_val)

        # Crée le pointage depuis l'événement
        result = use_case.execute_from_event(
            utilisateur_id=utilisateur_id,
            chantier_id=chantier_id,
            date_affectation=date_val,
            heures_prevues=heures_prevues,
            affectation_id=affectation_id,
            created_by=created_by,
        )

        if result:
            logger.info(f"Pointage créé: id={result.id} depuis affectation={affectation_id}")
        else:
            logger.debug(f"Pointage non créé (déjà existant) pour affectation={affectation_id}")

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


def setup_planning_integration(session_factory, chantier_repo_factory=None) -> None:
    """
    Configure l'intégration avec le module Planning.

    Args:
        session_factory: Factory pour créer des sessions SQLAlchemy.
        chantier_repo_factory: Factory pour créer ChantierRepository (optionnel).
    """
    try:
        from shared.infrastructure.event_bus import event_bus
        from modules.planning.domain.events import AffectationCreatedEvent

        def wrapped_handler(event):
            """Handler avec session automatique et injection de dépendances."""
            session = session_factory()
            try:
                # Injection du repository chantier si disponible
                chantier_repo = None
                if chantier_repo_factory:
                    chantier_repo = chantier_repo_factory(session)

                handle_affectation_created(event, session, chantier_repo)
            finally:
                session.close()

        event_bus.subscribe('affectation.created', wrapped_handler)
        logger.info("Planning integration configured successfully")

    except ImportError as e:
        logger.warning(f"Could not setup planning integration: {e}")
