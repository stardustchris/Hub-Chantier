"""Tests des Value Objects du module Formulaires."""

import pytest

from modules.formulaires.domain.value_objects import (
    TypeChamp,
    StatutFormulaire,
    CategorieFormulaire,
)


class TestTypeChamp:
    """Tests pour TypeChamp."""

    def test_types_disponibles(self):
        """Verifie que les types de base sont disponibles."""
        assert TypeChamp.TEXTE.value == "texte"
        assert TypeChamp.NOMBRE.value == "nombre"
        assert TypeChamp.PHOTO.value == "photo"
        assert TypeChamp.SIGNATURE.value == "signature"

    def test_est_auto_rempli(self):
        """Verifie les champs auto-remplis."""
        assert TypeChamp.AUTO_DATE.est_auto_rempli is True
        assert TypeChamp.AUTO_HEURE.est_auto_rempli is True
        assert TypeChamp.AUTO_LOCALISATION.est_auto_rempli is True
        assert TypeChamp.AUTO_INTERVENANT.est_auto_rempli is True
        assert TypeChamp.TEXTE.est_auto_rempli is False

    def test_est_media(self):
        """Verifie les champs media."""
        assert TypeChamp.PHOTO.est_media is True
        assert TypeChamp.PHOTO_MULTIPLE.est_media is True
        assert TypeChamp.TEXTE.est_media is False

    def test_est_signature(self):
        """Verifie le champ signature."""
        assert TypeChamp.SIGNATURE.est_signature is True
        assert TypeChamp.TEXTE.est_signature is False

    def test_est_decoratif(self):
        """Verifie les champs decoratifs."""
        assert TypeChamp.TITRE_SECTION.est_decoratif is True
        assert TypeChamp.SEPARATEUR.est_decoratif is True
        assert TypeChamp.TEXTE.est_decoratif is False

    def test_from_string(self):
        """Verifie la conversion depuis string."""
        assert TypeChamp.from_string("texte") == TypeChamp.TEXTE
        assert TypeChamp.from_string("PHOTO") == TypeChamp.PHOTO

    def test_from_string_invalid(self):
        """Verifie l'erreur pour type invalide."""
        with pytest.raises(ValueError):
            TypeChamp.from_string("invalid_type")

    def test_list_all(self):
        """Verifie la liste de tous les types."""
        types = TypeChamp.list_all()
        assert "texte" in types
        assert "photo" in types
        assert "signature" in types


class TestStatutFormulaire:
    """Tests pour StatutFormulaire."""

    def test_statuts_disponibles(self):
        """Verifie les statuts disponibles."""
        assert StatutFormulaire.BROUILLON.value == "brouillon"
        assert StatutFormulaire.SOUMIS.value == "soumis"
        assert StatutFormulaire.VALIDE.value == "valide"
        assert StatutFormulaire.ARCHIVE.value == "archive"

    def test_est_modifiable(self):
        """Verifie le statut modifiable."""
        assert StatutFormulaire.BROUILLON.est_modifiable is True
        assert StatutFormulaire.SOUMIS.est_modifiable is False
        assert StatutFormulaire.VALIDE.est_modifiable is False
        assert StatutFormulaire.ARCHIVE.est_modifiable is False

    def test_est_soumis(self):
        """Verifie le statut soumis."""
        assert StatutFormulaire.BROUILLON.est_soumis is False
        assert StatutFormulaire.SOUMIS.est_soumis is True
        assert StatutFormulaire.VALIDE.est_soumis is True
        assert StatutFormulaire.ARCHIVE.est_soumis is True

    def test_from_string(self):
        """Verifie la conversion depuis string."""
        assert StatutFormulaire.from_string("brouillon") == StatutFormulaire.BROUILLON
        assert StatutFormulaire.from_string("SOUMIS") == StatutFormulaire.SOUMIS

    def test_from_string_invalid(self):
        """Verifie l'erreur pour statut invalide."""
        with pytest.raises(ValueError):
            StatutFormulaire.from_string("invalid_status")


class TestCategorieFormulaire:
    """Tests pour CategorieFormulaire."""

    def test_categories_disponibles(self):
        """Verifie les categories disponibles."""
        assert CategorieFormulaire.INTERVENTION.value == "intervention"
        assert CategorieFormulaire.RECEPTION.value == "reception"
        assert CategorieFormulaire.SECURITE.value == "securite"
        assert CategorieFormulaire.GROS_OEUVRE.value == "gros_oeuvre"

    def test_label(self):
        """Verifie les labels."""
        assert CategorieFormulaire.INTERVENTION.label == "Interventions"
        assert CategorieFormulaire.SECURITE.label == "Securite"
        assert CategorieFormulaire.GROS_OEUVRE.label == "Gros Oeuvre"

    def test_from_string(self):
        """Verifie la conversion depuis string."""
        assert CategorieFormulaire.from_string("intervention") == CategorieFormulaire.INTERVENTION
        assert CategorieFormulaire.from_string("SECURITE") == CategorieFormulaire.SECURITE

    def test_from_string_invalid(self):
        """Verifie l'erreur pour categorie invalide."""
        with pytest.raises(ValueError):
            CategorieFormulaire.from_string("invalid_category")

    def test_list_all(self):
        """Verifie la liste de toutes les categories."""
        categories = CategorieFormulaire.list_all()
        assert len(categories) == 8
        assert any(c["value"] == "intervention" for c in categories)
        assert any(c["label"] == "Securite" for c in categories)
