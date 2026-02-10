"""Tests unitaires pour les Use Cases Facture du module Financier."""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.financier.domain.entities import FactureClient, SituationTravaux
from modules.financier.domain.repositories import JournalFinancierRepository
from modules.financier.domain.repositories.facture_repository import FactureRepository
from modules.financier.domain.repositories.situation_repository import (
    SituationRepository,
)
from modules.financier.application.ports.event_bus import EventBus
from modules.financier.application.dtos.facture_dtos import FactureCreateDTO
from modules.financier.application.use_cases.facture_use_cases import (
    CreateFactureFromSituationUseCase,
    CreateFactureAcompteUseCase,
    EmettreFactureUseCase,
    EnvoyerFactureUseCase,
    MarquerPayeeFactureUseCase,
    AnnulerFactureUseCase,
    FactureNotFoundError,
    FactureWorkflowError,
    SituationNonValideeError,
)


class TestCreateFactureFromSituationUseCase:
    """Tests pour le use case de creation de facture depuis une situation."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_facture_repo = Mock(spec=FactureRepository)
        self.mock_situation_repo = Mock(spec=SituationRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = CreateFactureFromSituationUseCase(
            facture_repository=self.mock_facture_repo,
            situation_repository=self.mock_situation_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_create_from_situation_success(self):
        """Test: creation reussie depuis une situation validee."""
        situation = SituationTravaux(
            id=1,
            chantier_id=100,
            budget_id=10,
            numero="SIT-2026-01",
            statut="validee",
            montant_cumule_ht=Decimal("100000"),
            taux_tva=Decimal("20.00"),
            retenue_garantie_pct=Decimal("5.00"),
            created_at=datetime.utcnow(),
        )
        self.mock_situation_repo.find_by_id.return_value = situation
        self.mock_facture_repo.count_factures_year.return_value = 0

        def save_side_effect(facture):
            facture.id = 1
            return facture

        self.mock_facture_repo.save.side_effect = save_side_effect

        result = self.use_case.execute(situation_id=1, created_by=5)

        assert result.id == 1
        assert result.chantier_id == 100
        assert result.situation_id == 1
        assert result.type_facture == "situation"
        assert result.statut == "brouillon"
        assert result.montant_ht == "100000"
        # Numero auto FAC-YYYY-0001 (format 4 digits)
        assert "FAC-" in result.numero_facture
        assert "-0001" in result.numero_facture
        self.mock_facture_repo.save.assert_called_once()
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_create_from_situation_non_validee(self):
        """Test: erreur si situation non validee."""
        situation = SituationTravaux(
            id=1,
            chantier_id=100,
            budget_id=10,
            numero="SIT-2026-01",
            statut="emise",
            montant_cumule_ht=Decimal("100000"),
            created_at=datetime.utcnow(),
        )
        self.mock_situation_repo.find_by_id.return_value = situation

        with pytest.raises(SituationNonValideeError):
            self.use_case.execute(situation_id=1, created_by=5)

    def test_create_from_situation_brouillon(self):
        """Test: erreur si situation en brouillon."""
        situation = SituationTravaux(
            id=1,
            chantier_id=100,
            budget_id=10,
            numero="SIT-2026-01",
            statut="brouillon",
            montant_cumule_ht=Decimal("100000"),
            created_at=datetime.utcnow(),
        )
        self.mock_situation_repo.find_by_id.return_value = situation

        with pytest.raises(SituationNonValideeError):
            self.use_case.execute(situation_id=1, created_by=5)

    def test_create_from_situation_not_found(self):
        """Test: erreur si situation non trouvee."""
        self.mock_situation_repo.find_by_id.return_value = None

        with pytest.raises(ValueError):
            self.use_case.execute(situation_id=999, created_by=5)


class TestCreateFactureAcompteUseCase:
    """Tests pour le use case de creation de facture d'acompte."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_facture_repo = Mock(spec=FactureRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = CreateFactureAcompteUseCase(
            facture_repository=self.mock_facture_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_create_acompte_success(self):
        """Test: creation reussie d'une facture d'acompte."""
        self.mock_facture_repo.count_factures_year.return_value = 3

        def save_side_effect(facture):
            facture.id = 1
            return facture

        self.mock_facture_repo.save.side_effect = save_side_effect

        dto = FactureCreateDTO(
            chantier_id=100,
            type_facture="acompte",
            montant_ht=Decimal("50000"),
            taux_tva=Decimal("20.00"),
            retenue_garantie_pct=Decimal("5.00"),
            notes="Acompte initial",
        )

        result = self.use_case.execute(dto, created_by=5)

        assert result.id == 1
        assert result.chantier_id == 100
        assert result.type_facture == "acompte"
        assert result.situation_id is None
        assert result.statut == "brouillon"
        assert result.montant_ht == "50000"
        assert result.notes == "Acompte initial"
        # Numero auto FAC-YYYY-0004 (format 4 digits)
        assert "FAC-" in result.numero_facture
        assert "-0004" in result.numero_facture
        self.mock_facture_repo.save.assert_called_once()
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()


class TestEmettreFactureUseCase:
    """Tests pour le use case d'emission de facture."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_facture_repo = Mock(spec=FactureRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = EmettreFactureUseCase(
            facture_repository=self.mock_facture_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def _make_facture(self, statut="brouillon"):
        """Cree une facture pour les tests."""
        return FactureClient(
            id=1,
            chantier_id=100,
            numero_facture="FAC-2026-01",
            type_facture="situation",
            montant_ht=Decimal("100000"),
            taux_tva=Decimal("20.00"),
            montant_tva=Decimal("20000"),
            montant_ttc=Decimal("120000"),
            statut=statut,
            created_at=datetime.utcnow(),
        )

    def test_emettre_success(self):
        """Test: emission reussie brouillon -> emise."""
        facture = self._make_facture()
        self.mock_facture_repo.find_by_id.return_value = facture
        self.mock_facture_repo.save.return_value = facture

        result = self.use_case.execute(facture_id=1, emis_par=5)

        assert result.statut == "emise"
        assert result.date_emission is not None
        self.mock_facture_repo.save.assert_called_once()
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_emettre_not_found(self):
        """Test: erreur si facture non trouvee."""
        self.mock_facture_repo.find_by_id.return_value = None

        with pytest.raises(FactureNotFoundError):
            self.use_case.execute(facture_id=999, emis_par=5)

    def test_emettre_depuis_emise(self):
        """Test: erreur si facture deja emise."""
        facture = self._make_facture(statut="emise")
        self.mock_facture_repo.find_by_id.return_value = facture

        with pytest.raises(FactureWorkflowError):
            self.use_case.execute(facture_id=1, emis_par=5)


class TestMarquerPayeeFactureUseCase:
    """Tests pour le use case de paiement de facture."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_facture_repo = Mock(spec=FactureRepository)
        self.mock_situation_repo = Mock(spec=SituationRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = MarquerPayeeFactureUseCase(
            facture_repository=self.mock_facture_repo,
            situation_repository=self.mock_situation_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def _make_facture(self, statut="envoyee", situation_id=None):
        """Cree une facture pour les tests."""
        return FactureClient(
            id=1,
            chantier_id=100,
            situation_id=situation_id,
            numero_facture="FAC-2026-01",
            type_facture="situation",
            montant_ht=Decimal("100000"),
            taux_tva=Decimal("20.00"),
            montant_tva=Decimal("20000"),
            montant_ttc=Decimal("120000"),
            statut=statut,
            created_at=datetime.utcnow(),
        )

    def test_marquer_payee_success(self):
        """Test: paiement reussi envoyee -> payee."""
        facture = self._make_facture()
        self.mock_facture_repo.find_by_id.return_value = facture
        self.mock_facture_repo.save.return_value = facture

        result = self.use_case.execute(facture_id=1, paye_par=5)

        assert result.statut == "payee"
        self.mock_facture_repo.save.assert_called_once()
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_marquer_payee_avec_situation_validee(self):
        """Test: paiement marque la situation associee comme facturee."""
        facture = self._make_facture(situation_id=10)
        situation = SituationTravaux(
            id=10,
            chantier_id=100,
            budget_id=1,
            numero="SIT-2026-01",
            statut="validee",
            created_at=datetime.utcnow(),
        )
        self.mock_facture_repo.find_by_id.return_value = facture
        self.mock_facture_repo.save.return_value = facture
        self.mock_situation_repo.find_by_id.return_value = situation
        self.mock_situation_repo.save.return_value = situation

        result = self.use_case.execute(facture_id=1, paye_par=5)

        assert result.statut == "payee"
        # Verifier que la situation est passee en facturee
        assert situation.statut == "facturee"
        self.mock_situation_repo.save.assert_called_once()

    def test_marquer_payee_not_found(self):
        """Test: erreur si facture non trouvee."""
        self.mock_facture_repo.find_by_id.return_value = None

        with pytest.raises(FactureNotFoundError):
            self.use_case.execute(facture_id=999, paye_par=5)

    def test_marquer_payee_depuis_brouillon(self):
        """Test: erreur si facture en brouillon."""
        facture = self._make_facture(statut="brouillon")
        self.mock_facture_repo.find_by_id.return_value = facture

        with pytest.raises(FactureWorkflowError):
            self.use_case.execute(facture_id=1, paye_par=5)


class TestAnnulerFactureUseCase:
    """Tests pour le use case d'annulation de facture."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_facture_repo = Mock(spec=FactureRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.use_case = AnnulerFactureUseCase(
            facture_repository=self.mock_facture_repo,
            journal_repository=self.mock_journal,
        )

    def _make_facture(self, statut="brouillon"):
        """Cree une facture pour les tests."""
        return FactureClient(
            id=1,
            chantier_id=100,
            numero_facture="FAC-2026-01",
            type_facture="situation",
            montant_ht=Decimal("100000"),
            taux_tva=Decimal("20.00"),
            montant_tva=Decimal("20000"),
            montant_ttc=Decimal("120000"),
            statut=statut,
            created_at=datetime.utcnow(),
        )

    def test_annuler_brouillon_success(self):
        """Test: annulation reussie d'un brouillon."""
        facture = self._make_facture(statut="brouillon")
        self.mock_facture_repo.find_by_id.return_value = facture
        self.mock_facture_repo.save.return_value = facture

        result = self.use_case.execute(facture_id=1, annule_par=5)

        assert result.statut == "annulee"
        self.mock_facture_repo.save.assert_called_once()
        self.mock_journal.save.assert_called_once()

    def test_annuler_emise_success(self):
        """Test: annulation reussie d'une facture emise."""
        facture = self._make_facture(statut="emise")
        self.mock_facture_repo.find_by_id.return_value = facture
        self.mock_facture_repo.save.return_value = facture

        result = self.use_case.execute(facture_id=1, annule_par=5)

        assert result.statut == "annulee"

    def test_annuler_not_found(self):
        """Test: erreur si facture non trouvee."""
        self.mock_facture_repo.find_by_id.return_value = None

        with pytest.raises(FactureNotFoundError):
            self.use_case.execute(facture_id=999, annule_par=5)

    def test_annuler_envoyee(self):
        """Test: erreur si facture envoyee."""
        facture = self._make_facture(statut="envoyee")
        self.mock_facture_repo.find_by_id.return_value = facture

        with pytest.raises(FactureWorkflowError):
            self.use_case.execute(facture_id=1, annule_par=5)

    def test_annuler_payee(self):
        """Test: erreur si facture payee."""
        facture = self._make_facture(statut="payee")
        self.mock_facture_repo.find_by_id.return_value = facture

        with pytest.raises(FactureWorkflowError):
            self.use_case.execute(facture_id=1, annule_par=5)
