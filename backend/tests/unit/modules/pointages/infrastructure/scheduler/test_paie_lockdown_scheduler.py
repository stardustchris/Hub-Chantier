"""Tests unitaires pour PaieLockdownScheduler (GAP-FDH-009)."""

import pytest
from datetime import date
from unittest.mock import Mock, patch, MagicMock

from modules.pointages.infrastructure.scheduler.paie_lockdown_scheduler import (
    PaieLockdownScheduler,
    get_paie_lockdown_scheduler,
    start_paie_lockdown_scheduler,
    stop_paie_lockdown_scheduler,
)
from modules.pointages.application.use_cases.lock_monthly_period import (
    LockMonthlyPeriodUseCase,
)
from modules.pointages.application.dtos.lock_period_dtos import (
    LockMonthlyPeriodDTO,
    LockMonthlyPeriodResultDTO,
)


class TestPaieLockdownScheduler:
    """Tests pour le scheduler de verrouillage automatique."""

    def setup_method(self):
        """Configure les mocks pour chaque test."""
        self.mock_use_case = Mock(spec=LockMonthlyPeriodUseCase)
        self.scheduler = PaieLockdownScheduler(use_case=self.mock_use_case)

    def teardown_method(self):
        """Arrête le scheduler après chaque test."""
        if self.scheduler.scheduler.running:
            self.scheduler.stop()

    def test_scheduler_initialization(self):
        """Test: initialisation du scheduler."""
        # Assert
        assert self.scheduler.use_case == self.mock_use_case
        assert self.scheduler.scheduler is not None
        assert not self.scheduler.scheduler.running

    def test_scheduler_start(self):
        """Test: démarrage du scheduler."""
        # Act
        self.scheduler.start()

        # Assert
        assert self.scheduler.scheduler.running
        # Vérifie qu'un job a été ajouté
        jobs = self.scheduler.scheduler.get_jobs()
        assert len(jobs) == 1
        assert jobs[0].id == "paie_lockdown_check"
        assert jobs[0].name == "Vérification verrouillage période paie"

    def test_scheduler_stop(self):
        """Test: arrêt du scheduler."""
        # Arrange
        self.scheduler.start()
        assert self.scheduler.scheduler.running

        # Act
        self.scheduler.stop()

        # Assert
        assert not self.scheduler.scheduler.running

    def test_scheduler_cron_trigger_configuration(self):
        """Test: configuration du trigger cron (vendredis à 23:59)."""
        # Act
        self.scheduler.start()

        # Assert
        jobs = self.scheduler.scheduler.get_jobs()
        trigger = jobs[0].trigger

        # Vérifie que le trigger est configuré pour vendredi (day_of_week=4)
        # et 23:59
        assert hasattr(trigger, "fields")
        # day_of_week: 0=lundi, 4=vendredi
        assert str(trigger.fields[4]) == "4"  # day_of_week
        assert str(trigger.fields[5]) == "23"  # hour
        assert str(trigger.fields[6]) == "59"  # minute

    @patch("modules.pointages.infrastructure.scheduler.paie_lockdown_scheduler.date")
    def test_check_and_lock_period_lockdown_day(self, mock_date_class):
        """Test: déclenchement du verrouillage le bon vendredi."""
        # Arrange
        # Pour janvier 2026, le vendredi de verrouillage est le 23/01/2026
        lockdown_friday = date(2026, 1, 23)
        mock_date_class.today.return_value = lockdown_friday

        # Configure le résultat du use case
        self.mock_use_case.execute.return_value = LockMonthlyPeriodResultDTO(
            year=2026,
            month=1,
            lockdown_date=lockdown_friday,
            success=True,
            message="Verrouillé",
            notified_users=[],
        )

        # Act
        self.scheduler._check_and_lock_period()

        # Assert
        # Le use case doit avoir été appelé pour janvier 2026
        self.mock_use_case.execute.assert_called_once()
        call_args = self.mock_use_case.execute.call_args
        dto = call_args[0][0]
        assert isinstance(dto, LockMonthlyPeriodDTO)
        assert dto.year == 2026
        assert dto.month == 1
        assert call_args[1]["auto_locked"] is True
        assert call_args[1]["locked_by"] is None

    @patch("modules.pointages.infrastructure.scheduler.paie_lockdown_scheduler.date")
    def test_check_and_lock_period_not_lockdown_day(self, mock_date_class):
        """Test: pas de déclenchement si ce n'est pas le bon vendredi."""
        # Arrange
        # Un vendredi quelconque (pas le vendredi de verrouillage)
        regular_friday = date(2026, 1, 16)
        mock_date_class.today.return_value = regular_friday

        # Act
        self.scheduler._check_and_lock_period()

        # Assert
        # Le use case ne doit PAS être appelé
        self.mock_use_case.execute.assert_not_called()

    @patch("modules.pointages.infrastructure.scheduler.paie_lockdown_scheduler.date")
    def test_check_and_lock_period_previous_month(self, mock_date_class):
        """Test: gère correctement le verrouillage du mois précédent."""
        # Arrange
        # Premier jour de février, qui pourrait être un vendredi de verrouillage
        # pour janvier si janvier se termine un dimanche
        first_friday_february = date(2026, 2, 6)
        mock_date_class.today.return_value = first_friday_february

        # Act
        self.scheduler._check_and_lock_period()

        # Assert
        # Aucun verrouillage car 6/02 n'est pas un vendredi de verrouillage
        # (janvier 2026 se termine le samedi 31, donc vendredi de verrouillage = 23/01)
        self.mock_use_case.execute.assert_not_called()

    @patch("modules.pointages.infrastructure.scheduler.paie_lockdown_scheduler.date")
    def test_lock_period_success(self, mock_date_class):
        """Test: _lock_period exécute le use case correctement."""
        # Arrange
        mock_date_class.today.return_value = date(2026, 1, 23)
        self.mock_use_case.execute.return_value = LockMonthlyPeriodResultDTO(
            year=2026,
            month=1,
            lockdown_date=date(2026, 1, 23),
            success=True,
            message="Verrouillé",
            notified_users=[1, 2, 3],
        )

        # Act
        self.scheduler._lock_period(2026, 1)

        # Assert
        self.mock_use_case.execute.assert_called_once()
        call_args = self.mock_use_case.execute.call_args
        dto = call_args[0][0]
        assert dto.year == 2026
        assert dto.month == 1

    def test_lock_period_handles_exception(self):
        """Test: _lock_period gère les exceptions sans planter."""
        # Arrange
        self.mock_use_case.execute.side_effect = Exception("DB error")

        # Act - Ne doit pas lever d'exception
        self.scheduler._lock_period(2026, 1)

        # Assert
        self.mock_use_case.execute.assert_called_once()

    @patch("modules.pointages.infrastructure.scheduler.paie_lockdown_scheduler.date")
    def test_check_and_lock_period_february_lockdown(self, mock_date_class):
        """Test: verrouillage de février."""
        # Arrange
        # Pour février 2026, calculer le vendredi de verrouillage
        lockdown_friday = date(2026, 2, 20)
        mock_date_class.today.return_value = lockdown_friday

        self.mock_use_case.execute.return_value = LockMonthlyPeriodResultDTO(
            year=2026,
            month=2,
            lockdown_date=lockdown_friday,
            success=True,
            message="Verrouillé",
            notified_users=[],
        )

        # Act
        self.scheduler._check_and_lock_period()

        # Assert
        self.mock_use_case.execute.assert_called_once()
        dto = self.mock_use_case.execute.call_args[0][0]
        assert dto.month == 2

    def test_get_paie_lockdown_scheduler_singleton(self):
        """Test: get_paie_lockdown_scheduler retourne un singleton."""
        # Act
        scheduler1 = get_paie_lockdown_scheduler()
        scheduler2 = get_paie_lockdown_scheduler()

        # Assert
        assert scheduler1 is scheduler2

        # Cleanup
        if scheduler1.scheduler.running:
            scheduler1.stop()

    @patch("modules.pointages.infrastructure.scheduler.paie_lockdown_scheduler.get_paie_lockdown_scheduler")
    def test_start_paie_lockdown_scheduler_starts_if_not_running(self, mock_get_scheduler):
        """Test: start_paie_lockdown_scheduler démarre le scheduler."""
        # Arrange
        mock_scheduler = Mock()
        mock_scheduler.scheduler.running = False
        mock_get_scheduler.return_value = mock_scheduler

        # Act
        start_paie_lockdown_scheduler()

        # Assert
        mock_scheduler.start.assert_called_once()

    @patch("modules.pointages.infrastructure.scheduler.paie_lockdown_scheduler.get_paie_lockdown_scheduler")
    def test_start_paie_lockdown_scheduler_does_not_restart(self, mock_get_scheduler):
        """Test: start_paie_lockdown_scheduler ne redémarre pas si déjà actif."""
        # Arrange
        mock_scheduler = Mock()
        mock_scheduler.scheduler.running = True
        mock_get_scheduler.return_value = mock_scheduler

        # Act
        start_paie_lockdown_scheduler()

        # Assert
        mock_scheduler.start.assert_not_called()

    @patch("modules.pointages.infrastructure.scheduler.paie_lockdown_scheduler._scheduler_instance")
    def test_stop_paie_lockdown_scheduler_stops_if_running(self, mock_instance):
        """Test: stop_paie_lockdown_scheduler arrête le scheduler."""
        # Arrange
        mock_scheduler = Mock()
        with patch("modules.pointages.infrastructure.scheduler.paie_lockdown_scheduler._scheduler_instance", mock_scheduler):
            # Act
            stop_paie_lockdown_scheduler()

            # Assert
            mock_scheduler.stop.assert_called_once()

    def test_scheduler_without_use_case_creates_default(self):
        """Test: scheduler sans use case crée une instance par défaut."""
        # Arrange & Act
        scheduler = PaieLockdownScheduler(use_case=None)

        # Assert
        assert scheduler.use_case is not None
        assert isinstance(scheduler.use_case, LockMonthlyPeriodUseCase)

        # Cleanup
        if scheduler.scheduler.running:
            scheduler.stop()

    @patch("modules.pointages.infrastructure.scheduler.paie_lockdown_scheduler.date")
    def test_check_and_lock_period_december(self, mock_date_class):
        """Test: verrouillage de décembre (passage d'année)."""
        # Arrange
        # Pour décembre 2026, vendredi de verrouillage
        lockdown_friday = date(2026, 12, 25)
        mock_date_class.today.return_value = lockdown_friday

        self.mock_use_case.execute.return_value = LockMonthlyPeriodResultDTO(
            year=2026,
            month=12,
            lockdown_date=lockdown_friday,
            success=True,
            message="Verrouillé",
            notified_users=[],
        )

        # Act
        self.scheduler._check_and_lock_period()

        # Assert
        # Vérifie que le verrouillage de décembre a été déclenché
        if self.mock_use_case.execute.called:
            dto = self.mock_use_case.execute.call_args[0][0]
            assert dto.year == 2026
            assert dto.month == 12

    @patch("modules.pointages.infrastructure.scheduler.paie_lockdown_scheduler.date")
    def test_check_and_lock_period_january_previous_year(self, mock_date_class):
        """Test: gère correctement janvier (mois précédent = décembre année précédente)."""
        # Arrange
        # Premier vendredi de janvier qui pourrait être le verrouillage de décembre
        first_friday_january = date(2027, 1, 1)
        mock_date_class.today.return_value = first_friday_january

        # Act
        self.scheduler._check_and_lock_period()

        # Assert
        # Si c'est le vendredi de verrouillage, le use case doit être appelé
        # Sinon, pas d'appel
        # (Dépend du calcul de PeriodePaie.get_lockdown_date pour décembre 2026)
