"""Tests unitaires pour le Value Object StatutDevis.

DEV-15: Workflow statut devis - State machine complete.
Tests des transitions valides/invalides, proprietes et methodes.
"""

import pytest

from modules.devis.domain.value_objects.statut_devis import StatutDevis


class TestStatutDevisValues:
    """Tests pour les valeurs et proprietes des statuts."""

    def test_all_statuts_exist(self):
        """Test: tous les statuts sont definis."""
        assert StatutDevis.BROUILLON
        assert StatutDevis.EN_VALIDATION
        assert StatutDevis.ENVOYE
        assert StatutDevis.VU
        assert StatutDevis.EN_NEGOCIATION
        assert StatutDevis.ACCEPTE
        assert StatutDevis.REFUSE
        assert StatutDevis.PERDU
        assert StatutDevis.EXPIRE

    def test_statut_values(self):
        """Test: les valeurs string des statuts sont correctes."""
        assert StatutDevis.BROUILLON.value == "brouillon"
        assert StatutDevis.EN_VALIDATION.value == "en_validation"
        assert StatutDevis.ENVOYE.value == "envoye"
        assert StatutDevis.VU.value == "vu"
        assert StatutDevis.EN_NEGOCIATION.value == "en_negociation"
        assert StatutDevis.ACCEPTE.value == "accepte"
        assert StatutDevis.REFUSE.value == "refuse"
        assert StatutDevis.PERDU.value == "perdu"
        assert StatutDevis.EXPIRE.value == "expire"

    def test_is_string_enum(self):
        """Test: StatutDevis est un str Enum."""
        assert isinstance(StatutDevis.BROUILLON, str)

    def test_total_statuts_count(self):
        """Test: il y a exactement 9 statuts."""
        assert len(StatutDevis) == 9


class TestStatutDevisLabels:
    """Tests pour les labels affichables."""

    def test_each_statut_has_label(self):
        """Test: chaque statut a un label non vide."""
        for statut in StatutDevis:
            assert statut.label is not None
            assert len(statut.label) > 0

    def test_specific_labels(self):
        """Test: labels specifiques corrects."""
        assert StatutDevis.BROUILLON.label == "Brouillon"
        assert StatutDevis.EN_VALIDATION.label == "En validation"
        assert StatutDevis.ENVOYE.label == "Envoye"
        assert StatutDevis.VU.label == "Vu"
        assert StatutDevis.EN_NEGOCIATION.label == "En negociation"
        assert StatutDevis.ACCEPTE.label == "Accepte"
        assert StatutDevis.REFUSE.label == "Refuse"
        assert StatutDevis.PERDU.label == "Perdu"
        assert StatutDevis.EXPIRE.label == "Expire"


class TestStatutDevisCouleurs:
    """Tests pour les couleurs CSS."""

    def test_each_statut_has_couleur(self):
        """Test: chaque statut a une couleur CSS valide."""
        for statut in StatutDevis:
            assert statut.couleur is not None
            assert statut.couleur.startswith("#")
            assert len(statut.couleur) == 7  # format #RRGGBB

    def test_specific_couleurs(self):
        """Test: couleurs specifiques correctes."""
        assert StatutDevis.BROUILLON.couleur == "#9E9E9E"
        assert StatutDevis.ACCEPTE.couleur == "#4CAF50"
        assert StatutDevis.REFUSE.couleur == "#F44336"


class TestStatutDevisProprietesMetier:
    """Tests pour les proprietes metier (est_final, est_modifiable, est_actif)."""

    # est_final
    def test_accepte_est_final(self):
        """Test: ACCEPTE est un etat final."""
        assert StatutDevis.ACCEPTE.est_final is True

    def test_refuse_est_final(self):
        """Test: REFUSE est un etat final."""
        assert StatutDevis.REFUSE.est_final is True

    def test_perdu_est_final(self):
        """Test: PERDU est un etat final."""
        assert StatutDevis.PERDU.est_final is True

    def test_brouillon_non_final(self):
        """Test: BROUILLON n'est pas un etat final."""
        assert StatutDevis.BROUILLON.est_final is False

    def test_envoye_non_final(self):
        """Test: ENVOYE n'est pas un etat final."""
        assert StatutDevis.ENVOYE.est_final is False

    def test_expire_non_final(self):
        """Test: EXPIRE n'est pas un etat final."""
        assert StatutDevis.EXPIRE.est_final is False

    def test_en_validation_non_final(self):
        """Test: EN_VALIDATION n'est pas un etat final."""
        assert StatutDevis.EN_VALIDATION.est_final is False

    # est_modifiable
    def test_brouillon_est_modifiable(self):
        """Test: BROUILLON est modifiable."""
        assert StatutDevis.BROUILLON.est_modifiable is True

    def test_en_negociation_est_modifiable(self):
        """Test: EN_NEGOCIATION est modifiable."""
        assert StatutDevis.EN_NEGOCIATION.est_modifiable is True

    def test_en_validation_non_modifiable(self):
        """Test: EN_VALIDATION n'est pas modifiable."""
        assert StatutDevis.EN_VALIDATION.est_modifiable is False

    def test_envoye_non_modifiable(self):
        """Test: ENVOYE n'est pas modifiable."""
        assert StatutDevis.ENVOYE.est_modifiable is False

    def test_accepte_non_modifiable(self):
        """Test: ACCEPTE n'est pas modifiable."""
        assert StatutDevis.ACCEPTE.est_modifiable is False

    # est_actif
    def test_brouillon_est_actif(self):
        """Test: BROUILLON est actif."""
        assert StatutDevis.BROUILLON.est_actif is True

    def test_accepte_est_actif(self):
        """Test: ACCEPTE est actif (dans le pipeline)."""
        assert StatutDevis.ACCEPTE.est_actif is True

    def test_refuse_non_actif(self):
        """Test: REFUSE n'est pas actif."""
        assert StatutDevis.REFUSE.est_actif is False

    def test_perdu_non_actif(self):
        """Test: PERDU n'est pas actif."""
        assert StatutDevis.PERDU.est_actif is False

    def test_expire_non_actif(self):
        """Test: EXPIRE n'est pas actif."""
        assert StatutDevis.EXPIRE.est_actif is False

    def test_envoye_est_actif(self):
        """Test: ENVOYE est actif."""
        assert StatutDevis.ENVOYE.est_actif is True


class TestStatutDevisInitial:
    """Tests pour le statut initial."""

    def test_initial_est_brouillon(self):
        """Test: statut initial est BROUILLON."""
        assert StatutDevis.initial() == StatutDevis.BROUILLON


class TestStatutDevisTransitions:
    """Tests pour la state machine de transitions."""

    # Transitions depuis BROUILLON
    def test_brouillon_vers_en_validation(self):
        """Test: BROUILLON -> EN_VALIDATION autorise."""
        assert StatutDevis.BROUILLON.peut_transitionner_vers(StatutDevis.EN_VALIDATION)

    def test_brouillon_vers_envoye_interdit(self):
        """Test: BROUILLON -> ENVOYE interdit."""
        assert not StatutDevis.BROUILLON.peut_transitionner_vers(StatutDevis.ENVOYE)

    def test_brouillon_vers_accepte_interdit(self):
        """Test: BROUILLON -> ACCEPTE interdit."""
        assert not StatutDevis.BROUILLON.peut_transitionner_vers(StatutDevis.ACCEPTE)

    def test_brouillon_transitions_possibles(self):
        """Test: transitions possibles depuis BROUILLON."""
        assert StatutDevis.BROUILLON.transitions_possibles() == {StatutDevis.EN_VALIDATION}

    # Transitions depuis EN_VALIDATION
    def test_en_validation_vers_brouillon(self):
        """Test: EN_VALIDATION -> BROUILLON autorise."""
        assert StatutDevis.EN_VALIDATION.peut_transitionner_vers(StatutDevis.BROUILLON)

    def test_en_validation_vers_envoye(self):
        """Test: EN_VALIDATION -> ENVOYE autorise."""
        assert StatutDevis.EN_VALIDATION.peut_transitionner_vers(StatutDevis.ENVOYE)

    def test_en_validation_vers_accepte_interdit(self):
        """Test: EN_VALIDATION -> ACCEPTE interdit."""
        assert not StatutDevis.EN_VALIDATION.peut_transitionner_vers(StatutDevis.ACCEPTE)

    def test_en_validation_transitions_possibles(self):
        """Test: transitions possibles depuis EN_VALIDATION."""
        assert StatutDevis.EN_VALIDATION.transitions_possibles() == {
            StatutDevis.BROUILLON, StatutDevis.ENVOYE
        }

    # Transitions depuis ENVOYE
    def test_envoye_vers_vu(self):
        """Test: ENVOYE -> VU autorise."""
        assert StatutDevis.ENVOYE.peut_transitionner_vers(StatutDevis.VU)

    def test_envoye_vers_en_negociation(self):
        """Test: ENVOYE -> EN_NEGOCIATION autorise."""
        assert StatutDevis.ENVOYE.peut_transitionner_vers(StatutDevis.EN_NEGOCIATION)

    def test_envoye_vers_accepte(self):
        """Test: ENVOYE -> ACCEPTE autorise."""
        assert StatutDevis.ENVOYE.peut_transitionner_vers(StatutDevis.ACCEPTE)

    def test_envoye_vers_refuse(self):
        """Test: ENVOYE -> REFUSE autorise."""
        assert StatutDevis.ENVOYE.peut_transitionner_vers(StatutDevis.REFUSE)

    def test_envoye_vers_expire(self):
        """Test: ENVOYE -> EXPIRE autorise."""
        assert StatutDevis.ENVOYE.peut_transitionner_vers(StatutDevis.EXPIRE)

    def test_envoye_vers_brouillon_interdit(self):
        """Test: ENVOYE -> BROUILLON interdit."""
        assert not StatutDevis.ENVOYE.peut_transitionner_vers(StatutDevis.BROUILLON)

    def test_envoye_transitions_possibles(self):
        """Test: transitions possibles depuis ENVOYE."""
        assert StatutDevis.ENVOYE.transitions_possibles() == {
            StatutDevis.VU, StatutDevis.EN_NEGOCIATION,
            StatutDevis.ACCEPTE, StatutDevis.REFUSE, StatutDevis.EXPIRE,
        }

    # Transitions depuis VU
    def test_vu_vers_en_negociation(self):
        """Test: VU -> EN_NEGOCIATION autorise."""
        assert StatutDevis.VU.peut_transitionner_vers(StatutDevis.EN_NEGOCIATION)

    def test_vu_vers_accepte(self):
        """Test: VU -> ACCEPTE autorise."""
        assert StatutDevis.VU.peut_transitionner_vers(StatutDevis.ACCEPTE)

    def test_vu_vers_refuse(self):
        """Test: VU -> REFUSE autorise."""
        assert StatutDevis.VU.peut_transitionner_vers(StatutDevis.REFUSE)

    def test_vu_vers_expire(self):
        """Test: VU -> EXPIRE autorise."""
        assert StatutDevis.VU.peut_transitionner_vers(StatutDevis.EXPIRE)

    def test_vu_transitions_possibles(self):
        """Test: transitions possibles depuis VU."""
        assert StatutDevis.VU.transitions_possibles() == {
            StatutDevis.EN_NEGOCIATION, StatutDevis.ACCEPTE,
            StatutDevis.REFUSE, StatutDevis.EXPIRE,
        }

    # Transitions depuis EN_NEGOCIATION
    def test_en_negociation_vers_envoye(self):
        """Test: EN_NEGOCIATION -> ENVOYE autorise (nouvelle version)."""
        assert StatutDevis.EN_NEGOCIATION.peut_transitionner_vers(StatutDevis.ENVOYE)

    def test_en_negociation_vers_accepte(self):
        """Test: EN_NEGOCIATION -> ACCEPTE autorise."""
        assert StatutDevis.EN_NEGOCIATION.peut_transitionner_vers(StatutDevis.ACCEPTE)

    def test_en_negociation_vers_refuse(self):
        """Test: EN_NEGOCIATION -> REFUSE autorise."""
        assert StatutDevis.EN_NEGOCIATION.peut_transitionner_vers(StatutDevis.REFUSE)

    def test_en_negociation_vers_perdu(self):
        """Test: EN_NEGOCIATION -> PERDU autorise."""
        assert StatutDevis.EN_NEGOCIATION.peut_transitionner_vers(StatutDevis.PERDU)

    def test_en_negociation_transitions_possibles(self):
        """Test: transitions possibles depuis EN_NEGOCIATION."""
        assert StatutDevis.EN_NEGOCIATION.transitions_possibles() == {
            StatutDevis.ENVOYE, StatutDevis.ACCEPTE,
            StatutDevis.REFUSE, StatutDevis.PERDU,
        }

    # Statuts terminaux
    def test_accepte_aucune_transition(self):
        """Test: ACCEPTE ne peut transitionner vers aucun statut."""
        assert len(StatutDevis.ACCEPTE.transitions_possibles()) == 0

    def test_refuse_aucune_transition(self):
        """Test: REFUSE ne peut transitionner vers aucun statut."""
        assert len(StatutDevis.REFUSE.transitions_possibles()) == 0

    def test_perdu_aucune_transition(self):
        """Test: PERDU ne peut transitionner vers aucun statut."""
        assert len(StatutDevis.PERDU.transitions_possibles()) == 0

    # Transitions depuis EXPIRE
    def test_expire_vers_en_negociation(self):
        """Test: EXPIRE -> EN_NEGOCIATION autorise."""
        assert StatutDevis.EXPIRE.peut_transitionner_vers(StatutDevis.EN_NEGOCIATION)

    def test_expire_transitions_possibles(self):
        """Test: transitions possibles depuis EXPIRE."""
        assert StatutDevis.EXPIRE.transitions_possibles() == {StatutDevis.EN_NEGOCIATION}

    # Transitions invalides supplementaires
    def test_accepte_vers_brouillon_interdit(self):
        """Test: ACCEPTE -> BROUILLON interdit."""
        assert not StatutDevis.ACCEPTE.peut_transitionner_vers(StatutDevis.BROUILLON)

    def test_refuse_vers_envoye_interdit(self):
        """Test: REFUSE -> ENVOYE interdit."""
        assert not StatutDevis.REFUSE.peut_transitionner_vers(StatutDevis.ENVOYE)

    def test_perdu_vers_en_negociation_interdit(self):
        """Test: PERDU -> EN_NEGOCIATION interdit."""
        assert not StatutDevis.PERDU.peut_transitionner_vers(StatutDevis.EN_NEGOCIATION)
