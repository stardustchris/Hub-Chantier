"""Tests pour les Value Objects du module Taches."""

import pytest

from modules.taches.domain.value_objects import (
    StatutTache,
    UniteMesure,
    CouleurProgression,
)


class TestStatutTache:
    """Tests pour StatutTache."""

    def test_statut_a_faire(self):
        """Test statut A faire."""
        statut = StatutTache.A_FAIRE
        assert statut.value == "a_faire"
        assert statut.display_name == "A faire"
        assert statut.icon == "☐"

    def test_statut_termine(self):
        """Test statut Termine."""
        statut = StatutTache.TERMINE
        assert statut.value == "termine"
        assert statut.display_name == "Termine"
        assert statut.icon == "✅"

    def test_from_string(self):
        """Test creation depuis string."""
        assert StatutTache.from_string("a_faire") == StatutTache.A_FAIRE
        assert StatutTache.from_string("termine") == StatutTache.TERMINE

    def test_from_string_invalid(self):
        """Test erreur pour string invalide."""
        with pytest.raises(ValueError):
            StatutTache.from_string("invalid")


class TestUniteMesure:
    """Tests pour UniteMesure."""

    def test_unites_disponibles(self):
        """Test que toutes les unites sont disponibles."""
        assert UniteMesure.M2.value == "m2"
        assert UniteMesure.M3.value == "m3"
        assert UniteMesure.ML.value == "ml"
        assert UniteMesure.KG.value == "kg"
        assert UniteMesure.LITRE.value == "litre"
        assert UniteMesure.UNITE.value == "unite"
        assert UniteMesure.HEURE.value == "heure"

    def test_display_name(self):
        """Test noms d'affichage."""
        assert UniteMesure.M2.display_name == "m²"
        assert UniteMesure.M3.display_name == "m³"

    def test_from_string(self):
        """Test creation depuis string."""
        assert UniteMesure.from_string("m2") == UniteMesure.M2
        assert UniteMesure.from_string("kg") == UniteMesure.KG

    def test_from_string_invalid(self):
        """Test erreur pour string invalide."""
        with pytest.raises(ValueError):
            UniteMesure.from_string("invalid")

    def test_list_all(self):
        """Test liste de toutes les unites."""
        unites = UniteMesure.list_all()
        assert len(unites) == len(UniteMesure)
        assert {"value": "m2", "display": "m²"} in unites


class TestCouleurProgression:
    """Tests pour CouleurProgression (TAC-20)."""

    def test_couleurs_disponibles(self):
        """Test que toutes les couleurs sont disponibles."""
        assert CouleurProgression.GRIS.value == "gris"
        assert CouleurProgression.VERT.value == "vert"
        assert CouleurProgression.JAUNE.value == "jaune"
        assert CouleurProgression.ROUGE.value == "rouge"

    def test_hex_codes(self):
        """Test codes hexadecimaux."""
        assert CouleurProgression.GRIS.hex_code == "#9E9E9E"
        assert CouleurProgression.VERT.hex_code == "#4CAF50"
        assert CouleurProgression.JAUNE.hex_code == "#FFC107"
        assert CouleurProgression.ROUGE.hex_code == "#F44336"

    def test_from_progression_gris(self):
        """Test couleur gris (0 heures)."""
        couleur = CouleurProgression.from_progression(0, 10)
        assert couleur == CouleurProgression.GRIS

    def test_from_progression_vert(self):
        """Test couleur verte (<= 80%)."""
        couleur = CouleurProgression.from_progression(7, 10)
        assert couleur == CouleurProgression.VERT

        couleur = CouleurProgression.from_progression(8, 10)
        assert couleur == CouleurProgression.VERT

    def test_from_progression_jaune(self):
        """Test couleur jaune (80% < x <= 100%)."""
        couleur = CouleurProgression.from_progression(8.1, 10)
        assert couleur == CouleurProgression.JAUNE

        couleur = CouleurProgression.from_progression(10, 10)
        assert couleur == CouleurProgression.JAUNE

    def test_from_progression_rouge(self):
        """Test couleur rouge (> 100%)."""
        couleur = CouleurProgression.from_progression(11, 10)
        assert couleur == CouleurProgression.ROUGE

    def test_from_progression_no_estimate(self):
        """Test avec heures estimees a 0."""
        couleur = CouleurProgression.from_progression(5, 0)
        assert couleur == CouleurProgression.ROUGE
