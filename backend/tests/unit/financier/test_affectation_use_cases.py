"""Tests unitaires pour les Use Cases Affectation du module Financier."""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch

from modules.financier.domain.entities import AffectationTacheLot, LotBudgetaire
from modules.financier.domain.entities.affectation_tache_lot import AffectationTacheLot
from modules.financier.domain.repositories import (
    LotBudgetaireRepository,
    JournalFinancierRepository,
    AffectationRepository,
    AvancementTacheRepository,
)
from modules.financier.domain.value_objects.avancement_tache import AvancementTache
from modules.financier.application.ports.event_bus import EventBus
from modules.financier.application.dtos.affectation_dtos import (
    AffectationCreateDTO,
    AffectationDTO,
    SuiviAffectationDTO,
)
from modules.financier.application.use_cases.affectation_use_cases import (
    CreateAffectationUseCase,
    DeleteAffectationUseCase,
    ListAffectationsByChantierUseCase,
    ListAffectationsByTacheUseCase,
    GetSuiviAvancementFinancierUseCase,
    AffectationNotFoundError,
    AffectationAlreadyExistsError,
    LotBudgetaireNotFoundForAffectationError,
)


class TestCreateAffectationUseCase:
    """Tests pour le use case de creation d'affectation."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_affectation_repo = Mock(spec=AffectationRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = CreateAffectationUseCase(
            affectation_repository=self.mock_affectation_repo,
            lot_repository=self.mock_lot_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_create_affectation_success(self):
        """Test: creation reussie d'une affectation tache/lot."""
        lot = LotBudgetaire(
            id=20,
            budget_id=1,
            code_lot="LOT-001",
            libelle="Terrassement",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
        )
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_affectation_repo.find_by_tache_and_lot.return_value = None

        def save_side_effect(affectation):
            affectation.id = 1
            return affectation

        self.mock_affectation_repo.save.side_effect = save_side_effect

        dto = AffectationCreateDTO(
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
            pourcentage_affectation=Decimal("75"),
        )

        result = self.use_case.execute(dto, created_by=3)

        assert result.id == 1
        assert result.chantier_id == 5
        assert result.tache_id == 10
        assert result.lot_budgetaire_id == 20
        assert result.pourcentage_affectation == "75"
        self.mock_affectation_repo.save.assert_called_once()
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_create_affectation_default_pourcentage(self):
        """Test: creation avec pourcentage par defaut (100%)."""
        lot = LotBudgetaire(
            id=20,
            budget_id=1,
            code_lot="LOT-001",
            libelle="Terrassement",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
        )
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_affectation_repo.find_by_tache_and_lot.return_value = None

        def save_side_effect(affectation):
            affectation.id = 1
            return affectation

        self.mock_affectation_repo.save.side_effect = save_side_effect

        dto = AffectationCreateDTO(
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
        )

        result = self.use_case.execute(dto, created_by=3)

        assert result.pourcentage_affectation == "100"

    def test_create_affectation_lot_not_found(self):
        """Test: erreur si le lot budgetaire n'existe pas."""
        self.mock_lot_repo.find_by_id.return_value = None

        dto = AffectationCreateDTO(
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=999,
        )

        with pytest.raises(LotBudgetaireNotFoundForAffectationError) as exc_info:
            self.use_case.execute(dto, created_by=3)
        assert exc_info.value.lot_id == 999

    def test_create_affectation_already_exists(self):
        """Test: erreur si une affectation existe deja pour la meme tache/lot."""
        lot = LotBudgetaire(
            id=20,
            budget_id=1,
            code_lot="LOT-001",
            libelle="Terrassement",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
        )
        self.mock_lot_repo.find_by_id.return_value = lot
        existing = AffectationTacheLot(
            id=99,
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
        )
        self.mock_affectation_repo.find_by_tache_and_lot.return_value = existing

        dto = AffectationCreateDTO(
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
        )

        with pytest.raises(AffectationAlreadyExistsError) as exc_info:
            self.use_case.execute(dto, created_by=3)
        assert exc_info.value.tache_id == 10
        assert exc_info.value.lot_id == 20

    def test_create_affectation_publishes_event(self):
        """Test: un event AffectationCreated est publie apres creation."""
        lot = LotBudgetaire(
            id=20,
            budget_id=1,
            code_lot="LOT-001",
            libelle="Terrassement",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
        )
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_affectation_repo.find_by_tache_and_lot.return_value = None

        def save_side_effect(affectation):
            affectation.id = 1
            return affectation

        self.mock_affectation_repo.save.side_effect = save_side_effect

        dto = AffectationCreateDTO(
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
        )
        self.use_case.execute(dto, created_by=3)

        event = self.mock_event_bus.publish.call_args[0][0]
        assert event.affectation_id == 1
        assert event.chantier_id == 5
        assert event.tache_id == 10
        assert event.lot_budgetaire_id == 20
        assert event.created_by == 3

    def test_create_affectation_journal_entry(self):
        """Test: une entree de journal est creee apres creation."""
        lot = LotBudgetaire(
            id=20,
            budget_id=1,
            code_lot="LOT-001",
            libelle="Terrassement",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
        )
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_affectation_repo.find_by_tache_and_lot.return_value = None

        def save_side_effect(affectation):
            affectation.id = 1
            return affectation

        self.mock_affectation_repo.save.side_effect = save_side_effect

        dto = AffectationCreateDTO(
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
        )
        self.use_case.execute(dto, created_by=3)

        journal_entry = self.mock_journal.save.call_args[0][0]
        assert journal_entry.entite_type == "affectation"
        assert journal_entry.action == "creation"
        assert journal_entry.chantier_id == 5
        assert journal_entry.auteur_id == 3


class TestDeleteAffectationUseCase:
    """Tests pour le use case de suppression d'affectation."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_affectation_repo = Mock(spec=AffectationRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = DeleteAffectationUseCase(
            affectation_repository=self.mock_affectation_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_delete_affectation_success(self):
        """Test: suppression reussie d'une affectation."""
        affectation = AffectationTacheLot(
            id=1,
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
        )
        self.mock_affectation_repo.find_by_id.return_value = affectation

        self.use_case.execute(affectation_id=1, deleted_by=3)

        self.mock_affectation_repo.delete.assert_called_once_with(1)
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_delete_affectation_not_found(self):
        """Test: erreur si affectation non trouvee."""
        self.mock_affectation_repo.find_by_id.return_value = None

        with pytest.raises(AffectationNotFoundError) as exc_info:
            self.use_case.execute(affectation_id=999, deleted_by=3)
        assert exc_info.value.affectation_id == 999

    def test_delete_affectation_publishes_event(self):
        """Test: un event AffectationDeleted est publie apres suppression."""
        affectation = AffectationTacheLot(
            id=1,
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
        )
        self.mock_affectation_repo.find_by_id.return_value = affectation

        self.use_case.execute(affectation_id=1, deleted_by=3)

        event = self.mock_event_bus.publish.call_args[0][0]
        assert event.affectation_id == 1
        assert event.chantier_id == 5
        assert event.tache_id == 10
        assert event.lot_budgetaire_id == 20
        assert event.deleted_by == 3

    def test_delete_affectation_journal_entry(self):
        """Test: une entree de journal est creee apres suppression."""
        affectation = AffectationTacheLot(
            id=1,
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
        )
        self.mock_affectation_repo.find_by_id.return_value = affectation

        self.use_case.execute(affectation_id=1, deleted_by=3)

        journal_entry = self.mock_journal.save.call_args[0][0]
        assert journal_entry.entite_type == "affectation"
        assert journal_entry.action == "suppression"
        assert journal_entry.auteur_id == 3


class TestListAffectationsByChantierUseCase:
    """Tests pour le use case de listage des affectations par chantier."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_affectation_repo = Mock(spec=AffectationRepository)
        self.use_case = ListAffectationsByChantierUseCase(
            affectation_repository=self.mock_affectation_repo,
        )

    def test_list_affectations_success(self):
        """Test: listage reussi des affectations d'un chantier."""
        affectations = [
            AffectationTacheLot(
                id=1,
                chantier_id=5,
                tache_id=10,
                lot_budgetaire_id=20,
                pourcentage_affectation=Decimal("100"),
                created_at=datetime.utcnow(),
            ),
            AffectationTacheLot(
                id=2,
                chantier_id=5,
                tache_id=11,
                lot_budgetaire_id=21,
                pourcentage_affectation=Decimal("50"),
                created_at=datetime.utcnow(),
            ),
        ]
        self.mock_affectation_repo.find_by_chantier.return_value = affectations

        result = self.use_case.execute(chantier_id=5)

        assert len(result) == 2
        assert result[0].tache_id == 10
        assert result[1].tache_id == 11
        self.mock_affectation_repo.find_by_chantier.assert_called_once_with(5)

    def test_list_affectations_vide(self):
        """Test: liste vide si aucune affectation."""
        self.mock_affectation_repo.find_by_chantier.return_value = []

        result = self.use_case.execute(chantier_id=5)

        assert len(result) == 0


class TestListAffectationsByTacheUseCase:
    """Tests pour le use case de listage des affectations par tache."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_affectation_repo = Mock(spec=AffectationRepository)
        self.use_case = ListAffectationsByTacheUseCase(
            affectation_repository=self.mock_affectation_repo,
        )

    def test_list_affectations_by_tache_success(self):
        """Test: listage reussi des affectations d'une tache."""
        affectations = [
            AffectationTacheLot(
                id=1,
                chantier_id=5,
                tache_id=10,
                lot_budgetaire_id=20,
                pourcentage_affectation=Decimal("60"),
                created_at=datetime.utcnow(),
            ),
            AffectationTacheLot(
                id=2,
                chantier_id=5,
                tache_id=10,
                lot_budgetaire_id=21,
                pourcentage_affectation=Decimal("40"),
                created_at=datetime.utcnow(),
            ),
        ]
        self.mock_affectation_repo.find_by_tache.return_value = affectations

        result = self.use_case.execute(tache_id=10)

        assert len(result) == 2
        assert result[0].lot_budgetaire_id == 20
        assert result[1].lot_budgetaire_id == 21
        self.mock_affectation_repo.find_by_tache.assert_called_once_with(10)

    def test_list_affectations_by_tache_vide(self):
        """Test: liste vide si aucune affectation pour la tache."""
        self.mock_affectation_repo.find_by_tache.return_value = []

        result = self.use_case.execute(tache_id=10)

        assert len(result) == 0


class TestGetSuiviAvancementFinancierUseCase:
    """Tests pour le use case de suivi croise avancement/financier."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_affectation_repo = Mock(spec=AffectationRepository)
        self.mock_avancement_repo = Mock(spec=AvancementTacheRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)
        self.use_case = GetSuiviAvancementFinancierUseCase(
            affectation_repository=self.mock_affectation_repo,
            avancement_repository=self.mock_avancement_repo,
            lot_repository=self.mock_lot_repo,
        )

    def test_suivi_success(self):
        """Test: suivi croise reussi avec avancement et montants."""
        affectation = AffectationTacheLot(
            id=1,
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
            pourcentage_affectation=Decimal("100"),
        )
        self.mock_affectation_repo.find_by_chantier.return_value = [affectation]

        avancement = AvancementTache(
            tache_id=10,
            titre="Terrassement zone A",
            statut="en_cours",
            heures_estimees=Decimal("40"),
            heures_realisees=Decimal("25"),
            quantite_estimee=Decimal("100"),
            quantite_realisee=Decimal("60"),
            progression_pct=Decimal("60"),
        )
        self.mock_avancement_repo.get_avancements_chantier.return_value = [avancement]

        lot = LotBudgetaire(
            id=20,
            budget_id=1,
            code_lot="LOT-001",
            libelle="Terrassement",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
        )
        self.mock_lot_repo.find_by_id.return_value = lot

        result = self.use_case.execute(chantier_id=5)

        assert len(result) == 1
        suivi = result[0]
        assert suivi.affectation_id == 1
        assert suivi.tache_id == 10
        assert suivi.tache_titre == "Terrassement zone A"
        assert suivi.tache_statut == "en_cours"
        assert suivi.tache_progression_pct == "60"
        assert suivi.lot_budgetaire_id == 20
        assert suivi.lot_code == "LOT-001"
        assert suivi.lot_libelle == "Terrassement"
        # lot_montant = 100 * 50 = 5000, affectation 100% => montant_affecte = 5000
        assert suivi.lot_montant_prevu_ht == "5000.00"
        assert suivi.montant_affecte_ht == "5000.00"

    def test_suivi_pourcentage_partiel(self):
        """Test: suivi avec pourcentage d'affectation partiel (50%)."""
        affectation = AffectationTacheLot(
            id=1,
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
            pourcentage_affectation=Decimal("50"),
        )
        self.mock_affectation_repo.find_by_chantier.return_value = [affectation]

        avancement = AvancementTache(
            tache_id=10,
            titre="Terrassement zone A",
            statut="en_cours",
            heures_estimees=Decimal("40"),
            heures_realisees=Decimal("25"),
            quantite_estimee=Decimal("100"),
            quantite_realisee=Decimal("60"),
            progression_pct=Decimal("60"),
        )
        self.mock_avancement_repo.get_avancements_chantier.return_value = [avancement]

        lot = LotBudgetaire(
            id=20,
            budget_id=1,
            code_lot="LOT-001",
            libelle="Terrassement",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
        )
        self.mock_lot_repo.find_by_id.return_value = lot

        result = self.use_case.execute(chantier_id=5)

        assert len(result) == 1
        # lot_montant = 5000, affectation 50% => montant_affecte = 2500
        assert result[0].montant_affecte_ht == "2500.00"

    def test_suivi_no_affectations(self):
        """Test: liste vide si aucune affectation pour le chantier."""
        self.mock_affectation_repo.find_by_chantier.return_value = []

        result = self.use_case.execute(chantier_id=5)

        assert len(result) == 0

    def test_suivi_tache_sans_avancement(self):
        """Test: suivi avec tache inconnue (pas d'avancement)."""
        affectation = AffectationTacheLot(
            id=1,
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
            pourcentage_affectation=Decimal("100"),
        )
        self.mock_affectation_repo.find_by_chantier.return_value = [affectation]
        self.mock_avancement_repo.get_avancements_chantier.return_value = []

        lot = LotBudgetaire(
            id=20,
            budget_id=1,
            code_lot="LOT-001",
            libelle="Terrassement",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
        )
        self.mock_lot_repo.find_by_id.return_value = lot

        result = self.use_case.execute(chantier_id=5)

        assert len(result) == 1
        assert result[0].tache_titre == "Tache inconnue"
        assert result[0].tache_statut == "inconnu"
        assert result[0].tache_progression_pct == "0"

    def test_suivi_lot_not_found_skipped(self):
        """Test: les affectations avec lot introuvable sont ignorees."""
        affectation = AffectationTacheLot(
            id=1,
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=999,
            pourcentage_affectation=Decimal("100"),
        )
        self.mock_affectation_repo.find_by_chantier.return_value = [affectation]
        self.mock_avancement_repo.get_avancements_chantier.return_value = []
        self.mock_lot_repo.find_by_id.return_value = None

        result = self.use_case.execute(chantier_id=5)

        assert len(result) == 0

    def test_suivi_multiple_affectations(self):
        """Test: suivi croise avec plusieurs affectations."""
        affectations = [
            AffectationTacheLot(
                id=1,
                chantier_id=5,
                tache_id=10,
                lot_budgetaire_id=20,
                pourcentage_affectation=Decimal("100"),
            ),
            AffectationTacheLot(
                id=2,
                chantier_id=5,
                tache_id=11,
                lot_budgetaire_id=21,
                pourcentage_affectation=Decimal("75"),
            ),
        ]
        self.mock_affectation_repo.find_by_chantier.return_value = affectations

        avancements = [
            AvancementTache(
                tache_id=10,
                titre="Terrassement",
                statut="terminee",
                heures_estimees=Decimal("40"),
                heures_realisees=Decimal("40"),
                quantite_estimee=Decimal("100"),
                quantite_realisee=Decimal("100"),
                progression_pct=Decimal("100"),
            ),
            AvancementTache(
                tache_id=11,
                titre="Maconnerie",
                statut="en_cours",
                heures_estimees=Decimal("80"),
                heures_realisees=Decimal("30"),
                quantite_estimee=Decimal("200"),
                quantite_realisee=Decimal("80"),
                progression_pct=Decimal("40"),
            ),
        ]
        self.mock_avancement_repo.get_avancements_chantier.return_value = avancements

        lot1 = LotBudgetaire(
            id=20,
            budget_id=1,
            code_lot="LOT-001",
            libelle="Terrassement",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
        )
        lot2 = LotBudgetaire(
            id=21,
            budget_id=1,
            code_lot="LOT-002",
            libelle="Maconnerie",
            quantite_prevue=Decimal("200"),
            prix_unitaire_ht=Decimal("80"),
        )
        self.mock_lot_repo.find_by_id.side_effect = lambda lid: {20: lot1, 21: lot2}.get(lid)

        result = self.use_case.execute(chantier_id=5)

        assert len(result) == 2
        assert result[0].tache_titre == "Terrassement"
        assert result[0].tache_progression_pct == "100"
        assert result[0].montant_affecte_ht == "5000.00"
        assert result[1].tache_titre == "Maconnerie"
        assert result[1].tache_progression_pct == "40"
        # lot2 montant = 200 * 80 = 16000, affectation 75% => 12000
        assert result[1].montant_affecte_ht == "12000.00"
