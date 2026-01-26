"""Tests unitaires pour CodeChantier value object."""

import pytest
from dataclasses import FrozenInstanceError

from modules.chantiers.domain.value_objects.code_chantier import CodeChantier


class TestCodeChantier:
    """Tests pour CodeChantier."""

    def test_create_valid_code(self):
        """Test création d'un code valide."""
        code = CodeChantier("A001")

        assert code.value == "A001"

    def test_create_lowercase_normalized(self):
        """Test normalisation en majuscules."""
        code = CodeChantier("a001")

        assert code.value == "A001"

    def test_create_with_spaces_stripped(self):
        """Test suppression des espaces."""
        code = CodeChantier("  A001  ")

        assert code.value == "A001"

    def test_create_special_code_conges(self):
        """Test création code spécial CONGES."""
        code = CodeChantier("CONGES")

        assert code.value == "CONGES"
        assert code.is_special is True

    def test_create_special_code_maladie(self):
        """Test création code spécial MALADIE."""
        code = CodeChantier("maladie")

        assert code.value == "MALADIE"
        assert code.is_special is True

    def test_create_special_code_formation(self):
        """Test création code spécial FORMATION."""
        code = CodeChantier("Formation")

        assert code.value == "FORMATION"

    def test_create_special_code_rtt(self):
        """Test création code spécial RTT."""
        code = CodeChantier("rtt")

        assert code.value == "RTT"

    def test_create_special_code_absent(self):
        """Test création code spécial ABSENT."""
        code = CodeChantier("ABSENT")

        assert code.value == "ABSENT"

    def test_empty_code_raises(self):
        """Test erreur si code vide."""
        with pytest.raises(ValueError, match="Le code chantier ne peut pas être vide"):
            CodeChantier("")

    def test_invalid_format_raises(self):
        """Test erreur si format invalide."""
        with pytest.raises(ValueError, match="Format de code chantier invalide"):
            CodeChantier("ABC")

    def test_invalid_format_short_raises(self):
        """Test erreur si format trop court."""
        with pytest.raises(ValueError, match="Format de code chantier invalide"):
            CodeChantier("A01")

    def test_invalid_format_only_numbers_raises(self):
        """Test erreur si seulement des chiffres."""
        with pytest.raises(ValueError, match="Format de code chantier invalide"):
            CodeChantier("0123")

    def test_frozen_immutability(self):
        """Test que CodeChantier est immutable."""
        code = CodeChantier("A001")

        with pytest.raises(FrozenInstanceError):
            code.value = "B001"

    def test_str(self):
        """Test __str__ retourne la valeur."""
        code = CodeChantier("A001")

        assert str(code) == "A001"

    def test_is_special_false(self):
        """Test is_special pour code normal."""
        code = CodeChantier("A001")

        assert code.is_special is False

    def test_letter_normal_code(self):
        """Test letter pour code normal."""
        code = CodeChantier("B023")

        assert code.letter == "B"

    def test_letter_special_code(self):
        """Test letter pour code spécial."""
        code = CodeChantier("CONGES")

        assert code.letter == "C"  # Première lettre du code

    def test_number_normal_code(self):
        """Test number pour code normal."""
        code = CodeChantier("A023")

        assert code.number == 23

    def test_number_special_code(self):
        """Test number pour code spécial retourne 0."""
        code = CodeChantier("CONGES")

        assert code.number == 0

    def test_generate_next_from_none(self):
        """Test génération depuis None retourne A001."""
        code = CodeChantier.generate_next(None)

        assert code.value == "A001"

    def test_generate_next_increment(self):
        """Test génération incrémente le numéro."""
        code = CodeChantier.generate_next("A001")

        assert code.value == "A002"

    def test_generate_next_increment_large(self):
        """Test génération incrémente numéro élevé."""
        code = CodeChantier.generate_next("A100")

        assert code.value == "A101"

    def test_generate_next_letter_change(self):
        """Test génération change de lettre à 999."""
        code = CodeChantier.generate_next("A999")

        assert code.value == "B001"

    def test_generate_next_z999_raises(self):
        """Test génération depuis Z999 lève erreur."""
        with pytest.raises(ValueError, match="Capacité maximale atteinte"):
            CodeChantier.generate_next("Z999")

    def test_from_string(self):
        """Test création depuis string."""
        code = CodeChantier.from_string("A001")

        assert code.value == "A001"

    def test_comparison_lt(self):
        """Test comparaison moins que."""
        code1 = CodeChantier("A001")
        code2 = CodeChantier("A002")

        assert code1 < code2

    def test_comparison_lt_different_letters(self):
        """Test comparaison avec lettres différentes."""
        code1 = CodeChantier("A999")
        code2 = CodeChantier("B001")

        assert code1 < code2

    def test_comparison_with_non_code(self):
        """Test comparaison avec non-CodeChantier lève TypeError."""
        code = CodeChantier("A001")

        with pytest.raises(TypeError):
            _ = code < "A002"
