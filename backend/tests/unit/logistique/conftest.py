"""Fixtures de test pour le module Logistique."""

import pytest
from datetime import date, time, datetime
from unittest.mock import Mock, MagicMock

from modules.logistique.domain.entities import Ressource, Reservation
from modules.logistique.domain.value_objects import (
    CategorieRessource,
    StatutReservation,
    PlageHoraire,
)
from modules.logistique.domain.repositories import (
    RessourceRepository,
    ReservationRepository,
)
from modules.logistique.application.ports.event_bus import EventBus


@pytest.fixture
def sample_ressource() -> Ressource:
    """Ressource de test standard."""
    return Ressource(
        id=1,
        code="GRU001",
        nom="Grue mobile 50T",
        description="Grue mobile pour levage jusqu'à 50 tonnes",
        categorie=CategorieRessource.ENGIN_LEVAGE,
        couleur="#FF5733",
        photo_url="https://example.com/grue.jpg",
        plage_horaire_defaut=PlageHoraire(heure_debut=time(7, 0), heure_fin=time(18, 0)),
        validation_requise=True,
        actif=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_ressource_no_validation() -> Ressource:
    """Ressource sans validation requise."""
    return Ressource(
        id=2,
        code="OUT001",
        nom="Marteau-piqueur",
        description="Marteau-piqueur électrique",
        categorie=CategorieRessource.GROS_OUTILLAGE,
        couleur="#3498DB",
        plage_horaire_defaut=PlageHoraire(heure_debut=time(8, 0), heure_fin=time(17, 0)),
        validation_requise=False,
        actif=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_reservation(sample_ressource: Ressource) -> Reservation:
    """Réservation de test standard (en attente)."""
    return Reservation(
        id=1,
        ressource_id=sample_ressource.id,
        chantier_id=100,
        demandeur_id=10,
        date_reservation=date.today(),
        heure_debut=time(9, 0),
        heure_fin=time(12, 0),
        statut=StatutReservation.EN_ATTENTE,
        commentaire="Besoin pour travaux de fondation",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def validated_reservation(sample_ressource: Ressource) -> Reservation:
    """Réservation validée."""
    return Reservation(
        id=2,
        ressource_id=sample_ressource.id,
        chantier_id=100,
        demandeur_id=10,
        date_reservation=date.today(),
        heure_debut=time(14, 0),
        heure_fin=time(17, 0),
        statut=StatutReservation.VALIDEE,
        valideur_id=5,
        validated_at=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_ressource_repository() -> Mock:
    """Mock du repository Ressource."""
    return Mock(spec=RessourceRepository)


@pytest.fixture
def mock_reservation_repository() -> Mock:
    """Mock du repository Reservation."""
    return Mock(spec=ReservationRepository)


@pytest.fixture
def mock_event_bus() -> Mock:
    """Mock de l'EventBus."""
    return Mock(spec=EventBus)


@pytest.fixture
def plage_matin() -> PlageHoraire:
    """Plage horaire du matin."""
    return PlageHoraire(heure_debut=time(8, 0), heure_fin=time(12, 0))


@pytest.fixture
def plage_apres_midi() -> PlageHoraire:
    """Plage horaire de l'après-midi."""
    return PlageHoraire(heure_debut=time(14, 0), heure_fin=time(18, 0))
