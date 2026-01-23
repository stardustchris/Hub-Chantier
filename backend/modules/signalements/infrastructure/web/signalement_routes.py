"""Routes FastAPI pour le module Signalements."""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from .dependencies import get_signalement_controller, get_current_user
from ...adapters.controllers import SignalementController
from ...application.dtos import (
    SignalementCreateDTO,
    SignalementUpdateDTO,
    SignalementSearchDTO,
    ReponseCreateDTO,
    ReponseUpdateDTO,
)
from ...application.use_cases import (
    SignalementNotFoundError,
    ReponseNotFoundError,
    InvalidStatusTransitionError,
    AccessDeniedError,
)


router = APIRouter(prefix="/signalements", tags=["Signalements"])


# ============ Pydantic Models ============

class SignalementCreateRequest(BaseModel):
    """Request pour créer un signalement (SIG-01)."""

    chantier_id: int
    titre: str
    description: str
    priorite: str = "moyenne"
    assigne_a: Optional[int] = None
    date_resolution_souhaitee: Optional[datetime] = None
    photo_url: Optional[str] = None
    localisation: Optional[str] = None


class SignalementUpdateRequest(BaseModel):
    """Request pour mettre à jour un signalement (SIG-04)."""

    titre: Optional[str] = None
    description: Optional[str] = None
    priorite: Optional[str] = None
    assigne_a: Optional[int] = None
    date_resolution_souhaitee: Optional[datetime] = None
    photo_url: Optional[str] = None
    localisation: Optional[str] = None


class MarquerTraiteRequest(BaseModel):
    """Request pour marquer un signalement comme traité (SIG-08)."""

    commentaire: str


class ReponseCreateRequest(BaseModel):
    """Request pour créer une réponse (SIG-07)."""

    contenu: str
    photo_url: Optional[str] = None
    est_resolution: bool = False


class ReponseUpdateRequest(BaseModel):
    """Request pour mettre à jour une réponse."""

    contenu: Optional[str] = None
    photo_url: Optional[str] = None


class SignalementResponse(BaseModel):
    """Response pour un signalement."""

    id: int
    chantier_id: int
    titre: str
    description: str
    priorite: str
    priorite_label: str
    priorite_couleur: str
    statut: str
    statut_label: str
    statut_couleur: str
    cree_par: int
    cree_par_nom: Optional[str]
    assigne_a: Optional[int]
    assigne_a_nom: Optional[str]
    date_resolution_souhaitee: Optional[datetime]
    date_traitement: Optional[datetime]
    date_cloture: Optional[datetime]
    commentaire_traitement: Optional[str]
    photo_url: Optional[str]
    localisation: Optional[str]
    created_at: datetime
    updated_at: datetime
    est_en_retard: bool
    temps_restant: Optional[str]
    pourcentage_temps: float
    nb_reponses: int
    nb_escalades: int

    class Config:
        from_attributes = True


class SignalementListResponse(BaseModel):
    """Response pour une liste de signalements."""

    signalements: List[SignalementResponse]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True


class ReponseResponse(BaseModel):
    """Response pour une réponse."""

    id: int
    signalement_id: int
    contenu: str
    auteur_id: int
    auteur_nom: Optional[str]
    photo_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    est_resolution: bool

    class Config:
        from_attributes = True


class ReponseListResponse(BaseModel):
    """Response pour une liste de réponses."""

    reponses: List[ReponseResponse]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True


class SignalementStatsResponse(BaseModel):
    """Response pour les statistiques (SIG-18)."""

    total: int
    par_statut: dict
    par_priorite: dict
    en_retard: int
    traites_cette_semaine: int
    temps_moyen_resolution: Optional[float]
    taux_resolution: float

    class Config:
        from_attributes = True


# ============ SIGNALEMENTS ============

@router.post("", response_model=SignalementResponse, status_code=status.HTTP_201_CREATED)
def create_signalement(
    request: SignalementCreateRequest,
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
    """Crée un nouveau signalement (SIG-01)."""
    try:
        dto = SignalementCreateDTO(
            chantier_id=request.chantier_id,
            titre=request.titre,
            description=request.description,
            cree_par=current_user["id"],
            priorite=request.priorite,
            assigne_a=request.assigne_a,
            date_resolution_souhaitee=request.date_resolution_souhaitee,
            photo_url=request.photo_url,
            localisation=request.localisation,
        )
        return controller.create_signalement(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{signalement_id}", response_model=SignalementResponse)
def get_signalement(
    signalement_id: int,
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
    """Récupère un signalement par son ID (SIG-02)."""
    try:
        return controller.get_signalement(signalement_id)
    except SignalementNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/chantier/{chantier_id}", response_model=SignalementListResponse)
def list_signalements_by_chantier(
    chantier_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    statut: Optional[str] = Query(None),
    priorite: Optional[str] = Query(None),
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
    """Liste les signalements d'un chantier (SIG-03)."""
    return controller.list_signalements(chantier_id, skip, limit, statut, priorite)


@router.get("", response_model=SignalementListResponse)
def search_signalements(
    query: Optional[str] = Query(None),
    chantier_id: Optional[int] = Query(None),
    statut: Optional[str] = Query(None),
    priorite: Optional[str] = Query(None),
    date_debut: Optional[datetime] = Query(None),
    date_fin: Optional[datetime] = Query(None),
    en_retard_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
    """Recherche des signalements avec filtres (SIG-10, SIG-19, SIG-20)."""
    search_dto = SignalementSearchDTO(
        query=query,
        chantier_id=chantier_id,
        statut=statut,
        priorite=priorite,
        date_debut=date_debut,
        date_fin=date_fin,
        en_retard_only=en_retard_only,
        skip=skip,
        limit=limit,
    )
    return controller.search_signalements(search_dto)


@router.put("/{signalement_id}", response_model=SignalementResponse)
def update_signalement(
    signalement_id: int,
    request: SignalementUpdateRequest,
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
    """Met à jour un signalement (SIG-04)."""
    try:
        dto = SignalementUpdateDTO(
            titre=request.titre,
            description=request.description,
            priorite=request.priorite,
            assigne_a=request.assigne_a,
            date_resolution_souhaitee=request.date_resolution_souhaitee,
            photo_url=request.photo_url,
            localisation=request.localisation,
        )
        return controller.update_signalement(
            signalement_id, dto, current_user["id"], current_user["role"]
        )
    except SignalementNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{signalement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_signalement(
    signalement_id: int,
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
    """Supprime un signalement (SIG-05)."""
    try:
        controller.delete_signalement(
            signalement_id, current_user["id"], current_user["role"]
        )
    except SignalementNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{signalement_id}/assigner", response_model=SignalementResponse)
def assigner_signalement(
    signalement_id: int,
    assigne_a: int = Query(...),
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
    """Assigne un signalement à un utilisateur."""
    try:
        return controller.assigner_signalement(
            signalement_id, assigne_a, current_user["role"]
        )
    except SignalementNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{signalement_id}/traiter", response_model=SignalementResponse)
def marquer_traite(
    signalement_id: int,
    request: MarquerTraiteRequest,
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
    """Marque un signalement comme traité (SIG-08)."""
    try:
        return controller.marquer_traite(
            signalement_id, request.commentaire, current_user["role"]
        )
    except SignalementNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStatusTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{signalement_id}/cloturer", response_model=SignalementResponse)
def cloturer_signalement(
    signalement_id: int,
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
    """Clôture un signalement (SIG-09)."""
    try:
        return controller.cloturer_signalement(
            signalement_id, current_user["role"]
        )
    except SignalementNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except InvalidStatusTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{signalement_id}/reouvrir", response_model=SignalementResponse)
def reouvrir_signalement(
    signalement_id: int,
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
    """Réouvre un signalement clôturé."""
    try:
        return controller.reouvrir_signalement(
            signalement_id, current_user["role"]
        )
    except SignalementNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except InvalidStatusTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ STATISTIQUES ============

@router.get("/stats/global", response_model=SignalementStatsResponse)
def get_statistiques(
    chantier_id: Optional[int] = Query(None),
    date_debut: Optional[datetime] = Query(None),
    date_fin: Optional[datetime] = Query(None),
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
    """Récupère les statistiques des signalements (SIG-18)."""
    return controller.get_statistiques(chantier_id, date_debut, date_fin)


@router.get("/alertes/en-retard", response_model=SignalementListResponse)
def get_signalements_en_retard(
    chantier_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
    """Récupère les signalements en retard (SIG-16)."""
    return controller.get_signalements_en_retard(chantier_id, skip, limit)


# ============ REPONSES ============

@router.post("/{signalement_id}/reponses", response_model=ReponseResponse, status_code=status.HTTP_201_CREATED)
def create_reponse(
    signalement_id: int,
    request: ReponseCreateRequest,
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
    """Ajoute une réponse à un signalement (SIG-07)."""
    try:
        dto = ReponseCreateDTO(
            signalement_id=signalement_id,
            contenu=request.contenu,
            auteur_id=current_user["id"],
            photo_url=request.photo_url,
            est_resolution=request.est_resolution,
        )
        return controller.create_reponse(dto)
    except SignalementNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{signalement_id}/reponses", response_model=ReponseListResponse)
def list_reponses(
    signalement_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
    """Liste les réponses d'un signalement."""
    return controller.list_reponses(signalement_id, skip, limit)


@router.put("/reponses/{reponse_id}", response_model=ReponseResponse)
def update_reponse(
    reponse_id: int,
    request: ReponseUpdateRequest,
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
    """Met à jour une réponse."""
    try:
        dto = ReponseUpdateDTO(
            contenu=request.contenu,
            photo_url=request.photo_url,
        )
        return controller.update_reponse(
            reponse_id, dto, current_user["id"], current_user["role"]
        )
    except ReponseNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/reponses/{reponse_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reponse(
    reponse_id: int,
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
    """Supprime une réponse."""
    try:
        controller.delete_reponse(
            reponse_id, current_user["id"], current_user["role"]
        )
    except ReponseNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
