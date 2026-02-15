"""Tests unitaires pour les Use Cases de decomposition des debourses.

DEV-05: Detail debourses avances - Vue decomposee par type.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.entities.lot_devis import LotDevis
from modules.devis.domain.entities.ligne_devis import LigneDevis
from modules.devis.domain.entities.debourse_detail import DebourseDetail
from modules.devis.domain.value_objects import TypeDebourse, StatutDevis
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.lot_devis_repository import LotDevisRepository
from modules.devis.domain.repositories.ligne_devis_repository import LigneDevisRepository
from modules.devis.domain.repositories.debourse_detail_repository import DebourseDetailRepository
from modules.devis.application.use_cases.decompose_debourse_use_cases import (
    DecomposerDebourseLigneUseCase,
    DecomposerDebourseDevisUseCase,
)
from modules.devis.application.dtos.decompose_debourse_dtos import (
    DecomposeDebourseDTO,
    DecomposeDevisDTO,
)


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


def _make_lot(lot_id, devis_id=1, libelle="Test"):
    """Cree un lot valide."""
    return LotDevis(
        id=lot_id, devis_id=devis_id,
        code_lot=f"LOT-{lot_id:03d}", libelle=libelle,
    )


def _make_ligne(ligne_id, lot_devis_id=1, libelle="Test"):
    """Cree une ligne valide."""
    return LigneDevis(
        id=ligne_id, lot_devis_id=lot_devis_id,
        libelle=libelle, quantite=Decimal("1"),
        prix_unitaire_ht=Decimal("0"),
    )


def _make_debourse(deb_id, ligne_id, type_debourse, qte, pu, libelle="Test", **kwargs):
    """Cree un debourse detaille valide."""
    return DebourseDetail(
        id=deb_id, ligne_devis_id=ligne_id,
        type_debourse=type_debourse, libelle=libelle,
        quantite=qte, prix_unitaire=pu,
        total=qte * pu,
        **kwargs,
    )


class TestDecomposerDebourseLigneUseCase:
    """Tests pour la decomposition par ligne."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_debourse_repo = Mock(spec=DebourseDetailRepository)
        self.use_case = DecomposerDebourseLigneUseCase(
            ligne_repository=self.mock_ligne_repo,
            debourse_repository=self.mock_debourse_repo,
        )

    def test_decompose_ligne_standard(self):
        """Test: decomposition d'une ligne avec MOE et materiaux."""
        ligne = _make_ligne(100)
        self.mock_ligne_repo.find_by_id.return_value = ligne

        debourses = [
            _make_debourse(1, 100, TypeDebourse.MOE, Decimal("120"), Decimal("42"),
                           libelle="Macon", metier="macon", taux_horaire=Decimal("42")),
            _make_debourse(2, 100, TypeDebourse.MATERIAUX, Decimal("800"), Decimal("3.50"),
                           libelle="Parpaings"),
        ]
        self.mock_debourse_repo.find_by_ligne.return_value = debourses

        result = self.use_case.execute(100)

        assert isinstance(result, DecomposeDebourseDTO)
        assert result.ligne_devis_id == 100
        # Decimal string representations preserve trailing precision
        assert Decimal(result.total_moe) == Decimal("5040")
        assert Decimal(result.total_materiaux) == Decimal("2800")
        assert Decimal(result.debourse_sec) == Decimal("7840")

    def test_decompose_ligne_inexistante(self):
        """Test: erreur si la ligne n'existe pas."""
        self.mock_ligne_repo.find_by_id.return_value = None

        from modules.devis.application.use_cases.ligne_use_cases import LigneDevisNotFoundError

        with pytest.raises(LigneDevisNotFoundError):
            self.use_case.execute(999)

    def test_decompose_ligne_sans_debourses(self):
        """Test: ligne sans debourses -> tout a zero."""
        ligne = _make_ligne(100)
        self.mock_ligne_repo.find_by_id.return_value = ligne
        self.mock_debourse_repo.find_by_ligne.return_value = []

        result = self.use_case.execute(100)

        assert result.debourse_sec == "0"
        assert result.total_moe == "0"
        assert result.total_materiaux == "0"
        assert result.details_par_type == {}


class TestDecomposerDebourseDevisUseCase:
    """Tests pour la decomposition du devis complet."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_debourse_repo = Mock(spec=DebourseDetailRepository)
        self.use_case = DecomposerDebourseDevisUseCase(
            devis_repository=self.mock_devis_repo,
            lot_repository=self.mock_lot_repo,
            ligne_repository=self.mock_ligne_repo,
            debourse_repository=self.mock_debourse_repo,
        )

    def test_decompose_devis_complet(self):
        """Test: decomposition d'un devis avec 2 lots."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis

        lot1 = _make_lot(1, libelle="Gros oeuvre")
        lot2 = _make_lot(2, libelle="Electricite")
        self.mock_lot_repo.find_by_devis.return_value = [lot1, lot2]

        ligne1 = _make_ligne(100, lot_devis_id=1, libelle="Fondation")
        ligne2 = _make_ligne(200, lot_devis_id=2, libelle="Cablage")

        def find_by_lot(lot_id, **kwargs):
            if lot_id == 1:
                return [ligne1]
            elif lot_id == 2:
                return [ligne2]
            return []
        self.mock_ligne_repo.find_by_lot.side_effect = find_by_lot

        debourses_l1 = [
            _make_debourse(1, 100, TypeDebourse.MOE, Decimal("120"), Decimal("42"),
                           metier="macon", taux_horaire=Decimal("42")),
        ]
        debourses_l2 = [
            _make_debourse(2, 200, TypeDebourse.MATERIAUX, Decimal("100"), Decimal("5")),
        ]

        def find_by_ligne(ligne_id):
            if ligne_id == 100:
                return debourses_l1
            elif ligne_id == 200:
                return debourses_l2
            return []
        self.mock_debourse_repo.find_by_ligne.side_effect = find_by_ligne

        result = self.use_case.execute(1)

        assert isinstance(result, DecomposeDevisDTO)
        assert result.devis_id == 1
        assert Decimal(result.total_moe) == Decimal("5040")
        assert Decimal(result.total_materiaux) == Decimal("500")
        assert Decimal(result.debourse_sec_total) == Decimal("5540")
        assert len(result.lots) == 2

    def test_decompose_devis_inexistant(self):
        """Test: erreur si le devis n'existe pas."""
        self.mock_devis_repo.find_by_id.return_value = None

        from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(999)

    def test_decompose_devis_vide(self):
        """Test: devis sans lots."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []

        result = self.use_case.execute(1)

        assert result.debourse_sec_total == "0"
        assert len(result.lots) == 0

    def test_decompose_devis_serialisation(self):
        """Test: le DTO se serialise correctement en dict."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []

        result = self.use_case.execute(1)
        d = result.to_dict()

        assert d["devis_id"] == 1
        assert d["debourse_sec_total"] == "0"
        assert isinstance(d["lots"], list)
