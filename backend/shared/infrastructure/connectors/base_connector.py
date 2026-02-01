"""Interface abstraite pour les connecteurs d'intégration."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

from shared.infrastructure.event_bus.domain_event import DomainEvent

logger = logging.getLogger(__name__)


class ConnectorError(Exception):
    """
    Exception levée lors d'erreurs de connecteur.

    Utilisée pour toutes les erreurs de transformation, formatage,
    ou validation dans les connecteurs.
    """

    def __init__(self, message: str, connector_name: str, event_type: str):
        """
        Initialise l'exception.

        Args:
            message: Message d'erreur descriptif.
            connector_name: Nom du connecteur concerné.
            event_type: Type d'événement en cours de traitement.
        """
        self.connector_name = connector_name
        self.event_type = event_type
        super().__init__(f"[{connector_name}] {event_type}: {message}")


class BaseConnector(ABC):
    """
    Interface abstraite pour tous les connecteurs d'intégration.

    Un connecteur transforme les DomainEvents du système Hub Chantier
    en payloads formatés pour des APIs tierces (Pennylane, Silae, etc.).

    Chaque connecteur implémente:
    - Les événements qu'il écoute
    - La logique de transformation des données
    - Le mapping vers les endpoints de l'API cible

    Attributes:
        name: Nom du connecteur (ex: "pennylane", "silae").
        supported_events: Liste des event_types supportés.

    Example:
        >>> connector = PennylaneConnector()
        >>> event = DomainEvent(
        ...     event_type="achat.created",
        ...     data={"montant": 1500.00, "libelle": "Achat matériaux"}
        ... )
        >>> payload = connector.transform_event(event)
        >>> endpoint = connector.get_api_endpoint(event.event_type)
    """

    def __init__(self, name: str, supported_events: list[str]):
        """
        Initialise le connecteur.

        Args:
            name: Nom du connecteur.
            supported_events: Liste des event_types supportés par ce connecteur.
        """
        self.name = name
        self.supported_events = supported_events
        logger.info(f"Connecteur {name} initialisé avec {len(supported_events)} événements supportés")

    @abstractmethod
    def format_data(self, event: DomainEvent) -> Dict[str, Any]:
        """
        Formate les données de l'événement pour l'API cible.

        Cette méthode contient la logique de transformation spécifique
        à chaque API (Pennylane, Silae, etc.).

        Args:
            event: L'événement de domaine à transformer.

        Returns:
            Les données formatées selon le schéma de l'API cible.

        Raises:
            ConnectorError: Si le formatage échoue (données manquantes, type invalide, etc.).
        """
        pass

    @abstractmethod
    def get_api_endpoint(self, event_type: str) -> str:
        """
        Retourne l'endpoint API correspondant au type d'événement.

        Args:
            event_type: Le type d'événement (ex: "achat.created").

        Returns:
            Le chemin de l'endpoint API (ex: "/invoices/supplier").

        Raises:
            ConnectorError: Si l'event_type n'est pas supporté.
        """
        pass

    def transform_event(self, event: DomainEvent) -> Dict[str, Any]:
        """
        Transforme un événement en payload API complet.

        Cette méthode orchestre la transformation complète:
        1. Valide que l'événement est supporté
        2. Formate les données via format_data()
        3. Ajoute les métadonnées nécessaires
        4. Détermine l'endpoint cible

        Args:
            event: L'événement de domaine à transformer.

        Returns:
            Le payload complet prêt pour l'envoi à l'API:
            {
                "endpoint": "/api/endpoint",
                "data": {...},
                "metadata": {...}
            }

        Raises:
            ConnectorError: Si l'événement n'est pas supporté ou si la transformation échoue.
        """
        logger.debug(f"[{self.name}] Transformation de l'événement {event.event_type}")

        # Vérifier que l'événement est supporté
        if event.event_type not in self.supported_events:
            raise ConnectorError(
                f"Événement {event.event_type} non supporté. "
                f"Événements supportés: {', '.join(self.supported_events)}",
                connector_name=self.name,
                event_type=event.event_type
            )

        try:
            # Formater les données
            formatted_data = self.format_data(event)

            # Déterminer l'endpoint
            endpoint = self.get_api_endpoint(event.event_type)

            # Construire le payload complet
            payload = {
                "endpoint": endpoint,
                "data": formatted_data,
                "metadata": {
                    "source": "hub-chantier",
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "occurred_at": event.occurred_at.isoformat(),
                    "connector": self.name,
                }
            }

            logger.info(
                f"[{self.name}] Événement {event.event_type} transformé avec succès "
                f"pour endpoint {endpoint}"
            )

            return payload

        except ConnectorError:
            raise
        except Exception as e:
            logger.error(
                f"[{self.name}] Erreur inattendue lors de la transformation: {e}",
                exc_info=True
            )
            raise ConnectorError(
                f"Erreur de transformation: {str(e)}",
                connector_name=self.name,
                event_type=event.event_type
            ) from e

    def supports_event(self, event_type: str) -> bool:
        """
        Vérifie si le connecteur supporte un type d'événement.

        Args:
            event_type: Le type d'événement à vérifier.

        Returns:
            True si l'événement est supporté, False sinon.
        """
        return event_type in self.supported_events

    def __repr__(self) -> str:
        """Représentation string pour debugging."""
        return f"<{self.__class__.__name__}(name={self.name}, events={len(self.supported_events)})>"
