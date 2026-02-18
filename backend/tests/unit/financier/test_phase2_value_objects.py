"""Tests unitaires pour les Value Objects Phase 2 du module Financier."""

import pytest
from decimal import Decimal

from modules.financier.domain.value_objects import (
    StatutAvenant,
    StatutSituation,
    StatutFacture,
    TypeAlerte,
    TypeFacture,
    CoutEmploye,
    CoutMaterielItem,
)


# ============================================================
# Tests StatutAvenant
# ============================================================

class TestStatutAvenant:
    """Tests pour l'enum StatutAvenant."""

    def test_statut_brouillon(self):
        """Test: valeur brouillon existe."""
        assert StatutAvenant.BROUILLON == "brouillon"
        assert StatutAvenant.BROUILLON.value == "brouillon"

    def test_statut_valide(self):
        """Test: valeur valide existe."""
        assert StatutAvenant.VALIDE == "valide"
        assert StatutAvenant.VALIDE.value == "valide"

    def test_statut_avenant_is_str_enum(self):
        """Test: StatutAvenant est un str enum."""
        assert isinstance(StatutAvenant.BROUILLON, str)

    def test_statut_avenant_values(self):
        """Test: tous les statuts attendus existent."""
        values = [s.value for s in StatutAvenant]
        assert "brouillon" in values
        assert "valide" in values
        assert len(values) == 2


# ============================================================
# Tests StatutSituation
# ============================================================

class TestStatutSituation:
    """Tests pour l'enum StatutSituation."""

    def test_statut_brouillon(self):
        """Test: valeur brouillon existe."""
        assert StatutSituation.BROUILLON == "brouillon"

    def test_statut_en_validation(self):
        """Test: valeur en_validation existe."""
        assert StatutSituation.EN_VALIDATION == "en_validation"

    def test_statut_emise(self):
        """Test: valeur emise existe."""
        assert StatutSituation.EMISE == "emise"

    def test_statut_validee(self):
        """Test: valeur validee existe."""
        assert StatutSituation.VALIDEE == "validee"

    def test_statut_facturee(self):
        """Test: valeur facturee existe."""
        assert StatutSituation.FACTUREE == "facturee"

    def test_statut_situation_values(self):
        """Test: tous les statuts attendus existent."""
        values = [s.value for s in StatutSituation]
        assert len(values) == 5
        assert set(values) == {"brouillon", "en_validation", "emise", "validee", "facturee"}

    def test_statut_situation_is_str_enum(self):
        """Test: StatutSituation est un str enum."""
        assert isinstance(StatutSituation.BROUILLON, str)


# ============================================================
# Tests StatutFacture
# ============================================================

class TestStatutFacture:
    """Tests pour l'enum StatutFacture."""

    def test_statut_brouillon(self):
        """Test: valeur brouillon existe."""
        assert StatutFacture.BROUILLON == "brouillon"

    def test_statut_emise(self):
        """Test: valeur emise existe."""
        assert StatutFacture.EMISE == "emise"

    def test_statut_envoyee(self):
        """Test: valeur envoyee existe."""
        assert StatutFacture.ENVOYEE == "envoyee"

    def test_statut_payee(self):
        """Test: valeur payee existe."""
        assert StatutFacture.PAYEE == "payee"

    def test_statut_annulee(self):
        """Test: valeur annulee existe."""
        assert StatutFacture.ANNULEE == "annulee"

    def test_statut_facture_values(self):
        """Test: tous les statuts attendus existent."""
        values = [s.value for s in StatutFacture]
        assert len(values) == 5
        assert set(values) == {"brouillon", "emise", "envoyee", "payee", "annulee"}

    def test_statut_facture_is_str_enum(self):
        """Test: StatutFacture est un str enum."""
        assert isinstance(StatutFacture.BROUILLON, str)


# ============================================================
# Tests TypeAlerte
# ============================================================

class TestTypeAlerte:
    """Tests pour l'enum TypeAlerte."""

    def test_seuil_engage(self):
        """Test: valeur seuil_engage existe."""
        assert TypeAlerte.SEUIL_ENGAGE == "seuil_engage"

    def test_seuil_realise(self):
        """Test: valeur seuil_realise existe."""
        assert TypeAlerte.SEUIL_REALISE == "seuil_realise"

    def test_depassement_lot(self):
        """Test: valeur depassement_lot existe."""
        assert TypeAlerte.DEPASSEMENT_LOT == "depassement_lot"

    def test_type_alerte_values(self):
        """Test: tous les types attendus existent."""
        values = [t.value for t in TypeAlerte]
        assert len(values) == 3
        assert set(values) == {"seuil_engage", "seuil_realise", "depassement_lot"}

    def test_type_alerte_is_str_enum(self):
        """Test: TypeAlerte est un str enum."""
        assert isinstance(TypeAlerte.SEUIL_ENGAGE, str)


# ============================================================
# Tests TypeFacture
# ============================================================

class TestTypeFacture:
    """Tests pour l'enum TypeFacture."""

    def test_acompte(self):
        """Test: valeur acompte existe."""
        assert TypeFacture.ACOMPTE == "acompte"

    def test_situation(self):
        """Test: valeur situation existe."""
        assert TypeFacture.SITUATION == "situation"

    def test_solde(self):
        """Test: valeur solde existe."""
        assert TypeFacture.SOLDE == "solde"

    def test_type_facture_values(self):
        """Test: tous les types attendus existent."""
        values = [t.value for t in TypeFacture]
        assert len(values) == 3
        assert set(values) == {"acompte", "situation", "solde"}

    def test_type_facture_is_str_enum(self):
        """Test: TypeFacture est un str enum."""
        assert isinstance(TypeFacture.ACOMPTE, str)


# ============================================================
# Tests CoutEmploye
# ============================================================

class TestCoutEmploye:
    """Tests pour le value object CoutEmploye."""

    def test_create_cout_employe(self):
        """Test: creation d'un CoutEmploye valide."""
        cout = CoutEmploye(
            user_id=1,
            nom="Dupont",
            prenom="Jean",
            heures_validees=Decimal("40"),
            taux_horaire=Decimal("25.50"),
            taux_horaire_charge=Decimal("32.50"),
            cout_total=Decimal("1020"),
        )
        assert cout.user_id == 1
        assert cout.nom == "Dupont"
        assert cout.prenom == "Jean"
        assert cout.heures_validees == Decimal("40")
        assert cout.taux_horaire == Decimal("25.50")
        assert cout.cout_total == Decimal("1020")

    def test_cout_employe_frozen(self):
        """Test: CoutEmploye est immutable (frozen=True)."""
        cout = CoutEmploye(
            user_id=1,
            nom="Dupont",
            prenom="Jean",
            heures_validees=Decimal("40"),
            taux_horaire=Decimal("25.50"),
            taux_horaire_charge=Decimal("32.50"),
            cout_total=Decimal("1020"),
        )
        with pytest.raises(AttributeError):
            cout.nom = "Martin"

    def test_cout_employe_equality(self):
        """Test: egalite entre deux CoutEmploye identiques."""
        cout1 = CoutEmploye(
            user_id=1,
            nom="Dupont",
            prenom="Jean",
            heures_validees=Decimal("40"),
            taux_horaire=Decimal("25.50"),
            taux_horaire_charge=Decimal("32.50"),
            cout_total=Decimal("1020"),
        )
        cout2 = CoutEmploye(
            user_id=1,
            nom="Dupont",
            prenom="Jean",
            heures_validees=Decimal("40"),
            taux_horaire=Decimal("25.50"),
            taux_horaire_charge=Decimal("32.50"),
            cout_total=Decimal("1020"),
        )
        assert cout1 == cout2


# ============================================================
# Tests CoutMaterielItem
# ============================================================

class TestCoutMaterielItem:
    """Tests pour le value object CoutMaterielItem."""

    def test_create_cout_materiel(self):
        """Test: creation d'un CoutMaterielItem valide."""
        cout = CoutMaterielItem(
            ressource_id=1,
            nom="Pelleteuse Cat 320",
            code="PELL-001",
            jours_reservation=5,
            tarif_journalier=Decimal("350"),
            cout_total=Decimal("1750"),
        )
        assert cout.ressource_id == 1
        assert cout.nom == "Pelleteuse Cat 320"
        assert cout.code == "PELL-001"
        assert cout.jours_reservation == 5
        assert cout.tarif_journalier == Decimal("350")
        assert cout.cout_total == Decimal("1750")

    def test_cout_materiel_frozen(self):
        """Test: CoutMaterielItem est immutable (frozen=True)."""
        cout = CoutMaterielItem(
            ressource_id=1,
            nom="Pelleteuse",
            code="PELL-001",
            jours_reservation=5,
            tarif_journalier=Decimal("350"),
            cout_total=Decimal("1750"),
        )
        with pytest.raises(AttributeError):
            cout.nom = "Grue"

    def test_cout_materiel_equality(self):
        """Test: egalite entre deux CoutMaterielItem identiques."""
        cout1 = CoutMaterielItem(
            ressource_id=1,
            nom="Pelleteuse",
            code="PELL-001",
            jours_reservation=5,
            tarif_journalier=Decimal("350"),
            cout_total=Decimal("1750"),
        )
        cout2 = CoutMaterielItem(
            ressource_id=1,
            nom="Pelleteuse",
            code="PELL-001",
            jours_reservation=5,
            tarif_journalier=Decimal("350"),
            cout_total=Decimal("1750"),
        )
        assert cout1 == cout2
