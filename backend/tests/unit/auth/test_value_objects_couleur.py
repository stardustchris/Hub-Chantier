"""Tests unitaires pour le Value Object Couleur."""

import pytest

from modules.auth.domain.value_objects.couleur import Couleur


class TestCouleurCreation:
    """Tests de création de Couleur."""

    def test_create_with_valid_hex_color(self):
        """Test création avec couleur hex valide de la palette."""
        couleur = Couleur("#E74C3C")  # Rouge
        assert couleur.value == "#E74C3C"

    def test_create_with_lowercase_hex(self):
        """Test création avec hex minuscule."""
        couleur = Couleur("#e74c3c")
        assert couleur.value == "#E74C3C"  # Normalisé en majuscules

    def test_create_without_hash(self):
        """Test création sans le # initial."""
        couleur = Couleur("E74C3C")
        assert couleur.value == "#E74C3C"

    def test_create_with_empty_uses_default(self):
        """Test création avec valeur vide utilise défaut."""
        couleur = Couleur("")
        assert couleur.value == Couleur.DEFAULT

    def test_create_with_none_uses_default(self):
        """Test création avec None utilise défaut."""
        couleur = Couleur(None)
        assert couleur.value == Couleur.DEFAULT

    def test_invalid_format_raises_error(self):
        """Test format invalide lève une erreur."""
        with pytest.raises(ValueError) as exc:
            Couleur("#FFF")  # Trop court
        assert "Format couleur invalide" in str(exc.value)

    def test_invalid_hex_raises_error(self):
        """Test hex invalide lève une erreur."""
        with pytest.raises(ValueError) as exc:
            Couleur("#GGGGGG")  # Caractères non hex
        assert "Code hexadécimal invalide" in str(exc.value)

    def test_color_not_in_palette_raises_error(self):
        """Test couleur hors palette lève une erreur."""
        with pytest.raises(ValueError) as exc:
            Couleur("#000000")  # Noir - pas dans la palette
        assert "Couleur non autorisée" in str(exc.value)


class TestCouleurStr:
    """Tests de __str__."""

    def test_str_returns_hex_value(self):
        """Test str retourne la valeur hex."""
        couleur = Couleur("#3498DB")
        assert str(couleur) == "#3498DB"


class TestCouleurFromName:
    """Tests de from_name."""

    def test_from_name_valid(self):
        """Test création depuis nom valide."""
        couleur = Couleur.from_name("rouge")
        assert couleur.value == "#E74C3C"

    def test_from_name_case_insensitive(self):
        """Test insensible à la casse."""
        couleur = Couleur.from_name("ROUGE")
        assert couleur.value == "#E74C3C"

    def test_from_name_bleu_clair(self):
        """Test nom composé."""
        couleur = Couleur.from_name("bleu_clair")
        assert couleur.value == "#3498DB"

    def test_from_name_invalid_raises_error(self):
        """Test nom invalide lève une erreur."""
        with pytest.raises(ValueError) as exc:
            Couleur.from_name("noir")
        assert "Nom de couleur invalide" in str(exc.value)


class TestCouleurDefault:
    """Tests de default."""

    def test_default_returns_bleu_clair(self):
        """Test défaut retourne bleu clair."""
        couleur = Couleur.default()
        assert couleur.value == "#3498DB"


class TestCouleurAllColors:
    """Tests de all_colors."""

    def test_all_colors_returns_16_colors(self):
        """Test retourne les 16 couleurs de la palette."""
        colors = Couleur.all_colors()
        assert len(colors) == 16

    def test_all_colors_contains_rouge(self):
        """Test contient rouge."""
        colors = Couleur.all_colors()
        assert "#E74C3C" in colors

    def test_all_colors_contains_bleu_clair(self):
        """Test contient bleu clair."""
        colors = Couleur.all_colors()
        assert "#3498DB" in colors


class TestCouleurGetName:
    """Tests de get_name."""

    def test_get_name_rouge(self):
        """Test obtenir nom de rouge."""
        couleur = Couleur("#E74C3C")
        assert couleur.get_name() == "rouge"

    def test_get_name_bleu_clair(self):
        """Test obtenir nom de bleu clair."""
        couleur = Couleur("#3498DB")
        assert couleur.get_name() == "bleu_clair"

    def test_get_name_all_palette_colors(self):
        """Test tous les noms de la palette."""
        for name, code in Couleur.PALETTE.items():
            couleur = Couleur(code)
            assert couleur.get_name() == name


class TestCouleurImmutability:
    """Tests d'immutabilité."""

    def test_couleur_is_frozen(self):
        """Test que Couleur est immuable."""
        couleur = Couleur("#E74C3C")
        with pytest.raises(AttributeError):
            couleur.value = "#3498DB"


class TestCouleurPalette:
    """Tests de la palette."""

    def test_palette_has_16_colors(self):
        """Test palette a 16 couleurs."""
        assert len(Couleur.PALETTE) == 16

    def test_all_palette_colors_are_valid_hex(self):
        """Test toutes les couleurs de la palette sont valides."""
        for name, code in Couleur.PALETTE.items():
            couleur = Couleur(code)
            assert couleur.value == code.upper()

    def test_expected_colors_in_palette(self):
        """Test couleurs attendues dans la palette."""
        expected = [
            "rouge", "orange", "jaune", "vert_clair", "vert_fonce",
            "marron", "corail", "magenta", "bleu_fonce", "bleu_clair",
            "cyan", "violet", "rose", "gris", "indigo", "lime"
        ]
        for name in expected:
            assert name in Couleur.PALETTE
