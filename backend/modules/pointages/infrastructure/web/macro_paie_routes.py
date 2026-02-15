"""Routes FastAPI pour les macros de paie (FDH-18).

CRUD des macros de paie + calcul automatique sur période.
Accès réservé aux Admin et Conducteur.
"""

import logging
from datetime import date
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from shared.infrastructure.web.dependencies import (
    get_current_user_id,
    get_current_user_role,
)
from ..persistence import SQLAlchemyMacroPaieRepository, SQLAlchemyPointageRepository
from ...application.use_cases.macro_paie_use_cases import (
    CreateMacroPaieUseCase,
    GetMacroPaieUseCase,
    ListMacrosPaieUseCase,
    UpdateMacroPaieUseCase,
    DeleteMacroPaieUseCase,
    CalculerMacrosPeriodeUseCase,
    MacroNotFoundError,
    MacroPaieCreateDTO,
    MacroPaieUpdateDTO,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/macros-paie", tags=["Macros de Paie (FDH-18)"])


# ============ Pydantic Models ============


class MacroPaieCreateRequest(BaseModel):
    """Request pour créer une macro de paie."""

    nom: str = Field(..., min_length=1, max_length=255)
    type_macro: str = Field(..., description="Type: indemnite_trajet, panier_repas, prime_intemperies, etc.")
    formule: str = Field(..., min_length=1, description="Expression de calcul")
    description: Optional[str] = None
    parametres: Optional[Dict[str, Any]] = None


class MacroPaieUpdateRequest(BaseModel):
    """Request pour mettre à jour une macro de paie."""

    nom: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    formule: Optional[str] = None
    parametres: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None


class MacroPaieResponse(BaseModel):
    """Response pour une macro de paie."""

    id: int
    nom: str
    type_macro: str
    type_macro_label: str
    description: Optional[str]
    formule: str
    parametres: Dict[str, Any]
    active: bool
    created_by: Optional[int]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class CalculMacroResultResponse(BaseModel):
    """Response pour un résultat de calcul de macro."""

    macro_id: int
    macro_nom: str
    type_macro: str
    resultat: float
    formule: str
    contexte: Dict[str, Any]


class CalculPeriodeResultResponse(BaseModel):
    """Response pour le résultat d'un calcul sur une période."""

    utilisateur_id: int
    date_debut: str
    date_fin: str
    resultats: List[CalculMacroResultResponse]
    total: float

    class Config:
        from_attributes = True


class CalculRequest(BaseModel):
    """Request pour le calcul de macros sur période."""

    utilisateur_id: int
    date_debut: date
    date_fin: date
    contexte_supplementaire: Optional[Dict[str, Any]] = None


# ============ Helper ============


def _require_admin_or_conducteur(user_role: str) -> None:
    """Vérifie que l'utilisateur est admin ou conducteur.

    Args:
        user_role: Rôle de l'utilisateur.

    Raises:
        HTTPException: Si le rôle n'est pas autorisé.
    """
    if user_role not in ("admin", "conducteur"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs et conducteurs",
        )


# ============ ROUTES ============


@router.post("", response_model=MacroPaieResponse, status_code=status.HTTP_201_CREATED)
def create_macro_paie(
    request: MacroPaieCreateRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
):
    """Crée une nouvelle macro de paie (admin/conducteur)."""
    _require_admin_or_conducteur(user_role)

    try:
        repo = SQLAlchemyMacroPaieRepository(db)
        use_case = CreateMacroPaieUseCase(repo)

        dto = MacroPaieCreateDTO(
            nom=request.nom,
            type_macro=request.type_macro,
            formule=request.formule,
            description=request.description,
            parametres=request.parametres,
            created_by=user_id,
        )

        result = use_case.execute(dto)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[MacroPaieResponse])
def list_macros_paie(
    active_only: bool = Query(True),
    type_macro: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
):
    """Liste les macros de paie (admin/conducteur)."""
    _require_admin_or_conducteur(user_role)

    try:
        repo = SQLAlchemyMacroPaieRepository(db)
        use_case = ListMacrosPaieUseCase(repo)
        return use_case.execute(active_only, type_macro, skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{macro_id}", response_model=MacroPaieResponse)
def get_macro_paie(
    macro_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
):
    """Récupère une macro de paie par ID (admin/conducteur)."""
    _require_admin_or_conducteur(user_role)

    try:
        repo = SQLAlchemyMacroPaieRepository(db)
        use_case = GetMacroPaieUseCase(repo)
        return use_case.execute(macro_id)
    except MacroNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{macro_id}", response_model=MacroPaieResponse)
def update_macro_paie(
    macro_id: int,
    request: MacroPaieUpdateRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
):
    """Met à jour une macro de paie (admin/conducteur)."""
    _require_admin_or_conducteur(user_role)

    try:
        repo = SQLAlchemyMacroPaieRepository(db)
        use_case = UpdateMacroPaieUseCase(repo)

        dto = MacroPaieUpdateDTO(
            nom=request.nom,
            description=request.description,
            formule=request.formule,
            parametres=request.parametres,
            active=request.active,
        )

        return use_case.execute(macro_id, dto)
    except MacroNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{macro_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_macro_paie(
    macro_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
):
    """Supprime une macro de paie (admin uniquement)."""
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent supprimer des macros",
        )

    try:
        repo = SQLAlchemyMacroPaieRepository(db)
        use_case = DeleteMacroPaieUseCase(repo)
        use_case.execute(macro_id)
    except MacroNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/calculer", response_model=CalculPeriodeResultResponse)
def calculer_macros_periode(
    request: CalculRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
):
    """Calcule toutes les macros actives sur une période pour un utilisateur.

    Applique automatiquement toutes les macros de paie actives sur les
    pointages de l'utilisateur pour la période donnée.
    """
    _require_admin_or_conducteur(user_role)

    try:
        macro_repo = SQLAlchemyMacroPaieRepository(db)
        pointage_repo = SQLAlchemyPointageRepository(db)

        use_case = CalculerMacrosPeriodeUseCase(macro_repo, pointage_repo)

        result = use_case.execute(
            utilisateur_id=request.utilisateur_id,
            date_debut=request.date_debut,
            date_fin=request.date_fin,
            contexte_supplementaire=request.contexte_supplementaire,
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
