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
from shared.infrastructure.web import get_current_user_id

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
    date_debut_prevue: Optional[str] = None  # CHT-20 (ISO format) - renommé pour frontend
    date_fin_prevue: Optional[str] = None  # CHT-20 (ISO format) - renommé pour frontend
    description: Optional[str] = None


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
    date_debut_prevue: Optional[str] = None  # Renommé pour frontend
    date_fin_prevue: Optional[str] = None  # Renommé pour frontend
    description: Optional[str] = None


class ChangeStatutRequest(BaseModel):
    """Requête de changement de statut."""

    statut: str  # "ouvert", "en_cours", "receptionne", "ferme"


class AssignResponsableRequest(BaseModel):
    """Requête d'assignation de responsable."""

    user_id: int


class UserSummary(BaseModel):
    """Résumé d'un utilisateur pour l'inclusion dans Chantier."""

    id: str
    email: str
    nom: str
    prenom: str
    role: str
    type_utilisateur: str
    telephone: Optional[str] = None
    metier: Optional[str] = None
    couleur: Optional[str] = None
    is_active: bool


class ChantierResponse(BaseModel):
    """Réponse chantier complète selon CDC - format frontend."""

    id: str  # String pour frontend
    code: str
    nom: str
    adresse: str
    statut: str
    couleur: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    contact_nom: Optional[str] = None
    contact_telephone: Optional[str] = None
    heures_estimees: Optional[float] = None
    date_debut_prevue: Optional[str] = None  # Renommé pour frontend
    date_fin_prevue: Optional[str] = None  # Renommé pour frontend
    description: Optional[str] = None
    conducteurs: List[UserSummary] = []  # Objets User complets pour frontend
    chefs: List[UserSummary] = []  # Objets User complets pour frontend
    created_at: str
    updated_at: Optional[str] = None


class ChantierListResponse(BaseModel):
    """Réponse liste chantiers paginée (CHT-14) - format frontend."""

    items: List[ChantierResponse]
    total: int
    page: int
    size: int
    pages: int


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
            date_debut=request.date_debut_prevue,  # Mapping frontend -> backend
            date_fin=request.date_fin_prevue,  # Mapping frontend -> backend
            description=request.description,
        )
        return _transform_chantier_response(result, controller)
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
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(100, ge=1, le=500, description="Nombre d'éléments par page"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    search: Optional[str] = Query(None, max_length=100, description="Recherche par nom ou code"),
    controller: ChantierController = Depends(get_chantier_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Liste les chantiers avec pagination et filtres.

    Args:
        page: Numéro de page (commence à 1).
        size: Nombre d'éléments par page.
        statut: Filtrer par statut (optionnel).
        search: Recherche textuelle par nom ou code.
        controller: Controller des chantiers.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Liste paginée des chantiers.
    """
    # Convertir page/size en skip/limit
    skip = (page - 1) * size

    result = controller.list(
        skip=skip,
        limit=size,
        statut=statut,
        search=search,
    )

    # Convertir au format frontend
    total = result.get("total", 0)
    pages = (total + size - 1) // size if size > 0 else 0
    chantiers_data = result.get("chantiers", [])

    return ChantierListResponse(
        items=[_transform_chantier_response(c, controller) for c in chantiers_data],
        total=total,
        page=page,
        size=size,
        pages=pages,
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
        result = controller.get_by_id(chantier_id)
        return _transform_chantier_response(result, controller)
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
        result = controller.get_by_code(code)
        return _transform_chantier_response(result, controller)
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
        result = controller.update(
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
            date_debut=request.date_debut_prevue,  # Mapping frontend -> backend
            date_fin=request.date_fin_prevue,  # Mapping frontend -> backend
            description=request.description,
        )
        return _transform_chantier_response(result, controller)
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
        result = controller.change_statut(chantier_id, request.statut)
        return _transform_chantier_response(result, controller)
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
        result = controller.demarrer(chantier_id)
        return _transform_chantier_response(result, controller)
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
        result = controller.receptionner(chantier_id)
        return _transform_chantier_response(result, controller)
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
        result = controller.fermer(chantier_id)
        return _transform_chantier_response(result, controller)
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
        result = controller.assigner_conducteur(chantier_id, request.user_id)
        return _transform_chantier_response(result, controller)
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
        result = controller.retirer_conducteur(chantier_id, user_id)
        return _transform_chantier_response(result, controller)
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
        result = controller.assigner_chef_chantier(chantier_id, request.user_id)
        return _transform_chantier_response(result, controller)
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
        result = controller.retirer_chef_chantier(chantier_id, user_id)
        return _transform_chantier_response(result, controller)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


# =============================================================================
# Helpers
# =============================================================================


def _get_user_summary(user_id: int, controller: ChantierController) -> Optional[UserSummary]:
    """Récupère les infos d'un utilisateur pour l'inclusion dans un chantier."""
    try:
        # Le controller a accès au user_repo via dependency injection
        # Pour l'instant, on retourne un objet minimal
        # TODO: Implémenter une vraie récupération des utilisateurs
        return None
    except Exception:
        return None


def _transform_chantier_response(chantier_dict: dict, controller: ChantierController) -> ChantierResponse:
    """
    Transforme un dictionnaire chantier du controller en ChantierResponse.

    Convertit les IDs des conducteurs/chefs en objets User complets.
    """
    # Récupérer les coordonnées GPS
    coords = chantier_dict.get("coordonnees_gps") or {}
    latitude = coords.get("latitude") if coords else None
    longitude = coords.get("longitude") if coords else None

    # Récupérer le contact
    contact = chantier_dict.get("contact") or {}
    contact_nom = contact.get("nom") if contact else None
    contact_telephone = contact.get("telephone") if contact else None

    # Pour les conducteurs et chefs, on garde les IDs pour l'instant
    # car la récupération des objets User complets nécessiterait une dépendance vers le module auth
    # TODO: Implémenter la récupération des objets User complets via un service partagé
    conducteur_ids = chantier_dict.get("conducteur_ids", [])
    chef_chantier_ids = chantier_dict.get("chef_chantier_ids", [])

    # Créer des objets UserSummary minimaux avec juste les IDs
    conducteurs = [
        UserSummary(
            id=str(uid),
            email="",
            nom="",
            prenom="",
            role="conducteur",
            type_utilisateur="employe",
            is_active=True,
        )
        for uid in conducteur_ids
    ]

    chefs = [
        UserSummary(
            id=str(uid),
            email="",
            nom="",
            prenom="",
            role="chef_chantier",
            type_utilisateur="employe",
            is_active=True,
        )
        for uid in chef_chantier_ids
    ]

    return ChantierResponse(
        id=str(chantier_dict.get("id", "")),
        code=chantier_dict.get("code", ""),
        nom=chantier_dict.get("nom", ""),
        adresse=chantier_dict.get("adresse", ""),
        statut=chantier_dict.get("statut", "ouvert"),
        couleur=chantier_dict.get("couleur"),
        latitude=latitude,
        longitude=longitude,
        contact_nom=contact_nom,
        contact_telephone=contact_telephone,
        heures_estimees=chantier_dict.get("heures_estimees"),
        date_debut_prevue=chantier_dict.get("date_debut"),
        date_fin_prevue=chantier_dict.get("date_fin"),
        description=chantier_dict.get("description"),
        conducteurs=conducteurs,
        chefs=chefs,
        created_at=chantier_dict.get("created_at", ""),
        updated_at=chantier_dict.get("updated_at"),
    )
