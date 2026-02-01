"""
Connecteurs pour intégrations tierces (Pennylane, Silae).

Ce package contient les connecteurs permettant d'exporter les données
vers des systèmes externes via webhooks:

- Pennylane: logiciel de comptabilité
- Silae: logiciel de paie

Architecture:
    BaseConnector (ABC) - Interface abstraite commune
    ├── PennylaneConnector - Export comptabilité
    └── SilaeConnector - Export paie

Utilisation:
    >>> from shared.infrastructure.connectors import get_connector
    >>> connector = get_connector("pennylane")
    >>> payload = connector.transform_event(event)
"""

from .base_connector import BaseConnector
from .registry import get_connector, CONNECTOR_REGISTRY

__all__ = [
    "BaseConnector",
    "get_connector",
    "CONNECTOR_REGISTRY",
]
