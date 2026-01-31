"""Tests unitaires pour les Use Cases Budget du module Financier."""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.financier.domain.entities import Budget
from modules.financier.domain.repositories import (
    BudgetRepository,
    JournalFinancierRepository,
)
from modules.financier.application.ports.event_bus import EventBus
from modules.financier.application.dtos import (
    BudgetCreateDTO,
    BudgetUpdateDTO,
)
from modules.financier.application.use_cases.budget_use_cases import (
    CreateBudgetUseCase,
    UpdateBudgetUseCase,
    GetBudgetUseCase,
    GetBudgetByChantierUseCase,
    BudgetNotFoundError,
    BudgetAlreadyExistsError,
)


class TestCreateBudgetUseCase:
    """Tests pour le use case de creation de budget."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=BudgetRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = CreateBudgetUseCase(
            budget_repository=self.mock_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_create_budget_success(self):
        """Test: creation reussie d'un budget."""
        dto = BudgetCreateDTO(
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
            retenue_garantie_pct=Decimal("5"),
            seuil_alerte_pct=Decimal("80"),
            seuil_validation_achat=Decimal("1000"),
        )

        # Pas de budget existant pour ce chantier
        self.mock_repo.find_by_chantier_id.return_value = None

        def save_side_effect(budget):
            budget.id = 1
            return budget

        self.mock_repo.save.side_effect = save_side_effect

        result = self.use_case.execute(dto, created_by=10)

        assert result.id == 1
        assert result.chantier_id == 100
        assert result.montant_initial_ht == "500000"
        self.mock_repo.save.assert_called_once()
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_create_budget_already_exists(self):
        """Test: erreur si un budget existe deja pour le chantier."""
        dto = BudgetCreateDTO(
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
        )

        # Budget existant
        self.mock_repo.find_by_chantier_id.return_value = Budget(
            id=99,
            chantier_id=100,
            montant_initial_ht=Decimal("300000"),
        )

        with pytest.raises(BudgetAlreadyExistsError) as exc_info:
            self.use_case.execute(dto, created_by=10)
        assert "100" in str(exc_info.value)
        self.mock_repo.save.assert_not_called()


class TestUpdateBudgetUseCase:
    """Tests pour le use case de mise a jour de budget."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=BudgetRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = UpdateBudgetUseCase(
            budget_repository=self.mock_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_update_budget_success(self):
        """Test: mise a jour reussie d'un budget."""
        existing = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
            created_at=datetime.utcnow(),
        )
        self.mock_repo.find_by_id.return_value = existing
        self.mock_repo.save.return_value = existing

        dto = BudgetUpdateDTO(montant_initial_ht=Decimal("600000"))
        result = self.use_case.execute(1, dto, updated_by=10)

        assert result.montant_initial_ht == "600000"
        self.mock_repo.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_update_budget_not_found(self):
        """Test: erreur si budget non trouve."""
        self.mock_repo.find_by_id.return_value = None

        dto = BudgetUpdateDTO(montant_initial_ht=Decimal("600000"))

        with pytest.raises(BudgetNotFoundError):
            self.use_case.execute(999, dto, updated_by=10)

    def test_update_budget_retenue_garantie(self):
        """Test: modification de la retenue de garantie via use case."""
        existing = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
            retenue_garantie_pct=Decimal("5"),
            created_at=datetime.utcnow(),
        )
        self.mock_repo.find_by_id.return_value = existing
        self.mock_repo.save.return_value = existing

        dto = BudgetUpdateDTO(retenue_garantie_pct=Decimal("10"))
        result = self.use_case.execute(1, dto, updated_by=10)

        assert result.retenue_garantie_pct == "10"

    def test_update_budget_multiple_fields(self):
        """Test: mise a jour de plusieurs champs a la fois."""
        existing = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
            notes="Ancienne note",
            created_at=datetime.utcnow(),
        )
        self.mock_repo.find_by_id.return_value = existing
        self.mock_repo.save.return_value = existing

        dto = BudgetUpdateDTO(
            montant_initial_ht=Decimal("600000"),
            notes="Nouvelle note",
        )
        result = self.use_case.execute(1, dto, updated_by=10)

        # Journal doit avoir 2 entrees (montant_initial_ht + notes)
        assert self.mock_journal.save.call_count == 2


class TestGetBudgetUseCase:
    """Tests pour le use case de recuperation d'un budget."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=BudgetRepository)
        self.use_case = GetBudgetUseCase(budget_repository=self.mock_repo)

    def test_get_budget_success(self):
        """Test: recuperation reussie d'un budget."""
        existing = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
            created_at=datetime.utcnow(),
        )
        self.mock_repo.find_by_id.return_value = existing

        result = self.use_case.execute(1)

        assert result.id == 1
        assert result.chantier_id == 100

    def test_get_budget_not_found(self):
        """Test: erreur si budget non trouve."""
        self.mock_repo.find_by_id.return_value = None

        with pytest.raises(BudgetNotFoundError):
            self.use_case.execute(999)


class TestGetBudgetByChantierUseCase:
    """Tests pour le use case de recuperation du budget d'un chantier."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=BudgetRepository)
        self.use_case = GetBudgetByChantierUseCase(
            budget_repository=self.mock_repo,
        )

    def test_get_budget_by_chantier_success(self):
        """Test: recuperation reussie du budget d'un chantier."""
        existing = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
            created_at=datetime.utcnow(),
        )
        self.mock_repo.find_by_chantier_id.return_value = existing

        result = self.use_case.execute(100)

        assert result.id == 1
        assert result.chantier_id == 100

    def test_get_budget_by_chantier_not_found(self):
        """Test: erreur si pas de budget pour ce chantier."""
        self.mock_repo.find_by_chantier_id.return_value = None

        with pytest.raises(BudgetNotFoundError):
            self.use_case.execute(999)
