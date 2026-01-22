"""Routes FastAPI pour la gestion des chantiers."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from ...adapters.controllers import ChantierController
from ...application.use_cases import (
    CodeChantierAlreadyExistsError,
    InvalidDatesError,
    ChantierNotFoundError,
    ChantierFermeError,
    ChantierActifError,
    TransitionNonAutoriseeError,
    InvalidRoleTypeError,
)
from .dependencies import get_chantier_controller
from modules.auth.infrastructure.web.dependencies import get_current_user_id

router = APIRouter(prefix="/chantiers", tags=["chantiers"])


# =============================================================================
# Pydantic models for request/response validation
# Selon CDC Section 4 - Gestion des Chantiers (CHT-01 à CHT-20)
# =============================================================================


class CoordonneesGPSResponse(BaseModel):
    """Coordonnées GPS d'un chantier."""

    latitude: float
    longitude: float


class ContactResponse(BaseModel):
    """Contact sur place d'un chantier."""

    nom: str
    telephone: str


class CreateChantierRequest(BaseModel):
    """Requête de création de chantier."""

    nom: str
    adresse: str
    code: Optional[str] = None  # Auto-généré si non fourni (CHT-19)
    couleur: Optional[str] = None  # CHT-02
    latitude: Optional[float] = None  # CHT-04
    longitude: Optional[float] = None  # CHT-04
    photo_couverture: Optional[str] = None  # CHT-01
    contact_nom: Optional[str] = None  # CHT-07
    contact_telephone: Optional[str] = None  # CHT-07
    heures_estimees: Optional[float] = None  # CHT-18
    date_debut: Optional[str] = None  # CHT-20 (ISO format)
    date_fin: Optional[str] = None  # CHT-20 (ISO format)
    description: Optional[str] = None
    conducteur_ids: Optional[List[int]] = None  # CHT-05
    chef_chantier_ids: Optional[List[int]] = None  # CHT-06


class UpdateChantierRequest(BaseModel):
    """Requête de mise à jour de chantier."""

    nom: Optional[str] = None
    adresse: Optional[str] = None
    couleur: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_couverture: Optional[str] = None
    contact_nom: Optional[str] = None
    contact_telephone: Optional[str] = None
    heures_estimees: Optional[float] = None
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None
    description: Optional[str] = None


class ChangeStatutRequest(BaseModel):
    """Requête de changement de statut."""

    statut: str  # "ouvert", "en_cours", "receptionne", "ferme"


class AssignResponsableRequest(BaseModel):
    """Requête d'assignation de responsable."""

    user_id: int


class ChantierResponse(BaseModel):
    """Réponse chantier complète selon CDC."""

    id: int
    code: str
    nom: str
    adresse: str
    statut: str
    statut_icon: str
    couleur: str
    coordonnees_gps: Optional[dict] = None
    photo_couverture: Optional[str] = None
    contact: Optional[dict] = None
    heures_estimees: Optional[float] = None
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None
    description: Optional[str] = None
    conducteur_ids: List[int]
    chef_chantier_ids: List[int]
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ChantierListResponse(BaseModel):
    """Réponse liste chantiers paginée (CHT-14)."""

    chantiers: List[ChantierResponse]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_previous: bool


class DeleteResponse(BaseModel):
    """Réponse de suppression."""

    deleted: bool
    id: int


# =============================================================================
# Routes CRUD Chantiers
# =============================================================================


@router.post("", response_model=ChantierResponse, status_code=status.HTTP_201_CREATED)
def create_chantier(
    request: CreateChantierRequest,
    controller: ChantierController = Depends(get_chantier_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Crée un nouveau chantier.

    Le code est auto-généré si non fourni (CHT-19).

    Args:
        request: Données de création.
        controller: Controller des chantiers.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le chantier créé.

    Raises:
        HTTPException 400: Code déjà utilisé ou données invalides.
    """
    try:
        result = controller.create(
            nom=request.nom,
            adresse=request.adresse,
            code=request.code,
            couleur=request.couleur,
            latitude=request.latitude,
            longitude=request.longitude,
            photo_couverture=request.photo_couverture,
            contact_nom=request.contact_nom,
            contact_telephone=request.contact_telephone,
            heures_estimees=request.heures_estimees,
            date_debut=request.date_debut,
            date_fin=request.date_fin,
            description=request.description,
            conducteur_ids=request.conducteur_ids,
            chef_chantier_ids=request.chef_chantier_ids,
        )
        return result
    except CodeChantierAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except InvalidDatesError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=ChantierListResponse)
def list_chantiers(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=500, description="Nombre d'éléments par page"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    conducteur_id: Optional[int] = Query(None, description="Filtrer par conducteur"),
    chef_chantier_id: Optional[int] = Query(None, description="Filtrer par chef"),
    responsable_id: Optional[int] = Query(
        None, description="Filtrer par responsable (conducteur ou chef)"
    ),
    actifs_uniquement: bool = Query(False, description="Uniquement les chantiers actifs"),
    search: Optional[str] = Query(None, description="Recherche par nom ou code"),
    controller: ChantierController = Depends(get_chantier_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Liste les chantiers avec pagination et filtres.

    Args:
        skip: Offset pour la pagination.
        limit: Limite d'éléments retournés.
        statut: Filtrer par statut (optionnel).
        conducteur_id: Filtrer par conducteur (optionnel).
        chef_chantier_id: Filtrer par chef de chantier (optionnel).
        responsable_id: Filtrer par responsable (optionnel).
        actifs_uniquement: Uniquement les chantiers actifs.
        search: Recherche textuelle par nom ou code.
        controller: Controller des chantiers.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Liste paginée des chantiers.
    """
    return controller.list(
        skip=skip,
        limit=limit,
        statut=statut,
        conducteur_id=conducteur_id,
        chef_chantier_id=chef_chantier_id,
        responsable_id=responsable_id,
        actifs_uniquement=actifs_uniquement,
        search=search,
    )


@router.get("/{chantier_id}", response_model=ChantierResponse)
def get_chantier(
    chantier_id: int,
    controller: ChantierController = Depends(get_chantier_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Récupère un chantier par son ID.

    Args:
        chantier_id: ID du chantier.
        controller: Controller des chantiers.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le chantier.

    Raises:
        HTTPException 404: Chantier non trouvé.
    """
    try:
        return controller.get_by_id(chantier_id)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.get("/code/{code}", response_model=ChantierResponse)
def get_chantier_by_code(
    code: str,
    controller: ChantierController = Depends(get_chantier_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Récupère un chantier par son code (CHT-19).

    Args:
        code: Code du chantier (ex: A001).
        controller: Controller des chantiers.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le chantier.

    Raises:
        HTTPException 404: Chantier non trouvé.
    """
    try:
        return controller.get_by_code(code)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.put("/{chantier_id}", response_model=ChantierResponse)
def update_chantier(
    chantier_id: int,
    request: UpdateChantierRequest,
    controller: ChantierController = Depends(get_chantier_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Met à jour un chantier.

    Args:
        chantier_id: ID du chantier à mettre à jour.
        request: Données de mise à jour.
        controller: Controller des chantiers.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le chantier mis à jour.

    Raises:
        HTTPException 404: Chantier non trouvé.
        HTTPException 400: Chantier fermé ou données invalides.
    """
    try:
        return controller.update(
            chantier_id=chantier_id,
            nom=request.nom,
            adresse=request.adresse,
            couleur=request.couleur,
            latitude=request.latitude,
            longitude=request.longitude,
            photo_couverture=request.photo_couverture,
            contact_nom=request.contact_nom,
            contact_telephone=request.contact_telephone,
            heures_estimees=request.heures_estimees,
            date_debut=request.date_debut,
            date_fin=request.date_fin,
            description=request.description,
        )
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except ChantierFermeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{chantier_id}", response_model=DeleteResponse)
def delete_chantier(
    chantier_id: int,
    force: bool = Query(False, description="Forcer la suppression d'un chantier actif"),
    controller: ChantierController = Depends(get_chantier_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Supprime un chantier.

    Le chantier doit être fermé, sauf si force=True.

    Args:
        chantier_id: ID du chantier à supprimer.
        force: Forcer la suppression même si actif.
        controller: Controller des chantiers.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Confirmation de suppression.

    Raises:
        HTTPException 404: Chantier non trouvé.
        HTTPException 400: Chantier actif et force=False.
    """
    try:
        return controller.delete(chantier_id, force=force)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except ChantierActifError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


# =============================================================================
# Routes de gestion du statut (CHT-03)
# =============================================================================


@router.post("/{chantier_id}/statut", response_model=ChantierResponse)
def change_statut(
    chantier_id: int,
    request: ChangeStatutRequest,
    controller: ChantierController = Depends(get_chantier_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Change le statut d'un chantier (CHT-03).

    Transitions autorisées:
    - Ouvert → En cours, Fermé
    - En cours → Réceptionné, Fermé
    - Réceptionné → En cours, Fermé
    - Fermé → (aucune)

    Args:
        chantier_id: ID du chantier.
        request: Nouveau statut.
        controller: Controller des chantiers.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le chantier mis à jour.

    Raises:
        HTTPException 404: Chantier non trouvé.
        HTTPException 400: Transition non autorisée.
    """
    try:
        return controller.change_statut(chantier_id, request.statut)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except TransitionNonAutoriseeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{chantier_id}/demarrer", response_model=ChantierResponse)
def demarrer_chantier(
    chantier_id: int,
    controller: ChantierController = Depends(get_chantier_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Passe le chantier en statut 'En cours'."""
    try:
        return controller.demarrer(chantier_id)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except TransitionNonAutoriseeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.post("/{chantier_id}/receptionner", response_model=ChantierResponse)
def receptionner_chantier(
    chantier_id: int,
    controller: ChantierController = Depends(get_chantier_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Passe le chantier en statut 'Réceptionné'."""
    try:
        return controller.receptionner(chantier_id)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except TransitionNonAutoriseeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.post("/{chantier_id}/fermer", response_model=ChantierResponse)
def fermer_chantier(
    chantier_id: int,
    controller: ChantierController = Depends(get_chantier_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Passe le chantier en statut 'Fermé'."""
    try:
        return controller.fermer(chantier_id)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except TransitionNonAutoriseeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


# =============================================================================
# Routes d'assignation de responsables (CHT-05, CHT-06)
# =============================================================================


@router.post("/{chantier_id}/conducteurs", response_model=ChantierResponse)
def assigner_conducteur(
    chantier_id: int,
    request: AssignResponsableRequest,
    controller: ChantierController = Depends(get_chantier_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Assigne un conducteur au chantier (CHT-05: Multi-conducteurs).

    Args:
        chantier_id: ID du chantier.
        request: ID du conducteur à assigner.
        controller: Controller des chantiers.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le chantier mis à jour.
    """
    try:
        return controller.assigner_conducteur(chantier_id, request.user_id)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.delete("/{chantier_id}/conducteurs/{user_id}", response_model=ChantierResponse)
def retirer_conducteur(
    chantier_id: int,
    user_id: int,
    controller: ChantierController = Depends(get_chantier_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Retire un conducteur du chantier."""
    try:
        return controller.retirer_conducteur(chantier_id, user_id)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.post("/{chantier_id}/chefs", response_model=ChantierResponse)
def assigner_chef_chantier(
    chantier_id: int,
    request: AssignResponsableRequest,
    controller: ChantierController = Depends(get_chantier_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Assigne un chef de chantier (CHT-06: Multi-chefs de chantier).

    Args:
        chantier_id: ID du chantier.
        request: ID du chef à assigner.
        controller: Controller des chantiers.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le chantier mis à jour.
    """
    try:
        return controller.assigner_chef_chantier(chantier_id, request.user_id)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.delete("/{chantier_id}/chefs/{user_id}", response_model=ChantierResponse)
def retirer_chef_chantier(
    chantier_id: int,
    user_id: int,
    controller: ChantierController = Depends(get_chantier_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Retire un chef de chantier."""
    try:
        return controller.retirer_chef_chantier(chantier_id, user_id)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
