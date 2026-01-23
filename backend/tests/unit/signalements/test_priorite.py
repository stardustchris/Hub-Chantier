"""Tests unitaires pour le Value Object Priorite."""

import pytest
from datetime import timedelta

from modules.signalements.domain.value_objects import Priorite


class TestPriorite:
    """Tests pour le value object Priorite."""

    def test_priorite_critique_delai_4h(self):
        """Test: priorité critique a un délai de 4 heures."""
        assert Priorite.CRITIQUE.delai_traitement == timedelta(hours=4)
        assert Priorite.CRITIQUE.delai_heures == 4

    def test_priorite_haute_delai_24h(self):
        """Test: priorité haute a un délai de 24 heures."""
        assert Priorite.HAUTE.delai_traitement == timedelta(hours=24)
        assert Priorite.HAUTE.delai_heures == 24

    def test_priorite_moyenne_delai_48h(self):
        """Test: priorité moyenne a un délai de 48 heures."""
        assert Priorite.MOYENNE.delai_traitement == timedelta(hours=48)
        assert Priorite.MOYENNE.delai_heures == 48

    def test_priorite_basse_delai_72h(self):
        """Test: priorité basse a un délai de 72 heures."""
        assert Priorite.BASSE.delai_traitement == timedelta(hours=72)
        assert Priorite.BASSE.delai_heures == 72

    def test_labels(self):
        """Test: chaque priorité a un label approprié."""
        assert Priorite.CRITIQUE.label == "Critique (4h)"
        assert Priorite.HAUTE.label == "Haute (24h)"
        assert Priorite.MOYENNE.label == "Moyenne (48h)"
        assert Priorite.BASSE.label == "Basse (72h)"

    def test_couleurs(self):
        """Test: chaque priorité a une couleur associée."""
        assert Priorite.CRITIQUE.couleur == "red"
        assert Priorite.HAUTE.couleur == "orange"
        assert Priorite.MOYENNE.couleur == "yellow"
        assert Priorite.BASSE.couleur == "green"

    def test_ordre_priorites(self):
        """Test: les priorités sont ordonnées correctement."""
        assert Priorite.CRITIQUE.ordre == 1
        assert Priorite.HAUTE.ordre == 2
        assert Priorite.MOYENNE.ordre == 3
        assert Priorite.BASSE.ordre == 4

    def test_from_string_valid(self):
        """Test: conversion de chaîne valide en Priorite."""
        assert Priorite.from_string("critique") == Priorite.CRITIQUE
        assert Priorite.from_string("HAUTE") == Priorite.HAUTE
        assert Priorite.from_string("Moyenne") == Priorite.MOYENNE
        assert Priorite.from_string("basse") == Priorite.BASSE

    def test_from_string_invalid(self):
        """Test: erreur avec chaîne invalide."""
        with pytest.raises(ValueError) as exc_info:
            Priorite.from_string("invalide")
        assert "Priorité invalide" in str(exc_info.value)

    def test_list_all_sorted(self):
        """Test: list_all retourne les priorités triées par ordre."""
        all_prios = Priorite.list_all()
        assert len(all_prios) == 4
        assert all_prios[0] == Priorite.CRITIQUE
        assert all_prios[1] == Priorite.HAUTE
        assert all_prios[2] == Priorite.MOYENNE
        assert all_prios[3] == Priorite.BASSE

    def test_values(self):
        """Test: les valeurs enum sont correctes."""
        assert Priorite.CRITIQUE.value == "critique"
        assert Priorite.HAUTE.value == "haute"
        assert Priorite.MOYENNE.value == "moyenne"
        assert Priorite.BASSE.value == "basse"
