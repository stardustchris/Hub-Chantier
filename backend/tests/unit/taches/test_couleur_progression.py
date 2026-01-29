"""Tests unitaires pour CouleurProgression value object."""

import pytest

from modules.taches.domain.value_objects.couleur_progression import CouleurProgression


class TestFromProgression:
    """Tests pour from_progression."""

    def test_zero_hours_returns_gris(self):
        """0 heures réalisées = gris (non commencé)."""
        assert CouleurProgression.from_progression(0, 100) == CouleurProgression.GRIS

    def test_zero_estimated_with_realized_returns_rouge(self):
        """0 heures estimées + heures réalisées > 0 = rouge."""
        assert CouleurProgression.from_progression(5, 0) == CouleurProgression.ROUGE

    def test_zero_estimated_zero_realized_returns_gris(self):
        """0 heures estimées + 0 réalisées = gris."""
        assert CouleurProgression.from_progression(0, 0) == CouleurProgression.GRIS

    def test_negative_estimated_with_realized_returns_rouge(self):
        """Heures estimées négatives + réalisées > 0 = rouge."""
        assert CouleurProgression.from_progression(5, -1) == CouleurProgression.ROUGE

    def test_ratio_under_80_returns_vert(self):
        """Ratio <= 80% = vert (dans les temps)."""
        assert CouleurProgression.from_progression(7, 10) == CouleurProgression.VERT
        assert CouleurProgression.from_progression(8, 10) == CouleurProgression.VERT

    def test_ratio_exactly_80_returns_vert(self):
        """Ratio = 80% = vert."""
        assert CouleurProgression.from_progression(80, 100) == CouleurProgression.VERT

    def test_ratio_between_80_and_100_returns_jaune(self):
        """Ratio entre 80% et 100% = jaune (attention)."""
        assert CouleurProgression.from_progression(9, 10) == CouleurProgression.JAUNE
        assert CouleurProgression.from_progression(85, 100) == CouleurProgression.JAUNE

    def test_ratio_exactly_100_returns_jaune(self):
        """Ratio = 100% = jaune."""
        assert CouleurProgression.from_progression(10, 10) == CouleurProgression.JAUNE

    def test_ratio_over_100_returns_rouge(self):
        """Ratio > 100% = rouge (dépassement)."""
        assert CouleurProgression.from_progression(11, 10) == CouleurProgression.ROUGE
        assert CouleurProgression.from_progression(200, 100) == CouleurProgression.ROUGE


class TestProperties:
    """Tests pour les propriétés de CouleurProgression."""

    def test_str(self):
        """__str__ retourne la valeur de l'enum."""
        assert str(CouleurProgression.VERT) == "vert"
        assert str(CouleurProgression.ROUGE) == "rouge"

    def test_hex_code(self):
        """hex_code retourne le code couleur."""
        assert CouleurProgression.GRIS.hex_code == "#9E9E9E"
        assert CouleurProgression.VERT.hex_code == "#4CAF50"
        assert CouleurProgression.JAUNE.hex_code == "#FFC107"
        assert CouleurProgression.ROUGE.hex_code == "#F44336"

    def test_display_name(self):
        """display_name retourne le texte d'affichage."""
        assert CouleurProgression.GRIS.display_name == "Non commence"
        assert CouleurProgression.VERT.display_name == "Dans les temps"
        assert CouleurProgression.JAUNE.display_name == "Attention"
        assert CouleurProgression.ROUGE.display_name == "Depassement"

    def test_icon(self):
        """icon retourne l'emoji."""
        assert CouleurProgression.VERT.icon == "🟢"
        assert CouleurProgression.ROUGE.icon == "🔴"

    def test_values(self):
        """Toutes les valeurs string sont correctes."""
        assert CouleurProgression.GRIS.value == "gris"
        assert CouleurProgression.VERT.value == "vert"
        assert CouleurProgression.JAUNE.value == "jaune"
        assert CouleurProgression.ROUGE.value == "rouge"
