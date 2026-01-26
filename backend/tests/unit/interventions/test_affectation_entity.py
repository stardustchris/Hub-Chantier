"""Tests unitaires pour l'entité AffectationIntervention."""

import pytest
from datetime import datetime

from modules.interventions.domain.entities.affectation_intervention import (
    AffectationIntervention,
)


class TestAffectationInterventionCreation:
    """Tests pour la création d'AffectationIntervention."""

    def test_create_minimal(self):
        """Test création avec champs minimum."""
        affectation = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
        )

        assert affectation.intervention_id == 1
        assert affectation.utilisateur_id == 5
        assert affectation.created_by == 10
        assert affectation.id is None
        assert affectation.est_principal is False
        assert affectation.commentaire is None

    def test_create_full(self):
        """Test création avec tous les champs."""
        affectation = AffectationIntervention(
            id=1,
            intervention_id=2,
            utilisateur_id=5,
            created_by=10,
            est_principal=True,
            commentaire="Technicien spécialisé",
        )

        assert affectation.id == 1
        assert affectation.est_principal is True
        assert affectation.commentaire == "Technicien spécialisé"

    def test_invalid_intervention_id_raises(self):
        """Test erreur si intervention_id <= 0."""
        with pytest.raises(ValueError, match="L'ID de l'intervention doit etre positif"):
            AffectationIntervention(
                intervention_id=0,
                utilisateur_id=5,
                created_by=10,
            )

    def test_invalid_utilisateur_id_raises(self):
        """Test erreur si utilisateur_id <= 0."""
        with pytest.raises(ValueError, match="L'ID de l'utilisateur doit etre positif"):
            AffectationIntervention(
                intervention_id=1,
                utilisateur_id=-1,
                created_by=10,
            )

    def test_invalid_created_by_raises(self):
        """Test erreur si created_by <= 0."""
        with pytest.raises(ValueError, match="L'ID du createur doit etre positif"):
            AffectationIntervention(
                intervention_id=1,
                utilisateur_id=5,
                created_by=0,
            )

    def test_commentaire_normalization(self):
        """Test normalisation du commentaire."""
        affectation = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
            commentaire="  Commentaire avec espaces  ",
        )

        assert affectation.commentaire == "Commentaire avec espaces"

    def test_empty_commentaire_becomes_none(self):
        """Test commentaire vide devient None."""
        affectation = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
            commentaire="   ",
        )

        assert affectation.commentaire is None


class TestAffectationInterventionMethods:
    """Tests pour les méthodes d'AffectationIntervention."""

    def test_est_supprimee_false(self):
        """Test est_supprimee sans suppression."""
        affectation = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
        )

        assert affectation.est_supprimee is False

    def test_definir_principal(self):
        """Test définir comme principal."""
        affectation = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
        )

        affectation.definir_principal()

        assert affectation.est_principal is True

    def test_retirer_principal(self):
        """Test retirer statut principal."""
        affectation = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
            est_principal=True,
        )

        affectation.retirer_principal()

        assert affectation.est_principal is False

    def test_ajouter_commentaire(self):
        """Test ajout de commentaire."""
        affectation = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
        )

        affectation.ajouter_commentaire("Nouveau commentaire")

        assert affectation.commentaire == "Nouveau commentaire"

    def test_ajouter_commentaire_empty(self):
        """Test ajout commentaire vide devient None."""
        affectation = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
            commentaire="Existant",
        )

        affectation.ajouter_commentaire("   ")

        assert affectation.commentaire is None

    def test_supprimer(self):
        """Test suppression (soft delete)."""
        affectation = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
        )

        affectation.supprimer(deleted_by=20)

        assert affectation.est_supprimee is True
        assert affectation.deleted_by == 20
        assert affectation.deleted_at is not None


class TestAffectationInterventionEquality:
    """Tests pour l'égalité et le hash."""

    def test_equality_same_id(self):
        """Test égalité avec même ID."""
        aff1 = AffectationIntervention(
            id=1,
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
        )
        aff2 = AffectationIntervention(
            id=1,
            intervention_id=2,  # Différent
            utilisateur_id=6,   # Différent
            created_by=11,      # Différent
        )

        assert aff1 == aff2

    def test_equality_different_id(self):
        """Test inégalité avec ID différents."""
        aff1 = AffectationIntervention(
            id=1,
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
        )
        aff2 = AffectationIntervention(
            id=2,
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
        )

        assert aff1 != aff2

    def test_equality_none_id(self):
        """Test inégalité avec ID None."""
        aff1 = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
        )
        aff2 = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
        )

        assert aff1 != aff2

    def test_equality_with_non_affectation(self):
        """Test inégalité avec non-AffectationIntervention."""
        affectation = AffectationIntervention(
            id=1,
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
        )

        assert affectation != "not an affectation"

    def test_hash_with_id(self):
        """Test hash avec ID."""
        affectation = AffectationIntervention(
            id=42,
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
        )

        assert hash(affectation) == hash(42)

    def test_str_principal(self):
        """Test représentation textuelle (principal)."""
        affectation = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
            est_principal=True,
        )

        result = str(affectation)
        assert "principal" in result
        assert "User 5" in result
        assert "INT 1" in result

    def test_str_secondaire(self):
        """Test représentation textuelle (secondaire)."""
        affectation = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=5,
            created_by=10,
            est_principal=False,
        )

        result = str(affectation)
        assert "secondaire" in result

    def test_repr(self):
        """Test représentation technique."""
        affectation = AffectationIntervention(
            id=1,
            intervention_id=2,
            utilisateur_id=5,
            created_by=10,
            est_principal=True,
        )

        result = repr(affectation)
        assert "AffectationIntervention" in result
        assert "id=1" in result
        assert "intervention_id=2" in result
        assert "utilisateur_id=5" in result
        assert "est_principal=True" in result
