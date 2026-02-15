"""Tests unitaires pour le service de decomposition des debourses.

DEV-05: Detail debourses avances - Breakdown par type.
"""

import pytest
from decimal import Decimal

from modules.devis.domain.entities.debourse_detail import DebourseDetail
from modules.devis.domain.value_objects import TypeDebourse
from modules.devis.domain.services.debourse_service import (
    DebourseService,
    DecomposeDebourse,
)


def _make_debourse(type_debourse, quantite, prix_unitaire, libelle="Test", **kwargs):
    """Cree un debourse detaille valide."""
    defaults = {
        "id": None,
        "ligne_devis_id": 1,
        "type_debourse": type_debourse,
        "libelle": libelle,
        "quantite": quantite,
        "prix_unitaire": prix_unitaire,
    }
    defaults.update(kwargs)
    return DebourseDetail(**defaults)


class TestDecomposeDebourse:
    """Tests pour le value object DecomposeDebourse."""

    def test_debourse_sec_vide(self):
        """Test: decomposition vide = debourse sec 0."""
        dc = DecomposeDebourse(ligne_devis_id=1)
        assert dc.debourse_sec == Decimal("0")

    def test_debourse_sec_calcule(self):
        """Test: debourse sec = somme de tous les types."""
        dc = DecomposeDebourse(
            ligne_devis_id=1,
            total_moe=Decimal("1800"),
            total_materiaux=Decimal("1750"),
            total_sous_traitance=Decimal("0"),
            total_materiel=Decimal("120"),
            total_deplacement=Decimal("195"),
        )
        assert dc.debourse_sec == Decimal("3865")

    def test_to_dict(self):
        """Test: serialisation en dictionnaire."""
        dc = DecomposeDebourse(
            ligne_devis_id=1,
            total_moe=Decimal("1800"),
        )
        d = dc.to_dict()
        assert d["ligne_devis_id"] == 1
        assert d["total_moe"] == "1800"
        assert d["debourse_sec"] == "1800"


class TestDebourseServiceDecomposer:
    """Tests pour la decomposition des debourses d'une ligne."""

    def test_decomposer_vide(self):
        """Test: aucun debourse -> tout a zero."""
        result = DebourseService.decomposer(ligne_devis_id=1, debourses=[])
        assert result.ligne_devis_id == 1
        assert result.debourse_sec == Decimal("0")
        assert result.total_moe == Decimal("0")
        assert result.total_materiaux == Decimal("0")
        assert result.details_par_type == {}

    def test_decomposer_moe_seul(self):
        """Test: un seul debourse MOE."""
        debourses = [
            _make_debourse(TypeDebourse.MOE, Decimal("40"), Decimal("42"),
                           libelle="Macon", metier="macon", taux_horaire=Decimal("42")),
        ]
        result = DebourseService.decomposer(1, debourses)
        assert result.total_moe == Decimal("1680")  # 40 * 42
        assert result.total_materiaux == Decimal("0")
        assert result.debourse_sec == Decimal("1680")
        assert "moe" in result.details_par_type
        assert len(result.details_par_type["moe"]) == 1
        assert result.details_par_type["moe"][0]["metier"] == "macon"

    def test_decomposer_multi_types(self):
        """Test: debourses multi-types (exemple lot maconnerie spec)."""
        debourses = [
            _make_debourse(TypeDebourse.MOE, Decimal("120"), Decimal("42"),
                           libelle="Macon", metier="macon", taux_horaire=Decimal("42")),
            _make_debourse(TypeDebourse.MATERIAUX, Decimal("800"), Decimal("3.50"),
                           libelle="Parpaings"),
            _make_debourse(TypeDebourse.MATERIAUX, Decimal("2"), Decimal("85"),
                           libelle="Mortier"),
        ]
        result = DebourseService.decomposer(1, debourses)

        assert result.total_moe == Decimal("5040")         # 120 * 42
        assert result.total_materiaux == Decimal("2970")    # 800*3.50 + 2*85 = 2800 + 170
        assert result.total_sous_traitance == Decimal("0")
        assert result.total_materiel == Decimal("0")
        assert result.total_deplacement == Decimal("0")
        assert result.debourse_sec == Decimal("8010")       # 5040 + 2970

    def test_decomposer_tous_types(self):
        """Test: tous les types de debourse representes."""
        debourses = [
            _make_debourse(TypeDebourse.MOE, Decimal("10"), Decimal("42"),
                           metier="electricien", taux_horaire=Decimal("42")),
            _make_debourse(TypeDebourse.MATERIAUX, Decimal("5"), Decimal("100")),
            _make_debourse(TypeDebourse.SOUS_TRAITANCE, Decimal("1"), Decimal("8500")),
            _make_debourse(TypeDebourse.MATERIEL, Decimal("1"), Decimal("120")),
            _make_debourse(TypeDebourse.DEPLACEMENT, Decimal("3"), Decimal("65")),
        ]
        result = DebourseService.decomposer(1, debourses)

        assert result.total_moe == Decimal("420")
        assert result.total_materiaux == Decimal("500")
        assert result.total_sous_traitance == Decimal("8500")
        assert result.total_materiel == Decimal("120")
        assert result.total_deplacement == Decimal("195")
        assert result.debourse_sec == Decimal("9735")
        assert len(result.details_par_type) == 5

    def test_decomposer_details_moe_avec_taux_horaire(self):
        """Test: details MOE contiennent le metier et taux horaire."""
        debourses = [
            _make_debourse(TypeDebourse.MOE, Decimal("40"), Decimal("42"),
                           libelle="Macon qualifie", metier="macon", taux_horaire=Decimal("42")),
            _make_debourse(TypeDebourse.MOE, Decimal("20"), Decimal("38"),
                           libelle="Manoeuvre", metier="manoeuvre", taux_horaire=Decimal("38")),
        ]
        result = DebourseService.decomposer(1, debourses)

        assert result.total_moe == Decimal("2440")  # 40*42 + 20*38
        moe_details = result.details_par_type["moe"]
        assert len(moe_details) == 2
        assert moe_details[0]["metier"] == "macon"
        assert moe_details[0]["taux_horaire"] == "42"
        assert moe_details[1]["metier"] == "manoeuvre"
        assert moe_details[1]["taux_horaire"] == "38"


class TestDebourseServiceCalculerDebourseSec:
    """Tests pour le calcul du debourse sec total."""

    def test_debourse_sec_vide(self):
        """Test: aucun debourse -> 0."""
        assert DebourseService.calculer_debourse_sec([]) == Decimal("0")

    def test_debourse_sec_un_element(self):
        """Test: un seul debourse."""
        debourses = [
            _make_debourse(TypeDebourse.MOE, Decimal("40"), Decimal("42")),
        ]
        assert DebourseService.calculer_debourse_sec(debourses) == Decimal("1680")

    def test_debourse_sec_multiple(self):
        """Test: plusieurs debourses."""
        debourses = [
            _make_debourse(TypeDebourse.MOE, Decimal("120"), Decimal("42")),      # 5040
            _make_debourse(TypeDebourse.MATERIAUX, Decimal("800"), Decimal("3.50")),  # 2800
            _make_debourse(TypeDebourse.MATERIAUX, Decimal("2"), Decimal("85")),     # 170
        ]
        assert DebourseService.calculer_debourse_sec(debourses) == Decimal("8010")

    def test_debourse_sec_exemple_spec(self):
        """Test: exemple concret de la spec (lot maconnerie)."""
        debourses = [
            _make_debourse(TypeDebourse.MOE, Decimal("120"), Decimal("42")),        # Macon: 5040
            _make_debourse(TypeDebourse.MATERIAUX, Decimal("800"), Decimal("3.50")),   # Parpaings: 2800
            _make_debourse(TypeDebourse.MATERIAUX, Decimal("2"), Decimal("85")),       # Mortier: 170
        ]
        # Debourse sec lot = 5040 + 2800 + 170 = 8010
        assert DebourseService.calculer_debourse_sec(debourses) == Decimal("8010")
