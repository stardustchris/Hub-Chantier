"""Tests unitaires pour SilaeConnector."""

import pytest
from datetime import datetime

from shared.infrastructure.event_bus.domain_event import DomainEvent
from shared.infrastructure.connectors.silae.connector import SilaeConnector
from shared.infrastructure.connectors.base_connector import ConnectorError


class TestSilaeConnector:
    """Tests pour le connecteur Silae."""

    def test_initialization(self):
        """Test l'initialisation du connecteur."""
        connector = SilaeConnector()

        assert connector.name == "silae"
        assert "feuille_heures.validated" in connector.supported_events
        assert "pointage.validated" in connector.supported_events

    def test_format_employee_hours_single_line(self):
        """Test le formatage d'heures avec une seule ligne."""
        connector = SilaeConnector()
        event = DomainEvent(
            event_type="feuille_heures.validated",
            aggregate_id="123",
            data={
                "employe_code": "EMP001",
                "periode": "2026-01",
                "heures": [
                    {
                        "date": "2026-01-15",
                        "type": "normal",
                        "quantite": 8.0,
                        "chantier_code": "CHT001"
                    }
                ]
            }
        )

        payload = connector.transform_event(event)

        assert payload["endpoint"] == "/employees/hours"
        assert payload["data"]["employee_code"] == "EMP001"
        assert payload["data"]["period"] == "2026-01"
        assert len(payload["data"]["hours"]) == 1
        assert payload["data"]["hours"][0]["date"] == "2026-01-15"
        assert payload["data"]["hours"][0]["type"] == "normal"
        assert payload["data"]["hours"][0]["quantity"] == 8.0
        assert payload["data"]["hours"][0]["cost_center"] == "CHT001"
        assert payload["data"]["external_id"] == "123"

    def test_format_employee_hours_multiple_lines(self):
        """Test le formatage d'heures avec plusieurs lignes."""
        connector = SilaeConnector()
        event = DomainEvent(
            event_type="feuille_heures.validated",
            data={
                "employe_code": "EMP002",
                "periode": "2026-01",
                "heures": [
                    {
                        "date": "2026-01-15",
                        "type": "normal",
                        "quantite": 8.0,
                        "chantier_code": "CHT001"
                    },
                    {
                        "date": "2026-01-16",
                        "type": "supplementaire",
                        "quantite": 2.0,
                        "chantier_code": "CHT002"
                    },
                    {
                        "date": "2026-01-17",
                        "type": "nuit",
                        "quantite": 5.0
                        # Pas de chantier_code (optionnel)
                    }
                ]
            }
        )

        payload = connector.transform_event(event)

        assert len(payload["data"]["hours"]) == 3
        # Ligne 1
        assert payload["data"]["hours"][0]["type"] == "normal"
        assert payload["data"]["hours"][0]["quantity"] == 8.0
        # Ligne 2
        assert payload["data"]["hours"][1]["type"] == "overtime"
        assert payload["data"]["hours"][1]["quantity"] == 2.0
        # Ligne 3
        assert payload["data"]["hours"][2]["type"] == "night"
        assert payload["data"]["hours"][2]["quantity"] == 5.0
        assert "cost_center" not in payload["data"]["hours"][2]

    def test_format_employee_hours_type_mapping(self):
        """Test le mapping des types d'heures."""
        connector = SilaeConnector()

        type_mapping = {
            "normal": "normal",
            "supplementaire": "overtime",
            "nuit": "night",
            "dimanche": "sunday",
            "ferie": "holiday",
        }

        for hub_type, silae_type in type_mapping.items():
            event = DomainEvent(
                event_type="feuille_heures.validated",
                data={
                    "employe_code": "EMP001",
                    "periode": "2026-01",
                    "heures": [
                        {
                            "date": "2026-01-15",
                            "type": hub_type,
                            "quantite": 8.0
                        }
                    ]
                }
            )

            payload = connector.transform_event(event)
            assert payload["data"]["hours"][0]["type"] == silae_type

    def test_format_employee_hours_missing_required_fields(self):
        """Test le formatage avec champs requis manquants."""
        connector = SilaeConnector()

        # Employe_code manquant
        event = DomainEvent(
            event_type="feuille_heures.validated",
            data={
                "periode": "2026-01",
                "heures": []
            }
        )

        with pytest.raises(ConnectorError) as exc_info:
            connector.transform_event(event)

        assert "manquants" in str(exc_info.value)

    def test_format_employee_hours_invalid_period(self):
        """Test le formatage avec période invalide."""
        connector = SilaeConnector()
        event = DomainEvent(
            event_type="feuille_heures.validated",
            data={
                "employe_code": "EMP001",
                "periode": "2026-13",  # Mois invalide
                "heures": [
                    {
                        "date": "2026-01-15",
                        "type": "normal",
                        "quantite": 8.0
                    }
                ]
            }
        )

        with pytest.raises(ConnectorError) as exc_info:
            connector.transform_event(event)

        assert "période invalide" in str(exc_info.value)

    def test_format_employee_hours_empty_hours_list(self):
        """Test le formatage avec liste d'heures vide."""
        connector = SilaeConnector()
        event = DomainEvent(
            event_type="feuille_heures.validated",
            data={
                "employe_code": "EMP001",
                "periode": "2026-01",
                "heures": []
            }
        )

        with pytest.raises(ConnectorError) as exc_info:
            connector.transform_event(event)

        # Une liste vide est traitée comme un champ manquant
        assert "manquants" in str(exc_info.value)

    def test_format_employee_hours_missing_hour_field(self):
        """Test le formatage avec champ manquant dans une ligne d'heures."""
        connector = SilaeConnector()
        event = DomainEvent(
            event_type="feuille_heures.validated",
            data={
                "employe_code": "EMP001",
                "periode": "2026-01",
                "heures": [
                    {
                        "date": "2026-01-15",
                        "type": "normal",
                        # quantite manquant
                    }
                ]
            }
        )

        with pytest.raises(ConnectorError) as exc_info:
            connector.transform_event(event)

        assert "Ligne 0" in str(exc_info.value)
        assert "quantite" in str(exc_info.value)

    def test_format_pointage_validated(self):
        """Test le formatage d'un pointage validé."""
        connector = SilaeConnector()
        event = DomainEvent(
            event_type="pointage.validated",
            aggregate_id="456",
            data={
                "employe_code": "EMP003",
                "periode": "2026-01",
                "heures": [
                    {
                        "date": "2026-01-15",
                        "type": "normal",
                        "quantite": 7.5,
                        "chantier_code": "CHT005"
                    }
                ]
            }
        )

        payload = connector.transform_event(event)

        # Les pointages utilisent le même endpoint
        assert payload["endpoint"] == "/employees/hours"
        assert payload["data"]["employee_code"] == "EMP003"
        assert payload["data"]["period"] == "2026-01"
        assert payload["data"]["external_id"] == "456"

    def test_get_api_endpoint(self):
        """Test la récupération des endpoints."""
        connector = SilaeConnector()

        assert connector.get_api_endpoint("feuille_heures.validated") == "/employees/hours"
        assert connector.get_api_endpoint("pointage.validated") == "/employees/hours"

    def test_get_api_endpoint_unknown(self):
        """Test la récupération d'un endpoint inconnu."""
        connector = SilaeConnector()

        with pytest.raises(ConnectorError) as exc_info:
            connector.get_api_endpoint("unknown.event")

        assert "Pas d'endpoint" in str(exc_info.value)

    def test_unsupported_event(self):
        """Test la transformation d'un événement non supporté."""
        connector = SilaeConnector()
        event = DomainEvent(
            event_type="user.created",
            data={"foo": "bar"}
        )

        with pytest.raises(ConnectorError) as exc_info:
            connector.transform_event(event)

        assert "non supporté" in str(exc_info.value)

    def test_metadata_included(self):
        """Test que les métadonnées sont bien incluses."""
        connector = SilaeConnector()
        event = DomainEvent(
            event_type="feuille_heures.validated",
            data={
                "employe_code": "EMP001",
                "periode": "2026-01",
                "heures": [
                    {
                        "date": "2026-01-15",
                        "type": "normal",
                        "quantite": 8.0
                    }
                ]
            },
            occurred_at=datetime(2026, 1, 31, 12, 0, 0)
        )

        payload = connector.transform_event(event)

        assert payload["metadata"]["source"] == "hub-chantier"
        assert payload["metadata"]["connector"] == "silae"
        assert payload["metadata"]["event_type"] == "feuille_heures.validated"
        assert "event_id" in payload["metadata"]
        assert "occurred_at" in payload["metadata"]
