"""Tests unitaires pour les Use Cases LotBudgetaire du module Financier."""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.financier.domain.entities import Budget, LotBudgetaire
from modules.financier.domain.repositories import (
    LotBudgetaireRepository,
    BudgetRepository,
    AchatRepository,
    JournalFinancierRepository,
)
from modules.financier.domain.value_objects import UniteMesure
from modules.financier.application.ports.event_bus import EventBus
from modules.financier.application.dtos import (
    LotBudgetaireCreateDTO,
    LotBudgetaireUpdateDTO,
)
from modules.financier.application.use_cases.lot_budgetaire_use_cases import (
    CreateLotBudgetaireUseCase,
    UpdateLotBudgetaireUseCase,
    DeleteLotBudgetaireUseCase,
    GetLotBudgetaireUseCase,
    ListLotsBudgetairesUseCase,
    LotNotFoundError,
    LotCodeExistsError,
)
from modules.financier.application.use_cases.budget_use_cases import (
    BudgetNotFoundError,
)


class TestCreateLotBudgetaireUseCase:
    """Tests pour le use case de creation de lot budgetaire."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = CreateLotBudgetaireUseCase(
            lot_repository=self.mock_lot_repo,
            budget_repository=self.mock_budget_repo,
            achat_repository=self.mock_achat_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_create_lot_success(self):
        """Test: creation reussie d'un lot budgetaire."""
        budget = Budget(
            id=10,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
        )
        self.mock_budget_repo.find_by_id.return_value = budget
        self.mock_lot_repo.find_by_code.return_value = None

        def save_side_effect(lot):
            lot.id = 1
            return lot

        self.mock_lot_repo.save.side_effect = save_side_effect

        dto = LotBudgetaireCreateDTO(
            budget_id=10,
            code_lot="GO-01",
            libelle="Gros oeuvre",
            unite=UniteMesure.M2,
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
        )
        result = self.use_case.execute(dto, created_by=10)

        assert result.id == 1
        assert result.code_lot == "GO-01"
        assert result.libelle == "Gros oeuvre"
        self.mock_lot_repo.save.assert_called_once()
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_create_lot_budget_not_found(self):
        """Test: erreur si le budget n'existe pas."""
        self.mock_budget_repo.find_by_id.return_value = None

        dto = LotBudgetaireCreateDTO(
            budget_id=999,
            code_lot="GO-01",
            libelle="Test",
        )

        with pytest.raises(BudgetNotFoundError):
            self.use_case.execute(dto, created_by=10)

    def test_create_lot_code_duplicate(self):
        """Test: erreur si le code lot existe deja dans le budget."""
        budget = Budget(
            id=10,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
        )
        self.mock_budget_repo.find_by_id.return_value = budget

        existing_lot = LotBudgetaire(
            id=99,
            budget_id=10,
            code_lot="GO-01",
            libelle="Existant",
        )
        self.mock_lot_repo.find_by_code.return_value = existing_lot

        dto = LotBudgetaireCreateDTO(
            budget_id=10,
            code_lot="GO-01",
            libelle="Nouveau",
        )

        with pytest.raises(LotCodeExistsError) as exc_info:
            self.use_case.execute(dto, created_by=10)
        assert "GO-01" in str(exc_info.value)


class TestUpdateLotBudgetaireUseCase:
    """Tests pour le use case de mise a jour de lot budgetaire."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = UpdateLotBudgetaireUseCase(
            lot_repository=self.mock_lot_repo,
            achat_repository=self.mock_achat_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_update_lot_success(self):
        """Test: mise a jour reussie d'un lot budgetaire."""
        existing = LotBudgetaire(
            id=1,
            budget_id=10,
            code_lot="GO-01",
            libelle="Ancien libelle",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
            created_at=datetime.utcnow(),
        )
        self.mock_lot_repo.find_by_id.return_value = existing
        self.mock_lot_repo.save.return_value = existing
        self.mock_achat_repo.somme_by_lot.return_value = Decimal("0")

        dto = LotBudgetaireUpdateDTO(libelle="Nouveau libelle")
        result = self.use_case.execute(1, dto, updated_by=10)

        assert result.libelle == "Nouveau libelle"
        self.mock_lot_repo.save.assert_called_once()

    def test_update_lot_not_found(self):
        """Test: erreur si lot non trouve."""
        self.mock_lot_repo.find_by_id.return_value = None

        dto = LotBudgetaireUpdateDTO(libelle="Test")

        with pytest.raises(LotNotFoundError):
            self.use_case.execute(999, dto, updated_by=10)

    def test_update_lot_code_duplicate(self):
        """Test: erreur si nouveau code existe deja dans le budget."""
        existing = LotBudgetaire(
            id=1,
            budget_id=10,
            code_lot="GO-01",
            libelle="Test",
            created_at=datetime.utcnow(),
        )
        self.mock_lot_repo.find_by_id.return_value = existing

        other = LotBudgetaire(
            id=2,
            budget_id=10,
            code_lot="GO-02",
            libelle="Autre",
        )
        self.mock_lot_repo.find_by_code.return_value = other

        dto = LotBudgetaireUpdateDTO(code_lot="GO-02")

        with pytest.raises(LotCodeExistsError):
            self.use_case.execute(1, dto, updated_by=10)


class TestDeleteLotBudgetaireUseCase:
    """Tests pour le use case de suppression de lot budgetaire."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = DeleteLotBudgetaireUseCase(
            lot_repository=self.mock_lot_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_delete_lot_success(self):
        """Test: suppression reussie d'un lot budgetaire."""
        existing = LotBudgetaire(
            id=1,
            budget_id=10,
            code_lot="GO-01",
            libelle="Test",
            created_at=datetime.utcnow(),
        )
        self.mock_lot_repo.find_by_id.return_value = existing
        self.mock_lot_repo.delete.return_value = True

        result = self.use_case.execute(1, deleted_by=10)

        assert result is True
        self.mock_lot_repo.delete.assert_called_once_with(1, deleted_by=10)
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_delete_lot_not_found(self):
        """Test: erreur si lot non trouve."""
        self.mock_lot_repo.find_by_id.return_value = None

        with pytest.raises(LotNotFoundError):
            self.use_case.execute(999, deleted_by=10)


class TestGetLotBudgetaireUseCase:
    """Tests pour le use case de recuperation d'un lot budgetaire."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.use_case = GetLotBudgetaireUseCase(
            lot_repository=self.mock_lot_repo,
            achat_repository=self.mock_achat_repo,
        )

    def test_get_lot_success(self):
        """Test: recuperation reussie d'un lot avec enrichissement."""
        existing = LotBudgetaire(
            id=1,
            budget_id=10,
            code_lot="GO-01",
            libelle="Gros oeuvre",
            unite=UniteMesure.M2,
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
            created_at=datetime.utcnow(),
        )
        self.mock_lot_repo.find_by_id.return_value = existing
        self.mock_achat_repo.somme_by_lot.return_value = Decimal("2000")

        result = self.use_case.execute(1)

        assert result.id == 1
        assert result.code_lot == "GO-01"
        # somme_by_lot appele 2 fois (engage + realise)
        assert self.mock_achat_repo.somme_by_lot.call_count == 2

    def test_get_lot_not_found(self):
        """Test: erreur si lot non trouve."""
        self.mock_lot_repo.find_by_id.return_value = None

        with pytest.raises(LotNotFoundError):
            self.use_case.execute(999)


class TestListLotsBudgetairesUseCase:
    """Tests pour le use case de listage des lots budgetaires."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.use_case = ListLotsBudgetairesUseCase(
            lot_repository=self.mock_lot_repo,
            achat_repository=self.mock_achat_repo,
        )

    def test_list_lots_success(self):
        """Test: listage reussi des lots budgetaires."""
        lots = [
            LotBudgetaire(
                id=1,
                budget_id=10,
                code_lot="GO-01",
                libelle="Gros oeuvre",
                quantite_prevue=Decimal("100"),
                prix_unitaire_ht=Decimal("50"),
                created_at=datetime.utcnow(),
            ),
            LotBudgetaire(
                id=2,
                budget_id=10,
                code_lot="SEC-01",
                libelle="Second oeuvre",
                quantite_prevue=Decimal("50"),
                prix_unitaire_ht=Decimal("30"),
                created_at=datetime.utcnow(),
            ),
        ]
        self.mock_lot_repo.find_all_by_budget.return_value = lots
        self.mock_lot_repo.count_by_budget.return_value = 2
        self.mock_achat_repo.somme_by_lot.return_value = Decimal("0")

        result = self.use_case.execute(budget_id=10)

        assert len(result.items) == 2
        assert result.total == 2
        assert result.items[0].code_lot == "GO-01"
