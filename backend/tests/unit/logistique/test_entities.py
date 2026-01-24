"""Tests des Entites du module Logistique.

CDC Section 11 - Gestion de la logistique et du materiel.
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import patch

from modules.logistique.domain.entities import Ressource, Reservation
from modules.logistique.domain.value_objects import TypeRessource, StatutReservation


class TestRessource:
    """Tests pour l'entite Ressource."""

    # ==================== Creation ====================

    def test_create_ressource_minimal(self):
        """Creation d'une ressource avec donnees minimales."""
        ressource = Ressource(
            code="GRU001",
            nom="Grue mobile 50T",
        )
        assert ressource.code == "GRU001"
        assert ressource.nom == "Grue mobile 50T"
        assert ressource.type_ressource == TypeRessource.OUTILLAGE
        assert ressource.is_active is True
        assert ressource.validation_requise is True
        assert ressource.plage_horaire_debut == "08:00"
        assert ressource.plage_horaire_fin == "18:00"

    def test_create_ressource_complet(self):
        """Creation d'une ressource avec toutes les donnees."""
        ressource = Ressource(
            id=1,
            code="NAC001",
            nom="Nacelle articulee 20m",
            description="Nacelle pour travaux en hauteur",
            type_ressource=TypeRessource.LEVAGE,
            photo_url="https://storage.example.com/nacelle.jpg",
            couleur="#FF5733",
            plage_horaire_debut="07:00",
            plage_horaire_fin="19:00",
            validation_requise=True,
            is_active=True,
        )
        assert ressource.id == 1
        assert ressource.code == "NAC001"
        assert ressource.nom == "Nacelle articulee 20m"
        assert ressource.description == "Nacelle pour travaux en hauteur"
        assert ressource.type_ressource == TypeRessource.LEVAGE
        assert ressource.photo_url == "https://storage.example.com/nacelle.jpg"
        assert ressource.couleur == "#FF5733"
        assert ressource.plage_horaire_debut == "07:00"
        assert ressource.plage_horaire_fin == "19:00"
        assert ressource.validation_requise is True

    def test_create_ressource_code_vide_raise_error(self):
        """Erreur si le code est vide."""
        with pytest.raises(ValueError, match="code.*obligatoire"):
            Ressource(code="", nom="Test")

    def test_create_ressource_nom_vide_raise_error(self):
        """Erreur si le nom est vide."""
        with pytest.raises(ValueError, match="nom.*obligatoire"):
            Ressource(code="TEST001", nom="")

    def test_create_ressource_plage_horaire_debut_vide_raise_error(self):
        """Erreur si plage_horaire_debut est vide."""
        with pytest.raises(ValueError, match="plages horaires.*obligatoires"):
            Ressource(
                code="TEST001",
                nom="Test",
                plage_horaire_debut="",
                plage_horaire_fin="18:00",
            )

    def test_create_ressource_plage_horaire_fin_vide_raise_error(self):
        """Erreur si plage_horaire_fin est vide."""
        with pytest.raises(ValueError, match="plages horaires.*obligatoires"):
            Ressource(
                code="TEST001",
                nom="Test",
                plage_horaire_debut="08:00",
                plage_horaire_fin="",
            )

    def test_couleur_par_defaut(self):
        """Verifie la couleur par defaut."""
        ressource = Ressource(code="TEST001", nom="Test")
        assert ressource.couleur == "#3498DB"

    # ==================== Proprietes ====================

    def test_is_deleted_false_par_defaut(self):
        """Une ressource n'est pas supprimee par defaut."""
        ressource = Ressource(code="TEST001", nom="Test")
        assert ressource.is_deleted is False

    def test_is_deleted_true_quand_deleted_at_defini(self):
        """Une ressource est supprimee si deleted_at est defini."""
        ressource = Ressource(
            code="TEST001",
            nom="Test",
            deleted_at=datetime.now(),
        )
        assert ressource.is_deleted is True

    # ==================== Methodes activer/desactiver ====================

    def test_activer_ressource(self):
        """Test de l'activation d'une ressource."""
        ressource = Ressource(code="TEST001", nom="Test", is_active=False)
        old_updated = ressource.updated_at

        ressource.activer()

        assert ressource.is_active is True
        assert ressource.updated_at >= old_updated

    def test_desactiver_ressource(self):
        """Test de la desactivation d'une ressource."""
        ressource = Ressource(code="TEST001", nom="Test", is_active=True)
        old_updated = ressource.updated_at

        ressource.desactiver()

        assert ressource.is_active is False
        assert ressource.updated_at >= old_updated

    # ==================== Methodes supprimer/restaurer ====================

    def test_supprimer_ressource(self):
        """Test de la suppression (soft delete) d'une ressource."""
        ressource = Ressource(code="TEST001", nom="Test")
        old_updated = ressource.updated_at

        ressource.supprimer()

        assert ressource.is_deleted is True
        assert ressource.deleted_at is not None
        assert ressource.is_active is False
        assert ressource.updated_at >= old_updated

    def test_restaurer_ressource(self):
        """Test de la restauration d'une ressource supprimee."""
        ressource = Ressource(
            code="TEST001",
            nom="Test",
            deleted_at=datetime.now(),
            is_active=False,
        )
        old_updated = ressource.updated_at

        ressource.restaurer()

        assert ressource.is_deleted is False
        assert ressource.deleted_at is None
        assert ressource.is_active is True
        assert ressource.updated_at >= old_updated

    # ==================== Methode update ====================

    def test_update_nom(self):
        """Test de la mise a jour du nom."""
        ressource = Ressource(code="TEST001", nom="Ancien nom")

        ressource.update(nom="Nouveau nom")

        assert ressource.nom == "Nouveau nom"

    def test_update_description(self):
        """Test de la mise a jour de la description."""
        ressource = Ressource(code="TEST001", nom="Test")

        ressource.update(description="Nouvelle description")

        assert ressource.description == "Nouvelle description"

    def test_update_type_ressource(self):
        """Test de la mise a jour du type de ressource."""
        ressource = Ressource(code="TEST001", nom="Test")

        ressource.update(type_ressource=TypeRessource.LEVAGE)

        assert ressource.type_ressource == TypeRessource.LEVAGE

    def test_update_photo_url(self):
        """Test de la mise a jour de l'URL de photo."""
        ressource = Ressource(code="TEST001", nom="Test")

        ressource.update(photo_url="https://example.com/photo.jpg")

        assert ressource.photo_url == "https://example.com/photo.jpg"

    def test_update_couleur(self):
        """Test de la mise a jour de la couleur."""
        ressource = Ressource(code="TEST001", nom="Test")

        ressource.update(couleur="#FF0000")

        assert ressource.couleur == "#FF0000"

    def test_update_plage_horaire_debut(self):
        """Test de la mise a jour de l'heure de debut."""
        ressource = Ressource(code="TEST001", nom="Test")

        ressource.update(plage_horaire_debut="06:00")

        assert ressource.plage_horaire_debut == "06:00"

    def test_update_plage_horaire_fin(self):
        """Test de la mise a jour de l'heure de fin."""
        ressource = Ressource(code="TEST001", nom="Test")

        ressource.update(plage_horaire_fin="20:00")

        assert ressource.plage_horaire_fin == "20:00"

    def test_update_validation_requise(self):
        """Test de la mise a jour de validation_requise."""
        ressource = Ressource(code="TEST001", nom="Test", validation_requise=True)

        ressource.update(validation_requise=False)

        assert ressource.validation_requise is False

    def test_update_plusieurs_champs(self):
        """Test de la mise a jour de plusieurs champs."""
        ressource = Ressource(code="TEST001", nom="Test")

        ressource.update(
            nom="Nouveau nom",
            description="Nouvelle description",
            couleur="#FF0000",
        )

        assert ressource.nom == "Nouveau nom"
        assert ressource.description == "Nouvelle description"
        assert ressource.couleur == "#FF0000"

    def test_update_met_a_jour_updated_at(self):
        """Test que update met a jour updated_at."""
        ressource = Ressource(code="TEST001", nom="Test")
        old_updated = ressource.updated_at

        ressource.update(nom="Nouveau nom")

        assert ressource.updated_at >= old_updated

    def test_update_avec_none_ne_modifie_pas(self):
        """Test que les valeurs None ne modifient pas les champs."""
        ressource = Ressource(
            code="TEST001",
            nom="Test",
            description="Description originale",
        )

        ressource.update(description=None)

        # None ne modifie pas le champ
        assert ressource.description == "Description originale"

    # ==================== Repr ====================

    def test_repr(self):
        """Test de la representation string."""
        ressource = Ressource(id=1, code="TEST001", nom="Test ressource")
        repr_str = repr(ressource)
        assert "id=1" in repr_str
        assert "code=TEST001" in repr_str
        assert "nom=Test ressource" in repr_str


class TestReservation:
    """Tests pour l'entite Reservation."""

    # ==================== Creation ====================

    def test_create_reservation_minimal(self):
        """Creation d'une reservation avec donnees minimales."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=2,
            demandeur_id=3,
        )
        assert reservation.ressource_id == 1
        assert reservation.chantier_id == 2
        assert reservation.demandeur_id == 3
        assert reservation.statut == StatutReservation.EN_ATTENTE
        assert reservation.valideur_id is None
        assert reservation.motif_refus is None

    def test_create_reservation_complet(self):
        """Creation d'une reservation avec toutes les donnees."""
        today = date.today()
        tomorrow = today + timedelta(days=1)

        reservation = Reservation(
            id=1,
            ressource_id=1,
            chantier_id=2,
            demandeur_id=3,
            date_debut=today,
            date_fin=tomorrow,
            heure_debut="09:00",
            heure_fin="17:00",
            note="Note de reservation",
            statut=StatutReservation.VALIDEE,
            valideur_id=5,
        )

        assert reservation.id == 1
        assert reservation.date_debut == today
        assert reservation.date_fin == tomorrow
        assert reservation.heure_debut == "09:00"
        assert reservation.heure_fin == "17:00"
        assert reservation.note == "Note de reservation"
        assert reservation.statut == StatutReservation.VALIDEE
        assert reservation.valideur_id == 5

    def test_create_reservation_ressource_id_invalide_raise_error(self):
        """Erreur si ressource_id est invalide."""
        with pytest.raises(ValueError, match="ressource_id.*obligatoire"):
            Reservation(ressource_id=0, chantier_id=1, demandeur_id=1)

        with pytest.raises(ValueError, match="ressource_id.*obligatoire"):
            Reservation(ressource_id=-1, chantier_id=1, demandeur_id=1)

    def test_create_reservation_chantier_id_invalide_raise_error(self):
        """Erreur si chantier_id est invalide (LOG-08)."""
        with pytest.raises(ValueError, match="chantier_id.*obligatoire"):
            Reservation(ressource_id=1, chantier_id=0, demandeur_id=1)

        with pytest.raises(ValueError, match="chantier_id.*obligatoire"):
            Reservation(ressource_id=1, chantier_id=-1, demandeur_id=1)

    def test_create_reservation_demandeur_id_invalide_raise_error(self):
        """Erreur si demandeur_id est invalide."""
        with pytest.raises(ValueError, match="demandeur_id.*obligatoire"):
            Reservation(ressource_id=1, chantier_id=1, demandeur_id=0)

        with pytest.raises(ValueError, match="demandeur_id.*obligatoire"):
            Reservation(ressource_id=1, chantier_id=1, demandeur_id=-1)

    def test_create_reservation_date_fin_avant_debut_raise_error(self):
        """Erreur si date_fin est avant date_debut."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        with pytest.raises(ValueError, match="date_fin.*>=.*date_debut"):
            Reservation(
                ressource_id=1,
                chantier_id=1,
                demandeur_id=1,
                date_debut=today,
                date_fin=yesterday,
            )

    def test_create_reservation_meme_date_ok(self):
        """Une reservation sur une meme date est valide."""
        today = date.today()
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            date_debut=today,
            date_fin=today,
        )
        assert reservation.date_debut == reservation.date_fin

    # ==================== Proprietes ====================

    def test_is_active_en_attente(self):
        """Une reservation EN_ATTENTE est active."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.EN_ATTENTE,
        )
        assert reservation.is_active is True

    def test_is_active_validee(self):
        """Une reservation VALIDEE est active."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.VALIDEE,
        )
        assert reservation.is_active is True

    def test_is_active_refusee(self):
        """Une reservation REFUSEE n'est pas active."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.REFUSEE,
        )
        assert reservation.is_active is False

    def test_is_active_annulee(self):
        """Une reservation ANNULEE n'est pas active."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.ANNULEE,
        )
        assert reservation.is_active is False

    def test_is_pending(self):
        """Test de la propriete is_pending."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.EN_ATTENTE,
        )
        assert reservation.is_pending is True

        reservation.statut = StatutReservation.VALIDEE
        assert reservation.is_pending is False

    def test_is_validated(self):
        """Test de la propriete is_validated."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.VALIDEE,
        )
        assert reservation.is_validated is True

        reservation.statut = StatutReservation.EN_ATTENTE
        assert reservation.is_validated is False

    def test_is_refused(self):
        """Test de la propriete is_refused."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.REFUSEE,
        )
        assert reservation.is_refused is True

        reservation.statut = StatutReservation.EN_ATTENTE
        assert reservation.is_refused is False

    def test_is_cancelled(self):
        """Test de la propriete is_cancelled."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.ANNULEE,
        )
        assert reservation.is_cancelled is True

        reservation.statut = StatutReservation.EN_ATTENTE
        assert reservation.is_cancelled is False

    # ==================== Methode valider ====================

    def test_valider_reservation_en_attente(self):
        """Test de la validation d'une reservation en attente."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.EN_ATTENTE,
        )

        reservation.valider(valideur_id=5)

        assert reservation.statut == StatutReservation.VALIDEE
        assert reservation.valideur_id == 5
        assert reservation.validated_at is not None

    def test_valider_reservation_deja_validee_raise_error(self):
        """Erreur si on essaie de valider une reservation deja validee."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.VALIDEE,
        )

        with pytest.raises(ValueError, match="Impossible de valider"):
            reservation.valider(valideur_id=5)

    def test_valider_reservation_refusee_raise_error(self):
        """Erreur si on essaie de valider une reservation refusee."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.REFUSEE,
        )

        with pytest.raises(ValueError, match="Impossible de valider"):
            reservation.valider(valideur_id=5)

    def test_valider_reservation_annulee_raise_error(self):
        """Erreur si on essaie de valider une reservation annulee."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.ANNULEE,
        )

        with pytest.raises(ValueError, match="Impossible de valider"):
            reservation.valider(valideur_id=5)

    # ==================== Methode refuser ====================

    def test_refuser_reservation_en_attente(self):
        """Test du refus d'une reservation en attente."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.EN_ATTENTE,
        )

        reservation.refuser(valideur_id=5, motif="Ressource indisponible")

        assert reservation.statut == StatutReservation.REFUSEE
        assert reservation.valideur_id == 5
        assert reservation.motif_refus == "Ressource indisponible"
        assert reservation.refused_at is not None

    def test_refuser_reservation_sans_motif(self):
        """Test du refus sans motif (LOG-16: motif optionnel)."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.EN_ATTENTE,
        )

        reservation.refuser(valideur_id=5)

        assert reservation.statut == StatutReservation.REFUSEE
        assert reservation.motif_refus is None

    def test_refuser_reservation_validee_raise_error(self):
        """Erreur si on essaie de refuser une reservation validee."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.VALIDEE,
        )

        with pytest.raises(ValueError, match="Impossible de refuser"):
            reservation.refuser(valideur_id=5)

    def test_refuser_reservation_deja_refusee_raise_error(self):
        """Erreur si on essaie de refuser une reservation deja refusee."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.REFUSEE,
        )

        with pytest.raises(ValueError, match="Impossible de refuser"):
            reservation.refuser(valideur_id=5)

    # ==================== Methode annuler ====================

    def test_annuler_reservation_en_attente(self):
        """Test de l'annulation d'une reservation en attente."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.EN_ATTENTE,
        )

        reservation.annuler()

        assert reservation.statut == StatutReservation.ANNULEE
        assert reservation.cancelled_at is not None

    def test_annuler_reservation_validee(self):
        """Test de l'annulation d'une reservation validee."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.VALIDEE,
        )

        reservation.annuler()

        assert reservation.statut == StatutReservation.ANNULEE
        assert reservation.cancelled_at is not None

    def test_annuler_reservation_refusee_raise_error(self):
        """Erreur si on essaie d'annuler une reservation refusee."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.REFUSEE,
        )

        with pytest.raises(ValueError, match="Impossible d'annuler"):
            reservation.annuler()

    def test_annuler_reservation_deja_annulee_raise_error(self):
        """Erreur si on essaie d'annuler une reservation deja annulee."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            statut=StatutReservation.ANNULEE,
        )

        with pytest.raises(ValueError, match="Impossible d'annuler"):
            reservation.annuler()

    # ==================== Methode chevauche ====================

    def test_chevauche_meme_dates_meme_heures(self):
        """Test de chevauchement avec memes dates et heures."""
        today = date.today()
        r1 = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            date_debut=today,
            date_fin=today,
            heure_debut="08:00",
            heure_fin="12:00",
        )
        r2 = Reservation(
            ressource_id=1,
            chantier_id=2,
            demandeur_id=2,
            date_debut=today,
            date_fin=today,
            heure_debut="08:00",
            heure_fin="12:00",
        )

        assert r1.chevauche(r2) is True
        assert r2.chevauche(r1) is True

    def test_chevauche_heures_superposees(self):
        """Test de chevauchement avec heures superposees."""
        today = date.today()
        r1 = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            date_debut=today,
            date_fin=today,
            heure_debut="08:00",
            heure_fin="12:00",
        )
        r2 = Reservation(
            ressource_id=1,
            chantier_id=2,
            demandeur_id=2,
            date_debut=today,
            date_fin=today,
            heure_debut="10:00",
            heure_fin="14:00",
        )

        assert r1.chevauche(r2) is True
        assert r2.chevauche(r1) is True

    def test_pas_chevauchement_heures_consecutives(self):
        """Pas de chevauchement si heures consecutives."""
        today = date.today()
        r1 = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            date_debut=today,
            date_fin=today,
            heure_debut="08:00",
            heure_fin="12:00",
        )
        r2 = Reservation(
            ressource_id=1,
            chantier_id=2,
            demandeur_id=2,
            date_debut=today,
            date_fin=today,
            heure_debut="12:00",
            heure_fin="18:00",
        )

        assert r1.chevauche(r2) is False
        assert r2.chevauche(r1) is False

    def test_pas_chevauchement_dates_differentes(self):
        """Pas de chevauchement si dates differentes."""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        r1 = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            date_debut=today,
            date_fin=today,
            heure_debut="08:00",
            heure_fin="18:00",
        )
        r2 = Reservation(
            ressource_id=1,
            chantier_id=2,
            demandeur_id=2,
            date_debut=tomorrow,
            date_fin=tomorrow,
            heure_debut="08:00",
            heure_fin="18:00",
        )

        assert r1.chevauche(r2) is False
        assert r2.chevauche(r1) is False

    def test_chevauche_dates_qui_se_suivent(self):
        """Pas de chevauchement si dates consecutives."""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        r1 = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            date_debut=today,
            date_fin=today,
            heure_debut="08:00",
            heure_fin="18:00",
        )
        r2 = Reservation(
            ressource_id=1,
            chantier_id=2,
            demandeur_id=2,
            date_debut=tomorrow,
            date_fin=tomorrow,
            heure_debut="08:00",
            heure_fin="18:00",
        )

        assert r1.chevauche(r2) is False

    def test_chevauche_multi_jours(self):
        """Test de chevauchement sur plusieurs jours."""
        today = date.today()
        r1 = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            date_debut=today,
            date_fin=today + timedelta(days=5),
            heure_debut="08:00",
            heure_fin="18:00",
        )
        r2 = Reservation(
            ressource_id=1,
            chantier_id=2,
            demandeur_id=2,
            date_debut=today + timedelta(days=3),
            date_fin=today + timedelta(days=7),
            heure_debut="08:00",
            heure_fin="18:00",
        )

        assert r1.chevauche(r2) is True
        assert r2.chevauche(r1) is True

    def test_pas_chevauchement_heures_separees(self):
        """Pas de chevauchement si heures separees."""
        today = date.today()
        r1 = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            date_debut=today,
            date_fin=today,
            heure_debut="08:00",
            heure_fin="10:00",
        )
        r2 = Reservation(
            ressource_id=1,
            chantier_id=2,
            demandeur_id=2,
            date_debut=today,
            date_fin=today,
            heure_debut="14:00",
            heure_fin="18:00",
        )

        assert r1.chevauche(r2) is False
        assert r2.chevauche(r1) is False

    # ==================== Repr ====================

    def test_repr(self):
        """Test de la representation string."""
        reservation = Reservation(
            id=1,
            ressource_id=2,
            chantier_id=3,
            demandeur_id=4,
            statut=StatutReservation.EN_ATTENTE,
        )
        repr_str = repr(reservation)
        assert "id=1" in repr_str
        assert "ressource_id=2" in repr_str
        assert "chantier_id=3" in repr_str
        assert "statut=en_attente" in repr_str

    # ==================== Workflow complet ====================

    def test_workflow_validation_complete(self):
        """Test du workflow complet de validation."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
        )

        # Initial: EN_ATTENTE
        assert reservation.statut == StatutReservation.EN_ATTENTE
        assert reservation.is_pending is True

        # Validation
        reservation.valider(valideur_id=5)
        assert reservation.statut == StatutReservation.VALIDEE
        assert reservation.is_validated is True
        assert reservation.valideur_id == 5

        # Annulation apres validation
        reservation.annuler()
        assert reservation.statut == StatutReservation.ANNULEE
        assert reservation.is_cancelled is True

    def test_workflow_refus_complete(self):
        """Test du workflow complet de refus."""
        reservation = Reservation(
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
        )

        # Initial: EN_ATTENTE
        assert reservation.statut == StatutReservation.EN_ATTENTE

        # Refus avec motif (LOG-16)
        reservation.refuser(valideur_id=5, motif="Conflit de planning")
        assert reservation.statut == StatutReservation.REFUSEE
        assert reservation.is_refused is True
        assert reservation.motif_refus == "Conflit de planning"

        # Impossible d'annuler apres refus
        with pytest.raises(ValueError):
            reservation.annuler()
