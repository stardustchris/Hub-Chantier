"""Routes FastAPI pour le module Taches - CDC Section 13."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from ...adapters.controllers import TacheController
from ...application import (
    TacheNotFoundError,
    TemplateNotFoundError,
    TemplateAlreadyExistsError,
    FeuilleTacheNotFoundError,
    FeuilleTacheAlreadyExistsError,
)
from .dependencies import get_tache_controller

# Routes pour auth dependency
from backend.modules.auth.infrastructure.web.dependencies import get_current_user_id

router = APIRouter(prefix="/taches", tags=["taches"])
templates_router = APIRouter(prefix="/templates-taches", tags=["templates-taches"])
feuilles_router = APIRouter(prefix="/feuilles-taches", tags=["feuilles-taches"])


# =============================================================================
# Pydantic models for request/response validation
# Selon CDC Section 13 - Gestion des Taches (TAC-01 a TAC-20)
# =============================================================================


class CreateTacheRequest(BaseModel):
    """Requete de creation de tache (TAC-06, TAC-07)."""

    chantier_id: int
    titre: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    date_echeance: Optional[str] = None
    unite_mesure: Optional[str] = None
    quantite_estimee: Optional[float] = None
    heures_estimees: Optional[float] = None


class UpdateTacheRequest(BaseModel):
    """Requete de mise a jour de tache."""

    titre: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    date_echeance: Optional[str] = None
    unite_mesure: Optional[str] = None
    quantite_estimee: Optional[float] = None
    heures_estimees: Optional[float] = None
    statut: Optional[str] = None
    ordre: Optional[int] = None


class CompleteTacheRequest(BaseModel):
    """Requete pour marquer une tache terminee (TAC-13)."""

    terminer: bool = True


class ReorderTacheRequest(BaseModel):
    """Requete pour reordonner une tache (TAC-15)."""

    tache_id: int
    ordre: int


class TacheResponse(BaseModel):
    """Reponse tache complete."""

    id: int
    chantier_id: int
    titre: str
    description: Optional[str]
    parent_id: Optional[int]
    ordre: int
    statut: str
    statut_display: str
    statut_icon: str
    date_echeance: Optional[str]
    unite_mesure: Optional[str]
    unite_mesure_display: Optional[str]
    quantite_estimee: Optional[float]
    quantite_realisee: float
    heures_estimees: Optional[float]
    heures_realisees: float
    progression_heures: float
    progression_quantite: float
    couleur_progression: str
    couleur_hex: str
    est_terminee: bool
    est_en_retard: bool
    a_sous_taches: bool
    nombre_sous_taches: int
    nombre_sous_taches_terminees: int
    template_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    sous_taches: List["TacheResponse"] = []


class TacheListResponse(BaseModel):
    """Reponse liste de taches paginee (TAC-01)."""

    items: List[TacheResponse]
    total: int
    page: int
    size: int
    pages: int


class TacheStatsResponse(BaseModel):
    """Reponse statistiques taches (TAC-20)."""

    chantier_id: int
    total_taches: int
    taches_terminees: int
    taches_en_cours: int
    taches_en_retard: int
    heures_estimees_total: float
    heures_realisees_total: float
    progression_globale: float


# Templates
class SousTacheModeleRequest(BaseModel):
    """Sous-tache pour creation de template."""

    titre: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    ordre: int = 0
    unite_mesure: Optional[str] = None
    heures_estimees_defaut: Optional[float] = None


class CreateTemplateRequest(BaseModel):
    """Requete de creation de template (TAC-04)."""

    nom: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    categorie: Optional[str] = None
    unite_mesure: Optional[str] = None
    heures_estimees_defaut: Optional[float] = None
    sous_taches: List[SousTacheModeleRequest] = []


class ImportTemplateRequest(BaseModel):
    """Requete d'import de template (TAC-05)."""

    template_id: int
    chantier_id: int


class TemplateResponse(BaseModel):
    """Reponse template."""

    id: int
    nom: str
    description: Optional[str]
    categorie: Optional[str]
    unite_mesure: Optional[str]
    unite_mesure_display: Optional[str]
    heures_estimees_defaut: Optional[float]
    nombre_sous_taches: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    sous_taches: List[dict] = []


class TemplateListResponse(BaseModel):
    """Reponse liste de templates."""

    items: List[TemplateResponse]
    total: int
    page: int
    size: int
    pages: int
    categories: List[str] = []


# Feuilles de taches
class CreateFeuilleTacheRequest(BaseModel):
    """Requete de creation de feuille de tache (TAC-18)."""

    tache_id: int
    utilisateur_id: int
    chantier_id: int
    date_travail: str  # Format ISO: YYYY-MM-DD
    heures_travaillees: float = 0.0
    quantite_realisee: float = 0.0
    commentaire: Optional[str] = None


class ValidateFeuilleTacheRequest(BaseModel):
    """Requete de validation de feuille (TAC-19)."""

    valider: bool = True
    motif_rejet: Optional[str] = None


class FeuilleTacheResponse(BaseModel):
    """Reponse feuille de tache."""

    id: int
    tache_id: int
    utilisateur_id: int
    chantier_id: int
    date_travail: str
    heures_travaillees: float
    quantite_realisee: float
    commentaire: Optional[str]
    statut_validation: str
    statut_display: str
    est_validee: bool
    est_en_attente: bool
    est_rejetee: bool
    validateur_id: Optional[int]
    date_validation: Optional[datetime]
    motif_rejet: Optional[str]
    created_at: datetime
    updated_at: datetime


class FeuilleTacheListResponse(BaseModel):
    """Reponse liste de feuilles paginee."""

    items: List[FeuilleTacheResponse]
    total: int
    page: int
    size: int
    pages: int
    total_heures: float = 0.0
    total_quantite: float = 0.0


# =============================================================================
# Routes Taches
# =============================================================================


@router.get("/chantier/{chantier_id}", response_model=TacheListResponse)
def list_taches_by_chantier(
    chantier_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    query: Optional[str] = Query(None, max_length=100, description="Recherche (TAC-14)"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    include_sous_taches: bool = Query(True, description="Inclure sous-taches (TAC-02)"),
    controller: TacheController = Depends(get_tache_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Liste les taches d'un chantier (TAC-01).

    Supporte la structure hierarchique (TAC-02) et la recherche (TAC-14).
    """
    result = controller.list_taches(
        chantier_id=chantier_id,
        query=query,
        statut=statut,
        page=page,
        size=size,
        include_sous_taches=include_sous_taches,
    )
    return result


@router.get("/chantier/{chantier_id}/stats", response_model=TacheStatsResponse)
def get_taches_stats(
    chantier_id: int,
    controller: TacheController = Depends(get_tache_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Obtient les statistiques des taches d'un chantier (TAC-20)."""
    return controller.get_tache_stats(chantier_id)


@router.get("/{tache_id}", response_model=TacheResponse)
def get_tache(
    tache_id: int,
    include_sous_taches: bool = Query(True),
    controller: TacheController = Depends(get_tache_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Recupere une tache par son ID."""
    try:
        return controller.get_tache(tache_id, include_sous_taches)
    except TacheNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("", response_model=TacheResponse, status_code=status.HTTP_201_CREATED)
def create_tache(
    request: CreateTacheRequest,
    controller: TacheController = Depends(get_tache_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Cree une nouvelle tache (TAC-06, TAC-07)."""
    try:
        return controller.create_tache(
            chantier_id=request.chantier_id,
            titre=request.titre,
            description=request.description,
            parent_id=request.parent_id,
            date_echeance=request.date_echeance,
            unite_mesure=request.unite_mesure,
            quantite_estimee=request.quantite_estimee,
            heures_estimees=request.heures_estimees,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{tache_id}", response_model=TacheResponse)
def update_tache(
    tache_id: int,
    request: UpdateTacheRequest,
    controller: TacheController = Depends(get_tache_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Met a jour une tache."""
    try:
        return controller.update_tache(
            tache_id=tache_id,
            titre=request.titre,
            description=request.description,
            date_echeance=request.date_echeance,
            unite_mesure=request.unite_mesure,
            quantite_estimee=request.quantite_estimee,
            heures_estimees=request.heures_estimees,
            statut=request.statut,
            ordre=request.ordre,
        )
    except TacheNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{tache_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tache(
    tache_id: int,
    controller: TacheController = Depends(get_tache_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Supprime une tache et ses sous-taches."""
    try:
        controller.delete_tache(tache_id)
    except TacheNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/{tache_id}/complete", response_model=TacheResponse)
def complete_tache(
    tache_id: int,
    request: CompleteTacheRequest,
    controller: TacheController = Depends(get_tache_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Marque une tache comme terminee ou la rouvre (TAC-13)."""
    try:
        return controller.complete_tache(tache_id, request.terminer)
    except TacheNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/reorder", response_model=List[TacheResponse])
def reorder_taches(
    ordres: List[ReorderTacheRequest],
    controller: TacheController = Depends(get_tache_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Reordonne plusieurs taches (TAC-15 - drag & drop)."""
    try:
        return controller.reorder_taches_batch(
            [{"tache_id": o.tache_id, "ordre": o.ordre} for o in ordres]
        )
    except TacheNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


# =============================================================================
# Routes Templates
# =============================================================================


@templates_router.get("", response_model=TemplateListResponse)
def list_templates(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    query: Optional[str] = Query(None, max_length=100),
    categorie: Optional[str] = Query(None),
    active_only: bool = Query(True),
    controller: TacheController = Depends(get_tache_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Liste les templates de taches (TAC-04)."""
    return controller.list_templates(
        query=query,
        categorie=categorie,
        active_only=active_only,
        page=page,
        size=size,
    )


@templates_router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    request: CreateTemplateRequest,
    controller: TacheController = Depends(get_tache_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Cree un nouveau template (TAC-04)."""
    try:
        sous_taches = [
            {
                "titre": st.titre,
                "description": st.description,
                "ordre": st.ordre,
                "unite_mesure": st.unite_mesure,
                "heures_estimees_defaut": st.heures_estimees_defaut,
            }
            for st in request.sous_taches
        ]
        return controller.create_template(
            nom=request.nom,
            description=request.description,
            categorie=request.categorie,
            unite_mesure=request.unite_mesure,
            heures_estimees_defaut=request.heures_estimees_defaut,
            sous_taches=sous_taches,
        )
    except TemplateAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@templates_router.post("/import", response_model=List[TacheResponse])
def import_template(
    request: ImportTemplateRequest,
    controller: TacheController = Depends(get_tache_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Importe un template dans un chantier (TAC-05)."""
    try:
        return controller.import_template(request.template_id, request.chantier_id)
    except TemplateNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


# =============================================================================
# Routes Feuilles de taches
# =============================================================================


@feuilles_router.get("/tache/{tache_id}", response_model=FeuilleTacheListResponse)
def list_feuilles_by_tache(
    tache_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    controller: TacheController = Depends(get_tache_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Liste les feuilles de tache d'une tache."""
    return controller.list_feuilles_by_tache(tache_id, page, size)


@feuilles_router.get("/chantier/{chantier_id}", response_model=FeuilleTacheListResponse)
def list_feuilles_by_chantier(
    chantier_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    date_debut: Optional[str] = Query(None),
    date_fin: Optional[str] = Query(None),
    statut: Optional[str] = Query(None),
    controller: TacheController = Depends(get_tache_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Liste les feuilles de tache d'un chantier."""
    return controller.list_feuilles_by_chantier(
        chantier_id, date_debut, date_fin, statut, page, size
    )


@feuilles_router.get("/en-attente", response_model=FeuilleTacheListResponse)
def list_feuilles_en_attente(
    chantier_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    controller: TacheController = Depends(get_tache_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Liste les feuilles en attente de validation (TAC-19)."""
    return controller.list_feuilles_en_attente(chantier_id, page, size)


@feuilles_router.post("", response_model=FeuilleTacheResponse, status_code=status.HTTP_201_CREATED)
def create_feuille_tache(
    request: CreateFeuilleTacheRequest,
    controller: TacheController = Depends(get_tache_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Cree une feuille de tache (TAC-18)."""
    try:
        return controller.create_feuille_tache(
            tache_id=request.tache_id,
            utilisateur_id=request.utilisateur_id,
            chantier_id=request.chantier_id,
            date_travail=request.date_travail,
            heures_travaillees=request.heures_travaillees,
            quantite_realisee=request.quantite_realisee,
            commentaire=request.commentaire,
        )
    except TacheNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except FeuilleTacheAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@feuilles_router.post("/{feuille_id}/validate", response_model=FeuilleTacheResponse)
def validate_feuille_tache(
    feuille_id: int,
    request: ValidateFeuilleTacheRequest,
    controller: TacheController = Depends(get_tache_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Valide ou rejette une feuille de tache (TAC-19)."""
    try:
        return controller.validate_feuille_tache(
            feuille_id=feuille_id,
            validateur_id=current_user_id,
            valider=request.valider,
            motif_rejet=request.motif_rejet,
        )
    except FeuilleTacheNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Ajouter les sous-routers
router.include_router(templates_router)
router.include_router(feuilles_router)
