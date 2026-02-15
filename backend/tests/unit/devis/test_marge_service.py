"""Tests unitaires pour le service de resolution des marges.

DEV-06: Gestion marges et coefficients.
Regle de priorite: ligne > lot > type debourse > global.
"""

import pytest
from decimal import Decimal

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.entities.debourse_detail import DebourseDetail
from modules.devis.domain.value_objects import TypeDebourse
from modules.devis.domain.services.marge_service import MargeService, MargeResolue


def _make_devis(**kwargs):
    """Cree un devis valide avec valeurs par defaut."""
    defaults = {
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "taux_marge_global": Decimal("15"),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


def _make_debourse(type_debourse, quantite, prix_unitaire, **kwargs):
    """Cree un debourse detaille valide."""
    defaults = {
        "ligne_devis_id": 1,
        "type_debourse": type_debourse,
        "libelle": f"Debourse {type_debourse.value}",
        "quantite": quantite,
        "prix_unitaire": prix_unitaire,
    }
    defaults.update(kwargs)
    return DebourseDetail(**defaults)


class TestResoudreMarge:
    """Tests pour la resolution de marge selon la hierarchie de priorite."""

    def test_priorite_1_marge_ligne(self):
        """Test: marge ligne prioritaire sur tout le reste."""
        devis = _make_devis(
            taux_marge_global=Decimal("15"),
            taux_marge_moe=Decimal("20"),
        )
        result = MargeService.resoudre_marge(
            ligne_marge=Decimal("25"),
            lot_marge=Decimal("18"),
            devis=devis,
            debourses=[_make_debourse(TypeDebourse.MOE, Decimal("10"), Decimal("42"))],
        )
        assert result.taux == Decimal("25")
        assert result.niveau == "ligne"

    def test_priorite_2_marge_lot(self):
        """Test: marge lot si pas de marge ligne."""
        devis = _make_devis(taux_marge_global=Decimal("15"))
        result = MargeService.resoudre_marge(
            ligne_marge=None,
            lot_marge=Decimal("18"),
            devis=devis,
        )
        assert result.taux == Decimal("18")
        assert result.niveau == "lot"

    def test_priorite_3_marge_type_debourse_moe(self):
        """Test: marge par type si ni ligne ni lot definis."""
        devis = _make_devis(
            taux_marge_global=Decimal("15"),
            taux_marge_moe=Decimal("20"),
        )
        debourses = [
            _make_debourse(TypeDebourse.MOE, Decimal("40"), Decimal("42")),
        ]
        result = MargeService.resoudre_marge(
            ligne_marge=None,
            lot_marge=None,
            devis=devis,
            debourses=debourses,
        )
        assert result.taux == Decimal("20")
        assert result.niveau == "type_debourse"

    def test_priorite_3_marge_type_debourse_materiaux(self):
        """Test: marge materiaux quand c'est le type principal."""
        devis = _make_devis(
            taux_marge_global=Decimal("15"),
            taux_marge_materiaux=Decimal("12"),
        )
        debourses = [
            _make_debourse(TypeDebourse.MATERIAUX, Decimal("100"), Decimal("35")),
            _make_debourse(TypeDebourse.MOE, Decimal("5"), Decimal("42")),
        ]
        result = MargeService.resoudre_marge(
            ligne_marge=None,
            lot_marge=None,
            devis=devis,
            debourses=debourses,
        )
        # Materiaux: 100*35 = 3500, MOE: 5*42 = 210 -> type principal = materiaux
        assert result.taux == Decimal("12")
        assert result.niveau == "type_debourse"

    def test_priorite_4_marge_globale(self):
        """Test: marge globale en fallback."""
        devis = _make_devis(taux_marge_global=Decimal("15"))
        result = MargeService.resoudre_marge(
            ligne_marge=None,
            lot_marge=None,
            devis=devis,
        )
        assert result.taux == Decimal("15")
        assert result.niveau == "global"

    def test_priorite_4_marge_globale_avec_debourses_sans_type_configure(self):
        """Test: marge globale si type debourse non configure sur devis."""
        devis = _make_devis(
            taux_marge_global=Decimal("15"),
            # taux_marge_moe non defini -> None
        )
        debourses = [
            _make_debourse(TypeDebourse.MOE, Decimal("40"), Decimal("42")),
        ]
        result = MargeService.resoudre_marge(
            ligne_marge=None,
            lot_marge=None,
            devis=devis,
            debourses=debourses,
        )
        assert result.taux == Decimal("15")
        assert result.niveau == "global"

    def test_marge_ligne_zero_est_prioritaire(self):
        """Test: marge ligne a 0% est considere comme defini (prioritaire)."""
        devis = _make_devis(taux_marge_global=Decimal("15"))
        result = MargeService.resoudre_marge(
            ligne_marge=Decimal("0"),
            lot_marge=Decimal("18"),
            devis=devis,
        )
        assert result.taux == Decimal("0")
        assert result.niveau == "ligne"

    def test_marge_lot_zero_est_prioritaire(self):
        """Test: marge lot a 0% est considere comme defini."""
        devis = _make_devis(taux_marge_global=Decimal("15"))
        result = MargeService.resoudre_marge(
            ligne_marge=None,
            lot_marge=Decimal("0"),
            devis=devis,
        )
        assert result.taux == Decimal("0")
        assert result.niveau == "lot"

    def test_debourses_vides_fallback_global(self):
        """Test: debourses vides -> marge globale."""
        devis = _make_devis(taux_marge_global=Decimal("15"))
        result = MargeService.resoudre_marge(
            ligne_marge=None,
            lot_marge=None,
            devis=devis,
            debourses=[],
        )
        assert result.taux == Decimal("15")
        assert result.niveau == "global"


class TestGetTypePrincipal:
    """Tests pour la determination du type de debourse principal."""

    def test_type_unique(self):
        """Test: un seul type de debourse."""
        debourses = [
            _make_debourse(TypeDebourse.MOE, Decimal("10"), Decimal("42")),
        ]
        result = MargeService._get_type_principal(debourses)
        assert result == TypeDebourse.MOE

    def test_type_plus_cher(self):
        """Test: le type le plus cher l'emporte."""
        debourses = [
            _make_debourse(TypeDebourse.MOE, Decimal("10"), Decimal("42")),      # 420
            _make_debourse(TypeDebourse.MATERIAUX, Decimal("50"), Decimal("35")), # 1750
        ]
        result = MargeService._get_type_principal(debourses)
        assert result == TypeDebourse.MATERIAUX

    def test_debourses_vides(self):
        """Test: debourses vides retourne None."""
        result = MargeService._get_type_principal([])
        assert result is None

    def test_plusieurs_debourses_meme_type(self):
        """Test: cumul des montants par type."""
        debourses = [
            _make_debourse(TypeDebourse.MOE, Decimal("20"), Decimal("42")),       # 840
            _make_debourse(TypeDebourse.MOE, Decimal("30"), Decimal("42")),       # 1260 -> total MOE = 2100
            _make_debourse(TypeDebourse.MATERIAUX, Decimal("50"), Decimal("35")), # 1750
        ]
        result = MargeService._get_type_principal(debourses)
        assert result == TypeDebourse.MOE  # 2100 > 1750


class TestCalculerPrixRevient:
    """Tests pour le calcul du prix de revient."""

    def test_calcul_standard(self):
        """Test: debourse 8010 * (1 + 12/100) = 8971.20."""
        result = MargeService.calculer_prix_revient(
            debourse_sec=Decimal("8010"),
            coefficient_frais_generaux=Decimal("12"),
        )
        assert result == Decimal("8971.20")

    def test_coefficient_zero(self):
        """Test: coefficient 0% -> prix revient = debourse sec."""
        result = MargeService.calculer_prix_revient(
            debourse_sec=Decimal("5000"),
            coefficient_frais_generaux=Decimal("0"),
        )
        assert result == Decimal("5000")

    def test_coefficient_standard_19(self):
        """Test: coefficient 19% (valeur par defaut entreprise)."""
        result = MargeService.calculer_prix_revient(
            debourse_sec=Decimal("1000"),
            coefficient_frais_generaux=Decimal("19"),
        )
        assert result == Decimal("1190")


class TestCalculerPrixVenteHT:
    """Tests pour le calcul du prix de vente HT."""

    def test_calcul_standard(self):
        """Test: prix revient 8971.20 * (1 + 18/100) = 10586.016."""
        result = MargeService.calculer_prix_vente_ht(
            prix_revient=Decimal("8971.20"),
            taux_marge=Decimal("18"),
        )
        assert result == Decimal("10586.016")

    def test_marge_zero(self):
        """Test: marge 0% -> prix vente = prix revient."""
        result = MargeService.calculer_prix_vente_ht(
            prix_revient=Decimal("5000"),
            taux_marge=Decimal("0"),
        )
        assert result == Decimal("5000")

    def test_marge_15_pct(self):
        """Test: marge 15% standard."""
        result = MargeService.calculer_prix_vente_ht(
            prix_revient=Decimal("1000"),
            taux_marge=Decimal("15"),
        )
        assert result == Decimal("1150")


class TestMargeResolue:
    """Tests pour le value object MargeResolue."""

    def test_repr(self):
        """Test: representation textuelle."""
        mr = MargeResolue(taux=Decimal("15"), niveau="global")
        assert "15" in repr(mr)
        assert "global" in repr(mr)
