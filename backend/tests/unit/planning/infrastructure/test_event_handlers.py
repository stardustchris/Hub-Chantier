"""Tests unitaires pour GAP-CHT-002 - Event handlers Planning.

Ce fichier teste :
- handle_chantier_statut_changed_for_planning : Blocage affectations futures quand chantier fermé
- register_planning_event_handlers : Enregistrement des handlers
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta
from dataclasses import dataclass

from modules.planning.domain.entities.affectation import Affectation
from modules.planning.infrastructure.event_handlers import (
    handle_chantier_statut_changed_for_planning,
    register_planning_event_handlers,
)


# =============================================================================
# Fixtures
# =============================================================================

@dataclass
class MockEvent:
    """Mock d'un événement ChantierStatutChangedEvent."""
    data: dict


@pytest.fixture
def mock_session():
    """Fixture: mock de session SQLAlchemy."""
    session = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    return session


@pytest.fixture
def mock_affectation_repo():
    """Fixture: mock du repository d'affectations."""
    return Mock()


def create_affectation(affectation_id: int, chantier_id: int, date_affectation: date, utilisateur_id: int = 1) -> Affectation:
    """Helper: crée une affectation de test."""
    return Affectation(
        id=affectation_id,
        utilisateur_id=utilisateur_id,
        chantier_id=chantier_id,
        date=date_affectation,
        created_by=1,
    )


# =============================================================================
# Tests GAP-CHT-002: Blocage affectations futures quand chantier fermé
# =============================================================================

class TestHandleChantierStatutChangedFerme:
    """Tests: Suppression des affectations futures quand chantier fermé."""

    @patch('modules.planning.infrastructure.event_handlers.SessionLocal')
    @patch('modules.planning.infrastructure.persistence.SQLAlchemyAffectationRepository')
    def test_should_delete_future_affectations_when_chantier_ferme(
        self,
        mock_repo_class,
        mock_session_local,
        mock_session,
        mock_affectation_repo,
    ):
        """Test: suppression des affectations futures quand statut = ferme."""
        # Arrange
        mock_session_local.return_value = mock_session
        mock_repo_class.return_value = mock_affectation_repo

        aujourdhui = date.today()
        date_future = aujourdhui + timedelta(days=1)

        # 2 affectations futures
        affectations_futures = [
            create_affectation(1, 10, date_future),
            create_affectation(2, 10, date_future + timedelta(days=1)),
        ]
        mock_affectation_repo.find_by_chantier.return_value = affectations_futures
        mock_affectation_repo.delete.return_value = True

        event = MockEvent(data={
            'chantier_id': 10,
            'nouveau_statut': 'ferme',
        })

        # Act
        handle_chantier_statut_changed_for_planning(event)

        # Assert
        # Vérifier appel find_by_chantier avec date range
        mock_affectation_repo.find_by_chantier.assert_called_once()
        call_kwargs = mock_affectation_repo.find_by_chantier.call_args[1]
        assert call_kwargs['chantier_id'] == 10
        assert call_kwargs['date_debut'] == aujourdhui

        # Vérifier suppression des 2 affectations
        assert mock_affectation_repo.delete.call_count == 2
        mock_affectation_repo.delete.assert_any_call(1)
        mock_affectation_repo.delete.assert_any_call(2)

        # Vérifier commit
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    @patch('modules.planning.infrastructure.event_handlers.SessionLocal')
    @patch('modules.planning.infrastructure.persistence.SQLAlchemyAffectationRepository')
    def test_should_handle_no_future_affectations_gracefully(
        self,
        mock_repo_class,
        mock_session_local,
        mock_session,
        mock_affectation_repo,
    ):
        """Test: pas d'erreur si aucune affectation future."""
        # Arrange
        mock_session_local.return_value = mock_session
        mock_repo_class.return_value = mock_affectation_repo

        # Aucune affectation future
        mock_affectation_repo.find_by_chantier.return_value = []

        event = MockEvent(data={
            'chantier_id': 10,
            'nouveau_statut': 'ferme',
        })

        # Act - should not raise
        handle_chantier_statut_changed_for_planning(event)

        # Assert
        # Pas de suppression appelée
        mock_affectation_repo.delete.assert_not_called()
        # Mais commit quand même
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()


class TestHandleChantierStatutChangedAutreStatut:
    """Tests: Skip si statut != ferme."""

    @patch('modules.planning.infrastructure.event_handlers.SessionLocal')
    def test_should_skip_when_statut_not_ferme(
        self,
        mock_session_local,
        mock_session,
    ):
        """Test: skip si nouveau_statut != 'ferme'."""
        # Arrange
        mock_session_local.return_value = mock_session

        event = MockEvent(data={
            'chantier_id': 10,
            'nouveau_statut': 'en_cours',  # Pas fermé
        })

        # Act
        handle_chantier_statut_changed_for_planning(event)

        # Assert - Pas de session créée ni opération DB
        mock_session_local.assert_not_called()

    @patch('modules.planning.infrastructure.event_handlers.SessionLocal')
    def test_should_skip_when_statut_ouvert(
        self,
        mock_session_local,
    ):
        """Test: skip si statut = ouvert."""
        # Arrange
        event = MockEvent(data={
            'chantier_id': 10,
            'nouveau_statut': 'ouvert',
        })

        # Act
        handle_chantier_statut_changed_for_planning(event)

        # Assert
        mock_session_local.assert_not_called()

    @patch('modules.planning.infrastructure.event_handlers.SessionLocal')
    def test_should_skip_when_statut_receptionne(
        self,
        mock_session_local,
    ):
        """Test: skip si statut = receptionne."""
        # Arrange
        event = MockEvent(data={
            'chantier_id': 10,
            'nouveau_statut': 'receptionne',
        })

        # Act
        handle_chantier_statut_changed_for_planning(event)

        # Assert
        mock_session_local.assert_not_called()


class TestHandleChantierStatutChangedEdgeCases:
    """Tests: Cas limites et gestion d'erreurs."""

    @patch('modules.planning.infrastructure.event_handlers.SessionLocal')
    @patch('modules.planning.infrastructure.event_handlers.logger')
    def test_should_warn_when_no_chantier_id(
        self,
        mock_logger,
        mock_session_local,
    ):
        """Test: warning si chantier_id manquant."""
        # Arrange
        event = MockEvent(data={
            # chantier_id manquant
            'nouveau_statut': 'ferme',
        })

        # Act
        handle_chantier_statut_changed_for_planning(event)

        # Assert - Warning loggé
        mock_logger.warning.assert_called_once()
        warning_msg = mock_logger.warning.call_args[0][0]
        assert "sans chantier_id" in warning_msg

        # Pas d'opération DB
        mock_session_local.assert_not_called()

    @patch('modules.planning.infrastructure.event_handlers.SessionLocal')
    @patch('modules.planning.infrastructure.persistence.SQLAlchemyAffectationRepository')
    @patch('modules.planning.infrastructure.event_handlers.logger')
    def test_should_rollback_on_error(
        self,
        mock_logger,
        mock_repo_class,
        mock_session_local,
        mock_session,
        mock_affectation_repo,
    ):
        """Test: rollback en cas d'erreur."""
        # Arrange
        mock_session_local.return_value = mock_session
        mock_repo_class.return_value = mock_affectation_repo

        # Simuler une erreur lors de find_by_chantier
        mock_affectation_repo.find_by_chantier.side_effect = Exception("DB Error")

        event = MockEvent(data={
            'chantier_id': 10,
            'nouveau_statut': 'ferme',
        })

        # Act - should not raise
        handle_chantier_statut_changed_for_planning(event)

        # Assert
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        mock_logger.error.assert_called_once()

    @patch('modules.planning.infrastructure.event_handlers.SessionLocal')
    @patch('modules.planning.infrastructure.persistence.SQLAlchemyAffectationRepository')
    def test_should_handle_event_with_getattr_fallback(
        self,
        mock_repo_class,
        mock_session_local,
        mock_session,
        mock_affectation_repo,
    ):
        """Test: extraction défensive avec getattr si event sans data dict."""
        # Arrange
        mock_session_local.return_value = mock_session
        mock_repo_class.return_value = mock_affectation_repo

        # Event avec attributs directs (pas de data dict)
        @dataclass
        class DirectEvent:
            chantier_id: int
            nouveau_statut: str

        event = DirectEvent(chantier_id=10, nouveau_statut='ferme')
        mock_affectation_repo.find_by_chantier.return_value = []

        # Act - should not raise
        handle_chantier_statut_changed_for_planning(event)

        # Assert - L'extraction défensive fonctionne
        mock_affectation_repo.find_by_chantier.assert_called_once()
        call_kwargs = mock_affectation_repo.find_by_chantier.call_args[1]
        assert call_kwargs['chantier_id'] == 10


class TestHandleChantierStatutChangedLogging:
    """Tests: Logging des opérations."""

    @patch('modules.planning.infrastructure.event_handlers.SessionLocal')
    @patch('modules.planning.infrastructure.persistence.SQLAlchemyAffectationRepository')
    @patch('modules.planning.infrastructure.event_handlers.logger')
    def test_should_log_info_when_deleting_affectations(
        self,
        mock_logger,
        mock_repo_class,
        mock_session_local,
        mock_session,
        mock_affectation_repo,
    ):
        """Test: log info quand affectations supprimées."""
        # Arrange
        mock_session_local.return_value = mock_session
        mock_repo_class.return_value = mock_affectation_repo

        aujourdhui = date.today()
        affectations = [create_affectation(1, 10, aujourdhui + timedelta(days=1))]
        mock_affectation_repo.find_by_chantier.return_value = affectations
        mock_affectation_repo.delete.return_value = True

        event = MockEvent(data={
            'chantier_id': 10,
            'nouveau_statut': 'ferme',
        })

        # Act
        handle_chantier_statut_changed_for_planning(event)

        # Assert - Log info avec compteur
        info_calls = [call for call in mock_logger.info.call_args_list]
        assert len(info_calls) >= 2  # Au moins 2 logs info

        # Vérifier qu'un log contient le nombre d'affectations supprimées
        found_count_log = False
        for call in info_calls:
            if "affectation(s) future(s) supprimée(s)" in str(call):
                found_count_log = True
                break
        assert found_count_log

    @patch('modules.planning.infrastructure.event_handlers.SessionLocal')
    @patch('modules.planning.infrastructure.persistence.SQLAlchemyAffectationRepository')
    @patch('modules.planning.infrastructure.event_handlers.logger')
    def test_should_log_debug_when_no_affectations(
        self,
        mock_logger,
        mock_repo_class,
        mock_session_local,
        mock_session,
        mock_affectation_repo,
    ):
        """Test: log debug quand aucune affectation à supprimer."""
        # Arrange
        mock_session_local.return_value = mock_session
        mock_repo_class.return_value = mock_affectation_repo
        mock_affectation_repo.find_by_chantier.return_value = []

        event = MockEvent(data={
            'chantier_id': 10,
            'nouveau_statut': 'ferme',
        })

        # Act
        handle_chantier_statut_changed_for_planning(event)

        # Assert - Log debug
        debug_calls = [call for call in mock_logger.debug.call_args_list]
        found_debug = any("Aucune affectation future" in str(call) for call in debug_calls)
        assert found_debug


# =============================================================================
# Tests: register_planning_event_handlers
# =============================================================================

class TestRegisterPlanningEventHandlers:
    """Tests: Enregistrement des handlers."""

    @patch('modules.planning.infrastructure.event_handlers.logger')
    def test_should_log_registration(self, mock_logger):
        """Test: log lors de l'enregistrement."""
        # Act
        register_planning_event_handlers()

        # Assert - Log info
        mock_logger.info.assert_called_once()
        log_msg = mock_logger.info.call_args[0][0]
        assert "Planning event handlers registered" in log_msg
        assert "chantier.statut_changed" in log_msg

    def test_should_not_raise_on_call(self):
        """Test: pas d'erreur lors de l'appel."""
        # Act - should not raise
        register_planning_event_handlers()

        # Assert - Function completes successfully
        assert True
