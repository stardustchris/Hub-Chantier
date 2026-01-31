"""Implementation de l'EventBus pour le module Financier.

H8: Audit trail - Log all domain events for traceability.
"""

from typing import Any, List, Optional
import logging

from shared.infrastructure.event_bus import EventBus as CoreEventBus
from ..application.ports.event_bus import EventBus

logger = logging.getLogger(__name__)


class FinancierEventBus(EventBus):
    """Implementation de l'interface EventBus du module Financier.

    Cette implementation:
    - Delegue au CoreEventBus de l'infrastructure partagee (si fourni)
    - Log tous les evenements pour l'audit trail
    - Gere les erreurs de publication de facon gracieuse

    Attributes:
        _bus: L'EventBus partage optionnel.

    Example:
        >>> bus = FinancierEventBus(CoreEventBus)
        >>> bus.publish(AchatCreatedEvent(...))
    """

    def __init__(self, core_event_bus: Optional[type] = None):
        """Initialise l'EventBus financier.

        Args:
            core_event_bus: La classe CoreEventBus (optionnelle).
                           Si None, les evenements sont logges mais non distribues.
        """
        self._bus = core_event_bus

    def publish(self, event: Any) -> None:
        """Publie un evenement de domaine et log pour audit.

        L'evenement sera:
        1. Logge pour l'audit trail (toujours)
        2. Distribue aux handlers abonnes via CoreEventBus (si configure)

        Args:
            event: L'evenement a publier (Domain Event).
        """
        event_type = type(event).__name__

        # Log pour audit trail (toujours, meme si pas de bus)
        self._log_event_for_audit(event)

        # Publier au bus partage si configure
        if self._bus is not None:
            try:
                self._bus.publish(event)
                logger.info(f"[FINANCIER] Event {event_type} published to core bus")
            except Exception as e:
                logger.error(f"[FINANCIER] Error publishing event {event_type}: {e}")
        else:
            logger.debug(f"[FINANCIER] Event {event_type} logged only (no core bus)")

    def publish_many(self, events: List[Any]) -> None:
        """Publie plusieurs evenements de domaine.

        Utile pour les operations en masse.

        Args:
            events: Liste d'evenements a publier.
        """
        logger.debug(f"[FINANCIER] Publishing batch of {len(events)} events")

        for event in events:
            self.publish(event)

        logger.info(f"[FINANCIER] Batch of {len(events)} events processed")

    def _log_event_for_audit(self, event: Any) -> None:
        """Log un evenement pour l'audit trail.

        Format: [AUDIT][FINANCIER] event_type | event_id | occurred_at | details

        Args:
            event: L'evenement a logger.
        """
        event_type = type(event).__name__
        event_id = getattr(event, "event_id", "N/A")
        occurred_at = getattr(event, "occurred_at", "N/A")

        # Construire les details selon le type d'event
        details = self._extract_event_details(event)

        logger.info(
            f"[AUDIT][FINANCIER] {event_type} | "
            f"event_id={event_id} | "
            f"occurred_at={occurred_at} | "
            f"{details}"
        )

    def _extract_event_details(self, event: Any) -> str:
        """Extrait les details significatifs d'un evenement pour le log.

        Args:
            event: L'evenement dont on extrait les details.

        Returns:
            String formatee avec les details cles.
        """
        event_type = type(event).__name__
        parts = []

        # Fournisseur events
        if "Fournisseur" in event_type:
            if hasattr(event, "fournisseur_id"):
                parts.append(f"fournisseur_id={event.fournisseur_id}")
            if hasattr(event, "raison_sociale"):
                parts.append(f"raison_sociale={event.raison_sociale}")
            if hasattr(event, "created_by"):
                parts.append(f"created_by={event.created_by}")
            if hasattr(event, "updated_by"):
                parts.append(f"updated_by={event.updated_by}")
            if hasattr(event, "deleted_by"):
                parts.append(f"deleted_by={event.deleted_by}")

        # Budget events
        elif "Budget" in event_type and "Lot" not in event_type:
            if hasattr(event, "budget_id"):
                parts.append(f"budget_id={event.budget_id}")
            if hasattr(event, "chantier_id"):
                parts.append(f"chantier_id={event.chantier_id}")
            if hasattr(event, "montant_initial_ht"):
                parts.append(f"montant_initial_ht={event.montant_initial_ht}")
            if hasattr(event, "montant_revise_ht"):
                parts.append(f"montant_revise_ht={event.montant_revise_ht}")

        # Lot Budgetaire events
        elif "LotBudgetaire" in event_type:
            if hasattr(event, "lot_id"):
                parts.append(f"lot_id={event.lot_id}")
            if hasattr(event, "budget_id"):
                parts.append(f"budget_id={event.budget_id}")
            if hasattr(event, "code_lot"):
                parts.append(f"code_lot={event.code_lot}")
            if hasattr(event, "total_prevu_ht"):
                parts.append(f"total_prevu_ht={event.total_prevu_ht}")

        # Achat events
        elif "Achat" in event_type:
            if hasattr(event, "achat_id"):
                parts.append(f"achat_id={event.achat_id}")
            if hasattr(event, "chantier_id"):
                parts.append(f"chantier_id={event.chantier_id}")
            if hasattr(event, "total_ht"):
                parts.append(f"total_ht={event.total_ht}")
            if hasattr(event, "total_ttc"):
                parts.append(f"total_ttc={event.total_ttc}")
            if hasattr(event, "valideur_id"):
                parts.append(f"valideur_id={event.valideur_id}")
            if hasattr(event, "motif") and event.motif:
                motif = event.motif[:50] + "..." if len(event.motif) > 50 else event.motif
                parts.append(f"motif={motif}")
            if hasattr(event, "numero_facture"):
                parts.append(f"facture={event.numero_facture}")

        # Depassement budget events
        elif "Depassement" in event_type:
            if hasattr(event, "chantier_id"):
                parts.append(f"chantier_id={event.chantier_id}")
            if hasattr(event, "pourcentage_consomme"):
                parts.append(f"pct={event.pourcentage_consomme}")
            if hasattr(event, "seuil_alerte_pct"):
                parts.append(f"seuil={event.seuil_alerte_pct}")

        return " | ".join(parts) if parts else "no details"
