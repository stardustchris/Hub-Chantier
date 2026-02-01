"""Tests unitaires pour l'entite LigneDevis.

DEV-03: Creation devis structure - Lignes avec quantites et prix.
DEV-06: Gestion marges et coefficients - Marge par ligne (priorite 1).
DEV-04: Metres numeriques - Verrouillage des quantites.
"""

import pytest
from datetime import datetime
from decimal import Decimal

from modules.devis.domain.entities.ligne_devis import LigneDevis
from modules.devis.domain.value_objects.unite_article import UniteArticle


class TestLigneDevisCreation:
    """Tests pour la creation d'une ligne de devis."""

    def test_create_ligne_valid(self):
        """Test: creation d'une ligne valide."""
        ligne = LigneDevis(
            id=1,
            lot_devis_id=10,
            libelle="Beton C25/30",
            unite=UniteArticle.M3,
            quantite=Decimal("25.5"),
            prix_unitaire_ht=Decimal("95.50"),
            ordre=1,
        )
        assert ligne.id == 1
        assert ligne.lot_devis_id == 10
        assert ligne.libelle == "Beton C25/30"
        assert ligne.unite == UniteArticle.M3
        assert ligne.quantite == Decimal("25.5")
        assert ligne.prix_unitaire_ht == Decimal("95.50")
        assert ligne.ordre == 1
        assert ligne.taux_marge_ligne is None
        assert ligne.verrouille is False
        assert ligne.article_id is None

    def test_create_ligne_minimal(self):
        """Test: creation d'une ligne avec le minimum requis."""
        ligne = LigneDevis(lot_devis_id=1, libelle="Test")
        assert ligne.lot_devis_id == 1
        assert ligne.libelle == "Test"
        assert ligne.unite == UniteArticle.U
        assert ligne.quantite == Decimal("0")
        assert ligne.prix_unitaire_ht == Decimal("0")
        assert ligne.taux_marge_ligne is None
        assert ligne.total_ht == Decimal("0")

    def test_create_ligne_avec_marge(self):
        """Test: creation d'une ligne avec marge specifique."""
        ligne = LigneDevis(
            lot_devis_id=1,
            libelle="Ligne avec marge",
            taux_marge_ligne=Decimal("25"),
        )
        assert ligne.taux_marge_ligne == Decimal("25")

    def test_create_ligne_avec_article(self):
        """Test: creation d'une ligne liee a un article."""
        ligne = LigneDevis(
            lot_devis_id=1,
            libelle="Depuis bibliotheque",
            article_id=42,
        )
        assert ligne.article_id == 42

    def test_create_ligne_lot_devis_id_zero(self):
        """Test: erreur si lot_devis_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            LigneDevis(lot_devis_id=0, libelle="Test")
        assert "lot" in str(exc_info.value).lower()

    def test_create_ligne_lot_devis_id_negatif(self):
        """Test: erreur si lot_devis_id est negatif."""
        with pytest.raises(ValueError):
            LigneDevis(lot_devis_id=-1, libelle="Test")

    def test_create_ligne_libelle_vide(self):
        """Test: erreur si libelle vide."""
        with pytest.raises(ValueError) as exc_info:
            LigneDevis(lot_devis_id=1, libelle="")
        assert "libelle" in str(exc_info.value).lower()

    def test_create_ligne_libelle_espaces(self):
        """Test: erreur si libelle uniquement espaces."""
        with pytest.raises(ValueError):
            LigneDevis(lot_devis_id=1, libelle="   ")

    def test_create_ligne_quantite_negative(self):
        """Test: erreur si quantite negative."""
        with pytest.raises(ValueError) as exc_info:
            LigneDevis(
                lot_devis_id=1,
                libelle="Test",
                quantite=Decimal("-1"),
            )
        assert "quantite" in str(exc_info.value).lower()

    def test_create_ligne_quantite_zero(self):
        """Test: quantite a zero est acceptee."""
        ligne = LigneDevis(
            lot_devis_id=1,
            libelle="Test",
            quantite=Decimal("0"),
        )
        assert ligne.quantite == Decimal("0")

    def test_create_ligne_prix_negatif(self):
        """Test: erreur si prix unitaire negatif."""
        with pytest.raises(ValueError) as exc_info:
            LigneDevis(
                lot_devis_id=1,
                libelle="Test",
                prix_unitaire_ht=Decimal("-1"),
            )
        assert "prix" in str(exc_info.value).lower()

    def test_create_ligne_prix_zero(self):
        """Test: prix unitaire a zero est accepte."""
        ligne = LigneDevis(
            lot_devis_id=1,
            libelle="Test",
            prix_unitaire_ht=Decimal("0"),
        )
        assert ligne.prix_unitaire_ht == Decimal("0")

    def test_create_ligne_marge_negative(self):
        """Test: erreur si taux de marge de ligne negatif."""
        with pytest.raises(ValueError) as exc_info:
            LigneDevis(
                lot_devis_id=1,
                libelle="Test",
                taux_marge_ligne=Decimal("-5"),
            )
        assert "marge" in str(exc_info.value).lower()

    def test_create_ligne_marge_zero(self):
        """Test: taux de marge a zero est accepte."""
        ligne = LigneDevis(
            lot_devis_id=1,
            libelle="Test",
            taux_marge_ligne=Decimal("0"),
        )
        assert ligne.taux_marge_ligne == Decimal("0")

    def test_create_ligne_marge_none(self):
        """Test: taux de marge None est accepte (utilise marge parente)."""
        ligne = LigneDevis(lot_devis_id=1, libelle="Test")
        assert ligne.taux_marge_ligne is None


class TestLigneDevisProprietes:
    """Tests pour les proprietes calculees."""

    def _make_ligne(self, **kwargs):
        """Cree une ligne valide avec valeurs par defaut."""
        defaults = {"lot_devis_id": 1, "libelle": "Test ligne"}
        defaults.update(kwargs)
        return LigneDevis(**defaults)

    def test_montant_ht_calcul(self):
        """Test: montant HT = quantite * prix unitaire."""
        ligne = self._make_ligne(
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("50"),
        )
        assert ligne.montant_ht == Decimal("500")

    def test_montant_ht_zero(self):
        """Test: montant HT a zero si quantite ou prix nul."""
        ligne = self._make_ligne(
            quantite=Decimal("0"),
            prix_unitaire_ht=Decimal("50"),
        )
        assert ligne.montant_ht == Decimal("0")

    def test_montant_ht_decimales(self):
        """Test: montant HT avec decimales."""
        ligne = self._make_ligne(
            quantite=Decimal("2.5"),
            prix_unitaire_ht=Decimal("30.20"),
        )
        assert ligne.montant_ht == Decimal("75.500")

    def test_est_supprime_non(self):
        """Test: ligne non supprimee."""
        ligne = self._make_ligne()
        assert ligne.est_supprime is False

    def test_est_supprime_oui(self):
        """Test: ligne supprimee."""
        ligne = self._make_ligne(deleted_at=datetime.utcnow())
        assert ligne.est_supprime is True


class TestLigneDevisVerrouillage:
    """Tests pour le verrouillage de quantite (DEV-04: metres numeriques)."""

    def _make_ligne(self, **kwargs):
        """Cree une ligne valide avec valeurs par defaut."""
        defaults = {
            "lot_devis_id": 1,
            "libelle": "Test ligne",
            "quantite": Decimal("10"),
            "prix_unitaire_ht": Decimal("50"),
        }
        defaults.update(kwargs)
        return LigneDevis(**defaults)

    def test_verrouiller(self):
        """Test: verrouillage de la quantite."""
        ligne = self._make_ligne()
        assert ligne.verrouille is False
        ligne.verrouiller()
        assert ligne.verrouille is True
        assert ligne.updated_at is not None

    def test_deverrouiller(self):
        """Test: deverrouillage de la quantite."""
        ligne = self._make_ligne(verrouille=True)
        ligne.deverrouiller()
        assert ligne.verrouille is False
        assert ligne.updated_at is not None

    def test_modifier_quantite_success(self):
        """Test: modification de quantite reussie."""
        ligne = self._make_ligne()
        ligne.modifier_quantite(Decimal("20"))
        assert ligne.quantite == Decimal("20")
        assert ligne.total_ht == ligne.montant_ht
        assert ligne.updated_at is not None

    def test_modifier_quantite_verrouillee(self):
        """Test: erreur si la quantite est verrouillee."""
        ligne = self._make_ligne(verrouille=True)
        with pytest.raises(ValueError) as exc_info:
            ligne.modifier_quantite(Decimal("20"))
        assert "verrouillee" in str(exc_info.value).lower()

    def test_modifier_quantite_negative(self):
        """Test: erreur si nouvelle quantite negative."""
        ligne = self._make_ligne()
        with pytest.raises(ValueError) as exc_info:
            ligne.modifier_quantite(Decimal("-5"))
        assert "quantite" in str(exc_info.value).lower()

    def test_modifier_quantite_zero(self):
        """Test: modification de quantite a zero est acceptee."""
        ligne = self._make_ligne()
        ligne.modifier_quantite(Decimal("0"))
        assert ligne.quantite == Decimal("0")
        assert ligne.total_ht == Decimal("0")

    def test_modifier_quantite_met_a_jour_total_ht(self):
        """Test: modifier_quantite met a jour total_ht correctement."""
        ligne = self._make_ligne(
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("50"),
        )
        ligne.modifier_quantite(Decimal("20"))
        # total_ht = montant_ht = 20 * 50 = 1000
        assert ligne.total_ht == Decimal("1000")


class TestLigneDevisSoftDelete:
    """Tests pour le soft delete."""

    def test_supprimer(self):
        """Test: suppression en soft delete."""
        ligne = LigneDevis(lot_devis_id=1, libelle="Test")
        assert ligne.est_supprime is False
        ligne.supprimer(deleted_by=1)
        assert ligne.est_supprime is True
        assert ligne.deleted_at is not None
        assert ligne.deleted_by == 1


class TestLigneDevisToDict:
    """Tests pour la conversion en dictionnaire."""

    def test_to_dict_basic(self):
        """Test: conversion en dictionnaire."""
        ligne = LigneDevis(
            id=1,
            lot_devis_id=10,
            libelle="Beton C25/30",
            unite=UniteArticle.M3,
            quantite=Decimal("25.5"),
            prix_unitaire_ht=Decimal("95.50"),
            ordre=2,
            verrouille=True,
        )
        d = ligne.to_dict()
        assert d["id"] == 1
        assert d["lot_devis_id"] == 10
        assert d["libelle"] == "Beton C25/30"
        assert d["unite"] == "m3"
        assert d["quantite"] == "25.5"
        assert d["prix_unitaire_ht"] == "95.50"
        assert d["ordre"] == 2
        assert d["verrouille"] is True
        assert d["taux_marge_ligne"] is None

    def test_to_dict_avec_marge(self):
        """Test: marge dans to_dict."""
        ligne = LigneDevis(
            id=1,
            lot_devis_id=10,
            libelle="Test",
            taux_marge_ligne=Decimal("25"),
        )
        d = ligne.to_dict()
        assert d["taux_marge_ligne"] == "25"

    def test_to_dict_article_id(self):
        """Test: article_id dans to_dict."""
        ligne = LigneDevis(
            id=1,
            lot_devis_id=10,
            libelle="Test",
            article_id=42,
        )
        d = ligne.to_dict()
        assert d["article_id"] == 42
