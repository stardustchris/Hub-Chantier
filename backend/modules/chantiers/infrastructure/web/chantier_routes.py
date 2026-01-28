"""Routes FastAPI pour la gestion des chantiers."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy.orm import Session

from ...adapters.controllers import ChantierController
from ..persistence import ContactChantierModel, PhaseChantierModel, ChantierOuvrierModel
from shared.infrastructure.database import get_db
from ...application.use_cases import (
    CodeChantierAlreadyExistsError,
    InvalidDatesError,
    ChantierNotFoundError,
    ChantierFermeError,
    ChantierActifError,
    TransitionNonAutoriseeError,
)
from ...domain.events.chantier_created import ChantierCreatedEvent
from .dependencies import get_chantier_controller, get_user_repository
from shared.infrastructure.web import (
    get_current_user_id,
    require_conducteur_or_admin,
    require_admin,
)
from shared.infrastructure.event_bus.dependencies import get_event_bus
from shared.infrastructure.event_bus import EventBus

# Type hints only - avoid runtime import cross-module
if TYPE_CHECKING:
    from modules.auth.domain.repositories import UserRepository

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
    profession: Optional[str] = None
    telephone: Optional[str] = None


class ContactRequest(BaseModel):
    """Contact pour création/mise à jour."""

    nom: str
    profession: Optional[str] = None
    telephone: Optional[str] = None


class ContactChantierResponse(BaseModel):
    """Contact complet d'un chantier avec profession."""

    id: int
    nom: str
    telephone: str
    profession: Optional[str] = None


class ContactChantierCreate(BaseModel):
    """Requête de création d'un contact chantier."""

    nom: str
    telephone: str
    profession: Optional[str] = None


class ContactChantierUpdate(BaseModel):
    """Requête de mise à jour d'un contact chantier."""

    nom: Optional[str] = None
    telephone: Optional[str] = None
    profession: Optional[str] = None


class PhaseChantierResponse(BaseModel):
    """Phase/étape d'un chantier."""

    id: int
    nom: str
    description: Optional[str] = None
    ordre: int
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None


class PhaseChantierCreate(BaseModel):
    """Requête de création d'une phase de chantier."""

    nom: str
    description: Optional[str] = None
    ordre: Optional[int] = 1
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None


class PhaseChantierUpdate(BaseModel):
    """Requête de mise à jour d'une phase de chantier."""

    nom: Optional[str] = None
    description: Optional[str] = None
    ordre: Optional[int] = None
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None


class CreateChantierRequest(BaseModel):
    """Requête de création de chantier."""

    nom: str
    adresse: str
    code: Optional[str] = None  # Auto-généré si non fourni (CHT-19)
    couleur: Optional[str] = None  # CHT-02
    latitude: Optional[float] = None  # CHT-04
    longitude: Optional[float] = None  # CHT-04
    photo_couverture: Optional[str] = None  # CHT-01
    contact_nom: Optional[str] = None  # CHT-07 (legacy single contact)
    contact_telephone: Optional[str] = None  # CHT-07 (legacy single contact)
    contacts: Optional[List[ContactRequest]] = None  # CHT-07 (multiple contacts)
    heures_estimees: Optional[float] = None  # CHT-18
    date_debut_prevue: Optional[str] = None  # CHT-20 (ISO format) - renommé pour frontend
    date_fin_prevue: Optional[str] = None  # CHT-20 (ISO format) - renommé pour frontend
    description: Optional[str] = None


class UpdateChantierRequest(BaseModel):
    """Requête de mise à jour de chantier."""

    nom: Optional[str] = None
    adresse: Optional[str] = None
    couleur: Optional[str] = None
    statut: Optional[str] = None  # Pour changement direct de statut
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_couverture: Optional[str] = None
    contact_nom: Optional[str] = None  # Legacy
    contact_telephone: Optional[str] = None  # Legacy
    contacts: Optional[List[ContactRequest]] = None  # Multiple contacts
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


class UserPublicSummary(BaseModel):
    """
    Résumé public d'un utilisateur (sans données sensibles RGPD).

    Utilisé pour l'affichage des conducteurs/chefs dans les chantiers.
    Ne contient PAS email ni téléphone pour conformité RGPD.
    """

    id: str
    nom: str
    prenom: str
    role: str
    type_utilisateur: str
    metier: Optional[str] = None
    couleur: Optional[str] = None
    is_active: bool


# Alias pour compatibilité (ne pas utiliser pour nouvelles features)
UserSummary = UserPublicSummary


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
    contact_nom: Optional[str] = None  # Legacy field
    contact_telephone: Optional[str] = None  # Legacy field
    contacts: List[ContactResponse] = []  # Multi-contacts
    phases: List[PhaseChantierResponse] = []  # Phases/étapes du chantier
    heures_estimees: Optional[float] = None
    date_debut_prevue: Optional[str] = None  # Renommé pour frontend
    date_fin_prevue: Optional[str] = None  # Renommé pour frontend
    description: Optional[str] = None
    conducteurs: List[UserPublicSummary] = []  # Objets User publics (sans email/tel)
    chefs: List[UserPublicSummary] = []  # Objets User publics (sans email/tel)
    ouvriers: List[UserPublicSummary] = []  # Ouvriers/intérimaires/sous-traitants
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
async def create_chantier(
    request: CreateChantierRequest,
    event_bus: EventBus = Depends(get_event_bus),
    controller: ChantierController = Depends(get_chantier_controller),
    user_repo: UserRepository = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC: conducteur ou admin requis
):
    """
    Crée un nouveau chantier.

    Le code est auto-généré si non fourni (CHT-19).
    RBAC: Requiert le rôle conducteur ou admin.

    Args:
        request: Données de création.
        event_bus: Event bus for publishing domain events.
        controller: Controller des chantiers.
        user_repo: Repository utilisateurs.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le chantier créé.

    Raises:
        HTTPException 400: Code déjà utilisé ou données invalides.
        HTTPException 403: Accès non autorisé.
    """
    try:
        # Convertir les contacts en liste de dicts
        contacts_data = None
        if request.contacts:
            contacts_data = [
                {"nom": c.nom, "profession": c.profession, "telephone": c.telephone}
                for c in request.contacts
            ]

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
            contacts=contacts_data,
            heures_estimees=request.heures_estimees,
            date_debut=request.date_debut_prevue,  # Mapping frontend -> backend
            date_fin=request.date_fin_prevue,  # Mapping frontend -> backend
            description=request.description,
        )

        # Publish event after database commit
        await event_bus.publish(ChantierCreatedEvent(
            chantier_id=result["id"],
            nom=result.get("nom", ""),
            adresse=result.get("adresse", ""),
            statut=result.get("statut", "ouvert"),
            metadata={
                "code": result.get("code", ""),
                "conducteur_ids": result.get("conducteur_ids", []),
                "chef_chantier_ids": result.get("chef_chantier_ids", []),
                "created_by": current_user_id
            }
        ))

        return _transform_chantier_response(result, controller, user_repo)
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
    db: Session = Depends(get_db),
    controller: ChantierController = Depends(get_chantier_controller),
    user_repo: UserRepository = Depends(get_user_repository),
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
        user_repo: Repository utilisateurs.
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
        items=[_transform_chantier_response(c, controller, user_repo, db) for c in chantiers_data],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{chantier_id}", response_model=ChantierResponse)
def get_chantier(
    chantier_id: int,
    db: Session = Depends(get_db),
    controller: ChantierController = Depends(get_chantier_controller),
    user_repo: UserRepository = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Récupère un chantier par son ID.

    Args:
        chantier_id: ID du chantier.
        db: Session base de données.
        controller: Controller des chantiers.
        user_repo: Repository utilisateurs.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le chantier.

    Raises:
        HTTPException 404: Chantier non trouvé.
    """
    try:
        result = controller.get_by_id(chantier_id)
        return _transform_chantier_response(result, controller, user_repo, db)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.get("/code/{code}", response_model=ChantierResponse)
def get_chantier_by_code(
    code: str,
    controller: ChantierController = Depends(get_chantier_controller),
    user_repo: UserRepository = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Récupère un chantier par son code (CHT-19).

    Args:
        code: Code du chantier (ex: A001).
        controller: Controller des chantiers.
        user_repo: Repository utilisateurs.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le chantier.

    Raises:
        HTTPException 404: Chantier non trouvé.
    """
    try:
        result = controller.get_by_code(code)
        return _transform_chantier_response(result, controller, user_repo)
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
    user_repo: UserRepository = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC: conducteur ou admin requis
):
    """
    Met à jour un chantier.

    RBAC: Requiert le rôle conducteur ou admin.

    Args:
        chantier_id: ID du chantier à mettre à jour.
        request: Données de mise à jour.
        controller: Controller des chantiers.
        user_repo: Repository utilisateurs.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le chantier mis à jour.

    Raises:
        HTTPException 404: Chantier non trouvé.
        HTTPException 400: Chantier fermé ou données invalides.
        HTTPException 403: Accès non autorisé.
    """
    try:
        # Convertir les contacts en liste de dicts
        contacts_data = None
        if request.contacts:
            contacts_data = [
                {"nom": c.nom, "profession": c.profession, "telephone": c.telephone}
                for c in request.contacts
            ]

        result = controller.update(
            chantier_id=chantier_id,
            nom=request.nom,
            adresse=request.adresse,
            couleur=request.couleur,
            statut=request.statut,
            latitude=request.latitude,
            longitude=request.longitude,
            photo_couverture=request.photo_couverture,
            contact_nom=request.contact_nom,
            contact_telephone=request.contact_telephone,
            contacts=contacts_data,
            heures_estimees=request.heures_estimees,
            date_debut=request.date_debut_prevue,  # Mapping frontend -> backend
            date_fin=request.date_fin_prevue,  # Mapping frontend -> backend
            description=request.description,
        )
        return _transform_chantier_response(result, controller, user_repo)
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
    _role: str = Depends(require_admin),  # RBAC: admin uniquement pour suppression
):
    """
    Supprime un chantier (soft delete).

    Le chantier doit être fermé, sauf si force=True.
    RBAC: Requiert le rôle admin.

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
        HTTPException 403: Accès non autorisé (admin requis).
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
    user_repo: UserRepository = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC: conducteur ou admin requis
):
    """
    Change le statut d'un chantier (CHT-03).

    RBAC: Requiert le rôle conducteur ou admin.

    Transitions autorisées:
    - Ouvert → En cours, Fermé
    - En cours → Réceptionné, Fermé
    - Réceptionné → En cours, Fermé
    - Fermé → (aucune)

    Args:
        chantier_id: ID du chantier.
        request: Nouveau statut.
        controller: Controller des chantiers.
        user_repo: Repository utilisateurs.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le chantier mis à jour.

    Raises:
        HTTPException 404: Chantier non trouvé.
        HTTPException 400: Transition non autorisée.
        HTTPException 403: Accès non autorisé.
    """
    try:
        result = controller.change_statut(chantier_id, request.statut)
        return _transform_chantier_response(result, controller, user_repo)
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
    user_repo: UserRepository = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
):
    """Passe le chantier en statut 'En cours'. RBAC: conducteur ou admin requis."""
    try:
        result = controller.demarrer(chantier_id)
        return _transform_chantier_response(result, controller, user_repo)
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
    user_repo: UserRepository = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
):
    """Passe le chantier en statut 'Réceptionné'. RBAC: conducteur ou admin requis."""
    try:
        result = controller.receptionner(chantier_id)
        return _transform_chantier_response(result, controller, user_repo)
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
    user_repo: UserRepository = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
):
    """Passe le chantier en statut 'Fermé'. RBAC: conducteur ou admin requis."""
    try:
        result = controller.fermer(chantier_id)
        return _transform_chantier_response(result, controller, user_repo)
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
    user_repo: UserRepository = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
):
    """
    Assigne un conducteur au chantier (CHT-05: Multi-conducteurs).

    RBAC: Requiert le rôle conducteur ou admin.

    Args:
        chantier_id: ID du chantier.
        request: ID du conducteur à assigner.
        controller: Controller des chantiers.
        user_repo: Repository utilisateurs.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le chantier mis à jour.
    """
    try:
        result = controller.assigner_conducteur(chantier_id, request.user_id)
        return _transform_chantier_response(result, controller, user_repo)
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
    user_repo: UserRepository = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
):
    """Retire un conducteur du chantier. RBAC: conducteur ou admin requis."""
    try:
        result = controller.retirer_conducteur(chantier_id, user_id)
        return _transform_chantier_response(result, controller, user_repo)
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
    user_repo: UserRepository = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
):
    """
    Assigne un chef de chantier (CHT-06: Multi-chefs de chantier).

    RBAC: Requiert le rôle conducteur ou admin.

    Args:
        chantier_id: ID du chantier.
        request: ID du chef à assigner.
        controller: Controller des chantiers.
        user_repo: Repository utilisateurs.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le chantier mis à jour.
    """
    try:
        result = controller.assigner_chef_chantier(chantier_id, request.user_id)
        return _transform_chantier_response(result, controller, user_repo)
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
    user_repo: UserRepository = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
):
    """Retire un chef de chantier. RBAC: conducteur ou admin requis."""
    try:
        result = controller.retirer_chef_chantier(chantier_id, user_id)
        return _transform_chantier_response(result, controller, user_repo)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


# =============================================================================
# Routes d'assignation des ouvriers (intérimaires, sous-traitants)
# =============================================================================


@router.post("/{chantier_id}/ouvriers", response_model=ChantierResponse)
def assigner_ouvrier(
    chantier_id: int,
    request: AssignResponsableRequest,
    db: Session = Depends(get_db),
    controller: ChantierController = Depends(get_chantier_controller),
    user_repo: UserRepository = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
):
    """
    Assigne un ouvrier/intérimaire/sous-traitant au chantier.

    RBAC: Requiert le rôle conducteur ou admin.

    Args:
        chantier_id: ID du chantier.
        request: ID de l'ouvrier à assigner.
        db: Session base de données.
        controller: Controller des chantiers.
        user_repo: Repository utilisateurs.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le chantier mis à jour.
    """
    from ..persistence import ChantierOuvrierModel

    # Vérifier si l'association existe déjà
    existing = db.query(ChantierOuvrierModel).filter(
        ChantierOuvrierModel.chantier_id == chantier_id,
        ChantierOuvrierModel.user_id == request.user_id,
    ).first()

    if not existing:
        # Créer l'association
        association = ChantierOuvrierModel(
            chantier_id=chantier_id,
            user_id=request.user_id,
        )
        db.add(association)
        db.commit()

    # Récupérer le chantier mis à jour
    try:
        result = controller.get_by_id(chantier_id)
        return _transform_chantier_response(result, controller, user_repo, db)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.delete("/{chantier_id}/ouvriers/{user_id}", response_model=ChantierResponse)
def retirer_ouvrier(
    chantier_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    controller: ChantierController = Depends(get_chantier_controller),
    user_repo: UserRepository = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
):
    """Retire un ouvrier du chantier. RBAC: conducteur ou admin requis."""
    from ..persistence import ChantierOuvrierModel

    # Supprimer l'association
    db.query(ChantierOuvrierModel).filter(
        ChantierOuvrierModel.chantier_id == chantier_id,
        ChantierOuvrierModel.user_id == user_id,
    ).delete()
    db.commit()

    # Récupérer le chantier mis à jour
    try:
        result = controller.get_by_id(chantier_id)
        return _transform_chantier_response(result, controller, user_repo, db)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


# =============================================================================
# Routes de gestion des contacts (CHT-07 - Multi-contacts)
# =============================================================================


@router.get("/{chantier_id}/contacts", response_model=List[ContactChantierResponse])
def list_contacts(
    chantier_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Liste tous les contacts d'un chantier.

    Args:
        chantier_id: ID du chantier.
        db: Session base de données.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Liste des contacts du chantier.
    """
    contacts = db.query(ContactChantierModel).filter(
        ContactChantierModel.chantier_id == chantier_id
    ).all()

    return [
        ContactChantierResponse(
            id=c.id,
            nom=c.nom,
            telephone=c.telephone,
            profession=c.profession,
        )
        for c in contacts
    ]


@router.post("/{chantier_id}/contacts", response_model=ContactChantierResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    chantier_id: int,
    request: ContactChantierCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Crée un nouveau contact pour un chantier.

    Args:
        chantier_id: ID du chantier.
        request: Données du contact.
        db: Session base de données.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le contact créé.
    """
    contact = ContactChantierModel(
        chantier_id=chantier_id,
        nom=request.nom,
        telephone=request.telephone,
        profession=request.profession,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)

    return ContactChantierResponse(
        id=contact.id,
        nom=contact.nom,
        telephone=contact.telephone,
        profession=contact.profession,
    )


@router.put("/{chantier_id}/contacts/{contact_id}", response_model=ContactChantierResponse)
def update_contact(
    chantier_id: int,
    contact_id: int,
    request: ContactChantierUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Met à jour un contact.

    Args:
        chantier_id: ID du chantier.
        contact_id: ID du contact.
        request: Données de mise à jour.
        db: Session base de données.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Le contact mis à jour.
    """
    contact = db.query(ContactChantierModel).filter(
        ContactChantierModel.id == contact_id,
        ContactChantierModel.chantier_id == chantier_id,
    ).first()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact {contact_id} non trouvé pour le chantier {chantier_id}",
        )

    if request.nom is not None:
        contact.nom = request.nom
    if request.telephone is not None:
        contact.telephone = request.telephone
    if request.profession is not None:
        contact.profession = request.profession

    db.commit()
    db.refresh(contact)

    return ContactChantierResponse(
        id=contact.id,
        nom=contact.nom,
        telephone=contact.telephone,
        profession=contact.profession,
    )


@router.delete("/{chantier_id}/contacts/{contact_id}")
def delete_contact(
    chantier_id: int,
    contact_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Supprime un contact.

    Args:
        chantier_id: ID du chantier.
        contact_id: ID du contact.
        db: Session base de données.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Confirmation de suppression.
    """
    contact = db.query(ContactChantierModel).filter(
        ContactChantierModel.id == contact_id,
        ContactChantierModel.chantier_id == chantier_id,
    ).first()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact {contact_id} non trouvé pour le chantier {chantier_id}",
        )

    db.delete(contact)
    db.commit()

    return {"deleted": True, "id": contact_id}


# =============================================================================
# Routes de gestion des phases (Chantiers en plusieurs étapes)
# =============================================================================


@router.get("/{chantier_id}/phases", response_model=List[PhaseChantierResponse])
def list_phases(
    chantier_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Liste toutes les phases d'un chantier.

    Args:
        chantier_id: ID du chantier.
        db: Session base de données.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Liste des phases du chantier ordonnées.
    """
    phases = db.query(PhaseChantierModel).filter(
        PhaseChantierModel.chantier_id == chantier_id
    ).order_by(PhaseChantierModel.ordre).all()

    return [
        PhaseChantierResponse(
            id=p.id,
            nom=p.nom,
            description=p.description,
            ordre=p.ordre,
            date_debut=p.date_debut.isoformat() if p.date_debut else None,
            date_fin=p.date_fin.isoformat() if p.date_fin else None,
        )
        for p in phases
    ]


@router.post("/{chantier_id}/phases", response_model=PhaseChantierResponse, status_code=status.HTTP_201_CREATED)
def create_phase(
    chantier_id: int,
    request: PhaseChantierCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Crée une nouvelle phase pour un chantier.

    Args:
        chantier_id: ID du chantier.
        request: Données de la phase.
        db: Session base de données.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        La phase créée.
    """
    from datetime import date as date_type

    # Calculer l'ordre si non fourni (dernier + 1)
    if request.ordre is None or request.ordre == 1:
        max_ordre = db.query(PhaseChantierModel).filter(
            PhaseChantierModel.chantier_id == chantier_id
        ).count()
        ordre = max_ordre + 1
    else:
        ordre = request.ordre

    # Parser les dates si fournies
    date_debut = None
    date_fin = None
    if request.date_debut:
        date_debut = date_type.fromisoformat(request.date_debut)
    if request.date_fin:
        date_fin = date_type.fromisoformat(request.date_fin)

    phase = PhaseChantierModel(
        chantier_id=chantier_id,
        nom=request.nom,
        description=request.description,
        ordre=ordre,
        date_debut=date_debut,
        date_fin=date_fin,
    )
    db.add(phase)
    db.commit()
    db.refresh(phase)

    return PhaseChantierResponse(
        id=phase.id,
        nom=phase.nom,
        description=phase.description,
        ordre=phase.ordre,
        date_debut=phase.date_debut.isoformat() if phase.date_debut else None,
        date_fin=phase.date_fin.isoformat() if phase.date_fin else None,
    )


@router.put("/{chantier_id}/phases/{phase_id}", response_model=PhaseChantierResponse)
def update_phase(
    chantier_id: int,
    phase_id: int,
    request: PhaseChantierUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Met à jour une phase.

    Args:
        chantier_id: ID du chantier.
        phase_id: ID de la phase.
        request: Données de mise à jour.
        db: Session base de données.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        La phase mise à jour.
    """
    from datetime import date as date_type

    phase = db.query(PhaseChantierModel).filter(
        PhaseChantierModel.id == phase_id,
        PhaseChantierModel.chantier_id == chantier_id,
    ).first()

    if not phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Phase {phase_id} non trouvée pour le chantier {chantier_id}",
        )

    if request.nom is not None:
        phase.nom = request.nom
    if request.description is not None:
        phase.description = request.description
    if request.ordre is not None:
        phase.ordre = request.ordre
    if request.date_debut is not None:
        phase.date_debut = date_type.fromisoformat(request.date_debut) if request.date_debut else None
    if request.date_fin is not None:
        phase.date_fin = date_type.fromisoformat(request.date_fin) if request.date_fin else None

    db.commit()
    db.refresh(phase)

    return PhaseChantierResponse(
        id=phase.id,
        nom=phase.nom,
        description=phase.description,
        ordre=phase.ordre,
        date_debut=phase.date_debut.isoformat() if phase.date_debut else None,
        date_fin=phase.date_fin.isoformat() if phase.date_fin else None,
    )


@router.delete("/{chantier_id}/phases/{phase_id}")
def delete_phase(
    chantier_id: int,
    phase_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Supprime une phase.

    Args:
        chantier_id: ID du chantier.
        phase_id: ID de la phase.
        db: Session base de données.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Confirmation de suppression.
    """
    phase = db.query(PhaseChantierModel).filter(
        PhaseChantierModel.id == phase_id,
        PhaseChantierModel.chantier_id == chantier_id,
    ).first()

    if not phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Phase {phase_id} non trouvée pour le chantier {chantier_id}",
        )

    db.delete(phase)
    db.commit()

    return {"deleted": True, "id": phase_id}


# =============================================================================
# Helpers
# =============================================================================


def _get_user_summary(user_id: int, user_repo: UserRepository) -> Optional[UserPublicSummary]:
    """
    Récupère les infos publiques d'un utilisateur pour l'inclusion dans un chantier.

    RGPD: Ne retourne PAS l'email ni le téléphone des utilisateurs.
    Ces données sensibles ne doivent pas être exposées dans les réponses API
    pour les autres utilisateurs.

    Args:
        user_id: ID de l'utilisateur à récupérer.
        user_repo: Repository pour accéder aux utilisateurs.

    Returns:
        UserPublicSummary avec les données publiques, ou None si non trouvé.
    """
    try:
        user = user_repo.find_by_id(user_id)
        if user:
            return UserPublicSummary(
                id=str(user.id),
                nom=user.nom,
                prenom=user.prenom,
                role=user.role.value,
                type_utilisateur=user.type_utilisateur.value,
                metier=user.metier,
                couleur=str(user.couleur) if user.couleur else None,
                is_active=user.is_active,
            )
        return None
    except (AttributeError, ValueError, TypeError):
        # Erreurs de conversion de types ou attributs manquants
        return None


def _transform_chantier_response(
    chantier_dict: dict,
    controller: ChantierController,
    user_repo: Optional[UserRepository] = None,
    db: Optional[Session] = None,
) -> ChantierResponse:
    """
    Transforme un dictionnaire chantier du controller en ChantierResponse.

    Convertit les IDs des conducteurs/chefs/ouvriers en objets User complets.
    """
    # Récupérer les coordonnées GPS
    coords = chantier_dict.get("coordonnees_gps") or {}
    latitude = coords.get("latitude") if coords else None
    longitude = coords.get("longitude") if coords else None

    # Récupérer le contact legacy (premier contact)
    contact = chantier_dict.get("contact") or {}
    contact_nom = contact.get("nom") if contact else None
    contact_telephone = contact.get("telephone") if contact else None

    # Récupérer les contacts multiples
    contacts_data = chantier_dict.get("contacts", [])
    contacts = [
        ContactResponse(
            nom=c.get("nom", ""),
            profession=c.get("profession"),
            telephone=c.get("telephone"),
        )
        for c in contacts_data
    ] if contacts_data else []

    # Si pas de contacts mais contact legacy, créer un contact
    if not contacts and contact_nom:
        contacts = [ContactResponse(
            nom=contact_nom,
            profession=None,
            telephone=contact_telephone,
        )]

    # Récupérer les IDs des conducteurs et chefs
    conducteur_ids = chantier_dict.get("conducteur_ids", [])
    chef_chantier_ids = chantier_dict.get("chef_chantier_ids", [])

    # Récupérer les IDs des ouvriers depuis la base de données
    ouvrier_ids = []
    if db:
        ouvrier_records = db.query(ChantierOuvrierModel).filter(
            ChantierOuvrierModel.chantier_id == chantier_dict.get("id")
        ).all()
        ouvrier_ids = [r.user_id for r in ouvrier_records]

    # Récupérer les objets User complets si le repo est disponible
    conducteurs = []
    chefs = []
    ouvriers = []

    if user_repo:
        for uid in conducteur_ids:
            user_summary = _get_user_summary(uid, user_repo)
            if user_summary:
                conducteurs.append(user_summary)

        for uid in chef_chantier_ids:
            user_summary = _get_user_summary(uid, user_repo)
            if user_summary:
                chefs.append(user_summary)

        for uid in ouvrier_ids:
            user_summary = _get_user_summary(uid, user_repo)
            if user_summary:
                ouvriers.append(user_summary)

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
        contacts=contacts,
        heures_estimees=chantier_dict.get("heures_estimees"),
        date_debut_prevue=chantier_dict.get("date_debut"),
        date_fin_prevue=chantier_dict.get("date_fin"),
        description=chantier_dict.get("description"),
        conducteurs=conducteurs,
        chefs=chefs,
        ouvriers=ouvriers,
        created_at=chantier_dict.get("created_at", ""),
        updated_at=chantier_dict.get("updated_at"),
    )
