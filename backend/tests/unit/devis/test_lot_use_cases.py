"""Tests unitaires pour les Use Cases de gestion des lots.

DEV-03: Creation devis structure - Arborescence par lots.
Couche Application - lot_use_cases.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.entities.lot_devis import LotDevis
from modules.devis.domain.entities.journal_devis import JournalDevis
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.lot_devis_repository import LotDevisRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.lot_use_cases import (
    CreateLotDevisUseCase,
    UpdateLotDevisUseCase,
    DeleteLotDevisUseCase,
    ReorderLotsUseCase,
    LotDevisNotFoundError,
)
from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError
from modules.devis.application.dtos.lot_dtos import (
    LotDevisCreateDTO,
    LotDevisUpdateDTO,
    LotDevisDTO,
)


def _make_devis(**kwargs):
    """Cree un devis valide."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "objet": "Renovation",
        "statut": StatutDevis.BROUILLON,
        "date_creation": date(2026, 1, 15),
        "created_at": datetime(2026, 1, 15),
        "updated_at": datetime(2026, 1, 15),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


def _make_lot(**kwargs):
    """Cree un lot valide."""
    defaults = {
        "id": 10,
        "devis_id": 1,
        "code_lot": "LOT-001",
        "libelle": "Gros oeuvre",
        "ordre": 1,
    }
    defaults.update(kwargs)
    return LotDevis(**defaults)


class TestCreateLotDevisUseCase:
    """Tests pour la creation de lots."""

    def setup_method(self):
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = CreateLotDevisUseCase(
            lot_repository=self.mock_lot_repo,
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_create_lot_success(self):
        """Test: creation de lot reussie."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        saved_lot = _make_lot()
        self.mock_lot_repo.save.return_value = saved_lot
        self.mock_journal_repo.save.return_value = Mock()

        dto = LotDevisCreateDTO(devis_id=1, titre="Gros oeuvre", numero="LOT-001", ordre=1)
        result = self.use_case.execute(dto, created_by=1)

        assert isinstance(result, LotDevisDTO)
        assert result.titre == "Gros oeuvre"
        self.mock_lot_repo.save.assert_called_once()

    def test_create_lot_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        dto = LotDevisCreateDTO(devis_id=999, titre="Lot")
        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(dto, created_by=1)

    def test_create_lot_auto_code(self):
        """Test: code auto-genere si non fourni."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.save.return_value = _make_lot(code_lot="LOT-000")
        self.mock_journal_repo.save.return_value = Mock()

        dto = LotDevisCreateDTO(devis_id=1, titre="Lot auto", numero="", ordre=0)
        self.use_case.execute(dto, created_by=1)

        lot_saved = self.mock_lot_repo.save.call_args[0][0]
        assert lot_saved.code_lot == "LOT-000"

    def test_create_lot_avec_marge(self):
        """Test: creation de lot avec marge specifique."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        saved_lot = _make_lot(taux_marge_lot=Decimal("20"))
        self.mock_lot_repo.save.return_value = saved_lot
        self.mock_journal_repo.save.return_value = Mock()

        dto = LotDevisCreateDTO(
            devis_id=1, titre="Electricite", marge_lot_pct=Decimal("20")
        )
        result = self.use_case.execute(dto, created_by=1)

        assert result.marge_lot_pct == "20"

    def test_create_lot_journal_entry(self):
        """Test: entree de journal pour creation de lot."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.save.return_value = _make_lot()
        self.mock_journal_repo.save.return_value = Mock()

        dto = LotDevisCreateDTO(devis_id=1, titre="Lot Journal")
        self.use_case.execute(dto, created_by=3)

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert journal_call.action == "ajout_lot"
        assert journal_call.auteur_id == 3


class TestUpdateLotDevisUseCase:
    """Tests pour la mise a jour de lots."""

    def setup_method(self):
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = UpdateLotDevisUseCase(
            lot_repository=self.mock_lot_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_update_lot_success(self):
        """Test: mise a jour reussie."""
        lot = _make_lot()
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_lot_repo.save.return_value = lot
        self.mock_journal_repo.save.return_value = Mock()

        dto = LotDevisUpdateDTO(titre="Nouveau titre")
        result = self.use_case.execute(lot_id=10, dto=dto, updated_by=1)

        assert isinstance(result, LotDevisDTO)
        self.mock_lot_repo.save.assert_called_once()

    def test_update_lot_not_found(self):
        """Test: erreur si lot non trouve."""
        self.mock_lot_repo.find_by_id.return_value = None

        dto = LotDevisUpdateDTO(titre="Nouveau")
        with pytest.raises(LotDevisNotFoundError) as exc_info:
            self.use_case.execute(lot_id=999, dto=dto, updated_by=1)
        assert exc_info.value.lot_id == 999

    def test_update_lot_multiple_fields(self):
        """Test: mise a jour de plusieurs champs."""
        lot = _make_lot()
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_lot_repo.save.return_value = lot
        self.mock_journal_repo.save.return_value = Mock()

        dto = LotDevisUpdateDTO(
            titre="Nouveau titre",
            numero="LOT-002",
            ordre=5,
            marge_lot_pct=Decimal("25"),
        )
        self.use_case.execute(lot_id=10, dto=dto, updated_by=1)

        assert lot.libelle == "Nouveau titre"
        assert lot.code_lot == "LOT-002"
        assert lot.ordre == 5
        assert lot.taux_marge_lot == Decimal("25")


class TestDeleteLotDevisUseCase:
    """Tests pour la suppression de lots."""

    def setup_method(self):
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = DeleteLotDevisUseCase(
            lot_repository=self.mock_lot_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_delete_lot_success(self):
        """Test: suppression reussie."""
        lot = _make_lot()
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute(lot_id=10, deleted_by=1)

        self.mock_lot_repo.delete.assert_called_once_with(10)

    def test_delete_lot_not_found(self):
        """Test: erreur si lot non trouve."""
        self.mock_lot_repo.find_by_id.return_value = None

        with pytest.raises(LotDevisNotFoundError):
            self.use_case.execute(lot_id=999, deleted_by=1)

    def test_delete_lot_journal_entry(self):
        """Test: entree de journal pour suppression."""
        lot = _make_lot()
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute(lot_id=10, deleted_by=2)

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert journal_call.action == "suppression_lot"
        assert journal_call.auteur_id == 2


class TestReorderLotsUseCase:
    """Tests pour le reordonnement des lots."""

    def setup_method(self):
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = ReorderLotsUseCase(
            lot_repository=self.mock_lot_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_reorder_success(self):
        """Test: reordonnement reussi."""
        lot1 = _make_lot(id=10, devis_id=1, ordre=0)
        lot2 = _make_lot(id=20, devis_id=1, code_lot="LOT-002", libelle="Lot 2", ordre=1)

        self.mock_lot_repo.find_by_id.side_effect = lambda lid: {10: lot1, 20: lot2}.get(lid)
        self.mock_lot_repo.save.side_effect = lambda l: l
        self.mock_lot_repo.find_by_devis.return_value = [lot2, lot1]  # New order
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, lot_ids=[20, 10], updated_by=1)

        assert isinstance(result, list)
        assert len(result) == 2
        assert lot2.ordre == 0
        assert lot1.ordre == 1

    def test_reorder_ignores_wrong_devis(self):
        """Test: lots d'un autre devis sont ignores."""
        lot1 = _make_lot(id=10, devis_id=1)
        lot_other = _make_lot(id=30, devis_id=2, code_lot="LOT-OTHER", libelle="Autre")

        self.mock_lot_repo.find_by_id.side_effect = lambda lid: {10: lot1, 30: lot_other}.get(lid)
        self.mock_lot_repo.save.side_effect = lambda l: l
        self.mock_lot_repo.find_by_devis.return_value = [lot1]
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute(devis_id=1, lot_ids=[30, 10], updated_by=1)

        # lot_other ne devrait pas etre reordonne car devis_id != 1
        assert lot_other.ordre != 0  # Restera inchange

    def test_reorder_journal_entry(self):
        """Test: entree de journal pour reordonnement."""
        self.mock_lot_repo.find_by_id.return_value = None
        self.mock_lot_repo.find_by_devis.return_value = []
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute(devis_id=1, lot_ids=[], updated_by=3)

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert journal_call.action == "reordonnement_lots"
