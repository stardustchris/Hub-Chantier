"""Tests unitaires pour SchedulerService."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from shared.infrastructure.scheduler.scheduler_service import SchedulerService, get_scheduler


class TestSchedulerService:
    """Tests pour SchedulerService."""

    def setup_method(self):
        self.scheduler = SchedulerService()

    def test_init_not_started(self):
        """Scheduler non démarré à l'initialisation."""
        assert self.scheduler._started is False

    def test_start(self):
        """Démarre le scheduler."""
        with patch.object(self.scheduler._scheduler, 'start'):
            self.scheduler.start()
            assert self.scheduler._started is True

    def test_start_idempotent(self):
        """start() appelé deux fois ne relance pas."""
        with patch.object(self.scheduler._scheduler, 'start') as mock_start:
            self.scheduler.start()
            self.scheduler.start()
            mock_start.assert_called_once()

    def test_shutdown(self):
        """Arrête le scheduler."""
        with patch.object(self.scheduler._scheduler, 'start'):
            self.scheduler.start()
        with patch.object(self.scheduler._scheduler, 'shutdown'):
            self.scheduler.shutdown()
            assert self.scheduler._started is False

    def test_shutdown_not_started_noop(self):
        """shutdown() sans start() ne fait rien."""
        # Ne doit pas lever d'erreur
        self.scheduler.shutdown()
        assert self.scheduler._started is False

    def test_add_cron_job(self):
        """Ajoute un job cron."""
        with patch.object(self.scheduler._scheduler, 'add_job') as mock_add:
            def my_func(): pass
            self.scheduler.add_cron_job(my_func, "test-cron", hour=9, minute=30)
            mock_add.assert_called_once()
            call_kwargs = mock_add.call_args
            assert call_kwargs.kwargs["id"] == "test-cron"
            assert call_kwargs.kwargs["replace_existing"] is True

    def test_add_interval_job(self):
        """Ajoute un job intervalle."""
        with patch.object(self.scheduler._scheduler, 'add_job') as mock_add:
            def my_func(): pass
            self.scheduler.add_interval_job(my_func, "test-interval", hours=1, minutes=30)
            mock_add.assert_called_once()
            assert mock_add.call_args.kwargs["id"] == "test-interval"

    def test_remove_job_existing(self):
        """Supprime un job existant."""
        with patch.object(self.scheduler._scheduler, 'remove_job') as mock_remove:
            result = self.scheduler.remove_job("test-job")
            assert result is True
            mock_remove.assert_called_once_with("test-job")

    def test_remove_job_nonexistent(self):
        """Suppression d'un job inexistant retourne False."""
        with patch.object(self.scheduler._scheduler, 'remove_job', side_effect=Exception("Not found")):
            result = self.scheduler.remove_job("ghost-job")
            assert result is False

    def test_get_jobs(self):
        """get_jobs() délègue au scheduler interne."""
        mock_jobs = [Mock(), Mock()]
        with patch.object(self.scheduler._scheduler, 'get_jobs', return_value=mock_jobs):
            result = self.scheduler.get_jobs()
            assert len(result) == 2

    def test_run_job_now_existing(self):
        """run_job_now() déclenche un job existant."""
        mock_job = Mock()
        with patch.object(self.scheduler._scheduler, 'get_job', return_value=mock_job):
            result = self.scheduler.run_job_now("test-job")
            assert result is True
            mock_job.modify.assert_called_once()

    def test_run_job_now_nonexistent(self):
        """run_job_now() retourne False si job non trouvé."""
        with patch.object(self.scheduler._scheduler, 'get_job', return_value=None):
            result = self.scheduler.run_job_now("ghost-job")
            assert result is False

    def test_is_running_false_initially(self):
        """is_running est False à l'initialisation."""
        assert self.scheduler.is_running is False

    def test_is_running_true_when_started(self):
        """is_running est True quand scheduler démarré."""
        self.scheduler._started = True
        with patch.object(type(self.scheduler._scheduler), 'running', new_callable=lambda: property(lambda self: True)):
            assert self.scheduler.is_running is True


class TestGetScheduler:
    """Tests pour la factory get_scheduler."""

    def test_returns_scheduler_service(self):
        """get_scheduler() retourne une instance SchedulerService."""
        with patch("shared.infrastructure.scheduler.scheduler_service._scheduler", None):
            scheduler = get_scheduler()
            assert isinstance(scheduler, SchedulerService)

    def test_singleton_pattern(self):
        """get_scheduler() retourne la même instance."""
        with patch("shared.infrastructure.scheduler.scheduler_service._scheduler", None):
            s1 = get_scheduler()
            with patch("shared.infrastructure.scheduler.scheduler_service._scheduler", s1):
                s2 = get_scheduler()
            assert s1 is s2
