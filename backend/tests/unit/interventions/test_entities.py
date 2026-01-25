"""Tests unitaires pour les Entities du module Interventions."""

import pytest
from datetime import date, time, datetime

from modules.interventions.domain.entities import (
    Intervention,
    TransitionStatutInvalideError,
    AffectationIntervention,
    InterventionMessage,
    TypeMessage,
    SignatureIntervention,
    TypeSignataire,
)
from modules.interventions.domain.value_objects import (
    StatutIntervention,
    PrioriteIntervention,
    TypeIntervention,
)


class TestIntervention:
    """Tests pour l'entite Intervention."""

    def test_creation_intervention_valide(self):
        """Verifie la creation d'une intervention valide."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )

        assert intervention.id is None
        assert intervention.type_intervention == TypeIntervention.SAV
        assert intervention.client_nom == "Client Test"
        assert intervention.client_adresse == "123 Rue Test"
        assert intervention.description == "Description test"
        assert intervention.statut == StatutIntervention.A_PLANIFIER
        assert intervention.priorite == PrioriteIntervention.NORMALE

    def test_creation_intervention_client_nom_vide(self):
        """Verifie qu'une erreur est levee si le nom client est vide."""
        with pytest.raises(ValueError, match="nom du client"):
            Intervention(
                type_intervention=TypeIntervention.SAV,
                client_nom="",
                client_adresse="123 Rue Test",
                description="Description test",
                created_by=1,
            )

    def test_creation_intervention_adresse_vide(self):
        """Verifie qu'une erreur est levee si l'adresse est vide."""
        with pytest.raises(ValueError, match="adresse"):
            Intervention(
                type_intervention=TypeIntervention.SAV,
                client_nom="Client Test",
                client_adresse="   ",
                description="Description test",
                created_by=1,
            )

    def test_creation_intervention_description_vide(self):
        """Verifie qu'une erreur est levee si la description est vide."""
        with pytest.raises(ValueError, match="description"):
            Intervention(
                type_intervention=TypeIntervention.SAV,
                client_nom="Client Test",
                client_adresse="123 Rue Test",
                description="",
                created_by=1,
            )

    def test_creation_intervention_created_by_invalide(self):
        """Verifie qu'une erreur est levee si created_by est invalide."""
        with pytest.raises(ValueError, match="createur"):
            Intervention(
                type_intervention=TypeIntervention.SAV,
                client_nom="Client Test",
                client_adresse="123 Rue Test",
                description="Description test",
                created_by=0,
            )

    def test_planifier_intervention(self):
        """Verifie la planification d'une intervention."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )

        date_planifiee = date(2026, 2, 15)
        heure_debut = time(9, 0)
        heure_fin = time(12, 0)

        intervention.planifier(date_planifiee, heure_debut, heure_fin)

        assert intervention.date_planifiee == date_planifiee
        assert intervention.heure_debut == heure_debut
        assert intervention.heure_fin == heure_fin
        assert intervention.statut == StatutIntervention.PLANIFIEE

    def test_planifier_intervention_horaires_invalides(self):
        """Verifie qu'une erreur est levee si les horaires sont invalides."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )

        with pytest.raises(ValueError, match="heure de fin"):
            intervention.planifier(
                date(2026, 2, 15),
                time(14, 0),  # Debut apres fin
                time(10, 0),
            )

    def test_demarrer_intervention(self):
        """Verifie le demarrage d'une intervention."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            statut=StatutIntervention.PLANIFIEE,
        )

        intervention.demarrer(time(9, 15))

        assert intervention.statut == StatutIntervention.EN_COURS
        assert intervention.heure_debut_reelle == time(9, 15)

    def test_demarrer_intervention_invalide(self):
        """Verifie qu'on ne peut pas demarrer depuis A_PLANIFIER."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            statut=StatutIntervention.A_PLANIFIER,
        )

        with pytest.raises(TransitionStatutInvalideError):
            intervention.demarrer()

    def test_terminer_intervention(self):
        """Verifie la fin d'une intervention."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            statut=StatutIntervention.EN_COURS,
        )

        intervention.terminer(
            heure_fin_reelle=time(11, 30),
            travaux_realises="Reparation effectuee",
            anomalies="RAS",
        )

        assert intervention.statut == StatutIntervention.TERMINEE
        assert intervention.heure_fin_reelle == time(11, 30)
        assert intervention.travaux_realises == "Reparation effectuee"
        assert intervention.anomalies == "RAS"

    def test_terminer_intervention_invalide(self):
        """Verifie qu'on ne peut pas terminer depuis A_PLANIFIER."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            statut=StatutIntervention.A_PLANIFIER,
        )

        with pytest.raises(TransitionStatutInvalideError):
            intervention.terminer()

    def test_annuler_intervention(self):
        """Verifie l'annulation d'une intervention."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            statut=StatutIntervention.PLANIFIEE,
        )

        intervention.annuler()

        assert intervention.statut == StatutIntervention.ANNULEE

    def test_annuler_intervention_terminee(self):
        """Verifie qu'on ne peut pas annuler une intervention terminee."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            statut=StatutIntervention.TERMINEE,
        )

        with pytest.raises(TransitionStatutInvalideError):
            intervention.annuler()

    def test_modifier_priorite(self):
        """Verifie la modification de priorite."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )

        intervention.modifier_priorite(PrioriteIntervention.URGENTE)

        assert intervention.priorite == PrioriteIntervention.URGENTE

    def test_modifier_client(self):
        """Verifie la modification des informations client."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )

        intervention.modifier_client(
            nom="Nouveau Client",
            adresse="456 Nouvelle Rue",
            telephone="0123456789",
            email="client@test.com",
        )

        assert intervention.client_nom == "Nouveau Client"
        assert intervention.client_adresse == "456 Nouvelle Rue"
        assert intervention.client_telephone == "0123456789"
        assert intervention.client_email == "client@test.com"

    def test_duree_prevue_minutes(self):
        """Verifie le calcul de la duree prevue."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            heure_debut=time(9, 0),
            heure_fin=time(12, 0),
        )

        assert intervention.duree_prevue_minutes == 180  # 3 heures

    def test_duree_prevue_minutes_sans_horaires(self):
        """Verifie que None est retourne si pas d'horaires."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )

        assert intervention.duree_prevue_minutes is None

    def test_est_planifiee(self):
        """Verifie la propriete est_planifiee."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )

        assert intervention.est_planifiee is False

        intervention.date_planifiee = date(2026, 2, 15)
        assert intervention.est_planifiee is True

    def test_soft_delete(self):
        """Verifie le soft delete."""
        intervention = Intervention(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )

        assert intervention.est_supprimee is False

        intervention.supprimer(deleted_by=1)

        assert intervention.est_supprimee is True
        assert intervention.deleted_at is not None
        assert intervention.deleted_by == 1


class TestAffectationIntervention:
    """Tests pour l'entite AffectationIntervention."""

    def test_creation_affectation_valide(self):
        """Verifie la creation d'une affectation valide."""
        affectation = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=2,
            created_by=3,
        )

        assert affectation.intervention_id == 1
        assert affectation.utilisateur_id == 2
        assert affectation.est_principal is False

    def test_creation_affectation_principale(self):
        """Verifie la creation d'une affectation principale."""
        affectation = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=2,
            created_by=3,
            est_principal=True,
        )

        assert affectation.est_principal is True

    def test_creation_affectation_intervention_invalide(self):
        """Verifie qu'une erreur est levee si intervention_id est invalide."""
        with pytest.raises(ValueError, match="intervention"):
            AffectationIntervention(
                intervention_id=0,
                utilisateur_id=2,
                created_by=3,
            )

    def test_definir_principal(self):
        """Verifie la definition comme principal."""
        affectation = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=2,
            created_by=3,
        )

        affectation.definir_principal()

        assert affectation.est_principal is True

    def test_retirer_principal(self):
        """Verifie le retrait du statut principal."""
        affectation = AffectationIntervention(
            intervention_id=1,
            utilisateur_id=2,
            created_by=3,
            est_principal=True,
        )

        affectation.retirer_principal()

        assert affectation.est_principal is False


class TestInterventionMessage:
    """Tests pour l'entite InterventionMessage."""

    def test_creation_commentaire(self):
        """Verifie la creation d'un commentaire."""
        message = InterventionMessage.creer_commentaire(
            intervention_id=1,
            auteur_id=2,
            contenu="Ceci est un commentaire",
        )

        assert message.type_message == TypeMessage.COMMENTAIRE
        assert message.contenu == "Ceci est un commentaire"
        assert message.inclure_rapport is True

    def test_creation_photo(self):
        """Verifie la creation d'un message photo."""
        message = InterventionMessage.creer_photo(
            intervention_id=1,
            auteur_id=2,
            description="Photo avant travaux",
            photos_urls=["https://example.com/photo1.jpg"],
        )

        assert message.type_message == TypeMessage.PHOTO
        assert message.a_photos is True
        assert len(message.photos_urls) == 1

    def test_creation_action(self):
        """Verifie la creation d'un message action."""
        message = InterventionMessage.creer_action(
            intervention_id=1,
            auteur_id=2,
            action="Intervention demarree",
        )

        assert message.type_message == TypeMessage.ACTION
        assert message.inclure_rapport is False

    def test_creation_systeme(self):
        """Verifie la creation d'un message systeme."""
        message = InterventionMessage.creer_systeme(
            intervention_id=1,
            message="Statut change vers EN_COURS",
        )

        assert message.type_message == TypeMessage.SYSTEME
        assert message.auteur_id == 0
        assert message.inclure_rapport is False

    def test_toggle_rapport_inclusion(self):
        """Verifie le toggle d'inclusion dans le rapport."""
        message = InterventionMessage.creer_commentaire(
            intervention_id=1,
            auteur_id=2,
            contenu="Test",
        )

        assert message.inclure_rapport is True

        message.exclure_du_rapport()
        assert message.inclure_rapport is False

        message.inclure_dans_rapport()
        assert message.inclure_rapport is True


class TestSignatureIntervention:
    """Tests pour l'entite SignatureIntervention."""

    def test_creation_signature_client(self):
        """Verifie la creation d'une signature client."""
        signature = SignatureIntervention.creer_signature_client(
            intervention_id=1,
            nom_client="M. Dupont",
            signature_data="data:image/png;base64,iVBORw0...",
        )

        assert signature.type_signataire == TypeSignataire.CLIENT
        assert signature.nom_signataire == "M. Dupont"
        assert signature.utilisateur_id is None
        assert signature.est_signature_client is True

    def test_creation_signature_technicien(self):
        """Verifie la creation d'une signature technicien."""
        signature = SignatureIntervention.creer_signature_technicien(
            intervention_id=1,
            utilisateur_id=5,
            nom_technicien="Jean Martin",
            signature_data="data:image/png;base64,iVBORw0...",
        )

        assert signature.type_signataire == TypeSignataire.TECHNICIEN
        assert signature.nom_signataire == "Jean Martin"
        assert signature.utilisateur_id == 5
        assert signature.est_signature_technicien is True

    def test_creation_signature_technicien_sans_user_id(self):
        """Verifie qu'une erreur est levee si user_id manquant pour technicien."""
        with pytest.raises(ValueError, match="utilisateur"):
            SignatureIntervention(
                intervention_id=1,
                type_signataire=TypeSignataire.TECHNICIEN,
                nom_signataire="Jean Martin",
                signature_data="data:image/png;base64,iVBORw0...",
            )

    def test_horodatage_str(self):
        """Verifie le format de l'horodatage."""
        signature = SignatureIntervention.creer_signature_client(
            intervention_id=1,
            nom_client="M. Dupont",
            signature_data="data:image/png;base64,iVBORw0...",
        )

        # Le format doit etre "DD/MM/YYYY a HH:MM"
        assert " a " in signature.horodatage_str
        assert "/" in signature.horodatage_str

    def test_geolocalisation(self):
        """Verifie la geolocalisation."""
        signature = SignatureIntervention.creer_signature_client(
            intervention_id=1,
            nom_client="M. Dupont",
            signature_data="data:image/png;base64,iVBORw0...",
            latitude=48.8566,
            longitude=2.3522,
        )

        assert signature.a_geolocalisation is True
        assert signature.latitude == 48.8566
        assert signature.longitude == 2.3522
