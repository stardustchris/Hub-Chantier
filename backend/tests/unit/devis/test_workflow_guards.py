"""Tests unitaires pour les guards du workflow devis.

DEV-15: Suivi statut devis - Guards role-based.
Couche Domain - services/workflow_guards.py
"""

import pytest
from decimal import Decimal

from modules.devis.domain.services.workflow_guards import (
    WorkflowGuards,
    TransitionNonAutoriseeError,
)


class TestWorkflowGuardsRoles:
    """Tests des guards par role."""

    def test_admin_peut_tout_faire(self):
        """Test: admin a acces a toutes les transitions."""
        transitions = [
            "soumettre", "valider", "retourner_brouillon",
            "marquer_vu", "negociation", "accepter",
            "refuser", "perdu", "expirer",
        ]
        for transition in transitions:
            assert WorkflowGuards.peut_effectuer_transition("admin", transition)

    def test_conducteur_transitions_autorisees(self):
        """Test: conducteur peut effectuer la plupart des transitions."""
        autorisees = ["soumettre", "valider", "retourner_brouillon",
                      "marquer_vu", "negociation", "accepter", "refuser", "perdu"]
        for transition in autorisees:
            assert WorkflowGuards.peut_effectuer_transition("conducteur", transition), \
                f"conducteur devrait pouvoir effectuer {transition}"

    def test_conducteur_ne_peut_pas_expirer(self):
        """Test: conducteur ne peut pas expirer un devis (action systeme)."""
        assert not WorkflowGuards.peut_effectuer_transition("conducteur", "expirer")

    def test_commercial_transitions_autorisees(self):
        """Test: commercial peut soumettre, valider, marquer vu, negocier, refuser."""
        autorisees = ["soumettre", "valider", "marquer_vu", "negociation", "refuser"]
        for transition in autorisees:
            assert WorkflowGuards.peut_effectuer_transition("commercial", transition), \
                f"commercial devrait pouvoir effectuer {transition}"

    def test_commercial_ne_peut_pas_accepter(self):
        """Test: commercial ne peut pas accepter un devis."""
        assert not WorkflowGuards.peut_effectuer_transition("commercial", "accepter")

    def test_commercial_ne_peut_pas_marquer_perdu(self):
        """Test: commercial ne peut pas marquer un devis comme perdu."""
        assert not WorkflowGuards.peut_effectuer_transition("commercial", "perdu")

    def test_chef_chantier_aucune_transition(self):
        """Test: chef de chantier ne peut effectuer aucune transition."""
        transitions = ["soumettre", "valider", "accepter", "refuser"]
        for transition in transitions:
            assert not WorkflowGuards.peut_effectuer_transition("chef_chantier", transition)

    def test_compagnon_aucune_transition(self):
        """Test: compagnon ne peut effectuer aucune transition."""
        assert not WorkflowGuards.peut_effectuer_transition("compagnon", "soumettre")


class TestWorkflowGuardsVerification:
    """Tests de la methode verifier_transition."""

    def test_verifier_transition_ok(self):
        """Test: pas d'exception si transition autorisee."""
        # Ne doit pas lever d'exception
        WorkflowGuards.verifier_transition("admin", "soumettre")

    def test_verifier_transition_role_interdit(self):
        """Test: exception si role non autorise."""
        with pytest.raises(TransitionNonAutoriseeError) as exc_info:
            WorkflowGuards.verifier_transition("compagnon", "soumettre")
        assert "compagnon" in str(exc_info.value)
        assert "soumettre" in str(exc_info.value)

    def test_verifier_transition_inconnue(self):
        """Test: exception si transition inconnue."""
        with pytest.raises(TransitionNonAutoriseeError) as exc_info:
            WorkflowGuards.verifier_transition("admin", "transition_inconnue")
        assert "inconnue" in str(exc_info.value)


class TestWorkflowGuardsSeuil50k:
    """Tests du guard seuil 50k EUR pour validation."""

    def test_validation_sous_seuil_conducteur_ok(self):
        """Test: conducteur peut valider un devis sous 50k EUR."""
        WorkflowGuards.verifier_transition("conducteur", "valider", montant_ht=49_999)

    def test_validation_au_seuil_conducteur_interdit(self):
        """Test: conducteur ne peut pas valider un devis a 50k EUR."""
        with pytest.raises(TransitionNonAutoriseeError) as exc_info:
            WorkflowGuards.verifier_transition("conducteur", "valider", montant_ht=50_000)
        assert "50000" in str(exc_info.value)

    def test_validation_au_dessus_seuil_conducteur_interdit(self):
        """Test: conducteur ne peut pas valider un devis au-dessus de 50k EUR."""
        with pytest.raises(TransitionNonAutoriseeError):
            WorkflowGuards.verifier_transition("conducteur", "valider", montant_ht=75_000)

    def test_validation_au_seuil_admin_ok(self):
        """Test: admin peut valider un devis a 50k EUR."""
        WorkflowGuards.verifier_transition("admin", "valider", montant_ht=50_000)

    def test_validation_au_dessus_seuil_admin_ok(self):
        """Test: admin peut valider un devis au-dessus de 50k EUR."""
        WorkflowGuards.verifier_transition("admin", "valider", montant_ht=100_000)

    def test_validation_sans_montant_commercial_ok(self):
        """Test: commercial peut valider sans montant specifie."""
        WorkflowGuards.verifier_transition("commercial", "valider")


class TestWorkflowGuardsTransitionInfo:
    """Tests de l'attribut d'erreur."""

    def test_erreur_contient_role_et_transition(self):
        """Test: l'erreur contient le role et la transition."""
        with pytest.raises(TransitionNonAutoriseeError) as exc_info:
            WorkflowGuards.verifier_transition("compagnon", "accepter")
        err = exc_info.value
        assert err.role == "compagnon"
        assert err.transition == "accepter"
