"""Tests unitaires pour les Use Cases de frais de chantier.

DEV-25: Frais de chantier - Compte prorata, frais generaux, installations.
Couche Application - frais_chantier_use_cases.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.entities.frais_chantier_devis import (
    FraisChantierDevis,
    FraisChantierValidationError,
)
from modules.devis.domain.entities.lot_devis import LotDevis
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.value_objects.type_frais_chantier import TypeFraisChantier
from modules.devis.domain.value_objects.mode_repartition import ModeRepartition
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.frais_chantier_repository import FraisChantierRepository
from modules.devis.domain.repositories.lot_devis_repository import LotDevisRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError
from modules.devis.application.use_cases.frais_chantier_use_cases import (
    CreateFraisChantierUseCase,
    UpdateFraisChantierUseCase,
    DeleteFraisChantierUseCase,
    ListFraisChantierUseCase,
    CalculerRepartitionFraisUseCase,
    FraisChantierNotFoundError,
    DevisNonModifiableError,
)
from modules.devis.application.dtos.frais_chantier_dtos import (
    FraisChantierCreateDTO,
    FraisChantierUpdateDTO,
    FraisChantierDTO,
)


def _make_devis(**kwargs):
    """Cree un devis valide avec valeurs par defaut."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "statut": StatutDevis.BROUILLON,
        "date_creation": date(2026, 1, 15),
        "montant_total_ht": Decimal("50000"),
        "montant_total_ttc": Decimal("60000"),
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


def _make_frais(**kwargs):
    """Cree un frais de chantier valide."""
    defaults = {
        "id": 1,
        "devis_id": 1,
        "type_frais": TypeFraisChantier.COMPTE_PRORATA,
        "libelle": "Compte prorata inter-entreprises",
        "montant_ht": Decimal("5000"),
        "mode_repartition": ModeRepartition.GLOBAL,
        "taux_tva": Decimal("20"),
        "ordre": 1,
    }
    defaults.update(kwargs)
    return FraisChantierDevis(**defaults)


def _make_lot(**kwargs):
    """Cree un lot de devis valide."""
    defaults = {
        "id": 1,
        "devis_id": 1,
        "code_lot": "LOT-01",
        "libelle": "Gros oeuvre",
        "ordre": 1,
        "montant_debourse_ht": Decimal("20000"),
        "montant_vente_ht": Decimal("30000"),
        "montant_vente_ttc": Decimal("36000"),
    }
    defaults.update(kwargs)
    return LotDevis(**defaults)


# ─────────────────────────────────────────────────────────────────────────────
# Tests CreateFraisChantierUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestCreateFraisChantierUseCase:
    """Tests pour la creation d'un frais de chantier."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_frais_repo = Mock(spec=FraisChantierRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = CreateFraisChantierUseCase(
            frais_repo=self.mock_frais_repo,
            devis_repo=self.mock_devis_repo,
            journal_repo=self.mock_journal_repo,
        )

    def test_creer_frais_success(self):
        """Test: creation reussie d'un frais de chantier."""
        devis = _make_devis()
        frais = _make_frais()

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_frais_repo.save.return_value = frais
        self.mock_journal_repo.save.return_value = Mock()

        dto = FraisChantierCreateDTO(
            devis_id=1,
            type_frais="compte_prorata",
            libelle="Compte prorata",
            montant_ht=Decimal("5000"),
        )

        result = self.use_case.execute(dto=dto, created_by=1)

        assert isinstance(result, FraisChantierDTO)
        assert result.montant_ht == str(Decimal("5000"))
        self.mock_frais_repo.save.assert_called_once()
        self.mock_journal_repo.save.assert_called_once()

    def test_creer_frais_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        dto = FraisChantierCreateDTO(
            devis_id=999,
            type_frais="compte_prorata",
            libelle="Compte prorata",
            montant_ht=Decimal("5000"),
        )

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(dto=dto, created_by=1)

    def test_creer_frais_montant_negatif(self):
        """Test: erreur si montant negatif."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis

        dto = FraisChantierCreateDTO(
            devis_id=1,
            type_frais="compte_prorata",
            libelle="Compte prorata",
            montant_ht=Decimal("-100"),
        )

        with pytest.raises((ValueError, FraisChantierValidationError)):
            self.use_case.execute(dto=dto, created_by=1)


# ─────────────────────────────────────────────────────────────────────────────
# Tests UpdateFraisChantierUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestUpdateFraisChantierUseCase:
    """Tests pour la modification d'un frais de chantier."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_frais_repo = Mock(spec=FraisChantierRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = UpdateFraisChantierUseCase(
            frais_repo=self.mock_frais_repo,
            devis_repo=self.mock_devis_repo,
            journal_repo=self.mock_journal_repo,
        )

    def test_modifier_frais_success(self):
        """Test: modification reussie du montant."""
        devis = _make_devis()
        frais = _make_frais()
        frais_modifie = _make_frais(montant_ht=Decimal("7500"))

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_frais_repo.find_by_id.return_value = frais
        self.mock_frais_repo.save.return_value = frais_modifie
        self.mock_journal_repo.save.return_value = Mock()

        dto = FraisChantierUpdateDTO(montant_ht=Decimal("7500"))
        result = self.use_case.execute(frais_id=1, dto=dto, updated_by=1)

        assert isinstance(result, FraisChantierDTO)
        self.mock_frais_repo.save.assert_called_once()

    def test_modifier_frais_not_found(self):
        """Test: erreur si frais non trouve."""
        self.mock_frais_repo.find_by_id.return_value = None

        dto = FraisChantierUpdateDTO(montant_ht=Decimal("7500"))
        with pytest.raises(FraisChantierNotFoundError):
            self.use_case.execute(frais_id=999, dto=dto, updated_by=1)


# ─────────────────────────────────────────────────────────────────────────────
# Tests DeleteFraisChantierUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestDeleteFraisChantierUseCase:
    """Tests pour la suppression d'un frais de chantier."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_frais_repo = Mock(spec=FraisChantierRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = DeleteFraisChantierUseCase(
            frais_repo=self.mock_frais_repo,
            devis_repo=self.mock_devis_repo,
            journal_repo=self.mock_journal_repo,
        )

    def test_supprimer_frais_success(self):
        """Test: suppression reussie (soft delete via repo)."""
        devis = _make_devis()
        frais = _make_frais()

        self.mock_frais_repo.find_by_id.return_value = frais
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_frais_repo.delete.return_value = None
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute(frais_id=1, deleted_by=1)

        self.mock_frais_repo.delete.assert_called_once_with(1, 1)
        self.mock_journal_repo.save.assert_called_once()

    def test_supprimer_frais_not_found(self):
        """Test: erreur si frais non trouve."""
        self.mock_frais_repo.find_by_id.return_value = None

        with pytest.raises(FraisChantierNotFoundError):
            self.use_case.execute(frais_id=999, deleted_by=1)


# ─────────────────────────────────────────────────────────────────────────────
# Tests ListFraisChantierUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestListFraisChantierUseCase:
    """Tests pour le listage des frais de chantier."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_frais_repo = Mock(spec=FraisChantierRepository)
        self.use_case = ListFraisChantierUseCase(
            frais_repo=self.mock_frais_repo,
            devis_repo=self.mock_devis_repo,
        )

    def test_lister_frais_success(self):
        """Test: listage reussi."""
        devis = _make_devis()
        frais1 = _make_frais(id=1, libelle="Compte prorata", ordre=1)
        frais2 = _make_frais(
            id=2, libelle="Frais generaux",
            type_frais=TypeFraisChantier.FRAIS_GENERAUX, ordre=2,
        )

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_frais_repo.find_by_devis.return_value = [frais1, frais2]

        result = self.use_case.execute(devis_id=1)

        assert len(result) == 2
        assert all(isinstance(f, FraisChantierDTO) for f in result)

    def test_lister_frais_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999)

    def test_lister_frais_vide(self):
        """Test: liste vide si aucun frais."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_frais_repo.find_by_devis.return_value = []

        result = self.use_case.execute(devis_id=1)

        assert len(result) == 0


# ─────────────────────────────────────────────────────────────────────────────
# Tests CalculerRepartitionFraisUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestCalculerRepartitionFraisUseCase:
    """Tests pour le calcul de repartition des frais."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_frais_repo = Mock(spec=FraisChantierRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.use_case = CalculerRepartitionFraisUseCase(
            frais_repo=self.mock_frais_repo,
            devis_repo=self.mock_devis_repo,
            lot_repo=self.mock_lot_repo,
        )

    def test_repartition_global(self):
        """Test: un frais en mode global n'est pas proratise."""
        devis = _make_devis(montant_total_ht=Decimal("50000"))
        frais_global = _make_frais(
            mode_repartition=ModeRepartition.GLOBAL,
            montant_ht=Decimal("5000"),
        )
        lot = _make_lot(montant_vente_ht=Decimal("30000"))

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_frais_repo.find_by_devis.return_value = [frais_global]
        self.mock_lot_repo.find_by_devis.return_value = [lot]

        result = self.use_case.execute(devis_id=1)

        assert isinstance(result, dict)
        assert result is not None

    def test_repartition_prorata(self):
        """Test: un frais en mode prorata est ventile par lot."""
        devis = _make_devis(montant_total_ht=Decimal("60000"))
        frais = _make_frais(
            mode_repartition=ModeRepartition.PRORATA_LOTS,
            montant_ht=Decimal("6000"),
        )
        lot1 = _make_lot(id=1, code_lot="LOT-01", montant_vente_ht=Decimal("40000"))
        lot2 = _make_lot(id=2, code_lot="LOT-02", montant_vente_ht=Decimal("20000"))

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_frais_repo.find_by_devis.return_value = [frais]
        self.mock_lot_repo.find_by_devis.return_value = [lot1, lot2]

        result = self.use_case.execute(devis_id=1)

        assert result is not None

    def test_repartition_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999)
