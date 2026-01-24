"""Tests des Entites du module Formulaires."""

import pytest

from modules.formulaires.domain.entities import (
    TemplateFormulaire,
    ChampTemplate,
    FormulaireRempli,
    PhotoFormulaire,
)
from modules.formulaires.domain.value_objects import (
    TypeChamp,
    StatutFormulaire,
    CategorieFormulaire,
)


class TestChampTemplate:
    """Tests pour ChampTemplate."""

    def test_create_champ_minimal(self):
        """Creation d'un champ avec donnees minimales."""
        champ = ChampTemplate(
            nom="titre",
            label="Titre",
            type_champ=TypeChamp.TEXTE,
        )
        assert champ.nom == "titre"
        assert champ.label == "Titre"
        assert champ.type_champ == TypeChamp.TEXTE
        assert champ.obligatoire is False
        assert champ.ordre == 0

    def test_create_champ_complet(self):
        """Creation d'un champ avec toutes les donnees."""
        champ = ChampTemplate(
            nom="quantite",
            label="Quantite",
            type_champ=TypeChamp.NOMBRE,
            obligatoire=True,
            ordre=1,
            placeholder="Entrez la quantite",
            min_value=0,
            max_value=1000,
        )
        assert champ.obligatoire is True
        assert champ.ordre == 1
        assert champ.min_value == 0
        assert champ.max_value == 1000

    def test_nom_normalise(self):
        """Verifie la normalisation du nom."""
        champ = ChampTemplate(
            nom="Mon Champ",
            label="Mon Champ",
            type_champ=TypeChamp.TEXTE,
        )
        assert champ.nom == "mon_champ"

    def test_nom_vide_raise_error(self):
        """Verifie l'erreur pour nom vide."""
        with pytest.raises(ValueError, match="nom du champ"):
            ChampTemplate(nom="", label="Test", type_champ=TypeChamp.TEXTE)

    def test_label_vide_raise_error(self):
        """Verifie l'erreur pour label vide."""
        with pytest.raises(ValueError, match="label du champ"):
            ChampTemplate(nom="test", label="", type_champ=TypeChamp.TEXTE)

    def test_champ_select_sans_options_raise_error(self):
        """Verifie l'erreur pour champ select sans options."""
        with pytest.raises(ValueError, match="necessite des options"):
            ChampTemplate(
                nom="choix",
                label="Choix",
                type_champ=TypeChamp.SELECT,
            )

    def test_champ_select_avec_options(self):
        """Creation d'un champ select avec options."""
        champ = ChampTemplate(
            nom="choix",
            label="Choix",
            type_champ=TypeChamp.SELECT,
            options=["option1", "option2", "option3"],
        )
        assert len(champ.options) == 3


class TestTemplateFormulaire:
    """Tests pour TemplateFormulaire."""

    def test_create_template_minimal(self):
        """Creation d'un template avec donnees minimales."""
        template = TemplateFormulaire(
            nom="Rapport d'intervention",
            categorie=CategorieFormulaire.INTERVENTION,
        )
        assert template.nom == "Rapport d'intervention"
        assert template.categorie == CategorieFormulaire.INTERVENTION
        assert template.is_active is True
        assert template.version == 1
        assert template.nombre_champs == 0

    def test_nom_vide_raise_error(self):
        """Verifie l'erreur pour nom vide."""
        with pytest.raises(ValueError, match="nom du template"):
            TemplateFormulaire(nom="", categorie=CategorieFormulaire.SECURITE)

    def test_ajouter_champ(self):
        """Test d'ajout de champ."""
        template = TemplateFormulaire(
            nom="Test",
            categorie=CategorieFormulaire.AUTRE,
        )
        champ = ChampTemplate(
            nom="titre",
            label="Titre",
            type_champ=TypeChamp.TEXTE,
        )
        template.ajouter_champ(champ)
        assert template.nombre_champs == 1
        assert template.champs[0].ordre == 1

    def test_ajouter_champ_doublon_raise_error(self):
        """Verifie l'erreur pour champ doublon."""
        template = TemplateFormulaire(
            nom="Test",
            categorie=CategorieFormulaire.AUTRE,
        )
        champ1 = ChampTemplate(nom="titre", label="Titre", type_champ=TypeChamp.TEXTE)
        champ2 = ChampTemplate(nom="titre", label="Autre Titre", type_champ=TypeChamp.TEXTE)
        template.ajouter_champ(champ1)
        with pytest.raises(ValueError, match="existe deja"):
            template.ajouter_champ(champ2)

    def test_retirer_champ(self):
        """Test de retrait de champ."""
        template = TemplateFormulaire(
            nom="Test",
            categorie=CategorieFormulaire.AUTRE,
        )
        champ = ChampTemplate(nom="titre", label="Titre", type_champ=TypeChamp.TEXTE)
        template.ajouter_champ(champ)
        assert template.nombre_champs == 1
        result = template.retirer_champ("titre")
        assert result is True
        assert template.nombre_champs == 0

    def test_get_champ(self):
        """Test de recuperation de champ."""
        template = TemplateFormulaire(
            nom="Test",
            categorie=CategorieFormulaire.AUTRE,
        )
        champ = ChampTemplate(nom="titre", label="Titre", type_champ=TypeChamp.TEXTE)
        template.ajouter_champ(champ)
        found = template.get_champ("titre")
        assert found is not None
        assert found.label == "Titre"

    def test_a_signature(self):
        """Test de detection de signature."""
        template = TemplateFormulaire(
            nom="Test",
            categorie=CategorieFormulaire.AUTRE,
        )
        assert template.a_signature is False

        champ = ChampTemplate(nom="sig", label="Signature", type_champ=TypeChamp.SIGNATURE)
        template.ajouter_champ(champ)
        assert template.a_signature is True

    def test_a_photo(self):
        """Test de detection de photo."""
        template = TemplateFormulaire(
            nom="Test",
            categorie=CategorieFormulaire.AUTRE,
        )
        assert template.a_photo is False

        champ = ChampTemplate(nom="photo", label="Photo", type_champ=TypeChamp.PHOTO)
        template.ajouter_champ(champ)
        assert template.a_photo is True

    def test_desactiver_activer(self):
        """Test de desactivation/activation."""
        template = TemplateFormulaire(
            nom="Test",
            categorie=CategorieFormulaire.AUTRE,
        )
        assert template.is_active is True
        template.desactiver()
        assert template.is_active is False
        template.activer()
        assert template.is_active is True

    def test_incrementer_version(self):
        """Test d'incrementation de version."""
        template = TemplateFormulaire(
            nom="Test",
            categorie=CategorieFormulaire.AUTRE,
        )
        assert template.version == 1
        template.incrementer_version()
        assert template.version == 2


class TestFormulaireRempli:
    """Tests pour FormulaireRempli."""

    def test_create_formulaire_minimal(self):
        """Creation d'un formulaire avec donnees minimales."""
        formulaire = FormulaireRempli(
            template_id=1,
            chantier_id=1,
            user_id=1,
        )
        assert formulaire.template_id == 1
        assert formulaire.chantier_id == 1
        assert formulaire.user_id == 1
        assert formulaire.statut == StatutFormulaire.BROUILLON
        assert formulaire.est_brouillon is True
        assert formulaire.est_signe is False

    def test_set_champ(self):
        """Test de definition d'un champ."""
        formulaire = FormulaireRempli(template_id=1, chantier_id=1, user_id=1)
        formulaire.set_champ("titre", "Mon titre", TypeChamp.TEXTE)
        assert len(formulaire.champs) == 1
        assert formulaire.get_valeur("titre") == "Mon titre"

    def test_set_champ_update(self):
        """Test de mise a jour d'un champ."""
        formulaire = FormulaireRempli(template_id=1, chantier_id=1, user_id=1)
        formulaire.set_champ("titre", "Premier titre", TypeChamp.TEXTE)
        formulaire.set_champ("titre", "Nouveau titre", TypeChamp.TEXTE)
        assert len(formulaire.champs) == 1
        assert formulaire.get_valeur("titre") == "Nouveau titre"

    def test_set_champ_non_modifiable_raise_error(self):
        """Verifie l'erreur pour formulaire non modifiable."""
        formulaire = FormulaireRempli(template_id=1, chantier_id=1, user_id=1)
        formulaire.soumettre()
        with pytest.raises(ValueError, match="modifiable"):
            formulaire.set_champ("titre", "Test", TypeChamp.TEXTE)

    def test_ajouter_photo(self):
        """Test d'ajout de photo."""
        formulaire = FormulaireRempli(template_id=1, chantier_id=1, user_id=1)
        photo = PhotoFormulaire(
            url="https://example.com/photo.jpg",
            nom_fichier="photo.jpg",
            champ_nom="photo_avant",
        )
        formulaire.ajouter_photo(photo)
        assert formulaire.nombre_photos == 1

    def test_signer(self):
        """Test de signature."""
        formulaire = FormulaireRempli(template_id=1, chantier_id=1, user_id=1)
        formulaire.signer("https://example.com/sig.png", "Jean Dupont")
        assert formulaire.est_signe is True
        assert formulaire.signature_nom == "Jean Dupont"

    def test_set_localisation(self):
        """Test de localisation."""
        formulaire = FormulaireRempli(template_id=1, chantier_id=1, user_id=1)
        formulaire.set_localisation(48.8566, 2.3522)
        assert formulaire.est_geolocalise is True
        assert formulaire.localisation_latitude == 48.8566

    def test_soumettre(self):
        """Test de soumission."""
        formulaire = FormulaireRempli(template_id=1, chantier_id=1, user_id=1)
        formulaire.soumettre()
        assert formulaire.statut == StatutFormulaire.SOUMIS
        assert formulaire.soumis_at is not None

    def test_soumettre_deja_soumis_raise_error(self):
        """Verifie l'erreur si deja soumis."""
        formulaire = FormulaireRempli(template_id=1, chantier_id=1, user_id=1)
        formulaire.soumettre()
        with pytest.raises(ValueError, match="brouillon"):
            formulaire.soumettre()

    def test_valider(self):
        """Test de validation."""
        formulaire = FormulaireRempli(template_id=1, chantier_id=1, user_id=1)
        formulaire.soumettre()
        formulaire.valider(valideur_id=2)
        assert formulaire.statut == StatutFormulaire.VALIDE
        assert formulaire.valide_by == 2
        assert formulaire.valide_at is not None

    def test_valider_non_soumis_raise_error(self):
        """Verifie l'erreur si non soumis."""
        formulaire = FormulaireRempli(template_id=1, chantier_id=1, user_id=1)
        with pytest.raises(ValueError, match="soumis"):
            formulaire.valider(valideur_id=2)

    def test_archiver(self):
        """Test d'archivage."""
        formulaire = FormulaireRempli(template_id=1, chantier_id=1, user_id=1)
        formulaire.soumettre()
        formulaire.valider(valideur_id=2)
        formulaire.archiver()
        assert formulaire.statut == StatutFormulaire.ARCHIVE


class TestPhotoFormulaire:
    """Tests pour PhotoFormulaire."""

    def test_create_photo(self):
        """Creation d'une photo."""
        photo = PhotoFormulaire(
            url="https://example.com/photo.jpg",
            nom_fichier="photo.jpg",
            champ_nom="photo_avant",
        )
        assert photo.url == "https://example.com/photo.jpg"
        assert photo.est_geolocalisee is False

    def test_photo_geolocalisee(self):
        """Photo avec geolocalisation."""
        photo = PhotoFormulaire(
            url="https://example.com/photo.jpg",
            nom_fichier="photo.jpg",
            champ_nom="photo_avant",
            latitude=48.8566,
            longitude=2.3522,
        )
        assert photo.est_geolocalisee is True
