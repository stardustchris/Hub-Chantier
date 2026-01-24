"""Tests unitaires pour les Entities du module Logistique."""

import pytest
from datetime import date, time, datetime

from modules.logistique.domain.entities import Ressource, Reservation
from modules.logistique.domain.entities.reservation import (
    TransitionStatutInvalideError,
)
from modules.logistique.domain.value_objects import (
    CategorieRessource,
    StatutReservation,
    PlageHoraire,
)


class TestRessource:
    """Tests pour l'entité Ressource."""

    def test_create_ressource_valid(self, sample_ressource: Ressource):
        """Test: création d'une ressource valide."""
        assert sample_ressource.id == 1
        assert sample_ressource.code == "GRU001"
        assert sample_ressource.nom == "Grue mobile 50T"
        assert sample_ressource.categorie == CategorieRessource.ENGIN_LEVAGE
        assert sample_ressource.validation_requise is True
        assert sample_ressource.actif is True

    def test_ressource_default_plage_horaire(self, sample_ressource: Ressource):
        """Test: plage horaire par défaut."""
        plage = sample_ressource.plage_horaire_defaut
        assert isinstance(plage, PlageHoraire)
        assert plage.heure_debut == time(7, 0)
        assert plage.heure_fin == time(18, 0)

    def test_ressource_desactiver(self, sample_ressource: Ressource):
        """Test: désactivation d'une ressource."""
        assert sample_ressource.actif is True
        sample_ressource.desactiver()
        assert sample_ressource.actif is False

    def test_ressource_activer(self, sample_ressource: Ressource):
        """Test: activation d'une ressource."""
        sample_ressource.actif = False
        sample_ressource.activer()
        assert sample_ressource.actif is True

    def test_ressource_modifier_plage_horaire(self, sample_ressource: Ressource):
        """Test: modification de la plage horaire par défaut."""
        nouvelle_plage = PlageHoraire(heure_debut=time(6, 0), heure_fin=time(20, 0))
        sample_ressource.modifier_plage_horaire(nouvelle_plage)
        assert sample_ressource.plage_horaire_defaut == nouvelle_plage

    def test_ressource_activer_validation(self, sample_ressource_no_validation: Ressource):
        """Test: activation de la validation N+1."""
        assert sample_ressource_no_validation.validation_requise is False
        sample_ressource_no_validation.activer_validation()
        assert sample_ressource_no_validation.validation_requise is True

    def test_ressource_desactiver_validation(self, sample_ressource: Ressource):
        """Test: désactivation de la validation N+1."""
        assert sample_ressource.validation_requise is True
        sample_ressource.desactiver_validation()
        assert sample_ressource.validation_requise is False

    def test_ressource_peut_etre_reservee(self, sample_ressource: Ressource):
        """Test: ressource active peut être réservée."""
        assert sample_ressource.peut_etre_reservee() is True
        sample_ressource.desactiver()
        assert sample_ressource.peut_etre_reservee() is False

    def test_ressource_label_complet(self, sample_ressource: Ressource):
        """Test: label complet de la ressource."""
        assert sample_ressource.label_complet == "[GRU001] Grue mobile 50T"

    def test_ressource_create_without_nom_raises_error(self):
        """Test: erreur si nom manquant."""
        with pytest.raises(ValueError) as exc_info:
            Ressource(code="TEST", nom="")
        assert "nom" in str(exc_info.value).lower()

    def test_ressource_create_without_code_raises_error(self):
        """Test: erreur si code manquant."""
        with pytest.raises(ValueError) as exc_info:
            Ressource(code="", nom="Test")
        assert "code" in str(exc_info.value).lower()


class TestReservation:
    """Tests pour l'entité Reservation."""

    def test_create_reservation_valid(self, sample_reservation: Reservation):
        """Test: création d'une réservation valide."""
        assert sample_reservation.id == 1
        assert sample_reservation.ressource_id == 1
        assert sample_reservation.chantier_id == 100
        assert sample_reservation.demandeur_id == 10
        assert sample_reservation.statut == StatutReservation.EN_ATTENTE

    def test_reservation_plage_horaire(self, sample_reservation: Reservation):
        """Test: accès à la plage horaire."""
        plage = sample_reservation.plage_horaire
        assert isinstance(plage, PlageHoraire)
        assert plage.heure_debut == time(9, 0)
        assert plage.heure_fin == time(12, 0)

    def test_reservation_valider(self, sample_reservation: Reservation):
        """Test: validation d'une réservation."""
        valideur_id = 5
        sample_reservation.valider(valideur_id)

        assert sample_reservation.statut == StatutReservation.VALIDEE
        assert sample_reservation.valideur_id == valideur_id
        assert sample_reservation.validated_at is not None

    def test_reservation_valider_depuis_mauvais_statut(
        self, validated_reservation: Reservation
    ):
        """Test: impossible de valider une réservation déjà validée."""
        with pytest.raises(TransitionStatutInvalideError):
            validated_reservation.valider(10)

    def test_reservation_refuser(self, sample_reservation: Reservation):
        """Test: refus d'une réservation."""
        valideur_id = 5
        motif = "Ressource en maintenance"
        sample_reservation.refuser(valideur_id, motif)

        assert sample_reservation.statut == StatutReservation.REFUSEE
        assert sample_reservation.valideur_id == valideur_id
        assert sample_reservation.motif_refus == motif
        assert sample_reservation.validated_at is not None

    def test_reservation_refuser_sans_motif(self, sample_reservation: Reservation):
        """Test: refus sans motif optionnel."""
        sample_reservation.refuser(5)
        assert sample_reservation.statut == StatutReservation.REFUSEE
        assert sample_reservation.motif_refus is None

    def test_reservation_refuser_depuis_mauvais_statut(
        self, validated_reservation: Reservation
    ):
        """Test: impossible de refuser une réservation validée."""
        with pytest.raises(TransitionStatutInvalideError):
            validated_reservation.refuser(10, "Trop tard")

    def test_reservation_annuler_en_attente(self, sample_reservation: Reservation):
        """Test: annulation d'une réservation en attente."""
        sample_reservation.annuler()
        assert sample_reservation.statut == StatutReservation.ANNULEE

    def test_reservation_annuler_validee(self, validated_reservation: Reservation):
        """Test: annulation d'une réservation validée."""
        validated_reservation.annuler()
        assert validated_reservation.statut == StatutReservation.ANNULEE

    def test_reservation_annuler_refusee_interdit(self, sample_reservation: Reservation):
        """Test: impossible d'annuler une réservation refusée."""
        sample_reservation.refuser(5)
        with pytest.raises(TransitionStatutInvalideError):
            sample_reservation.annuler()

    def test_reservation_est_en_attente(self, sample_reservation: Reservation):
        """Test: vérification du statut en attente."""
        assert sample_reservation.est_en_attente is True

    def test_reservation_est_validee(self, validated_reservation: Reservation):
        """Test: vérification du statut validé."""
        assert validated_reservation.est_validee is True
        assert validated_reservation.est_en_attente is False

    def test_reservation_chevauche_meme_ressource_meme_jour(
        self, sample_reservation: Reservation
    ):
        """Test: détection de chevauchement sur la même ressource."""
        autre_reservation = Reservation(
            id=99,
            ressource_id=sample_reservation.ressource_id,
            chantier_id=200,
            demandeur_id=20,
            date_reservation=sample_reservation.date_reservation,
            heure_debut=time(10, 0),  # Chevauche 9h-12h
            heure_fin=time(14, 0),
            statut=StatutReservation.VALIDEE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert sample_reservation.chevauche(autre_reservation) is True

    def test_reservation_pas_chevauche_ressource_differente(
        self, sample_reservation: Reservation
    ):
        """Test: pas de chevauchement sur ressource différente."""
        autre_reservation = Reservation(
            id=99,
            ressource_id=999,  # Ressource différente
            chantier_id=200,
            demandeur_id=20,
            date_reservation=sample_reservation.date_reservation,
            heure_debut=time(10, 0),
            heure_fin=time(14, 0),
            statut=StatutReservation.VALIDEE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert sample_reservation.chevauche(autre_reservation) is False

    def test_reservation_pas_chevauche_jour_different(
        self, sample_reservation: Reservation
    ):
        """Test: pas de chevauchement sur jour différent."""
        from datetime import timedelta
        autre_reservation = Reservation(
            id=99,
            ressource_id=sample_reservation.ressource_id,
            chantier_id=200,
            demandeur_id=20,
            date_reservation=sample_reservation.date_reservation + timedelta(days=1),
            heure_debut=time(9, 0),
            heure_fin=time(12, 0),
            statut=StatutReservation.VALIDEE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert sample_reservation.chevauche(autre_reservation) is False

    def test_reservation_pas_chevauche_plages_adjacentes(
        self, sample_reservation: Reservation
    ):
        """Test: pas de chevauchement pour plages adjacentes."""
        autre_reservation = Reservation(
            id=99,
            ressource_id=sample_reservation.ressource_id,
            chantier_id=200,
            demandeur_id=20,
            date_reservation=sample_reservation.date_reservation,
            heure_debut=time(12, 0),  # Commence quand l'autre finit
            heure_fin=time(15, 0),
            statut=StatutReservation.VALIDEE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert sample_reservation.chevauche(autre_reservation) is False

    def test_reservation_create_without_ressource_raises_error(self):
        """Test: erreur si ressource_id manquant."""
        with pytest.raises(ValueError):
            Reservation(
                ressource_id=0,
                chantier_id=100,
                demandeur_id=10,
                date_reservation=date.today(),
                heure_debut=time(9, 0),
                heure_fin=time(12, 0),
            )

    def test_reservation_create_without_chantier_raises_error(self):
        """Test: erreur si chantier_id manquant (LOG-08)."""
        with pytest.raises(ValueError):
            Reservation(
                ressource_id=1,
                chantier_id=0,
                demandeur_id=10,
                date_reservation=date.today(),
                heure_debut=time(9, 0),
                heure_fin=time(12, 0),
            )

    def test_reservation_create_heure_fin_avant_debut_raises_error(self):
        """Test: erreur si heure_fin avant heure_debut."""
        with pytest.raises(ValueError):
            Reservation(
                ressource_id=1,
                chantier_id=100,
                demandeur_id=10,
                date_reservation=date.today(),
                heure_debut=time(12, 0),
                heure_fin=time(9, 0),
            )
