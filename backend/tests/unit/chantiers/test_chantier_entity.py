"""Tests unitaires pour l'entité Chantier."""

import pytest
from datetime import date, datetime

from modules.chantiers.domain.entities.chantier import Chantier
from modules.chantiers.domain.value_objects import (
    CodeChantier,
    StatutChantier,
    CoordonneesGPS,
    ContactChantier,
)
from shared.domain.value_objects import Couleur


class TestChantierCreation:
    """Tests pour la création de Chantier."""

    def test_create_minimal_chantier(self):
        """Test création d'un chantier avec champs minimum."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Chantier Test",
            adresse="123 Rue Test",
        )

        assert chantier.nom == "Chantier Test"
        assert chantier.adresse == "123 Rue Test"
        assert chantier.id is None
        assert chantier.statut.value.value == "ouvert"
        assert chantier.couleur is not None

    def test_create_full_chantier(self):
        """Test création d'un chantier avec tous les champs."""
        chantier = Chantier(
            id=1,
            code=CodeChantier("A002"),
            nom="Chantier Complet",
            adresse="456 Avenue Principale",
            statut=StatutChantier.en_cours(),
            couleur=Couleur("#FF0000"),
            coordonnees_gps=CoordonneesGPS(latitude=48.8566, longitude=2.3522),
            contact=ContactChantier(nom="Jean Test"),
            heures_estimees=100.0,
            date_debut=date(2024, 1, 1),
            date_fin=date(2024, 6, 30),
            description="Description test",
            conducteur_ids=[1, 2],
            chef_chantier_ids=[3],
        )

        assert chantier.id == 1
        assert chantier.nom == "Chantier Complet"
        assert chantier.heures_estimees == 100.0
        assert chantier.has_gps is True
        assert chantier.has_contact is True

    def test_nom_normalization(self):
        """Test normalisation du nom."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="  Chantier Test  ",
            adresse="123 Rue Test",
        )

        assert chantier.nom == "Chantier Test"

    def test_adresse_normalization(self):
        """Test normalisation de l'adresse."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Chantier Test",
            adresse="  123 Rue Test  ",
        )

        assert chantier.adresse == "123 Rue Test"

    def test_empty_nom_raises(self):
        """Test erreur si nom vide."""
        with pytest.raises(ValueError, match="Le nom du chantier ne peut pas être vide"):
            Chantier(
                code=CodeChantier("A001"),
                nom="",
                adresse="123 Rue Test",
            )

    def test_empty_adresse_raises(self):
        """Test erreur si adresse vide."""
        with pytest.raises(ValueError, match="L'adresse du chantier ne peut pas être vide"):
            Chantier(
                code=CodeChantier("A001"),
                nom="Chantier Test",
                adresse="",
            )

    def test_invalid_dates_raises(self):
        """Test erreur si date_fin < date_debut."""
        with pytest.raises(ValueError, match="date de fin ne peut pas être antérieure"):
            Chantier(
                code=CodeChantier("A001"),
                nom="Chantier Test",
                adresse="123 Rue Test",
                date_debut=date(2024, 6, 1),
                date_fin=date(2024, 1, 1),
            )


class TestChantierProperties:
    """Tests pour les propriétés de Chantier."""

    def test_code_str(self):
        """Test code_str property."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        assert chantier.code_str == "A001"

    def test_is_active_ouvert(self):
        """Test is_active pour statut ouvert."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            statut=StatutChantier.ouvert(),
        )

        assert chantier.is_active is True

    def test_is_active_ferme(self):
        """Test is_active pour statut fermé."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            statut=StatutChantier.ferme(),
        )

        assert chantier.is_active is False

    def test_allows_modifications_ouvert(self):
        """Test allows_modifications pour statut ouvert."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            statut=StatutChantier.ouvert(),
        )

        assert chantier.allows_modifications is True

    def test_has_gps_false(self):
        """Test has_gps sans coordonnées."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        assert chantier.has_gps is False

    def test_has_contact_false(self):
        """Test has_contact sans contact."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        assert chantier.has_contact is False

    def test_duree_prevue_jours(self):
        """Test calcul durée prévue."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            date_debut=date(2024, 1, 1),
            date_fin=date(2024, 1, 31),
        )

        assert chantier.duree_prevue_jours == 30

    def test_duree_prevue_jours_none(self):
        """Test durée prévue sans dates."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        assert chantier.duree_prevue_jours is None


class TestChantierStatutMethods:
    """Tests pour les méthodes de changement de statut."""

    def test_demarrer(self):
        """Test passage en cours."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            statut=StatutChantier.ouvert(),
        )

        chantier.demarrer()

        assert chantier.statut.value.value == "en_cours"

    def test_receptionner(self):
        """Test passage à réceptionné."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            statut=StatutChantier.en_cours(),
        )

        chantier.receptionner()

        assert chantier.statut.value.value == "receptionne"

    def test_fermer(self):
        """Test fermeture."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            statut=StatutChantier.receptionne(),
        )

        chantier.fermer()

        assert chantier.statut.value.value == "ferme"

    def test_rouvrir_from_receptionne(self):
        """Test réouverture depuis réceptionné."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            statut=StatutChantier.receptionne(),
        )

        chantier.rouvrir()

        assert chantier.statut.value.value == "en_cours"

    def test_rouvrir_from_ouvert_raises(self):
        """Test réouverture depuis ouvert lève erreur."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            statut=StatutChantier.ouvert(),
        )

        with pytest.raises(ValueError, match="Seul un chantier réceptionné"):
            chantier.rouvrir()

    def test_change_statut_invalid_transition_raises(self):
        """Test transition non autorisée lève erreur."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            statut=StatutChantier.ferme(),
        )

        # Fermé ne peut transitionner vers aucun autre statut
        with pytest.raises(ValueError, match="Transition non autorisée"):
            chantier.change_statut(StatutChantier.ouvert())


class TestChantierResponsables:
    """Tests pour la gestion des responsables."""

    def test_assigner_conducteur(self):
        """Test assignation conducteur."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        chantier.assigner_conducteur(1)

        assert 1 in chantier.conducteur_ids

    def test_assigner_conducteur_already_assigned(self):
        """Test assignation conducteur déjà assigné."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            conducteur_ids=[1],
        )

        chantier.assigner_conducteur(1)

        assert chantier.conducteur_ids.count(1) == 1

    def test_retirer_conducteur(self):
        """Test retrait conducteur."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            conducteur_ids=[1, 2],
        )

        chantier.retirer_conducteur(1)

        assert 1 not in chantier.conducteur_ids
        assert 2 in chantier.conducteur_ids

    def test_retirer_conducteur_not_assigned(self):
        """Test retrait conducteur non assigné."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        chantier.retirer_conducteur(999)  # Ne lève pas d'erreur

        assert 999 not in chantier.conducteur_ids

    def test_assigner_chef_chantier(self):
        """Test assignation chef de chantier."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        chantier.assigner_chef_chantier(1)

        assert 1 in chantier.chef_chantier_ids

    def test_retirer_chef_chantier(self):
        """Test retrait chef de chantier."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            chef_chantier_ids=[1],
        )

        chantier.retirer_chef_chantier(1)

        assert 1 not in chantier.chef_chantier_ids

    def test_is_conducteur_true(self):
        """Test is_conducteur pour conducteur assigné."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            conducteur_ids=[1, 2],
        )

        assert chantier.is_conducteur(1) is True
        assert chantier.is_conducteur(3) is False

    def test_is_chef_chantier_true(self):
        """Test is_chef_chantier pour chef assigné."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            chef_chantier_ids=[1],
        )

        assert chantier.is_chef_chantier(1) is True
        assert chantier.is_chef_chantier(2) is False

    def test_is_responsable(self):
        """Test is_responsable."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            conducteur_ids=[1],
            chef_chantier_ids=[2],
        )

        assert chantier.is_responsable(1) is True
        assert chantier.is_responsable(2) is True
        assert chantier.is_responsable(3) is False


class TestChantierUpdateMethods:
    """Tests pour les méthodes de mise à jour."""

    def test_update_coordonnees_gps(self):
        """Test mise à jour GPS."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )
        gps = CoordonneesGPS(latitude=48.8566, longitude=2.3522)

        chantier.update_coordonnees_gps(gps)

        assert chantier.coordonnees_gps == gps

    def test_update_contact(self):
        """Test mise à jour contact."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )
        contact = ContactChantier(nom="Jean Test")

        chantier.update_contact(contact)

        assert chantier.contact == contact

    def test_update_dates(self):
        """Test mise à jour dates."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        chantier.update_dates(
            date_debut=date(2024, 1, 1),
            date_fin=date(2024, 6, 30),
        )

        assert chantier.date_debut == date(2024, 1, 1)
        assert chantier.date_fin == date(2024, 6, 30)

    def test_update_dates_invalid_raises(self):
        """Test mise à jour dates invalides lève erreur."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        with pytest.raises(ValueError, match="date de fin ne peut pas être antérieure"):
            chantier.update_dates(
                date_debut=date(2024, 6, 1),
                date_fin=date(2024, 1, 1),
            )

    def test_update_heures_estimees(self):
        """Test mise à jour heures estimées."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        chantier.update_heures_estimees(150.0)

        assert chantier.heures_estimees == 150.0

    def test_update_heures_estimees_negative_raises(self):
        """Test heures négatives lève erreur."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        with pytest.raises(ValueError, match="heures estimées doivent être positives"):
            chantier.update_heures_estimees(-10.0)

    def test_update_photo_couverture(self):
        """Test mise à jour photo couverture."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        chantier.update_photo_couverture("https://example.com/photo.jpg")

        assert chantier.photo_couverture == "https://example.com/photo.jpg"

    def test_update_infos(self):
        """Test mise à jour infos générales."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        chantier.update_infos(
            nom="Nouveau Nom",
            adresse="Nouvelle Adresse",
            description="Nouvelle description",
            couleur=Couleur("#00FF00"),
        )

        assert chantier.nom == "Nouveau Nom"
        assert chantier.adresse == "Nouvelle Adresse"
        assert chantier.description == "Nouvelle description"

    def test_update_infos_empty_nom_raises(self):
        """Test mise à jour nom vide lève erreur."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        with pytest.raises(ValueError, match="Le nom ne peut pas être vide"):
            chantier.update_infos(nom="")

    def test_update_infos_empty_adresse_raises(self):
        """Test mise à jour adresse vide lève erreur."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        with pytest.raises(ValueError, match="L'adresse ne peut pas être vide"):
            chantier.update_infos(adresse="")

    def test_update_infos_empty_description(self):
        """Test mise à jour description vide devient None."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
            description="Description initiale",
        )

        chantier.update_infos(description="   ")

        assert chantier.description is None


class TestChantierEquality:
    """Tests pour l'égalité et le hash."""

    def test_equality_same_id(self):
        """Test égalité avec même ID."""
        chantier1 = Chantier(
            id=1,
            code=CodeChantier("A001"),
            nom="Test1",
            adresse="Test",
        )
        chantier2 = Chantier(
            id=1,
            code=CodeChantier("A002"),
            nom="Test2",
            adresse="Autre",
        )

        assert chantier1 == chantier2

    def test_equality_different_id(self):
        """Test inégalité avec ID différents."""
        chantier1 = Chantier(
            id=1,
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )
        chantier2 = Chantier(
            id=2,
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        assert chantier1 != chantier2

    def test_equality_none_id(self):
        """Test inégalité avec ID None."""
        chantier1 = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )
        chantier2 = Chantier(
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        assert chantier1 != chantier2

    def test_equality_with_non_chantier(self):
        """Test inégalité avec non-Chantier."""
        chantier = Chantier(
            id=1,
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        assert chantier != "not a chantier"

    def test_hash_with_id(self):
        """Test hash avec ID."""
        chantier = Chantier(
            id=1,
            code=CodeChantier("A001"),
            nom="Test",
            adresse="Test",
        )

        assert hash(chantier) == hash(1)

    def test_str(self):
        """Test représentation textuelle."""
        chantier = Chantier(
            code=CodeChantier("A001"),
            nom="Chantier Test",
            adresse="Test",
        )

        assert str(chantier) == "A001 - Chantier Test"
