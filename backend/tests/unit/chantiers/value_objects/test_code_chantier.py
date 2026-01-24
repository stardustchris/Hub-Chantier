"""Tests unitaires pour CodeChantier Value Object."""

import pytest

from modules.chantiers.domain.value_objects import CodeChantier


class TestCodeChantier:
    """Tests pour le Value Object CodeChantier (CHT-19)."""

    # ==========================================================================
    # Tests de création valide
    # ==========================================================================

    def test_create_valid_code_uppercase(self):
        """Test: création avec code majuscule valide."""
        code = CodeChantier("A001")
        assert code.value == "A001"
        assert str(code) == "A001"

    def test_create_valid_code_lowercase_normalized(self):
        """Test: les minuscules sont normalisées en majuscules."""
        code = CodeChantier("b023")
        assert code.value == "B023"

    def test_create_valid_code_with_spaces_trimmed(self):
        """Test: les espaces sont supprimés."""
        code = CodeChantier("  C456  ")
        assert code.value == "C456"

    def test_create_valid_code_z999(self):
        """Test: le code maximum Z999 est valide."""
        code = CodeChantier("Z999")
        assert code.value == "Z999"

    # ==========================================================================
    # Tests de création invalide
    # ==========================================================================

    def test_create_empty_raises_error(self):
        """Test: code vide lève une erreur."""
        with pytest.raises(ValueError) as exc_info:
            CodeChantier("")
        assert "vide" in str(exc_info.value).lower()

    def test_create_invalid_format_no_digits_raises_error(self):
        """Test: code sans chiffres lève une erreur."""
        with pytest.raises(ValueError) as exc_info:
            CodeChantier("ABCD")
        assert "Format" in str(exc_info.value)

    def test_create_invalid_format_no_letter_raises_error(self):
        """Test: code sans lettre lève une erreur."""
        with pytest.raises(ValueError) as exc_info:
            CodeChantier("1234")
        assert "Format" in str(exc_info.value)

    def test_create_invalid_format_too_many_digits_raises_error(self):
        """Test: code avec trop de chiffres lève une erreur."""
        with pytest.raises(ValueError) as exc_info:
            CodeChantier("A1234")
        assert "Format" in str(exc_info.value)

    def test_create_invalid_format_two_letters_raises_error(self):
        """Test: code avec deux lettres lève une erreur."""
        with pytest.raises(ValueError) as exc_info:
            CodeChantier("AB01")
        assert "Format" in str(exc_info.value)

    # ==========================================================================
    # Tests des propriétés
    # ==========================================================================

    def test_letter_property(self):
        """Test: la propriété letter retourne la lettre."""
        code = CodeChantier("B123")
        assert code.letter == "B"

    def test_number_property(self):
        """Test: la propriété number retourne le numéro."""
        code = CodeChantier("B123")
        assert code.number == 123

    def test_number_property_leading_zeros(self):
        """Test: la propriété number gère les zéros initiaux."""
        code = CodeChantier("A001")
        assert code.number == 1

    # ==========================================================================
    # Tests de génération de code suivant
    # ==========================================================================

    def test_generate_next_from_none(self):
        """Test: génération du premier code A001."""
        code = CodeChantier.generate_next(None)
        assert code.value == "A001"

    def test_generate_next_increment_number(self):
        """Test: incrémentation du numéro."""
        code = CodeChantier.generate_next("A001")
        assert code.value == "A002"

    def test_generate_next_increment_to_999(self):
        """Test: incrémentation jusqu'à 999."""
        code = CodeChantier.generate_next("A998")
        assert code.value == "A999"

    def test_generate_next_letter_rollover(self):
        """Test: passage à la lettre suivante après 999."""
        code = CodeChantier.generate_next("A999")
        assert code.value == "B001"

    def test_generate_next_z999_raises_error(self):
        """Test: Z999 ne peut pas être incrémenté."""
        with pytest.raises(ValueError) as exc_info:
            CodeChantier.generate_next("Z999")
        assert "maximale" in str(exc_info.value).lower()

    # ==========================================================================
    # Tests de comparaison
    # ==========================================================================

    def test_equality(self):
        """Test: deux codes identiques sont égaux."""
        code1 = CodeChantier("A001")
        code2 = CodeChantier("A001")
        assert code1 == code2

    def test_inequality(self):
        """Test: deux codes différents ne sont pas égaux."""
        code1 = CodeChantier("A001")
        code2 = CodeChantier("A002")
        assert code1 != code2

    def test_less_than(self):
        """Test: comparaison pour tri."""
        code1 = CodeChantier("A001")
        code2 = CodeChantier("A002")
        code3 = CodeChantier("B001")
        assert code1 < code2
        assert code2 < code3

    def test_immutability(self):
        """Test: le code est immuable (frozen)."""
        code = CodeChantier("A001")
        with pytest.raises(AttributeError):
            code.value = "B002"
