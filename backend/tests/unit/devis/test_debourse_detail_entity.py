"""Tests unitaires pour l'entite DebourseDetail.

DEV-05: Detail debourses avances - Breakdown par ligne.
"""

import pytest
from datetime import datetime
from decimal import Decimal

from modules.devis.domain.entities.debourse_detail import DebourseDetail
from modules.devis.domain.value_objects.type_debourse import TypeDebourse


class TestDebourseDetailCreation:
    """Tests pour la creation d'un debourse detail."""

    def test_create_debourse_valid(self):
        """Test: creation d'un debourse valide."""
        debourse = DebourseDetail(
            id=1,
            ligne_devis_id=10,
            type_debourse=TypeDebourse.MATERIAUX,
            libelle="Ciment Portland CEM I",
            quantite=Decimal("50"),
            prix_unitaire=Decimal("12.50"),
        )
        assert debourse.id == 1
        assert debourse.ligne_devis_id == 10
        assert debourse.type_debourse == TypeDebourse.MATERIAUX
        assert debourse.libelle == "Ciment Portland CEM I"
        assert debourse.quantite == Decimal("50")
        assert debourse.prix_unitaire == Decimal("12.50")
        assert debourse.total == Decimal("0")

    def test_create_debourse_minimal(self):
        """Test: creation d'un debourse avec le minimum requis."""
        debourse = DebourseDetail(ligne_devis_id=1, libelle="Test")
        assert debourse.ligne_devis_id == 1
        assert debourse.libelle == "Test"
        assert debourse.type_debourse == TypeDebourse.MATERIAUX
        assert debourse.quantite == Decimal("0")
        assert debourse.prix_unitaire == Decimal("0")

    def test_create_debourse_moe(self):
        """Test: creation d'un debourse main d'oeuvre avec taux horaire."""
        debourse = DebourseDetail(
            ligne_devis_id=1,
            type_debourse=TypeDebourse.MOE,
            libelle="Macon qualifie",
            quantite=Decimal("8"),
            prix_unitaire=Decimal("35"),
            metier="macon",
            taux_horaire=Decimal("35"),
        )
        assert debourse.type_debourse == TypeDebourse.MOE
        assert debourse.metier == "macon"
        assert debourse.taux_horaire == Decimal("35")
        assert debourse.est_moe is True

    def test_create_debourse_sous_traitance(self):
        """Test: creation d'un debourse sous-traitance."""
        debourse = DebourseDetail(
            ligne_devis_id=1,
            type_debourse=TypeDebourse.SOUS_TRAITANCE,
            libelle="Plomberie sous-traitee",
            quantite=Decimal("1"),
            prix_unitaire=Decimal("5000"),
        )
        assert debourse.type_debourse == TypeDebourse.SOUS_TRAITANCE
        assert debourse.est_moe is False

    def test_create_debourse_deplacement(self):
        """Test: creation d'un debourse deplacement."""
        debourse = DebourseDetail(
            ligne_devis_id=1,
            type_debourse=TypeDebourse.DEPLACEMENT,
            libelle="Frais de deplacement",
            quantite=Decimal("5"),
            prix_unitaire=Decimal("0.50"),
        )
        assert debourse.type_debourse == TypeDebourse.DEPLACEMENT

    def test_create_debourse_ligne_devis_id_zero(self):
        """Test: erreur si ligne_devis_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            DebourseDetail(ligne_devis_id=0, libelle="Test")
        assert "ligne" in str(exc_info.value).lower()

    def test_create_debourse_ligne_devis_id_negatif(self):
        """Test: erreur si ligne_devis_id est negatif."""
        with pytest.raises(ValueError):
            DebourseDetail(ligne_devis_id=-1, libelle="Test")

    def test_create_debourse_libelle_vide(self):
        """Test: erreur si libelle vide."""
        with pytest.raises(ValueError) as exc_info:
            DebourseDetail(ligne_devis_id=1, libelle="")
        assert "libelle" in str(exc_info.value).lower()

    def test_create_debourse_libelle_espaces(self):
        """Test: erreur si libelle uniquement espaces."""
        with pytest.raises(ValueError):
            DebourseDetail(ligne_devis_id=1, libelle="   ")

    def test_create_debourse_quantite_negative(self):
        """Test: erreur si quantite negative."""
        with pytest.raises(ValueError) as exc_info:
            DebourseDetail(
                ligne_devis_id=1,
                libelle="Test",
                quantite=Decimal("-1"),
            )
        assert "quantite" in str(exc_info.value).lower()

    def test_create_debourse_quantite_zero(self):
        """Test: quantite a zero est acceptee."""
        debourse = DebourseDetail(
            ligne_devis_id=1,
            libelle="Test",
            quantite=Decimal("0"),
        )
        assert debourse.quantite == Decimal("0")

    def test_create_debourse_prix_negatif(self):
        """Test: erreur si prix unitaire negatif."""
        with pytest.raises(ValueError) as exc_info:
            DebourseDetail(
                ligne_devis_id=1,
                libelle="Test",
                prix_unitaire=Decimal("-1"),
            )
        assert "prix" in str(exc_info.value).lower()

    def test_create_debourse_prix_zero(self):
        """Test: prix unitaire a zero est accepte."""
        debourse = DebourseDetail(
            ligne_devis_id=1,
            libelle="Test",
            prix_unitaire=Decimal("0"),
        )
        assert debourse.prix_unitaire == Decimal("0")

    def test_create_debourse_taux_horaire_negatif(self):
        """Test: erreur si taux horaire negatif."""
        with pytest.raises(ValueError) as exc_info:
            DebourseDetail(
                ligne_devis_id=1,
                type_debourse=TypeDebourse.MOE,
                libelle="Macon",
                taux_horaire=Decimal("-10"),
            )
        assert "taux" in str(exc_info.value).lower()

    def test_create_debourse_taux_horaire_zero(self):
        """Test: taux horaire a zero est accepte."""
        debourse = DebourseDetail(
            ligne_devis_id=1,
            type_debourse=TypeDebourse.MOE,
            libelle="Benevole",
            taux_horaire=Decimal("0"),
        )
        assert debourse.taux_horaire == Decimal("0")

    def test_create_debourse_taux_horaire_none(self):
        """Test: taux horaire None est accepte."""
        debourse = DebourseDetail(
            ligne_devis_id=1,
            libelle="Test",
            taux_horaire=None,
        )
        assert debourse.taux_horaire is None


class TestDebourseDetailProprietes:
    """Tests pour les proprietes calculees."""

    def _make_debourse(self, **kwargs):
        """Cree un debourse valide avec valeurs par defaut."""
        defaults = {"ligne_devis_id": 1, "libelle": "Test debourse"}
        defaults.update(kwargs)
        return DebourseDetail(**defaults)

    def test_montant_calcule(self):
        """Test: montant calcule = quantite * prix unitaire."""
        debourse = self._make_debourse(
            quantite=Decimal("10"),
            prix_unitaire=Decimal("25.50"),
        )
        assert debourse.montant_calcule == Decimal("255.00")

    def test_montant_calcule_zero(self):
        """Test: montant calcule a zero."""
        debourse = self._make_debourse(
            quantite=Decimal("0"),
            prix_unitaire=Decimal("50"),
        )
        assert debourse.montant_calcule == Decimal("0")

    def test_montant_calcule_decimales(self):
        """Test: montant calcule avec decimales."""
        debourse = self._make_debourse(
            quantite=Decimal("2.5"),
            prix_unitaire=Decimal("30.20"),
        )
        assert debourse.montant_calcule == Decimal("75.500")

    def test_est_moe_true(self):
        """Test: est_moe retourne True pour type MOE."""
        debourse = self._make_debourse(type_debourse=TypeDebourse.MOE)
        assert debourse.est_moe is True

    def test_est_moe_false_materiaux(self):
        """Test: est_moe retourne False pour type MATERIAUX."""
        debourse = self._make_debourse(type_debourse=TypeDebourse.MATERIAUX)
        assert debourse.est_moe is False

    def test_est_moe_false_sous_traitance(self):
        """Test: est_moe retourne False pour type SOUS_TRAITANCE."""
        debourse = self._make_debourse(type_debourse=TypeDebourse.SOUS_TRAITANCE)
        assert debourse.est_moe is False

    def test_est_moe_false_materiel(self):
        """Test: est_moe retourne False pour type MATERIEL."""
        debourse = self._make_debourse(type_debourse=TypeDebourse.MATERIEL)
        assert debourse.est_moe is False

    def test_est_moe_false_deplacement(self):
        """Test: est_moe retourne False pour type DEPLACEMENT."""
        debourse = self._make_debourse(type_debourse=TypeDebourse.DEPLACEMENT)
        assert debourse.est_moe is False


class TestDebourseDetailToDict:
    """Tests pour la conversion en dictionnaire."""

    def test_to_dict_materiaux(self):
        """Test: conversion en dictionnaire pour type MATERIAUX."""
        debourse = DebourseDetail(
            id=1,
            ligne_devis_id=10,
            type_debourse=TypeDebourse.MATERIAUX,
            libelle="Ciment",
            quantite=Decimal("50"),
            prix_unitaire=Decimal("12.50"),
            total=Decimal("625"),
        )
        d = debourse.to_dict()
        assert d["id"] == 1
        assert d["ligne_devis_id"] == 10
        assert d["type_debourse"] == "materiaux"
        assert d["libelle"] == "Ciment"
        assert d["quantite"] == "50"
        assert d["prix_unitaire"] == "12.50"
        assert d["total"] == "625"
        # Pas de champs MOE pour MATERIAUX
        assert "metier" not in d
        assert "taux_horaire" not in d

    def test_to_dict_moe(self):
        """Test: conversion en dictionnaire pour type MOE."""
        debourse = DebourseDetail(
            id=2,
            ligne_devis_id=10,
            type_debourse=TypeDebourse.MOE,
            libelle="Macon qualifie",
            quantite=Decimal("8"),
            prix_unitaire=Decimal("35"),
            metier="macon",
            taux_horaire=Decimal("35"),
            total=Decimal("280"),
        )
        d = debourse.to_dict()
        assert d["type_debourse"] == "moe"
        assert d["metier"] == "macon"
        assert d["taux_horaire"] == "35"

    def test_to_dict_moe_sans_taux_horaire(self):
        """Test: MOE sans taux horaire dans to_dict."""
        debourse = DebourseDetail(
            id=3,
            ligne_devis_id=10,
            type_debourse=TypeDebourse.MOE,
            libelle="Aide",
            quantite=Decimal("4"),
            prix_unitaire=Decimal("20"),
        )
        d = debourse.to_dict()
        assert d["metier"] is None
        assert d["taux_horaire"] is None
