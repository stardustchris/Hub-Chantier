"""Tests unitaires pour les events du module Interventions."""

import pytest
from datetime import datetime
from dataclasses import FrozenInstanceError

from modules.interventions.domain.events.intervention_events import (
    InterventionCreee,
    InterventionPlanifiee,
    InterventionDemarree,
    InterventionTerminee,
    InterventionAnnulee,
    TechnicienAffecte,
    TechnicienDesaffecte,
    SignatureAjoutee,
    RapportGenere,
    MessageAjoute,
)
from modules.interventions.domain.value_objects import (
    TypeIntervention,
    PrioriteIntervention,
)


class TestInterventionCreee:
    """Tests pour InterventionCreee."""

    def test_create_with_all_fields(self):
        """Test création avec tous les champs."""
        timestamp = datetime.utcnow()
        event = InterventionCreee(
            intervention_id=1,
            code="INT-2024-001",
            type_intervention=TypeIntervention.DEPANNAGE,
            priorite=PrioriteIntervention.HAUTE,
            client_nom="Client Test",
            created_by=5,
            timestamp=timestamp,
        )

        assert event.intervention_id == 1
        assert event.code == "INT-2024-001"
        assert event.type_intervention == TypeIntervention.DEPANNAGE
        assert event.priorite == PrioriteIntervention.HAUTE
        assert event.client_nom == "Client Test"
        assert event.created_by == 5
        assert event.timestamp == timestamp

    def test_create_with_default_timestamp(self):
        """Test création avec timestamp par défaut."""
        before = datetime.utcnow()
        event = InterventionCreee(
            intervention_id=1,
            code="INT-2024-001",
            type_intervention=TypeIntervention.MAINTENANCE,
            priorite=PrioriteIntervention.NORMALE,
            client_nom="Client",
            created_by=1,
        )
        after = datetime.utcnow()

        assert event.timestamp is not None
        assert before <= event.timestamp <= after

    def test_frozen_immutability(self):
        """Test que l'event est immutable."""
        event = InterventionCreee(
            intervention_id=1,
            code="INT-2024-001",
            type_intervention=TypeIntervention.DEPANNAGE,
            priorite=PrioriteIntervention.HAUTE,
            client_nom="Client",
            created_by=1,
        )

        with pytest.raises(FrozenInstanceError):
            event.intervention_id = 2


class TestInterventionPlanifiee:
    """Tests pour InterventionPlanifiee."""

    def test_create_with_all_fields(self):
        """Test création avec tous les champs."""
        event = InterventionPlanifiee(
            intervention_id=1,
            code="INT-2024-001",
            date_planifiee="2024-03-15",
            heure_debut="09:00",
            heure_fin="17:00",
            techniciens_ids=[1, 2, 3],
        )

        assert event.intervention_id == 1
        assert event.date_planifiee == "2024-03-15"
        assert event.heure_debut == "09:00"
        assert event.heure_fin == "17:00"
        assert event.techniciens_ids == [1, 2, 3]

    def test_create_with_default_timestamp(self):
        """Test timestamp par défaut."""
        event = InterventionPlanifiee(
            intervention_id=1,
            code="INT-2024-001",
            date_planifiee="2024-03-15",
            heure_debut=None,
            heure_fin=None,
            techniciens_ids=[1],
        )

        assert event.timestamp is not None


class TestInterventionDemarree:
    """Tests pour InterventionDemarree."""

    def test_create_event(self):
        """Test création de l'event."""
        event = InterventionDemarree(
            intervention_id=1,
            code="INT-2024-001",
            technicien_id=5,
            heure_debut_reelle="08:30",
        )

        assert event.intervention_id == 1
        assert event.technicien_id == 5
        assert event.heure_debut_reelle == "08:30"

    def test_create_with_default_timestamp(self):
        """Test timestamp par défaut."""
        event = InterventionDemarree(
            intervention_id=1,
            code="INT-2024-001",
            technicien_id=5,
            heure_debut_reelle="08:30",
        )

        assert event.timestamp is not None


class TestInterventionTerminee:
    """Tests pour InterventionTerminee."""

    def test_create_with_all_fields(self):
        """Test création avec tous les champs."""
        event = InterventionTerminee(
            intervention_id=1,
            code="INT-2024-001",
            heure_fin_reelle="17:30",
            travaux_realises="Remplacement de pièces",
            anomalies="Aucune",
        )

        assert event.heure_fin_reelle == "17:30"
        assert event.travaux_realises == "Remplacement de pièces"
        assert event.anomalies == "Aucune"

    def test_create_without_optional(self):
        """Test création sans champs optionnels."""
        event = InterventionTerminee(
            intervention_id=1,
            code="INT-2024-001",
            heure_fin_reelle="17:30",
            travaux_realises=None,
            anomalies=None,
        )

        assert event.travaux_realises is None
        assert event.anomalies is None

    def test_create_with_default_timestamp(self):
        """Test timestamp par défaut."""
        event = InterventionTerminee(
            intervention_id=1,
            code="INT-2024-001",
            heure_fin_reelle="17:30",
            travaux_realises=None,
            anomalies=None,
        )

        assert event.timestamp is not None


class TestInterventionAnnulee:
    """Tests pour InterventionAnnulee."""

    def test_create_event(self):
        """Test création de l'event."""
        event = InterventionAnnulee(
            intervention_id=1,
            code="INT-2024-001",
            annule_par=10,
        )

        assert event.intervention_id == 1
        assert event.code == "INT-2024-001"
        assert event.annule_par == 10

    def test_create_with_default_timestamp(self):
        """Test timestamp par défaut."""
        event = InterventionAnnulee(
            intervention_id=1,
            code="INT-2024-001",
            annule_par=10,
        )

        assert event.timestamp is not None


class TestTechnicienAffecte:
    """Tests pour TechnicienAffecte."""

    def test_create_principal(self):
        """Test affectation principal."""
        event = TechnicienAffecte(
            intervention_id=1,
            utilisateur_id=5,
            est_principal=True,
            affecte_par=10,
        )

        assert event.utilisateur_id == 5
        assert event.est_principal is True
        assert event.affecte_par == 10

    def test_create_secondaire(self):
        """Test affectation secondaire."""
        event = TechnicienAffecte(
            intervention_id=1,
            utilisateur_id=6,
            est_principal=False,
            affecte_par=10,
        )

        assert event.est_principal is False

    def test_create_with_default_timestamp(self):
        """Test timestamp par défaut."""
        event = TechnicienAffecte(
            intervention_id=1,
            utilisateur_id=5,
            est_principal=True,
            affecte_par=10,
        )

        assert event.timestamp is not None


class TestTechnicienDesaffecte:
    """Tests pour TechnicienDesaffecte."""

    def test_create_event(self):
        """Test création de l'event."""
        event = TechnicienDesaffecte(
            intervention_id=1,
            utilisateur_id=5,
            desaffecte_par=10,
        )

        assert event.intervention_id == 1
        assert event.utilisateur_id == 5
        assert event.desaffecte_par == 10

    def test_create_with_default_timestamp(self):
        """Test timestamp par défaut."""
        event = TechnicienDesaffecte(
            intervention_id=1,
            utilisateur_id=5,
            desaffecte_par=10,
        )

        assert event.timestamp is not None


class TestSignatureAjoutee:
    """Tests pour SignatureAjoutee."""

    def test_create_client_signature(self):
        """Test signature client."""
        event = SignatureAjoutee(
            intervention_id=1,
            type_signataire="client",
            nom_signataire="Jean Dupont",
        )

        assert event.type_signataire == "client"
        assert event.nom_signataire == "Jean Dupont"

    def test_create_technicien_signature(self):
        """Test signature technicien."""
        event = SignatureAjoutee(
            intervention_id=1,
            type_signataire="technicien",
            nom_signataire="Marie Martin",
        )

        assert event.type_signataire == "technicien"

    def test_create_with_default_timestamp(self):
        """Test timestamp par défaut."""
        event = SignatureAjoutee(
            intervention_id=1,
            type_signataire="client",
            nom_signataire="Test",
        )

        assert event.timestamp is not None


class TestRapportGenere:
    """Tests pour RapportGenere."""

    def test_create_event(self):
        """Test création de l'event."""
        event = RapportGenere(
            intervention_id=1,
            code="INT-2024-001",
            rapport_url="https://storage.example.com/rapports/INT-2024-001.pdf",
            genere_par=5,
        )

        assert event.rapport_url == "https://storage.example.com/rapports/INT-2024-001.pdf"
        assert event.genere_par == 5

    def test_create_with_default_timestamp(self):
        """Test timestamp par défaut."""
        event = RapportGenere(
            intervention_id=1,
            code="INT-2024-001",
            rapport_url="url",
            genere_par=5,
        )

        assert event.timestamp is not None


class TestMessageAjoute:
    """Tests pour MessageAjoute."""

    def test_create_event(self):
        """Test création de l'event."""
        event = MessageAjoute(
            intervention_id=1,
            message_id=10,
            type_message="note",
            auteur_id=5,
        )

        assert event.message_id == 10
        assert event.type_message == "note"
        assert event.auteur_id == 5

    def test_create_with_default_timestamp(self):
        """Test timestamp par défaut."""
        event = MessageAjoute(
            intervention_id=1,
            message_id=10,
            type_message="note",
            auteur_id=5,
        )

        assert event.timestamp is not None
