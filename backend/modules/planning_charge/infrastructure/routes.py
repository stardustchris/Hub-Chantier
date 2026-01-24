"""Routes API pour le module planning de charge."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from shared.infrastructure.database import get_db
from shared.infrastructure.web.dependencies import get_current_user_id

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


router = APIRouter(prefix="/planning-charge", tags=["Planning de Charge"])


def get_controller(db: Session = Depends(get_db)) -> PlanningChargeController:
    """Factory pour le controller avec injection de dependances."""
    repo = SQLAlchemyBesoinChargeRepository(db)

    # Creer les use cases
    create_uc = CreateBesoinUseCase(repo)
    update_uc = UpdateBesoinUseCase(repo)
    delete_uc = DeleteBesoinUseCase(repo)
    get_planning_uc = GetPlanningChargeUseCase(repo)
    get_besoins_uc = GetBesoinsByChantierUseCase(repo)
    get_occupation_uc = GetOccupationDetailsUseCase(repo)

    return PlanningChargeController(
        create_besoin_uc=create_uc,
        update_besoin_uc=update_uc,
        delete_besoin_uc=delete_uc,
        get_planning_uc=get_planning_uc,
        get_besoins_uc=get_besoins_uc,
        get_occupation_uc=get_occupation_uc,
    )


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
    controller: PlanningChargeController = Depends(get_controller),
):
    """
    Endpoint principal du planning de charge.

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
    controller: PlanningChargeController = Depends(get_controller),
):
    """
    Modal details occupation.

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
    controller: PlanningChargeController = Depends(get_controller),
):
    """Recupere les besoins pour un chantier specifique."""
    try:
        return controller.get_besoins_by_chantier(
            chantier_id=chantier_id,
            semaine_debut=semaine_debut,
            semaine_fin=semaine_fin,
        )
    except InvalidSemaineRangeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/besoins",
    response_model=BesoinChargeResponse,
    status_code=201,
    summary="Creer un besoin (PDC-16)",
    description="Cree un nouveau besoin en main d'oeuvre pour un chantier/semaine/type.",
)
def create_besoin(
    request: CreateBesoinRequest,
    current_user_id: int = Depends(get_current_user_id),
    controller: PlanningChargeController = Depends(get_controller),
):
    """
    Modal planification des besoins.

    Cree un besoin en main d'oeuvre pour:
    - Un chantier specifique
    - Une semaine donnee
    - Un type de metier
    """
    try:
        return controller.create_besoin(request, current_user_id)
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
    request: UpdateBesoinRequest,
    current_user_id: int = Depends(get_current_user_id),
    controller: PlanningChargeController = Depends(get_controller),
):
    """Met a jour un besoin existant."""
    try:
        return controller.update_besoin(besoin_id, request, current_user_id)
    except BesoinNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/besoins/{besoin_id}",
    status_code=204,
    summary="Supprimer un besoin",
    description="Supprime un besoin existant.",
)
def delete_besoin(
    besoin_id: int,
    current_user_id: int = Depends(get_current_user_id),
    controller: PlanningChargeController = Depends(get_controller),
):
    """Supprime un besoin."""
    try:
        controller.delete_besoin(besoin_id, current_user_id)
    except BesoinNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
