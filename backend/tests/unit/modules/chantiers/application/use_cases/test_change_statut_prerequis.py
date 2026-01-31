"""Tests unitaires pour ChangeStatutUseCase avec prérequis et audit.

Gap: GAP-CHT-001 - Validation prérequis réception
Gap: GAP-CHT-005 - Audit logging changement statut
Gap: GAP-CHT-006 - Logging structuré
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call

from modules.chantiers.domain.entities import Chantier
from modules.chantiers.domain.value_objects import CodeChantier, StatutChantier
from modules.chantiers.domain.repositories import ChantierRepository
from modules.chantiers.application.use_cases.change_statut import (
    ChangeStatutUseCase,
    PrerequisReceptionNonRemplisError,
)
from modules.chantiers.application.dtos import ChangeStatutDTO


class TestChangeStatutUseCasePrerequisEtAudit:
    """Tests pour changement statut avec prérequis et audit."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_chantier_repo = Mock(spec=ChantierRepository)
        self.mock_formulaire_repo = Mock()
        self.mock_signalement_repo = Mock()
        self.mock_pointage_repo = Mock()
        self.mock_audit_service = Mock()

    def _create_chantier(
        self, chantier_id: int = 1, statut: str = "en_cours"
    ) -> Chantier:
        """Crée un chantier de test."""
        return Chantier(
            id=chantier_id,
            code=CodeChantier("A001"),
            nom="Chantier Test",
            adresse="Adresse Test",
            statut=StatutChantier.from_string(statut),
        )

    def _setup_prerequis_valides(self):
        """Configure les mocks pour avoir tous les prérequis valides."""
        # Formulaires OK (>= 3)
        self.mock_formulaire_repo.count_by_chantier.return_value = 5

        # Signalements OK (pas de critiques ouverts)
        mock_signalement = MagicMock()
        mock_signalement.statut.value = "resolu"
        mock_signalement.priorite.value = "critique"
        self.mock_signalement_repo.find_by_chantier.return_value = [mock_signalement]

        # Pointages OK (tous validés)
        mock_pointage = MagicMock()
        mock_pointage.statut.value = "valide"
        self.mock_pointage_repo.search.return_value = ([mock_pointage], 1)

    def _setup_prerequis_formulaires_manquants(self):
        """Configure les mocks pour avoir formulaires manquants."""
        self.mock_formulaire_repo.count_by_chantier.return_value = 1  # Insuffisant

    def _setup_prerequis_signalements_critiques(self):
        """Configure les mocks pour avoir signalements critiques ouverts."""
        mock_signalement = MagicMock()
        mock_signalement.statut.value = "ouvert"
        mock_signalement.priorite.value = "critique"
        self.mock_signalement_repo.find_by_chantier.return_value = [mock_signalement]

    def _setup_prerequis_pointages_non_valides(self):
        """Configure les mocks pour avoir pointages non validés."""
        mock_pointage = MagicMock()
        mock_pointage.statut.value = "brouillon"
        self.mock_pointage_repo.search.return_value = ([mock_pointage], 1)

    # ==================== Tests GAP-CHT-001: Prérequis Réception ====================

    def test_receptionner_avec_prerequis_valides(self):
        """Test: réception autorisée si tous les prérequis sont valides."""
        # Arrange
        self._setup_prerequis_valides()
        use_case = ChangeStatutUseCase(
            chantier_repo=self.mock_chantier_repo,
            formulaire_repo=self.mock_formulaire_repo,
            signalement_repo=self.mock_signalement_repo,
            pointage_repo=self.mock_pointage_repo,
        )

        chantier = self._create_chantier(statut="en_cours")
        self.mock_chantier_repo.find_by_id.return_value = chantier
        self.mock_chantier_repo.save.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="receptionne")

        # Act
        result = use_case.execute(1, dto)

        # Assert
        assert result.statut == "receptionne"
        self.mock_formulaire_repo.count_by_chantier.assert_called_once_with(1)
        self.mock_signalement_repo.find_by_chantier.assert_called_once_with(1)
        self.mock_pointage_repo.search.assert_called_once_with(chantier_id=1)

    def test_receptionner_sans_prerequis_formulaires_raises_error(self):
        """Test: réception refusée si formulaires manquants."""
        # Arrange
        self._setup_prerequis_formulaires_manquants()
        use_case = ChangeStatutUseCase(
            chantier_repo=self.mock_chantier_repo,
            formulaire_repo=self.mock_formulaire_repo,
        )

        chantier = self._create_chantier(statut="en_cours")
        self.mock_chantier_repo.find_by_id.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="receptionne")

        # Act & Assert
        with pytest.raises(PrerequisReceptionNonRemplisError) as exc_info:
            use_case.execute(1, dto)

        assert exc_info.value.chantier_id == 1
        assert len(exc_info.value.prerequis_manquants) > 0
        assert "Formulaires manquants" in exc_info.value.prerequis_manquants[0]

    def test_receptionner_sans_prerequis_signalements_raises_error(self):
        """Test: réception refusée si signalements critiques ouverts."""
        # Arrange
        self._setup_prerequis_signalements_critiques()
        use_case = ChangeStatutUseCase(
            chantier_repo=self.mock_chantier_repo,
            signalement_repo=self.mock_signalement_repo,
        )

        chantier = self._create_chantier(statut="en_cours")
        self.mock_chantier_repo.find_by_id.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="receptionne")

        # Act & Assert
        with pytest.raises(PrerequisReceptionNonRemplisError) as exc_info:
            use_case.execute(1, dto)

        assert exc_info.value.chantier_id == 1
        assert "signalement(s) critique(s)" in exc_info.value.prerequis_manquants[0]

    def test_receptionner_sans_prerequis_pointages_raises_error(self):
        """Test: réception refusée si pointages non validés."""
        # Arrange
        self._setup_prerequis_pointages_non_valides()
        use_case = ChangeStatutUseCase(
            chantier_repo=self.mock_chantier_repo,
            pointage_repo=self.mock_pointage_repo,
        )

        chantier = self._create_chantier(statut="en_cours")
        self.mock_chantier_repo.find_by_id.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="receptionne")

        # Act & Assert
        with pytest.raises(PrerequisReceptionNonRemplisError) as exc_info:
            use_case.execute(1, dto)

        assert exc_info.value.chantier_id == 1
        assert "pointage(s) non validé(s)" in exc_info.value.prerequis_manquants[0]

    def test_receptionner_error_contient_details(self):
        """Test: erreur prérequis contient détails pour debugging."""
        # Arrange
        self._setup_prerequis_formulaires_manquants()
        self._setup_prerequis_signalements_critiques()
        use_case = ChangeStatutUseCase(
            chantier_repo=self.mock_chantier_repo,
            formulaire_repo=self.mock_formulaire_repo,
            signalement_repo=self.mock_signalement_repo,
        )

        chantier = self._create_chantier(statut="en_cours")
        self.mock_chantier_repo.find_by_id.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="receptionne")

        # Act & Assert
        with pytest.raises(PrerequisReceptionNonRemplisError) as exc_info:
            use_case.execute(1, dto)

        # Vérifier que details contient comptages
        assert 'formulaires_count' in exc_info.value.details
        assert 'signalements_critiques' in exc_info.value.details
        assert exc_info.value.details['formulaires_count'] == 1

    def test_transition_non_receptionne_sans_verification_prerequis(self):
        """Test: transitions autres que réception ne vérifient PAS les prérequis."""
        # Arrange - Aucun repo fourni
        use_case = ChangeStatutUseCase(
            chantier_repo=self.mock_chantier_repo,
        )

        chantier = self._create_chantier(statut="ouvert")
        self.mock_chantier_repo.find_by_id.return_value = chantier
        self.mock_chantier_repo.save.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="en_cours")

        # Act
        result = use_case.execute(1, dto)

        # Assert - Transition réussie sans vérification prérequis
        assert result.statut == "en_cours"

    def test_receptionner_shortcut_avec_prerequis_valides(self):
        """Test: méthode receptionner() avec prérequis valides."""
        # Arrange
        self._setup_prerequis_valides()
        use_case = ChangeStatutUseCase(
            chantier_repo=self.mock_chantier_repo,
            formulaire_repo=self.mock_formulaire_repo,
            signalement_repo=self.mock_signalement_repo,
            pointage_repo=self.mock_pointage_repo,
        )

        chantier = self._create_chantier(statut="en_cours")
        self.mock_chantier_repo.find_by_id.return_value = chantier
        self.mock_chantier_repo.save.return_value = chantier

        # Act
        result = use_case.receptionner(1)

        # Assert
        assert result.statut == "receptionne"

    # ==================== Tests GAP-CHT-005: Audit Logging ====================

    def test_change_statut_appelle_audit_service(self):
        """Test: changement statut appelle audit_service.log_chantier_status_changed."""
        # Arrange
        use_case = ChangeStatutUseCase(
            chantier_repo=self.mock_chantier_repo,
            audit_service=self.mock_audit_service,
        )

        chantier = self._create_chantier(statut="ouvert")
        self.mock_chantier_repo.find_by_id.return_value = chantier
        self.mock_chantier_repo.save.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="en_cours")

        # Act
        use_case.execute(1, dto)

        # Assert
        self.mock_audit_service.log_chantier_status_changed.assert_called_once()
        call_args = self.mock_audit_service.log_chantier_status_changed.call_args
        assert call_args.kwargs['chantier_id'] == 1
        assert call_args.kwargs['old_status'] == "ouvert"
        assert call_args.kwargs['new_status'] == "en_cours"

    def test_change_statut_sans_audit_service_fonctionne(self):
        """Test: changement statut fonctionne sans audit_service (optionnel)."""
        # Arrange - Aucun audit_service
        use_case = ChangeStatutUseCase(
            chantier_repo=self.mock_chantier_repo,
        )

        chantier = self._create_chantier(statut="ouvert")
        self.mock_chantier_repo.find_by_id.return_value = chantier
        self.mock_chantier_repo.save.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="en_cours")

        # Act - Pas d'erreur levée
        result = use_case.execute(1, dto)

        # Assert
        assert result.statut == "en_cours"

    def test_receptionner_avec_audit_et_prerequis(self):
        """Test: réception avec prérequis valides ET audit logging."""
        # Arrange
        self._setup_prerequis_valides()
        use_case = ChangeStatutUseCase(
            chantier_repo=self.mock_chantier_repo,
            formulaire_repo=self.mock_formulaire_repo,
            signalement_repo=self.mock_signalement_repo,
            pointage_repo=self.mock_pointage_repo,
            audit_service=self.mock_audit_service,
        )

        chantier = self._create_chantier(statut="en_cours")
        self.mock_chantier_repo.find_by_id.return_value = chantier
        self.mock_chantier_repo.save.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="receptionne")

        # Act
        result = use_case.execute(1, dto)

        # Assert - Transition réussie
        assert result.statut == "receptionne"

        # Assert - Audit appelé
        self.mock_audit_service.log_chantier_status_changed.assert_called_once()
        call_args = self.mock_audit_service.log_chantier_status_changed.call_args
        assert call_args.kwargs['old_status'] == "en_cours"
        assert call_args.kwargs['new_status'] == "receptionne"

    # ==================== Tests GAP-CHT-006: Logging Structuré ====================

    @patch('modules.chantiers.application.use_cases.change_statut.logger')
    def test_execute_logs_started_event(self, mock_logger):
        """Test: execute() log événement 'started' avec données structurées."""
        # Arrange
        use_case = ChangeStatutUseCase(
            chantier_repo=self.mock_chantier_repo,
        )

        chantier = self._create_chantier(statut="ouvert")
        self.mock_chantier_repo.find_by_id.return_value = chantier
        self.mock_chantier_repo.save.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="en_cours")

        # Act
        use_case.execute(1, dto)

        # Assert - Vérifier appel logger.info avec extra
        info_calls = mock_logger.info.call_args_list
        started_call = info_calls[0]

        assert "Use case execution started" in started_call.args[0]
        assert 'extra' in started_call.kwargs
        extra = started_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.started"
        assert extra['use_case'] == "ChangeStatutUseCase"
        assert extra['chantier_id'] == 1
        assert extra['nouveau_statut'] == "en_cours"

    @patch('modules.chantiers.application.use_cases.change_statut.logger')
    def test_execute_logs_succeeded_event(self, mock_logger):
        """Test: execute() log événement 'succeeded' avec détails."""
        # Arrange
        use_case = ChangeStatutUseCase(
            chantier_repo=self.mock_chantier_repo,
        )

        chantier = self._create_chantier(statut="ouvert")
        self.mock_chantier_repo.find_by_id.return_value = chantier
        self.mock_chantier_repo.save.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="en_cours")

        # Act
        use_case.execute(1, dto)

        # Assert - Vérifier appel logger.info avec extra (2ème appel)
        info_calls = mock_logger.info.call_args_list
        assert len(info_calls) >= 2
        succeeded_call = info_calls[1]

        assert "Use case execution succeeded" in succeeded_call.args[0]
        extra = succeeded_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.succeeded"
        assert extra['ancien_statut'] == "ouvert"
        assert extra['nouveau_statut'] == "en_cours"

    @patch('modules.chantiers.application.use_cases.change_statut.logger')
    def test_execute_logs_failed_event_on_error(self, mock_logger):
        """Test: execute() log événement 'failed' en cas d'erreur."""
        # Arrange
        use_case = ChangeStatutUseCase(
            chantier_repo=self.mock_chantier_repo,
        )

        # Provoquer une erreur (chantier non trouvé)
        self.mock_chantier_repo.find_by_id.return_value = None

        dto = ChangeStatutDTO(nouveau_statut="en_cours")

        # Act & Assert
        with pytest.raises(Exception):
            use_case.execute(999, dto)

        # Assert - Vérifier appel logger.error
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args

        assert "Use case execution failed" in error_call.args[0]
        extra = error_call.kwargs['extra']
        assert extra['event'] == "chantier.use_case.failed"
        assert extra['use_case'] == "ChangeStatutUseCase"
        assert extra['chantier_id'] == 999
        assert 'error_type' in extra
        assert 'error_message' in extra

    @patch('modules.chantiers.application.use_cases.change_statut.logger')
    def test_execute_logs_prerequis_failure(self, mock_logger):
        """Test: échec prérequis log événement 'failed' avec type d'erreur."""
        # Arrange
        self._setup_prerequis_formulaires_manquants()
        use_case = ChangeStatutUseCase(
            chantier_repo=self.mock_chantier_repo,
            formulaire_repo=self.mock_formulaire_repo,
        )

        chantier = self._create_chantier(statut="en_cours")
        self.mock_chantier_repo.find_by_id.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="receptionne")

        # Act & Assert
        with pytest.raises(PrerequisReceptionNonRemplisError):
            use_case.execute(1, dto)

        # Assert - Vérifier log erreur
        mock_logger.error.assert_called_once()
        extra = mock_logger.error.call_args.kwargs['extra']
        assert extra['error_type'] == "PrerequisReceptionNonRemplisError"
