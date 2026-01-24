"""Mappers pour convertir les requêtes HTTP en DTOs.

M14: Extraction des helpers de mapping request → DTO.
Réduit la duplication dans les routes.
"""

from typing import Optional
from datetime import date, time

from ...application.dtos import (
    RessourceCreateDTO,
    RessourceUpdateDTO,
    ReservationCreateDTO,
    ReservationUpdateDTO,
)
from ...domain.value_objects import CategorieRessource


def map_ressource_create_request(
    nom: str,
    code: str,
    categorie: CategorieRessource,
    photo_url: Optional[str] = None,
    couleur: str = "#3B82F6",
    heure_debut_defaut: time = time(8, 0),
    heure_fin_defaut: time = time(18, 0),
    validation_requise: Optional[bool] = None,
    description: Optional[str] = None,
) -> RessourceCreateDTO:
    """Convertit une requête de création de ressource en DTO.

    Args:
        nom: Nom de la ressource
        code: Code unique de la ressource
        categorie: Catégorie de la ressource
        photo_url: URL de la photo (optionnel)
        couleur: Couleur hexadécimale (défaut: #3B82F6)
        heure_debut_defaut: Heure de début par défaut
        heure_fin_defaut: Heure de fin par défaut
        validation_requise: Nécessite validation N+1 (optionnel)
        description: Description de la ressource (optionnel)

    Returns:
        RessourceCreateDTO prêt à être utilisé par le use case
    """
    return RessourceCreateDTO(
        nom=nom,
        code=code,
        categorie=categorie,
        photo_url=photo_url,
        couleur=couleur,
        heure_debut_defaut=heure_debut_defaut,
        heure_fin_defaut=heure_fin_defaut,
        validation_requise=validation_requise,
        description=description,
    )


def map_ressource_update_request(
    nom: Optional[str] = None,
    code: Optional[str] = None,
    categorie: Optional[CategorieRessource] = None,
    photo_url: Optional[str] = None,
    couleur: Optional[str] = None,
    heure_debut_defaut: Optional[time] = None,
    heure_fin_defaut: Optional[time] = None,
    validation_requise: Optional[bool] = None,
    actif: Optional[bool] = None,
    description: Optional[str] = None,
) -> RessourceUpdateDTO:
    """Convertit une requête de mise à jour de ressource en DTO.

    Args:
        nom: Nouveau nom (optionnel)
        code: Nouveau code (optionnel)
        categorie: Nouvelle catégorie (optionnel)
        photo_url: Nouvelle URL photo (optionnel)
        couleur: Nouvelle couleur (optionnel)
        heure_debut_defaut: Nouvelle heure début (optionnel)
        heure_fin_defaut: Nouvelle heure fin (optionnel)
        validation_requise: Nouveau statut validation (optionnel)
        actif: Nouveau statut actif (optionnel)
        description: Nouvelle description (optionnel)

    Returns:
        RessourceUpdateDTO prêt à être utilisé par le use case
    """
    return RessourceUpdateDTO(
        nom=nom,
        code=code,
        categorie=categorie,
        photo_url=photo_url,
        couleur=couleur,
        heure_debut_defaut=heure_debut_defaut,
        heure_fin_defaut=heure_fin_defaut,
        validation_requise=validation_requise,
        actif=actif,
        description=description,
    )


def map_reservation_create_request(
    ressource_id: int,
    chantier_id: int,
    date_reservation: date,
    heure_debut: time,
    heure_fin: time,
    commentaire: Optional[str] = None,
) -> ReservationCreateDTO:
    """Convertit une requête de création de réservation en DTO.

    Args:
        ressource_id: ID de la ressource à réserver
        chantier_id: ID du chantier associé
        date_reservation: Date de la réservation
        heure_debut: Heure de début
        heure_fin: Heure de fin
        commentaire: Commentaire (optionnel)

    Returns:
        ReservationCreateDTO prêt à être utilisé par le use case
    """
    return ReservationCreateDTO(
        ressource_id=ressource_id,
        chantier_id=chantier_id,
        date_reservation=date_reservation,
        heure_debut=heure_debut,
        heure_fin=heure_fin,
        commentaire=commentaire,
    )


def map_reservation_update_request(
    date_reservation: Optional[date] = None,
    heure_debut: Optional[time] = None,
    heure_fin: Optional[time] = None,
    commentaire: Optional[str] = None,
) -> ReservationUpdateDTO:
    """Convertit une requête de mise à jour de réservation en DTO.

    Args:
        date_reservation: Nouvelle date (optionnel)
        heure_debut: Nouvelle heure début (optionnel)
        heure_fin: Nouvelle heure fin (optionnel)
        commentaire: Nouveau commentaire (optionnel)

    Returns:
        ReservationUpdateDTO prêt à être utilisé par le use case
    """
    return ReservationUpdateDTO(
        date_reservation=date_reservation,
        heure_debut=heure_debut,
        heure_fin=heure_fin,
        commentaire=commentaire,
    )
