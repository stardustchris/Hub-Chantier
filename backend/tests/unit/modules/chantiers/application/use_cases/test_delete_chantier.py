"""Tests unitaires pour DeleteChantierUseCase.

Gap: GAP-CHT-006 - Logging structuré
"""

import pytest
from unittest.mock import Mock, patch

from modules.chantiers.domain.entities import Chantier
from modules.chantiers.domain.value_objects import CodeChantier, StatutChantier
from modules.chantiers.domain.repositories import ChantierRepository
from modules.chantiers.application.use_cases.delete_chantier import (
    DeleteChantierUseCase,
    ChantierActifError,
)
from modules.chantiers.application.use_cases.get_chantier import ChantierNotFoundError


class TestDeleteChantierUseCase:
    """Tests pour la suppression d'un chantier."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=ChantierRepository)
        self.mock_event_publisher = Mock()

    def _create_chantier(self, statut: str = "ferme", chantier_id: int = 1) -> Chantier:
        """Crée un chantier de test."""
        return Chantier(
            id=chantier_id,
            code=CodeChantier("A001"),
            nom="Chantier Test",
            adresse="123 Rue Test",
            statut=StatutChantier.from_string(statut),
        )

    # ==================== Tests Succès ====================

    def test_delete_chantier_ferme_success(self):
        """Test: suppression d'un chantier fermé réussit."""
        # Arrange
        use_case = DeleteChantierUseCase(
            chantier_repo=self.mock_repo,
            event_publisher=self.mock_event_publisher,
        )

        chantier = self._create_chantier(statut="ferme")
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.delete.return_value = True

        # Act
        result = use_case.execute(1, force=False)

        # Assert
        assert result is True
        self.mock_repo.delete.assert_called_once_with(1)
        self.mock_event_publisher.assert_called_once()

    def test_delete_chantier_with_force_flag(self):
        """Test: suppression avec force=True permet de supprimer chantier actif."""
        # Arrange
        use_case = DeleteChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier(statut="en_cours")  # Actif
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.delete.return_value = True

        # Act
        result = use_case.execute(1, force=True)

        # Assert
        assert result is True
        self.mock_repo.delete.assert_called_once_with(1)

    def test_delete_chantier_publishes_event(self):
        """Test: événement ChantierDeletedEvent publié."""
        # Arrange
        use_case = DeleteChantierUseCase(
            chantier_repo=self.mock_repo,
            event_publisher=self.mock_event_publisher,
        )

        chantier = self._create_chantier(statut="ferme")
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.delete.return_value = True

        # Act
        use_case.execute(1)

        # Assert
        self.mock_event_publisher.assert_called_once()
        event = self.mock_event_publisher.call_args[0][0]
        assert event.chantier_id == 1
        assert event.code == "A001"
        assert event.nom == "Chantier Test"

    def test_delete_chantier_receptionne_success(self):
        """Test: suppression d'un chantier fermé (après réception) réussit."""
        # Arrange
        use_case = DeleteChantierUseCase(chantier_repo=self.mock_repo)

        # Statut "ferme" car un chantier réceptionné est encore actif
        chantier = self._create_chantier(statut="ferme")
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.delete.return_value = True

        # Act
        result = use_case.execute(1)

        # Assert
        assert result is True
        self.mock_repo.delete.assert_called_once()

    def test_delete_chantier_without_event_publisher_succeeds(self):
        """Test: suppression réussie sans event_publisher (optionnel)."""
        # Arrange
        use_case = DeleteChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier(statut="ferme")
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.delete.return_value = True

        # Act - Pas d'erreur
        result = use_case.execute(1)

        # Assert
        assert result is True

    # ==================== Tests Erreurs ====================

    def test_delete_chantier_not_found_raises_error(self):
        """Test: chantier non trouvé lève ChantierNotFoundError."""
        # Arrange
        use_case = DeleteChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ChantierNotFoundError) as exc_info:
            use_case.execute(999)

        assert exc_info.value.identifier == 999 or exc_info.value.identifier == "999"

    def test_delete_chantier_actif_without_force_raises_error(self):
        """Test: suppression chantier actif sans force lève ChantierActifError."""
        # Arrange
        use_case = DeleteChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier(statut="en_cours")  # Actif
        self.mock_repo.find_by_id.return_value = chantier

        # Act & Assert
        with pytest.raises(ChantierActifError) as exc_info:
            use_case.execute(1, force=False)

        assert exc_info.value.chantier_id == 1
        assert "fermé" in exc_info.value.message

    def test_delete_chantier_ouvert_without_force_raises_error(self):
        """Test: suppression chantier ouvert sans force lève ChantierActifError."""
        # Arrange
        use_case = DeleteChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier(statut="ouvert")  # Actif
        self.mock_repo.find_by_id.return_value = chantier

        # Act & Assert
        with pytest.raises(ChantierActifError):
            use_case.execute(1, force=False)

    def test_delete_chantier_returns_false_if_repo_fails(self):
        """Test: retourne False si repository échoue."""
        # Arrange
        use_case = DeleteChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier(statut="ferme")
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.delete.return_value = False  # Échec

        # Act
        result = use_case.execute(1)

        # Assert
        assert result is False

    # ==================== Tests Logging Structuré (GAP-CHT-006) ====================

    @patch('modules.chantiers.application.use_cases.delete_chantier.logger')
    def test_execute_logs_started_event(self, mock_logger):
        """Test: execute() log événement 'started' avec extra dict."""
        # Arrange
        use_case = DeleteChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier(statut="ferme")
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.delete.return_value = True

        # Act
        use_case.execute(1, force=False)

        # Assert
        info_calls = mock_logger.info.call_args_list
        started_call = info_calls[0]

        assert "Use case execution started" in started_call.args[0]
        assert 'extra' in started_call.kwargs
        extra = started_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.started"
        assert extra['use_case'] == "DeleteChantierUseCase"
        assert extra['chantier_id'] == 1
        assert extra['operation'] == "delete"
        assert extra['force'] == False

    @patch('modules.chantiers.application.use_cases.delete_chantier.logger')
    def test_execute_logs_succeeded_event(self, mock_logger):
        """Test: execute() log événement 'succeeded' avec détails."""
        # Arrange
        use_case = DeleteChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier(statut="ferme")
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.delete.return_value = True

        # Act
        use_case.execute(1)

        # Assert
        info_calls = mock_logger.info.call_args_list
        assert len(info_calls) >= 2
        succeeded_call = info_calls[1]

        assert "Use case execution succeeded" in succeeded_call.args[0]
        extra = succeeded_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.succeeded"
        assert extra['use_case'] == "DeleteChantierUseCase"
        assert extra['chantier_id'] == 1
        assert extra['chantier_code'] == "A001"

    @patch('modules.chantiers.application.use_cases.delete_chantier.logger')
    def test_execute_logs_failed_event_on_error(self, mock_logger):
        """Test: execute() log événement 'failed' en cas d'erreur."""
        # Arrange
        use_case = DeleteChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ChantierNotFoundError):
            use_case.execute(999)

        # Assert
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args

        assert "Use case execution failed" in error_call.args[0]
        extra = error_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.failed"
        assert extra['use_case'] == "DeleteChantierUseCase"
        assert extra['chantier_id'] == 999
        assert extra['error_type'] == "ChantierNotFoundError"
        assert 'error_message' in extra

    @patch('modules.chantiers.application.use_cases.delete_chantier.logger')
    def test_execute_logs_chantier_actif_error(self, mock_logger):
        """Test: échec suppression chantier actif log erreur ChantierActifError."""
        # Arrange
        use_case = DeleteChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier(statut="en_cours")
        self.mock_repo.find_by_id.return_value = chantier

        # Act & Assert
        with pytest.raises(ChantierActifError):
            use_case.execute(1, force=False)

        # Assert
        mock_logger.error.assert_called_once()
        extra = mock_logger.error.call_args.kwargs['extra']
        assert extra['error_type'] == "ChantierActifError"
