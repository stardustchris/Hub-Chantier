"""Helpers pour enrichir les DTOs avec des données associées.

M15: Extraction des helpers d'enrichissement DTO.
Réduit la duplication dans les use cases.
"""

from typing import Dict, List, Optional

from ..dtos import ReservationDTO
from ...domain.entities import Reservation, Ressource
from ...domain.repositories import RessourceRepository
from ....auth.domain.repositories import UserRepository
from ....auth.domain.entities import User


def enrich_reservation_dto(
    reservation: Reservation,
    ressource: Optional[Ressource] = None,
    demandeur: Optional[User] = None,
    valideur: Optional[User] = None,
) -> ReservationDTO:
    """Enrichit un DTO de réservation avec les infos de la ressource et des utilisateurs.

    Args:
        reservation: L'entité Reservation
        ressource: L'entité Ressource associée (optionnel)
        demandeur: L'utilisateur demandeur (optionnel)
        valideur: L'utilisateur valideur (optionnel)

    Returns:
        ReservationDTO enrichi avec les infos ressource et utilisateurs
    """
    demandeur_nom = None
    if demandeur:
        demandeur_nom = f"{demandeur.prenom} {demandeur.nom}"

    valideur_nom = None
    if valideur:
        valideur_nom = f"{valideur.prenom} {valideur.nom}"

    return ReservationDTO.from_entity(
        reservation,
        ressource_nom=ressource.nom if ressource else None,
        ressource_code=ressource.code if ressource else None,
        ressource_couleur=ressource.couleur if ressource else None,
        demandeur_nom=demandeur_nom,
        valideur_nom=valideur_nom,
    )


def enrich_reservations_list(
    reservations: List[Reservation],
    ressource_repository: RessourceRepository,
    user_repository: Optional[UserRepository] = None,
) -> List[ReservationDTO]:
    """Enrichit une liste de réservations avec les infos des ressources et utilisateurs.

    Utilise des caches pour éviter les requêtes multiples pour les mêmes entités.

    Args:
        reservations: Liste des réservations à enrichir
        ressource_repository: Repository pour récupérer les ressources
        user_repository: Repository pour récupérer les utilisateurs (optionnel)

    Returns:
        Liste de ReservationDTO enrichis
    """
    # Caches pour éviter les requêtes multiples
    ressources_cache: Dict[int, Optional[Ressource]] = {}
    users_cache: Dict[int, Optional[User]] = {}
    items: List[ReservationDTO] = []

    for reservation in reservations:
        # Récupérer la ressource du cache ou de la DB
        if reservation.ressource_id not in ressources_cache:
            ressources_cache[reservation.ressource_id] = ressource_repository.find_by_id(
                reservation.ressource_id
            )
        ressource = ressources_cache[reservation.ressource_id]

        # Récupérer les utilisateurs si repository fourni
        demandeur = None
        valideur = None
        if user_repository:
            if reservation.demandeur_id not in users_cache:
                users_cache[reservation.demandeur_id] = user_repository.find_by_id(
                    reservation.demandeur_id
                )
            demandeur = users_cache[reservation.demandeur_id]

            if reservation.valideur_id and reservation.valideur_id not in users_cache:
                users_cache[reservation.valideur_id] = user_repository.find_by_id(
                    reservation.valideur_id
                )
            if reservation.valideur_id:
                valideur = users_cache[reservation.valideur_id]

        items.append(enrich_reservation_dto(reservation, ressource, demandeur, valideur))

    return items


def get_ressource_info(
    ressource_id: int,
    ressource_repository: RessourceRepository,
) -> Optional[Ressource]:
    """Récupère les informations d'une ressource.

    Helper simple pour récupérer une ressource de façon sécurisée.

    Args:
        ressource_id: ID de la ressource
        ressource_repository: Repository pour récupérer la ressource

    Returns:
        L'entité Ressource ou None si non trouvée
    """
    return ressource_repository.find_by_id(ressource_id)
