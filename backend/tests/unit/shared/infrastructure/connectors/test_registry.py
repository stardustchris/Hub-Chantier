"""Tests unitaires pour le registre de connecteurs."""

import pytest

from shared.infrastructure.connectors.registry import (
    get_connector,
    list_connectors,
    find_connector_for_event,
    ConnectorNotFoundError,
    CONNECTOR_REGISTRY,
)
from shared.infrastructure.connectors.pennylane.connector import PennylaneConnector
from shared.infrastructure.connectors.silae.connector import SilaeConnector


class TestConnectorRegistry:
    """Tests pour le registre de connecteurs."""

    def test_registry_contains_all_connectors(self):
        """Test que le registre contient tous les connecteurs."""
        assert "pennylane" in CONNECTOR_REGISTRY
        assert "silae" in CONNECTOR_REGISTRY
        assert CONNECTOR_REGISTRY["pennylane"] == PennylaneConnector
        assert CONNECTOR_REGISTRY["silae"] == SilaeConnector

    def test_get_connector_pennylane(self):
        """Test la récupération du connecteur Pennylane."""
        connector = get_connector("pennylane")

        assert isinstance(connector, PennylaneConnector)
        assert connector.name == "pennylane"

    def test_get_connector_silae(self):
        """Test la récupération du connecteur Silae."""
        connector = get_connector("silae")

        assert isinstance(connector, SilaeConnector)
        assert connector.name == "silae"

    def test_get_connector_case_insensitive(self):
        """Test que get_connector est insensible à la casse."""
        connector1 = get_connector("PENNYLANE")
        connector2 = get_connector("Pennylane")
        connector3 = get_connector("pennylane")

        assert all(isinstance(c, PennylaneConnector) for c in [connector1, connector2, connector3])

    def test_get_connector_not_found(self):
        """Test la récupération d'un connecteur inexistant."""
        with pytest.raises(ConnectorNotFoundError) as exc_info:
            get_connector("unknown")

        assert "unknown" in str(exc_info.value)
        assert "pennylane" in str(exc_info.value)  # Liste des disponibles
        assert "silae" in str(exc_info.value)

    def test_get_connector_creates_new_instance(self):
        """Test que get_connector crée une nouvelle instance à chaque appel."""
        connector1 = get_connector("pennylane")
        connector2 = get_connector("pennylane")

        # Deux instances différentes
        assert connector1 is not connector2
        # Mais du même type
        assert type(connector1) == type(connector2)

    def test_list_connectors(self):
        """Test la liste des connecteurs disponibles."""
        connectors = list_connectors()

        assert isinstance(connectors, dict)
        assert "pennylane" in connectors
        assert "silae" in connectors

        # Vérifier les événements Pennylane
        assert "achat.created" in connectors["pennylane"]
        assert "situation_travaux.created" in connectors["pennylane"]
        assert "paiement.created" in connectors["pennylane"]

        # Vérifier les événements Silae
        assert "feuille_heures.validated" in connectors["silae"]
        assert "pointage.validated" in connectors["silae"]

    def test_find_connector_for_event_pennylane(self):
        """Test la recherche de connecteur pour un événement Pennylane."""
        assert find_connector_for_event("achat.created") == "pennylane"
        assert find_connector_for_event("situation_travaux.created") == "pennylane"
        assert find_connector_for_event("paiement.created") == "pennylane"

    def test_find_connector_for_event_silae(self):
        """Test la recherche de connecteur pour un événement Silae."""
        assert find_connector_for_event("feuille_heures.validated") == "silae"
        assert find_connector_for_event("pointage.validated") == "silae"

    def test_find_connector_for_event_not_found(self):
        """Test la recherche de connecteur pour un événement non supporté."""
        assert find_connector_for_event("user.created") is None
        assert find_connector_for_event("unknown.event") is None

    def test_connector_not_found_error_message(self):
        """Test le message d'erreur de ConnectorNotFoundError."""
        error = ConnectorNotFoundError("test-connector")

        assert "test-connector" in str(error)
        assert "non trouvé" in str(error)
        assert "disponibles" in str(error)
