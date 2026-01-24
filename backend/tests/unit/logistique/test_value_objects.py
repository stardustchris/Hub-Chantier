"""Tests unitaires pour les Value Objects du module Logistique."""

import pytest
from datetime import time

from modules.logistique.domain.value_objects import (
    CategorieRessource,
    StatutReservation,
    PlageHoraire,
)


class TestCategorieRessource:
    """Tests pour CategorieRessource."""

    def test_all_categories_exist(self):
        """Test: toutes les catégories sont définies."""
        assert CategorieRessource.ENGIN_LEVAGE
        assert CategorieRessource.ENGIN_TERRASSEMENT
        assert CategorieRessource.VEHICULE
        assert CategorieRessource.GROS_OUTILLAGE
        assert CategorieRessource.EQUIPEMENT

    def test_category_values(self):
        """Test: les valeurs des catégories sont correctes."""
        assert CategorieRessource.ENGIN_LEVAGE.value == "engin_levage"
        assert CategorieRessource.ENGIN_TERRASSEMENT.value == "engin_terrassement"
        assert CategorieRessource.VEHICULE.value == "vehicule"
        assert CategorieRessource.GROS_OUTILLAGE.value == "gros_outillage"
        assert CategorieRessource.EQUIPEMENT.value == "equipement"

    def test_category_labels(self):
        """Test: chaque catégorie a un label."""
        for cat in CategorieRessource:
            assert cat.label is not None
            assert len(cat.label) > 0

    def test_category_exemples(self):
        """Test: chaque catégorie a des exemples."""
        for cat in CategorieRessource:
            assert cat.exemples is not None
            assert len(cat.exemples) > 0

    def test_category_validation_requise(self):
        """Test: validation_requise selon la catégorie."""
        assert CategorieRessource.ENGIN_LEVAGE.validation_requise is True
        assert CategorieRessource.ENGIN_TERRASSEMENT.validation_requise is True
        assert CategorieRessource.EQUIPEMENT.validation_requise is True
        assert CategorieRessource.VEHICULE.validation_requise is False
        assert CategorieRessource.GROS_OUTILLAGE.validation_requise is False

    def test_all_categories_method(self):
        """Test: all_categories retourne toutes les catégories."""
        all_cats = CategorieRessource.all_categories()
        assert len(all_cats) == 5


class TestStatutReservation:
    """Tests pour StatutReservation."""

    def test_all_statuts_exist(self):
        """Test: tous les statuts sont définis."""
        assert StatutReservation.EN_ATTENTE
        assert StatutReservation.VALIDEE
        assert StatutReservation.REFUSEE
        assert StatutReservation.ANNULEE

    def test_statut_values(self):
        """Test: les valeurs des statuts sont correctes."""
        assert StatutReservation.EN_ATTENTE.value == "en_attente"
        assert StatutReservation.VALIDEE.value == "validee"
        assert StatutReservation.REFUSEE.value == "refusee"
        assert StatutReservation.ANNULEE.value == "annulee"

    def test_statut_labels(self):
        """Test: chaque statut a un label."""
        for statut in StatutReservation:
            assert statut.label is not None
            assert len(statut.label) > 0

    def test_statut_colors(self):
        """Test: chaque statut a une couleur."""
        for statut in StatutReservation:
            assert statut.couleur is not None
            assert statut.couleur.startswith("#")

    def test_statut_emoji(self):
        """Test: chaque statut a un emoji."""
        for statut in StatutReservation:
            assert statut.emoji is not None

    def test_transition_en_attente_vers_validee(self):
        """Test: transition EN_ATTENTE -> VALIDEE autorisée."""
        assert StatutReservation.EN_ATTENTE.peut_transitionner_vers(StatutReservation.VALIDEE)

    def test_transition_en_attente_vers_refusee(self):
        """Test: transition EN_ATTENTE -> REFUSEE autorisée."""
        assert StatutReservation.EN_ATTENTE.peut_transitionner_vers(StatutReservation.REFUSEE)

    def test_transition_en_attente_vers_annulee(self):
        """Test: transition EN_ATTENTE -> ANNULEE autorisée."""
        assert StatutReservation.EN_ATTENTE.peut_transitionner_vers(StatutReservation.ANNULEE)

    def test_transition_validee_vers_annulee(self):
        """Test: transition VALIDEE -> ANNULEE autorisée."""
        assert StatutReservation.VALIDEE.peut_transitionner_vers(StatutReservation.ANNULEE)

    def test_transition_validee_vers_refusee_interdite(self):
        """Test: transition VALIDEE -> REFUSEE interdite."""
        assert not StatutReservation.VALIDEE.peut_transitionner_vers(StatutReservation.REFUSEE)

    def test_transition_refusee_vers_validee_interdite(self):
        """Test: transition REFUSEE -> VALIDEE interdite."""
        assert not StatutReservation.REFUSEE.peut_transitionner_vers(StatutReservation.VALIDEE)

    def test_transition_annulee_vers_validee_interdite(self):
        """Test: transition ANNULEE -> VALIDEE interdite."""
        assert not StatutReservation.ANNULEE.peut_transitionner_vers(StatutReservation.VALIDEE)

    def test_est_finale_refusee(self):
        """Test: REFUSEE est un état final."""
        assert StatutReservation.REFUSEE.est_finale

    def test_est_finale_annulee(self):
        """Test: ANNULEE est un état final."""
        assert StatutReservation.ANNULEE.est_finale

    def test_est_finale_en_attente(self):
        """Test: EN_ATTENTE n'est pas un état final."""
        assert not StatutReservation.EN_ATTENTE.est_finale

    def test_est_finale_validee(self):
        """Test: VALIDEE n'est pas un état final."""
        assert not StatutReservation.VALIDEE.est_finale

    def test_est_active_en_attente(self):
        """Test: EN_ATTENTE est active."""
        assert StatutReservation.EN_ATTENTE.est_active

    def test_est_active_validee(self):
        """Test: VALIDEE est active."""
        assert StatutReservation.VALIDEE.est_active

    def test_est_active_refusee(self):
        """Test: REFUSEE n'est pas active."""
        assert not StatutReservation.REFUSEE.est_active

    def test_initial(self):
        """Test: statut initial."""
        assert StatutReservation.initial() == StatutReservation.EN_ATTENTE


class TestPlageHoraire:
    """Tests pour PlageHoraire."""

    def test_creation_plage_valide(self):
        """Test: création d'une plage horaire valide."""
        plage = PlageHoraire(heure_debut=time(8, 0), heure_fin=time(12, 0))
        assert plage.heure_debut == time(8, 0)
        assert plage.heure_fin == time(12, 0)

    def test_plage_horaire_immutable(self):
        """Test: PlageHoraire est immuable (frozen)."""
        plage = PlageHoraire(heure_debut=time(8, 0), heure_fin=time(12, 0))
        with pytest.raises(Exception):  # FrozenInstanceError
            plage.heure_debut = time(9, 0)

    def test_duree_en_minutes(self):
        """Test: calcul de la durée en minutes."""
        plage = PlageHoraire(heure_debut=time(8, 0), heure_fin=time(12, 0))
        assert plage.duree_minutes == 240  # 4 heures = 240 minutes

    def test_duree_en_heures(self):
        """Test: calcul de la durée en heures."""
        plage = PlageHoraire(heure_debut=time(8, 0), heure_fin=time(12, 0))
        assert plage.duree_heures == 4.0

    def test_chevauchement_total(self):
        """Test: détection de chevauchement total."""
        plage1 = PlageHoraire(heure_debut=time(8, 0), heure_fin=time(12, 0))
        plage2 = PlageHoraire(heure_debut=time(9, 0), heure_fin=time(11, 0))
        assert plage1.chevauche(plage2)
        assert plage2.chevauche(plage1)

    def test_chevauchement_partiel_debut(self):
        """Test: détection de chevauchement partiel au début."""
        plage1 = PlageHoraire(heure_debut=time(8, 0), heure_fin=time(12, 0))
        plage2 = PlageHoraire(heure_debut=time(7, 0), heure_fin=time(9, 0))
        assert plage1.chevauche(plage2)

    def test_chevauchement_partiel_fin(self):
        """Test: détection de chevauchement partiel à la fin."""
        plage1 = PlageHoraire(heure_debut=time(8, 0), heure_fin=time(12, 0))
        plage2 = PlageHoraire(heure_debut=time(11, 0), heure_fin=time(14, 0))
        assert plage1.chevauche(plage2)

    def test_pas_de_chevauchement_avant(self):
        """Test: pas de chevauchement quand plage2 avant plage1."""
        plage1 = PlageHoraire(heure_debut=time(10, 0), heure_fin=time(12, 0))
        plage2 = PlageHoraire(heure_debut=time(8, 0), heure_fin=time(9, 0))
        assert not plage1.chevauche(plage2)

    def test_pas_de_chevauchement_apres(self):
        """Test: pas de chevauchement quand plage2 après plage1."""
        plage1 = PlageHoraire(heure_debut=time(8, 0), heure_fin=time(10, 0))
        plage2 = PlageHoraire(heure_debut=time(11, 0), heure_fin=time(13, 0))
        assert not plage1.chevauche(plage2)

    def test_adjacentes_pas_de_chevauchement(self):
        """Test: plages adjacentes ne se chevauchent pas."""
        plage1 = PlageHoraire(heure_debut=time(8, 0), heure_fin=time(10, 0))
        plage2 = PlageHoraire(heure_debut=time(10, 0), heure_fin=time(12, 0))
        assert not plage1.chevauche(plage2)

    def test_contient_heure(self):
        """Test: vérification qu'une heure est dans la plage."""
        plage = PlageHoraire(heure_debut=time(8, 0), heure_fin=time(12, 0))
        assert plage.contient(time(10, 0))
        assert plage.contient(time(8, 0))  # Borne incluse
        assert not plage.contient(time(12, 0))  # Borne exclue
        assert not plage.contient(time(7, 0))
        assert not plage.contient(time(13, 0))

    def test_format_display(self):
        """Test: format d'affichage."""
        plage = PlageHoraire(heure_debut=time(8, 0), heure_fin=time(12, 0))
        assert plage.format_display() == "08:00 - 12:00"

    def test_par_defaut(self):
        """Test: plage par défaut."""
        plage = PlageHoraire.par_defaut()
        assert plage.heure_debut == time(8, 0)
        assert plage.heure_fin == time(18, 0)

    def test_from_strings(self):
        """Test: création depuis des chaînes."""
        plage = PlageHoraire.from_strings("09:00", "17:00")
        assert plage.heure_debut == time(9, 0)
        assert plage.heure_fin == time(17, 0)

    def test_equality(self):
        """Test: égalité entre PlageHoraire."""
        plage1 = PlageHoraire(heure_debut=time(8, 0), heure_fin=time(12, 0))
        plage2 = PlageHoraire(heure_debut=time(8, 0), heure_fin=time(12, 0))
        plage3 = PlageHoraire(heure_debut=time(9, 0), heure_fin=time(12, 0))
        assert plage1 == plage2
        assert plage1 != plage3

    def test_to_dict(self):
        """Test: conversion en dictionnaire."""
        plage = PlageHoraire(heure_debut=time(8, 0), heure_fin=time(12, 0))
        d = plage.to_dict()
        assert d["heure_debut"] == "08:00:00"
        assert d["heure_fin"] == "12:00:00"

    def test_creation_plage_invalide_raises_error(self):
        """Test: erreur si heure fin avant heure début."""
        with pytest.raises(ValueError):
            PlageHoraire(heure_debut=time(12, 0), heure_fin=time(8, 0))
