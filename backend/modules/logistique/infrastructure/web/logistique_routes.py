"""Routes FastAPI pour le module Logistique.

LOG-01 à LOG-18: API REST complète pour la gestion du matériel et réservations.
"""

from datetime import date, time
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from modules.auth.infrastructure.web.dependencies import get_current_user_id
from shared.infrastructure.web import (
    require_admin,
    require_conducteur_or_admin,
    get_current_user_role,
)

from ...domain.value_objects import CategorieRessource, StatutReservation
from ...domain.entities.reservation import (
    ReservationConflitError,
    TransitionStatutInvalideError,
)
from ...application.use_cases.ressource_use_cases import (
    RessourceNotFoundError,
    RessourceCodeExistsError,
)
from ...application.use_cases.reservation_use_cases import (
    ReservationNotFoundError,
    RessourceInactiveError,
)
from ...application.dtos import (
    RessourceCreateDTO,
    RessourceUpdateDTO,
    ReservationCreateDTO,
    ReservationUpdateDTO,
)
from .dependencies import (
    get_create_ressource_use_case,
    get_update_ressource_use_case,
    get_delete_ressource_use_case,
    get_get_ressource_use_case,
    get_list_ressources_use_case,
    get_create_reservation_use_case,
    get_update_reservation_use_case,
    get_valider_reservation_use_case,
    get_refuser_reservation_use_case,
    get_annuler_reservation_use_case,
    get_get_reservation_use_case,
    get_planning_ressource_use_case,
    get_historique_ressource_use_case,
    get_list_reservations_en_attente_use_case,
)


router = APIRouter(prefix="/logistique", tags=["logistique"])


# =============================================================================
# Schemas Pydantic
# =============================================================================


class RessourceCreateRequest(BaseModel):
    """Requête de création de ressource."""

    nom: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=20, pattern=r"^[A-Z0-9\-]+$")
    categorie: CategorieRessource
    photo_url: Optional[str] = Field(None, max_length=500)
    couleur: str = Field(default="#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")
    heure_debut_defaut: time = Field(default=time(8, 0))
    heure_fin_defaut: time = Field(default=time(18, 0))
    validation_requise: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=2000)


class RessourceUpdateRequest(BaseModel):
    """Requête de mise à jour de ressource."""

    nom: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, min_length=1, max_length=20, pattern=r"^[A-Z0-9\-]+$")
    categorie: Optional[CategorieRessource] = None
    photo_url: Optional[str] = Field(None, max_length=500)
    couleur: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    heure_debut_defaut: Optional[time] = None
    heure_fin_defaut: Optional[time] = None
    validation_requise: Optional[bool] = None
    actif: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=2000)


class ReservationCreateRequest(BaseModel):
    """Requête de création de réservation."""

    ressource_id: int = Field(..., gt=0)
    chantier_id: int = Field(..., gt=0)
    date_reservation: date
    heure_debut: time
    heure_fin: time
    commentaire: Optional[str] = Field(None, max_length=1000)


class ReservationUpdateRequest(BaseModel):
    """Requête de mise à jour de réservation."""

    date_reservation: Optional[date] = None
    heure_debut: Optional[time] = None
    heure_fin: Optional[time] = None
    commentaire: Optional[str] = Field(None, max_length=1000)


class RefuserReservationRequest(BaseModel):
    """Requête de refus de réservation."""

    motif: Optional[str] = Field(None, max_length=1000)


# =============================================================================
# Routes Ressources (LOG-01, LOG-02)
# =============================================================================


@router.post("/ressources", status_code=status.HTTP_201_CREATED)
async def create_ressource(
    request: RessourceCreateRequest,
    current_user_id: int = Depends(require_admin),
    use_case=Depends(get_create_ressource_use_case),
):
    """Crée une nouvelle ressource.

    LOG-01: Référentiel matériel - Admin uniquement.
    """
    try:
        dto = RessourceCreateDTO(
            nom=request.nom,
            code=request.code,
            categorie=request.categorie,
            photo_url=request.photo_url,
            couleur=request.couleur,
            heure_debut_defaut=request.heure_debut_defaut,
            heure_fin_defaut=request.heure_fin_defaut,
            validation_requise=request.validation_requise,
            description=request.description,
        )
        result = use_case.execute(dto, current_user_id)
        return result
    except RessourceCodeExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ressources")
async def list_ressources(
    categorie: Optional[CategorieRessource] = None,
    actif_seulement: bool = True,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_list_ressources_use_case),
):
    """Liste les ressources avec filtres.

    Accessible à tous les utilisateurs authentifiés.
    """
    return use_case.execute(
        categorie=categorie,
        actif_seulement=actif_seulement,
        limit=limit,
        offset=offset,
    )


@router.get("/ressources/{ressource_id}")
async def get_ressource(
    ressource_id: int,
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_get_ressource_use_case),
):
    """Récupère une ressource par son ID."""
    try:
        return use_case.execute(ressource_id)
    except RessourceNotFoundError:
        raise HTTPException(status_code=404, detail="Ressource non trouvée")


@router.put("/ressources/{ressource_id}")
async def update_ressource(
    ressource_id: int,
    request: RessourceUpdateRequest,
    current_user_id: int = Depends(require_admin),
    use_case=Depends(get_update_ressource_use_case),
):
    """Met à jour une ressource.

    LOG-01: Admin uniquement.
    """
    try:
        dto = RessourceUpdateDTO(
            nom=request.nom,
            code=request.code,
            categorie=request.categorie,
            photo_url=request.photo_url,
            couleur=request.couleur,
            heure_debut_defaut=request.heure_debut_defaut,
            heure_fin_defaut=request.heure_fin_defaut,
            validation_requise=request.validation_requise,
            actif=request.actif,
            description=request.description,
        )
        return use_case.execute(ressource_id, dto, current_user_id)
    except RessourceNotFoundError:
        raise HTTPException(status_code=404, detail="Ressource non trouvée")
    except RessourceCodeExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/ressources/{ressource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ressource(
    ressource_id: int,
    current_user_id: int = Depends(require_admin),
    use_case=Depends(get_delete_ressource_use_case),
):
    """Supprime une ressource.

    LOG-01: Admin uniquement.
    """
    try:
        use_case.execute(ressource_id, current_user_id)
    except RessourceNotFoundError:
        raise HTTPException(status_code=404, detail="Ressource non trouvée")


# =============================================================================
# Routes Réservations (LOG-07 à LOG-18)
# =============================================================================


@router.post("/reservations", status_code=status.HTTP_201_CREATED)
async def create_reservation(
    request: ReservationCreateRequest,
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_create_reservation_use_case),
):
    """Crée une nouvelle réservation.

    LOG-07: Demande de réservation - Depuis mobile ou web.
    LOG-08: Sélection chantier obligatoire.
    LOG-09: Sélection créneau.
    """
    try:
        dto = ReservationCreateDTO(
            ressource_id=request.ressource_id,
            chantier_id=request.chantier_id,
            date_reservation=request.date_reservation,
            heure_debut=request.heure_debut,
            heure_fin=request.heure_fin,
            commentaire=request.commentaire,
        )
        return use_case.execute(dto, current_user_id)
    except RessourceNotFoundError:
        raise HTTPException(status_code=404, detail="Ressource non trouvée")
    except RessourceInactiveError:
        raise HTTPException(status_code=400, detail="Cette ressource n'est pas disponible")
    except ReservationConflitError as e:
        raise HTTPException(
            status_code=409,
            detail=f"Conflit de réservation: {str(e)}",
        )


@router.get("/reservations/en-attente")
async def list_reservations_en_attente(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    current_user_id: int = Depends(require_conducteur_or_admin),
    use_case=Depends(get_list_reservations_en_attente_use_case),
):
    """Liste les réservations en attente de validation.

    LOG-11: Workflow validation - Liste des demandes à valider.
    Accessible aux chefs de chantier, conducteurs et admins.
    """
    return use_case.execute(limit=limit, offset=offset)


@router.get("/reservations/{reservation_id}")
async def get_reservation(
    reservation_id: int,
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    use_case=Depends(get_get_reservation_use_case),
):
    """Récupère une réservation par son ID.

    Accessible au demandeur de la réservation ou aux conducteurs/admins.
    """
    try:
        reservation = use_case.execute(reservation_id)
        # SEC-001: Vérifier que l'utilisateur est autorisé
        is_owner = reservation.demandeur_id == current_user_id
        is_privileged = current_user_role in ("admin", "conducteur", "chef_chantier")
        if not is_owner and not is_privileged:
            raise HTTPException(
                status_code=403,
                detail="Vous n'êtes pas autorisé à consulter cette réservation",
            )
        return reservation
    except ReservationNotFoundError:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")


@router.put("/reservations/{reservation_id}")
async def update_reservation(
    reservation_id: int,
    request: ReservationUpdateRequest,
    current_user_id: int = Depends(get_current_user_id),
    get_use_case=Depends(get_get_reservation_use_case),
    use_case=Depends(get_update_reservation_use_case),
):
    """Met à jour une réservation.

    Seules les réservations en attente peuvent être modifiées.
    Seul le demandeur peut modifier sa réservation.
    """
    try:
        # SEC-002: Vérifier que l'utilisateur est le propriétaire
        existing = get_use_case.execute(reservation_id)
        if existing.demandeur_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="Seul le demandeur peut modifier sa réservation",
            )

        dto = ReservationUpdateDTO(
            date_reservation=request.date_reservation,
            heure_debut=request.heure_debut,
            heure_fin=request.heure_fin,
            commentaire=request.commentaire,
        )
        return use_case.execute(reservation_id, dto, current_user_id)
    except ReservationNotFoundError:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ReservationConflitError as e:
        raise HTTPException(status_code=409, detail=f"Conflit: {str(e)}")


@router.post("/reservations/{reservation_id}/valider")
async def valider_reservation(
    reservation_id: int,
    current_user_id: int = Depends(require_conducteur_or_admin),
    use_case=Depends(get_valider_reservation_use_case),
):
    """Valide une réservation.

    LOG-11: Workflow validation - Chef valide → Confirmée 🟢.
    Accessible aux chefs de chantier, conducteurs et admins.
    """
    try:
        return use_case.execute(reservation_id, current_user_id)
    except ReservationNotFoundError:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")
    except TransitionStatutInvalideError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reservations/{reservation_id}/refuser")
async def refuser_reservation(
    reservation_id: int,
    request: RefuserReservationRequest,
    current_user_id: int = Depends(require_conducteur_or_admin),
    use_case=Depends(get_refuser_reservation_use_case),
):
    """Refuse une réservation.

    LOG-16: Motif de refus - Champ texte optionnel.
    Accessible aux chefs de chantier, conducteurs et admins.
    """
    try:
        return use_case.execute(reservation_id, current_user_id, request.motif)
    except ReservationNotFoundError:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")
    except TransitionStatutInvalideError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reservations/{reservation_id}/annuler")
async def annuler_reservation(
    reservation_id: int,
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    get_use_case=Depends(get_get_reservation_use_case),
    use_case=Depends(get_annuler_reservation_use_case),
):
    """Annule une réservation.

    Accessible au demandeur de la réservation ou aux conducteurs/admins.
    """
    try:
        # SEC-003: Vérifier que l'utilisateur est autorisé
        existing = get_use_case.execute(reservation_id)
        is_owner = existing.demandeur_id == current_user_id
        is_privileged = current_user_role in ("admin", "conducteur", "chef_chantier")
        if not is_owner and not is_privileged:
            raise HTTPException(
                status_code=403,
                detail="Vous n'êtes pas autorisé à annuler cette réservation",
            )

        return use_case.execute(reservation_id, current_user_id)
    except ReservationNotFoundError:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")
    except TransitionStatutInvalideError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# Routes Planning (LOG-03, LOG-04, LOG-18)
# =============================================================================


@router.get("/ressources/{ressource_id}/planning")
async def get_planning_ressource(
    ressource_id: int,
    date_debut: date,
    date_fin: Optional[date] = None,
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_planning_ressource_use_case),
):
    """Récupère le planning d'une ressource.

    LOG-03: Planning par ressource - Vue calendrier hebdomadaire 7 jours.
    LOG-04: Navigation semaine.
    """
    try:
        return use_case.execute(
            ressource_id=ressource_id,
            date_debut=date_debut,
            date_fin=date_fin,
        )
    except RessourceNotFoundError:
        raise HTTPException(status_code=404, detail="Ressource non trouvée")


@router.get("/ressources/{ressource_id}/historique")
async def get_historique_ressource(
    ressource_id: int,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_historique_ressource_use_case),
):
    """Récupère l'historique des réservations d'une ressource.

    LOG-18: Historique par ressource - Journal complet des réservations.
    """
    try:
        return use_case.execute(
            ressource_id=ressource_id,
            limit=limit,
            offset=offset,
        )
    except RessourceNotFoundError:
        raise HTTPException(status_code=404, detail="Ressource non trouvée")
