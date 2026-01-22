"""Tests pour les entites du module Taches."""

import pytest
from datetime import date, timedelta

from backend.modules.taches.domain.entities import Tache, TemplateModele, FeuilleTache
from backend.modules.taches.domain.value_objects import StatutTache, UniteMesure, CouleurProgression


class TestTache:
    """Tests pour l'entite Tache."""

    def test_create_tache_minimal(self):
        """Test creation d'une tache avec les champs minimaux."""
        tache = Tache(chantier_id=1, titre="Ma tache")

        assert tache.chantier_id == 1
        assert tache.titre == "Ma tache"
        assert tache.statut == StatutTache.A_FAIRE
        assert tache.heures_realisees == 0.0
        assert not tache.est_terminee

    def test_create_tache_complete(self):
        """Test creation d'une tache avec tous les champs."""
        tache = Tache(
            chantier_id=1,
            titre="Coffrage voiles",
            description="Mise en place des banches",
            heures_estimees=16.0,
            unite_mesure=UniteMesure.M2,
            quantite_estimee=50.0,
            date_echeance=date.today() + timedelta(days=7),
        )

        assert tache.titre == "Coffrage voiles"
        assert tache.heures_estimees == 16.0
        assert tache.unite_mesure == UniteMesure.M2
        assert tache.quantite_estimee == 50.0

    def test_titre_strip(self):
        """Test que le titre est nettoye des espaces."""
        tache = Tache(chantier_id=1, titre="  Ma tache  ")
        assert tache.titre == "Ma tache"

    def test_titre_vide_raise_error(self):
        """Test qu'un titre vide leve une erreur."""
        with pytest.raises(ValueError, match="titre"):
            Tache(chantier_id=1, titre="")

    def test_heures_negatives_raise_error(self):
        """Test que des heures negatives levent une erreur."""
        with pytest.raises(ValueError):
            Tache(chantier_id=1, titre="Test", heures_estimees=-5)

    def test_terminer_tache(self):
        """Test marquer une tache comme terminee (TAC-13)."""
        tache = Tache(chantier_id=1, titre="Test")
        assert not tache.est_terminee

        tache.terminer()

        assert tache.est_terminee
        assert tache.statut == StatutTache.TERMINE

    def test_rouvrir_tache(self):
        """Test rouvrir une tache terminee."""
        tache = Tache(chantier_id=1, titre="Test")
        tache.terminer()
        assert tache.est_terminee

        tache.rouvrir()

        assert not tache.est_terminee
        assert tache.statut == StatutTache.A_FAIRE

    def test_ajouter_heures(self):
        """Test ajouter des heures realisees (TAC-12)."""
        tache = Tache(chantier_id=1, titre="Test", heures_estimees=10.0)
        assert tache.heures_realisees == 0.0

        tache.ajouter_heures(5.0)
        assert tache.heures_realisees == 5.0

        tache.ajouter_heures(3.0)
        assert tache.heures_realisees == 8.0

    def test_ajouter_heures_negatives_raise_error(self):
        """Test que des heures negatives levent une erreur."""
        tache = Tache(chantier_id=1, titre="Test")
        with pytest.raises(ValueError):
            tache.ajouter_heures(-5)

    def test_progression_heures(self):
        """Test calcul de la progression en heures."""
        tache = Tache(chantier_id=1, titre="Test", heures_estimees=10.0)

        assert tache.progression_heures == 0.0

        tache.ajouter_heures(5.0)
        assert tache.progression_heures == 50.0

        tache.ajouter_heures(5.0)
        assert tache.progression_heures == 100.0

    def test_couleur_progression_gris(self):
        """Test couleur gris si pas de travail (TAC-20)."""
        tache = Tache(chantier_id=1, titre="Test", heures_estimees=10.0)
        assert tache.couleur_progression == CouleurProgression.GRIS

    def test_couleur_progression_vert(self):
        """Test couleur verte si <= 80% (TAC-20)."""
        tache = Tache(chantier_id=1, titre="Test", heures_estimees=10.0)
        tache.ajouter_heures(7.0)  # 70%
        assert tache.couleur_progression == CouleurProgression.VERT

    def test_couleur_progression_jaune(self):
        """Test couleur jaune entre 80% et 100% (TAC-20)."""
        tache = Tache(chantier_id=1, titre="Test", heures_estimees=10.0)
        tache.ajouter_heures(9.0)  # 90%
        assert tache.couleur_progression == CouleurProgression.JAUNE

    def test_couleur_progression_rouge(self):
        """Test couleur rouge si > 100% (TAC-20)."""
        tache = Tache(chantier_id=1, titre="Test", heures_estimees=10.0)
        tache.ajouter_heures(12.0)  # 120%
        assert tache.couleur_progression == CouleurProgression.ROUGE

    def test_est_en_retard(self):
        """Test detection des taches en retard."""
        # Tache sans echeance
        tache1 = Tache(chantier_id=1, titre="Test1")
        assert not tache1.est_en_retard

        # Tache avec echeance future
        tache2 = Tache(
            chantier_id=1,
            titre="Test2",
            date_echeance=date.today() + timedelta(days=7),
        )
        assert not tache2.est_en_retard

        # Tache avec echeance passee
        tache3 = Tache(
            chantier_id=1,
            titre="Test3",
            date_echeance=date.today() - timedelta(days=1),
        )
        assert tache3.est_en_retard

        # Tache terminee avec echeance passee (pas en retard)
        tache4 = Tache(
            chantier_id=1,
            titre="Test4",
            date_echeance=date.today() - timedelta(days=1),
        )
        tache4.terminer()
        assert not tache4.est_en_retard


class TestTemplateModele:
    """Tests pour l'entite TemplateModele."""

    def test_create_template(self):
        """Test creation d'un template (TAC-04)."""
        template = TemplateModele(
            nom="Coffrage voiles",
            description="Mise en place des banches",
            categorie="Gros Oeuvre",
        )

        assert template.nom == "Coffrage voiles"
        assert template.categorie == "Gros Oeuvre"
        assert template.is_active
        assert template.nombre_sous_taches == 0

    def test_ajouter_sous_tache(self):
        """Test ajout de sous-taches au template."""
        template = TemplateModele(nom="Test")

        template.ajouter_sous_tache("Etape 1")
        template.ajouter_sous_tache("Etape 2")

        assert template.nombre_sous_taches == 2
        assert template.sous_taches[0].titre == "Etape 1"
        assert template.sous_taches[1].titre == "Etape 2"

    def test_desactiver_template(self):
        """Test desactivation d'un template."""
        template = TemplateModele(nom="Test")
        assert template.is_active

        template.desactiver()

        assert not template.is_active


class TestFeuilleTache:
    """Tests pour l'entite FeuilleTache."""

    def test_create_feuille(self):
        """Test creation d'une feuille de tache (TAC-18)."""
        feuille = FeuilleTache(
            tache_id=1,
            utilisateur_id=1,
            chantier_id=1,
            date_travail=date.today(),
            heures_travaillees=8.0,
        )

        assert feuille.tache_id == 1
        assert feuille.heures_travaillees == 8.0
        assert feuille.est_en_attente
        assert not feuille.est_validee

    def test_valider_feuille(self):
        """Test validation d'une feuille (TAC-19)."""
        feuille = FeuilleTache(
            tache_id=1,
            utilisateur_id=1,
            chantier_id=1,
            date_travail=date.today(),
            heures_travaillees=8.0,
        )

        feuille.valider(validateur_id=2)

        assert feuille.est_validee
        assert feuille.validateur_id == 2
        assert feuille.date_validation is not None

    def test_rejeter_feuille(self):
        """Test rejet d'une feuille."""
        feuille = FeuilleTache(
            tache_id=1,
            utilisateur_id=1,
            chantier_id=1,
            date_travail=date.today(),
            heures_travaillees=8.0,
        )

        feuille.rejeter(validateur_id=2, motif="Heures incorrectes")

        assert feuille.est_rejetee
        assert feuille.motif_rejet == "Heures incorrectes"

    def test_rejeter_sans_motif_raise_error(self):
        """Test que rejeter sans motif leve une erreur."""
        feuille = FeuilleTache(
            tache_id=1,
            utilisateur_id=1,
            chantier_id=1,
            date_travail=date.today(),
        )

        with pytest.raises(ValueError, match="motif"):
            feuille.rejeter(validateur_id=2, motif="")

    def test_modifier_feuille_validee_raise_error(self):
        """Test qu'on ne peut pas modifier une feuille validee."""
        feuille = FeuilleTache(
            tache_id=1,
            utilisateur_id=1,
            chantier_id=1,
            date_travail=date.today(),
            heures_travaillees=8.0,
        )
        feuille.valider(validateur_id=2)

        with pytest.raises(ValueError, match="validee"):
            feuille.modifier(heures_travaillees=10.0)
