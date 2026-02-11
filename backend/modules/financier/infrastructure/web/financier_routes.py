"""Routes FastAPI pour le module Financier.

FIN-01 a FIN-15: API REST complete pour la gestion financiere des chantiers.
"""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from shared.infrastructure.web import (
    get_current_user_id,
    get_current_user_role,
    get_current_user_chantier_ids,
    require_admin,
    require_conducteur_or_admin,
    require_chef_or_above,
)

from ...domain.value_objects import TypeFournisseur, TypeAchat, StatutAchat, UniteMesure
from ...domain.entities.achat import (
    AchatValidationError,
    TransitionStatutAchatInvalideError,
)
from ...application.use_cases.fournisseur_use_cases import (
    FournisseurNotFoundError,
    FournisseurSiretExistsError,
)
from ...application.use_cases.budget_use_cases import (
    BudgetNotFoundError,
    BudgetAlreadyExistsError,
)
from ...application.use_cases.lot_budgetaire_use_cases import (
    LotNotFoundError,
    LotCodeExistsError,
)
from ...application.use_cases.achat_use_cases import (
    AchatNotFoundError,
    FournisseurInactifError,
)
from ...application.use_cases.avenant_use_cases import (
    AvenantNotFoundError,
    AvenantAlreadyValideError,
)
from ...application.use_cases.situation_use_cases import (
    SituationNotFoundError,
    SituationWorkflowError,
)
from ...application.use_cases.facture_use_cases import (
    FactureNotFoundError,
    FactureWorkflowError,
    SituationNonValideeError,
)
from ...application.use_cases.alerte_use_cases import AlerteNotFoundError
from ...application.use_cases.affectation_use_cases import (
    AffectationNotFoundError,
    AllocationDepasseError,
    LotBudgetaireIntrouvableError,
)
from ...application.use_cases.export_comptable_use_cases import ExportComptableError
from ...application.use_cases.pnl_use_cases import PnLChantierNotFoundError
from ...application.use_cases.bilan_cloture_use_cases import (
    BilanClotureError,
    BudgetNonTrouveError as BilanBudgetNonTrouveError,
    ChantierNonTrouveError as BilanChantierNonTrouveError,
)
from ...application.dtos import (
    FournisseurCreateDTO,
    FournisseurUpdateDTO,
    BudgetCreateDTO,
    BudgetUpdateDTO,
    LotBudgetaireCreateDTO,
    LotBudgetaireUpdateDTO,
    AchatCreateDTO,
    AchatUpdateDTO,
    AvenantCreateDTO,
    AvenantUpdateDTO,
    SituationCreateDTO,
    SituationUpdateDTO,
    LigneSituationCreateDTO,
    FactureCreateDTO,
    CreateAffectationDTO,
    ConfigurationEntrepriseUpdateDTO,
)
from .dependencies import (
    # Fournisseur
    get_create_fournisseur_use_case,
    get_update_fournisseur_use_case,
    get_delete_fournisseur_use_case,
    get_get_fournisseur_use_case,
    get_list_fournisseurs_use_case,
    # Budget
    get_create_budget_use_case,
    get_update_budget_use_case,
    get_get_budget_use_case,
    get_get_budget_by_chantier_use_case,
    # Lot Budgetaire
    get_create_lot_budgetaire_use_case,
    get_update_lot_budgetaire_use_case,
    get_delete_lot_budgetaire_use_case,
    get_get_lot_budgetaire_use_case,
    get_list_lots_budgetaires_use_case,
    # Achat
    get_create_achat_use_case,
    get_update_achat_use_case,
    get_valider_achat_use_case,
    get_refuser_achat_use_case,
    get_passer_commande_achat_use_case,
    get_marquer_livre_achat_use_case,
    get_marquer_facture_achat_use_case,
    get_get_achat_use_case,
    get_list_achats_use_case,
    get_list_achats_en_attente_use_case,
    # Avenant (FIN-04)
    get_create_avenant_use_case,
    get_update_avenant_use_case,
    get_valider_avenant_use_case,
    get_get_avenant_use_case,
    get_list_avenants_use_case,
    get_delete_avenant_use_case,
    # Situation (FIN-07)
    get_create_situation_use_case,
    get_update_situation_use_case,
    get_soumettre_situation_use_case,
    get_valider_situation_use_case,
    get_marquer_validee_client_use_case,
    get_marquer_facturee_situation_use_case,
    get_get_situation_use_case,
    get_list_situations_use_case,
    get_delete_situation_use_case,
    # Facture (FIN-08)
    get_create_facture_from_situation_use_case,
    get_create_facture_acompte_use_case,
    get_emettre_facture_use_case,
    get_envoyer_facture_use_case,
    get_marquer_payee_facture_use_case,
    get_annuler_facture_use_case,
    get_get_facture_use_case,
    get_list_factures_use_case,
    # Couts (FIN-09, FIN-10)
    get_cout_main_oeuvre_use_case,
    get_cout_materiel_use_case,
    # Alertes (FIN-12)
    get_verifier_depassement_use_case,
    get_acquitter_alerte_use_case,
    get_list_alertes_use_case,
    # Dashboard
    get_dashboard_financier_use_case,
    # Evolution financiere (FIN-17)
    get_evolution_financiere_use_case,
    # Consolidation (FIN-20)
    get_vue_consolidee_use_case,
    # Suggestions (FIN-21/22)
    get_suggestions_financieres_use_case,
    # AI Provider (FIN-21)
    get_ai_suggestion_provider,
    # Affectation (FIN-03)
    get_create_affectation_use_case,
    get_delete_affectation_use_case,
    get_list_affectations_by_chantier_use_case,
    get_affectations_by_tache_use_case,
    # Export comptable (FIN-13)
    get_export_comptable_use_case,
    # P&L (GAP #9)
    get_pnl_chantier_use_case,
    # Bilan de cloture (GAP #10)
    get_bilan_cloture_use_case,
    # Journal
    get_journal_financier_repository,
    # Configuration entreprise
    get_get_configuration_entreprise_use_case,
    get_update_configuration_entreprise_use_case,
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/financier", tags=["financier"])


# =============================================================================
# Helper - Verification acces chantier (IDOR protection)
# =============================================================================


def _check_chantier_access(chantier_id: int, user_role: str, user_chantier_ids: list[int] | None):
    """Verifie que l'utilisateur a acces au chantier.

    Admin et conducteur ont acces a tous les chantiers.
    Chef chantier et compagnon ont acces uniquement a leurs chantiers assignes.
    """
    if user_chantier_ids is not None and chantier_id not in user_chantier_ids:
        raise HTTPException(
            status_code=403,
            detail="Vous n'avez pas accès à ce chantier",
        )


# =============================================================================
# Helper - Gel financier chantier ferme
# =============================================================================


def _check_chantier_not_closed(chantier_id: int, db: Session) -> None:
    """Verifie que le chantier n'est pas ferme avant operation financiere.

    Un chantier ferme ne doit plus accepter d'operations financieres
    d'ecriture (creation achat, avenant, situation, mise a jour achat).

    Note: On utilise is_active (False uniquement pour "ferme") plutot que
    allows_modifications (False pour "ferme" ET "receptionne"). Un chantier
    receptionne peut encore avoir des operations financieres (dernieres
    factures, etc.).

    Args:
        chantier_id: ID du chantier.
        db: Session base de donnees.

    Raises:
        HTTPException 403 si le chantier est ferme.
    """
    from modules.chantiers.infrastructure.persistence import SQLAlchemyChantierRepository

    chantier_repo = SQLAlchemyChantierRepository(db)
    chantier = chantier_repo.find_by_id(chantier_id)
    if chantier and not chantier.statut.is_active():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operations financieres interdites sur un chantier ferme",
        )


# Valeurs autorisees pour entite_type dans le journal financier
ENTITE_TYPES_AUTORISES = {
    "budget", "lot_budgetaire", "achat", "fournisseur",
    "avenant", "situation", "facture", "alerte",
}


# =============================================================================
# Schemas Pydantic - Fournisseurs
# =============================================================================


class FournisseurCreateRequest(BaseModel):
    """Requete de creation de fournisseur."""

    raison_sociale: str = Field(..., min_length=1, max_length=200)
    type: TypeFournisseur = TypeFournisseur.NEGOCE_MATERIAUX
    siret: Optional[str] = Field(None, max_length=14, pattern=r"^\d{14}$")
    adresse: Optional[str] = Field(None, max_length=500)
    contact_principal: Optional[str] = Field(None, max_length=200)
    telephone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=200)
    conditions_paiement: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=2000)


class FournisseurUpdateRequest(BaseModel):
    """Requete de mise a jour de fournisseur."""

    raison_sociale: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[TypeFournisseur] = None
    siret: Optional[str] = Field(None, max_length=14, pattern=r"^\d{14}$")
    adresse: Optional[str] = Field(None, max_length=500)
    contact_principal: Optional[str] = Field(None, max_length=200)
    telephone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=200)
    conditions_paiement: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=2000)
    actif: Optional[bool] = None


# =============================================================================
# Schemas Pydantic - Budgets
# =============================================================================


class BudgetCreateRequest(BaseModel):
    """Requete de creation de budget."""

    chantier_id: int = Field(..., gt=0)
    montant_initial_ht: Decimal = Field(default=Decimal("0"), ge=0)
    retenue_garantie_pct: Decimal = Field(default=Decimal("5"), ge=0, le=5, description="Loi 71-584: max 5%")
    seuil_alerte_pct: Decimal = Field(default=Decimal("80"), ge=0, le=100)
    seuil_validation_achat: Decimal = Field(default=Decimal("1000"), ge=0)
    notes: Optional[str] = Field(None, max_length=2000)


class BudgetUpdateRequest(BaseModel):
    """Requete de mise a jour de budget."""

    montant_initial_ht: Optional[Decimal] = Field(None, ge=0)
    montant_avenants_ht: Optional[Decimal] = None
    retenue_garantie_pct: Optional[Decimal] = Field(None, ge=0, le=5, description="Loi 71-584: max 5%")
    seuil_alerte_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    seuil_validation_achat: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=2000)


# =============================================================================
# Schemas Pydantic - Lots Budgetaires
# =============================================================================


class LotBudgetaireCreateRequest(BaseModel):
    """Requete de creation de lot budgetaire."""

    budget_id: int = Field(..., gt=0)
    code_lot: str = Field(..., min_length=1, max_length=20)
    libelle: str = Field(..., min_length=1, max_length=200)
    unite: UniteMesure = UniteMesure.U
    quantite_prevue: Decimal = Field(default=Decimal("0"), ge=0)
    prix_unitaire_ht: Decimal = Field(default=Decimal("0"), ge=0)
    parent_lot_id: Optional[int] = Field(None, gt=0)
    ordre: int = Field(default=0, ge=0)


class LotBudgetaireUpdateRequest(BaseModel):
    """Requete de mise a jour de lot budgetaire."""

    code_lot: Optional[str] = Field(None, min_length=1, max_length=20)
    libelle: Optional[str] = Field(None, min_length=1, max_length=200)
    unite: Optional[UniteMesure] = None
    quantite_prevue: Optional[Decimal] = Field(None, ge=0)
    prix_unitaire_ht: Optional[Decimal] = Field(None, ge=0)
    parent_lot_id: Optional[int] = Field(None, gt=0)
    ordre: Optional[int] = Field(None, ge=0)


# =============================================================================
# Schemas Pydantic - Achats
# =============================================================================


class AchatCreateRequest(BaseModel):
    """Requete de creation d'achat."""

    chantier_id: int = Field(..., gt=0)
    libelle: str = Field(..., min_length=1, max_length=200)
    quantite: Decimal = Field(..., gt=0)
    prix_unitaire_ht: Decimal = Field(..., ge=0)
    fournisseur_id: Optional[int] = Field(None, gt=0)
    lot_budgetaire_id: Optional[int] = Field(None, gt=0)
    type_achat: TypeAchat = TypeAchat.MATERIAU
    unite: UniteMesure = UniteMesure.U
    taux_tva: Decimal = Field(default=Decimal("20"))
    date_commande: Optional[date] = None
    date_livraison_prevue: Optional[date] = None
    commentaire: Optional[str] = Field(None, max_length=2000)


class AchatUpdateRequest(BaseModel):
    """Requete de mise a jour d'achat (seulement si statut = demande)."""

    fournisseur_id: Optional[int] = Field(None, gt=0)
    lot_budgetaire_id: Optional[int] = Field(None, gt=0)
    type_achat: Optional[TypeAchat] = None
    libelle: Optional[str] = Field(None, min_length=1, max_length=200)
    quantite: Optional[Decimal] = Field(None, gt=0)
    unite: Optional[UniteMesure] = None
    prix_unitaire_ht: Optional[Decimal] = Field(None, ge=0)
    taux_tva: Optional[Decimal] = None
    date_commande: Optional[date] = None
    date_livraison_prevue: Optional[date] = None
    commentaire: Optional[str] = Field(None, max_length=2000)


class RefuserAchatRequest(BaseModel):
    """Requete de refus d'achat."""

    motif: str = Field(..., min_length=1, max_length=1000)


class FacturerAchatRequest(BaseModel):
    """Requete de facturation d'achat."""

    numero_facture: str = Field(..., min_length=1, max_length=50)


# =============================================================================
# Routes Fournisseurs (FIN-14)
# =============================================================================


@router.post("/fournisseurs", status_code=status.HTTP_201_CREATED)
async def create_fournisseur(
    request: FournisseurCreateRequest,
    _role: str = Depends(require_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_create_fournisseur_use_case),
):
    """Cree un nouveau fournisseur.

    FIN-14: Repertoire fournisseurs - Admin uniquement.
    """
    try:
        dto = FournisseurCreateDTO(
            raison_sociale=request.raison_sociale,
            type=request.type,
            siret=request.siret,
            adresse=request.adresse,
            contact_principal=request.contact_principal,
            telephone=request.telephone,
            email=request.email,
            conditions_paiement=request.conditions_paiement,
            notes=request.notes,
        )
        result = use_case.execute(dto, current_user_id)
        return result.to_dict()
    except FournisseurSiretExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/fournisseurs")
async def list_fournisseurs(
    type: Optional[TypeFournisseur] = None,
    actif_seulement: bool = True,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    _role: str = Depends(require_conducteur_or_admin),
    use_case=Depends(get_list_fournisseurs_use_case),
):
    """Liste les fournisseurs avec filtres.

    FIN-14: Accessible aux conducteurs et admins.
    """
    result = use_case.execute(
        type=type,
        actif_seulement=actif_seulement,
        limit=limit,
        offset=offset,
    )
    return {
        "items": [f.to_dict() for f in result.items],
        "total": result.total,
        "limit": result.limit,
        "offset": result.offset,
    }


@router.get("/fournisseurs/{fournisseur_id}")
async def get_fournisseur(
    fournisseur_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case=Depends(get_get_fournisseur_use_case),
):
    """Recupere un fournisseur par son ID."""
    try:
        result = use_case.execute(fournisseur_id)
        return result.to_dict()
    except FournisseurNotFoundError:
        raise HTTPException(status_code=404, detail="Fournisseur non trouve")


@router.put("/fournisseurs/{fournisseur_id}")
async def update_fournisseur(
    fournisseur_id: int,
    request: FournisseurUpdateRequest,
    _role: str = Depends(require_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_update_fournisseur_use_case),
):
    """Met a jour un fournisseur.

    FIN-14: Admin uniquement.
    """
    try:
        dto = FournisseurUpdateDTO(
            raison_sociale=request.raison_sociale,
            type=request.type,
            siret=request.siret,
            adresse=request.adresse,
            contact_principal=request.contact_principal,
            telephone=request.telephone,
            email=request.email,
            conditions_paiement=request.conditions_paiement,
            notes=request.notes,
            actif=request.actif,
        )
        result = use_case.execute(fournisseur_id, dto, current_user_id)
        return result.to_dict()
    except FournisseurNotFoundError:
        raise HTTPException(status_code=404, detail="Fournisseur non trouve")
    except FournisseurSiretExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete(
    "/fournisseurs/{fournisseur_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_fournisseur(
    fournisseur_id: int,
    _role: str = Depends(require_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_delete_fournisseur_use_case),
):
    """Supprime un fournisseur (soft delete).

    FIN-14: Admin uniquement.
    """
    try:
        use_case.execute(fournisseur_id, current_user_id)
    except FournisseurNotFoundError:
        raise HTTPException(status_code=404, detail="Fournisseur non trouve")


# =============================================================================
# Routes Budgets (FIN-01)
# =============================================================================


@router.post("/budgets", status_code=status.HTTP_201_CREATED)
async def create_budget(
    request: BudgetCreateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_create_budget_use_case),
):
    """Cree un budget pour un chantier.

    FIN-01: Un seul budget par chantier.
    """
    try:
        dto = BudgetCreateDTO(
            chantier_id=request.chantier_id,
            montant_initial_ht=request.montant_initial_ht,
            retenue_garantie_pct=request.retenue_garantie_pct,
            seuil_alerte_pct=request.seuil_alerte_pct,
            seuil_validation_achat=request.seuil_validation_achat,
            notes=request.notes,
        )
        result = use_case.execute(dto, current_user_id)
        return result.to_dict()
    except BudgetAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/budgets/{budget_id}")
async def get_budget(
    budget_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case=Depends(get_get_budget_use_case),
):
    """Recupere un budget par son ID."""
    try:
        result = use_case.execute(budget_id)
        return result.to_dict()
    except BudgetNotFoundError:
        raise HTTPException(status_code=404, detail="Budget non trouve")


@router.get("/chantiers/{chantier_id}/budget")
async def get_budget_by_chantier(
    chantier_id: int,
    _role: str = Depends(require_chef_or_above),
    current_user_id: int = Depends(get_current_user_id),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_get_budget_by_chantier_use_case),
):
    """Recupere le budget d'un chantier.

    FIN-01: Accessible aux chefs de chantier et superieurs.
    """
    _check_chantier_access(chantier_id, _role, user_chantier_ids)
    try:
        result = use_case.execute(chantier_id)
        return result.to_dict()
    except BudgetNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Aucun budget pour ce chantier",
        )


@router.put("/budgets/{budget_id}")
async def update_budget(
    budget_id: int,
    request: BudgetUpdateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_update_budget_use_case),
):
    """Met a jour un budget.

    FIN-01: Conducteurs et admins. Seuil validation achat: admin uniquement.
    """
    # M-07: Seul un admin peut modifier le seuil de validation achat
    if request.seuil_validation_achat is not None and _role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Seul un administrateur peut modifier le seuil de validation achat",
        )
    try:
        dto = BudgetUpdateDTO(
            montant_initial_ht=request.montant_initial_ht,
            montant_avenants_ht=request.montant_avenants_ht,
            retenue_garantie_pct=request.retenue_garantie_pct,
            seuil_alerte_pct=request.seuil_alerte_pct,
            seuil_validation_achat=request.seuil_validation_achat,
            notes=request.notes,
        )
        result = use_case.execute(budget_id, dto, current_user_id)
        return result.to_dict()
    except BudgetNotFoundError:
        raise HTTPException(status_code=404, detail="Budget non trouve")


# =============================================================================
# Routes Lots Budgetaires (FIN-02)
# =============================================================================


@router.post("/lots-budgetaires", status_code=status.HTTP_201_CREATED)
async def create_lot_budgetaire(
    request: LotBudgetaireCreateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_create_lot_budgetaire_use_case),
):
    """Cree un lot budgetaire.

    FIN-02: Decomposition en lots.
    """
    try:
        dto = LotBudgetaireCreateDTO(
            budget_id=request.budget_id,
            code_lot=request.code_lot,
            libelle=request.libelle,
            unite=request.unite,
            quantite_prevue=request.quantite_prevue,
            prix_unitaire_ht=request.prix_unitaire_ht,
            parent_lot_id=request.parent_lot_id,
            ordre=request.ordre,
        )
        result = use_case.execute(dto, current_user_id)
        return result.to_dict()
    except BudgetNotFoundError:
        raise HTTPException(status_code=404, detail="Budget non trouve")
    except LotCodeExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/budgets/{budget_id}/lots")
async def list_lots_budgetaires(
    budget_id: int,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    _role: str = Depends(require_chef_or_above),
    current_user_id: int = Depends(get_current_user_id),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_list_lots_budgetaires_use_case),
    budget_use_case=Depends(get_get_budget_use_case),
):
    """Liste les lots budgetaires d'un budget.

    FIN-02: Accessible aux chefs de chantier et superieurs.
    """
    # IDOR: verifier acces au chantier via le budget
    try:
        budget_dto = budget_use_case.execute(budget_id)
        _check_chantier_access(budget_dto.chantier_id, _role, user_chantier_ids)
    except BudgetNotFoundError:
        raise HTTPException(status_code=404, detail="Budget non trouve")
    result = use_case.execute(
        budget_id=budget_id,
        limit=limit,
        offset=offset,
    )
    return {
        "items": [lot.to_dict() for lot in result.items],
        "total": result.total,
        "limit": result.limit,
        "offset": result.offset,
    }


@router.get("/lots-budgetaires/{lot_id}")
async def get_lot_budgetaire(
    lot_id: int,
    _role: str = Depends(require_chef_or_above),
    current_user_id: int = Depends(get_current_user_id),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_get_lot_budgetaire_use_case),
    budget_use_case=Depends(get_get_budget_use_case),
):
    """Recupere un lot budgetaire par son ID."""
    try:
        result = use_case.execute(lot_id)
        # IDOR: verifier acces au chantier via le budget du lot
        budget_dto = budget_use_case.execute(result.budget_id)
        _check_chantier_access(budget_dto.chantier_id, _role, user_chantier_ids)
        return result.to_dict()
    except LotNotFoundError:
        raise HTTPException(status_code=404, detail="Lot budgetaire non trouve")
    except BudgetNotFoundError:
        raise HTTPException(status_code=404, detail="Budget non trouve")


@router.put("/lots-budgetaires/{lot_id}")
async def update_lot_budgetaire(
    lot_id: int,
    request: LotBudgetaireUpdateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_update_lot_budgetaire_use_case),
):
    """Met a jour un lot budgetaire.

    FIN-02: Conducteurs et admins.
    """
    try:
        dto = LotBudgetaireUpdateDTO(
            code_lot=request.code_lot,
            libelle=request.libelle,
            unite=request.unite,
            quantite_prevue=request.quantite_prevue,
            prix_unitaire_ht=request.prix_unitaire_ht,
            parent_lot_id=request.parent_lot_id,
            ordre=request.ordre,
        )
        result = use_case.execute(lot_id, dto, current_user_id)
        return result.to_dict()
    except LotNotFoundError:
        raise HTTPException(status_code=404, detail="Lot budgetaire non trouve")
    except LotCodeExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete(
    "/lots-budgetaires/{lot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_lot_budgetaire(
    lot_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_delete_lot_budgetaire_use_case),
):
    """Supprime un lot budgetaire (soft delete).

    FIN-02: Conducteurs et admins.
    """
    try:
        use_case.execute(lot_id, current_user_id)
    except LotNotFoundError:
        raise HTTPException(status_code=404, detail="Lot budgetaire non trouve")


# =============================================================================
# Template Gros Oeuvre (pre-remplissage lots GO)
# =============================================================================


TEMPLATE_GO = [
    {"code": "GO-FOND", "libelle": "Fondations", "pct": 12},
    {"code": "GO-INF", "libelle": "Infrastructure (sous-sol)", "pct": 8},
    {"code": "GO-RDC", "libelle": "Gros oeuvre RDC", "pct": 18},
    {"code": "GO-R1", "libelle": "Gros oeuvre R+1", "pct": 16},
    {"code": "GO-R2", "libelle": "Gros oeuvre R+2", "pct": 14},
    {"code": "GO-TOIT", "libelle": "Toiture-terrasse", "pct": 10},
    {"code": "GO-ESC", "libelle": "Escaliers et paliers", "pct": 5},
    {"code": "GO-FAC", "libelle": "Facades et enduits", "pct": 8},
    {"code": "GO-VRD", "libelle": "VRD et assainissement", "pct": 5},
    {"code": "GO-DIV", "libelle": "Divers et aleas", "pct": 4},
]


@router.post("/budgets/{budget_id}/template-go", status_code=status.HTTP_201_CREATED)
async def appliquer_template_go(
    budget_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    lot_use_case=Depends(get_create_lot_budgetaire_use_case),
    budget_use_case=Depends(get_get_budget_use_case),
):
    """Applique le template Gros Oeuvre sur un budget.

    Cree 10 lots pre-remplis avec des proportions typiques GO.
    Le montant de chaque lot est calcule en pourcentage du montant_initial_ht du budget.
    """
    # 1. Verifier que le budget existe et recuperer montant_initial_ht
    try:
        budget_dto = budget_use_case.execute(budget_id)
    except BudgetNotFoundError:
        raise HTTPException(status_code=404, detail="Budget non trouve")

    montant_initial_ht = Decimal(budget_dto.montant_initial_ht)

    # 2. Creer les lots GO
    lots_crees = []
    for idx, tpl in enumerate(TEMPLATE_GO):
        prix_unitaire_ht = montant_initial_ht * Decimal(tpl["pct"]) / Decimal("100")
        dto = LotBudgetaireCreateDTO(
            budget_id=budget_id,
            code_lot=tpl["code"],
            libelle=tpl["libelle"],
            unite=UniteMesure.U,
            quantite_prevue=Decimal("1"),
            prix_unitaire_ht=prix_unitaire_ht,
            ordre=idx,
        )
        try:
            result = lot_use_case.execute(dto, current_user_id)
            lots_crees.append(result.to_dict())
        except LotCodeExistsError:
            # Lot avec ce code existe deja, on passe au suivant
            logger.warning(
                "Template GO: lot %s existe deja dans le budget %d, ignore",
                tpl["code"],
                budget_id,
            )

    return lots_crees


# =============================================================================
# Routes Achats (FIN-05, FIN-06, FIN-07)
# =============================================================================


@router.post("/achats", status_code=status.HTTP_201_CREATED)
async def create_achat(
    request: AchatCreateRequest,
    _role: str = Depends(require_chef_or_above),
    current_user_id: int = Depends(get_current_user_id),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    db: Session = Depends(get_db),
    use_case=Depends(get_create_achat_use_case),
):
    """Cree un nouvel achat.

    FIN-05: Saisie achat - Chef de chantier et superieur.
    FIN-07: Auto-validation si montant < seuil budget.
    """
    _check_chantier_access(request.chantier_id, _role, user_chantier_ids)
    _check_chantier_not_closed(request.chantier_id, db)
    try:
        dto = AchatCreateDTO(
            chantier_id=request.chantier_id,
            libelle=request.libelle,
            quantite=request.quantite,
            prix_unitaire_ht=request.prix_unitaire_ht,
            fournisseur_id=request.fournisseur_id,
            lot_budgetaire_id=request.lot_budgetaire_id,
            type_achat=request.type_achat,
            unite=request.unite,
            taux_tva=request.taux_tva,
            date_commande=request.date_commande,
            date_livraison_prevue=request.date_livraison_prevue,
            commentaire=request.commentaire,
        )
        result = use_case.execute(dto, current_user_id)
        return result.to_dict()
    except FournisseurNotFoundError:
        raise HTTPException(status_code=404, detail="Fournisseur non trouve")
    except FournisseurInactifError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AchatValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/achats")
async def list_achats(
    chantier_id: Optional[int] = Query(None, gt=0),
    statut: Optional[StatutAchat] = None,
    fournisseur_id: Optional[int] = Query(None, gt=0),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_list_achats_use_case),
):
    """Liste les achats avec filtres.

    FIN-06: Suivi achat - Chef de chantier et superieur.
    """
    if chantier_id is not None:
        _check_chantier_access(chantier_id, _role, user_chantier_ids)
    result = use_case.execute(
        chantier_id=chantier_id,
        statut=statut,
        fournisseur_id=fournisseur_id,
        limit=limit,
        offset=offset,
    )
    return {
        "items": [a.to_dict() for a in result.items],
        "total": result.total,
        "limit": result.limit,
        "offset": result.offset,
    }


@router.get("/achats/en-attente")
async def list_achats_en_attente(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    _role: str = Depends(require_conducteur_or_admin),
    use_case=Depends(get_list_achats_en_attente_use_case),
):
    """Liste les achats en attente de validation.

    FIN-07: Validation N+1 - Conducteurs et admins.
    """
    result = use_case.execute(limit=limit, offset=offset)
    return {
        "items": [a.to_dict() for a in result.items],
        "total": result.total,
        "limit": result.limit,
        "offset": result.offset,
    }


@router.get("/achats/suggestions")
async def get_achat_suggestions(
    search: str = Query(..., min_length=3),
    limit: int = Query(10, ge=1, le=50),
    _role: str = Depends(require_chef_or_above),
    db: Session = Depends(get_db),
):
    """Autocomplete pour les libelles d'achats passes.

    Retourne des suggestions uniques basees sur l'historique des achats.
    Minimum 3 caracteres requis.
    """
    from ...infrastructure.persistence.sqlalchemy_achat_repository import SQLAlchemyAchatRepository

    repo = SQLAlchemyAchatRepository(db)
    return repo.search_suggestions(search, limit)


@router.get("/achats/{achat_id}")
async def get_achat(
    achat_id: int,
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_get_achat_use_case),
):
    """Recupere un achat par son ID."""
    try:
        result = use_case.execute(achat_id)
        _check_chantier_access(result.chantier_id, _role, user_chantier_ids)
        return result.to_dict()
    except AchatNotFoundError:
        raise HTTPException(status_code=404, detail="Achat non trouve")


@router.put("/achats/{achat_id}")
async def update_achat(
    achat_id: int,
    request: AchatUpdateRequest,
    _role: str = Depends(require_chef_or_above),
    current_user_id: int = Depends(get_current_user_id),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    db: Session = Depends(get_db),
    use_case=Depends(get_update_achat_use_case),
    get_achat_uc=Depends(get_get_achat_use_case),
):
    """Met a jour un achat (seulement si statut = demande).

    FIN-05: Modification limitee au statut demande.
    """
    # IDOR: verifier acces au chantier de l'achat
    try:
        existing_achat = get_achat_uc.execute(achat_id)
        _check_chantier_access(existing_achat.chantier_id, _role, user_chantier_ids)
    except AchatNotFoundError:
        raise HTTPException(status_code=404, detail="Achat non trouve")
    _check_chantier_not_closed(existing_achat.chantier_id, db)
    try:
        dto = AchatUpdateDTO(
            fournisseur_id=request.fournisseur_id,
            lot_budgetaire_id=request.lot_budgetaire_id,
            type_achat=request.type_achat,
            libelle=request.libelle,
            quantite=request.quantite,
            unite=request.unite,
            prix_unitaire_ht=request.prix_unitaire_ht,
            taux_tva=request.taux_tva,
            date_commande=request.date_commande,
            date_livraison_prevue=request.date_livraison_prevue,
            commentaire=request.commentaire,
        )
        result = use_case.execute(achat_id, dto, current_user_id)
        return result.to_dict()
    except AchatNotFoundError:
        raise HTTPException(status_code=404, detail="Achat non trouve")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/achats/{achat_id}/valider")
async def valider_achat(
    achat_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    use_case=Depends(get_valider_achat_use_case),
    get_achat_uc=Depends(get_get_achat_use_case),
):
    """Valide un achat (demande -> valide).

    FIN-07: Validation N+1 - Conducteurs et admins.
    """
    try:
        existing = get_achat_uc.execute(achat_id)
    except AchatNotFoundError:
        raise HTTPException(status_code=404, detail="Achat non trouve")
    _check_chantier_not_closed(existing.chantier_id, db)
    try:
        result = use_case.execute(achat_id, current_user_id)
        return result.to_dict()
    except AchatNotFoundError:
        raise HTTPException(status_code=404, detail="Achat non trouve")
    except TransitionStatutAchatInvalideError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/achats/{achat_id}/refuser")
async def refuser_achat(
    achat_id: int,
    request: RefuserAchatRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_refuser_achat_use_case),
):
    """Refuse un achat.

    FIN-07: Validation N+1 - Motif obligatoire.
    """
    try:
        result = use_case.execute(achat_id, current_user_id, request.motif)
        return result.to_dict()
    except AchatNotFoundError:
        raise HTTPException(status_code=404, detail="Achat non trouve")
    except AchatValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransitionStatutAchatInvalideError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/achats/{achat_id}/commander")
async def passer_commande_achat(
    achat_id: int,
    _role: str = Depends(require_chef_or_above),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    use_case=Depends(get_passer_commande_achat_use_case),
    get_achat_uc=Depends(get_get_achat_use_case),
):
    """Passe un achat en commande (valide -> commande).

    FIN-06: Workflow - Chef de chantier et superieur.
    """
    try:
        existing = get_achat_uc.execute(achat_id)
    except AchatNotFoundError:
        raise HTTPException(status_code=404, detail="Achat non trouve")
    _check_chantier_not_closed(existing.chantier_id, db)
    try:
        result = use_case.execute(achat_id, current_user_id)
        return result.to_dict()
    except AchatNotFoundError:
        raise HTTPException(status_code=404, detail="Achat non trouve")
    except TransitionStatutAchatInvalideError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/achats/{achat_id}/livrer")
async def marquer_livre_achat(
    achat_id: int,
    _role: str = Depends(require_chef_or_above),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    use_case=Depends(get_marquer_livre_achat_use_case),
    get_achat_uc=Depends(get_get_achat_use_case),
):
    """Marque un achat comme livre (commande -> livre).

    FIN-06: Workflow - Chef de chantier et superieur.
    """
    try:
        existing = get_achat_uc.execute(achat_id)
    except AchatNotFoundError:
        raise HTTPException(status_code=404, detail="Achat non trouve")
    _check_chantier_not_closed(existing.chantier_id, db)
    try:
        result = use_case.execute(achat_id, current_user_id)
        return result.to_dict()
    except AchatNotFoundError:
        raise HTTPException(status_code=404, detail="Achat non trouve")
    except TransitionStatutAchatInvalideError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/achats/{achat_id}/facturer")
async def marquer_facture_achat(
    achat_id: int,
    request: FacturerAchatRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    use_case=Depends(get_marquer_facture_achat_use_case),
    get_achat_uc=Depends(get_get_achat_use_case),
):
    """Marque un achat comme facture (livre -> facture).

    FIN-06: Workflow - Conducteurs et admins.
    """
    try:
        existing = get_achat_uc.execute(achat_id)
    except AchatNotFoundError:
        raise HTTPException(status_code=404, detail="Achat non trouve")
    _check_chantier_not_closed(existing.chantier_id, db)
    try:
        result = use_case.execute(achat_id, request.numero_facture, current_user_id)
        return result.to_dict()
    except AchatNotFoundError:
        raise HTTPException(status_code=404, detail="Achat non trouve")
    except AchatValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransitionStatutAchatInvalideError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# Routes Dashboard Financier (FIN-11)
# =============================================================================


@router.get("/chantiers/{chantier_id}/dashboard-financier")
async def get_dashboard_financier(
    chantier_id: int,
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_dashboard_financier_use_case),
):
    """Tableau de bord financier d'un chantier.

    FIN-11: KPI, derniers achats, repartition par lot.
    Calcule la marge BTP avec repartition des couts fixes.
    """
    _check_chantier_access(chantier_id, _role, user_chantier_ids)
    try:
        result = use_case.execute(chantier_id)
        return result.to_dict()
    except BudgetNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Aucun budget pour ce chantier",
        )
    except Exception as e:
        logger.exception(
            "Erreur lors du calcul du dashboard financier",
            extra={"event": "dashboard.error", "chantier_id": chantier_id},
        )
        raise HTTPException(
            status_code=500,
            detail="Erreur serveur interne",
        )


# =============================================================================
# Routes Evolution Financiere (FIN-17)
# =============================================================================


@router.get("/chantiers/{chantier_id}/evolution-financiere")
async def get_evolution_financiere(
    chantier_id: int,
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_evolution_financiere_use_case),
):
    """Evolution financiere mensuelle d'un chantier.

    FIN-17: Courbes prevu/engage/realise cumules pour graphique Recharts.
    """
    _check_chantier_access(chantier_id, _role, user_chantier_ids)
    try:
        result = use_case.execute(chantier_id)
        return result.to_dict()
    except BudgetNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Aucun budget pour ce chantier",
        )


# =============================================================================
# Routes Consolidation Financiere (FIN-20)
# =============================================================================


@router.get("/finances/consolidation")
async def get_vue_consolidee_finances(
    chantier_ids: Optional[str] = Query(
        None,
        description="Liste d'IDs de chantiers separes par virgules (ex: 1,2,3)",
    ),
    statut_chantier: Optional[str] = Query(
        None,
        description="Filtre par statut chantier (ouvert, en_cours, receptionne, ferme)",
        pattern="^(ouvert|en_cours|receptionne|ferme)$",
    ),
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_vue_consolidee_use_case),
):
    """Vue consolidee financiere multi-chantiers.

    FIN-20: Agrege les KPI de plusieurs chantiers pour la page /finances.
    Admin voit tous les chantiers, les autres voient leurs chantiers assignes.
    Peut etre filtre par statut operationnel du chantier.
    """
    # Determiner les chantier_ids accessibles
    if chantier_ids:
        # Parse la liste depuis le query parameter
        try:
            requested_ids = [int(x.strip()) for x in chantier_ids.split(",") if x.strip()]
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Format invalide pour chantier_ids. Attendu: 1,2,3",
            )
        # Filtrer par les chantiers accessibles si restrictions
        if user_chantier_ids is not None:
            accessible_ids = [cid for cid in requested_ids if cid in user_chantier_ids]
        else:
            accessible_ids = requested_ids
    elif user_chantier_ids is not None:
        accessible_ids = user_chantier_ids
    else:
        # Admin sans filtre : on retourne une liste vide
        # (le frontend doit fournir les IDs)
        accessible_ids = []

    result = use_case.execute(
        accessible_ids,
        statut_chantier=statut_chantier,
    )
    return result.to_dict()


@router.get("/finances/consolidation/ia")
async def get_analyse_ia_consolidee(
    chantier_ids: Optional[str] = Query(
        None,
        description="Liste d'IDs de chantiers separes par virgules (ex: 1,2,3)",
    ),
    statut_chantier: Optional[str] = Query(
        None,
        description="Filtre par statut chantier (ouvert, en_cours, receptionne, ferme)",
        pattern="^(ouvert|en_cours|receptionne|ferme)$",
    ),
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_vue_consolidee_use_case),
):
    """Analyse IA consolidee multi-chantiers via Gemini 3 Flash.

    FIN-20+: Genere une analyse strategique IA basee sur les KPI consolides.
    Utilise Gemini 3 Flash pour fournir synthese, alertes et recommandations.
    Retourne un fallback algorithmique si Gemini n'est pas disponible.
    """
    # Determiner les chantier_ids accessibles (meme logique que consolidation)
    if chantier_ids:
        try:
            requested_ids = [int(x.strip()) for x in chantier_ids.split(",") if x.strip()]
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Format invalide pour chantier_ids. Attendu: 1,2,3",
            )
        if user_chantier_ids is not None:
            accessible_ids = [cid for cid in requested_ids if cid in user_chantier_ids]
        else:
            accessible_ids = requested_ids
    elif user_chantier_ids is not None:
        accessible_ids = user_chantier_ids
    else:
        accessible_ids = []

    # Recuperer les donnees consolidees
    consolidated = use_case.execute(
        accessible_ids,
        statut_chantier=statut_chantier,
    )
    consolidated_dict = consolidated.to_dict()

    # Essayer d'obtenir le provider IA
    ai_provider = get_ai_suggestion_provider()
    if ai_provider is None:
        # Fallback algorithmique si Gemini non disponible
        return _generate_fallback_analysis(consolidated_dict)

    try:
        # Appeler Gemini 3 Flash pour l'analyse consolidee
        analysis = ai_provider.generate_consolidated_analysis(consolidated_dict)
        if analysis:
            return analysis
        # Si analyse vide, fallback
        return _generate_fallback_analysis(consolidated_dict)
    except Exception as e:
        logger.warning("Erreur analyse IA consolidee: %s", str(e))
        return _generate_fallback_analysis(consolidated_dict)


def _generate_fallback_analysis(consolidated_dict: dict) -> dict:
    """Genere une analyse algorithmique de fallback si Gemini non disponible."""
    kpi = consolidated_dict.get("kpi_globaux", {})
    nb_chantiers = kpi.get("nb_chantiers", 0)
    nb_ok = kpi.get("nb_chantiers_ok", 0)
    nb_attention = kpi.get("nb_chantiers_attention", 0)
    nb_depassement = kpi.get("nb_chantiers_depassement", 0)
    marge_moyenne = float(kpi.get("marge_moyenne_pct", "0"))

    # Synthese
    if nb_depassement > 0:
        synthese = (
            f"{nb_chantiers} chantiers suivis. {nb_depassement} chantier(s) en depassement "
            f"necessitent une attention immediate. Marge moyenne: {marge_moyenne:.1f}%."
        )
    elif nb_attention > 0:
        synthese = (
            f"{nb_chantiers} chantiers suivis dont {nb_attention} a surveiller. "
            f"Situation globale sous controle. Marge moyenne: {marge_moyenne:.1f}%."
        )
    else:
        synthese = (
            f"{nb_chantiers} chantiers suivis, tous en bonne sante financiere. "
            f"Marge moyenne: {marge_moyenne:.1f}%."
        )

    # Alertes
    alertes = []
    if nb_depassement > 0:
        alertes.append(f"{nb_depassement} chantier(s) en depassement budgetaire")
    if nb_attention > 0:
        alertes.append(f"{nb_attention} chantier(s) approchent du seuil d'alerte (>80%)")
    if marge_moyenne < 10:
        alertes.append(f"Marge moyenne faible ({marge_moyenne:.1f}%)")

    # Recommandations
    recommandations = []
    if nb_depassement > 0:
        recommandations.append("Examiner les chantiers en depassement pour creer des avenants")
    if nb_attention > 0:
        recommandations.append("Planifier une revue des chantiers a risque cette semaine")
    if marge_moyenne < 15:
        recommandations.append("Negocier les tarifs fournisseurs pour ameliorer les marges")
    if not recommandations:
        recommandations.append("Maintenir le suivi actuel, situation saine")

    # Score de sante
    if nb_chantiers > 0:
        score = int((nb_ok / nb_chantiers) * 100)
    else:
        score = 100

    # Tendance
    if nb_depassement > nb_chantiers * 0.2:
        tendance = "baisse"
    elif nb_ok > nb_chantiers * 0.8:
        tendance = "hausse"
    else:
        tendance = "stable"

    return {
        "synthese": synthese,
        "alertes": alertes[:3],
        "recommandations": recommandations[:3],
        "tendance": tendance,
        "score_sante": score,
        "source": "regles",
        "ai_available": False,
    }


# =============================================================================
# Routes Suggestions Financieres (FIN-21/22)
# =============================================================================


@router.get("/chantiers/{chantier_id}/suggestions")
async def get_suggestions_financieres(
    chantier_id: int,
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_suggestions_financieres_use_case),
):
    """Suggestions financieres algorithmiques pour un chantier.

    FIN-21/22: Genere des suggestions deterministes (pas d'IA)
    et des indicateurs predictifs (burn rate, date epuisement).
    """
    _check_chantier_access(chantier_id, _role, user_chantier_ids)
    try:
        result = use_case.execute(chantier_id)
        return result.to_dict()
    except BudgetNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Aucun budget pour ce chantier",
        )


# =============================================================================
# Routes Journal Financier (FIN-15)
# =============================================================================


@router.get("/journal-financier")
async def list_journal_financier(
    entite_type: Optional[str] = None,
    entite_id: Optional[int] = Query(None, gt=0),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    journal_repo=Depends(get_journal_financier_repository),
):
    """Liste les entrees du journal financier.

    FIN-15: Audit trail - Conducteurs et admins.
    """
    # L-04: Valider entite_type contre les valeurs autorisees
    if entite_type and entite_type not in ENTITE_TYPES_AUTORISES:
        raise HTTPException(
            status_code=400,
            detail=f"Type d'entité invalide: {entite_type}. "
            f"Valeurs autorisées: {', '.join(sorted(ENTITE_TYPES_AUTORISES))}",
        )
    if entite_type and entite_id:
        entries = journal_repo.find_by_entite(
            entite_type=entite_type,
            entite_id=entite_id,
            limit=limit,
            offset=offset,
        )
        total = journal_repo.count_by_entite(entite_type, entite_id)
    else:
        # Lister les entrees de l'auteur courant comme fallback
        entries = journal_repo.find_by_auteur(
            auteur_id=current_user_id,
            limit=limit,
            offset=offset,
        )
        total = len(entries) if len(entries) < limit else limit + 1

    return {
        "items": [
            {
                "id": entry.id,
                "entite_type": entry.entite_type,
                "entite_id": entry.entite_id,
                "chantier_id": entry.chantier_id,
                "action": entry.action,
                "details": entry.details,
                "auteur_id": entry.auteur_id,
                "created_at": entry.created_at.isoformat() if entry.created_at else None,
            }
            for entry in entries
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


# =============================================================================
# Schemas Pydantic - Avenants (FIN-04)
# =============================================================================


class AvenantCreateRequest(BaseModel):
    """Requete de creation d'avenant budgetaire."""

    budget_id: int = Field(..., gt=0)
    motif: str = Field(..., min_length=1, max_length=500)
    montant_ht: Decimal = Field(default=Decimal("0"))
    impact_description: Optional[str] = Field(None, max_length=2000)


class AvenantUpdateRequest(BaseModel):
    """Requete de mise a jour d'avenant budgetaire."""

    motif: Optional[str] = Field(None, min_length=1, max_length=500)
    montant_ht: Optional[Decimal] = None
    impact_description: Optional[str] = Field(None, max_length=2000)


# =============================================================================
# Routes Avenants (FIN-04)
# =============================================================================


@router.get("/budgets/{budget_id}/avenants")
async def list_avenants(
    budget_id: int,
    _role: str = Depends(require_chef_or_above),
    current_user_id: int = Depends(get_current_user_id),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_list_avenants_use_case),
    budget_use_case=Depends(get_get_budget_use_case),
):
    """Liste les avenants d'un budget.

    FIN-04: Accessible aux chefs de chantier et superieurs.
    """
    # IDOR: verifier acces au chantier via le budget
    try:
        budget_dto = budget_use_case.execute(budget_id)
        _check_chantier_access(budget_dto.chantier_id, _role, user_chantier_ids)
    except BudgetNotFoundError:
        raise HTTPException(status_code=404, detail="Budget non trouve")
    result = use_case.execute(budget_id)
    return {
        "items": [a.to_dict() for a in result],
        "total": len(result),
    }


@router.post("/avenants", status_code=status.HTTP_201_CREATED)
async def create_avenant(
    request: AvenantCreateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    use_case=Depends(get_create_avenant_use_case),
    budget_use_case=Depends(get_get_budget_use_case),
):
    """Cree un nouvel avenant budgetaire.

    FIN-04: Conducteurs et admins.
    """
    # Gel financier : verifier que le chantier du budget n'est pas ferme
    try:
        budget_dto = budget_use_case.execute(request.budget_id)
        _check_chantier_not_closed(budget_dto.chantier_id, db)
    except BudgetNotFoundError:
        raise HTTPException(status_code=404, detail="Budget non trouve")
    try:
        dto = AvenantCreateDTO(
            budget_id=request.budget_id,
            motif=request.motif,
            montant_ht=request.montant_ht,
            impact_description=request.impact_description,
        )
        result = use_case.execute(dto, current_user_id)
        return result.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/avenants/{avenant_id}")
async def update_avenant(
    avenant_id: int,
    request: AvenantUpdateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_update_avenant_use_case),
):
    """Met a jour un avenant budgetaire (brouillon uniquement).

    FIN-04: Conducteurs et admins.
    """
    try:
        dto = AvenantUpdateDTO(
            motif=request.motif,
            montant_ht=request.montant_ht,
            impact_description=request.impact_description,
        )
        result = use_case.execute(avenant_id, dto, current_user_id)
        return result.to_dict()
    except AvenantNotFoundError:
        raise HTTPException(status_code=404, detail="Avenant non trouve")
    except AvenantAlreadyValideError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/avenants/{avenant_id}/valider")
async def valider_avenant(
    avenant_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_valider_avenant_use_case),
):
    """Valide un avenant budgetaire et met a jour le budget.

    FIN-04: Conducteurs et admins.
    """
    try:
        result = use_case.execute(avenant_id, current_user_id)
        return result.to_dict()
    except AvenantNotFoundError:
        raise HTTPException(status_code=404, detail="Avenant non trouve")
    except AvenantAlreadyValideError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/avenants/{avenant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_avenant(
    avenant_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_delete_avenant_use_case),
):
    """Supprime un avenant budgetaire (soft delete, brouillon uniquement).

    FIN-04: Conducteurs et admins.
    """
    try:
        use_case.execute(avenant_id, current_user_id)
    except AvenantNotFoundError:
        raise HTTPException(status_code=404, detail="Avenant non trouve")
    except AvenantAlreadyValideError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# Schemas Pydantic - Situations (FIN-07)
# =============================================================================


class LigneSituationCreateRequest(BaseModel):
    """Requete pour une ligne de situation (avancement par lot)."""

    lot_budgetaire_id: int = Field(..., gt=0)
    pourcentage_avancement: Decimal = Field(default=Decimal("0"), ge=0, le=100)


class SituationCreateRequest(BaseModel):
    """Requete de creation de situation de travaux."""

    chantier_id: int = Field(..., gt=0)
    budget_id: int = Field(..., gt=0)
    periode_debut: date
    periode_fin: date
    retenue_garantie_pct: Decimal = Field(default=Decimal("5.00"), ge=0, le=5, description="Loi 71-584: max 5%")
    taux_tva: Decimal = Field(default=Decimal("20.00"), ge=0)
    notes: Optional[str] = Field(None, max_length=2000)
    lignes: list[LigneSituationCreateRequest] = Field(default_factory=list)


class SituationUpdateRequest(BaseModel):
    """Requete de mise a jour de situation de travaux."""

    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    retenue_garantie_pct: Optional[Decimal] = Field(None, ge=0, le=5, description="Loi 71-584: max 5%")
    taux_tva: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=2000)
    lignes: Optional[list[LigneSituationCreateRequest]] = None


# =============================================================================
# Routes Situations (FIN-07)
# =============================================================================


@router.get("/chantiers/{chantier_id}/situations")
async def list_situations(
    chantier_id: int,
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_list_situations_use_case),
):
    """Liste les situations de travaux d'un chantier.

    FIN-07: Accessible aux chefs de chantier et superieurs.
    """
    _check_chantier_access(chantier_id, _role, user_chantier_ids)
    result = use_case.execute(chantier_id)
    return {
        "items": [s.to_dict() for s in result],
        "total": len(result),
    }


@router.post("/situations", status_code=status.HTTP_201_CREATED)
async def create_situation(
    request: SituationCreateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    db: Session = Depends(get_db),
    use_case=Depends(get_create_situation_use_case),
):
    """Cree une situation de travaux (auto-creation des lignes depuis les lots).

    FIN-07: Conducteurs et admins.
    """
    _check_chantier_access(request.chantier_id, _role, user_chantier_ids)
    _check_chantier_not_closed(request.chantier_id, db)
    try:
        lignes_dto = [
            LigneSituationCreateDTO(
                lot_budgetaire_id=l.lot_budgetaire_id,
                pourcentage_avancement=l.pourcentage_avancement,
            )
            for l in request.lignes
        ]
        dto = SituationCreateDTO(
            chantier_id=request.chantier_id,
            budget_id=request.budget_id,
            periode_debut=request.periode_debut,
            periode_fin=request.periode_fin,
            retenue_garantie_pct=request.retenue_garantie_pct,
            taux_tva=request.taux_tva,
            notes=request.notes,
            lignes=lignes_dto,
        )
        result = use_case.execute(dto, current_user_id)
        return result.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/situations/{situation_id}")
async def update_situation(
    situation_id: int,
    request: SituationUpdateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_update_situation_use_case),
):
    """Met a jour une situation de travaux (brouillon uniquement).

    FIN-07: Conducteurs et admins.
    """
    try:
        lignes_dto = None
        if request.lignes is not None:
            lignes_dto = [
                LigneSituationCreateDTO(
                    lot_budgetaire_id=l.lot_budgetaire_id,
                    pourcentage_avancement=l.pourcentage_avancement,
                )
                for l in request.lignes
            ]
        dto = SituationUpdateDTO(
            periode_debut=request.periode_debut,
            periode_fin=request.periode_fin,
            retenue_garantie_pct=request.retenue_garantie_pct,
            taux_tva=request.taux_tva,
            notes=request.notes,
            lignes=lignes_dto,
        )
        result = use_case.execute(situation_id, dto, current_user_id)
        return result.to_dict()
    except SituationNotFoundError:
        raise HTTPException(status_code=404, detail="Situation non trouvee")
    except SituationWorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/situations/{situation_id}/soumettre")
async def soumettre_situation(
    situation_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    use_case=Depends(get_soumettre_situation_use_case),
    get_situation_uc=Depends(get_get_situation_use_case),
):
    """Soumet une situation pour validation (brouillon -> en_validation).

    FIN-07: Conducteurs et admins.
    """
    try:
        existing = get_situation_uc.execute(situation_id)
    except SituationNotFoundError:
        raise HTTPException(status_code=404, detail="Situation non trouvee")
    _check_chantier_not_closed(existing.chantier_id, db)
    try:
        result = use_case.execute(situation_id, current_user_id)
        return result.to_dict()
    except SituationNotFoundError:
        raise HTTPException(status_code=404, detail="Situation non trouvee")
    except SituationWorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/situations/{situation_id}/valider")
async def valider_situation(
    situation_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_valider_situation_use_case),
):
    """Valide et emet une situation (en_validation -> emise).

    FIN-07: Conducteurs et admins.
    """
    try:
        result = use_case.execute(situation_id, current_user_id)
        return result.to_dict()
    except SituationNotFoundError:
        raise HTTPException(status_code=404, detail="Situation non trouvee")
    except SituationWorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/situations/{situation_id}/valider-client")
async def valider_client_situation(
    situation_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_marquer_validee_client_use_case),
):
    """Marque une situation comme validee par le client (emise -> validee).

    FIN-07: Conducteurs et admins.
    """
    try:
        result = use_case.execute(situation_id, current_user_id)
        return result.to_dict()
    except SituationNotFoundError:
        raise HTTPException(status_code=404, detail="Situation non trouvee")
    except SituationWorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/situations/{situation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_situation(
    situation_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_delete_situation_use_case),
):
    """Supprime une situation de travaux (soft delete, brouillon uniquement).

    FIN-07: Conducteurs et admins.
    """
    try:
        use_case.execute(situation_id, current_user_id)
    except SituationNotFoundError:
        raise HTTPException(status_code=404, detail="Situation non trouvee")
    except SituationWorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/situations/{situation_id}")
async def get_situation(
    situation_id: int,
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_get_situation_use_case),
):
    """Recupere une situation de travaux avec ses lignes.

    FIN-07: Accessible aux chefs de chantier et superieurs.
    """
    try:
        result = use_case.execute(situation_id)
        _check_chantier_access(result.chantier_id, _role, user_chantier_ids)
        return result.to_dict()
    except SituationNotFoundError:
        raise HTTPException(status_code=404, detail="Situation non trouvee")


# =============================================================================
# Schemas Pydantic - Factures (FIN-08)
# =============================================================================


class FactureFromSituationRequest(BaseModel):
    """Requete de creation de facture depuis une situation."""

    situation_id: int = Field(..., gt=0)


class FactureAcompteCreateRequest(BaseModel):
    """Requete de creation de facture d'acompte."""

    chantier_id: int = Field(..., gt=0)
    montant_ht: Decimal = Field(..., ge=0)
    taux_tva: Decimal = Field(default=Decimal("20.00"), ge=0)
    retenue_garantie_pct: Decimal = Field(default=Decimal("5.00"), ge=0, le=5, description="Loi 71-584: max 5%")
    notes: Optional[str] = Field(None, max_length=2000)


# =============================================================================
# Routes Factures (FIN-08)
# =============================================================================


@router.get("/chantiers/{chantier_id}/factures")
async def list_factures(
    chantier_id: int,
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_list_factures_use_case),
):
    """Liste les factures d'un chantier.

    FIN-08: Accessible aux chefs de chantier et superieurs.
    """
    _check_chantier_access(chantier_id, _role, user_chantier_ids)
    result = use_case.execute(chantier_id)
    return {
        "items": [f.to_dict() for f in result],
        "total": len(result),
    }


@router.post("/factures/from-situation", status_code=status.HTTP_201_CREATED)
async def create_facture_from_situation(
    request: FactureFromSituationRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_create_facture_from_situation_use_case),
):
    """Cree une facture a partir d'une situation validee.

    FIN-08: Conducteurs et admins.
    """
    try:
        result = use_case.execute(request.situation_id, current_user_id)
        return result.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SituationNonValideeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/factures/acompte", status_code=status.HTTP_201_CREATED)
async def create_facture_acompte(
    request: FactureAcompteCreateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_create_facture_acompte_use_case),
):
    """Cree une facture d'acompte (sans situation).

    FIN-08: Conducteurs et admins.
    """
    _check_chantier_access(request.chantier_id, _role, user_chantier_ids)
    try:
        dto = FactureCreateDTO(
            chantier_id=request.chantier_id,
            type_facture="acompte",
            montant_ht=request.montant_ht,
            taux_tva=request.taux_tva,
            retenue_garantie_pct=request.retenue_garantie_pct,
            notes=request.notes,
        )
        result = use_case.execute(dto, current_user_id)
        return result.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/factures/{facture_id}/emettre")
async def emettre_facture(
    facture_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_emettre_facture_use_case),
):
    """Emet une facture (brouillon -> emise).

    FIN-08: Conducteurs et admins.
    """
    try:
        result = use_case.execute(facture_id, current_user_id)
        return result.to_dict()
    except FactureNotFoundError:
        raise HTTPException(status_code=404, detail="Facture non trouvee")
    except FactureWorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/factures/{facture_id}/envoyer")
async def envoyer_facture(
    facture_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_envoyer_facture_use_case),
):
    """Envoie une facture au client (emise -> envoyee).

    FIN-08: Conducteurs et admins.
    """
    try:
        result = use_case.execute(facture_id, current_user_id)
        return result.to_dict()
    except FactureNotFoundError:
        raise HTTPException(status_code=404, detail="Facture non trouvee")
    except FactureWorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/factures/{facture_id}/payer")
async def marquer_payee_facture(
    facture_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_marquer_payee_facture_use_case),
):
    """Marque une facture comme payee (envoyee -> payee).

    FIN-08: Conducteurs et admins.
    """
    try:
        result = use_case.execute(facture_id, current_user_id)
        return result.to_dict()
    except FactureNotFoundError:
        raise HTTPException(status_code=404, detail="Facture non trouvee")
    except FactureWorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/factures/{facture_id}/annuler")
async def annuler_facture(
    facture_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_annuler_facture_use_case),
):
    """Annule une facture (brouillon/emise -> annulee).

    FIN-08: Conducteurs et admins.
    """
    try:
        result = use_case.execute(facture_id, current_user_id)
        return result.to_dict()
    except FactureNotFoundError:
        raise HTTPException(status_code=404, detail="Facture non trouvee")
    except FactureWorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/factures/{facture_id}")
async def get_facture(
    facture_id: int,
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_get_facture_use_case),
):
    """Recupere une facture par son ID.

    FIN-08: Accessible aux chefs de chantier et superieurs.
    """
    try:
        result = use_case.execute(facture_id)
        _check_chantier_access(result.chantier_id, _role, user_chantier_ids)
        return result.to_dict()
    except FactureNotFoundError:
        raise HTTPException(status_code=404, detail="Facture non trouvee")


# =============================================================================
# Routes Couts Main-d'Oeuvre (FIN-09)
# =============================================================================


@router.get("/chantiers/{chantier_id}/couts-main-oeuvre")
async def get_couts_main_oeuvre(
    chantier_id: int,
    date_debut: Optional[date] = Query(None),
    date_fin: Optional[date] = Query(None),
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_cout_main_oeuvre_use_case),
):
    """Recupere les couts main-d'oeuvre d'un chantier.

    FIN-09: Accessible aux chefs de chantier et superieurs.
    Filtres optionnels par periode (date_debut, date_fin).
    """
    _check_chantier_access(chantier_id, _role, user_chantier_ids)
    result = use_case.execute(chantier_id, date_debut, date_fin)
    return {
        "chantier_id": result.chantier_id,
        "total_heures": result.total_heures,
        "cout_total": result.cout_total,
        "details": [
            {
                "user_id": d.user_id,
                "nom": d.nom,
                "prenom": d.prenom,
                "heures_validees": d.heures_validees,
                "taux_horaire": d.taux_horaire,
                "taux_horaire_charge": d.taux_horaire_charge,
                "cout_total": d.cout_total,
            }
            for d in result.details
        ],
    }


# =============================================================================
# Routes Couts Materiel (FIN-10)
# =============================================================================


@router.get("/chantiers/{chantier_id}/couts-materiel")
async def get_couts_materiel(
    chantier_id: int,
    date_debut: Optional[date] = Query(None),
    date_fin: Optional[date] = Query(None),
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_cout_materiel_use_case),
):
    """Recupere les couts materiel d'un chantier.

    FIN-10: Accessible aux chefs de chantier et superieurs.
    Filtres optionnels par periode (date_debut, date_fin).
    Calcule les couts a partir des reservations validees (module logistique).
    """
    _check_chantier_access(chantier_id, _role, user_chantier_ids)
    result = use_case.execute(chantier_id, date_debut, date_fin)
    return result


# =============================================================================
# Routes Alertes (FIN-12)
# =============================================================================


@router.get("/chantiers/{chantier_id}/alertes")
async def list_alertes(
    chantier_id: int,
    non_acquittees_seulement: bool = Query(default=False),
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_list_alertes_use_case),
):
    """Liste les alertes de depassement d'un chantier.

    FIN-12: Accessible aux chefs de chantier et superieurs.
    """
    _check_chantier_access(chantier_id, _role, user_chantier_ids)
    result = use_case.execute(chantier_id, non_acquittees_seulement)
    return {
        "items": [a.to_dict() for a in result],
        "total": len(result),
    }


@router.post("/chantiers/{chantier_id}/alertes/verifier")
async def verifier_depassement(
    chantier_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_verifier_depassement_use_case),
):
    """Declenche une verification des depassements budgetaires.

    FIN-12: Conducteurs et admins.
    """
    _check_chantier_access(chantier_id, _role, user_chantier_ids)
    try:
        result = use_case.execute(chantier_id)
        return {
            "alertes_creees": [a.to_dict() for a in result],
            "total": len(result),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/alertes/{alerte_id}/acquitter")
async def acquitter_alerte(
    alerte_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_acquitter_alerte_use_case),
):
    """Acquitte une alerte de depassement.

    FIN-12: Conducteurs et admins.
    """
    try:
        result = use_case.execute(alerte_id, current_user_id)
        return result.to_dict()
    except AlerteNotFoundError:
        raise HTTPException(status_code=404, detail="Alerte non trouvee")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# Schemas Pydantic - Affectations Budget-Tache (FIN-03)
# =============================================================================


class AffectationCreateRequest(BaseModel):
    """Requete de creation d'affectation budget-tache."""

    tache_id: int = Field(..., gt=0)
    pourcentage_allocation: Decimal = Field(..., ge=0, le=100)


# =============================================================================
# Routes Affectations Budget-Tache (FIN-03)
# =============================================================================


@router.post(
    "/lots/{lot_id}/affectations",
    status_code=status.HTTP_201_CREATED,
)
async def create_affectation(
    lot_id: int,
    request: AffectationCreateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    use_case=Depends(get_create_affectation_use_case),
):
    """Cree une affectation entre un lot budgetaire et une tache.

    FIN-03: Affectation budgets aux taches - Conducteurs et admins.
    """
    try:
        dto = CreateAffectationDTO(
            lot_budgetaire_id=lot_id,
            tache_id=request.tache_id,
            pourcentage_allocation=request.pourcentage_allocation,
        )
        result = use_case.execute(dto)
        return result.to_dict()
    except LotBudgetaireIntrouvableError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AllocationDepasseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/affectations/{affectation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_affectation(
    affectation_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case=Depends(get_delete_affectation_use_case),
):
    """Supprime une affectation budget-tache.

    FIN-03: Conducteurs et admins.
    """
    try:
        use_case.execute(affectation_id)
    except AffectationNotFoundError:
        raise HTTPException(status_code=404, detail="Affectation non trouvee")


@router.get("/chantiers/{chantier_id}/affectations")
async def list_affectations_by_chantier(
    chantier_id: int,
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_list_affectations_by_chantier_use_case),
):
    """Liste les affectations budget-tache d'un chantier avec details lots.

    FIN-03: Accessible aux chefs de chantier et superieurs.
    """
    _check_chantier_access(chantier_id, _role, user_chantier_ids)
    result = use_case.execute(chantier_id)
    return {
        "items": [a.to_dict() for a in result],
        "total": len(result),
    }


@router.get("/taches/{tache_id}/affectations")
async def get_affectations_by_tache(
    tache_id: int,
    _role: str = Depends(require_chef_or_above),
    use_case=Depends(get_affectations_by_tache_use_case),
):
    """Liste les lots budgetaires affectes a une tache.

    FIN-03: Accessible aux chefs de chantier et superieurs.
    """
    result = use_case.execute(tache_id)
    return {
        "items": [a.to_dict() for a in result],
        "total": len(result),
    }


# =============================================================================
# Routes Export Comptable (FIN-13)
# =============================================================================


@router.get("/chantiers/{chantier_id}/export")
async def export_comptable(
    chantier_id: int,
    format: str = Query(default="csv", pattern="^(csv|xlsx)$"),
    _role: str = Depends(require_conducteur_or_admin),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_export_comptable_use_case),
):
    """Exporte les donnees comptables d'un chantier en CSV ou Excel.

    FIN-13: Export comptable - Conducteurs et admins.

    Args:
        chantier_id: ID du chantier.
        format: Format d'export (csv ou xlsx).

    Returns:
        StreamingResponse avec le fichier CSV ou Excel.
    """
    _check_chantier_access(chantier_id, _role, user_chantier_ids)
    try:
        dto = use_case.execute(chantier_id)

        if format == "xlsx":
            content = use_case.to_xlsx(dto)
            return StreamingResponse(
                iter([content]),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": (
                        f'attachment; filename="export_comptable_chantier_{chantier_id}.xlsx"'
                    ),
                },
            )
        else:
            content = use_case.to_csv(dto)
            return StreamingResponse(
                iter([content]),
                media_type="text/csv; charset=utf-8",
                headers={
                    "Content-Disposition": (
                        f'attachment; filename="export_comptable_chantier_{chantier_id}.csv"'
                    ),
                },
            )
    except ExportComptableError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(
            "Erreur lors de l'export comptable",
            extra={"event": "export.error", "chantier_id": chantier_id},
        )
        raise HTTPException(status_code=500, detail="Erreur serveur interne")


# =============================================================================
# Routes P&L - Profit & Loss (GAP #9)
# =============================================================================


@router.get("/chantiers/{chantier_id}/pnl")
async def get_pnl_chantier(
    chantier_id: int,
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_pnl_chantier_use_case),
):
    """Profit & Loss d'un chantier.

    GAP #9: Vue P&L montrant CA (factures emises), couts reels
    (achats + MO + materiel), marge brute et marge %.
    Accessible aux chefs de chantier et superieurs.
    """
    _check_chantier_access(chantier_id, _role, user_chantier_ids)
    try:
        result = use_case.execute(chantier_id)
        return result.to_dict()
    except PnLChantierNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Aucun budget pour ce chantier",
        )
    except Exception as e:
        logger.exception(
            "Erreur lors du calcul du P&L",
            extra={"event": "pnl.error", "chantier_id": chantier_id},
        )
        raise HTTPException(
            status_code=500,
            detail="Erreur serveur interne",
        )


# =============================================================================
# Routes Bilan de Cloture (GAP #10)
# =============================================================================


@router.get("/chantiers/{chantier_id}/bilan-cloture")
async def get_bilan_cloture(
    chantier_id: int,
    _role: str = Depends(require_chef_or_above),
    user_chantier_ids: list[int] | None = Depends(get_current_user_chantier_ids),
    use_case=Depends(get_bilan_cloture_use_case),
):
    """Bilan de cloture d'un chantier.

    GAP #10: Rapport recapitulatif financier aggregeant budget, achats,
    avenants, situations et ecarts par lot. Disponible pour tout chantier,
    le champ ``est_definitif`` indique si le chantier est ferme.
    Accessible aux chefs de chantier et superieurs.
    """
    _check_chantier_access(chantier_id, _role, user_chantier_ids)
    try:
        result = use_case.execute(chantier_id)
        return result.to_dict()
    except BilanChantierNonTrouveError:
        raise HTTPException(
            status_code=404,
            detail="Chantier non trouve",
        )
    except BilanBudgetNonTrouveError:
        raise HTTPException(
            status_code=404,
            detail="Aucun budget pour ce chantier",
        )
    except BilanClotureError as e:
        raise HTTPException(
            status_code=400,
            detail=e.message,
        )
    except Exception as e:
        logger.exception(
            "Erreur lors du calcul du bilan de cloture",
            extra={"event": "bilan_cloture.error", "chantier_id": chantier_id},
        )
        raise HTTPException(
            status_code=500,
            detail="Erreur serveur interne",
        )


# =============================================================================
# Routes Configuration Entreprise (Admin Only)
# =============================================================================


class ConfigurationEntrepriseUpdateRequest(BaseModel):
    """Requete de mise a jour de la configuration entreprise."""

    couts_fixes_annuels: Optional[float] = Field(None, ge=0, description="Couts fixes annuels en EUR")
    coeff_frais_generaux: Optional[float] = Field(None, ge=0, le=100, description="Coefficient frais generaux (%)")
    coeff_charges_patronales: Optional[float] = Field(None, ge=1, description="Coefficient charges patronales (ex: 1.45)")
    coeff_heures_sup: Optional[float] = Field(None, ge=1, description="Coefficient heures sup (ex: 1.25)")
    coeff_heures_sup_2: Optional[float] = Field(None, ge=1, description="Coefficient heures sup 2e palier (ex: 1.50)")
    notes: Optional[str] = Field(None, max_length=1000)


@router.get("/configuration/{annee}")
async def get_configuration_entreprise(
    annee: int = Path(ge=2020, le=2099),
    _role: str = Depends(require_admin),
    use_case=Depends(get_get_configuration_entreprise_use_case),
):
    """Lecture de la configuration entreprise pour une annee.

    Acces reserve aux administrateurs.
    EDGE-003: retourne les valeurs par defaut si aucune config en BDD.
    """
    result, is_default = use_case.execute(annee)

    # Alerte revalidation: warning si config non mise a jour depuis 180+ jours
    stale_warning = None
    if not is_default and result.updated_at:
        age = datetime.utcnow() - result.updated_at
        if age > timedelta(days=180):
            jours = age.days
            stale_warning = (
                f"Cette configuration n'a pas ete mise a jour depuis {jours} jours. "
                "Pensez a revalider les parametres financiers."
            )

    return {
        "id": result.id,
        "couts_fixes_annuels": str(result.couts_fixes_annuels),
        "annee": result.annee,
        "coeff_frais_generaux": str(result.coeff_frais_generaux),
        "coeff_charges_patronales": str(result.coeff_charges_patronales),
        "coeff_heures_sup": str(result.coeff_heures_sup),
        "coeff_heures_sup_2": str(result.coeff_heures_sup_2),
        "notes": result.notes,
        "updated_at": result.updated_at.isoformat() if result.updated_at else None,
        "updated_by": result.updated_by,
        "is_default": is_default,
        "stale_warning": stale_warning,
    }


@router.put("/configuration/{annee}")
async def update_configuration_entreprise(
    annee: int = Path(ge=2020, le=2099),
    request: ConfigurationEntrepriseUpdateRequest = ...,
    _role: str = Depends(require_admin),
    user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_update_configuration_entreprise_use_case),
):
    """Mise a jour de la configuration entreprise pour une annee.

    Acces reserve aux administrateurs.
    EDGE-001: si aucune config n'existe, en cree une (created=true).
    VAL-002/EDGE-002: renvoie des warnings pour valeurs suspectes.
    """
    try:
        dto = ConfigurationEntrepriseUpdateDTO(
            couts_fixes_annuels=Decimal(str(request.couts_fixes_annuels)) if request.couts_fixes_annuels is not None else None,
            coeff_frais_generaux=Decimal(str(request.coeff_frais_generaux)) if request.coeff_frais_generaux is not None else None,
            coeff_charges_patronales=Decimal(str(request.coeff_charges_patronales)) if request.coeff_charges_patronales is not None else None,
            coeff_heures_sup=Decimal(str(request.coeff_heures_sup)) if request.coeff_heures_sup is not None else None,
            coeff_heures_sup_2=Decimal(str(request.coeff_heures_sup_2)) if request.coeff_heures_sup_2 is not None else None,
            notes=request.notes,
        )
        result, created, warnings = use_case.execute(annee, dto, user_id)
        return {
            "id": result.id,
            "couts_fixes_annuels": str(result.couts_fixes_annuels),
            "annee": result.annee,
            "coeff_frais_generaux": str(result.coeff_frais_generaux),
            "coeff_charges_patronales": str(result.coeff_charges_patronales),
            "coeff_heures_sup": str(result.coeff_heures_sup),
            "coeff_heures_sup_2": str(result.coeff_heures_sup_2),
            "notes": result.notes,
            "updated_at": result.updated_at.isoformat() if result.updated_at else None,
            "updated_by": result.updated_by,
            "created": created,
            "warnings": warnings,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=str(e),
        )
