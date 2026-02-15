"""Routes FastAPI pour la gestion des chantiers."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from sqlalchemy.orm import Session

from ...adapters.controllers import ChantierController
from shared.infrastructure.database import get_db
from ...application.use_cases import (
    CodeChantierAlreadyExistsError,
    InvalidDatesError,
    ChantierNotFoundError,
    ChantierFermeError,
    ChantierActifError,
    TransitionNonAutoriseeError,
    PrerequisReceptionNonRemplisError,  # GAP-CHT-001
    FermerChantierUseCase,
    PrerequisClotureNonRemplisError,
    FermetureForceeNonAutoriseeError,
)
from ...domain.events.chantier_created import ChantierCreatedEvent
from .dependencies import get_chantier_controller, get_chantier_repository, get_user_repository, get_fermer_chantier_use_case
from .chantier_presenter import transform_chantier_response, chantier_dto_to_dict
from .chantier_schemas import (
    CoordonneesGPSResponse, ContactResponse, ContactRequest,
    ContactChantierResponse, ContactChantierCreate, ContactChantierUpdate,
    PhaseChantierResponse, PhaseChantierCreate, PhaseChantierUpdate,
    CreateChantierRequest, UpdateChantierRequest,
    ChangeStatutRequest, AssignResponsableRequest,
    UserPublicSummary,
    ChantierResponse, ChantierListResponse, DeleteResponse,
)
from shared.infrastructure.web import (
    get_current_user_id,
    require_conducteur_or_admin,
    require_admin,
)
from shared.infrastructure.event_bus.dependencies import get_event_bus
from shared.infrastructure.event_bus import EventBus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chantiers", tags=["chantiers"])




# =============================================================================
# Routes CRUD Chantiers
# =============================================================================


@router.post("", response_model=ChantierResponse, status_code=status.HTTP_201_CREATED)
async def create_chantier(
    request: CreateChantierRequest,
    event_bus: EventBus = Depends(get_event_bus),
    controller: ChantierController = Depends(get_chantier_controller),
    user_repo: "UserRepository" = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC: conducteur ou admin requis
) -> ChantierResponse:
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
            type_travaux=request.type_travaux,
            batiment_plus_2ans=request.batiment_plus_2ans,
            usage_habitation=request.usage_habitation,
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

        return transform_chantier_response(result, controller, user_repo)
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


# Codes des chantiers spéciaux (absences) à exclure par défaut
CHANTIERS_SPECIAUX_CODES = ['CONGES', 'MALADIE', 'FORMATION', 'RTT', 'ABSENT']


@router.get("", response_model=ChantierListResponse)
def list_chantiers(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(100, ge=1, le=500, description="Nombre d'éléments par page"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    search: Optional[str] = Query(None, max_length=100, description="Recherche par nom ou code"),
    exclude_special: bool = Query(True, description="Exclure les chantiers spéciaux (absences)"),
    controller: ChantierController = Depends(get_chantier_controller),
    chantier_repo=Depends(get_chantier_repository),
    user_repo: "UserRepository" = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
) -> ChantierListResponse:
    """Liste les chantiers avec pagination et filtres."""
    # Convertir page/size en skip/limit
    skip = (page - 1) * size

    # Codes à exclure si exclude_special est True
    exclude_codes = CHANTIERS_SPECIAUX_CODES if exclude_special else None

    result = controller.list(
        skip=skip,
        limit=size,
        statut=statut,
        search=search,
        exclude_codes=exclude_codes,
    )

    # Convertir au format frontend
    total = result.get("total", 0)
    pages = (total + size - 1) // size if size > 0 else 0
    chantiers_data = result.get("chantiers", [])

    return ChantierListResponse(
        items=[transform_chantier_response(c, controller, user_repo, chantier_repo) for c in chantiers_data],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{chantier_id}", response_model=ChantierResponse)
def get_chantier(
    chantier_id: int,
    controller: ChantierController = Depends(get_chantier_controller),
    chantier_repo=Depends(get_chantier_repository),
    user_repo: "UserRepository" = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
) -> ChantierResponse:
    """Récupère un chantier par son ID."""
    try:
        result = controller.get_by_id(chantier_id)
        return transform_chantier_response(result, controller, user_repo, chantier_repo)
    except ChantierNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.get("/code/{code}", response_model=ChantierResponse)
def get_chantier_by_code(
    code: str,
    controller: ChantierController = Depends(get_chantier_controller),
    user_repo: "UserRepository" = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
) -> ChantierResponse:
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
        return transform_chantier_response(result, controller, user_repo)
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
    user_repo: "UserRepository" = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC: conducteur ou admin requis
) -> ChantierResponse:
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
            maitre_ouvrage=request.maitre_ouvrage,
            type_travaux=request.type_travaux,
            batiment_plus_2ans=request.batiment_plus_2ans,
            usage_habitation=request.usage_habitation,
        )
        response = transform_chantier_response(result, controller, user_repo)
        return response
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
    except Exception as e:
        logger.exception(
            "Erreur mise a jour chantier %d", chantier_id,
            extra={"event": "chantier.update.error", "chantier_id": chantier_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise a jour du chantier",
        )


@router.delete("/{chantier_id}", response_model=DeleteResponse)
def delete_chantier(
    chantier_id: int,
    force: bool = Query(False, description="Forcer la suppression d'un chantier actif"),
    controller: ChantierController = Depends(get_chantier_controller),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_admin),  # RBAC: admin uniquement pour suppression
) -> DeleteResponse:
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
    user_repo: "UserRepository" = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC: conducteur ou admin requis
) -> ChantierResponse:
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
        return transform_chantier_response(result, controller, user_repo)
    except PrerequisReceptionNonRemplisError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "prerequis_non_remplis",
                "message": str(e),
                "prerequis_manquants": e.prerequis_manquants,
                "details": e.details
            }
        )
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
    user_repo: "UserRepository" = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
) -> ChantierResponse:
    """Passe le chantier en statut 'En cours'. RBAC: conducteur ou admin requis."""
    try:
        result = controller.demarrer(chantier_id)
        return transform_chantier_response(result, controller, user_repo)
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
    user_repo: "UserRepository" = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
) -> ChantierResponse:
    """Passe le chantier en statut 'Réceptionné'. RBAC: conducteur ou admin requis."""
    try:
        result = controller.receptionner(chantier_id)
        return transform_chantier_response(result, controller, user_repo)
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
    force: bool = Query(False, description="Forcer la fermeture sans verification des pre-requis"),
    use_case: FermerChantierUseCase = Depends(get_fermer_chantier_use_case),
    user_repo: "UserRepository" = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
) -> ChantierResponse:
    """Passe le chantier en statut 'Ferme'. RBAC: conducteur ou admin requis.

    Verifie les pre-requis financiers avant fermeture (GAP #8):
    - Achats tous clotures (factures ou refuses)
    - Situations de travaux toutes validees ou facturees
    - Avenants en brouillon (avertissement non bloquant)

    Si les pre-requis ne sont pas remplis, retourne HTTP 409 Conflict.
    Le parametre force=True permet de bypasser les verifications.

    Args:
        chantier_id: ID du chantier a fermer.
        force: Si True, ignore les verifications de pre-requis.
        use_case: Use case de fermeture.
        user_repo: Repository utilisateurs.
        current_user_id: ID de l'utilisateur connecte.

    Returns:
        Le chantier mis a jour, avec avertissements eventuels.

    Raises:
        HTTPException 404: Chantier non trouve.
        HTTPException 400: Transition non autorisee.
        HTTPException 403: Force non autorise (non-admin).
        HTTPException 409: Pre-requis de cloture non remplis.
    """
    try:
        result = use_case.execute(
            chantier_id=chantier_id,
            force=force,
            role=_role,
            user_id=current_user_id,
        )
        chantier_dict = chantier_dto_to_dict(result.chantier)
        return transform_chantier_response(chantier_dict, None, user_repo)
    except FermetureForceeNonAutoriseeError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )
    except PrerequisClotureNonRemplisError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "prerequis_cloture_non_remplis",
                "message": e.message,
                "blocages": e.blocages,
                "avertissements": e.avertissements,
            },
        )
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
    user_repo: "UserRepository" = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
) -> ChantierResponse:
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
        return transform_chantier_response(result, controller, user_repo)
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
    user_repo: "UserRepository" = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
) -> ChantierResponse:
    """Retire un conducteur du chantier. RBAC: conducteur ou admin requis."""
    try:
        result = controller.retirer_conducteur(chantier_id, user_id)
        return transform_chantier_response(result, controller, user_repo)
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
    user_repo: "UserRepository" = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
) -> ChantierResponse:
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
        return transform_chantier_response(result, controller, user_repo)
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
    user_repo: "UserRepository" = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
) -> ChantierResponse:
    """Retire un chef de chantier. RBAC: conducteur ou admin requis."""
    try:
        result = controller.retirer_chef_chantier(chantier_id, user_id)
        return transform_chantier_response(result, controller, user_repo)
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
    chantier_repo=Depends(get_chantier_repository),
    controller: ChantierController = Depends(get_chantier_controller),
    user_repo: "UserRepository" = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
) -> ChantierResponse:
    """Assigne un ouvrier/intérimaire/sous-traitant au chantier.

    RBAC: Requiert le rôle conducteur ou admin.
    """
    chantier_repo.assign_ouvrier(chantier_id, request.user_id)

    try:
        result = controller.get_by_id(chantier_id)
        return transform_chantier_response(result, controller, user_repo, chantier_repo)
    except ChantierNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete("/{chantier_id}/ouvriers/{user_id}", response_model=ChantierResponse)
def retirer_ouvrier(
    chantier_id: int,
    user_id: int,
    chantier_repo=Depends(get_chantier_repository),
    controller: ChantierController = Depends(get_chantier_controller),
    user_repo: "UserRepository" = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC
) -> ChantierResponse:
    """Retire un ouvrier du chantier. RBAC: conducteur ou admin requis."""
    chantier_repo.remove_ouvrier(chantier_id, user_id)

    try:
        result = controller.get_by_id(chantier_id)
        return transform_chantier_response(result, controller, user_repo, chantier_repo)
    except ChantierNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


# =============================================================================
# Routes de gestion des contacts (CHT-07 - Multi-contacts)
# =============================================================================


@router.get("/{chantier_id}/contacts", response_model=List[ContactChantierResponse])
def list_contacts(
    chantier_id: int,
    chantier_repo=Depends(get_chantier_repository),
    current_user_id: int = Depends(get_current_user_id),
) -> List[ContactChantierResponse]:
    """Liste tous les contacts d'un chantier."""
    contacts = chantier_repo.list_contacts(chantier_id)
    return [
        ContactChantierResponse(
            id=c.id, nom=c.nom, telephone=c.telephone, profession=c.profession,
        )
        for c in contacts
    ]


@router.post("/{chantier_id}/contacts", response_model=ContactChantierResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    chantier_id: int,
    request: ContactChantierCreate,
    chantier_repo=Depends(get_chantier_repository),
    current_user_id: int = Depends(get_current_user_id),
) -> ContactChantierResponse:
    """Crée un nouveau contact pour un chantier."""
    contact = chantier_repo.create_contact(
        chantier_id, request.nom, request.telephone, request.profession,
    )
    return ContactChantierResponse(
        id=contact.id, nom=contact.nom, telephone=contact.telephone, profession=contact.profession,
    )


@router.put("/{chantier_id}/contacts/{contact_id}", response_model=ContactChantierResponse)
def update_contact(
    chantier_id: int,
    contact_id: int,
    request: ContactChantierUpdate,
    chantier_repo=Depends(get_chantier_repository),
    current_user_id: int = Depends(get_current_user_id),
) -> ContactChantierResponse:
    """Met à jour un contact."""
    result = chantier_repo.update_contact(
        chantier_id, contact_id,
        nom=request.nom, telephone=request.telephone, profession=request.profession,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact {contact_id} non trouvé pour le chantier {chantier_id}",
        )
    return ContactChantierResponse(
        id=result.id, nom=result.nom, telephone=result.telephone, profession=result.profession,
    )


@router.delete("/{chantier_id}/contacts/{contact_id}")
def delete_contact(
    chantier_id: int,
    contact_id: int,
    chantier_repo=Depends(get_chantier_repository),
    current_user_id: int = Depends(get_current_user_id),
) -> dict:
    """Supprime un contact."""
    if not chantier_repo.delete_contact(chantier_id, contact_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact {contact_id} non trouvé pour le chantier {chantier_id}",
        )
    return {"deleted": True, "id": contact_id}


# =============================================================================
# Routes de gestion des phases (Chantiers en plusieurs étapes)
# =============================================================================


@router.get("/{chantier_id}/phases", response_model=List[PhaseChantierResponse])
def list_phases(
    chantier_id: int,
    chantier_repo=Depends(get_chantier_repository),
    current_user_id: int = Depends(get_current_user_id),
) -> List[PhaseChantierResponse]:
    """Liste toutes les phases d'un chantier."""
    phases = chantier_repo.list_phases(chantier_id)
    return [
        PhaseChantierResponse(
            id=p.id, nom=p.nom, description=p.description, ordre=p.ordre,
            date_debut=p.date_debut.isoformat() if p.date_debut else None,
            date_fin=p.date_fin.isoformat() if p.date_fin else None,
        )
        for p in phases
    ]


@router.post("/{chantier_id}/phases", response_model=PhaseChantierResponse, status_code=status.HTTP_201_CREATED)
def create_phase(
    chantier_id: int,
    request: PhaseChantierCreate,
    chantier_repo=Depends(get_chantier_repository),
    current_user_id: int = Depends(get_current_user_id),
) -> PhaseChantierResponse:
    """Crée une nouvelle phase pour un chantier."""
    from datetime import date as date_type
    parsed_debut = date_type.fromisoformat(request.date_debut) if request.date_debut else None
    parsed_fin = date_type.fromisoformat(request.date_fin) if request.date_fin else None
    phase = chantier_repo.create_phase(
        chantier_id, request.nom,
        description=request.description, ordre=request.ordre,
        date_debut=parsed_debut, date_fin=parsed_fin,
    )
    return PhaseChantierResponse(
        id=phase.id, nom=phase.nom, description=phase.description, ordre=phase.ordre,
        date_debut=phase.date_debut.isoformat() if phase.date_debut else None,
        date_fin=phase.date_fin.isoformat() if phase.date_fin else None,
    )


@router.put("/{chantier_id}/phases/{phase_id}", response_model=PhaseChantierResponse)
def update_phase(
    chantier_id: int,
    phase_id: int,
    request: PhaseChantierUpdate,
    chantier_repo=Depends(get_chantier_repository),
    current_user_id: int = Depends(get_current_user_id),
) -> PhaseChantierResponse:
    """Met à jour une phase."""
    from datetime import date as date_type
    parsed_debut = date_type.fromisoformat(request.date_debut) if request.date_debut else None
    parsed_fin = date_type.fromisoformat(request.date_fin) if request.date_fin else None
    result = chantier_repo.update_phase(
        chantier_id, phase_id,
        nom=request.nom, description=request.description, ordre=request.ordre,
        date_debut=parsed_debut, date_fin=parsed_fin,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Phase {phase_id} non trouvée pour le chantier {chantier_id}",
        )
    return PhaseChantierResponse(
        id=result.id, nom=result.nom, description=result.description, ordre=result.ordre,
        date_debut=result.date_debut.isoformat() if result.date_debut else None,
        date_fin=result.date_fin.isoformat() if result.date_fin else None,
    )


@router.delete("/{chantier_id}/phases/{phase_id}")
def delete_phase(
    chantier_id: int,
    phase_id: int,
    chantier_repo=Depends(get_chantier_repository),
    current_user_id: int = Depends(get_current_user_id),
) -> dict:
    """Supprime une phase."""
    if not chantier_repo.delete_phase(chantier_id, phase_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Phase {phase_id} non trouvée pour le chantier {chantier_id}",
        )
    return {"deleted": True, "id": phase_id}
