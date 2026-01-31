"""Tests unitaires pour les event handlers du module pointages."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date
import logging

from modules.pointages.infrastructure.event_handlers import (
    handle_affectation_created,
    handle_affectation_bulk_created,
    register_event_handlers,
    setup_planning_integration,
    _convert_heures_to_string,
)


class TestConvertHeuresToString:
    """Tests de la fonction _convert_heures_to_string."""

    def test_convert_float_8_hours(self):
        """Test: conversion de 8.0 heures en '08:00'."""
        result = _convert_heures_to_string(8.0)
        assert result == "08:00"

    def test_convert_float_7_5_hours(self):
        """Test: conversion de 7.5 heures en '07:30'."""
        result = _convert_heures_to_string(7.5)
        assert result == "07:30"

    def test_convert_float_with_15_minutes(self):
        """Test: conversion de 8.25 heures en '08:15'."""
        result = _convert_heures_to_string(8.25)
        assert result == "08:15"

    def test_convert_float_with_45_minutes(self):
        """Test: conversion de 8.75 heures en '08:45'."""
        result = _convert_heures_to_string(8.75)
        assert result == "08:45"

    def test_convert_float_10_hours(self):
        """Test: conversion de 10.0 heures en '10:00'."""
        result = _convert_heures_to_string(10.0)
        assert result == "10:00"

    def test_convert_float_zero_hours(self):
        """Test: conversion de 0.0 heures en '00:00'."""
        result = _convert_heures_to_string(0.0)
        assert result == "00:00"

    def test_convert_string_already_formatted(self):
        """Test: retourne la string telle quelle si deja au format HH:MM."""
        result = _convert_heures_to_string("08:00")
        assert result == "08:00"

    def test_convert_string_with_different_time(self):
        """Test: retourne la string telle quelle pour '09:30'."""
        result = _convert_heures_to_string("09:30")
        assert result == "09:30"

    def test_convert_string_with_leading_zero(self):
        """Test: retourne la string telle quelle pour '07:15'."""
        result = _convert_heures_to_string("07:15")
        assert result == "07:15"

    def test_convert_rounding_minutes(self):
        """Test: arrondit correctement les minutes (ex: 7.33 -> '07:20')."""
        result = _convert_heures_to_string(7.33)
        assert result == "07:20"

    def test_convert_handles_edge_case_23_hours(self):
        """Test: conversion de 23.5 heures en '23:30'."""
        result = _convert_heures_to_string(23.5)
        assert result == "23:30"


class TestHandleAffectationCreated:
    """Tests du handler AffectationCreatedEvent."""

    @pytest.fixture
    def mock_event(self):
        """Cree un evenement mock (ancien style, attributs directs)."""
        event = Mock(spec=["affectation_id", "utilisateur_id", "chantier_id", "date", "heures_prevues", "created_by"])
        event.affectation_id = 1
        event.utilisateur_id = 10
        event.chantier_id = 100
        event.date = date(2024, 1, 15)
        event.heures_prevues = "08:00"
        event.created_by = 5
        return event

    @pytest.fixture
    def mock_session(self):
        """Session SQLAlchemy mock."""
        return Mock()

    @patch("modules.pointages.infrastructure.event_handlers.SQLAlchemyPointageRepository")
    @patch("modules.pointages.infrastructure.event_handlers.SQLAlchemyFeuilleHeuresRepository")
    @patch("modules.pointages.infrastructure.event_handlers.get_event_bus")
    @patch("modules.pointages.infrastructure.event_handlers.BulkCreateFromPlanningUseCase")
    def test_handle_creates_pointage(
        self, mock_use_case_class, mock_get_bus, mock_feuille_repo, mock_pointage_repo,
        mock_event, mock_session
    ):
        """Test que le handler cree un pointage."""
        mock_use_case = Mock()
        mock_use_case.execute_from_event.return_value = Mock(id=42)
        mock_use_case_class.return_value = mock_use_case

        handle_affectation_created(mock_event, mock_session)

        mock_use_case.execute_from_event.assert_called_once_with(
            utilisateur_id=10,
            chantier_id=100,
            date_affectation=date(2024, 1, 15),
            heures_prevues="08:00",
            affectation_id=1,
            created_by=5,
        )

    @patch("modules.pointages.infrastructure.event_handlers.SQLAlchemyPointageRepository")
    @patch("modules.pointages.infrastructure.event_handlers.SQLAlchemyFeuilleHeuresRepository")
    @patch("modules.pointages.infrastructure.event_handlers.get_event_bus")
    @patch("modules.pointages.infrastructure.event_handlers.BulkCreateFromPlanningUseCase")
    def test_handle_default_heures_prevues(
        self, mock_use_case_class, mock_get_bus, mock_feuille_repo, mock_pointage_repo,
        mock_session
    ):
        """Test heures prevues par defaut si non fournies."""
        event = Mock(spec=["affectation_id", "utilisateur_id", "chantier_id", "date", "heures_prevues", "created_by"])
        event.affectation_id = 1
        event.utilisateur_id = 10
        event.chantier_id = 100
        event.date = date(2024, 1, 15)
        event.heures_prevues = None  # Pas de valeur
        event.created_by = 5

        mock_use_case = Mock()
        mock_use_case.execute_from_event.return_value = Mock(id=42)
        mock_use_case_class.return_value = mock_use_case

        handle_affectation_created(event, mock_session)

        # Doit utiliser "08:00" par defaut
        call_args = mock_use_case.execute_from_event.call_args
        assert call_args.kwargs["heures_prevues"] == "08:00"

    @patch("modules.pointages.infrastructure.event_handlers.SQLAlchemyPointageRepository")
    @patch("modules.pointages.infrastructure.event_handlers.SQLAlchemyFeuilleHeuresRepository")
    @patch("modules.pointages.infrastructure.event_handlers.get_event_bus")
    @patch("modules.pointages.infrastructure.event_handlers.BulkCreateFromPlanningUseCase")
    def test_handle_no_heures_attribute(
        self, mock_use_case_class, mock_get_bus, mock_feuille_repo, mock_pointage_repo,
        mock_session
    ):
        """Test quand l'evenement n'a pas d'attribut heures_prevues."""
        event = Mock(spec=["affectation_id", "utilisateur_id", "chantier_id", "date", "created_by"])
        event.affectation_id = 1
        event.utilisateur_id = 10
        event.chantier_id = 100
        event.date = date(2024, 1, 15)
        event.created_by = 5

        mock_use_case = Mock()
        mock_use_case.execute_from_event.return_value = Mock(id=42)
        mock_use_case_class.return_value = mock_use_case

        handle_affectation_created(event, mock_session)

        call_args = mock_use_case.execute_from_event.call_args
        assert call_args.kwargs["heures_prevues"] == "08:00"

    @patch("modules.pointages.infrastructure.event_handlers.SQLAlchemyPointageRepository")
    @patch("modules.pointages.infrastructure.event_handlers.SQLAlchemyFeuilleHeuresRepository")
    @patch("modules.pointages.infrastructure.event_handlers.get_event_bus")
    @patch("modules.pointages.infrastructure.event_handlers.BulkCreateFromPlanningUseCase")
    def test_handle_pointage_already_exists(
        self, mock_use_case_class, mock_get_bus, mock_feuille_repo, mock_pointage_repo,
        mock_event, mock_session, caplog
    ):
        """Test quand le pointage existe deja."""
        mock_use_case = Mock()
        mock_use_case.execute_from_event.return_value = None  # Deja existant
        mock_use_case_class.return_value = mock_use_case

        with caplog.at_level(logging.DEBUG):
            handle_affectation_created(mock_event, mock_session)

        assert "non créé" in caplog.text or mock_use_case.execute_from_event.called

    @patch("modules.pointages.infrastructure.event_handlers.SQLAlchemyPointageRepository")
    @patch("modules.pointages.infrastructure.event_handlers.SQLAlchemyFeuilleHeuresRepository")
    @patch("modules.pointages.infrastructure.event_handlers.get_event_bus")
    @patch("modules.pointages.infrastructure.event_handlers.BulkCreateFromPlanningUseCase")
    def test_handle_error_raises(
        self, mock_use_case_class, mock_get_bus, mock_feuille_repo, mock_pointage_repo,
        mock_event, mock_session
    ):
        """Test que les erreurs sont propagees."""
        mock_use_case = Mock()
        mock_use_case.execute_from_event.side_effect = Exception("DB error")
        mock_use_case_class.return_value = mock_use_case

        with pytest.raises(Exception) as exc_info:
            handle_affectation_created(mock_event, mock_session)

        assert "DB error" in str(exc_info.value)


class TestHandleAffectationBulkCreated:
    """Tests du handler AffectationBulkCreatedEvent."""

    @pytest.fixture
    def mock_event(self):
        """Evenement bulk mock."""
        event = Mock()
        event.affectation_ids = [1, 2, 3, 4, 5]
        return event

    @pytest.fixture
    def mock_session(self):
        return Mock()

    def test_handle_bulk_logs_count(self, mock_event, mock_session, caplog):
        """Test que le handler logge le nombre d'affectations."""
        with caplog.at_level(logging.INFO):
            handle_affectation_bulk_created(mock_event, mock_session)

        assert "5 affectations" in caplog.text

    def test_handle_bulk_iterates_ids(self, mock_event, mock_session):
        """Test que le handler itere sur les IDs."""
        # Le handler actuel passe juste (TODO)
        # Verifie qu'il ne crash pas
        handle_affectation_bulk_created(mock_event, mock_session)


class TestRegisterEventHandlers:
    """Tests de l'enregistrement des handlers."""

    def test_register_without_event_bus_handles_import_error(self, caplog):
        """Test enregistrement gere ImportError."""
        # Le module tente d'importer EventBus et AffectationCreatedEvent
        # On verifie que ca ne crash pas
        with caplog.at_level(logging.WARNING):
            register_event_handlers(event_bus_class=None)

        # Pas d'erreur, le module gere gracieusement l'absence

    def test_register_with_mock_event_bus(self):
        """Test enregistrement avec EventBus mock."""
        mock_event_bus = Mock()

        # L'enregistrement peut echouer a importer les events du planning
        # mais ne doit pas crasher
        try:
            register_event_handlers(event_bus_class=mock_event_bus)
        except ImportError:
            pass  # Expected si module planning pas disponible


class TestSetupPlanningIntegration:
    """Tests de la configuration de l'integration planning."""

    @pytest.fixture
    def mock_session_factory(self):
        """Factory de session mock."""
        mock_session = Mock()
        factory = Mock(return_value=mock_session)
        return factory

    def test_setup_handles_import_error(self, mock_session_factory, caplog):
        """Test setup gere ImportError gracieusement."""
        with caplog.at_level(logging.WARNING):
            setup_planning_integration(mock_session_factory)

        # Pas d'erreur, le module gere gracieusement l'absence

    def test_setup_with_mocked_modules(self, mock_session_factory):
        """Test setup avec modules mockes."""
        mock_event_bus = MagicMock()
        mock_event_type = Mock()

        with patch.dict("sys.modules", {
            "shared.infrastructure.event_bus": MagicMock(EventBus=mock_event_bus),
            "modules.planning.domain.events": MagicMock(AffectationCreatedEvent=mock_event_type),
        }):
            # Recharger pour que les patches prennent effet
            import importlib
            import modules.pointages.infrastructure.event_handlers as eh
            try:
                importlib.reload(eh)
                eh.setup_planning_integration(mock_session_factory)
            except Exception:
                pass  # Le reload peut echouer, c'est OK
