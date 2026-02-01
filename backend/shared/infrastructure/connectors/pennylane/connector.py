"""Connecteur Pennylane pour export des données comptables."""

import logging
from typing import Dict, Any

from shared.infrastructure.event_bus.domain_event import DomainEvent
from ..base_connector import BaseConnector, ConnectorError
from .formatters import format_supplier_invoice, format_customer_invoice, format_transaction

logger = logging.getLogger(__name__)


class PennylaneConnector(BaseConnector):
    """
    Connecteur pour l'API Pennylane (logiciel de comptabilité).

    Transforme les événements Hub Chantier en appels API Pennylane v1:
    - achat.created → POST /invoices/supplier (factures fournisseurs)
    - situation_travaux.created → POST /invoices/customer (factures clients)
    - paiement.created → POST /transactions (transactions bancaires)

    Note:
        Ce connecteur ne fait pas les appels HTTP directement.
        Il se contente de transformer les événements en payloads formatés.
        La livraison HTTP est gérée par WebhookDeliveryService.

    Example:
        >>> connector = PennylaneConnector()
        >>> event = DomainEvent(
        ...     event_type="achat.created",
        ...     data={"date": "2026-01-31", "montant": 1500.00, "libelle": "Achat matériaux"}
        ... )
        >>> payload = connector.transform_event(event)
        >>> print(payload["endpoint"])
        /invoices/supplier
        >>> print(payload["data"])
        {"date": "2026-01-31", "amount": 1500.00, "label": "Achat matériaux", ...}
    """

    # Mapping event_type → endpoint API Pennylane
    ENDPOINT_MAPPING = {
        "achat.created": "/invoices/supplier",
        "situation_travaux.created": "/invoices/customer",
        "paiement.created": "/transactions",
    }

    def __init__(self):
        """Initialise le connecteur Pennylane."""
        super().__init__(
            name="pennylane",
            supported_events=list(self.ENDPOINT_MAPPING.keys())
        )
        logger.info("Connecteur Pennylane initialisé")

    def format_data(self, event: DomainEvent) -> Dict[str, Any]:
        """
        Formate les données de l'événement pour l'API Pennylane v1.

        Délègue le formatage aux fonctions spécialisées selon le type d'événement:
        - achat.created → format_supplier_invoice()
        - situation_travaux.created → format_customer_invoice()
        - paiement.created → format_transaction()

        Args:
            event: L'événement de domaine à transformer.

        Returns:
            Les données formatées selon le schéma Pennylane v1.

        Raises:
            ConnectorError: Si le formatage échoue ou si des données requises manquent.
        """
        logger.debug(f"Formatage événement {event.event_type} pour Pennylane")

        # Dispatcher vers le bon formatter
        if event.event_type == "achat.created":
            return format_supplier_invoice(event)

        elif event.event_type == "situation_travaux.created":
            return format_customer_invoice(event)

        elif event.event_type == "paiement.created":
            return format_transaction(event)

        else:
            # Ne devrait jamais arriver (validé dans transform_event)
            raise ConnectorError(
                f"Aucun formatter disponible pour {event.event_type}",
                connector_name=self.name,
                event_type=event.event_type
            )

    def get_api_endpoint(self, event_type: str) -> str:
        """
        Retourne l'endpoint API Pennylane pour le type d'événement.

        Args:
            event_type: Le type d'événement (ex: "achat.created").

        Returns:
            Le chemin de l'endpoint API Pennylane (ex: "/invoices/supplier").

        Raises:
            ConnectorError: Si l'event_type n'a pas d'endpoint associé.
        """
        endpoint = self.ENDPOINT_MAPPING.get(event_type)

        if not endpoint:
            raise ConnectorError(
                f"Pas d'endpoint défini pour {event_type}. "
                f"Endpoints disponibles: {list(self.ENDPOINT_MAPPING.keys())}",
                connector_name=self.name,
                event_type=event_type
            )

        logger.debug(f"Endpoint Pennylane pour {event_type}: {endpoint}")
        return endpoint
