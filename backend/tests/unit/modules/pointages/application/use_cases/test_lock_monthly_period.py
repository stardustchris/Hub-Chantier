"""Tests unitaires pour LockMonthlyPeriodUseCase (GAP-FDH-009)."""

import pytest
from datetime import date
from unittest.mock import Mock

from modules.pointages.application.use_cases.lock_monthly_period import (
    LockMonthlyPeriodUseCase,
    LockMonthlyPeriodError,
)
from modules.pointages.application.dtos.lock_period_dtos import (
    LockMonthlyPeriodDTO,
)
from modules.pointages.domain.events.periode_paie_locked import PeriodePaieLockedEvent


class TestLockMonthlyPeriodUseCase:
    """Tests pour le use case de verrouillage de période de paie."""

    def setup_method(self):
        """Configure les mocks pour chaque test."""
        self.event_bus = Mock()
        self.use_case = LockMonthlyPeriodUseCase(event_bus=self.event_bus)

    def test_lock_period_success_auto(self):
        """Test nominal: verrouillage automatique réussi."""
        # Arrange
        dto = LockMonthlyPeriodDTO(year=2026, month=1)

        # Act
        result = self.use_case.execute(dto, auto_locked=True, locked_by=None)

        # Assert
        assert result.year == 2026
        assert result.month == 1
        assert result.success is True
        assert "Janvier 2026" in result.message
        assert "verrouillée" in result.message.lower()
        assert isinstance(result.lockdown_date, date)
        assert isinstance(result.notified_users, list)

        # Vérifie que l'événement a été publié
        assert self.event_bus.publish.call_count == 1
        published_event = self.event_bus.publish.call_args[0][0]
        assert isinstance(published_event, PeriodePaieLockedEvent)
        assert published_event.year == 2026
        assert published_event.month == 1
        assert published_event.auto_locked is True
        assert published_event.locked_by is None

    def test_lock_period_success_manual(self):
        """Test: verrouillage manuel réussi."""
        # Arrange
        dto = LockMonthlyPeriodDTO(year=2026, month=2)

        # Act
        result = self.use_case.execute(dto, auto_locked=False, locked_by=4)

        # Assert
        assert result.year == 2026
        assert result.month == 2
        assert result.success is True
        assert "Février 2026" in result.message

        # Vérifie que l'événement a été publié avec les bons paramètres
        published_event = self.event_bus.publish.call_args[0][0]
        assert published_event.auto_locked is False
        assert published_event.locked_by == 4

    def test_lock_period_invalid_month_too_low(self):
        """Test: erreur si mois < 1."""
        # Arrange
        dto = LockMonthlyPeriodDTO(year=2026, month=0)

        # Act & Assert
        with pytest.raises(LockMonthlyPeriodError) as exc_info:
            self.use_case.execute(dto)

        assert "mois doit être compris entre 1 et 12" in str(exc_info.value).lower()
        assert self.event_bus.publish.call_count == 0

    def test_lock_period_invalid_month_too_high(self):
        """Test: erreur si mois > 12."""
        # Arrange
        dto = LockMonthlyPeriodDTO(year=2026, month=13)

        # Act & Assert
        with pytest.raises(LockMonthlyPeriodError) as exc_info:
            self.use_case.execute(dto)

        assert "mois doit être compris entre 1 et 12" in str(exc_info.value).lower()
        assert self.event_bus.publish.call_count == 0

    def test_lock_period_invalid_year_too_low(self):
        """Test: erreur si année < 2000."""
        # Arrange
        dto = LockMonthlyPeriodDTO(year=1999, month=1)

        # Act & Assert
        with pytest.raises(LockMonthlyPeriodError) as exc_info:
            self.use_case.execute(dto)

        assert "année doit être comprise entre 2000 et 2100" in str(exc_info.value).lower()
        assert self.event_bus.publish.call_count == 0

    def test_lock_period_invalid_year_too_high(self):
        """Test: erreur si année > 2100."""
        # Arrange
        dto = LockMonthlyPeriodDTO(year=2101, month=1)

        # Act & Assert
        with pytest.raises(LockMonthlyPeriodError) as exc_info:
            self.use_case.execute(dto)

        assert "année doit être comprise entre 2000 et 2100" in str(exc_info.value).lower()
        assert self.event_bus.publish.call_count == 0

    def test_lock_period_all_months(self):
        """Test: verrouillage pour tous les mois (1 à 12)."""
        # Act & Assert - Tous les mois doivent fonctionner
        for month in range(1, 13):
            dto = LockMonthlyPeriodDTO(year=2026, month=month)
            result = self.use_case.execute(dto)

            assert result.success is True
            assert result.month == month
            assert result.year == 2026

    def test_lock_period_lockdown_date_calculation(self):
        """Test: calcul correct de la date de verrouillage."""
        # Arrange - Janvier 2026
        dto = LockMonthlyPeriodDTO(year=2026, month=1)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        # Pour janvier 2026, la dernière semaine commence le lundi 26
        # Le vendredi précédent est le 23/01/2026
        assert result.lockdown_date == date(2026, 1, 23)

    def test_lock_period_message_format(self):
        """Test: format du message de confirmation."""
        # Arrange
        dto = LockMonthlyPeriodDTO(year=2026, month=3)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert "Mars 2026" in result.message
        assert "verrouillée" in result.message.lower()
        assert result.lockdown_date.strftime("%d/%m/%Y") in result.message
        assert "aucune modification" in result.message.lower()

    def test_lock_period_without_event_bus(self):
        """Test: utilise NullEventBus si event_bus non fourni."""
        # Arrange
        use_case = LockMonthlyPeriodUseCase(event_bus=None)
        dto = LockMonthlyPeriodDTO(year=2026, month=1)

        # Act
        result = use_case.execute(dto)

        # Assert
        assert result.success is True
        # NullEventBus ne lève pas d'erreur

    def test_lock_period_february_leap_year(self):
        """Test: verrouillage de février année bissextile."""
        # Arrange - 2024 est bissextile
        dto = LockMonthlyPeriodDTO(year=2024, month=2)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.success is True
        assert result.month == 2
        assert result.year == 2024
        # Février 2024 a 29 jours

    def test_lock_period_december(self):
        """Test: verrouillage de décembre."""
        # Arrange
        dto = LockMonthlyPeriodDTO(year=2026, month=12)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.success is True
        assert "Décembre 2026" in result.message

    def test_lock_period_event_data_completeness(self):
        """Test: événement publié contient toutes les données."""
        # Arrange
        dto = LockMonthlyPeriodDTO(year=2026, month=6)

        # Act
        result = self.use_case.execute(dto, auto_locked=True, locked_by=None)

        # Assert
        published_event = self.event_bus.publish.call_args[0][0]
        assert hasattr(published_event, "year")
        assert hasattr(published_event, "month")
        assert hasattr(published_event, "lockdown_date")
        assert hasattr(published_event, "auto_locked")
        assert hasattr(published_event, "locked_by")
        assert published_event.year == 2026
        assert published_event.month == 6
        assert published_event.lockdown_date == result.lockdown_date

    def test_lock_period_notified_users_empty_by_default(self):
        """Test: liste des utilisateurs notifiés est vide par défaut (TODO)."""
        # Arrange
        dto = LockMonthlyPeriodDTO(year=2026, month=1)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        # Pour l'instant, _get_users_to_notify retourne []
        assert result.notified_users == []

    def test_lock_period_boundary_years(self):
        """Test: années limites (2000 et 2100)."""
        # Arrange & Act & Assert
        # Année 2000
        dto_2000 = LockMonthlyPeriodDTO(year=2000, month=1)
        result_2000 = self.use_case.execute(dto_2000)
        assert result_2000.success is True
        assert result_2000.year == 2000

        # Année 2100
        dto_2100 = LockMonthlyPeriodDTO(year=2100, month=12)
        result_2100 = self.use_case.execute(dto_2100)
        assert result_2100.success is True
        assert result_2100.year == 2100
