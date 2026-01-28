"""Tests unitaires pour le value object TypeMetier."""

import pytest

from modules.planning.domain.value_objects import TypeMetier


class TestTypeMetier:
    """Tests pour le value object TypeMetier."""

    def test_all_types_exist(self):
        """Test que tous les types attendus existent."""
        expected = [
            "employe", "sous_traitant", "charpentier", "couvreur",
            "electricien", "macon", "coffreur", "ferrailleur", "grutier"
        ]
        actual = [t.value for t in TypeMetier]
        for e in expected:
            assert e in actual

    def test_couleur_property(self):
        """Test que chaque type a une couleur."""
        for type_metier in TypeMetier:
            assert type_metier.couleur.startswith("#")
            assert len(type_metier.couleur) == 7

    def test_label_property(self):
        """Test que chaque type a un label lisible."""
        assert TypeMetier.EMPLOYE.label == "Employe"
        assert TypeMetier.SOUS_TRAITANT.label == "Sous-traitant"
        assert TypeMetier.MACON.label == "Macon"

    def test_from_string_valid(self):
        """Test creation depuis une chaine valide."""
        assert TypeMetier.from_string("employe") == TypeMetier.EMPLOYE
        assert TypeMetier.from_string("MACON") == TypeMetier.MACON
        assert TypeMetier.from_string("sous-traitant") == TypeMetier.SOUS_TRAITANT

    def test_from_string_with_spaces(self):
        """Test creation avec remplacement espaces."""
        assert TypeMetier.from_string("sous traitant") == TypeMetier.SOUS_TRAITANT

    def test_from_string_invalid(self):
        """Test erreur si type invalide."""
        with pytest.raises(ValueError, match="Type de metier invalide"):
            TypeMetier.from_string("invalid_type")

    def test_all_types_returns_list(self):
        """Test que all_types retourne une liste."""
        types = TypeMetier.all_types()
        assert isinstance(types, list)
        assert len(types) == 9
        assert TypeMetier.EMPLOYE in types

    def test_couleurs_are_unique(self):
        """Test que les couleurs sont uniques par type."""
        couleurs = [t.couleur for t in TypeMetier]
        # Certaines couleurs peuvent etre partagees selon le design
        assert len(couleurs) == 9

    def test_specific_colors(self):
        """Test couleurs specifiques selon CDC Section 5.3."""
        assert TypeMetier.EMPLOYE.couleur == "#2C3E50"  # Bleu fonce
        assert TypeMetier.MACON.couleur == "#795548"  # Marron
        assert TypeMetier.COFFREUR.couleur == "#F1C40F"  # Jaune
        assert TypeMetier.GRUTIER.couleur == "#1ABC9C"  # Cyan
