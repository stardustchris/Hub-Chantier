"""Tests pour le scheduler de nettoyage des webhook deliveries (GDPR)."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from shared.infrastructure.webhooks.cleanup_scheduler import (
    cleanup_old_deliveries_job,
    start_cleanup_scheduler,
    stop_cleanup_scheduler,
    run_cleanup_now,
    RETENTION_DAYS,
)
from shared.infrastructure.webhooks.models import WebhookDeliveryModel


class TestCleanupScheduler:
    """Tests pour le scheduler de nettoyage GDPR."""

    def test_cleanup_job_deletes_old_deliveries(self):
        """Doit supprimer les deliveries plus anciennes que RETENTION_DAYS jours."""
        # Arrange: Mock de la session et query
        mock_db = Mock(spec=Session)
        mock_query = Mock()

        # Simuler delete qui retourne 1 (1 delivery supprimée)
        mock_query.filter.return_value.delete.return_value = 1
        mock_db.query.return_value = mock_query

        # Act: Exécuter le job avec mock
        with patch('shared.infrastructure.webhooks.cleanup_scheduler.SessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_db
            cleanup_old_deliveries_job()

        # Assert: Delete doit avoir été appelé
        mock_db.query.assert_called_once_with(WebhookDeliveryModel)
        assert mock_query.filter.called
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    def test_cleanup_job_preserves_recent_deliveries(self):
        """Doit conserver toutes les deliveries récentes (< RETENTION_DAYS)."""
        # Arrange: Mock retournant 0 deliveries supprimées (toutes récentes)
        mock_db = Mock(spec=Session)
        mock_query = Mock()

        # Simuler delete qui retourne 0 (aucune delivery à supprimer)
        mock_query.filter.return_value.delete.return_value = 0
        mock_db.query.return_value = mock_query

        # Act: Exécuter le nettoyage
        with patch('shared.infrastructure.webhooks.cleanup_scheduler.SessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_db
            cleanup_old_deliveries_job()

        # Assert: Commit doit être appelé même si rien n'est supprimé
        mock_db.query.assert_called_once_with(WebhookDeliveryModel)
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    def test_cleanup_job_handles_empty_database(self):
        """Doit gérer le cas où la base est vide sans erreur."""
        # Arrange: Mock base vide (delete retourne 0)
        mock_db = Mock(spec=Session)
        mock_query = Mock()

        mock_query.filter.return_value.delete.return_value = 0
        mock_db.query.return_value = mock_query

        # Act: Exécuter le nettoyage (ne doit pas lever d'exception)
        with patch('shared.infrastructure.webhooks.cleanup_scheduler.SessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_db
            cleanup_old_deliveries_job()

        # Assert: Pas d'erreur, commit appelé normalement
        mock_db.query.assert_called_once_with(WebhookDeliveryModel)
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    def test_cleanup_job_rollback_on_error(self):
        """Doit rollback la transaction en cas d'erreur."""
        # Arrange: Mock SessionLocal pour simuler une erreur
        mock_session_local = Mock()
        mock_db = Mock(spec=Session)

        # Simuler une erreur lors du delete
        mock_query = Mock()
        mock_query.filter.return_value.delete.side_effect = Exception("Database error")
        mock_db.query.return_value = mock_query

        mock_session_local.return_value = mock_db

        # Act: Exécuter le nettoyage (doit gérer l'erreur)
        with patch('shared.infrastructure.webhooks.cleanup_scheduler.SessionLocal', mock_session_local):
            # Ne doit pas lever d'exception (erreur loggée)
            cleanup_old_deliveries_job()

        # Assert: Rollback doit avoir été appelé
        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()

    def test_scheduler_starts_and_configures_job(self):
        """Doit démarrer le scheduler avec la configuration correcte."""
        # Arrange: Arrêter le scheduler global s'il existe
        stop_cleanup_scheduler()

        # Act: Démarrer le scheduler
        scheduler = start_cleanup_scheduler()

        # Assert: Scheduler doit être démarré
        assert scheduler is not None
        assert scheduler.running is True

        # Vérifier que le job est enregistré
        jobs = scheduler.get_jobs()
        assert len(jobs) >= 1

        cleanup_job = next(
            (job for job in jobs if job.id == 'webhook_deliveries_cleanup'),
            None
        )
        assert cleanup_job is not None
        assert cleanup_job.name == 'Cleanup Webhook Deliveries (GDPR)'
        assert cleanup_job.max_instances == 1  # Pas de parallélisme

        # Cleanup: Arrêter le scheduler
        stop_cleanup_scheduler()

    def test_scheduler_prevents_duplicate_jobs(self):
        """Doit empêcher le démarrage de plusieurs instances du scheduler."""
        # Arrange: Arrêter le scheduler global
        stop_cleanup_scheduler()

        # Act: Démarrer le scheduler deux fois
        scheduler1 = start_cleanup_scheduler()
        scheduler2 = start_cleanup_scheduler()  # 2ème appel

        # Assert: Doit retourner la même instance
        assert scheduler1 is scheduler2

        # Vérifier qu'il n'y a qu'un seul job
        jobs = scheduler1.get_jobs()
        cleanup_jobs = [j for j in jobs if j.id == 'webhook_deliveries_cleanup']
        assert len(cleanup_jobs) == 1

        # Cleanup
        stop_cleanup_scheduler()

    def test_manual_cleanup_execution(self):
        """Doit permettre l'exécution manuelle du nettoyage."""
        # Arrange: Mock de la session
        mock_db = Mock(spec=Session)
        mock_query = Mock()

        # Simuler delete qui retourne 1 (1 delivery supprimée)
        mock_query.filter.return_value.delete.return_value = 1
        mock_db.query.return_value = mock_query

        # Act: Exécuter manuellement
        with patch('shared.infrastructure.webhooks.cleanup_scheduler.SessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_db
            run_cleanup_now()

        # Assert: La fonction cleanup_old_deliveries_job doit avoir été exécutée
        mock_db.query.assert_called_with(WebhookDeliveryModel)
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    def test_scheduler_stop_gracefully(self):
        """Doit arrêter le scheduler proprement."""
        # Arrange: Démarrer le scheduler
        stop_cleanup_scheduler()  # Reset
        scheduler = start_cleanup_scheduler()
        assert scheduler.running is True

        # Act: Arrêter le scheduler
        stop_cleanup_scheduler()

        # Assert: Scheduler doit être arrêté
        assert scheduler.running is False

        # Vérifier qu'on peut le redémarrer après
        new_scheduler = start_cleanup_scheduler()
        assert new_scheduler.running is True

        # Cleanup
        stop_cleanup_scheduler()
