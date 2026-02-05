"""Tests unitaires pour le Value Object TauxTVA.

DEV-23: Generation attestation TVA reglementaire.
Couche Domain - value_objects/taux_tva.py
"""

import pytest
from decimal import Decimal

from modules.devis.domain.value_objects.taux_tva import (
    TauxTVA,
    TauxTVAInvalideError,
)


class TestTauxTVA:
    """Tests pour le value object TauxTVA."""

    # ─────────────────────────────────────────────────────────────────
    # Creation
    # ─────────────────────────────────────────────────────────────────

    def test_creation_taux_5_5(self):
        """Test: creation avec taux 5.5% reussie."""
        tva = TauxTVA(Decimal("5.5"))
        assert tva.taux == Decimal("5.5")

    def test_creation_taux_10(self):
        """Test: creation avec taux 10% reussie."""
        tva = TauxTVA(Decimal("10.0"))
        assert tva.taux == Decimal("10.0")

    def test_creation_taux_20(self):
        """Test: creation avec taux 20% reussie."""
        tva = TauxTVA(Decimal("20.0"))
        assert tva.taux == Decimal("20.0")

    def test_creation_taux_float_converti(self):
        """Test: creation depuis un float (via str) reussie."""
        tva = TauxTVA(5.5)
        assert tva.taux == Decimal("5.5")

    def test_creation_taux_invalide(self):
        """Test: erreur si taux non autorise (ex: 7%)."""
        with pytest.raises(TauxTVAInvalideError):
            TauxTVA(Decimal("7"))

    def test_creation_taux_zero_invalide(self):
        """Test: erreur si taux 0%."""
        with pytest.raises(TauxTVAInvalideError):
            TauxTVA(Decimal("0"))

    def test_creation_taux_negatif_invalide(self):
        """Test: erreur si taux negatif."""
        with pytest.raises(TauxTVAInvalideError):
            TauxTVA(Decimal("-5"))

    # ─────────────────────────────────────────────────────────────────
    # Property necessite_attestation
    # ─────────────────────────────────────────────────────────────────

    def test_necessite_attestation_5_5(self):
        """Test: 5.5% necessite attestation."""
        tva = TauxTVA(Decimal("5.5"))
        assert tva.necessite_attestation is True

    def test_necessite_attestation_10(self):
        """Test: 10% necessite attestation."""
        tva = TauxTVA(Decimal("10.0"))
        assert tva.necessite_attestation is True

    def test_necessite_attestation_20(self):
        """Test: 20% ne necessite PAS attestation."""
        tva = TauxTVA(Decimal("20.0"))
        assert tva.necessite_attestation is False

    # ─────────────────────────────────────────────────────────────────
    # Property type_cerfa
    # ─────────────────────────────────────────────────────────────────

    def test_type_cerfa_5_5(self):
        """Test: 5.5% -> CERFA 1301-SD."""
        tva = TauxTVA(Decimal("5.5"))
        assert tva.type_cerfa == "1301-SD"

    def test_type_cerfa_10(self):
        """Test: 10% -> CERFA 1300-SD."""
        tva = TauxTVA(Decimal("10.0"))
        assert tva.type_cerfa == "1300-SD"

    def test_type_cerfa_20(self):
        """Test: 20% -> None (pas de CERFA)."""
        tva = TauxTVA(Decimal("20.0"))
        assert tva.type_cerfa is None

    # ─────────────────────────────────────────────────────────────────
    # Property type_attestation
    # ─────────────────────────────────────────────────────────────────

    def test_type_attestation_5_5(self):
        """Test: 5.5% -> CERFA_1301_SD."""
        tva = TauxTVA(Decimal("5.5"))
        assert tva.type_attestation == "CERFA_1301_SD"

    def test_type_attestation_10(self):
        """Test: 10% -> CERFA_1300_SD."""
        tva = TauxTVA(Decimal("10.0"))
        assert tva.type_attestation == "CERFA_1300_SD"

    def test_type_attestation_20(self):
        """Test: 20% -> None."""
        tva = TauxTVA(Decimal("20.0"))
        assert tva.type_attestation is None

    # ─────────────────────────────────────────────────────────────────
    # Property libelle
    # ─────────────────────────────────────────────────────────────────

    def test_libelle_5_5(self):
        """Test: libelle pour 5.5%."""
        tva = TauxTVA(Decimal("5.5"))
        assert "5.5" in tva.libelle

    def test_libelle_10(self):
        """Test: libelle pour 10%."""
        tva = TauxTVA(Decimal("10.0"))
        assert "10" in tva.libelle

    def test_libelle_20(self):
        """Test: libelle pour 20%."""
        tva = TauxTVA(Decimal("20.0"))
        assert "20" in tva.libelle

    # ─────────────────────────────────────────────────────────────────
    # Calcul montant TVA
    # ─────────────────────────────────────────────────────────────────

    def test_calculer_montant_tva_5_5(self):
        """Test: TVA = 550 pour 10000 HT a 5.5%."""
        tva = TauxTVA(Decimal("5.5"))
        montant = tva.calculer_montant_tva(Decimal("10000"))
        assert montant == Decimal("550.00")

    def test_calculer_montant_tva_10(self):
        """Test: TVA = 1000 pour 10000 HT a 10%."""
        tva = TauxTVA(Decimal("10.0"))
        montant = tva.calculer_montant_tva(Decimal("10000"))
        assert montant == Decimal("1000.00")

    def test_calculer_montant_tva_20(self):
        """Test: TVA = 2000 pour 10000 HT a 20%."""
        tva = TauxTVA(Decimal("20.0"))
        montant = tva.calculer_montant_tva(Decimal("10000"))
        assert montant == Decimal("2000.00")

    def test_calculer_montant_tva_arrondi(self):
        """Test: arrondi au centime."""
        tva = TauxTVA(Decimal("5.5"))
        montant = tva.calculer_montant_tva(Decimal("33"))
        assert montant == Decimal("1.82")

    # ─────────────────────────────────────────────────────────────────
    # Egalite, hash, repr
    # ─────────────────────────────────────────────────────────────────

    def test_egalite(self):
        """Test: deux TauxTVA avec meme taux sont egaux."""
        t1 = TauxTVA(Decimal("10.0"))
        t2 = TauxTVA(Decimal("10.0"))
        assert t1 == t2

    def test_inegalite(self):
        """Test: deux TauxTVA avec taux differents ne sont pas egaux."""
        t1 = TauxTVA(Decimal("5.5"))
        t2 = TauxTVA(Decimal("20.0"))
        assert t1 != t2

    def test_egalite_non_taux_tva(self):
        """Test: inegalite avec un objet non TauxTVA."""
        t = TauxTVA(Decimal("10.0"))
        assert t != "10.0"

    def test_hash_identique(self):
        """Test: meme hash pour meme taux."""
        t1 = TauxTVA(Decimal("5.5"))
        t2 = TauxTVA(Decimal("5.5"))
        assert hash(t1) == hash(t2)

    def test_repr(self):
        """Test: repr lisible."""
        t = TauxTVA(Decimal("10.0"))
        assert "10.0" in repr(t)

    def test_str(self):
        """Test: str affiche le pourcentage."""
        t = TauxTVA(Decimal("20.0"))
        assert str(t) == "20.0%"


class TestTauxDefautPourChantier:
    """Tests pour la resolution du taux TVA par defaut selon le contexte chantier (DEV-TVA)."""

    def test_renovation_habitation_plus_2ans(self):
        """Renovation standard + habitation > 2 ans -> 10%."""
        taux = TauxTVA.taux_defaut_pour_chantier(
            type_travaux="renovation",
            batiment_plus_2ans=True,
            usage_habitation=True,
        )
        assert taux == Decimal("10")

    def test_renovation_energetique_habitation_plus_2ans(self):
        """Renovation energetique + habitation > 2 ans -> 5.5%."""
        taux = TauxTVA.taux_defaut_pour_chantier(
            type_travaux="renovation_energetique",
            batiment_plus_2ans=True,
            usage_habitation=True,
        )
        assert taux == Decimal("5.5")

    def test_construction_neuve(self):
        """Construction neuve -> 20% (meme si habitation > 2 ans)."""
        taux = TauxTVA.taux_defaut_pour_chantier(
            type_travaux="construction_neuve",
            batiment_plus_2ans=True,
            usage_habitation=True,
        )
        assert taux == Decimal("20")

    def test_batiment_moins_2ans(self):
        """Renovation mais batiment < 2 ans -> 20%."""
        taux = TauxTVA.taux_defaut_pour_chantier(
            type_travaux="renovation",
            batiment_plus_2ans=False,
            usage_habitation=True,
        )
        assert taux == Decimal("20")

    def test_pas_habitation(self):
        """Renovation > 2 ans mais pas habitation -> 20%."""
        taux = TauxTVA.taux_defaut_pour_chantier(
            type_travaux="renovation",
            batiment_plus_2ans=True,
            usage_habitation=False,
        )
        assert taux == Decimal("20")

    def test_aucune_info(self):
        """Aucun contexte -> 20% (fallback standard)."""
        taux = TauxTVA.taux_defaut_pour_chantier(
            type_travaux=None,
            batiment_plus_2ans=None,
            usage_habitation=None,
        )
        assert taux == Decimal("20")

    def test_type_travaux_none_mais_batiment_ok(self):
        """Batiment ok mais pas de type travaux -> 20%."""
        taux = TauxTVA.taux_defaut_pour_chantier(
            type_travaux=None,
            batiment_plus_2ans=True,
            usage_habitation=True,
        )
        assert taux == Decimal("20")

    def test_batiment_none(self):
        """Batiment None (inconnu) -> 20%."""
        taux = TauxTVA.taux_defaut_pour_chantier(
            type_travaux="renovation",
            batiment_plus_2ans=None,
            usage_habitation=True,
        )
        assert taux == Decimal("20")
