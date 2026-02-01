"""Tests unitaires pour les Use Cases de gestion des lignes.

DEV-03 + DEV-05: Lignes de devis avec debourses.
Couche Application - ligne_use_cases.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.devis.domain.entities.lot_devis import LotDevis
from modules.devis.domain.entities.ligne_devis import LigneDevis
from modules.devis.domain.entities.debourse_detail import DebourseDetail
from modules.devis.domain.entities.journal_devis import JournalDevis
from modules.devis.domain.value_objects.type_debourse import TypeDebourse
from modules.devis.domain.value_objects.unite_article import UniteArticle
from modules.devis.domain.repositories.lot_devis_repository import LotDevisRepository
from modules.devis.domain.repositories.ligne_devis_repository import LigneDevisRepository
from modules.devis.domain.repositories.debourse_detail_repository import DebourseDetailRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.ligne_use_cases import (
    CreateLigneDevisUseCase,
    UpdateLigneDevisUseCase,
    DeleteLigneDevisUseCase,
    LigneDevisNotFoundError,
)
from modules.devis.application.use_cases.lot_use_cases import LotDevisNotFoundError
from modules.devis.application.dtos.ligne_dtos import (
    LigneDevisCreateDTO,
    LigneDevisUpdateDTO,
    LigneDevisDTO,
)
from modules.devis.application.dtos.debourse_dtos import DebourseDetailCreateDTO


def _make_lot(**kwargs):
    """Cree un lot valide."""
    defaults = {
        "id": 10,
        "devis_id": 1,
        "code_lot": "LOT-001",
        "libelle": "Gros oeuvre",
    }
    defaults.update(kwargs)
    return LotDevis(**defaults)


def _make_ligne(**kwargs):
    """Cree une ligne valide."""
    defaults = {
        "id": 100,
        "lot_devis_id": 10,
        "libelle": "Beton C25/30",
        "unite": UniteArticle.M3,
        "quantite": Decimal("10"),
        "prix_unitaire_ht": Decimal("95.50"),
        "taux_tva": Decimal("20"),
        "ordre": 1,
    }
    defaults.update(kwargs)
    return LigneDevis(**defaults)


class TestCreateLigneDevisUseCase:
    """Tests pour la creation de lignes."""

    def setup_method(self):
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_debourse_repo = Mock(spec=DebourseDetailRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = CreateLigneDevisUseCase(
            ligne_repository=self.mock_ligne_repo,
            lot_repository=self.mock_lot_repo,
            debourse_repository=self.mock_debourse_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_create_ligne_success(self):
        """Test: creation de ligne reussie."""
        lot = _make_lot()
        saved_ligne = _make_ligne()
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_ligne_repo.save.return_value = saved_ligne
        self.mock_journal_repo.save.return_value = Mock()

        dto = LigneDevisCreateDTO(
            lot_devis_id=10,
            designation="Beton C25/30",
            unite="m3",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("95.50"),
        )
        result = self.use_case.execute(dto, created_by=1)

        assert isinstance(result, LigneDevisDTO)
        assert result.designation == "Beton C25/30"

    def test_create_ligne_lot_not_found(self):
        """Test: erreur si lot non trouve."""
        self.mock_lot_repo.find_by_id.return_value = None

        dto = LigneDevisCreateDTO(lot_devis_id=999, designation="Test")
        with pytest.raises(LotDevisNotFoundError):
            self.use_case.execute(dto, created_by=1)

    def test_create_ligne_avec_debourses(self):
        """Test: creation de ligne avec debourses inline."""
        lot = _make_lot()
        saved_ligne = _make_ligne()
        saved_debourse = DebourseDetail(
            id=1000, ligne_devis_id=100, libelle="Ciment",
            type_debourse=TypeDebourse.MATERIAUX,
            quantite=Decimal("50"), prix_unitaire=Decimal("12"),
        )

        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_ligne_repo.save.return_value = saved_ligne
        self.mock_debourse_repo.save.return_value = saved_debourse
        self.mock_journal_repo.save.return_value = Mock()

        dto = LigneDevisCreateDTO(
            lot_devis_id=10,
            designation="Beton",
            debourses=[
                DebourseDetailCreateDTO(
                    type_debourse="materiaux",
                    designation="Ciment",
                    quantite=Decimal("50"),
                    prix_unitaire=Decimal("12"),
                ),
            ],
        )
        result = self.use_case.execute(dto, created_by=1)

        assert len(result.debourses) == 1
        self.mock_debourse_repo.save.assert_called_once()

    def test_create_ligne_unite_invalide_fallback(self):
        """Test: unite invalide tombe sur U par defaut."""
        lot = _make_lot()
        saved_ligne = _make_ligne(unite=UniteArticle.U)
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_ligne_repo.save.return_value = saved_ligne
        self.mock_journal_repo.save.return_value = Mock()

        dto = LigneDevisCreateDTO(
            lot_devis_id=10,
            designation="Test",
            unite="invalid_unit",
        )
        self.use_case.execute(dto, created_by=1)

        ligne_saved = self.mock_ligne_repo.save.call_args[0][0]
        assert ligne_saved.unite == UniteArticle.U

    def test_create_ligne_journal_entry(self):
        """Test: entree de journal pour creation de ligne."""
        lot = _make_lot()
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_ligne_repo.save.return_value = _make_ligne()
        self.mock_journal_repo.save.return_value = Mock()

        dto = LigneDevisCreateDTO(lot_devis_id=10, designation="Ligne journal")
        self.use_case.execute(dto, created_by=3)

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert journal_call.action == "ajout_ligne"
        assert journal_call.auteur_id == 3
        assert journal_call.devis_id == 1  # From lot.devis_id


class TestUpdateLigneDevisUseCase:
    """Tests pour la mise a jour de lignes."""

    def setup_method(self):
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_debourse_repo = Mock(spec=DebourseDetailRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.use_case = UpdateLigneDevisUseCase(
            ligne_repository=self.mock_ligne_repo,
            debourse_repository=self.mock_debourse_repo,
            journal_repository=self.mock_journal_repo,
            lot_repository=self.mock_lot_repo,
        )

    def test_update_ligne_success(self):
        """Test: mise a jour reussie."""
        ligne = _make_ligne()
        lot = _make_lot()
        self.mock_ligne_repo.find_by_id.return_value = ligne
        self.mock_ligne_repo.save.return_value = ligne
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_debourse_repo.find_by_ligne.return_value = []
        self.mock_journal_repo.save.return_value = Mock()

        dto = LigneDevisUpdateDTO(designation="Nouveau libelle")
        result = self.use_case.execute(ligne_id=100, dto=dto, updated_by=1)

        assert isinstance(result, LigneDevisDTO)
        assert ligne.libelle == "Nouveau libelle"

    def test_update_ligne_not_found(self):
        """Test: erreur si ligne non trouvee."""
        self.mock_ligne_repo.find_by_id.return_value = None

        dto = LigneDevisUpdateDTO(designation="Nouveau")
        with pytest.raises(LigneDevisNotFoundError) as exc_info:
            self.use_case.execute(ligne_id=999, dto=dto, updated_by=1)
        assert exc_info.value.ligne_id == 999

    def test_update_ligne_replace_debourses(self):
        """Test: remplacement des debourses lors de la mise a jour."""
        ligne = _make_ligne()
        lot = _make_lot()
        saved_debourse = DebourseDetail(
            id=2000, ligne_devis_id=100, libelle="Nouveau Ciment",
            type_debourse=TypeDebourse.MATERIAUX,
            quantite=Decimal("30"), prix_unitaire=Decimal("15"),
        )

        self.mock_ligne_repo.find_by_id.return_value = ligne
        self.mock_ligne_repo.save.return_value = ligne
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_debourse_repo.save.return_value = saved_debourse
        self.mock_journal_repo.save.return_value = Mock()

        dto = LigneDevisUpdateDTO(
            debourses=[
                DebourseDetailCreateDTO(
                    type_debourse="materiaux",
                    designation="Nouveau Ciment",
                    quantite=Decimal("30"),
                    prix_unitaire=Decimal("15"),
                ),
            ],
        )
        result = self.use_case.execute(ligne_id=100, dto=dto, updated_by=1)

        self.mock_debourse_repo.delete_by_ligne.assert_called_once_with(100)
        assert len(result.debourses) == 1

    def test_update_ligne_keep_existing_debourses(self):
        """Test: garde les debourses existants si non fournis."""
        ligne = _make_ligne()
        lot = _make_lot()
        existing_debourse = DebourseDetail(
            id=1000, ligne_devis_id=100, libelle="Ciment existant",
            quantite=Decimal("50"), prix_unitaire=Decimal("12"),
        )

        self.mock_ligne_repo.find_by_id.return_value = ligne
        self.mock_ligne_repo.save.return_value = ligne
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_debourse_repo.find_by_ligne.return_value = [existing_debourse]
        self.mock_journal_repo.save.return_value = Mock()

        dto = LigneDevisUpdateDTO(designation="Mise a jour")
        result = self.use_case.execute(ligne_id=100, dto=dto, updated_by=1)

        self.mock_debourse_repo.delete_by_ligne.assert_not_called()
        assert len(result.debourses) == 1

    def test_update_ligne_multiple_fields(self):
        """Test: mise a jour de plusieurs champs."""
        ligne = _make_ligne()
        lot = _make_lot()
        self.mock_ligne_repo.find_by_id.return_value = ligne
        self.mock_ligne_repo.save.return_value = ligne
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_debourse_repo.find_by_ligne.return_value = []
        self.mock_journal_repo.save.return_value = Mock()

        dto = LigneDevisUpdateDTO(
            designation="Nouveau libelle",
            quantite=Decimal("20"),
            prix_unitaire_ht=Decimal("150"),
            marge_ligne_pct=Decimal("25"),
        )
        self.use_case.execute(ligne_id=100, dto=dto, updated_by=1)

        assert ligne.libelle == "Nouveau libelle"
        assert ligne.quantite == Decimal("20")
        assert ligne.prix_unitaire_ht == Decimal("150")
        assert ligne.taux_marge_ligne == Decimal("25")


class TestDeleteLigneDevisUseCase:
    """Tests pour la suppression de lignes."""

    def setup_method(self):
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_debourse_repo = Mock(spec=DebourseDetailRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.use_case = DeleteLigneDevisUseCase(
            ligne_repository=self.mock_ligne_repo,
            debourse_repository=self.mock_debourse_repo,
            journal_repository=self.mock_journal_repo,
            lot_repository=self.mock_lot_repo,
        )

    def test_delete_ligne_success(self):
        """Test: suppression reussie."""
        ligne = _make_ligne()
        lot = _make_lot()
        self.mock_ligne_repo.find_by_id.return_value = ligne
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute(ligne_id=100, deleted_by=1)

        self.mock_debourse_repo.delete_by_ligne.assert_called_once_with(100)
        self.mock_ligne_repo.delete.assert_called_once_with(100)

    def test_delete_ligne_not_found(self):
        """Test: erreur si ligne non trouvee."""
        self.mock_ligne_repo.find_by_id.return_value = None

        with pytest.raises(LigneDevisNotFoundError):
            self.use_case.execute(ligne_id=999, deleted_by=1)

    def test_delete_ligne_journal_entry(self):
        """Test: entree de journal pour suppression."""
        ligne = _make_ligne()
        lot = _make_lot()
        self.mock_ligne_repo.find_by_id.return_value = ligne
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute(ligne_id=100, deleted_by=2)

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert journal_call.action == "suppression_ligne"
        assert journal_call.auteur_id == 2

    def test_delete_ligne_debourses_deleted_first(self):
        """Test: les debourses sont supprimes avant la ligne."""
        ligne = _make_ligne()
        lot = _make_lot()
        self.mock_ligne_repo.find_by_id.return_value = ligne
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_journal_repo.save.return_value = Mock()

        call_order = []
        self.mock_debourse_repo.delete_by_ligne.side_effect = lambda *a: call_order.append("debourse")
        self.mock_ligne_repo.delete.side_effect = lambda *a: call_order.append("ligne")

        self.use_case.execute(ligne_id=100, deleted_by=1)

        assert call_order == ["debourse", "ligne"]
