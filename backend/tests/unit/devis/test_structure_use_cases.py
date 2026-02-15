"""Tests unitaires pour les Use Cases de structure de devis.

DEV-03: Creation devis structure - Arborescence lots/chapitres/lignes.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch, call, ANY

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.entities.lot_devis import LotDevis
from modules.devis.domain.entities.ligne_devis import LigneDevis
from modules.devis.domain.entities.debourse_detail import DebourseDetail
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.value_objects import TypeDebourse, UniteArticle
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.lot_devis_repository import LotDevisRepository
from modules.devis.domain.repositories.ligne_devis_repository import LigneDevisRepository
from modules.devis.domain.repositories.debourse_detail_repository import DebourseDetailRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.structure_use_cases import (
    CreateDevisStructureUseCase,
    RenumeroterDevisUseCase,
    GetStructureDevisUseCase,
)
from modules.devis.application.dtos.structure_dtos import (
    CreateDevisStructureDTO,
    LotStructureDTO,
    SousChapitreStructureDTO,
    LigneStructureDTO,
    StructureDevisDTO,
)
from modules.devis.application.dtos.debourse_dtos import DebourseDetailCreateDTO


def _make_devis(**kwargs):
    """Cree un devis valide avec valeurs par defaut."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "statut": StatutDevis.BROUILLON,
        "date_creation": date(2026, 1, 15),
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


def _make_lot(lot_id, devis_id=1, code_lot="LOT-001", libelle="Test", **kwargs):
    """Cree un lot valide."""
    defaults = {
        "id": lot_id,
        "devis_id": devis_id,
        "code_lot": code_lot,
        "libelle": libelle,
        "ordre": 0,
    }
    defaults.update(kwargs)
    return LotDevis(**defaults)


class TestCreateDevisStructureUseCase:
    """Tests pour le use case de creation de structure de devis."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_debourse_repo = Mock(spec=DebourseDetailRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = CreateDevisStructureUseCase(
            devis_repository=self.mock_devis_repo,
            lot_repository=self.mock_lot_repo,
            ligne_repository=self.mock_ligne_repo,
            debourse_repository=self.mock_debourse_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_create_structure_un_lot_une_ligne(self):
        """Test: creation d'un lot avec une ligne."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis

        # Simuler la creation du lot
        saved_lot = _make_lot(10, code_lot="1", libelle="Gros oeuvre")
        self.mock_lot_repo.save.return_value = saved_lot

        # Simuler la creation de la ligne
        saved_ligne = LigneDevis(
            id=100, lot_devis_id=10, libelle="Fondation",
            quantite=Decimal("10"), prix_unitaire_ht=Decimal("150"),
        )
        self.mock_ligne_repo.save.return_value = saved_ligne
        self.mock_journal_repo.save.return_value = Mock()

        dto = CreateDevisStructureDTO(
            devis_id=1,
            lots=[
                LotStructureDTO(
                    titre="Gros oeuvre",
                    lignes=[
                        LigneStructureDTO(
                            designation="Fondation",
                            quantite=Decimal("10"),
                            prix_unitaire_ht=Decimal("150"),
                        ),
                    ],
                ),
            ],
        )

        result = self.use_case.execute(dto, created_by=1)

        assert isinstance(result, StructureDevisDTO)
        assert result.devis_id == 1
        assert result.nombre_lots == 1
        assert result.nombre_lignes == 1
        self.mock_lot_repo.save.assert_called_once()
        self.mock_ligne_repo.save.assert_called_once()
        self.mock_journal_repo.save.assert_called_once()

    def test_create_structure_devis_inexistant(self):
        """Test: erreur si le devis n'existe pas."""
        self.mock_devis_repo.find_by_id.return_value = None

        from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError

        dto = CreateDevisStructureDTO(devis_id=999, lots=[])
        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(dto, created_by=1)

    def test_create_structure_avec_sous_chapitres(self):
        """Test: creation d'un lot avec sous-chapitres."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis

        lot_counter = [0]
        def save_lot_side_effect(lot):
            lot_counter[0] += 1
            lot.id = lot_counter[0] * 10
            return lot
        self.mock_lot_repo.save.side_effect = save_lot_side_effect

        ligne_counter = [0]
        def save_ligne_side_effect(ligne):
            ligne_counter[0] += 1
            ligne.id = ligne_counter[0] * 100
            return ligne
        self.mock_ligne_repo.save.side_effect = save_ligne_side_effect
        self.mock_journal_repo.save.return_value = Mock()

        dto = CreateDevisStructureDTO(
            devis_id=1,
            lots=[
                LotStructureDTO(
                    titre="Gros oeuvre",
                    sous_chapitres=[
                        SousChapitreStructureDTO(
                            titre="Fondations",
                            lignes=[
                                LigneStructureDTO(designation="Beton C25"),
                            ],
                        ),
                        SousChapitreStructureDTO(
                            titre="Elevation",
                            lignes=[
                                LigneStructureDTO(designation="Parpaings"),
                            ],
                        ),
                    ],
                ),
            ],
        )

        result = self.use_case.execute(dto, created_by=1)

        assert result.nombre_lots == 1
        assert result.nombre_lignes == 2
        # 1 lot racine + 2 sous-chapitres = 3 saves lot
        assert self.mock_lot_repo.save.call_count == 3
        # 2 lignes = 2 saves ligne
        assert self.mock_ligne_repo.save.call_count == 2

    def test_create_structure_avec_debourses(self):
        """Test: creation de lignes avec debourses."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        saved_lot = _make_lot(10, code_lot="1", libelle="Elec")
        self.mock_lot_repo.save.return_value = saved_lot

        saved_ligne = LigneDevis(
            id=100, lot_devis_id=10, libelle="Cable",
            quantite=Decimal("50"), prix_unitaire_ht=Decimal("5"),
        )
        self.mock_ligne_repo.save.return_value = saved_ligne

        saved_debourse = DebourseDetail(
            id=1000, ligne_devis_id=100,
            type_debourse=TypeDebourse.MATERIAUX,
            libelle="Cable 3G2.5", quantite=Decimal("50"),
            prix_unitaire=Decimal("2.50"),
            total=Decimal("125"),
        )
        self.mock_debourse_repo.save.return_value = saved_debourse
        self.mock_journal_repo.save.return_value = Mock()

        dto = CreateDevisStructureDTO(
            devis_id=1,
            lots=[
                LotStructureDTO(
                    titre="Electricite",
                    lignes=[
                        LigneStructureDTO(
                            designation="Cable 3G2.5",
                            quantite=Decimal("50"),
                            prix_unitaire_ht=Decimal("5"),
                            debourses=[
                                DebourseDetailCreateDTO(
                                    type_debourse="materiaux",
                                    designation="Cable 3G2.5",
                                    quantite=Decimal("50"),
                                    prix_unitaire=Decimal("2.50"),
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

        result = self.use_case.execute(dto, created_by=1)

        assert result.nombre_lignes == 1
        self.mock_debourse_repo.save.assert_called_once()

    def test_numerotation_automatique_lots(self):
        """Test: les lots recoivent les codes 1, 2, 3..."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis

        lots_saved = []
        def save_lot_side_effect(lot):
            lot.id = len(lots_saved) + 1
            lots_saved.append(lot)
            return lot
        self.mock_lot_repo.save.side_effect = save_lot_side_effect
        self.mock_journal_repo.save.return_value = Mock()

        dto = CreateDevisStructureDTO(
            devis_id=1,
            lots=[
                LotStructureDTO(titre="Gros oeuvre"),
                LotStructureDTO(titre="Second oeuvre"),
                LotStructureDTO(titre="Electricite"),
            ],
        )

        result = self.use_case.execute(dto, created_by=1)

        assert result.nombre_lots == 3
        assert lots_saved[0].code_lot == "1"
        assert lots_saved[1].code_lot == "2"
        assert lots_saved[2].code_lot == "3"


class TestRenumeroterDevisUseCase:
    """Tests pour le use case de renumerotation automatique."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = RenumeroterDevisUseCase(
            devis_repository=self.mock_devis_repo,
            lot_repository=self.mock_lot_repo,
            ligne_repository=self.mock_ligne_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_renumeroter_lots_racine(self):
        """Test: renumerotation de lots racine."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis

        lots = [
            _make_lot(1, code_lot="OLD-1", libelle="Lot A"),
            _make_lot(2, code_lot="OLD-2", libelle="Lot B"),
        ]
        self.mock_lot_repo.find_by_devis.return_value = lots
        self.mock_lot_repo.find_children.return_value = []
        self.mock_lot_repo.save.side_effect = lambda lot: lot
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, updated_by=1)

        assert len(result) == 2
        # Verifier que les codes ont ete mis a jour
        assert lots[0].code_lot == "1"
        assert lots[1].code_lot == "2"

    def test_renumeroter_devis_inexistant(self):
        """Test: erreur si le devis n'existe pas."""
        self.mock_devis_repo.find_by_id.return_value = None

        from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, updated_by=1)


class TestGetStructureDevisUseCase:
    """Tests pour le use case de recuperation de structure."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_debourse_repo = Mock(spec=DebourseDetailRepository)
        self.use_case = GetStructureDevisUseCase(
            devis_repository=self.mock_devis_repo,
            lot_repository=self.mock_lot_repo,
            ligne_repository=self.mock_ligne_repo,
            debourse_repository=self.mock_debourse_repo,
        )

    def test_get_structure_vide(self):
        """Test: devis sans lots."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []

        result = self.use_case.execute(devis_id=1)

        assert isinstance(result, StructureDevisDTO)
        assert result.devis_id == 1
        assert result.nombre_lots == 0
        assert result.nombre_lignes == 0
        assert result.total_ht == "0"

    def test_get_structure_avec_lots_et_lignes(self):
        """Test: devis avec lots et lignes."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis

        lot = _make_lot(1, libelle="Gros oeuvre",
                        montant_debourse_ht=Decimal("8010"),
                        montant_vente_ht=Decimal("10586"),
                        montant_vente_ttc=Decimal("12703"))
        self.mock_lot_repo.find_by_devis.return_value = [lot]

        ligne = LigneDevis(
            id=100, lot_devis_id=1, libelle="Fondation",
            quantite=Decimal("10"), prix_unitaire_ht=Decimal("150"),
            total_ht=Decimal("1500"), montant_ttc=Decimal("1800"),
        )
        self.mock_ligne_repo.find_by_lot.return_value = [ligne]
        self.mock_debourse_repo.find_by_ligne.return_value = []

        result = self.use_case.execute(devis_id=1)

        assert result.nombre_lots == 1
        assert result.nombre_lignes == 1
        assert result.total_debourse_sec == "8010"
        assert result.total_ht == "10586"

    def test_get_structure_devis_inexistant(self):
        """Test: erreur si le devis n'existe pas."""
        self.mock_devis_repo.find_by_id.return_value = None

        from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999)
