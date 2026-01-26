"""Tests unitaires supplémentaires pour les Entities Interventions."""

import pytest
from datetime import date, time, datetime

from modules.interventions.domain.entities import (
    Intervention,
    TransitionStatutInvalideError,
    InterventionMessage,
    TypeMessage,
    SignatureIntervention,
    TypeSignataire,
    AffectationIntervention,
)
from modules.interventions.domain.value_objects import (
    StatutIntervention,
    PrioriteIntervention,
    TypeIntervention,
)


class TestInterventionAdditional:
    """Tests supplémentaires pour l'entité Intervention."""

    def test_creation_intervention_with_horaires_invalides(self):
        """Test création avec horaires invalides lève erreur."""
        with pytest.raises(ValueError, match="heure de fin"):
            Intervention(
                type_intervention=TypeIntervention.SAV,
                client_nom="Client Test",
                client_adresse="123 Rue Test",
                description="Description test",
                created_by=1,
                heure_debut=time(14, 0),
                heure_fin=time(10, 0),
            )

    def test_est_terminee(self):
        """Test propriété est_terminee."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            statut=StatutIntervention.TERMINEE,
        )

        assert intervention.est_terminee is True

    def test_est_annulee(self):
        """Test propriété est_annulee."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            statut=StatutIntervention.ANNULEE,
        )

        assert intervention.est_annulee is True

    def test_est_active(self):
        """Test propriété est_active."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            statut=StatutIntervention.EN_COURS,
        )

        assert intervention.est_active is True

    def test_est_active_false_when_deleted(self):
        """Test est_active False si supprimée."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            statut=StatutIntervention.EN_COURS,
        )
        intervention.supprimer(deleted_by=1)

        assert intervention.est_active is False

    def test_duree_reelle_minutes(self):
        """Test calcul durée réelle."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            heure_debut_reelle=time(9, 0),
            heure_fin_reelle=time(11, 30),
        )

        assert intervention.duree_reelle_minutes == 150

    def test_duree_reelle_minutes_sans_horaires(self):
        """Test durée réelle None si pas d'horaires."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )

        assert intervention.duree_reelle_minutes is None

    def test_horaires_str(self):
        """Test format horaires string."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            heure_debut=time(9, 0),
            heure_fin=time(12, 0),
        )

        assert intervention.horaires_str == "09:00 - 12:00"

    def test_horaires_str_sans_horaires(self):
        """Test horaires_str None si pas d'horaires."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )

        assert intervention.horaires_str is None

    def test_demarrer_sans_heure(self):
        """Test démarrage sans heure utilise heure courante."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            statut=StatutIntervention.PLANIFIEE,
        )

        intervention.demarrer()

        assert intervention.heure_debut_reelle is not None

    def test_terminer_sans_heure(self):
        """Test terminer sans heure utilise heure courante."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            statut=StatutIntervention.EN_COURS,
        )

        intervention.terminer()

        assert intervention.heure_fin_reelle is not None

    def test_marquer_rapport_genere(self):
        """Test marquer rapport généré."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )

        intervention.marquer_rapport_genere("https://example.com/rapport.pdf")

        assert intervention.rapport_genere is True
        assert intervention.rapport_url == "https://example.com/rapport.pdf"

    def test_modifier_description_vide(self):
        """Test modifier description vide lève erreur."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )

        with pytest.raises(ValueError, match="description"):
            intervention.modifier_description("")

    def test_modifier_client_nom_vide(self):
        """Test modifier client nom vide lève erreur."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )

        with pytest.raises(ValueError, match="nom du client"):
            intervention.modifier_client(nom="")

    def test_modifier_client_adresse_vide(self):
        """Test modifier client adresse vide lève erreur."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )

        with pytest.raises(ValueError, match="adresse"):
            intervention.modifier_client(adresse="   ")

    def test_modifier_client_telephone_vide(self):
        """Test modifier client téléphone vide devient None."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            client_telephone="0123456789",
        )

        intervention.modifier_client(telephone="   ")

        assert intervention.client_telephone is None

    def test_equality_same_id(self):
        """Test égalité même ID."""
        i1 = Intervention(
            id=1,
            type_intervention=TypeIntervention.SAV,
            client_nom="Client A",
            client_adresse="Adresse A",
            description="Desc A",
            created_by=1,
        )
        i2 = Intervention(
            id=1,
            type_intervention=TypeIntervention.MAINTENANCE,
            client_nom="Client B",
            client_adresse="Adresse B",
            description="Desc B",
            created_by=2,
        )

        assert i1 == i2

    def test_equality_different_id(self):
        """Test inégalité IDs différents."""
        i1 = Intervention(
            id=1,
            type_intervention=TypeIntervention.SAV,
            client_nom="Client",
            client_adresse="Adresse",
            description="Desc",
            created_by=1,
        )
        i2 = Intervention(
            id=2,
            type_intervention=TypeIntervention.SAV,
            client_nom="Client",
            client_adresse="Adresse",
            description="Desc",
            created_by=1,
        )

        assert i1 != i2

    def test_equality_none_id(self):
        """Test inégalité si un ID est None."""
        i1 = Intervention(
            id=1,
            type_intervention=TypeIntervention.SAV,
            client_nom="Client",
            client_adresse="Adresse",
            description="Desc",
            created_by=1,
        )
        i2 = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client",
            client_adresse="Adresse",
            description="Desc",
            created_by=1,
        )

        assert i1 != i2

    def test_equality_not_intervention(self):
        """Test inégalité avec autre type."""
        i = Intervention(
            id=1,
            type_intervention=TypeIntervention.SAV,
            client_nom="Client",
            client_adresse="Adresse",
            description="Desc",
            created_by=1,
        )

        assert i != "not an intervention"

    def test_hash_with_id(self):
        """Test hash avec ID."""
        i = Intervention(
            id=42,
            type_intervention=TypeIntervention.SAV,
            client_nom="Client",
            client_adresse="Adresse",
            description="Desc",
            created_by=1,
        )

        assert hash(i) == hash(42)

    def test_hash_without_id(self):
        """Test hash sans ID."""
        i = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client",
            client_adresse="Adresse",
            description="Desc",
            created_by=1,
        )

        assert hash(i) is not None

    def test_str(self):
        """Test représentation string."""
        i = Intervention(
            code="INT-2026-0001",
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="Adresse",
            description="Desc",
            created_by=1,
        )

        assert "INT-2026-0001" in str(i)
        assert "SAV" in str(i)
        assert "Client Test" in str(i)

    def test_repr(self):
        """Test représentation technique."""
        i = Intervention(
            id=1,
            code="INT-2026-0001",
            type_intervention=TypeIntervention.SAV,
            client_nom="Client",
            client_adresse="Adresse",
            description="Desc",
            created_by=1,
        )

        assert "Intervention" in repr(i)
        assert "id=1" in repr(i)


class TestTransitionStatutInvalideError:
    """Tests pour TransitionStatutInvalideError."""

    def test_error_message(self):
        """Test message d'erreur."""
        error = TransitionStatutInvalideError(
            StatutIntervention.A_PLANIFIER,
            StatutIntervention.TERMINEE,
        )

        assert "Transition invalide" in str(error)
        assert error.statut_actuel == StatutIntervention.A_PLANIFIER
        assert error.statut_cible == StatutIntervention.TERMINEE


class TestInterventionMessageAdditional:
    """Tests supplémentaires pour InterventionMessage."""

    def test_creation_message_contenu_vide(self):
        """Test création message contenu vide lève erreur."""
        with pytest.raises(ValueError, match="contenu"):
            InterventionMessage.creer_commentaire(
                intervention_id=1,
                auteur_id=2,
                contenu="",
            )

    def test_creation_message_intervention_invalide(self):
        """Test création message intervention invalide."""
        with pytest.raises(ValueError, match="intervention"):
            InterventionMessage.creer_commentaire(
                intervention_id=0,
                auteur_id=2,
                contenu="Contenu",
            )

    def test_message_a_photos_false(self):
        """Test a_photos False si pas de photos."""
        message = InterventionMessage.creer_commentaire(
            intervention_id=1,
            auteur_id=2,
            contenu="Commentaire sans photo",
        )

        assert message.a_photos is False

    def test_message_est_supprime(self):
        """Test est_supprime."""
        message = InterventionMessage.creer_commentaire(
            intervention_id=1,
            auteur_id=2,
            contenu="Test",
        )

        assert message.est_supprime is False

        message.supprimer(deleted_by=1)

        assert message.est_supprime is True


class TestAffectationInterventionAdditional:
    """Tests supplémentaires pour AffectationIntervention."""

    def test_creation_affectation_utilisateur_invalide(self):
        """Test création affectation utilisateur invalide."""
        with pytest.raises(ValueError, match="utilisateur"):
            AffectationIntervention(
                intervention_id=1,
                utilisateur_id=0,
                created_by=3,
            )

    def test_affectation_est_supprimee(self):
        """Test est_supprimee."""
        affectation = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=2,
            created_by=3,
        )

        assert affectation.est_supprimee is False

        affectation.supprimer(deleted_by=3)

        assert affectation.est_supprimee is True

    def test_affectation_equality(self):
        """Test égalité affectations."""
        a1 = AffectationIntervention(
            id=1,
            intervention_id=1,
            utilisateur_id=2,
            created_by=3,
        )
        a2 = AffectationIntervention(
            id=1,
            intervention_id=5,
            utilisateur_id=6,
            created_by=7,
        )

        assert a1 == a2

    def test_affectation_hash(self):
        """Test hash affectation."""
        a = AffectationIntervention(
            id=42,
            intervention_id=1,
            utilisateur_id=2,
            created_by=3,
        )

        assert hash(a) == hash(42)


class TestSignatureInterventionAdditional:
    """Tests supplémentaires pour SignatureIntervention."""

    def test_creation_signature_intervention_invalide(self):
        """Test création signature intervention invalide."""
        with pytest.raises(ValueError, match="intervention"):
            SignatureIntervention(
                intervention_id=0,
                type_signataire=TypeSignataire.CLIENT,
                nom_signataire="Client",
                signature_data="data:...",
            )

    def test_creation_signature_nom_vide(self):
        """Test création signature nom vide."""
        with pytest.raises(ValueError, match="nom du signataire"):
            SignatureIntervention(
                intervention_id=1,
                type_signataire=TypeSignataire.CLIENT,
                nom_signataire="",
                signature_data="data:...",
            )

    def test_creation_signature_data_vide(self):
        """Test création signature data vide."""
        with pytest.raises(ValueError, match="donnees de signature"):
            SignatureIntervention(
                intervention_id=1,
                type_signataire=TypeSignataire.CLIENT,
                nom_signataire="Client",
                signature_data="",
            )

    def test_signature_est_supprimee(self):
        """Test est_supprimee."""
        signature = SignatureIntervention.creer_signature_client(
            intervention_id=1,
            nom_client="Client",
            signature_data="data:...",
        )

        assert signature.est_supprimee is False

        signature.supprimer(deleted_by=1)

        assert signature.est_supprimee is True

    def test_signature_a_geolocalisation_partielle(self):
        """Test a_geolocalisation False si partielle."""
        signature = SignatureIntervention.creer_signature_client(
            intervention_id=1,
            nom_client="Client",
            signature_data="data:...",
            latitude=48.8566,
        )

        assert signature.a_geolocalisation is False

    def test_signature_str(self):
        """Test représentation string."""
        signature = SignatureIntervention.creer_signature_client(
            intervention_id=1,
            nom_client="M. Dupont",
            signature_data="data:...",
        )

        assert "Client" in str(signature)
        assert "M. Dupont" in str(signature)

    def test_signature_repr(self):
        """Test représentation technique."""
        signature = SignatureIntervention(
            id=1,
            intervention_id=2,
            type_signataire=TypeSignataire.CLIENT,
            nom_signataire="Client",
            signature_data="data:...",
        )

        assert "SignatureIntervention" in repr(signature)
        assert "id=1" in repr(signature)


class TestTypeSignataire:
    """Tests pour TypeSignataire."""

    def test_type_signataire_label_client(self):
        """Test label client."""
        assert TypeSignataire.CLIENT.label == "Client"

    def test_type_signataire_label_technicien(self):
        """Test label technicien."""
        assert TypeSignataire.TECHNICIEN.label == "Technicien"
