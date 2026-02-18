"""Tests unitaires pour les Use Cases Situation du module Financier."""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, call

from modules.financier.domain.entities import (
    SituationTravaux,
    LigneSituation,
    Budget,
    LotBudgetaire,
)
from modules.financier.domain.repositories import (
    BudgetRepository,
    LotBudgetaireRepository,
    JournalFinancierRepository,
)
from modules.financier.domain.repositories.situation_repository import (
    SituationRepository,
    LigneSituationRepository,
)
from modules.financier.application.ports.event_bus import EventBus
from modules.financier.application.dtos.situation_dtos import (
    SituationCreateDTO,
    SituationUpdateDTO,
    LigneSituationCreateDTO,
)
from modules.financier.application.use_cases.situation_use_cases import (
    CreateSituationUseCase,
    UpdateSituationUseCase,
    SoumettreSituationUseCase,
    ValiderSituationUseCase,
    MarquerValideeClientUseCase,
    DeleteSituationUseCase,
    SituationNotFoundError,
    SituationWorkflowError,
)


class TestCreateSituationUseCase:
    """Tests pour le use case de creation de situation."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_situation_repo = Mock(spec=SituationRepository)
        self.mock_ligne_repo = Mock(spec=LigneSituationRepository)
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = CreateSituationUseCase(
            situation_repository=self.mock_situation_repo,
            ligne_repository=self.mock_ligne_repo,
            budget_repository=self.mock_budget_repo,
            lot_repository=self.mock_lot_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_create_situation_success(self):
        """Test: creation reussie d'une situation avec auto-numero et lignes."""
        budget = Budget(id=10, chantier_id=100, montant_initial_ht=Decimal("500000"))
        self.mock_budget_repo.find_by_id.return_value = budget
        self.mock_situation_repo.find_derniere_situation.return_value = None
        self.mock_situation_repo.next_numero_situation.return_value = 1

        lot1 = LotBudgetaire(
            id=1,
            budget_id=10,
            code_lot="LOT001",
            libelle="Gros oeuvre",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("500"),
        )
        lot2 = LotBudgetaire(
            id=2,
            budget_id=10,
            code_lot="LOT002",
            libelle="Second oeuvre",
            quantite_prevue=Decimal("50"),
            prix_unitaire_ht=Decimal("200"),
        )
        self.mock_lot_repo.find_by_budget_id.return_value = [lot1, lot2]

        def save_situation_side_effect(situation):
            situation.id = 1
            return situation

        self.mock_situation_repo.save.side_effect = save_situation_side_effect

        def save_all_lines(lignes):
            for i, l in enumerate(lignes):
                l.id = i + 1
            return lignes

        self.mock_ligne_repo.save_all.side_effect = save_all_lines

        dto = SituationCreateDTO(
            chantier_id=100,
            budget_id=10,
            periode_debut=date(2026, 1, 1),
            periode_fin=date(2026, 1, 31),
            lignes=[
                LigneSituationCreateDTO(
                    lot_budgetaire_id=1,
                    pourcentage_avancement=Decimal("30"),
                ),
                LigneSituationCreateDTO(
                    lot_budgetaire_id=2,
                    pourcentage_avancement=Decimal("50"),
                ),
            ],
        )

        result = self.use_case.execute(dto, created_by=5)

        assert result.id == 1
        assert result.chantier_id == 100
        assert result.statut == "brouillon"
        # Numero auto: SIT-YYYY-0001 (format 4 digits atomique)
        assert "SIT-" in result.numero
        assert "-0001" in result.numero
        assert len(result.lignes) == 2
        self.mock_situation_repo.save.assert_called()
        self.mock_ligne_repo.save_all.assert_called_once()
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_create_situation_budget_not_found(self):
        """Test: erreur si budget n'existe pas."""
        self.mock_budget_repo.find_by_id.return_value = None

        dto = SituationCreateDTO(
            chantier_id=100,
            budget_id=999,
            periode_debut=date(2026, 1, 1),
            periode_fin=date(2026, 1, 31),
        )

        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(dto, created_by=5)
        assert "999" in str(exc_info.value)


class TestSoumettreSituationUseCase:
    """Tests pour le use case de soumission de situation."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_situation_repo = Mock(spec=SituationRepository)
        self.mock_ligne_repo = Mock(spec=LigneSituationRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.use_case = SoumettreSituationUseCase(
            situation_repository=self.mock_situation_repo,
            ligne_repository=self.mock_ligne_repo,
            journal_repository=self.mock_journal,
        )

    def _make_situation(self, statut="brouillon"):
        """Cree une situation pour les tests."""
        return SituationTravaux(
            id=1,
            chantier_id=100,
            budget_id=10,
            numero="SIT-2026-01",
            statut=statut,
            montant_cumule_precedent_ht=Decimal("0"),
            montant_periode_ht=Decimal("0"),
            created_at=datetime.utcnow(),
        )

    def test_soumettre_success(self):
        """Test: soumission reussie brouillon -> en_validation."""
        situation = self._make_situation()
        self.mock_situation_repo.find_by_id.return_value = situation
        self.mock_situation_repo.save.return_value = situation
        self.mock_ligne_repo.find_by_situation_id.return_value = []

        result = self.use_case.execute(situation_id=1, submitted_by=5)

        assert result.statut == "en_validation"
        self.mock_situation_repo.save.assert_called_once()
        self.mock_journal.save.assert_called_once()

    def test_soumettre_not_found(self):
        """Test: erreur si situation non trouvee."""
        self.mock_situation_repo.find_by_id.return_value = None

        with pytest.raises(SituationNotFoundError):
            self.use_case.execute(situation_id=999, submitted_by=5)

    def test_soumettre_depuis_en_validation(self):
        """Test: erreur si deja en validation."""
        situation = self._make_situation(statut="en_validation")
        self.mock_situation_repo.find_by_id.return_value = situation

        with pytest.raises(SituationWorkflowError):
            self.use_case.execute(situation_id=1, submitted_by=5)


class TestValiderSituationUseCase:
    """Tests pour le use case de validation de situation."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_situation_repo = Mock(spec=SituationRepository)
        self.mock_ligne_repo = Mock(spec=LigneSituationRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = ValiderSituationUseCase(
            situation_repository=self.mock_situation_repo,
            ligne_repository=self.mock_ligne_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_valider_success(self):
        """Test: validation reussie en_validation -> emise."""
        situation = SituationTravaux(
            id=1,
            chantier_id=100,
            budget_id=10,
            numero="SIT-2026-01",
            statut="en_validation",
            montant_cumule_precedent_ht=Decimal("0"),
            montant_periode_ht=Decimal("100000"),
            montant_cumule_ht=Decimal("100000"),
            created_at=datetime.utcnow(),
        )
        self.mock_situation_repo.find_by_id.return_value = situation
        self.mock_situation_repo.save.return_value = situation
        self.mock_ligne_repo.find_by_situation_id.return_value = []

        result = self.use_case.execute(situation_id=1, validated_by=5)

        assert result.statut == "emise"
        self.mock_situation_repo.save.assert_called_once()
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_valider_not_found(self):
        """Test: erreur si situation non trouvee."""
        self.mock_situation_repo.find_by_id.return_value = None

        with pytest.raises(SituationNotFoundError):
            self.use_case.execute(situation_id=999, validated_by=5)

    def test_valider_depuis_brouillon(self):
        """Test: erreur si situation en brouillon."""
        situation = SituationTravaux(
            id=1,
            chantier_id=100,
            budget_id=10,
            numero="SIT-2026-01",
            statut="brouillon",
            montant_cumule_precedent_ht=Decimal("0"),
            montant_periode_ht=Decimal("0"),
            created_at=datetime.utcnow(),
        )
        self.mock_situation_repo.find_by_id.return_value = situation

        with pytest.raises(SituationWorkflowError):
            self.use_case.execute(situation_id=1, validated_by=5)


class TestMarquerValideeClientUseCase:
    """Tests pour le use case de validation client."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_situation_repo = Mock(spec=SituationRepository)
        self.mock_ligne_repo = Mock(spec=LigneSituationRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = MarquerValideeClientUseCase(
            situation_repository=self.mock_situation_repo,
            ligne_repository=self.mock_ligne_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_marquer_validee_client_success(self):
        """Test: validation client reussie emise -> validee."""
        situation = SituationTravaux(
            id=1,
            chantier_id=100,
            budget_id=10,
            numero="SIT-2026-01",
            statut="emise",
            montant_cumule_precedent_ht=Decimal("0"),
            montant_periode_ht=Decimal("100000"),
            montant_cumule_ht=Decimal("100000"),
            created_at=datetime.utcnow(),
        )
        self.mock_situation_repo.find_by_id.return_value = situation
        self.mock_situation_repo.save.return_value = situation
        self.mock_ligne_repo.find_by_situation_id.return_value = []

        result = self.use_case.execute(situation_id=1, marked_by=5)

        assert result.statut == "validee"
        self.mock_situation_repo.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_marquer_validee_client_not_found(self):
        """Test: erreur si situation non trouvee."""
        self.mock_situation_repo.find_by_id.return_value = None

        with pytest.raises(SituationNotFoundError):
            self.use_case.execute(situation_id=999, marked_by=5)

    def test_marquer_validee_client_depuis_brouillon(self):
        """Test: erreur si situation en brouillon."""
        situation = SituationTravaux(
            id=1,
            chantier_id=100,
            budget_id=10,
            numero="SIT-2026-01",
            statut="brouillon",
            montant_cumule_precedent_ht=Decimal("0"),
            montant_periode_ht=Decimal("0"),
            created_at=datetime.utcnow(),
        )
        self.mock_situation_repo.find_by_id.return_value = situation

        with pytest.raises(SituationWorkflowError):
            self.use_case.execute(situation_id=1, marked_by=5)


class TestUpdateSituationUseCase:
    """Tests pour le use case de mise a jour de situation."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_situation_repo = Mock(spec=SituationRepository)
        self.mock_ligne_repo = Mock(spec=LigneSituationRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.use_case = UpdateSituationUseCase(
            situation_repository=self.mock_situation_repo,
            ligne_repository=self.mock_ligne_repo,
            lot_repository=self.mock_lot_repo,
            journal_repository=self.mock_journal,
        )

    def test_update_situation_lignes(self):
        """Test: mise a jour des lignes d'avancement."""
        situation = SituationTravaux(
            id=1,
            chantier_id=100,
            budget_id=10,
            numero="SIT-2026-01",
            statut="brouillon",
            montant_cumule_precedent_ht=Decimal("0"),
            montant_periode_ht=Decimal("0"),
            created_at=datetime.utcnow(),
        )
        ligne = LigneSituation(
            id=1,
            situation_id=1,
            lot_budgetaire_id=10,
            pourcentage_avancement=Decimal("30"),
            montant_marche_ht=Decimal("100000"),
            montant_cumule_precedent_ht=Decimal("0"),
        )
        self.mock_situation_repo.find_by_id.return_value = situation
        self.mock_situation_repo.save.return_value = situation
        self.mock_ligne_repo.find_by_situation_id.return_value = [ligne]
        self.mock_ligne_repo.save_all.return_value = [ligne]

        dto = SituationUpdateDTO(
            lignes=[
                LigneSituationCreateDTO(
                    lot_budgetaire_id=10,
                    pourcentage_avancement=Decimal("60"),
                ),
            ],
        )

        result = self.use_case.execute(1, dto, updated_by=5)

        self.mock_situation_repo.save.assert_called_once()
        self.mock_ligne_repo.save_all.assert_called_once()

    def test_update_situation_not_found(self):
        """Test: erreur si situation non trouvee."""
        self.mock_situation_repo.find_by_id.return_value = None

        dto = SituationUpdateDTO(notes="Test")

        with pytest.raises(SituationNotFoundError):
            self.use_case.execute(999, dto, updated_by=5)

    def test_update_situation_non_brouillon(self):
        """Test: erreur si situation pas en brouillon."""
        situation = SituationTravaux(
            id=1,
            chantier_id=100,
            budget_id=10,
            numero="SIT-2026-01",
            statut="en_validation",
            montant_cumule_precedent_ht=Decimal("0"),
            montant_periode_ht=Decimal("0"),
            created_at=datetime.utcnow(),
        )
        self.mock_situation_repo.find_by_id.return_value = situation

        dto = SituationUpdateDTO(notes="Test")

        with pytest.raises(SituationWorkflowError):
            self.use_case.execute(1, dto, updated_by=5)


class TestDeleteSituationUseCase:
    """Tests pour le use case de suppression de situation."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_situation_repo = Mock(spec=SituationRepository)
        self.mock_ligne_repo = Mock(spec=LigneSituationRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.use_case = DeleteSituationUseCase(
            situation_repository=self.mock_situation_repo,
            ligne_repository=self.mock_ligne_repo,
            journal_repository=self.mock_journal,
        )

    def test_delete_brouillon_success(self):
        """Test: suppression reussie d'une situation brouillon."""
        situation = SituationTravaux(
            id=1,
            chantier_id=100,
            budget_id=10,
            numero="SIT-2026-01",
            statut="brouillon",
            montant_cumule_precedent_ht=Decimal("0"),
            montant_periode_ht=Decimal("0"),
            created_at=datetime.utcnow(),
        )
        self.mock_situation_repo.find_by_id.return_value = situation

        self.use_case.execute(situation_id=1, deleted_by=5)

        self.mock_ligne_repo.delete_by_situation_id.assert_called_once_with(1)
        self.mock_situation_repo.delete.assert_called_once_with(1, 5)
        self.mock_journal.save.assert_called_once()

    def test_delete_not_found(self):
        """Test: erreur si situation non trouvee."""
        self.mock_situation_repo.find_by_id.return_value = None

        with pytest.raises(SituationNotFoundError):
            self.use_case.execute(situation_id=999, deleted_by=5)

    def test_delete_non_brouillon(self):
        """Test: erreur si situation pas en brouillon."""
        situation = SituationTravaux(
            id=1,
            chantier_id=100,
            budget_id=10,
            numero="SIT-2026-01",
            statut="emise",
            montant_cumule_precedent_ht=Decimal("0"),
            montant_periode_ht=Decimal("0"),
            created_at=datetime.utcnow(),
        )
        self.mock_situation_repo.find_by_id.return_value = situation

        with pytest.raises(SituationWorkflowError):
            self.use_case.execute(situation_id=1, deleted_by=5)
