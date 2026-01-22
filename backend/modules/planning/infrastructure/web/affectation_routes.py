"""Routes FastAPI pour la gestion des affectations."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional, List

from ...application.use_cases import (
    CreateAffectationUseCase,
    GetAffectationUseCase,
    ListAffectationsUseCase,
    UpdateAffectationUseCase,
    DeleteAffectationUseCase,
    DeplacerAffectationUseCase,
    DupliquerAffectationsUseCase,
    AffectationAlreadyExistsError,
    AffectationNotFoundError,
    InvalidCreneauError,
)
from ...application.dtos import (
    CreateAffectationDTO,
    UpdateAffectationDTO,
    DeplacerAffectationDTO,
    DupliquerAffectationsDTO,
    ListAffectationsDTO,
)
from .dependencies import (
    get_create_affectation_use_case,
    get_get_affectation_use_case,
    get_list_affectations_use_case,
    get_update_affectation_use_case,
    get_delete_affectation_use_case,
    get_deplacer_affectation_use_case,
    get_dupliquer_affectations_use_case,
)
from shared.infrastructure.web import get_current_user_id


router = APIRouter(prefix="/planning", tags=["planning"])


# =============================================================================
# Pydantic models for request/response validation
# Selon CDC Section 5 - Planning Opérationnel (PLN-01 à PLN-28)
# =============================================================================


class CreateAffectationRequest(BaseModel):
    """Requête de création d'affectation."""

    utilisateur_id: int
    chantier_id: int
    date_affectation: str  # ISO format: YYYY-MM-DD
    heure_debut: Optional[str] = None  # Format HH:MM
    heure_fin: Optional[str] = None  # Format HH:MM
    note: Optional[str] = None
    recurrence: str = "unique"
    jours_recurrence: List[int] = []
    date_fin_recurrence: Optional[str] = None


class UpdateAffectationRequest(BaseModel):
    """Requête de mise à jour d'affectation."""

    chantier_id: Optional[int] = None
    date_affectation: Optional[str] = None
    heure_debut: Optional[str] = None
    heure_fin: Optional[str] = None
    note: Optional[str] = None


class DeplacerAffectationRequest(BaseModel):
    """Requête de déplacement d'affectation (PLN-27: Drag & Drop)."""

    nouvelle_date: str  # ISO format
    nouveau_chantier_id: Optional[int] = None


class DupliquerAffectationsRequest(BaseModel):
    """Requête de duplication d'affectations (PLN-16)."""

    utilisateur_id: int
    date_source_debut: str
    date_source_fin: str
    date_cible_debut: str


class AffectationResponse(BaseModel):
    """Réponse affectation complète."""

    id: int
    utilisateur_id: int
    chantier_id: int
    date_affectation: str
    heure_debut: Optional[str] = None
    heure_fin: Optional[str] = None
    note: Optional[str] = None
    recurrence: str
    jours_recurrence: List[int] = []
    date_fin_recurrence: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AffectationListResponse(BaseModel):
    """Réponse liste d'affectations paginée."""

    items: List[AffectationResponse]
    total: int
    skip: int
    limit: int


class DeleteResponse(BaseModel):
    """Réponse de suppression."""

    deleted: bool
    id: int


# =============================================================================
# Routes CRUD Affectations
# =============================================================================


@router.post("", response_model=AffectationResponse, status_code=status.HTTP_201_CREATED)
def create_affectation(
    request: CreateAffectationRequest,
    use_case: CreateAffectationUseCase = Depends(get_create_affectation_use_case),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Crée une nouvelle affectation (PLN-03, PLN-28).

    Args:
        request: Données de création.
        use_case: Use case de création.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        L'affectation créée.

    Raises:
        HTTPException 400: Affectation existe déjà ou données invalides.
    """
    try:
        dto = CreateAffectationDTO(
            utilisateur_id=request.utilisateur_id,
            chantier_id=request.chantier_id,
            date_affectation=request.date_affectation,
            heure_debut=request.heure_debut,
            heure_fin=request.heure_fin,
            note=request.note,
            recurrence=request.recurrence,
            jours_recurrence=request.jours_recurrence,
            date_fin_recurrence=request.date_fin_recurrence,
        )
        result = use_case.execute(dto, created_by=current_user_id)
        return AffectationResponse(**result.to_dict())
    except AffectationAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except InvalidCreneauError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=AffectationListResponse)
def list_affectations(
    date_debut: str = Query(..., description="Date de début (ISO format)"),
    date_fin: str = Query(..., description="Date de fin (ISO format)"),
    utilisateur_id: Optional[int] = Query(None, description="Filtrer par utilisateur"),
    chantier_id: Optional[int] = Query(None, description="Filtrer par chantier"),
    skip: int = Query(0, ge=0, description="Offset pour pagination"),
    limit: int = Query(100, ge=1, le=500, description="Limite pour pagination"),
    use_case: ListAffectationsUseCase = Depends(get_list_affectations_use_case),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Liste les affectations avec filtres (PLN-01, PLN-02).

    Vues disponibles:
    - Vue Chantiers: filter by chantier_id
    - Vue Utilisateurs: filter by utilisateur_id
    - Vue Globale: sans filtre

    Args:
        date_debut: Date de début de la période.
        date_fin: Date de fin de la période.
        utilisateur_id: Filtrer par utilisateur (optionnel).
        chantier_id: Filtrer par chantier (optionnel).
        skip: Offset pour pagination.
        limit: Limite pour pagination.

    Returns:
        Liste paginée des affectations.
    """
    dto = ListAffectationsDTO(
        date_debut=date_debut,
        date_fin=date_fin,
        utilisateur_id=utilisateur_id,
        chantier_id=chantier_id,
        skip=skip,
        limit=limit,
    )
    result = use_case.execute(dto)
    return AffectationListResponse(
        items=[AffectationResponse(**a.to_dict()) for a in result.affectations],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
    )


@router.get("/{affectation_id}", response_model=AffectationResponse)
def get_affectation(
    affectation_id: int,
    use_case: GetAffectationUseCase = Depends(get_get_affectation_use_case),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Récupère une affectation par son ID.

    Args:
        affectation_id: ID de l'affectation.

    Returns:
        L'affectation.

    Raises:
        HTTPException 404: Affectation non trouvée.
    """
    try:
        result = use_case.execute(affectation_id)
        return AffectationResponse(**result.to_dict())
    except AffectationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.put("/{affectation_id}", response_model=AffectationResponse)
def update_affectation(
    affectation_id: int,
    request: UpdateAffectationRequest,
    use_case: UpdateAffectationUseCase = Depends(get_update_affectation_use_case),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Met à jour une affectation.

    Args:
        affectation_id: ID de l'affectation à modifier.
        request: Données de mise à jour.

    Returns:
        L'affectation mise à jour.

    Raises:
        HTTPException 404: Affectation non trouvée.
    """
    try:
        dto = UpdateAffectationDTO(
            affectation_id=affectation_id,
            chantier_id=request.chantier_id,
            date_affectation=request.date_affectation,
            heure_debut=request.heure_debut,
            heure_fin=request.heure_fin,
            note=request.note,
        )
        result = use_case.execute(dto, updated_by=current_user_id)
        return AffectationResponse(**result.to_dict())
    except AffectationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{affectation_id}", response_model=DeleteResponse)
def delete_affectation(
    affectation_id: int,
    use_case: DeleteAffectationUseCase = Depends(get_delete_affectation_use_case),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Supprime une affectation.

    Args:
        affectation_id: ID de l'affectation à supprimer.

    Returns:
        Confirmation de suppression.

    Raises:
        HTTPException 404: Affectation non trouvée.
    """
    try:
        result = use_case.execute(affectation_id, deleted_by=current_user_id)
        return DeleteResponse(**result)
    except AffectationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


# =============================================================================
# Routes spécifiques Planning
# =============================================================================


@router.post("/{affectation_id}/deplacer", response_model=AffectationResponse)
def deplacer_affectation(
    affectation_id: int,
    request: DeplacerAffectationRequest,
    use_case: DeplacerAffectationUseCase = Depends(get_deplacer_affectation_use_case),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Déplace une affectation vers une nouvelle date/chantier (PLN-27: Drag & Drop).

    Args:
        affectation_id: ID de l'affectation à déplacer.
        request: Nouvelle date et/ou nouveau chantier.

    Returns:
        L'affectation déplacée.

    Raises:
        HTTPException 404: Affectation non trouvée.
    """
    try:
        dto = DeplacerAffectationDTO(
            affectation_id=affectation_id,
            nouvelle_date=request.nouvelle_date,
            nouveau_chantier_id=request.nouveau_chantier_id,
        )
        result = use_case.execute(dto, moved_by=current_user_id)
        return AffectationResponse(**result.to_dict())
    except AffectationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.post("/dupliquer", response_model=List[AffectationResponse])
def dupliquer_affectations(
    request: DupliquerAffectationsRequest,
    use_case: DupliquerAffectationsUseCase = Depends(get_dupliquer_affectations_use_case),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Duplique les affectations d'une période vers une autre (PLN-16).

    Args:
        request: Période source et période cible.

    Returns:
        Liste des affectations créées.
    """
    try:
        dto = DupliquerAffectationsDTO(
            utilisateur_id=request.utilisateur_id,
            date_source_debut=request.date_source_debut,
            date_source_fin=request.date_source_fin,
            date_cible_debut=request.date_cible_debut,
        )
        results = use_case.execute(dto, created_by=current_user_id)
        return [AffectationResponse(**r.to_dict()) for r in results]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/date/{date_affectation}", response_model=AffectationListResponse)
def get_affectations_by_date(
    date_affectation: str,
    use_case: ListAffectationsUseCase = Depends(get_list_affectations_use_case),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Récupère toutes les affectations pour une date donnée.

    Args:
        date_affectation: Date au format ISO.

    Returns:
        Liste des affectations du jour.
    """
    result = use_case.get_by_date(date_affectation)
    return AffectationListResponse(
        items=[AffectationResponse(**a.to_dict()) for a in result.affectations],
        total=result.total,
        skip=0,
        limit=result.total,
    )
