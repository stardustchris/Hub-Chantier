"""Routes API pour le module planning de charge."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from shared.infrastructure.cache import cache_manager
from shared.infrastructure.web.dependencies import (
    get_current_user_id,
    get_current_user_role,
    require_conducteur_or_admin,
    require_chef_or_above,
)
from shared.infrastructure.audit import AuditService

# Cache key prefix for planning charge
CACHE_PREFIX = "planning_charge"


def _invalidate_planning_cache() -> None:
    """
    Invalide tous les caches du planning de charge.

    Supprime toutes les entrees de cache commencant par le prefixe
    CACHE_PREFIX pour forcer le rechargement des donnees.
    """
    cache_manager.invalidate_pattern(CACHE_PREFIX)

from ..application.use_cases import (
    CreateBesoinUseCase,
    UpdateBesoinUseCase,
    DeleteBesoinUseCase,
    GetPlanningChargeUseCase,
    GetBesoinsByChantierUseCase,
    GetOccupationDetailsUseCase,
    BesoinNotFoundError,
    BesoinAlreadyExistsError,
    InvalidSemaineRangeError,
)
from ..adapters.controllers import (
    PlanningChargeController,
    CreateBesoinRequest,
    UpdateBesoinRequest,
    PlanningChargeFiltersRequest,
    BesoinChargeResponse,
    PlanningChargeResponse,
    OccupationDetailsResponse,
    ListeBesoinResponse,
)
from .persistence import SQLAlchemyBesoinChargeRepository
from .providers import (
    SQLAlchemyChantierProvider,
    SQLAlchemyAffectationProvider,
    SQLAlchemyUtilisateurProvider,
)


router = APIRouter(prefix="/planning-charge", tags=["Planning de Charge"])


def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    """
    Factory pour le service d'audit.

    Args:
        db: Session de base de donnees injectee par FastAPI.

    Returns:
        Instance du service d'audit configuree.
    """
    return AuditService(db)


def get_controller(db: Session = Depends(get_db)) -> PlanningChargeController:
    """
    Factory pour le controller avec injection de dependances.

    Construit le controller avec toutes ses dependances (repositories,
    providers, use cases) pour les endpoints du planning de charge.

    Args:
        db: Session de base de donnees injectee par FastAPI.

    Returns:
        Instance du PlanningChargeController completement configuree.
    """
    repo = SQLAlchemyBesoinChargeRepository(db)

    # Providers pour integration avec autres modules
    chantier_provider = SQLAlchemyChantierProvider(db)
    affectation_provider = SQLAlchemyAffectationProvider(db)
    utilisateur_provider = SQLAlchemyUtilisateurProvider(db)

    # Creer les use cases avec providers
    create_uc = CreateBesoinUseCase(repo)
    update_uc = UpdateBesoinUseCase(repo)
    delete_uc = DeleteBesoinUseCase(repo)
    get_planning_uc = GetPlanningChargeUseCase(
        repo,
        chantier_provider=chantier_provider,
        affectation_provider=affectation_provider,
    )
    get_besoins_uc = GetBesoinsByChantierUseCase(repo)
    get_occupation_uc = GetOccupationDetailsUseCase(
        repo,
        utilisateur_provider=utilisateur_provider,
        affectation_provider=affectation_provider,
    )

    return PlanningChargeController(
        create_besoin_uc=create_uc,
        update_besoin_uc=update_uc,
        delete_besoin_uc=delete_uc,
        get_planning_uc=get_planning_uc,
        get_besoins_uc=get_besoins_uc,
        get_occupation_uc=get_occupation_uc,
    )


# =============================================================================
# ENDPOINTS LECTURE (Chef de chantier+)
# =============================================================================


@router.get(
    "",
    response_model=PlanningChargeResponse,
    summary="Recuperer le planning de charge (PDC-01)",
    description="Retourne la vue tabulaire complete avec chantiers en lignes et semaines en colonnes.",
)
def get_planning_charge(
    semaine_debut: str = Query(..., description="Semaine de debut (SXX-YYYY)"),
    semaine_fin: str = Query(..., description="Semaine de fin (SXX-YYYY)"),
    recherche: Optional[str] = Query(None, description="Recherche par nom de chantier"),
    mode_avance: bool = Query(False, description="Mode avance"),
    unite: str = Query("heures", description="Unite: heures ou jours_homme"),
    _role: str = Depends(require_chef_or_above),  # RBAC: Chef+ peut voir
    controller: PlanningChargeController = Depends(get_controller),
) -> PlanningChargeResponse:
    """
    Endpoint principal du planning de charge.

    RBAC: Accessible aux chefs de chantier, conducteurs et admins.

    Fonctionnalites:
    - PDC-01: Vue tabulaire chantiers x semaines
    - PDC-02: Compteur total chantiers
    - PDC-03: Barre de recherche
    - PDC-04: Toggle mode avance
    - PDC-05: Toggle Hrs / J/H
    - PDC-07 a PDC-10: Colonnes et cellules
    - PDC-11 a PDC-15: Footer avec indicateurs
    """
    try:
        request = PlanningChargeFiltersRequest(
            semaine_debut=semaine_debut,
            semaine_fin=semaine_fin,
            recherche=recherche,
            mode_avance=mode_avance,
            unite=unite,
        )
        return controller.get_planning_charge(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/occupation/{semaine_code}",
    response_model=OccupationDetailsResponse,
    summary="Details d'occupation par type (PDC-17)",
    description="Retourne le taux d'occupation par type/metier pour une semaine.",
)
def get_occupation_details(
    semaine_code: str,
    _role: str = Depends(require_chef_or_above),  # RBAC: Chef+ peut voir
    controller: PlanningChargeController = Depends(get_controller),
) -> OccupationDetailsResponse:
    """
    Modal details occupation.

    RBAC: Accessible aux chefs de chantier, conducteurs et admins.

    Affiche le taux d'occupation par type de metier
    avec code couleur pour une semaine donnee.
    """
    try:
        return controller.get_occupation_details(semaine_code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/chantiers/{chantier_id}/besoins",
    response_model=ListeBesoinResponse,
    summary="Besoins d'un chantier",
    description="Retourne les besoins d'un chantier sur une plage de semaines.",
)
def get_besoins_by_chantier(
    chantier_id: int,
    semaine_debut: str = Query(..., description="Semaine de debut"),
    semaine_fin: str = Query(..., description="Semaine de fin"),
    page: int = Query(1, ge=1, description="Numero de page"),
    page_size: int = Query(50, ge=1, le=100, description="Taille de la page"),
    _role: str = Depends(require_chef_or_above),  # RBAC: Chef+ peut voir
    controller: PlanningChargeController = Depends(get_controller),
) -> ListeBesoinResponse:
    """
    Recupere les besoins pour un chantier specifique.

    RBAC: Accessible aux chefs de chantier, conducteurs et admins.
    Supporte la pagination avec les parametres page et page_size.
    """
    try:
        return controller.get_besoins_by_chantier(
            chantier_id=chantier_id,
            semaine_debut=semaine_debut,
            semaine_fin=semaine_fin,
            page=page,
            page_size=page_size,
        )
    except InvalidSemaineRangeError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# ENDPOINTS MODIFICATION (Conducteur/Admin uniquement)
# =============================================================================


@router.post(
    "/besoins",
    response_model=BesoinChargeResponse,
    status_code=201,
    summary="Creer un besoin (PDC-16)",
    description="Cree un nouveau besoin en main d'oeuvre pour un chantier/semaine/type.",
)
def create_besoin(
    request_data: CreateBesoinRequest,
    request: Request,
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC: Conducteur+ seulement
    controller: PlanningChargeController = Depends(get_controller),
    audit: AuditService = Depends(get_audit_service),
) -> BesoinChargeResponse:
    """
    Modal planification des besoins.

    RBAC: Reserve aux conducteurs et administrateurs.

    Cree un besoin en main d'oeuvre pour:
    - Un chantier specifique
    - Une semaine donnee
    - Un type de metier
    """
    try:
        result = controller.create_besoin(request_data, current_user_id)

        # Invalidate cache after data modification
        _invalidate_planning_cache()

        # Audit Trail
        audit.log_action(
            entity_type="besoin_charge",
            entity_id=result.id,
            action="created",
            user_id=current_user_id,
            new_values={
                "chantier_id": result.chantier_id,
                "semaine_code": result.semaine_code,
                "type_metier": result.type_metier,
                "besoin_heures": result.besoin_heures,
            },
            ip_address=request.client.host if request.client else None,
        )

        return result
    except BesoinAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/besoins/{besoin_id}",
    response_model=BesoinChargeResponse,
    summary="Mettre a jour un besoin",
    description="Modifie un besoin existant.",
)
def update_besoin(
    besoin_id: int,
    request_data: UpdateBesoinRequest,
    request: Request,
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC: Conducteur+ seulement
    controller: PlanningChargeController = Depends(get_controller),
    audit: AuditService = Depends(get_audit_service),
) -> BesoinChargeResponse:
    """
    Met a jour un besoin existant.

    RBAC: Reserve aux conducteurs et administrateurs.
    """
    try:
        # Recuperer anciennes valeurs pour audit
        old_besoins = controller.get_besoins_uc.besoin_repo.find_by_id(besoin_id)
        old_values = None
        if old_besoins:
            old_values = {
                "besoin_heures": old_besoins.besoin_heures,
                "type_metier": old_besoins.type_metier.value,
                "note": old_besoins.note,
            }

        result = controller.update_besoin(besoin_id, request_data, current_user_id)

        # Invalidate cache after data modification
        _invalidate_planning_cache()

        # Audit Trail
        audit.log_action(
            entity_type="besoin_charge",
            entity_id=besoin_id,
            action="updated",
            user_id=current_user_id,
            old_values=old_values,
            new_values={
                "besoin_heures": result.besoin_heures,
                "type_metier": result.type_metier,
                "note": result.note,
            },
            ip_address=request.client.host if request.client else None,
        )

        return result
    except BesoinNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/besoins/{besoin_id}",
    status_code=204,
    summary="Supprimer un besoin",
    description="Supprime un besoin existant (soft delete).",
)
def delete_besoin(
    besoin_id: int,
    request: Request,
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),  # RBAC: Conducteur+ seulement
    controller: PlanningChargeController = Depends(get_controller),
    audit: AuditService = Depends(get_audit_service),
) -> None:
    """
    Supprime un besoin (soft delete).

    RBAC: Reserve aux conducteurs et administrateurs.
    """
    try:
        # Recuperer valeurs pour audit avant suppression
        old_besoin = controller.get_besoins_uc.besoin_repo.find_by_id(besoin_id)
        old_values = None
        if old_besoin:
            old_values = {
                "chantier_id": old_besoin.chantier_id,
                "semaine_code": old_besoin.semaine.code,
                "type_metier": old_besoin.type_metier.value,
                "besoin_heures": old_besoin.besoin_heures,
            }

        controller.delete_besoin(besoin_id, current_user_id)

        # Invalidate cache after data modification
        _invalidate_planning_cache()

        # Audit Trail
        audit.log_action(
            entity_type="besoin_charge",
            entity_id=besoin_id,
            action="deleted",
            user_id=current_user_id,
            old_values=old_values,
            ip_address=request.client.host if request.client else None,
        )
    except BesoinNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
