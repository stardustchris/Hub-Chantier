"""Tests unitaires pour AssignResponsableUseCase.

Gap: GAP-CHT-006 - Logging structuré
"""

import pytest
from unittest.mock import Mock, patch

from modules.chantiers.domain.entities import Chantier
from modules.chantiers.domain.value_objects import CodeChantier, StatutChantier
from modules.chantiers.domain.repositories import ChantierRepository
from modules.chantiers.application.use_cases.assign_responsable import (
    AssignResponsableUseCase,
    InvalidRoleTypeError,
)
from modules.chantiers.application.use_cases.get_chantier import ChantierNotFoundError
from modules.chantiers.application.dtos import AssignResponsableDTO


class TestAssignResponsableUseCase:
    """Tests pour l'assignation de responsables à un chantier."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=ChantierRepository)
        self.mock_event_publisher = Mock()

    def _create_chantier(self, chantier_id: int = 1) -> Chantier:
        """Crée un chantier de test."""
        return Chantier(
            id=chantier_id,
            code=CodeChantier("A001"),
            nom="Chantier Test",
            adresse="123 Rue Test",
            statut=StatutChantier.ouvert(),
        )

    # ==================== Tests Succès - Conducteur ====================

    def test_assign_conducteur_success(self):
        """Test: assignation d'un conducteur réussit (CHT-05)."""
        # Arrange
        use_case = AssignResponsableUseCase(
            chantier_repo=self.mock_repo,
            event_publisher=self.mock_event_publisher,
        )

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = AssignResponsableDTO(user_id=10, role_type="conducteur")

        # Act
        result = use_case.execute(1, dto)

        # Assert
        assert 10 in result.conducteur_ids
        self.mock_repo.save.assert_called_once()
        self.mock_event_publisher.assert_called_once()

    def test_assign_conducteur_publishes_event(self):
        """Test: événement ConducteurAssigneEvent publié."""
        # Arrange
        use_case = AssignResponsableUseCase(
            chantier_repo=self.mock_repo,
            event_publisher=self.mock_event_publisher,
        )

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = AssignResponsableDTO(user_id=15, role_type="conducteur")

        # Act
        use_case.execute(1, dto)

        # Assert
        self.mock_event_publisher.assert_called_once()
        event = self.mock_event_publisher.call_args[0][0]
        assert event.chantier_id == 1
        assert event.conducteur_id == 15
        assert event.code == "A001"

    def test_assigner_conducteur_shortcut_method(self):
        """Test: méthode raccourci assigner_conducteur()."""
        # Arrange
        use_case = AssignResponsableUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        # Act
        result = use_case.assigner_conducteur(1, 20)

        # Assert
        assert 20 in result.conducteur_ids
        self.mock_repo.save.assert_called_once()

    def test_retirer_conducteur_success(self):
        """Test: retrait d'un conducteur réussit."""
        # Arrange
        use_case = AssignResponsableUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        chantier.assigner_conducteur(25)
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        # Act
        result = use_case.retirer_conducteur(1, 25)

        # Assert
        assert 25 not in result.conducteur_ids
        self.mock_repo.save.assert_called_once()

    # ==================== Tests Succès - Chef de Chantier ====================

    def test_assign_chef_chantier_success(self):
        """Test: assignation d'un chef de chantier réussit (CHT-06)."""
        # Arrange
        use_case = AssignResponsableUseCase(
            chantier_repo=self.mock_repo,
            event_publisher=self.mock_event_publisher,
        )

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = AssignResponsableDTO(user_id=30, role_type="chef_chantier")

        # Act
        result = use_case.execute(1, dto)

        # Assert
        assert 30 in result.chef_chantier_ids
        self.mock_repo.save.assert_called_once()
        self.mock_event_publisher.assert_called_once()

    def test_assign_chef_with_variant_role_type(self):
        """Test: assignation chef accepte 'chef' comme variante."""
        # Arrange
        use_case = AssignResponsableUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = AssignResponsableDTO(user_id=35, role_type="chef")  # Variante

        # Act
        result = use_case.execute(1, dto)

        # Assert
        assert 35 in result.chef_chantier_ids
        self.mock_repo.save.assert_called_once()

    def test_assign_chef_publishes_event(self):
        """Test: événement ChefChantierAssigneEvent publié."""
        # Arrange
        use_case = AssignResponsableUseCase(
            chantier_repo=self.mock_repo,
            event_publisher=self.mock_event_publisher,
        )

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = AssignResponsableDTO(user_id=40, role_type="chef_chantier")

        # Act
        use_case.execute(1, dto)

        # Assert
        self.mock_event_publisher.assert_called_once()
        event = self.mock_event_publisher.call_args[0][0]
        assert event.chantier_id == 1
        assert event.chef_id == 40
        assert event.code == "A001"

    def test_assigner_chef_chantier_shortcut_method(self):
        """Test: méthode raccourci assigner_chef_chantier()."""
        # Arrange
        use_case = AssignResponsableUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        # Act
        result = use_case.assigner_chef_chantier(1, 45)

        # Assert
        assert 45 in result.chef_chantier_ids
        self.mock_repo.save.assert_called_once()

    def test_retirer_chef_chantier_success(self):
        """Test: retrait d'un chef de chantier réussit."""
        # Arrange
        use_case = AssignResponsableUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        chantier.assigner_chef_chantier(50)
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        # Act
        result = use_case.retirer_chef_chantier(1, 50)

        # Assert
        assert 50 not in result.chef_chantier_ids
        self.mock_repo.save.assert_called_once()

    # ==================== Tests Cas Limites ====================

    def test_assign_role_type_case_insensitive(self):
        """Test: role_type insensible à la casse."""
        # Arrange
        use_case = AssignResponsableUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = AssignResponsableDTO(user_id=55, role_type="CONDUCTEUR")

        # Act
        result = use_case.execute(1, dto)

        # Assert
        assert 55 in result.conducteur_ids

    def test_assign_role_type_with_whitespace(self):
        """Test: role_type avec espaces est nettoyé."""
        # Arrange
        use_case = AssignResponsableUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = AssignResponsableDTO(user_id=60, role_type="  chef_chantier  ")

        # Act
        result = use_case.execute(1, dto)

        # Assert
        assert 60 in result.chef_chantier_ids

    def test_assign_without_event_publisher_succeeds(self):
        """Test: assignation réussie sans event_publisher (optionnel)."""
        # Arrange
        use_case = AssignResponsableUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = AssignResponsableDTO(user_id=65, role_type="conducteur")

        # Act - Pas d'erreur
        result = use_case.execute(1, dto)

        # Assert
        assert 65 in result.conducteur_ids

    # ==================== Tests Erreurs ====================

    def test_assign_chantier_not_found_raises_error(self):
        """Test: chantier non trouvé lève ChantierNotFoundError."""
        # Arrange
        use_case = AssignResponsableUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.find_by_id.return_value = None

        dto = AssignResponsableDTO(user_id=70, role_type="conducteur")

        # Act & Assert
        with pytest.raises(ChantierNotFoundError) as exc_info:
            use_case.execute(999, dto)

        assert exc_info.value.identifier == 999 or exc_info.value.identifier == "999"

    def test_assign_invalid_role_type_raises_error(self):
        """Test: role_type invalide lève InvalidRoleTypeError."""
        # Arrange
        use_case = AssignResponsableUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier

        dto = AssignResponsableDTO(user_id=75, role_type="manager")  # Invalide

        # Act & Assert
        with pytest.raises(InvalidRoleTypeError) as exc_info:
            use_case.execute(1, dto)

        assert exc_info.value.role_type == "manager"
        assert "conducteur" in exc_info.value.message
        assert "chef_chantier" in exc_info.value.message

    def test_retirer_conducteur_chantier_not_found_raises_error(self):
        """Test: retrait conducteur avec chantier non trouvé lève erreur."""
        # Arrange
        use_case = AssignResponsableUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ChantierNotFoundError):
            use_case.retirer_conducteur(999, 80)

    def test_retirer_chef_chantier_not_found_raises_error(self):
        """Test: retrait chef avec chantier non trouvé lève erreur."""
        # Arrange
        use_case = AssignResponsableUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ChantierNotFoundError):
            use_case.retirer_chef_chantier(999, 85)

    # ==================== Tests Logging Structuré (GAP-CHT-006) ====================

    @patch('modules.chantiers.application.use_cases.assign_responsable.logger')
    def test_execute_logs_started_event(self, mock_logger):
        """Test: execute() log événement 'started' avec extra dict."""
        # Arrange
        use_case = AssignResponsableUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = AssignResponsableDTO(user_id=90, role_type="conducteur")

        # Act
        use_case.execute(1, dto)

        # Assert
        info_calls = mock_logger.info.call_args_list
        started_call = info_calls[0]

        assert "Use case execution started" in started_call.args[0]
        assert 'extra' in started_call.kwargs
        extra = started_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.started"
        assert extra['use_case'] == "AssignResponsableUseCase"
        assert extra['chantier_id'] == 1
        assert extra['operation'] == "assign_responsable"
        assert extra['user_id'] == 90
        assert extra['role_type'] == "conducteur"

    @patch('modules.chantiers.application.use_cases.assign_responsable.logger')
    def test_execute_logs_succeeded_event(self, mock_logger):
        """Test: execute() log événement 'succeeded' avec détails."""
        # Arrange
        use_case = AssignResponsableUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = AssignResponsableDTO(user_id=95, role_type="chef_chantier")

        # Act
        use_case.execute(1, dto)

        # Assert
        info_calls = mock_logger.info.call_args_list
        assert len(info_calls) >= 2
        succeeded_call = info_calls[1]

        assert "Use case execution succeeded" in succeeded_call.args[0]
        extra = succeeded_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.succeeded"
        assert extra['use_case'] == "AssignResponsableUseCase"
        assert extra['chantier_id'] == 1
        assert extra['user_id'] == 95
        assert extra['role_type'] == "chef_chantier"

    @patch('modules.chantiers.application.use_cases.assign_responsable.logger')
    def test_execute_logs_failed_event_on_error(self, mock_logger):
        """Test: execute() log événement 'failed' en cas d'erreur."""
        # Arrange
        use_case = AssignResponsableUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.find_by_id.return_value = None

        dto = AssignResponsableDTO(user_id=100, role_type="conducteur")

        # Act & Assert
        with pytest.raises(ChantierNotFoundError):
            use_case.execute(999, dto)

        # Assert
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args

        assert "Use case execution failed" in error_call.args[0]
        extra = error_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.failed"
        assert extra['use_case'] == "AssignResponsableUseCase"
        assert extra['chantier_id'] == 999
        assert extra['error_type'] == "ChantierNotFoundError"
        assert 'error_message' in extra

    @patch('modules.chantiers.application.use_cases.assign_responsable.logger')
    def test_execute_logs_invalid_role_error(self, mock_logger):
        """Test: erreur role invalide log événement 'failed' avec type d'erreur."""
        # Arrange
        use_case = AssignResponsableUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier

        dto = AssignResponsableDTO(user_id=105, role_type="invalid")

        # Act & Assert
        with pytest.raises(InvalidRoleTypeError):
            use_case.execute(1, dto)

        # Assert
        mock_logger.error.assert_called_once()
        extra = mock_logger.error.call_args.kwargs['extra']
        assert extra['error_type'] == "InvalidRoleTypeError"
