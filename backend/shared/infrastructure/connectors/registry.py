"""Registre des connecteurs disponibles."""

import logging
from typing import Dict, Type, Optional

from .base_connector import BaseConnector
from .pennylane.connector import PennylaneConnector
from .silae.connector import SilaeConnector

logger = logging.getLogger(__name__)


# Registre global des connecteurs disponibles
CONNECTOR_REGISTRY: Dict[str, Type[BaseConnector]] = {
    "pennylane": PennylaneConnector,
    "silae": SilaeConnector,
}


class ConnectorNotFoundError(Exception):
    """Exception levée quand un connecteur n'existe pas."""

    def __init__(self, connector_name: str):
        """
        Initialise l'exception.

        Args:
            connector_name: Nom du connecteur recherché.
        """
        available = ", ".join(CONNECTOR_REGISTRY.keys())
        super().__init__(
            f"Connecteur '{connector_name}' non trouvé. "
            f"Connecteurs disponibles: {available}"
        )


def get_connector(connector_name: str) -> BaseConnector:
    """
    Récupère une instance de connecteur par nom.

    Cette fonction est le point d'entrée principal pour obtenir
    un connecteur. Elle instancie le connecteur à chaque appel.

    Args:
        connector_name: Nom du connecteur (ex: "pennylane", "silae").

    Returns:
        Instance du connecteur demandé.

    Raises:
        ConnectorNotFoundError: Si le connecteur n'existe pas.

    Example:
        >>> connector = get_connector("pennylane")
        >>> connector.name
        'pennylane'
        >>> connector.supported_events
        ['achat.created', 'situation_travaux.created', 'paiement.created']
    """
    connector_class = CONNECTOR_REGISTRY.get(connector_name.lower())

    if not connector_class:
        logger.error(f"Tentative d'accès au connecteur inexistant: {connector_name}")
        raise ConnectorNotFoundError(connector_name)

    logger.debug(f"Instanciation du connecteur: {connector_name}")
    return connector_class()


def list_connectors() -> Dict[str, list[str]]:
    """
    Liste tous les connecteurs disponibles avec leurs événements supportés.

    Returns:
        Dictionnaire {connector_name: [supported_events]}.

    Example:
        >>> list_connectors()
        {
            "pennylane": ["achat.created", "situation_travaux.created", "paiement.created"],
            "silae": ["feuille_heures.validated", "pointage.validated"]
        }
    """
    result = {}
    for name, connector_class in CONNECTOR_REGISTRY.items():
        instance = connector_class()
        result[name] = instance.supported_events

    return result


def find_connector_for_event(event_type: str) -> Optional[str]:
    """
    Trouve quel connecteur supporte un type d'événement donné.

    Args:
        event_type: Le type d'événement (ex: "achat.created").

    Returns:
        Le nom du premier connecteur qui supporte cet événement,
        ou None si aucun connecteur ne le supporte.

    Example:
        >>> find_connector_for_event("achat.created")
        'pennylane'
        >>> find_connector_for_event("user.login")
        None
    """
    for name, connector_class in CONNECTOR_REGISTRY.items():
        instance = connector_class()
        if instance.supports_event(event_type):
            return name

    return None
