"""Tests unitaires pour les Value Objects du module Interventions."""

import pytest

from modules.interventions.domain.value_objects import (
    StatutIntervention,
    PrioriteIntervention,
    TypeIntervention,
)


class TestStatutIntervention:
    """Tests pour StatutIntervention."""

    def test_statut_values(self):
        """Verifie que tous les statuts sont definis."""
        assert StatutIntervention.A_PLANIFIER.value == "a_planifier"
        assert StatutIntervention.PLANIFIEE.value == "planifiee"
        assert StatutIntervention.EN_COURS.value == "en_cours"
        assert StatutIntervention.TERMINEE.value == "terminee"
        assert StatutIntervention.ANNULEE.value == "annulee"

    def test_statut_labels(self):
        """Verifie les labels des statuts."""
        assert StatutIntervention.A_PLANIFIER.label == "A planifier"
        assert StatutIntervention.PLANIFIEE.label == "Planifiee"
        assert StatutIntervention.EN_COURS.label == "En cours"
        assert StatutIntervention.TERMINEE.label == "Terminee"
        assert StatutIntervention.ANNULEE.label == "Annulee"

    def test_statut_couleurs(self):
        """Verifie que chaque statut a une couleur."""
        for statut in StatutIntervention:
            assert statut.couleur.startswith("#")
            assert len(statut.couleur) == 7

    def test_statut_icones(self):
        """Verifie que chaque statut a une icone."""
        for statut in StatutIntervention:
            assert len(statut.icone) > 0

    def test_est_active(self):
        """Verifie la propriete est_active."""
        assert StatutIntervention.A_PLANIFIER.est_active is True
        assert StatutIntervention.PLANIFIEE.est_active is True
        assert StatutIntervention.EN_COURS.est_active is True
        assert StatutIntervention.TERMINEE.est_active is False
        assert StatutIntervention.ANNULEE.est_active is False

    def test_est_modifiable(self):
        """Verifie la propriete est_modifiable."""
        assert StatutIntervention.A_PLANIFIER.est_modifiable is True
        assert StatutIntervention.PLANIFIEE.est_modifiable is True
        assert StatutIntervention.EN_COURS.est_modifiable is True
        assert StatutIntervention.TERMINEE.est_modifiable is True
        assert StatutIntervention.ANNULEE.est_modifiable is False

    def test_transitions_possibles_a_planifier(self):
        """Verifie les transitions depuis A_PLANIFIER."""
        transitions = StatutIntervention.A_PLANIFIER.transitions_possibles()
        assert StatutIntervention.PLANIFIEE in transitions
        assert StatutIntervention.ANNULEE in transitions
        assert StatutIntervention.EN_COURS not in transitions
        assert StatutIntervention.TERMINEE not in transitions

    def test_transitions_possibles_planifiee(self):
        """Verifie les transitions depuis PLANIFIEE."""
        transitions = StatutIntervention.PLANIFIEE.transitions_possibles()
        assert StatutIntervention.EN_COURS in transitions
        assert StatutIntervention.A_PLANIFIER in transitions
        assert StatutIntervention.ANNULEE in transitions
        assert StatutIntervention.TERMINEE not in transitions

    def test_transitions_possibles_en_cours(self):
        """Verifie les transitions depuis EN_COURS."""
        transitions = StatutIntervention.EN_COURS.transitions_possibles()
        assert StatutIntervention.TERMINEE in transitions
        assert StatutIntervention.ANNULEE in transitions
        assert StatutIntervention.PLANIFIEE not in transitions

    def test_transitions_possibles_terminee(self):
        """Verifie qu'aucune transition n'est possible depuis TERMINEE."""
        transitions = StatutIntervention.TERMINEE.transitions_possibles()
        assert len(transitions) == 0

    def test_transitions_possibles_annulee(self):
        """Verifie qu'aucune transition n'est possible depuis ANNULEE."""
        transitions = StatutIntervention.ANNULEE.transitions_possibles()
        assert len(transitions) == 0

    def test_peut_transitionner_vers_valid(self):
        """Verifie les transitions valides."""
        assert StatutIntervention.A_PLANIFIER.peut_transitionner_vers(
            StatutIntervention.PLANIFIEE
        )
        assert StatutIntervention.PLANIFIEE.peut_transitionner_vers(
            StatutIntervention.EN_COURS
        )
        assert StatutIntervention.EN_COURS.peut_transitionner_vers(
            StatutIntervention.TERMINEE
        )

    def test_peut_transitionner_vers_invalid(self):
        """Verifie les transitions invalides."""
        assert not StatutIntervention.A_PLANIFIER.peut_transitionner_vers(
            StatutIntervention.TERMINEE
        )
        assert not StatutIntervention.TERMINEE.peut_transitionner_vers(
            StatutIntervention.A_PLANIFIER
        )
        assert not StatutIntervention.ANNULEE.peut_transitionner_vers(
            StatutIntervention.EN_COURS
        )


class TestPrioriteIntervention:
    """Tests pour PrioriteIntervention."""

    def test_priorite_values(self):
        """Verifie que toutes les priorites sont definies."""
        assert PrioriteIntervention.BASSE.value == "basse"
        assert PrioriteIntervention.NORMALE.value == "normale"
        assert PrioriteIntervention.HAUTE.value == "haute"
        assert PrioriteIntervention.URGENTE.value == "urgente"

    def test_priorite_labels(self):
        """Verifie les labels des priorites."""
        assert PrioriteIntervention.BASSE.label == "Basse"
        assert PrioriteIntervention.NORMALE.label == "Normale"
        assert PrioriteIntervention.HAUTE.label == "Haute"
        assert PrioriteIntervention.URGENTE.label == "Urgente"

    def test_priorite_couleurs(self):
        """Verifie que chaque priorite a une couleur."""
        for priorite in PrioriteIntervention:
            assert priorite.couleur.startswith("#")
            assert len(priorite.couleur) == 7

    def test_priorite_ordre(self):
        """Verifie l'ordre des priorites."""
        assert PrioriteIntervention.BASSE.ordre == 1
        assert PrioriteIntervention.NORMALE.ordre == 2
        assert PrioriteIntervention.HAUTE.ordre == 3
        assert PrioriteIntervention.URGENTE.ordre == 4

    def test_priorite_comparaison(self):
        """Verifie la comparaison des priorites."""
        assert PrioriteIntervention.BASSE < PrioriteIntervention.NORMALE
        assert PrioriteIntervention.NORMALE < PrioriteIntervention.HAUTE
        assert PrioriteIntervention.HAUTE < PrioriteIntervention.URGENTE
        assert PrioriteIntervention.BASSE <= PrioriteIntervention.BASSE
        assert not PrioriteIntervention.URGENTE < PrioriteIntervention.BASSE


class TestTypeIntervention:
    """Tests pour TypeIntervention."""

    def test_type_values(self):
        """Verifie que tous les types sont definis."""
        assert TypeIntervention.SAV.value == "sav"
        assert TypeIntervention.MAINTENANCE.value == "maintenance"
        assert TypeIntervention.DEPANNAGE.value == "depannage"
        assert TypeIntervention.LEVEE_RESERVES.value == "levee_reserves"
        assert TypeIntervention.AUTRE.value == "autre"

    def test_type_labels(self):
        """Verifie les labels des types."""
        assert TypeIntervention.SAV.label == "SAV"
        assert TypeIntervention.MAINTENANCE.label == "Maintenance"
        assert TypeIntervention.DEPANNAGE.label == "Depannage"
        assert TypeIntervention.LEVEE_RESERVES.label == "Levee de reserves"
        assert TypeIntervention.AUTRE.label == "Autre"

    def test_type_couleurs(self):
        """Verifie que chaque type a une couleur."""
        for type_int in TypeIntervention:
            assert type_int.couleur.startswith("#")
            assert len(type_int.couleur) == 7

    def test_type_icones(self):
        """Verifie que chaque type a une icone."""
        for type_int in TypeIntervention:
            assert len(type_int.icone) > 0

    def test_type_descriptions(self):
        """Verifie que chaque type a une description."""
        for type_int in TypeIntervention:
            assert len(type_int.description) > 0
