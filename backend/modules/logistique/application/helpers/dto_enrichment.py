"""Helpers pour enrichir les DTOs avec des données associées.

M15: Extraction des helpers d'enrichissement DTO.
Réduit la duplication dans les use cases.
"""

from typing import Dict, List, Optional

from ..dtos import ReservationDTO
from ...domain.entities import Reservation, Ressource
from ...domain.repositories import RessourceRepository


def enrich_reservation_dto(
    reservation: Reservation,
    ressource: Optional[Ressource] = None,
) -> ReservationDTO:
    """Enrichit un DTO de réservation avec les infos de la ressource.

    Args:
        reservation: L'entité Reservation
        ressource: L'entité Ressource associée (optionnel)

    Returns:
        ReservationDTO enrichi avec les infos ressource
    """
    return ReservationDTO.from_entity(
        reservation,
        ressource_nom=ressource.nom if ressource else None,
        ressource_code=ressource.code if ressource else None,
        ressource_couleur=ressource.couleur if ressource else None,
    )


def enrich_reservations_list(
    reservations: List[Reservation],
    ressource_repository: RessourceRepository,
) -> List[ReservationDTO]:
    """Enrichit une liste de réservations avec les infos des ressources.

    Utilise un cache pour éviter les requêtes multiples pour la même ressource.

    Args:
        reservations: Liste des réservations à enrichir
        ressource_repository: Repository pour récupérer les ressources

    Returns:
        Liste de ReservationDTO enrichis
    """
    # Cache pour éviter les requêtes multiples
    ressources_cache: Dict[int, Optional[Ressource]] = {}
    items: List[ReservationDTO] = []

    for reservation in reservations:
        # Récupérer la ressource du cache ou de la DB
        if reservation.ressource_id not in ressources_cache:
            ressources_cache[reservation.ressource_id] = ressource_repository.find_by_id(
                reservation.ressource_id
            )

        ressource = ressources_cache[reservation.ressource_id]
        items.append(enrich_reservation_dto(reservation, ressource))

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
