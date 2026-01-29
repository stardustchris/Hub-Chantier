"""Tests unitaires pour les mappers logistique."""

from datetime import date, time

from modules.logistique.infrastructure.web.mappers import (
    map_ressource_create_request,
    map_ressource_update_request,
    map_reservation_create_request,
    map_reservation_update_request,
)
from modules.logistique.domain.value_objects import CategorieRessource


class TestMapRessourceCreateRequest:
    """Tests pour map_ressource_create_request."""

    def test_creation_basique(self):
        """Crée un DTO avec les champs requis."""
        dto = map_ressource_create_request(
            nom="Grue",
            code="GRU-001",
            categorie=CategorieRessource.ENGIN_LEVAGE,
        )
        assert dto.nom == "Grue"
        assert dto.code == "GRU-001"
        assert dto.categorie == CategorieRessource.ENGIN_LEVAGE
        assert dto.couleur == "#3B82F6"

    def test_creation_complète(self):
        """Crée un DTO avec tous les champs."""
        dto = map_ressource_create_request(
            nom="Bétonnière",
            code="BET-002",
            categorie=CategorieRessource.ENGIN_LEVAGE,
            photo_url="/photos/bet.jpg",
            couleur="#FF0000",
            heure_debut_defaut=time(7, 0),
            heure_fin_defaut=time(17, 0),
            validation_requise=True,
            description="Grande bétonnière",
        )
        assert dto.photo_url == "/photos/bet.jpg"
        assert dto.couleur == "#FF0000"
        assert dto.validation_requise is True
        assert dto.description == "Grande bétonnière"


class TestMapRessourceUpdateRequest:
    """Tests pour map_ressource_update_request."""

    def test_update_partiel(self):
        """Met à jour seulement le nom."""
        dto = map_ressource_update_request(nom="Nouveau Nom")
        assert dto.nom == "Nouveau Nom"
        assert dto.code is None
        assert dto.actif is None

    def test_update_complet(self):
        """Met à jour tous les champs."""
        dto = map_ressource_update_request(
            nom="N",
            code="C",
            categorie=CategorieRessource.VEHICULE,
            actif=False,
        )
        assert dto.nom == "N"
        assert dto.code == "C"
        assert dto.actif is False


class TestMapReservationCreateRequest:
    """Tests pour map_reservation_create_request."""

    def test_creation(self):
        """Crée un DTO de réservation."""
        dto = map_reservation_create_request(
            ressource_id=1,
            chantier_id=5,
            date_reservation=date(2026, 2, 15),
            heure_debut=time(8, 0),
            heure_fin=time(12, 0),
            commentaire="Besoin urgent",
        )
        assert dto.ressource_id == 1
        assert dto.chantier_id == 5
        assert dto.commentaire == "Besoin urgent"

    def test_creation_sans_commentaire(self):
        """Crée un DTO sans commentaire."""
        dto = map_reservation_create_request(
            ressource_id=1,
            chantier_id=5,
            date_reservation=date(2026, 2, 15),
            heure_debut=time(8, 0),
            heure_fin=time(12, 0),
        )
        assert dto.commentaire is None


class TestMapReservationUpdateRequest:
    """Tests pour map_reservation_update_request."""

    def test_update_date_seule(self):
        """Met à jour seulement la date."""
        dto = map_reservation_update_request(date_reservation=date(2026, 3, 1))
        assert dto.date_reservation == date(2026, 3, 1)
        assert dto.heure_debut is None

    def test_update_commentaire(self):
        """Met à jour le commentaire."""
        dto = map_reservation_update_request(commentaire="Mis à jour")
        assert dto.commentaire == "Mis à jour"
