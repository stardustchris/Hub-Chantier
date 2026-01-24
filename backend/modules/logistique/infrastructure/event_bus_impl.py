"""Implementation de l'EventBus pour le module Logistique.

H8: Audit trail - Log all domain events for traceability.
"""

from typing import Any, List, Optional
import logging

from shared.infrastructure.event_bus import EventBus as CoreEventBus
from ..application.ports.event_bus import EventBus

logger = logging.getLogger(__name__)


class LogistiqueEventBus(EventBus):
    """
    Implementation de l'interface EventBus du module Logistique.

    Cette implementation:
    - Delegue au CoreEventBus de l'infrastructure partagee (si fourni)
    - Log tous les evenements pour l'audit trail
    - Gere les erreurs de publication de facon gracieuse

    Attributes:
        _bus: L'EventBus partage optionnel.

    Example:
        >>> bus = LogistiqueEventBus(CoreEventBus)
        >>> bus.publish(ReservationCreatedEvent(...))
    """

    def __init__(self, core_event_bus: Optional[type] = None):
        """
        Initialise l'EventBus logistique.

        Args:
            core_event_bus: La classe CoreEventBus (optionnelle).
                           Si None, les evenements sont logges mais non distribues.
        """
        self._bus = core_event_bus

    def publish(self, event: Any) -> None:
        """
        Publie un evenement de domaine et log pour audit.

        L'evenement sera:
        1. Logge pour l'audit trail (toujours)
        2. Distribue aux handlers abonnes via CoreEventBus (si configure)

        Args:
            event: L'evenement a publier (Domain Event).

        Example:
            >>> event_bus.publish(ReservationCreatedEvent(
            ...     reservation_id=1,
            ...     ressource_id=2,
            ...     ressource_nom="Grue T450",
            ...     chantier_id=3,
            ...     demandeur_id=4,
            ...     date_reservation=date(2026, 1, 25),
            ...     heure_debut=time(8, 0),
            ...     heure_fin=time(18, 0),
            ...     validation_requise=True,
            ... ))
        """
        event_type = type(event).__name__

        # Log pour audit trail (toujours, meme si pas de bus)
        self._log_event_for_audit(event)

        # Publier au bus partage si configure
        if self._bus is not None:
            try:
                self._bus.publish(event)
                logger.info(f"[LOGISTIQUE] Event {event_type} published to core bus")
            except Exception as e:
                logger.error(f"[LOGISTIQUE] Error publishing event {event_type}: {e}")
        else:
            logger.debug(f"[LOGISTIQUE] Event {event_type} logged only (no core bus)")

    def publish_many(self, events: List[Any]) -> None:
        """
        Publie plusieurs evenements de domaine.

        Utile pour les operations en masse.

        Args:
            events: Liste d'evenements a publier.

        Example:
            >>> event_bus.publish_many([event1, event2, event3])
        """
        logger.debug(f"[LOGISTIQUE] Publishing batch of {len(events)} events")

        for event in events:
            self.publish(event)

        logger.info(f"[LOGISTIQUE] Batch of {len(events)} events processed")

    def _log_event_for_audit(self, event: Any) -> None:
        """
        Log un evenement pour l'audit trail.

        Format: [AUDIT][LOGISTIQUE] event_type | event_id | occurred_at | details

        Args:
            event: L'evenement a logger.
        """
        event_type = type(event).__name__
        event_id = getattr(event, "event_id", "N/A")
        occurred_at = getattr(event, "occurred_at", "N/A")

        # Construire les details selon le type d'event
        details = self._extract_event_details(event)

        logger.info(
            f"[AUDIT][LOGISTIQUE] {event_type} | "
            f"event_id={event_id} | "
            f"occurred_at={occurred_at} | "
            f"{details}"
        )

    def _extract_event_details(self, event: Any) -> str:
        """
        Extrait les details significatifs d'un evenement pour le log.

        Args:
            event: L'evenement dont on extrait les details.

        Returns:
            String formatee avec les details cles.
        """
        event_type = type(event).__name__
        parts = []

        # Ressource events
        if "Ressource" in event_type:
            if hasattr(event, "ressource_id"):
                parts.append(f"ressource_id={event.ressource_id}")
            if hasattr(event, "code"):
                parts.append(f"code={event.code}")
            if hasattr(event, "created_by"):
                parts.append(f"created_by={event.created_by}")
            if hasattr(event, "updated_by"):
                parts.append(f"updated_by={event.updated_by}")
            if hasattr(event, "deleted_by"):
                parts.append(f"deleted_by={event.deleted_by}")

        # Reservation events
        elif "Reservation" in event_type:
            if hasattr(event, "reservation_id"):
                parts.append(f"reservation_id={event.reservation_id}")
            if hasattr(event, "ressource_id"):
                parts.append(f"ressource_id={event.ressource_id}")
            if hasattr(event, "demandeur_id"):
                parts.append(f"demandeur_id={event.demandeur_id}")
            if hasattr(event, "date_reservation"):
                parts.append(f"date={event.date_reservation}")
            if hasattr(event, "valideur_id"):
                parts.append(f"valideur_id={event.valideur_id}")
            if hasattr(event, "motif") and event.motif:
                # Tronquer le motif pour le log
                motif = event.motif[:50] + "..." if len(event.motif) > 50 else event.motif
                parts.append(f"motif={motif}")

        return " | ".join(parts) if parts else "no details"


class NoOpEventBus(EventBus):
    """
    Implementation nulle de l'EventBus.

    Utilise pour les tests ou quand la publication d'evenements
    n'est pas necessaire. Ne fait rien.

    Example:
        >>> bus = NoOpEventBus()
        >>> bus.publish(some_event)  # Ne fait rien
    """

    def publish(self, event: Any) -> None:
        """Ne publie rien (implementation nulle)."""
        pass

    def publish_many(self, events: List[Any]) -> None:
        """Ne publie rien (implementation nulle)."""
        pass
