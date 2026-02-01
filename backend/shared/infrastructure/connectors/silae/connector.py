"""Connecteur Silae pour export des heures de paie."""

import logging
from typing import Dict, Any

from shared.infrastructure.event_bus.domain_event import DomainEvent
from ..base_connector import BaseConnector, ConnectorError
from .formatters import format_employee_hours

logger = logging.getLogger(__name__)


class SilaeConnector(BaseConnector):
    """
    Connecteur pour l'API Silae (logiciel de paie).

    Transforme les événements Hub Chantier en appels API Silae:
    - feuille_heures.validated → POST /employees/hours (export heures validées)
    - pointage.validated → POST /employees/hours (export pointages validés)

    Les deux événements produisent le même format de sortie mais peuvent
    avoir des structures de données d'entrée différentes.

    Note:
        Ce connecteur ne fait pas les appels HTTP directement.
        Il se contente de transformer les événements en payloads formatés.
        La livraison HTTP est gérée par WebhookDeliveryService.

    Example:
        >>> connector = SilaeConnector()
        >>> event = DomainEvent(
        ...     event_type="feuille_heures.validated",
        ...     data={
        ...         "employe_code": "EMP001",
        ...         "periode": "2026-01",
        ...         "heures": [
        ...             {
        ...                 "date": "2026-01-15",
        ...                 "type": "normal",
        ...                 "quantite": 8.0,
        ...                 "chantier_code": "CHT001"
        ...             }
        ...         ]
        ...     }
        ... )
        >>> payload = connector.transform_event(event)
        >>> print(payload["endpoint"])
        /employees/hours
        >>> print(payload["data"])
        {"employee_code": "EMP001", "period": "2026-01", "hours": [...], ...}
    """

    # Mapping event_type → endpoint API Silae
    ENDPOINT_MAPPING = {
        "feuille_heures.validated": "/employees/hours",
        "pointage.validated": "/employees/hours",
    }

    def __init__(self):
        """Initialise le connecteur Silae."""
        super().__init__(
            name="silae",
            supported_events=list(self.ENDPOINT_MAPPING.keys())
        )
        logger.info("Connecteur Silae initialisé")

    def format_data(self, event: DomainEvent) -> Dict[str, Any]:
        """
        Formate les données de l'événement pour l'API Silae.

        Les événements feuille_heures.validated et pointage.validated
        utilisent le même formatter (format_employee_hours) car ils
        produisent le même format de sortie.

        Args:
            event: L'événement de domaine à transformer.

        Returns:
            Les données formatées selon le schéma Silae.

        Raises:
            ConnectorError: Si le formatage échoue ou si des données requises manquent.
        """
        logger.debug(f"Formatage événement {event.event_type} pour Silae")

        # Les deux événements utilisent le même formatter
        if event.event_type in ["feuille_heures.validated", "pointage.validated"]:
            return format_employee_hours(event)

        else:
            # Ne devrait jamais arriver (validé dans transform_event)
            raise ConnectorError(
                f"Aucun formatter disponible pour {event.event_type}",
                connector_name=self.name,
                event_type=event.event_type
            )

    def get_api_endpoint(self, event_type: str) -> str:
        """
        Retourne l'endpoint API Silae pour le type d'événement.

        Args:
            event_type: Le type d'événement (ex: "feuille_heures.validated").

        Returns:
            Le chemin de l'endpoint API Silae (ex: "/employees/hours").

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

        logger.debug(f"Endpoint Silae pour {event_type}: {endpoint}")
        return endpoint
