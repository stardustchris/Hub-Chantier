"""Tests unitaires pour l'entite LotDevis.

DEV-03: Creation devis structure - Arborescence par lots/chapitres.
DEV-06: Gestion marges et coefficients - Marge par lot (priorite 2).
"""

import pytest
from datetime import datetime
from decimal import Decimal

from modules.devis.domain.entities.lot_devis import LotDevis


class TestLotDevisCreation:
    """Tests pour la creation d'un lot de devis."""

    def test_create_lot_valid(self):
        """Test: creation d'un lot valide."""
        lot = LotDevis(
            id=1,
            devis_id=10,
            code_lot="LOT-001",
            libelle="Gros oeuvre",
            ordre=1,
        )
        assert lot.id == 1
        assert lot.devis_id == 10
        assert lot.code_lot == "LOT-001"
        assert lot.libelle == "Gros oeuvre"
        assert lot.ordre == 1
        assert lot.taux_marge_lot is None
        assert lot.parent_id is None
        assert lot.montant_debourse_ht == Decimal("0")
        assert lot.montant_vente_ht == Decimal("0")

    def test_create_lot_avec_marge(self):
        """Test: creation d'un lot avec marge specifique."""
        lot = LotDevis(
            devis_id=10,
            code_lot="LOT-002",
            libelle="Electricite",
            taux_marge_lot=Decimal("20"),
        )
        assert lot.taux_marge_lot == Decimal("20")

    def test_create_lot_sous_chapitre(self):
        """Test: creation d'un sous-chapitre (avec parent_id)."""
        lot = LotDevis(
            devis_id=10,
            code_lot="LOT-001-A",
            libelle="Fondations",
            parent_id=1,
        )
        assert lot.parent_id == 1
        assert lot.est_sous_chapitre is True

    def test_create_lot_devis_id_zero(self):
        """Test: erreur si devis_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            LotDevis(devis_id=0, code_lot="LOT-001", libelle="Test")
        assert "devis" in str(exc_info.value).lower()

    def test_create_lot_devis_id_negatif(self):
        """Test: erreur si devis_id est negatif."""
        with pytest.raises(ValueError):
            LotDevis(devis_id=-1, code_lot="LOT-001", libelle="Test")

    def test_create_lot_code_vide(self):
        """Test: erreur si code du lot vide."""
        with pytest.raises(ValueError) as exc_info:
            LotDevis(devis_id=1, code_lot="", libelle="Test")
        assert "code" in str(exc_info.value).lower()

    def test_create_lot_code_espaces(self):
        """Test: erreur si code du lot uniquement espaces."""
        with pytest.raises(ValueError):
            LotDevis(devis_id=1, code_lot="   ", libelle="Test")

    def test_create_lot_libelle_vide(self):
        """Test: erreur si libelle vide."""
        with pytest.raises(ValueError) as exc_info:
            LotDevis(devis_id=1, code_lot="LOT-001", libelle="")
        assert "libelle" in str(exc_info.value).lower()

    def test_create_lot_libelle_espaces(self):
        """Test: erreur si libelle uniquement espaces."""
        with pytest.raises(ValueError):
            LotDevis(devis_id=1, code_lot="LOT-001", libelle="   ")

    def test_create_lot_marge_negative(self):
        """Test: erreur si taux de marge negatif."""
        with pytest.raises(ValueError) as exc_info:
            LotDevis(
                devis_id=1,
                code_lot="LOT-001",
                libelle="Test",
                taux_marge_lot=Decimal("-1"),
            )
        assert "marge" in str(exc_info.value).lower()

    def test_create_lot_marge_zero(self):
        """Test: taux de marge a zero est accepte."""
        lot = LotDevis(
            devis_id=1,
            code_lot="LOT-001",
            libelle="Test",
            taux_marge_lot=Decimal("0"),
        )
        assert lot.taux_marge_lot == Decimal("0")

    def test_create_lot_marge_none(self):
        """Test: taux de marge None est accepte (utilise marge parente)."""
        lot = LotDevis(
            devis_id=1,
            code_lot="LOT-001",
            libelle="Test",
        )
        assert lot.taux_marge_lot is None


class TestLotDevisProprietes:
    """Tests pour les proprietes calculees."""

    def test_est_sous_chapitre_oui(self):
        """Test: lot avec parent est un sous-chapitre."""
        lot = LotDevis(
            devis_id=1, code_lot="LOT-001-A", libelle="Sous-lot", parent_id=5
        )
        assert lot.est_sous_chapitre is True

    def test_est_sous_chapitre_non(self):
        """Test: lot sans parent n'est pas un sous-chapitre."""
        lot = LotDevis(devis_id=1, code_lot="LOT-001", libelle="Lot principal")
        assert lot.est_sous_chapitre is False

    def test_est_supprime_non(self):
        """Test: lot non supprime."""
        lot = LotDevis(devis_id=1, code_lot="LOT-001", libelle="Test")
        assert lot.est_supprime is False

    def test_est_supprime_oui(self):
        """Test: lot supprime."""
        lot = LotDevis(
            devis_id=1,
            code_lot="LOT-001",
            libelle="Test",
            deleted_at=datetime.utcnow(),
        )
        assert lot.est_supprime is True


class TestLotDevisSoftDelete:
    """Tests pour le soft delete."""

    def test_supprimer(self):
        """Test: suppression en soft delete."""
        lot = LotDevis(devis_id=1, code_lot="LOT-001", libelle="Test")
        assert lot.est_supprime is False
        lot.supprimer(deleted_by=1)
        assert lot.est_supprime is True
        assert lot.deleted_at is not None
        assert lot.deleted_by == 1


class TestLotDevisToDict:
    """Tests pour la conversion en dictionnaire."""

    def test_to_dict(self):
        """Test: conversion en dictionnaire."""
        lot = LotDevis(
            id=1,
            devis_id=10,
            code_lot="LOT-001",
            libelle="Gros oeuvre",
            ordre=1,
            taux_marge_lot=Decimal("18"),
            montant_debourse_ht=Decimal("50000"),
            montant_vente_ht=Decimal("59000"),
        )
        d = lot.to_dict()
        assert d["id"] == 1
        assert d["devis_id"] == 10
        assert d["code_lot"] == "LOT-001"
        assert d["libelle"] == "Gros oeuvre"
        assert d["ordre"] == 1
        assert d["taux_marge_lot"] == "18"
        assert d["montant_debourse_ht"] == "50000"
        assert d["montant_vente_ht"] == "59000"
        assert d["parent_id"] is None

    def test_to_dict_marge_none(self):
        """Test: marge None dans to_dict."""
        lot = LotDevis(devis_id=1, code_lot="LOT-001", libelle="Test")
        d = lot.to_dict()
        assert d["taux_marge_lot"] is None
