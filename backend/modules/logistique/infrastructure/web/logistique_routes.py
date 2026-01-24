"""Routes FastAPI pour le module Logistique.

CDC Section 11 - LOG-01 a LOG-18.
"""
from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from shared.infrastructure.web.dependencies import get_current_user_id, get_current_user_role

from .dependencies import (
    # Ressource use cases
    get_create_ressource_use_case,
    get_ressource_use_case,
    get_list_ressources_use_case,
    get_update_ressource_use_case,
    get_delete_ressource_use_case,
    get_activate_ressource_use_case,
    # Reservation use cases
    get_create_reservation_use_case,
    get_reservation_use_case,
    get_list_reservations_use_case,
    get_validate_reservation_use_case,
    get_refuse_reservation_use_case,
    get_cancel_reservation_use_case,
    get_planning_ressource_use_case,
    get_pending_reservations_use_case,
    get_check_conflits_use_case,
)
from ...application.use_cases import (
    CreateRessourceUseCase,
    GetRessourceUseCase,
    ListRessourcesUseCase,
    UpdateRessourceUseCase,
    DeleteRessourceUseCase,
    ActivateRessourceUseCase,
    CreateReservationUseCase,
    GetReservationUseCase,
    ListReservationsUseCase,
    ValidateReservationUseCase,
    RefuseReservationUseCase,
    CancelReservationUseCase,
    GetPlanningRessourceUseCase,
    GetPendingReservationsUseCase,
    CheckConflitsUseCase,
    RessourceNotFoundError,
    RessourceCodeAlreadyExistsError,
    AccessDeniedError,
    ReservationNotFoundError,
    ConflitReservationError,
    InvalidStatusTransitionError,
)
from ...application.dtos import (
    CreateRessourceDTO,
    UpdateRessourceDTO,
    CreateReservationDTO,
    ValidateReservationDTO,
    RefuseReservationDTO,
    ReservationFiltersDTO,
)


router = APIRouter(prefix="/logistique", tags=["logistique"])


# ----- Schemas Pydantic -----

class RessourceCreateSchema(BaseModel):
    """Schema pour la creation d'une ressource."""
    code: str = Field(..., min_length=1, max_length=20)
    nom: str = Field(..., min_length=1, max_length=255)
    type_ressource: str = Field(..., description="levage, terrassement, vehicule, outillage, equipement")
    description: Optional[str] = None
    photo_url: Optional[str] = None
    couleur: str = "#3498DB"
    plage_horaire_debut: str = "08:00"
    plage_horaire_fin: str = "18:00"
    validation_requise: bool = True


class RessourceUpdateSchema(BaseModel):
    """Schema pour la mise a jour d'une ressource."""
    nom: Optional[str] = Field(None, min_length=1, max_length=255)
    type_ressource: Optional[str] = None
    description: Optional[str] = None
    photo_url: Optional[str] = None
    couleur: Optional[str] = None
    plage_horaire_debut: Optional[str] = None
    plage_horaire_fin: Optional[str] = None
    validation_requise: Optional[bool] = None


class ActivateSchema(BaseModel):
    """Schema pour activer/desactiver une ressource."""
    is_active: bool


class ReservationCreateSchema(BaseModel):
    """Schema pour la creation d'une reservation."""
    ressource_id: int
    chantier_id: int
    date_debut: date
    date_fin: date
    heure_debut: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    heure_fin: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    note: Optional[str] = None


class RefuseSchema(BaseModel):
    """Schema pour le refus d'une reservation."""
    motif: Optional[str] = None


# ----- Routes Ressources -----

@router.post("/ressources", status_code=status.HTTP_201_CREATED)
async def create_ressource(
    data: RessourceCreateSchema,
    user_role: str = Depends(get_current_user_role),
    use_case: CreateRessourceUseCase = Depends(get_create_ressource_use_case),
):
    """Cree une nouvelle ressource (LOG-01).

    Seuls les administrateurs peuvent creer des ressources.
    """
    try:
        dto = CreateRessourceDTO(
            code=data.code,
            nom=data.nom,
            type_ressource=data.type_ressource,
            description=data.description,
            photo_url=data.photo_url,
            couleur=data.couleur,
            plage_horaire_debut=data.plage_horaire_debut,
            plage_horaire_fin=data.plage_horaire_fin,
            validation_requise=data.validation_requise,
        )
        result = use_case.execute(dto, user_role)
        return result
    except AccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RessourceCodeAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/ressources")
async def list_ressources(
    type_ressource: Optional[str] = None,
    is_active: Optional[bool] = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    use_case: ListRessourcesUseCase = Depends(get_list_ressources_use_case),
):
    """Liste les ressources."""
    return use_case.execute(
        type_ressource=type_ressource,
        is_active=is_active,
        skip=skip,
        limit=limit,
    )


@router.get("/ressources/{ressource_id}")
async def get_ressource(
    ressource_id: int,
    use_case: GetRessourceUseCase = Depends(get_ressource_use_case),
):
    """Obtient une ressource par ID (LOG-02)."""
    try:
        return use_case.execute(ressource_id)
    except RessourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/ressources/{ressource_id}")
async def update_ressource(
    ressource_id: int,
    data: RessourceUpdateSchema,
    user_role: str = Depends(get_current_user_role),
    use_case: UpdateRessourceUseCase = Depends(get_update_ressource_use_case),
):
    """Met a jour une ressource."""
    try:
        dto = UpdateRessourceDTO(
            id=ressource_id,
            nom=data.nom,
            type_ressource=data.type_ressource,
            description=data.description,
            photo_url=data.photo_url,
            couleur=data.couleur,
            plage_horaire_debut=data.plage_horaire_debut,
            plage_horaire_fin=data.plage_horaire_fin,
            validation_requise=data.validation_requise,
        )
        return use_case.execute(dto, user_role)
    except AccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RessourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/ressources/{ressource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ressource(
    ressource_id: int,
    user_role: str = Depends(get_current_user_role),
    use_case: DeleteRessourceUseCase = Depends(get_delete_ressource_use_case),
):
    """Supprime une ressource (soft delete)."""
    try:
        use_case.execute(ressource_id, user_role)
    except AccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RessourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/ressources/{ressource_id}/activate")
async def activate_ressource(
    ressource_id: int,
    data: ActivateSchema,
    user_role: str = Depends(get_current_user_role),
    use_case: ActivateRessourceUseCase = Depends(get_activate_ressource_use_case),
):
    """Active ou desactive une ressource."""
    try:
        return use_case.execute(ressource_id, data.is_active, user_role)
    except AccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RessourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ----- Routes Reservations -----

@router.post("/reservations", status_code=status.HTTP_201_CREATED)
async def create_reservation(
    data: ReservationCreateSchema,
    user_id: int = Depends(get_current_user_id),
    use_case: CreateReservationUseCase = Depends(get_create_reservation_use_case),
):
    """Cree une nouvelle reservation (LOG-07)."""
    try:
        dto = CreateReservationDTO(
            ressource_id=data.ressource_id,
            chantier_id=data.chantier_id,
            demandeur_id=user_id,
            date_debut=data.date_debut,
            date_fin=data.date_fin,
            heure_debut=data.heure_debut,
            heure_fin=data.heure_fin,
            note=data.note,
        )
        return use_case.execute(dto)
    except RessourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflitReservationError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": str(e), "conflits": e.conflits},
        )


@router.get("/reservations")
async def list_reservations(
    ressource_id: Optional[int] = None,
    chantier_id: Optional[int] = None,
    demandeur_id: Optional[int] = None,
    statut: Optional[str] = None,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    use_case: ListReservationsUseCase = Depends(get_list_reservations_use_case),
):
    """Liste les reservations."""
    filters = ReservationFiltersDTO(
        ressource_id=ressource_id,
        chantier_id=chantier_id,
        demandeur_id=demandeur_id,
        statut=statut,
        date_debut=date_debut,
        date_fin=date_fin,
        skip=skip,
        limit=limit,
    )
    return use_case.execute(filters)


@router.get("/reservations/pending")
async def get_pending_reservations(
    ressource_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    use_case: GetPendingReservationsUseCase = Depends(get_pending_reservations_use_case),
):
    """Liste les reservations en attente de validation."""
    return use_case.execute(ressource_id=ressource_id, skip=skip, limit=limit)


@router.get("/reservations/{reservation_id}")
async def get_reservation(
    reservation_id: int,
    use_case: GetReservationUseCase = Depends(get_reservation_use_case),
):
    """Obtient une reservation par ID."""
    try:
        return use_case.execute(reservation_id)
    except ReservationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/reservations/{reservation_id}/validate")
async def validate_reservation(
    reservation_id: int,
    user_id: int = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    use_case: ValidateReservationUseCase = Depends(get_validate_reservation_use_case),
):
    """Valide une reservation (LOG-11)."""
    try:
        dto = ValidateReservationDTO(
            reservation_id=reservation_id,
            valideur_id=user_id,
        )
        return use_case.execute(dto, user_role)
    except AccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ReservationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidStatusTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/reservations/{reservation_id}/refuse")
async def refuse_reservation(
    reservation_id: int,
    data: RefuseSchema,
    user_id: int = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
    use_case: RefuseReservationUseCase = Depends(get_refuse_reservation_use_case),
):
    """Refuse une reservation (LOG-11, LOG-16)."""
    try:
        dto = RefuseReservationDTO(
            reservation_id=reservation_id,
            valideur_id=user_id,
            motif=data.motif,
        )
        return use_case.execute(dto, user_role)
    except AccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ReservationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidStatusTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/reservations/{reservation_id}/cancel")
async def cancel_reservation(
    reservation_id: int,
    user_id: int = Depends(get_current_user_id),
    use_case: CancelReservationUseCase = Depends(get_cancel_reservation_use_case),
):
    """Annule une reservation."""
    try:
        return use_case.execute(reservation_id, user_id)
    except AccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ReservationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidStatusTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/ressources/{ressource_id}/planning")
async def get_ressource_planning(
    ressource_id: int,
    semaine_debut: date = Query(..., description="Date du lundi de la semaine"),
    use_case: GetPlanningRessourceUseCase = Depends(get_planning_ressource_use_case),
):
    """Obtient le planning d'une ressource pour une semaine (LOG-03)."""
    try:
        return use_case.execute(ressource_id, semaine_debut)
    except RessourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/reservations/check-conflits")
async def check_conflits(
    data: ReservationCreateSchema,
    user_id: int = Depends(get_current_user_id),
    use_case: CheckConflitsUseCase = Depends(get_check_conflits_use_case),
):
    """Verifie les conflits avant creation (LOG-17)."""
    dto = CreateReservationDTO(
        ressource_id=data.ressource_id,
        chantier_id=data.chantier_id,
        demandeur_id=user_id,
        date_debut=data.date_debut,
        date_fin=data.date_fin,
        heure_debut=data.heure_debut,
        heure_fin=data.heure_fin,
        note=data.note,
    )
    result = use_case.execute(dto)
    if result:
        return {"has_conflict": True, "conflict": result}
    return {"has_conflict": False}
