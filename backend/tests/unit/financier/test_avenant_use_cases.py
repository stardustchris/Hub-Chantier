"""Tests unitaires pour les Use Cases Avenant du module Financier."""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch

from modules.financier.domain.entities import AvenantBudgetaire, Budget
from modules.financier.domain.repositories import (
    BudgetRepository,
    JournalFinancierRepository,
)
from modules.financier.domain.repositories.avenant_repository import AvenantRepository
from modules.financier.application.ports.event_bus import EventBus
from modules.financier.application.dtos.avenant_dtos import (
    AvenantCreateDTO,
    AvenantUpdateDTO,
)
from modules.financier.application.use_cases.avenant_use_cases import (
    CreateAvenantUseCase,
    UpdateAvenantUseCase,
    ValiderAvenantUseCase,
    GetAvenantUseCase,
    ListAvenantsUseCase,
    DeleteAvenantUseCase,
    AvenantNotFoundError,
    AvenantAlreadyValideError,
)


class TestCreateAvenantUseCase:
    """Tests pour le use case de creation d'avenant."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_avenant_repo = Mock(spec=AvenantRepository)
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = CreateAvenantUseCase(
            avenant_repository=self.mock_avenant_repo,
            budget_repository=self.mock_budget_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_create_avenant_success(self):
        """Test: creation reussie d'un avenant avec auto-numero."""
        budget = Budget(
            id=10,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
        )
        self.mock_budget_repo.find_by_id.return_value = budget
        self.mock_avenant_repo.count_by_budget_id.return_value = 2

        def save_side_effect(avenant):
            avenant.id = 1
            return avenant

        self.mock_avenant_repo.save.side_effect = save_side_effect

        dto = AvenantCreateDTO(
            budget_id=10,
            motif="Travaux supplementaires",
            montant_ht=Decimal("25000"),
            impact_description="Ajout terrassement",
        )

        result = self.use_case.execute(dto, created_by=5)

        assert result.id == 1
        assert result.budget_id == 10
        assert result.motif == "Travaux supplementaires"
        assert result.montant_ht == "25000"
        assert result.statut == "brouillon"
        # Numero auto: AVN-YYYY-03 (count=2 -> 03)
        assert "AVN-" in result.numero
        assert "-03" in result.numero
        self.mock_avenant_repo.save.assert_called_once()
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_create_avenant_budget_not_found(self):
        """Test: erreur si le budget n'existe pas."""
        self.mock_budget_repo.find_by_id.return_value = None

        dto = AvenantCreateDTO(
            budget_id=999,
            motif="Test",
            montant_ht=Decimal("10000"),
        )

        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(dto, created_by=5)
        assert "999" in str(exc_info.value)

    def test_create_avenant_premier_avenant(self):
        """Test: premier avenant d'un budget (numero -01)."""
        budget = Budget(id=10, chantier_id=100, montant_initial_ht=Decimal("500000"))
        self.mock_budget_repo.find_by_id.return_value = budget
        self.mock_avenant_repo.count_by_budget_id.return_value = 0

        def save_side_effect(avenant):
            avenant.id = 1
            return avenant

        self.mock_avenant_repo.save.side_effect = save_side_effect

        dto = AvenantCreateDTO(
            budget_id=10,
            motif="Premier avenant",
            montant_ht=Decimal("5000"),
        )

        result = self.use_case.execute(dto, created_by=5)
        assert "-01" in result.numero


class TestValiderAvenantUseCase:
    """Tests pour le use case de validation d'avenant."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_avenant_repo = Mock(spec=AvenantRepository)
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = ValiderAvenantUseCase(
            avenant_repository=self.mock_avenant_repo,
            budget_repository=self.mock_budget_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_valider_avenant_success(self):
        """Test: validation reussie d'un avenant et mise a jour du budget."""
        avenant = AvenantBudgetaire(
            id=1,
            budget_id=10,
            numero="AVN-2026-01",
            motif="Travaux supplementaires",
            montant_ht=Decimal("25000"),
            statut="brouillon",
            created_at=datetime.utcnow(),
        )
        budget = Budget(
            id=10,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
        )
        self.mock_avenant_repo.find_by_id.return_value = avenant
        self.mock_avenant_repo.save.return_value = avenant
        self.mock_avenant_repo.somme_avenants_valides.return_value = Decimal("25000")
        self.mock_budget_repo.find_by_id.return_value = budget
        self.mock_budget_repo.save.return_value = budget

        result = self.use_case.execute(avenant_id=1, validated_by=5)

        assert result.statut == "valide"
        assert result.validated_by == 5
        self.mock_avenant_repo.save.assert_called_once()
        self.mock_budget_repo.save.assert_called_once()
        # Verifie que le budget a ete mis a jour
        assert budget.montant_avenants_ht == Decimal("25000")
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_valider_avenant_not_found(self):
        """Test: erreur si avenant non trouve."""
        self.mock_avenant_repo.find_by_id.return_value = None

        with pytest.raises(AvenantNotFoundError):
            self.use_case.execute(avenant_id=999, validated_by=5)

    def test_valider_avenant_deja_valide(self):
        """Test: erreur si avenant deja valide."""
        avenant = AvenantBudgetaire(
            id=1,
            budget_id=10,
            numero="AVN-2026-01",
            motif="Test",
            montant_ht=Decimal("10000"),
            statut="valide",
            created_at=datetime.utcnow(),
        )
        self.mock_avenant_repo.find_by_id.return_value = avenant

        with pytest.raises(AvenantAlreadyValideError):
            self.use_case.execute(avenant_id=1, validated_by=5)


class TestUpdateAvenantUseCase:
    """Tests pour le use case de mise a jour d'avenant."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_avenant_repo = Mock(spec=AvenantRepository)
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.use_case = UpdateAvenantUseCase(
            avenant_repository=self.mock_avenant_repo,
            budget_repository=self.mock_budget_repo,
            journal_repository=self.mock_journal,
        )

    def test_update_avenant_success(self):
        """Test: mise a jour reussie d'un avenant brouillon."""
        avenant = AvenantBudgetaire(
            id=1,
            budget_id=10,
            numero="AVN-2026-01",
            motif="Ancien motif",
            montant_ht=Decimal("10000"),
            statut="brouillon",
            created_at=datetime.utcnow(),
        )
        budget = Budget(id=10, chantier_id=100, montant_initial_ht=Decimal("500000"))
        self.mock_avenant_repo.find_by_id.return_value = avenant
        self.mock_avenant_repo.save.return_value = avenant
        self.mock_budget_repo.find_by_id.return_value = budget

        dto = AvenantUpdateDTO(
            motif="Nouveau motif",
            montant_ht=Decimal("15000"),
        )

        result = self.use_case.execute(1, dto, updated_by=5)

        assert result.motif == "Nouveau motif"
        assert result.montant_ht == "15000"
        self.mock_avenant_repo.save.assert_called_once()

    def test_update_avenant_not_found(self):
        """Test: erreur si avenant non trouve."""
        self.mock_avenant_repo.find_by_id.return_value = None

        dto = AvenantUpdateDTO(motif="Test")

        with pytest.raises(AvenantNotFoundError):
            self.use_case.execute(999, dto, updated_by=5)

    def test_update_avenant_deja_valide(self):
        """Test: erreur si avenant deja valide."""
        avenant = AvenantBudgetaire(
            id=1,
            budget_id=10,
            numero="AVN-2026-01",
            motif="Test",
            montant_ht=Decimal("10000"),
            statut="valide",
            created_at=datetime.utcnow(),
        )
        self.mock_avenant_repo.find_by_id.return_value = avenant

        dto = AvenantUpdateDTO(motif="Nouveau motif")

        with pytest.raises(AvenantAlreadyValideError):
            self.use_case.execute(1, dto, updated_by=5)


class TestDeleteAvenantUseCase:
    """Tests pour le use case de suppression d'avenant."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_avenant_repo = Mock(spec=AvenantRepository)
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.use_case = DeleteAvenantUseCase(
            avenant_repository=self.mock_avenant_repo,
            budget_repository=self.mock_budget_repo,
            journal_repository=self.mock_journal,
        )

    def test_delete_avenant_brouillon_success(self):
        """Test: suppression reussie d'un avenant brouillon."""
        avenant = AvenantBudgetaire(
            id=1,
            budget_id=10,
            numero="AVN-2026-01",
            motif="Test",
            montant_ht=Decimal("10000"),
            statut="brouillon",
            created_at=datetime.utcnow(),
        )
        budget = Budget(id=10, chantier_id=100, montant_initial_ht=Decimal("500000"))
        self.mock_avenant_repo.find_by_id.return_value = avenant
        self.mock_budget_repo.find_by_id.return_value = budget

        self.use_case.execute(avenant_id=1, deleted_by=5)

        self.mock_avenant_repo.delete.assert_called_once_with(1, 5)
        self.mock_journal.save.assert_called_once()

    def test_delete_avenant_not_found(self):
        """Test: erreur si avenant non trouve."""
        self.mock_avenant_repo.find_by_id.return_value = None

        with pytest.raises(AvenantNotFoundError):
            self.use_case.execute(avenant_id=999, deleted_by=5)

    def test_delete_avenant_valide(self):
        """Test: erreur si avenant deja valide (soft delete interdit)."""
        avenant = AvenantBudgetaire(
            id=1,
            budget_id=10,
            numero="AVN-2026-01",
            motif="Test",
            montant_ht=Decimal("10000"),
            statut="valide",
            created_at=datetime.utcnow(),
        )
        self.mock_avenant_repo.find_by_id.return_value = avenant

        with pytest.raises(AvenantAlreadyValideError):
            self.use_case.execute(avenant_id=1, deleted_by=5)


class TestListAvenantsUseCase:
    """Tests pour le use case de listage des avenants."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_avenant_repo = Mock(spec=AvenantRepository)
        self.use_case = ListAvenantsUseCase(
            avenant_repository=self.mock_avenant_repo,
        )

    def test_list_avenants_success(self):
        """Test: listage reussi des avenants d'un budget."""
        avenants = [
            AvenantBudgetaire(
                id=1,
                budget_id=10,
                numero="AVN-2026-01",
                motif="Avenant 1",
                montant_ht=Decimal("10000"),
                created_at=datetime.utcnow(),
            ),
            AvenantBudgetaire(
                id=2,
                budget_id=10,
                numero="AVN-2026-02",
                motif="Avenant 2",
                montant_ht=Decimal("5000"),
                created_at=datetime.utcnow(),
            ),
        ]
        self.mock_avenant_repo.find_by_budget_id.return_value = avenants

        result = self.use_case.execute(budget_id=10)

        assert len(result) == 2
        assert result[0].numero == "AVN-2026-01"
        assert result[1].numero == "AVN-2026-02"
        self.mock_avenant_repo.find_by_budget_id.assert_called_once_with(10)

    def test_list_avenants_vide(self):
        """Test: liste vide si aucun avenant."""
        self.mock_avenant_repo.find_by_budget_id.return_value = []

        result = self.use_case.execute(budget_id=10)

        assert len(result) == 0


class TestGetAvenantUseCase:
    """Tests pour le use case de recuperation d'un avenant."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_avenant_repo = Mock(spec=AvenantRepository)
        self.use_case = GetAvenantUseCase(
            avenant_repository=self.mock_avenant_repo,
        )

    def test_get_avenant_success(self):
        """Test: recuperation reussie d'un avenant."""
        avenant = AvenantBudgetaire(
            id=1,
            budget_id=10,
            numero="AVN-2026-01",
            motif="Test",
            montant_ht=Decimal("10000"),
            created_at=datetime.utcnow(),
        )
        self.mock_avenant_repo.find_by_id.return_value = avenant

        result = self.use_case.execute(1)

        assert result.id == 1
        assert result.numero == "AVN-2026-01"

    def test_get_avenant_not_found(self):
        """Test: erreur si avenant non trouve."""
        self.mock_avenant_repo.find_by_id.return_value = None

        with pytest.raises(AvenantNotFoundError):
            self.use_case.execute(999)
