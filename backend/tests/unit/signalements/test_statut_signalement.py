"""Tests unitaires pour le Value Object StatutSignalement."""

import pytest

from modules.signalements.domain.value_objects import StatutSignalement


class TestStatutSignalement:
    """Tests pour le value object StatutSignalement."""

    def test_labels(self):
        """Test: chaque statut a un label approprié."""
        assert StatutSignalement.OUVERT.label == "Ouvert"
        assert StatutSignalement.EN_COURS.label == "En cours"
        assert StatutSignalement.TRAITE.label == "Traité"
        assert StatutSignalement.CLOTURE.label == "Clôturé"

    def test_couleurs(self):
        """Test: chaque statut a une couleur associée."""
        assert StatutSignalement.OUVERT.couleur == "red"
        assert StatutSignalement.EN_COURS.couleur == "orange"
        assert StatutSignalement.TRAITE.couleur == "blue"
        assert StatutSignalement.CLOTURE.couleur == "green"

    def test_est_actif(self):
        """Test: seuls OUVERT et EN_COURS sont actifs."""
        assert StatutSignalement.OUVERT.est_actif is True
        assert StatutSignalement.EN_COURS.est_actif is True
        assert StatutSignalement.TRAITE.est_actif is False
        assert StatutSignalement.CLOTURE.est_actif is False

    def test_est_resolu(self):
        """Test: seuls TRAITE et CLOTURE sont résolus."""
        assert StatutSignalement.OUVERT.est_resolu is False
        assert StatutSignalement.EN_COURS.est_resolu is False
        assert StatutSignalement.TRAITE.est_resolu is True
        assert StatutSignalement.CLOTURE.est_resolu is True

    def test_peut_etre_modifie(self):
        """Test: seul CLOTURE ne peut pas être modifié."""
        assert StatutSignalement.OUVERT.peut_etre_modifie is True
        assert StatutSignalement.EN_COURS.peut_etre_modifie is True
        assert StatutSignalement.TRAITE.peut_etre_modifie is True
        assert StatutSignalement.CLOTURE.peut_etre_modifie is False

    def test_ordre(self):
        """Test: les statuts sont ordonnés correctement."""
        assert StatutSignalement.OUVERT.ordre == 1
        assert StatutSignalement.EN_COURS.ordre == 2
        assert StatutSignalement.TRAITE.ordre == 3
        assert StatutSignalement.CLOTURE.ordre == 4

    def test_transition_ouvert_vers_en_cours(self):
        """Test: OUVERT peut passer à EN_COURS."""
        assert StatutSignalement.OUVERT.peut_transitionner_vers(
            StatutSignalement.EN_COURS
        ) is True

    def test_transition_ouvert_vers_traite(self):
        """Test: OUVERT peut passer directement à TRAITE."""
        assert StatutSignalement.OUVERT.peut_transitionner_vers(
            StatutSignalement.TRAITE
        ) is True

    def test_transition_ouvert_vers_cloture_interdit(self):
        """Test: OUVERT ne peut PAS passer directement à CLOTURE (doit passer par TRAITE)."""
        assert StatutSignalement.OUVERT.peut_transitionner_vers(
            StatutSignalement.CLOTURE
        ) is False

    def test_transition_en_cours_vers_traite(self):
        """Test: EN_COURS peut passer à TRAITE."""
        assert StatutSignalement.EN_COURS.peut_transitionner_vers(
            StatutSignalement.TRAITE
        ) is True

    def test_transition_en_cours_vers_cloture_interdit(self):
        """Test: EN_COURS ne peut PAS passer directement à CLOTURE (doit passer par TRAITE)."""
        assert StatutSignalement.EN_COURS.peut_transitionner_vers(
            StatutSignalement.CLOTURE
        ) is False

    def test_transition_en_cours_vers_ouvert_reouverture(self):
        """Test: EN_COURS peut revenir à OUVERT (réouverture)."""
        assert StatutSignalement.EN_COURS.peut_transitionner_vers(
            StatutSignalement.OUVERT
        ) is True

    def test_transition_traite_vers_cloture(self):
        """Test: TRAITE peut passer à CLOTURE."""
        assert StatutSignalement.TRAITE.peut_transitionner_vers(
            StatutSignalement.CLOTURE
        ) is True

    def test_transition_traite_vers_ouvert_reouverture(self):
        """Test: TRAITE peut revenir à OUVERT (réouverture)."""
        assert StatutSignalement.TRAITE.peut_transitionner_vers(
            StatutSignalement.OUVERT
        ) is True

    def test_transition_traite_vers_en_cours_invalide(self):
        """Test: TRAITE ne peut pas passer à EN_COURS."""
        assert StatutSignalement.TRAITE.peut_transitionner_vers(
            StatutSignalement.EN_COURS
        ) is False

    def test_transition_cloture_vers_ouvert_reouverture(self):
        """Test: CLOTURE peut revenir à OUVERT (réouverture exceptionnelle)."""
        assert StatutSignalement.CLOTURE.peut_transitionner_vers(
            StatutSignalement.OUVERT
        ) is True

    def test_transition_cloture_vers_en_cours_invalide(self):
        """Test: CLOTURE ne peut pas passer à EN_COURS."""
        assert StatutSignalement.CLOTURE.peut_transitionner_vers(
            StatutSignalement.EN_COURS
        ) is False

    def test_transition_cloture_vers_traite_invalide(self):
        """Test: CLOTURE ne peut pas passer à TRAITE."""
        assert StatutSignalement.CLOTURE.peut_transitionner_vers(
            StatutSignalement.TRAITE
        ) is False

    def test_from_string_valid(self):
        """Test: conversion de chaîne valide en StatutSignalement."""
        assert StatutSignalement.from_string("ouvert") == StatutSignalement.OUVERT
        assert StatutSignalement.from_string("EN_COURS") == StatutSignalement.EN_COURS
        assert StatutSignalement.from_string("Traite") == StatutSignalement.TRAITE
        assert StatutSignalement.from_string("CLOTURE") == StatutSignalement.CLOTURE

    def test_from_string_invalid(self):
        """Test: erreur avec chaîne invalide."""
        with pytest.raises(ValueError) as exc_info:
            StatutSignalement.from_string("invalide")
        assert "Statut invalide" in str(exc_info.value)

    def test_list_actifs(self):
        """Test: list_actifs retourne OUVERT et EN_COURS."""
        actifs = StatutSignalement.list_actifs()
        assert len(actifs) == 2
        assert StatutSignalement.OUVERT in actifs
        assert StatutSignalement.EN_COURS in actifs

    def test_list_all_sorted(self):
        """Test: list_all retourne tous les statuts triés."""
        all_statuts = StatutSignalement.list_all()
        assert len(all_statuts) == 4
        assert all_statuts[0] == StatutSignalement.OUVERT
        assert all_statuts[1] == StatutSignalement.EN_COURS
        assert all_statuts[2] == StatutSignalement.TRAITE
        assert all_statuts[3] == StatutSignalement.CLOTURE

    def test_values(self):
        """Test: les valeurs enum sont correctes."""
        assert StatutSignalement.OUVERT.value == "ouvert"
        assert StatutSignalement.EN_COURS.value == "en_cours"
        assert StatutSignalement.TRAITE.value == "traite"
        assert StatutSignalement.CLOTURE.value == "cloture"
