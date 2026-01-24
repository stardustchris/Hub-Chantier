"""Tests unitaires pour le value object UniteCharge."""

import pytest

from modules.planning_charge.domain.value_objects import UniteCharge


class TestUniteCharge:
    """Tests pour le value object UniteCharge."""

    def test_heures_value(self):
        """Test valeur heures."""
        assert UniteCharge.HEURES.value == "heures"

    def test_jours_homme_value(self):
        """Test valeur jours/homme."""
        assert UniteCharge.JOURS_HOMME.value == "jours_homme"

    def test_label_short(self):
        """Test labels courts."""
        assert UniteCharge.HEURES.label == "Hrs"
        assert UniteCharge.JOURS_HOMME.label == "J/H"

    def test_label_long(self):
        """Test labels longs."""
        assert UniteCharge.HEURES.label_long == "Heures"
        assert UniteCharge.JOURS_HOMME.label_long == "Jours/Homme"

    def test_convertir_heures_to_heures(self):
        """Test conversion heures vers heures (identite)."""
        result = UniteCharge.HEURES.convertir(35.0)
        assert result == 35.0

    def test_convertir_heures_to_jours_homme(self):
        """Test conversion heures vers jours/homme."""
        result = UniteCharge.JOURS_HOMME.convertir(35.0)
        assert result == 5.0  # 35h / 7h = 5 J/H

    def test_convertir_with_custom_hours_per_day(self):
        """Test conversion avec heures par jour personnalisees."""
        result = UniteCharge.JOURS_HOMME.convertir(40.0, heures_par_jour=8.0)
        assert result == 5.0  # 40h / 8h = 5 J/H

    def test_convertir_zero_hours_per_day(self):
        """Test conversion avec 0 heures par jour."""
        result = UniteCharge.JOURS_HOMME.convertir(35.0, heures_par_jour=0.0)
        assert result == 0.0

    def test_formater_heures(self):
        """Test formatage en heures."""
        result = UniteCharge.HEURES.formater(35.5)
        assert result == "35.5h"

    def test_formater_jours_homme(self):
        """Test formatage en jours/homme."""
        result = UniteCharge.JOURS_HOMME.formater(5.0)
        assert result == "5.0 J/H"

    def test_from_string_heures(self):
        """Test creation depuis 'heures'."""
        assert UniteCharge.from_string("heures") == UniteCharge.HEURES
        assert UniteCharge.from_string("Hrs") == UniteCharge.HEURES
        assert UniteCharge.from_string("h") == UniteCharge.HEURES

    def test_from_string_jours_homme(self):
        """Test creation depuis 'jours_homme'."""
        assert UniteCharge.from_string("jours_homme") == UniteCharge.JOURS_HOMME
        assert UniteCharge.from_string("j/h") == UniteCharge.JOURS_HOMME
        assert UniteCharge.from_string("JH") == UniteCharge.JOURS_HOMME

    def test_from_string_invalid(self):
        """Test erreur si unite invalide."""
        with pytest.raises(ValueError, match="Unite invalide"):
            UniteCharge.from_string("invalid")
