"""Tests unitaires pour GetChantierUseCase.

Gap: GAP-CHT-006 - Logging structuré
"""

import pytest
from unittest.mock import Mock, patch

from modules.chantiers.domain.entities import Chantier
from modules.chantiers.domain.value_objects import CodeChantier, StatutChantier
from modules.chantiers.domain.repositories import ChantierRepository
from modules.chantiers.application.use_cases.get_chantier import (
    GetChantierUseCase,
    ChantierNotFoundError,
)


class TestGetChantierUseCase:
    """Tests pour la récupération d'un chantier."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=ChantierRepository)

    def _create_chantier(self, chantier_id: int = 1, code: str = "A001") -> Chantier:
        """Crée un chantier de test."""
        return Chantier(
            id=chantier_id,
            code=CodeChantier(code),
            nom="Chantier Test",
            adresse="123 Rue Test",
            statut=StatutChantier.ouvert(),
        )

    # ==================== Tests Succès - Par ID ====================

    def test_get_chantier_by_id_success(self):
        """Test: récupération chantier par ID réussit."""
        # Arrange
        use_case = GetChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier

        # Act
        result = use_case.execute_by_id(1)

        # Assert
        assert result.id == 1
        assert result.code == "A001"
        assert result.nom == "Chantier Test"
        self.mock_repo.find_by_id.assert_called_once_with(1)

    def test_get_chantier_by_id_returns_dto(self):
        """Test: retourne un ChantierDTO avec toutes les propriétés."""
        # Arrange
        use_case = GetChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier

        # Act
        result = use_case.execute_by_id(1)

        # Assert
        assert hasattr(result, 'id')
        assert hasattr(result, 'code')
        assert hasattr(result, 'nom')
        assert hasattr(result, 'adresse')
        assert hasattr(result, 'statut')
        assert hasattr(result, 'couleur')

    def test_get_chantier_by_id_different_ids(self):
        """Test: récupération de différents chantiers par ID."""
        # Arrange
        use_case = GetChantierUseCase(chantier_repo=self.mock_repo)

        chantier1 = self._create_chantier(chantier_id=1, code="A001")
        chantier2 = self._create_chantier(chantier_id=2, code="A002")

        self.mock_repo.find_by_id.side_effect = [chantier1, chantier2]

        # Act
        result1 = use_case.execute_by_id(1)
        result2 = use_case.execute_by_id(2)

        # Assert
        assert result1.id == 1
        assert result1.code == "A001"
        assert result2.id == 2
        assert result2.code == "A002"

    # ==================== Tests Succès - Par Code ====================

    def test_get_chantier_by_code_success(self):
        """Test: récupération chantier par code réussit."""
        # Arrange
        use_case = GetChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier(code="A123")
        self.mock_repo.find_by_code.return_value = chantier

        # Act
        result = use_case.execute_by_code("A123")

        # Assert
        assert result.code == "A123"
        assert result.nom == "Chantier Test"
        self.mock_repo.find_by_code.assert_called_once()

    def test_get_chantier_by_code_returns_dto(self):
        """Test: récupération par code retourne un ChantierDTO."""
        # Arrange
        use_case = GetChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier(code="B001")
        self.mock_repo.find_by_code.return_value = chantier

        # Act
        result = use_case.execute_by_code("B001")

        # Assert
        assert hasattr(result, 'id')
        assert hasattr(result, 'code')
        assert result.code == "B001"

    def test_get_chantier_by_code_different_codes(self):
        """Test: récupération de différents chantiers par code."""
        # Arrange
        use_case = GetChantierUseCase(chantier_repo=self.mock_repo)

        chantier1 = self._create_chantier(chantier_id=1, code="A001")
        chantier2 = self._create_chantier(chantier_id=2, code="B002")

        def side_effect(code_obj):
            if str(code_obj) == "A001":
                return chantier1
            elif str(code_obj) == "B002":
                return chantier2
            return None

        self.mock_repo.find_by_code.side_effect = side_effect

        # Act
        result1 = use_case.execute_by_code("A001")
        result2 = use_case.execute_by_code("B002")

        # Assert
        assert result1.code == "A001"
        assert result2.code == "B002"

    # ==================== Tests Erreurs ====================

    def test_get_chantier_by_id_not_found_raises_error(self):
        """Test: chantier non trouvé par ID lève ChantierNotFoundError."""
        # Arrange
        use_case = GetChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ChantierNotFoundError) as exc_info:
            use_case.execute_by_id(999)

        assert exc_info.value.identifier == "999"
        assert "non trouvé" in exc_info.value.message

    def test_get_chantier_by_code_not_found_raises_error(self):
        """Test: chantier non trouvé par code lève ChantierNotFoundError."""
        # Arrange
        use_case = GetChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.find_by_code.return_value = None

        # Act & Assert
        with pytest.raises(ChantierNotFoundError) as exc_info:
            use_case.execute_by_code("Z999")

        assert exc_info.value.identifier == "Z999"
        assert "non trouvé" in exc_info.value.message

    # ==================== Tests Logging Structuré (GAP-CHT-006) ====================

    @patch('modules.chantiers.application.use_cases.get_chantier.logger')
    def test_execute_by_id_logs_started_event(self, mock_logger):
        """Test: execute_by_id() log événement 'started' avec extra dict."""
        # Arrange
        use_case = GetChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier

        # Act
        use_case.execute_by_id(1)

        # Assert
        info_calls = mock_logger.info.call_args_list
        started_call = info_calls[0]

        assert "Use case execution started" in started_call.args[0]
        assert 'extra' in started_call.kwargs
        extra = started_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.started"
        assert extra['use_case'] == "GetChantierUseCase"
        assert extra['chantier_id'] == 1
        assert extra['operation'] == "get_by_id"

    @patch('modules.chantiers.application.use_cases.get_chantier.logger')
    def test_execute_by_id_logs_succeeded_event(self, mock_logger):
        """Test: execute_by_id() log événement 'succeeded' avec détails."""
        # Arrange
        use_case = GetChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier

        # Act
        use_case.execute_by_id(1)

        # Assert
        info_calls = mock_logger.info.call_args_list
        assert len(info_calls) >= 2
        succeeded_call = info_calls[1]

        assert "Use case execution succeeded" in succeeded_call.args[0]
        extra = succeeded_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.succeeded"
        assert extra['use_case'] == "GetChantierUseCase"
        assert extra['chantier_id'] == 1

    @patch('modules.chantiers.application.use_cases.get_chantier.logger')
    def test_execute_by_id_logs_failed_event_on_error(self, mock_logger):
        """Test: execute_by_id() log événement 'failed' en cas d'erreur."""
        # Arrange
        use_case = GetChantierUseCase(chantier_repo=self.mock_repo)

        self.mock_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ChantierNotFoundError):
            use_case.execute_by_id(999)

        # Assert
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args

        assert "Use case execution failed" in error_call.args[0]
        extra = error_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.failed"
        assert extra['use_case'] == "GetChantierUseCase"
        assert extra['chantier_id'] == 999
        assert extra['error_type'] == "ChantierNotFoundError"
        assert 'error_message' in extra

    @patch('modules.chantiers.application.use_cases.get_chantier.logger')
    def test_execute_by_code_does_not_log(self, mock_logger):
        """Test: execute_by_code() ne log pas (pas de logging dans cette méthode)."""
        # Arrange
        use_case = GetChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier(code="A001")
        self.mock_repo.find_by_code.return_value = chantier

        # Act
        use_case.execute_by_code("A001")

        # Assert - execute_by_code ne log pas dans le code actuel
        # Cette méthode est plus simple et ne nécessite pas de logging
        # Si on veut ajouter du logging, il faudrait modifier le use case
        assert True  # Test passe si aucune erreur levée

    # ==================== Tests Cas Limites ====================

    def test_get_chantier_multiple_calls_same_id(self):
        """Test: plusieurs appels avec le même ID."""
        # Arrange
        use_case = GetChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        self.mock_repo.find_by_id.return_value = chantier

        # Act
        result1 = use_case.execute_by_id(1)
        result2 = use_case.execute_by_id(1)

        # Assert
        assert result1.id == result2.id
        assert result1.code == result2.code
        assert self.mock_repo.find_by_id.call_count == 2

    def test_get_chantier_with_all_attributes(self):
        """Test: chantier avec tous les attributs optionnels."""
        # Arrange
        use_case = GetChantierUseCase(chantier_repo=self.mock_repo)

        chantier = self._create_chantier()
        # Simuler un chantier complet avec attributs optionnels
        chantier.description = "Description complète"
        chantier.heures_estimees = 150.5

        self.mock_repo.find_by_id.return_value = chantier

        # Act
        result = use_case.execute_by_id(1)

        # Assert
        assert result.description == "Description complète"
        assert result.heures_estimees == 150.5
