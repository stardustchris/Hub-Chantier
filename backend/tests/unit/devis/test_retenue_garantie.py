"""Tests unitaires pour le Value Object RetenueGarantie et les properties du Devis.

DEV-22: Parametrage retenue de garantie par devis (0%, 5%, 10%).
Couche Domain - value_objects/retenue_garantie.py + entite Devis.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal

from modules.devis.domain.value_objects.retenue_garantie import (
    RetenueGarantie,
    RetenueGarantieInvalideError,
)
from modules.devis.domain.entities.devis import Devis, DevisValidationError
from modules.devis.domain.value_objects.statut_devis import StatutDevis


def _make_devis(**kwargs):
    """Cree un devis valide avec valeurs par defaut."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "objet": "Renovation bureau",
        "statut": StatutDevis.BROUILLON,
        "date_creation": date(2026, 1, 15),
        "montant_total_ht": Decimal("10000"),
        "montant_total_ttc": Decimal("12000"),
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


# ─────────────────────────────────────────────────────────────────────────────
# Tests Value Object RetenueGarantie
# ─────────────────────────────────────────────────────────────────────────────

class TestRetenueGarantie:
    """Tests pour le value object RetenueGarantie."""

    def test_creation_taux_zero(self):
        """Test: creation avec taux 0% reussie."""
        rg = RetenueGarantie(Decimal("0"))
        assert rg.taux == Decimal("0")

    def test_creation_taux_cinq(self):
        """Test: creation avec taux 5% reussie."""
        rg = RetenueGarantie(Decimal("5"))
        assert rg.taux == Decimal("5")

    def test_creation_taux_dix_rejete(self):
        """Test: creation avec taux 10% rejetee (loi 71-584: plafond 5%)."""
        with pytest.raises(RetenueGarantieInvalideError):
            RetenueGarantie(Decimal("10"))

    def test_creation_taux_entier(self):
        """Test: creation avec int converti en Decimal."""
        rg = RetenueGarantie(5)
        assert rg.taux == Decimal("5")

    def test_creation_taux_invalide(self):
        """Test: erreur si taux non autorise (ex: 3%)."""
        with pytest.raises(RetenueGarantieInvalideError):
            RetenueGarantie(Decimal("3"))

    def test_creation_taux_negatif(self):
        """Test: erreur si taux negatif."""
        with pytest.raises(RetenueGarantieInvalideError):
            RetenueGarantie(Decimal("-5"))

    def test_creation_taux_quinze_invalide(self):
        """Test: erreur si taux 15% (non autorise)."""
        with pytest.raises(RetenueGarantieInvalideError):
            RetenueGarantie(Decimal("15"))

    def test_calculer_montant_taux_zero(self):
        """Test: montant retenu = 0 pour taux 0%."""
        rg = RetenueGarantie(Decimal("0"))
        montant = rg.calculer_montant(Decimal("10000"))
        assert montant == Decimal("0.00")

    def test_calculer_montant_taux_cinq(self):
        """Test: montant retenu = 500 pour 10000 HT a 5% (loi 71-584: sur HT)."""
        rg = RetenueGarantie(Decimal("5"))
        montant = rg.calculer_montant(Decimal("10000"))
        assert montant == Decimal("500.00")

    def test_calculer_montant_taux_dix_rejete(self):
        """Test: taux 10% rejete, impossible de calculer montant (loi 71-584: plafond 5%)."""
        with pytest.raises(RetenueGarantieInvalideError):
            RetenueGarantie(Decimal("10"))

    def test_montant_net_a_payer_taux_cinq(self):
        """Test: net = TTC - retenue(HT) = 12000 - 500 = 11500 (loi 71-584)."""
        rg = RetenueGarantie(Decimal("5"))
        net = rg.montant_net_a_payer(Decimal("10000"), Decimal("12000"))
        assert net == Decimal("11500.00")

    def test_montant_net_a_payer_taux_zero(self):
        """Test: net = montant TTC pour taux 0%."""
        rg = RetenueGarantie(Decimal("0"))
        net = rg.montant_net_a_payer(Decimal("10000"), Decimal("12000"))
        assert net == Decimal("12000.00")

    def test_egalite(self):
        """Test: deux RetenueGarantie avec meme taux sont egales."""
        rg1 = RetenueGarantie(Decimal("5"))
        rg2 = RetenueGarantie(Decimal("5"))
        assert rg1 == rg2

    def test_inegalite(self):
        """Test: deux RetenueGarantie avec taux differents ne sont pas egales."""
        rg1 = RetenueGarantie(Decimal("0"))
        rg2 = RetenueGarantie(Decimal("5"))
        assert rg1 != rg2

    def test_hash(self):
        """Test: meme hash pour meme taux."""
        rg1 = RetenueGarantie(Decimal("5"))
        rg2 = RetenueGarantie(Decimal("5"))
        assert hash(rg1) == hash(rg2)

    def test_repr(self):
        """Test: repr lisible."""
        rg = RetenueGarantie(Decimal("5"))
        assert "5" in repr(rg)

    def test_str(self):
        """Test: str affiche le pourcentage."""
        rg = RetenueGarantie(Decimal("5"))
        assert str(rg) == "5%"


# ─────────────────────────────────────────────────────────────────────────────
# Tests des properties calculees sur entite Devis
# ─────────────────────────────────────────────────────────────────────────────

class TestDevisRetenueGarantie:
    """Tests pour les properties de retenue de garantie sur l'entite Devis."""

    def test_devis_retenue_garantie_property(self):
        """Test: la property retourne un RetenueGarantie valide."""
        devis = _make_devis(retenue_garantie_pct=Decimal("5"))
        rg = devis.retenue_garantie
        assert isinstance(rg, RetenueGarantie)
        assert rg.taux == Decimal("5")

    def test_devis_montant_retenue_garantie_zero(self):
        """Test: montant retenu = 0 quand taux = 0%."""
        devis = _make_devis(
            retenue_garantie_pct=Decimal("0"),
            montant_total_ttc=Decimal("12000"),
        )
        assert devis.montant_retenue_garantie == Decimal("0.00")

    def test_devis_montant_retenue_garantie_cinq(self):
        """Test: montant retenu = 500 pour 10000 HT a 5% (loi 71-584: sur HT)."""
        devis = _make_devis(
            retenue_garantie_pct=Decimal("5"),
            montant_total_ht=Decimal("10000"),
            montant_total_ttc=Decimal("12000"),
        )
        assert devis.montant_retenue_garantie == Decimal("500.00")

    def test_devis_montant_net_a_payer(self):
        """Test: montant net = TTC - retenue(HT) (loi 71-584)."""
        devis = _make_devis(
            retenue_garantie_pct=Decimal("5"),
            montant_total_ht=Decimal("10000"),
            montant_total_ttc=Decimal("12000"),
        )
        # retenue = 5% × 10000 HT = 500, net = 12000 - 500 = 11500
        assert devis.montant_net_a_payer == Decimal("11500.00")

    def test_devis_creation_retenue_invalide(self):
        """Test: erreur si retenue de garantie invalide dans Devis."""
        with pytest.raises(DevisValidationError, match="retenue de garantie"):
            _make_devis(retenue_garantie_pct=Decimal("7"))

    def test_devis_creation_retenue_zero_valide(self):
        """Test: creation devis avec retenue 0% reussie."""
        devis = _make_devis(retenue_garantie_pct=Decimal("0"))
        assert devis.retenue_garantie_pct == Decimal("0")
