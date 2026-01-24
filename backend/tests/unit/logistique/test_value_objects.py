"""Tests des Value Objects du module Logistique.

CDC Section 11 - Gestion de la logistique et du materiel.
"""

import pytest

from modules.logistique.domain.value_objects import TypeRessource, StatutReservation


class TestTypeRessource:
    """Tests pour TypeRessource."""

    def test_types_disponibles(self):
        """Verifie que tous les types de ressources sont disponibles."""
        assert TypeRessource.LEVAGE.value == "levage"
        assert TypeRessource.TERRASSEMENT.value == "terrassement"
        assert TypeRessource.VEHICULE.value == "vehicule"
        assert TypeRessource.OUTILLAGE.value == "outillage"
        assert TypeRessource.EQUIPEMENT.value == "equipement"

    def test_labels(self):
        """Verifie les labels affichables de chaque type."""
        assert TypeRessource.LEVAGE.label == "Engins de levage"
        assert TypeRessource.TERRASSEMENT.label == "Engins de terrassement"
        assert TypeRessource.VEHICULE.label == "Vehicules"
        assert TypeRessource.OUTILLAGE.label == "Gros outillage"
        assert TypeRessource.EQUIPEMENT.label == "Equipements"

    def test_validation_requise_par_defaut_levage(self):
        """Verifie que le type LEVAGE requiert validation N+1."""
        assert TypeRessource.LEVAGE.validation_requise_par_defaut is True

    def test_validation_requise_par_defaut_terrassement(self):
        """Verifie que le type TERRASSEMENT requiert validation N+1."""
        assert TypeRessource.TERRASSEMENT.validation_requise_par_defaut is True

    def test_validation_requise_par_defaut_equipement(self):
        """Verifie que le type EQUIPEMENT requiert validation N+1."""
        assert TypeRessource.EQUIPEMENT.validation_requise_par_defaut is True

    def test_validation_non_requise_par_defaut_vehicule(self):
        """Verifie que le type VEHICULE ne requiert pas validation N+1."""
        assert TypeRessource.VEHICULE.validation_requise_par_defaut is False

    def test_validation_non_requise_par_defaut_outillage(self):
        """Verifie que le type OUTILLAGE ne requiert pas validation N+1."""
        assert TypeRessource.OUTILLAGE.validation_requise_par_defaut is False

    def test_exemples_levage(self):
        """Verifie les exemples pour le type LEVAGE."""
        exemples = TypeRessource.LEVAGE.exemples
        assert "Grue mobile" in exemples
        assert "Manitou" in exemples
        assert "Nacelle" in exemples
        assert "Chariot elevateur" in exemples

    def test_exemples_terrassement(self):
        """Verifie les exemples pour le type TERRASSEMENT."""
        exemples = TypeRessource.TERRASSEMENT.exemples
        assert "Mini-pelle" in exemples
        assert "Pelleteuse" in exemples
        assert "Compacteur" in exemples
        assert "Dumper" in exemples

    def test_exemples_vehicule(self):
        """Verifie les exemples pour le type VEHICULE."""
        exemples = TypeRessource.VEHICULE.exemples
        assert "Camion benne" in exemples
        assert "Fourgon" in exemples
        assert "Vehicule utilitaire" in exemples

    def test_exemples_outillage(self):
        """Verifie les exemples pour le type OUTILLAGE."""
        exemples = TypeRessource.OUTILLAGE.exemples
        assert "Betonniere" in exemples
        assert "Vibrateur" in exemples
        assert "Pompe a beton" in exemples

    def test_exemples_equipement(self):
        """Verifie les exemples pour le type EQUIPEMENT."""
        exemples = TypeRessource.EQUIPEMENT.exemples
        assert "Echafaudage" in exemples
        assert "Etais" in exemples
        assert "Banches" in exemples
        assert "Coffrages" in exemples

    def test_type_ressource_est_str_enum(self):
        """Verifie que TypeRessource herite de str et Enum."""
        assert isinstance(TypeRessource.LEVAGE, str)
        assert TypeRessource.LEVAGE == "levage"

    def test_nombre_total_types(self):
        """Verifie le nombre total de types de ressources."""
        assert len(TypeRessource) == 5


class TestStatutReservation:
    """Tests pour StatutReservation."""

    def test_statuts_disponibles(self):
        """Verifie que tous les statuts sont disponibles."""
        assert StatutReservation.EN_ATTENTE.value == "en_attente"
        assert StatutReservation.VALIDEE.value == "validee"
        assert StatutReservation.REFUSEE.value == "refusee"
        assert StatutReservation.ANNULEE.value == "annulee"

    def test_labels(self):
        """Verifie les labels affichables de chaque statut."""
        assert StatutReservation.EN_ATTENTE.label == "En attente"
        assert StatutReservation.VALIDEE.label == "Validee"
        assert StatutReservation.REFUSEE.label == "Refusee"
        assert StatutReservation.ANNULEE.label == "Annulee"

    def test_couleurs_hexa(self):
        """Verifie les couleurs hexadecimales de chaque statut (LOG-12)."""
        assert StatutReservation.EN_ATTENTE.couleur == "#F1C40F"  # Jaune
        assert StatutReservation.VALIDEE.couleur == "#2ECC71"     # Vert
        assert StatutReservation.REFUSEE.couleur == "#E74C3C"     # Rouge
        assert StatutReservation.ANNULEE.couleur == "#95A5A6"     # Gris

    def test_emojis(self):
        """Verifie les emojis associes a chaque statut."""
        assert StatutReservation.EN_ATTENTE.emoji == "🟡"
        assert StatutReservation.VALIDEE.emoji == "🟢"
        assert StatutReservation.REFUSEE.emoji == "🔴"
        assert StatutReservation.ANNULEE.emoji == "⚪"

    def test_is_active_en_attente(self):
        """Verifie qu'une reservation EN_ATTENTE est active."""
        assert StatutReservation.EN_ATTENTE.is_active is True

    def test_is_active_validee(self):
        """Verifie qu'une reservation VALIDEE est active."""
        assert StatutReservation.VALIDEE.is_active is True

    def test_is_active_refusee(self):
        """Verifie qu'une reservation REFUSEE n'est pas active."""
        assert StatutReservation.REFUSEE.is_active is False

    def test_is_active_annulee(self):
        """Verifie qu'une reservation ANNULEE n'est pas active."""
        assert StatutReservation.ANNULEE.is_active is False

    # Transitions valides depuis EN_ATTENTE

    def test_transition_en_attente_vers_validee(self):
        """EN_ATTENTE peut transitionner vers VALIDEE."""
        assert StatutReservation.EN_ATTENTE.peut_transitionner_vers(
            StatutReservation.VALIDEE
        ) is True

    def test_transition_en_attente_vers_refusee(self):
        """EN_ATTENTE peut transitionner vers REFUSEE."""
        assert StatutReservation.EN_ATTENTE.peut_transitionner_vers(
            StatutReservation.REFUSEE
        ) is True

    def test_transition_en_attente_vers_annulee(self):
        """EN_ATTENTE peut transitionner vers ANNULEE."""
        assert StatutReservation.EN_ATTENTE.peut_transitionner_vers(
            StatutReservation.ANNULEE
        ) is True

    # Transitions valides depuis VALIDEE

    def test_transition_validee_vers_annulee(self):
        """VALIDEE peut transitionner vers ANNULEE."""
        assert StatutReservation.VALIDEE.peut_transitionner_vers(
            StatutReservation.ANNULEE
        ) is True

    # Transitions invalides depuis VALIDEE

    def test_transition_validee_vers_refusee_invalide(self):
        """VALIDEE ne peut pas transitionner vers REFUSEE."""
        assert StatutReservation.VALIDEE.peut_transitionner_vers(
            StatutReservation.REFUSEE
        ) is False

    def test_transition_validee_vers_en_attente_invalide(self):
        """VALIDEE ne peut pas transitionner vers EN_ATTENTE."""
        assert StatutReservation.VALIDEE.peut_transitionner_vers(
            StatutReservation.EN_ATTENTE
        ) is False

    # Transitions invalides depuis REFUSEE (terminal)

    def test_transition_refusee_est_terminal(self):
        """REFUSEE est un statut terminal, aucune transition permise."""
        assert StatutReservation.REFUSEE.peut_transitionner_vers(
            StatutReservation.EN_ATTENTE
        ) is False
        assert StatutReservation.REFUSEE.peut_transitionner_vers(
            StatutReservation.VALIDEE
        ) is False
        assert StatutReservation.REFUSEE.peut_transitionner_vers(
            StatutReservation.ANNULEE
        ) is False

    # Transitions invalides depuis ANNULEE (terminal)

    def test_transition_annulee_est_terminal(self):
        """ANNULEE est un statut terminal, aucune transition permise."""
        assert StatutReservation.ANNULEE.peut_transitionner_vers(
            StatutReservation.EN_ATTENTE
        ) is False
        assert StatutReservation.ANNULEE.peut_transitionner_vers(
            StatutReservation.VALIDEE
        ) is False
        assert StatutReservation.ANNULEE.peut_transitionner_vers(
            StatutReservation.REFUSEE
        ) is False

    # Transitions vers soi-meme invalides

    def test_transition_vers_soi_meme_invalide(self):
        """Un statut ne peut pas transitionner vers lui-meme."""
        for statut in StatutReservation:
            assert statut.peut_transitionner_vers(statut) is False

    def test_statut_reservation_est_str_enum(self):
        """Verifie que StatutReservation herite de str et Enum."""
        assert isinstance(StatutReservation.EN_ATTENTE, str)
        assert StatutReservation.EN_ATTENTE == "en_attente"

    def test_nombre_total_statuts(self):
        """Verifie le nombre total de statuts."""
        assert len(StatutReservation) == 4

    def test_workflow_complet_validation(self):
        """Test du workflow complet: EN_ATTENTE -> VALIDEE -> ANNULEE."""
        statut = StatutReservation.EN_ATTENTE
        assert statut.peut_transitionner_vers(StatutReservation.VALIDEE) is True
        statut = StatutReservation.VALIDEE
        assert statut.peut_transitionner_vers(StatutReservation.ANNULEE) is True

    def test_workflow_complet_refus(self):
        """Test du workflow complet: EN_ATTENTE -> REFUSEE (terminal)."""
        statut = StatutReservation.EN_ATTENTE
        assert statut.peut_transitionner_vers(StatutReservation.REFUSEE) is True
        statut = StatutReservation.REFUSEE
        # REFUSEE est terminal
        for autre_statut in StatutReservation:
            assert statut.peut_transitionner_vers(autre_statut) is False

    def test_workflow_annulation_directe(self):
        """Test du workflow: EN_ATTENTE -> ANNULEE (terminal)."""
        statut = StatutReservation.EN_ATTENTE
        assert statut.peut_transitionner_vers(StatutReservation.ANNULEE) is True
        statut = StatutReservation.ANNULEE
        # ANNULEE est terminal
        for autre_statut in StatutReservation:
            assert statut.peut_transitionner_vers(autre_statut) is False
