"""Tests unitaires pour CategorieRessource value object."""

from modules.logistique.domain.value_objects import CategorieRessource


class TestCategorieRessource:
    """Tests pour CategorieRessource."""

    def test_all_values(self):
        """Toutes les catégories existent."""
        assert CategorieRessource.ENGIN_LEVAGE == "engin_levage"
        assert CategorieRessource.ENGIN_TERRASSEMENT == "engin_terrassement"
        assert CategorieRessource.VEHICULE == "vehicule"
        assert CategorieRessource.GROS_OUTILLAGE == "gros_outillage"
        assert CategorieRessource.EQUIPEMENT == "equipement"

    def test_label(self):
        """Chaque catégorie a un label lisible."""
        assert CategorieRessource.ENGIN_LEVAGE.label == "Engin de levage"
        assert CategorieRessource.VEHICULE.label == "Véhicule"
        assert CategorieRessource.GROS_OUTILLAGE.label == "Gros outillage"
        assert CategorieRessource.EQUIPEMENT.label == "Équipement"

    def test_exemples(self):
        """Chaque catégorie a des exemples."""
        assert "Grue mobile" in CategorieRessource.ENGIN_LEVAGE.exemples
        assert "Camion benne" in CategorieRessource.VEHICULE.exemples
        assert "Bétonnière" in CategorieRessource.GROS_OUTILLAGE.exemples

    def test_validation_requise(self):
        """Certaines catégories requièrent validation N+1."""
        assert CategorieRessource.ENGIN_LEVAGE.validation_requise is True
        assert CategorieRessource.ENGIN_TERRASSEMENT.validation_requise is True
        assert CategorieRessource.EQUIPEMENT.validation_requise is True
        assert CategorieRessource.VEHICULE.validation_requise is False
        assert CategorieRessource.GROS_OUTILLAGE.validation_requise is False

    def test_all_categories(self):
        """all_categories() retourne toutes les catégories."""
        cats = CategorieRessource.all_categories()
        assert len(cats) == 5
        assert CategorieRessource.ENGIN_LEVAGE in cats
