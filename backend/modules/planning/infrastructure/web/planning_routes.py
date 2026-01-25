"""Routes FastAPI pour le module planning.

Ce module definit les endpoints API pour le Planning Operationnel
selon CDC Section 5 (PLN-01 a PLN-28).
"""

from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query

from ...adapters.controllers import PlanningController
from ...adapters.controllers.planning_schemas import (
    CreateAffectationRequest,
    UpdateAffectationRequest,
    AffectationResponse,
    PlanningFiltersRequest,
    DuplicateAffectationsRequest,
    DeleteResponse,
    NonPlanifiesResponse,
    ResizeAffectationRequest,
)
from ...application.use_cases import (
    AffectationConflictError,
    AffectationNotFoundError,
    InvalidDateRangeError,
    NoAffectationsToDuplicateError,
)
from .dependencies import get_planning_controller
from shared.infrastructure.web import get_current_user_id, get_current_user_role

router = APIRouter(prefix="/planning", tags=["Planning"])


# =============================================================================
# Routes CRUD Affectations
# =============================================================================


@router.post(
    "/affectations",
    response_model=AffectationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Creer une affectation",
    responses={
        201: {"description": "Affectation creee avec succes"},
        400: {"description": "Conflit ou donnees invalides"},
        403: {"description": "Non autorise"},
    },
)
def create_affectation(
    request: CreateAffectationRequest,
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    controller: PlanningController = Depends(get_planning_controller),
):
    """
    Cree une nouvelle affectation (PLN-04 a PLN-09).

    Seuls les admin et conducteur peuvent creer des affectations.

    - **type_affectation = unique**: Cree une seule affectation pour la date donnee.
    - **type_affectation = recurrente**: Cree plusieurs affectations selon les jours
      de recurrence jusqu'a la date de fin.

    Args:
        request: Donnees de creation de l'affectation.
        current_user_id: ID de l'utilisateur connecte.
        current_user_role: Role de l'utilisateur.
        controller: Controller du planning.

    Returns:
        L'affectation creee (ou la premiere d'une serie recurrente).

    Raises:
        HTTPException 400: Conflit avec affectation existante ou donnees invalides.
        HTTPException 403: Utilisateur non autorise.
    """
    # Verifier les permissions
    if current_user_role not in ("admin", "conducteur"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les admin et conducteur peuvent creer des affectations",
        )

    try:
        result = controller.create(request, current_user_id)
        return result
    except AffectationConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except InvalidDateRangeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/affectations",
    response_model=List[AffectationResponse],
    summary="Recuperer le planning",
    responses={
        200: {"description": "Liste des affectations"},
    },
)
def get_planning(
    date_debut: date = Query(..., description="Date de debut de la periode"),
    date_fin: date = Query(..., description="Date de fin de la periode"),
    utilisateur_ids: Optional[List[int]] = Query(
        None, description="Filtrer par IDs utilisateurs"
    ),
    chantier_ids: Optional[List[int]] = Query(
        None, description="Filtrer par IDs chantiers"
    ),
    metiers: Optional[List[str]] = Query(None, description="Filtrer par metiers"),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    controller: PlanningController = Depends(get_planning_controller),
):
    """
    Recupere le planning pour une periode (PLN-01 a PLN-03).

    Le planning est filtre selon le role de l'utilisateur:
    - **Admin/Conducteur**: Voient tout le planning.
    - **Chef de chantier**: Voit uniquement ses chantiers.
    - **Compagnon**: Voit uniquement son planning.

    Args:
        date_debut: Date de debut de la periode (incluse).
        date_fin: Date de fin de la periode (incluse).
        utilisateur_ids: Liste d'IDs utilisateurs a filtrer (optionnel).
        chantier_ids: Liste d'IDs chantiers a filtrer (optionnel).
        metiers: Liste de metiers a filtrer (optionnel).
        current_user_id: ID de l'utilisateur connecte.
        current_user_role: Role de l'utilisateur.
        controller: Controller du planning.

    Returns:
        Liste des affectations avec enrichissement (noms, couleurs).
    """
    filters = PlanningFiltersRequest(
        date_debut=date_debut,
        date_fin=date_fin,
        utilisateur_ids=utilisateur_ids,
        chantier_ids=chantier_ids,
        metiers=metiers,
        planifies_only=False,
        non_planifies_only=False,
    )
    return controller.get_planning(filters, current_user_id, current_user_role)


@router.get(
    "/affectations/{affectation_id}",
    response_model=AffectationResponse,
    summary="Recuperer une affectation",
    responses={
        200: {"description": "Affectation trouvee"},
        404: {"description": "Affectation non trouvee"},
    },
)
def get_affectation(
    affectation_id: int,
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    controller: PlanningController = Depends(get_planning_controller),
):
    """
    Recupere une affectation par son ID.

    Args:
        affectation_id: ID de l'affectation.
        current_user_id: ID de l'utilisateur connecte.
        current_user_role: Role de l'utilisateur.
        controller: Controller du planning.

    Returns:
        L'affectation demandee.

    Raises:
        HTTPException 404: Affectation non trouvee.
    """
    # Utiliser le get_planning avec un filtre large pour trouver l'affectation
    # Cela respecte aussi les permissions par role
    # Note: Pour une implementation plus efficace, on pourrait ajouter un use case dedie
    from datetime import timedelta

    today = date.today()
    filters = PlanningFiltersRequest(
        date_debut=today - timedelta(days=365),
        date_fin=today + timedelta(days=365),
    )

    affectations = controller.get_planning(filters, current_user_id, current_user_role)
    for aff in affectations:
        if aff["id"] == affectation_id:
            return aff

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Affectation {affectation_id} non trouvee",
    )


@router.put(
    "/affectations/{affectation_id}",
    response_model=AffectationResponse,
    summary="Modifier une affectation",
    responses={
        200: {"description": "Affectation modifiee"},
        400: {"description": "Donnees invalides"},
        403: {"description": "Non autorise"},
        404: {"description": "Affectation non trouvee"},
    },
)
def update_affectation(
    affectation_id: int,
    request: UpdateAffectationRequest,
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    controller: PlanningController = Depends(get_planning_controller),
):
    """
    Met a jour une affectation (PLN-07, PLN-08).

    Seuls les admin et conducteur peuvent modifier des affectations.

    Args:
        affectation_id: ID de l'affectation a modifier.
        request: Donnees de mise a jour.
        current_user_id: ID de l'utilisateur connecte.
        current_user_role: Role de l'utilisateur.
        controller: Controller du planning.

    Returns:
        L'affectation modifiee.

    Raises:
        HTTPException 400: Donnees invalides.
        HTTPException 403: Utilisateur non autorise.
        HTTPException 404: Affectation non trouvee.
    """
    # Verifier les permissions
    if current_user_role not in ("admin", "conducteur"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les admin et conducteur peuvent modifier des affectations",
        )

    try:
        result = controller.update(affectation_id, request, current_user_id)
        return result
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


@router.delete(
    "/affectations/{affectation_id}",
    response_model=DeleteResponse,
    summary="Supprimer une affectation",
    responses={
        200: {"description": "Affectation supprimee"},
        403: {"description": "Non autorise"},
        404: {"description": "Affectation non trouvee"},
    },
)
def delete_affectation(
    affectation_id: int,
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    controller: PlanningController = Depends(get_planning_controller),
):
    """
    Supprime une affectation (PLN-09).

    Seuls les admin et conducteur peuvent supprimer des affectations.

    Args:
        affectation_id: ID de l'affectation a supprimer.
        current_user_id: ID de l'utilisateur connecte.
        current_user_role: Role de l'utilisateur.
        controller: Controller du planning.

    Returns:
        Confirmation de la suppression.

    Raises:
        HTTPException 403: Utilisateur non autorise.
        HTTPException 404: Affectation non trouvee.
    """
    # Verifier les permissions
    if current_user_role not in ("admin", "conducteur"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les admin et conducteur peuvent supprimer des affectations",
        )

    try:
        result = controller.delete(affectation_id, current_user_id)
        return result
    except AffectationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.post(
    "/affectations/{affectation_id}/resize",
    response_model=List[AffectationResponse],
    status_code=status.HTTP_200_OK,
    summary="Redimensionner une affectation",
    responses={
        200: {"description": "Affectation(s) creees/mises a jour"},
        400: {"description": "Conflit ou donnees invalides"},
        403: {"description": "Non autorise"},
        404: {"description": "Affectation non trouvee"},
    },
)
def resize_affectation(
    affectation_id: int,
    request: ResizeAffectationRequest,
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    controller: PlanningController = Depends(get_planning_controller),
):
    """
    Redimensionne une affectation en creant/supprimant des jours.

    Permet d'etendre ou reduire la duree d'une affectation via drag & drop
    sur les bords. Cree de nouvelles affectations pour les jours manquants
    ou supprime les affectations en trop.

    Seuls les admin et conducteur peuvent redimensionner des affectations.

    Args:
        affectation_id: ID de l'affectation de reference.
        request: Nouvelles dates de debut/fin.
        current_user_id: ID de l'utilisateur connecte.
        current_user_role: Role de l'utilisateur.
        controller: Controller du planning.

    Returns:
        Liste des affectations dans la nouvelle plage.

    Raises:
        HTTPException 400: Conflit avec affectation existante.
        HTTPException 403: Utilisateur non autorise.
        HTTPException 404: Affectation non trouvee.
    """
    # Verifier les permissions
    if current_user_role not in ("admin", "conducteur"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les admin et conducteur peuvent redimensionner des affectations",
        )

    try:
        result = controller.resize(affectation_id, request, current_user_id)
        return result
    except AffectationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except AffectationConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# =============================================================================
# Routes de duplication (PLN-13, PLN-14)
# =============================================================================


@router.post(
    "/affectations/duplicate",
    response_model=List[AffectationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Dupliquer des affectations",
    responses={
        201: {"description": "Affectations dupliquees"},
        400: {"description": "Conflit ou aucune affectation source"},
        403: {"description": "Non autorise"},
    },
)
def duplicate_affectations(
    request: DuplicateAffectationsRequest,
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    controller: PlanningController = Depends(get_planning_controller),
):
    """
    Duplique les affectations d'une periode vers une autre (PLN-13, PLN-14).

    Copie les affectations d'un utilisateur de la periode source vers la periode cible,
    en conservant la structure relative des jours (ex: dupliquer la semaine precedente).

    Seuls les admin et conducteur peuvent dupliquer des affectations.

    Args:
        request: Donnees de duplication.
        current_user_id: ID de l'utilisateur connecte.
        current_user_role: Role de l'utilisateur.
        controller: Controller du planning.

    Returns:
        Liste des nouvelles affectations creees.

    Raises:
        HTTPException 400: Conflit avec affectation existante ou aucune source.
        HTTPException 403: Utilisateur non autorise.
    """
    # Verifier les permissions
    if current_user_role not in ("admin", "conducteur"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les admin et conducteur peuvent dupliquer des affectations",
        )

    try:
        result = controller.duplicate(request, current_user_id)
        return result
    except NoAffectationsToDuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except AffectationConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


# =============================================================================
# Routes utilisateurs non planifies (PLN-10)
# =============================================================================


@router.get(
    "/non-planifies",
    response_model=NonPlanifiesResponse,
    summary="Recuperer les utilisateurs non planifies",
    responses={
        200: {"description": "Liste des IDs utilisateurs non planifies"},
        403: {"description": "Non autorise"},
    },
)
def get_non_planifies(
    date_debut: date = Query(..., description="Date de debut de la periode"),
    date_fin: date = Query(..., description="Date de fin de la periode"),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    controller: PlanningController = Depends(get_planning_controller),
):
    """
    Recupere les utilisateurs non planifies sur une periode (PLN-10).

    Identifie les utilisateurs actifs qui n'ont aucune affectation
    sur la periode specifiee.

    Seuls les admin et conducteur peuvent voir cette information.

    Args:
        date_debut: Date de debut de la periode (incluse).
        date_fin: Date de fin de la periode (incluse).
        current_user_id: ID de l'utilisateur connecte.
        current_user_role: Role de l'utilisateur.
        controller: Controller du planning.

    Returns:
        Liste des IDs utilisateurs non planifies avec le compte.

    Raises:
        HTTPException 403: Utilisateur non autorise.
    """
    # Verifier les permissions
    if current_user_role not in ("admin", "conducteur"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les admin et conducteur peuvent voir les non planifies",
        )

    try:
        result = controller.get_non_planifies(date_debut, date_fin)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# =============================================================================
# Routes par chantier (vue onglet Chantiers)
# =============================================================================


@router.get(
    "/chantiers/{chantier_id}/affectations",
    response_model=List[AffectationResponse],
    summary="Recuperer les affectations d'un chantier",
    responses={
        200: {"description": "Liste des affectations du chantier"},
    },
)
def get_affectations_chantier(
    chantier_id: int,
    date_debut: date = Query(..., description="Date de debut de la periode"),
    date_fin: date = Query(..., description="Date de fin de la periode"),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    controller: PlanningController = Depends(get_planning_controller),
):
    """
    Recupere les affectations pour un chantier specifique.

    Utile pour la vue planning de l'onglet Chantiers.
    Le resultat est filtre selon le role de l'utilisateur.

    Args:
        chantier_id: ID du chantier.
        date_debut: Date de debut de la periode (incluse).
        date_fin: Date de fin de la periode (incluse).
        current_user_id: ID de l'utilisateur connecte.
        current_user_role: Role de l'utilisateur.
        controller: Controller du planning.

    Returns:
        Liste des affectations du chantier.
    """
    return controller.get_planning_by_chantier(
        chantier_id, date_debut, date_fin, current_user_id, current_user_role
    )


# =============================================================================
# Routes par utilisateur (vue onglet Utilisateurs)
# =============================================================================


@router.get(
    "/utilisateurs/{utilisateur_id}/affectations",
    response_model=List[AffectationResponse],
    summary="Recuperer les affectations d'un utilisateur",
    responses={
        200: {"description": "Liste des affectations de l'utilisateur"},
    },
)
def get_affectations_utilisateur(
    utilisateur_id: int,
    date_debut: date = Query(..., description="Date de debut de la periode"),
    date_fin: date = Query(..., description="Date de fin de la periode"),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    controller: PlanningController = Depends(get_planning_controller),
):
    """
    Recupere les affectations pour un utilisateur specifique.

    Utile pour la vue planning de l'onglet Utilisateurs.
    Le resultat est filtre selon le role de l'utilisateur connecte.

    Args:
        utilisateur_id: ID de l'utilisateur cible.
        date_debut: Date de debut de la periode (incluse).
        date_fin: Date de fin de la periode (incluse).
        current_user_id: ID de l'utilisateur connecte.
        current_user_role: Role de l'utilisateur.
        controller: Controller du planning.

    Returns:
        Liste des affectations de l'utilisateur.
    """
    return controller.get_planning_by_utilisateur(
        utilisateur_id, date_debut, date_fin, current_user_id, current_user_role
    )


# =============================================================================
# Route de creation en masse (pour recurrence)
# =============================================================================


@router.post(
    "/affectations/bulk",
    response_model=List[AffectationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Creer plusieurs affectations (recurrence)",
    responses={
        201: {"description": "Affectations creees"},
        400: {"description": "Conflit ou donnees invalides"},
        403: {"description": "Non autorise"},
    },
)
def create_affectations_bulk(
    request: CreateAffectationRequest,
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    controller: PlanningController = Depends(get_planning_controller),
):
    """
    Cree plusieurs affectations en une seule requete.

    Identique a la creation simple mais retourne TOUTES les affectations
    creees (utile pour les affectations recurrentes).

    Seuls les admin et conducteur peuvent creer des affectations.

    Args:
        request: Donnees de creation (avec recurrence).
        current_user_id: ID de l'utilisateur connecte.
        current_user_role: Role de l'utilisateur.
        controller: Controller du planning.

    Returns:
        Liste de toutes les affectations creees.

    Raises:
        HTTPException 400: Conflit ou donnees invalides.
        HTTPException 403: Utilisateur non autorise.
    """
    # Verifier les permissions
    if current_user_role not in ("admin", "conducteur"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les admin et conducteur peuvent creer des affectations",
        )

    try:
        result = controller.create_many(request, current_user_id)
        return result
    except AffectationConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except InvalidDateRangeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
