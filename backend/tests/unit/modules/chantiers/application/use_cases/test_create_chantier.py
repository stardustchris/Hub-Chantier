"""Tests unitaires pour CreateChantierUseCase.

Gap: GAP-CHT-006 - Logging structuré
"""

import pytest
from unittest.mock import Mock, patch
from datetime import date

from modules.chantiers.domain.entities import Chantier
from modules.chantiers.domain.value_objects import CodeChantier, StatutChantier
from modules.chantiers.domain.repositories import ChantierRepository
from modules.chantiers.application.use_cases.create_chantier import (
    CreateChantierUseCase,
    CodeChantierAlreadyExistsError,
    InvalidDatesError,
)
from modules.chantiers.application.dtos import CreateChantierDTO


class TestCreateChantierUseCase:
    """Tests pour la création d'un chantier."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=ChantierRepository)
        self.mock_event_publisher = Mock()

    def _create_chantier_entity(self, code: str = "A001", nom: str = "Chantier Test") -> Chantier:
        """Crée une entité chantier de test."""
        return Chantier(
            id=1,
            code=CodeChantier(code),
            nom=nom,
            adresse="123 Rue Test",
            statut=StatutChantier.ouvert(),
        )

    # ==================== Tests Succès ====================

    def test_create_chantier_with_all_fields(self):
        """Test: création chantier avec tous les champs."""
        # Arrange
        use_case = CreateChantierUseCase(
            chantier_repo=self.mock_repo,
            event_publisher=self.mock_event_publisher,
        )

        self.mock_repo.exists_by_code.return_value = False
        created_chantier = self._create_chantier_entity()
        self.mock_repo.save.return_value = created_chantier

        dto = CreateChantierDTO(
            code="A001",
            nom="Chantier Test",
            adresse="123 Rue Test",
            couleur="#FF0000",
            latitude=48.8566,
            longitude=2.3522,
            contact_nom="Jean Dupont",
            contact_telephone="0612345678",
            heures_estimees=100.0,
            date_debut="2026-02-01",
            date_fin="2026-06-30",
            description="Description test",
            conducteur_ids=[1, 2],
            chef_chantier_ids=[3],
        )

        # Act
        result = use_case.execute(dto)

        # Assert
        assert result.code == "A001"
        assert result.nom == "Chantier Test"
        self.mock_repo.exists_by_code.assert_called_once()
        self.mock_repo.save.assert_called_once()
        self.mock_event_publisher.assert_called_once()

    def test_create_chantier_with_minimal_fields(self):
        """Test: création chantier avec champs minimaux (nom, adresse)."""
        # Arrange
        use_case = CreateChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.get_last_code.return_value = "A001"  # Retourne string, pas CodeChantier
        created_chantier = self._create_chantier_entity("A002", "Minimal")
        self.mock_repo.save.return_value = created_chantier

        dto = CreateChantierDTO(
            nom="Minimal",
            adresse="Adresse minimale",
        )

        # Act
        result = use_case.execute(dto)

        # Assert
        assert result.nom == "Minimal"
        self.mock_repo.get_last_code.assert_called_once()
        self.mock_repo.save.assert_called_once()

    def test_create_chantier_auto_generates_code(self):
        """Test: génération automatique du code chantier (CHT-19)."""
        # Arrange
        use_case = CreateChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.get_last_code.return_value = "A005"
        created_chantier = self._create_chantier_entity("A006")
        self.mock_repo.save.return_value = created_chantier

        dto = CreateChantierDTO(nom="Test", adresse="Test")

        # Act
        result = use_case.execute(dto)

        # Assert
        self.mock_repo.get_last_code.assert_called_once()
        assert result.code == "A006"

    def test_create_chantier_with_gps_coordinates(self):
        """Test: création chantier avec coordonnées GPS (CHT-04)."""
        # Arrange
        use_case = CreateChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.get_last_code.return_value = "A001"

        # Mock save pour retourner le chantier passé en paramètre
        def save_side_effect(chantier):
            chantier.id = 1
            return chantier
        self.mock_repo.save.side_effect = save_side_effect

        dto = CreateChantierDTO(
            nom="Test GPS",
            adresse="Test",
            latitude=45.764043,
            longitude=4.835659,
        )

        # Act
        result = use_case.execute(dto)

        # Assert
        assert result.coordonnees_gps is not None
        assert result.coordonnees_gps["latitude"] == 45.764043

    def test_create_chantier_with_contact(self):
        """Test: création chantier avec contact (CHT-07)."""
        # Arrange
        use_case = CreateChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.get_last_code.return_value = "A001"

        def save_side_effect(chantier):
            chantier.id = 1
            return chantier
        self.mock_repo.save.side_effect = save_side_effect

        dto = CreateChantierDTO(
            nom="Test Contact",
            adresse="Test",
            contact_nom="Marie Martin",
            contact_telephone="0698765432",
        )

        # Act
        result = use_case.execute(dto)

        # Assert
        assert result.contact is not None
        assert result.contact["nom"] == "Marie Martin"

    def test_create_chantier_with_dates(self):
        """Test: création chantier avec dates (CHT-20)."""
        # Arrange
        use_case = CreateChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.get_last_code.return_value = "A001"

        def save_side_effect(chantier):
            chantier.id = 1
            return chantier
        self.mock_repo.save.side_effect = save_side_effect

        dto = CreateChantierDTO(
            nom="Test Dates",
            adresse="Test",
            date_debut="2026-03-01",
            date_fin="2026-09-30",
        )

        # Act
        result = use_case.execute(dto)

        # Assert
        assert result.date_debut == "2026-03-01"
        assert result.date_fin == "2026-09-30"

    def test_create_chantier_publishes_event(self):
        """Test: événement ChantierCreatedEvent publié."""
        # Arrange
        use_case = CreateChantierUseCase(
            chantier_repo=self.mock_repo,
            event_publisher=self.mock_event_publisher,
        )

        self.mock_repo.get_last_code.return_value = "A001"
        created_chantier = self._create_chantier_entity("A002", "Event Test")
        self.mock_repo.save.return_value = created_chantier

        dto = CreateChantierDTO(
            nom="Event Test",
            adresse="Test",
            conducteur_ids=[5],
            chef_chantier_ids=[10],
        )

        # Act
        use_case.execute(dto)

        # Assert
        self.mock_event_publisher.assert_called_once()
        event = self.mock_event_publisher.call_args[0][0]
        assert event.chantier_id == 1
        assert event.code == "A002"
        assert event.nom == "Event Test"

    # ==================== Tests Erreurs ====================

    def test_create_chantier_with_duplicate_code_raises_error(self):
        """Test: code chantier déjà existant lève CodeChantierAlreadyExistsError."""
        # Arrange
        use_case = CreateChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.exists_by_code.return_value = True

        dto = CreateChantierDTO(
            code="A001",
            nom="Duplicate",
            adresse="Test",
        )

        # Act & Assert
        with pytest.raises(CodeChantierAlreadyExistsError) as exc_info:
            use_case.execute(dto)

        assert exc_info.value.code == "A001"
        assert "déjà utilisé" in exc_info.value.message

    def test_create_chantier_with_invalid_dates_raises_error(self):
        """Test: date_fin < date_debut lève InvalidDatesError."""
        # Arrange
        use_case = CreateChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.get_last_code.return_value = "A001"

        dto = CreateChantierDTO(
            nom="Invalid Dates",
            adresse="Test",
            date_debut="2026-06-30",
            date_fin="2026-02-01",  # Avant date_debut
        )

        # Act & Assert
        with pytest.raises(InvalidDatesError) as exc_info:
            use_case.execute(dto)

        assert "antérieure" in exc_info.value.message

    def test_create_chantier_without_event_publisher_succeeds(self):
        """Test: création réussie sans event_publisher (optionnel)."""
        # Arrange
        use_case = CreateChantierUseCase(chantier_repo=self.mock_repo)  # Pas d'event_publisher

        self.mock_repo.get_last_code.return_value = "A001"

        def save_side_effect(chantier):
            chantier.id = 1
            return chantier
        self.mock_repo.save.side_effect = save_side_effect

        dto = CreateChantierDTO(nom="No Events", adresse="Test")

        # Act - Pas d'erreur
        result = use_case.execute(dto)

        # Assert
        assert result.nom == "No Events"

    # ==================== Tests Logging Structuré (GAP-CHT-006) ====================

    @patch('modules.chantiers.application.use_cases.create_chantier.logger')
    def test_execute_logs_started_event(self, mock_logger):
        """Test: execute() log événement 'started' avec extra dict."""
        # Arrange
        use_case = CreateChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.exists_by_code.return_value = False
        created_chantier = self._create_chantier_entity()
        self.mock_repo.save.return_value = created_chantier

        dto = CreateChantierDTO(code="A001", nom="Log Test", adresse="Test")

        # Act
        use_case.execute(dto)

        # Assert
        info_calls = mock_logger.info.call_args_list
        started_call = info_calls[0]

        assert "Use case execution started" in started_call.args[0]
        assert 'extra' in started_call.kwargs
        extra = started_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.started"
        assert extra['use_case'] == "CreateChantierUseCase"
        assert extra['operation'] == "create"
        assert extra['chantier_nom'] == "Log Test"
        assert extra['chantier_code'] == "A001"

    @patch('modules.chantiers.application.use_cases.create_chantier.logger')
    def test_execute_logs_succeeded_event(self, mock_logger):
        """Test: execute() log événement 'succeeded' avec détails."""
        # Arrange
        use_case = CreateChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.get_last_code.return_value = "A001"
        created_chantier = self._create_chantier_entity("A002", "Success")
        self.mock_repo.save.return_value = created_chantier

        dto = CreateChantierDTO(nom="Success", adresse="Test")

        # Act
        use_case.execute(dto)

        # Assert
        info_calls = mock_logger.info.call_args_list
        assert len(info_calls) >= 2
        succeeded_call = info_calls[1]

        assert "Use case execution succeeded" in succeeded_call.args[0]
        extra = succeeded_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.succeeded"
        assert extra['use_case'] == "CreateChantierUseCase"
        assert extra['chantier_id'] == 1
        assert extra['chantier_code'] == "A002"
        assert extra['chantier_nom'] == "Success"

    @patch('modules.chantiers.application.use_cases.create_chantier.logger')
    def test_execute_logs_failed_event_on_error(self, mock_logger):
        """Test: execute() log événement 'failed' en cas d'erreur."""
        # Arrange
        use_case = CreateChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.exists_by_code.return_value = True

        dto = CreateChantierDTO(code="A999", nom="Fail", adresse="Test")

        # Act & Assert
        with pytest.raises(CodeChantierAlreadyExistsError):
            use_case.execute(dto)

        # Assert
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args

        assert "Use case execution failed" in error_call.args[0]
        extra = error_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.failed"
        assert extra['use_case'] == "CreateChantierUseCase"
        assert extra['operation'] == "create"
        assert extra['error_type'] == "CodeChantierAlreadyExistsError"
        assert 'error_message' in extra
