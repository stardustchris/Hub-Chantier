"""Tests unitaires pour PennylaneConnector."""

import pytest
from datetime import datetime

from shared.infrastructure.event_bus.domain_event import DomainEvent
from shared.infrastructure.connectors.pennylane.connector import PennylaneConnector
from shared.infrastructure.connectors.base_connector import ConnectorError


class TestPennylaneConnector:
    """Tests pour le connecteur Pennylane."""

    def test_initialization(self):
        """Test l'initialisation du connecteur."""
        connector = PennylaneConnector()

        assert connector.name == "pennylane"
        assert "achat.created" in connector.supported_events
        assert "situation_travaux.created" in connector.supported_events
        assert "paiement.created" in connector.supported_events

    def test_format_supplier_invoice(self):
        """Test le formatage d'un achat en facture fournisseur."""
        connector = PennylaneConnector()
        event = DomainEvent(
            event_type="achat.created",
            aggregate_id="456",
            data={
                "date": "2026-01-31",
                "montant": 1500.00,
                "libelle": "Achat matériaux",
                "numero_facture": "F-2026-001",
                "category_id": "CAT-123"
            }
        )

        payload = connector.transform_event(event)

        assert payload["endpoint"] == "/invoices/supplier"
        assert payload["data"]["date"] == "2026-01-31"
        assert payload["data"]["amount"] == 1500.00
        assert payload["data"]["label"] == "Achat matériaux"
        assert payload["data"]["invoice_number"] == "F-2026-001"
        assert payload["data"]["category_id"] == "CAT-123"
        assert payload["data"]["external_id"] == "456"

    def test_format_supplier_invoice_missing_fields(self):
        """Test le formatage d'un achat avec champs manquants."""
        connector = PennylaneConnector()
        event = DomainEvent(
            event_type="achat.created",
            data={
                "date": "2026-01-31",
                # montant manquant
                "libelle": "Achat matériaux"
            }
        )

        with pytest.raises(ConnectorError) as exc_info:
            connector.transform_event(event)

        assert "manquants" in str(exc_info.value)
        assert "montant" in str(exc_info.value)

    def test_format_customer_invoice(self):
        """Test le formatage d'une situation de travaux."""
        connector = PennylaneConnector()
        event = DomainEvent(
            event_type="situation_travaux.created",
            aggregate_id="789",
            data={
                "date": "2026-01-31",
                "montant": 25000.00,
                "libelle": "Situation mensuelle",
                "numero": 1,
                "chantier_nom": "Chantier ABC"
            }
        )

        payload = connector.transform_event(event)

        assert payload["endpoint"] == "/invoices/customer"
        assert payload["data"]["date"] == "2026-01-31"
        assert payload["data"]["amount"] == 25000.00
        assert payload["data"]["label"] == "Situation mensuelle - Chantier ABC"
        assert payload["data"]["invoice_number"] == "SIT-0001"
        assert payload["data"]["external_id"] == "789"

    def test_format_customer_invoice_optional_fields(self):
        """Test le formatage d'une situation sans champs optionnels."""
        connector = PennylaneConnector()
        event = DomainEvent(
            event_type="situation_travaux.created",
            data={
                "date": "2026-01-31",
                "montant": 25000.00,
                "libelle": "Situation mensuelle"
                # Pas de numero, pas de chantier_nom
            }
        )

        payload = connector.transform_event(event)

        assert payload["endpoint"] == "/invoices/customer"
        assert payload["data"]["date"] == "2026-01-31"
        assert payload["data"]["amount"] == 25000.00
        assert payload["data"]["label"] == "Situation mensuelle"
        assert "invoice_number" not in payload["data"]

    def test_format_transaction(self):
        """Test le formatage d'un paiement."""
        connector = PennylaneConnector()
        event = DomainEvent(
            event_type="paiement.created",
            aggregate_id="999",
            data={
                "date": "2026-01-31",
                "montant": 5000.00,
                "libelle": "Paiement facture client",
                "type": "virement"
            }
        )

        payload = connector.transform_event(event)

        assert payload["endpoint"] == "/transactions"
        assert payload["data"]["date"] == "2026-01-31"
        assert payload["data"]["amount"] == 5000.00
        assert payload["data"]["label"] == "Paiement facture client"
        assert payload["data"]["payment_method"] == "bank_transfer"
        assert payload["data"]["external_id"] == "999"

    def test_format_transaction_payment_types(self):
        """Test les différents types de paiement."""
        connector = PennylaneConnector()

        payment_types = {
            "virement": "bank_transfer",
            "cheque": "check",
            "especes": "cash",
            "cb": "card",
            "autre": "other",
        }

        for hub_type, pennylane_type in payment_types.items():
            event = DomainEvent(
                event_type="paiement.created",
                data={
                    "date": "2026-01-31",
                    "montant": 100.00,
                    "libelle": "Test",
                    "type": hub_type
                }
            )

            payload = connector.transform_event(event)
            assert payload["data"]["payment_method"] == pennylane_type

    def test_get_api_endpoint(self):
        """Test la récupération des endpoints."""
        connector = PennylaneConnector()

        assert connector.get_api_endpoint("achat.created") == "/invoices/supplier"
        assert connector.get_api_endpoint("situation_travaux.created") == "/invoices/customer"
        assert connector.get_api_endpoint("paiement.created") == "/transactions"

    def test_get_api_endpoint_unknown(self):
        """Test la récupération d'un endpoint inconnu."""
        connector = PennylaneConnector()

        with pytest.raises(ConnectorError) as exc_info:
            connector.get_api_endpoint("unknown.event")

        assert "Pas d'endpoint" in str(exc_info.value)

    def test_unsupported_event(self):
        """Test la transformation d'un événement non supporté."""
        connector = PennylaneConnector()
        event = DomainEvent(
            event_type="user.created",
            data={"foo": "bar"}
        )

        with pytest.raises(ConnectorError) as exc_info:
            connector.transform_event(event)

        assert "non supporté" in str(exc_info.value)

    def test_metadata_included(self):
        """Test que les métadonnées sont bien incluses."""
        connector = PennylaneConnector()
        event = DomainEvent(
            event_type="achat.created",
            data={
                "date": "2026-01-31",
                "montant": 100.00,
                "libelle": "Test"
            },
            occurred_at=datetime(2026, 1, 31, 12, 0, 0)
        )

        payload = connector.transform_event(event)

        assert payload["metadata"]["source"] == "hub-chantier"
        assert payload["metadata"]["connector"] == "pennylane"
        assert payload["metadata"]["event_type"] == "achat.created"
        assert "event_id" in payload["metadata"]
        assert "occurred_at" in payload["metadata"]
