"""Routes FastAPI pour le module Devis.

DEV-03: CRUD devis
DEV-15: Workflow statut
DEV-17: Dashboard
DEV-19: Recherche avancee
"""

from datetime import date
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from shared.infrastructure.web import (
    get_current_user_id,
    get_current_user_role,
    require_conducteur_or_admin,
)

from ...domain.entities.devis import TransitionStatutDevisInvalideError
from ...domain.value_objects import StatutDevis
from ...application.use_cases.devis_use_cases import (
    DevisNotFoundError,
    DevisNotModifiableError,
)
from ...application.dtos.devis_dtos import DevisCreateDTO, DevisUpdateDTO

from .dependencies import (
    get_create_devis_use_case,
    get_update_devis_use_case,
    get_get_devis_use_case,
    get_list_devis_use_case,
    get_delete_devis_use_case,
    get_soumettre_devis_use_case,
    get_valider_devis_use_case,
    get_retourner_brouillon_use_case,
    get_accepter_devis_use_case,
    get_refuser_devis_use_case,
    get_perdu_devis_use_case,
    get_search_devis_use_case,
    get_dashboard_devis_use_case,
    get_calculer_totaux_use_case,
    get_journal_devis_use_case,
    get_create_lot_use_case,
    get_update_lot_use_case,
    get_delete_lot_use_case,
    get_create_ligne_use_case,
    get_update_ligne_use_case,
    get_delete_ligne_use_case,
    get_create_article_use_case,
    get_list_articles_use_case,
    get_get_article_use_case,
    get_delete_article_use_case,
)


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic request models
# ─────────────────────────────────────────────────────────────────────────────

class DevisCreateRequest(BaseModel):
    client_nom: str = Field(..., min_length=1, max_length=200)
    objet: str = Field(..., min_length=1, max_length=500)
    chantier_ref: Optional[str] = Field(None, max_length=50)
    client_adresse: Optional[str] = Field(None, max_length=500)
    client_email: Optional[str] = Field(None, max_length=255)
    client_telephone: Optional[str] = Field(None, max_length=30)
    date_validite: Optional[date] = None
    taux_tva_defaut: Decimal = Decimal("20")
    taux_marge_global: Decimal = Decimal("15")
    taux_marge_moe: Optional[Decimal] = None
    taux_marge_materiaux: Optional[Decimal] = None
    taux_marge_sous_traitance: Optional[Decimal] = None
    taux_marge_materiel: Optional[Decimal] = None
    taux_marge_deplacement: Optional[Decimal] = None
    coefficient_frais_generaux: Decimal = Decimal("12")
    retenue_garantie_pct: Decimal = Decimal("0")
    notes: Optional[str] = Field(None, max_length=2000)
    commercial_id: Optional[int] = None
    conducteur_id: Optional[int] = None


class DevisUpdateRequest(BaseModel):
    client_nom: Optional[str] = Field(None, min_length=1, max_length=200)
    objet: Optional[str] = Field(None, min_length=1, max_length=500)
    chantier_ref: Optional[str] = Field(None, max_length=50)
    client_adresse: Optional[str] = Field(None, max_length=500)
    client_email: Optional[str] = Field(None, max_length=255)
    client_telephone: Optional[str] = Field(None, max_length=30)
    date_validite: Optional[date] = None
    taux_tva_defaut: Optional[Decimal] = None
    taux_marge_global: Optional[Decimal] = None
    taux_marge_moe: Optional[Decimal] = None
    taux_marge_materiaux: Optional[Decimal] = None
    taux_marge_sous_traitance: Optional[Decimal] = None
    taux_marge_materiel: Optional[Decimal] = None
    taux_marge_deplacement: Optional[Decimal] = None
    coefficient_frais_generaux: Optional[Decimal] = None
    retenue_garantie_pct: Optional[Decimal] = None
    notes: Optional[str] = Field(None, max_length=2000)
    commercial_id: Optional[int] = None
    conducteur_id: Optional[int] = None


class MotifRequest(BaseModel):
    motif: str = Field(..., min_length=1, max_length=1000)


class LotCreateRequest(BaseModel):
    devis_id: int
    titre: str = Field(..., min_length=1, max_length=300)
    numero: str = ""
    ordre: int = 0
    marge_lot_pct: Optional[Decimal] = None


class LotUpdateRequest(BaseModel):
    titre: Optional[str] = Field(None, min_length=1, max_length=300)
    numero: Optional[str] = None
    ordre: Optional[int] = None
    marge_lot_pct: Optional[Decimal] = None


class DebourseCreateRequest(BaseModel):
    type_debourse: str = Field(..., min_length=1)
    designation: str = Field(..., min_length=1, max_length=300)
    quantite: Decimal = Decimal("0")
    prix_unitaire: Decimal = Decimal("0")
    unite: str = "U"


class LigneCreateRequest(BaseModel):
    lot_devis_id: int
    designation: str = Field(..., min_length=1, max_length=500)
    unite: str = "U"
    quantite: Decimal = Decimal("0")
    prix_unitaire_ht: Decimal = Decimal("0")
    taux_tva: Decimal = Decimal("20")
    ordre: int = 0
    marge_ligne_pct: Optional[Decimal] = None
    article_id: Optional[int] = None
    debourses: List[DebourseCreateRequest] = []


class LigneUpdateRequest(BaseModel):
    designation: Optional[str] = Field(None, min_length=1, max_length=500)
    unite: Optional[str] = None
    quantite: Optional[Decimal] = None
    prix_unitaire_ht: Optional[Decimal] = None
    taux_tva: Optional[Decimal] = None
    ordre: Optional[int] = None
    marge_ligne_pct: Optional[Decimal] = None
    article_id: Optional[int] = None
    debourses: Optional[List[DebourseCreateRequest]] = None


# ─────────────────────────────────────────────────────────────────────────────
# Router
# ─────────────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/devis", tags=["devis"])


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/dashboard")
async def get_dashboard(
    _role: str = Depends(require_conducteur_or_admin),
    use_case=Depends(get_dashboard_devis_use_case),
):
    """Tableau de bord devis - KPI pipeline commercial (DEV-17)."""
    result = use_case.execute()
    return result.to_dict()


# ─────────────────────────────────────────────────────────────────────────────
# Devis CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("")
async def list_devis(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _role: str = Depends(require_conducteur_or_admin),
    use_case=Depends(get_list_devis_use_case),
):
    """Liste les devis avec pagination (DEV-03)."""
    result = use_case.execute(limit=limit, offset=offset)
    return {
        "items": [d.to_dict() for d in result.items],
        "total": result.total,
        "limit": result.limit,
        "offset": result.offset,
    }


@router.get("/search")
async def search_devis(
    client_nom: Optional[str] = None,
    statut: Optional[str] = None,
    date_min: Optional[date] = None,
    date_max: Optional[date] = None,
    montant_min: Optional[Decimal] = None,
    montant_max: Optional[Decimal] = None,
    commercial_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _role: str = Depends(require_conducteur_or_admin),
    use_case=Depends(get_search_devis_use_case),
):
    """Recherche avancee de devis (DEV-19)."""
    statut_enum = None
    if statut:
        try:
            statut_enum = StatutDevis(statut)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Statut invalide: {statut}",
            )

    result = use_case.execute(
        client_nom=client_nom,
        statut=statut_enum,
        date_creation_min=date_min,
        date_creation_max=date_max,
        montant_min=montant_min,
        montant_max=montant_max,
        commercial_id=commercial_id,
        search=search,
        limit=limit,
        offset=offset,
    )
    return {
        "items": [d.to_dict() for d in result.items],
        "total": result.total,
        "limit": result.limit,
        "offset": result.offset,
    }


@router.get("/{devis_id}")
async def get_devis(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case=Depends(get_get_devis_use_case),
):
    """Recupere un devis avec ses details complets (DEV-03)."""
    try:
        result = use_case.execute(devis_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_devis(
    request: DevisCreateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_create_devis_use_case),
):
    """Cree un nouveau devis (DEV-03)."""
    dto = DevisCreateDTO(
        client_nom=request.client_nom,
        objet=request.objet,
        chantier_ref=request.chantier_ref,
        client_adresse=request.client_adresse,
        client_email=request.client_email,
        client_telephone=request.client_telephone,
        date_validite=request.date_validite,
        taux_tva_defaut=request.taux_tva_defaut,
        taux_marge_global=request.taux_marge_global,
        taux_marge_moe=request.taux_marge_moe,
        taux_marge_materiaux=request.taux_marge_materiaux,
        taux_marge_sous_traitance=request.taux_marge_sous_traitance,
        taux_marge_materiel=request.taux_marge_materiel,
        taux_marge_deplacement=request.taux_marge_deplacement,
        coefficient_frais_generaux=request.coefficient_frais_generaux,
        retenue_garantie_pct=request.retenue_garantie_pct,
        notes=request.notes,
        commercial_id=request.commercial_id,
        conducteur_id=request.conducteur_id,
    )
    result = use_case.execute(dto, current_user_id)
    return result.to_dict()


@router.put("/{devis_id}")
async def update_devis(
    devis_id: int,
    request: DevisUpdateRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_update_devis_use_case),
):
    """Met a jour un devis (DEV-03)."""
    dto = DevisUpdateDTO(**request.model_dump(exclude_unset=True))
    try:
        result = use_case.execute(devis_id, dto, current_user_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except DevisNotModifiableError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{devis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_devis(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_delete_devis_use_case),
):
    """Supprime un devis en brouillon (DEV-03)."""
    try:
        use_case.execute(devis_id, current_user_id)
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except DevisNotModifiableError as e:
        raise HTTPException(status_code=409, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Workflow transitions (DEV-15)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/{devis_id}/soumettre")
async def soumettre_devis(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_soumettre_devis_use_case),
):
    """Soumet un devis pour validation (brouillon -> en_validation)."""
    try:
        result = use_case.execute(devis_id, current_user_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except TransitionStatutDevisInvalideError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{devis_id}/valider")
async def valider_devis(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_valider_devis_use_case),
):
    """Valide et envoie un devis (en_validation -> envoye)."""
    try:
        result = use_case.execute(devis_id, current_user_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except TransitionStatutDevisInvalideError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{devis_id}/retourner-brouillon")
async def retourner_brouillon(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_retourner_brouillon_use_case),
):
    """Retourne un devis en brouillon (en_validation -> brouillon)."""
    try:
        result = use_case.execute(devis_id, current_user_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except TransitionStatutDevisInvalideError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{devis_id}/accepter")
async def accepter_devis(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_accepter_devis_use_case),
):
    """Accepte un devis (envoye/vu/en_negociation -> accepte)."""
    try:
        result = use_case.execute(devis_id, current_user_id)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except TransitionStatutDevisInvalideError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{devis_id}/refuser")
async def refuser_devis(
    devis_id: int,
    body: MotifRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_refuser_devis_use_case),
):
    """Refuse un devis avec motif (envoye/vu/en_negociation -> refuse)."""
    try:
        result = use_case.execute(devis_id, current_user_id, body.motif)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except TransitionStatutDevisInvalideError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{devis_id}/perdu")
async def marquer_perdu(
    devis_id: int,
    body: MotifRequest,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_perdu_devis_use_case),
):
    """Marque un devis comme perdu avec motif (en_negociation -> perdu)."""
    try:
        result = use_case.execute(devis_id, current_user_id, body.motif)
        return result.to_dict()
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")
    except TransitionStatutDevisInvalideError as e:
        raise HTTPException(status_code=409, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Calcul totaux (DEV-06)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/{devis_id}/calculer")
async def calculer_totaux(
    devis_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    current_user_id: int = Depends(get_current_user_id),
    use_case=Depends(get_calculer_totaux_use_case),
):
    """Recalcule les totaux et marges du devis (DEV-06)."""
    try:
        result = use_case.execute(devis_id, current_user_id)
        return result
    except DevisNotFoundError:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} non trouve")


# ─────────────────────────────────────────────────────────────────────────────
# Journal (DEV-18)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/{devis_id}/journal")
async def get_journal(
    devis_id: int,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _role: str = Depends(require_conducteur_or_admin),
    use_case=Depends(get_journal_devis_use_case),
):
    """Consulte le journal d'audit d'un devis (DEV-18)."""
    result = use_case.execute(devis_id, limit=limit, offset=offset)
    return {
        "items": [e.to_dict() for e in result["items"]],
        "total": result["total"],
        "limit": result["limit"],
        "offset": result["offset"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Articles (DEV-01) - sous-routeur
# ─────────────────────────────────────────────────────────────────────────────

articles_router = APIRouter(prefix="/articles-devis", tags=["articles-devis"])


@articles_router.get("")
async def list_articles(
    categorie: Optional[str] = None,
    search: Optional[str] = None,
    actif: bool = True,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _role: str = Depends(require_conducteur_or_admin),
    use_case=Depends(get_list_articles_use_case),
):
    """Liste les articles de la bibliotheque (DEV-01)."""
    result = use_case.execute(
        categorie=categorie,
        actif_seulement=actif,
        search=search,
        limit=limit,
        offset=offset,
    )
    return {
        "items": [a.to_dict() for a in result.items],
        "total": result.total,
        "limit": result.limit,
        "offset": result.offset,
    }


@articles_router.get("/{article_id}")
async def get_article(
    article_id: int,
    _role: str = Depends(require_conducteur_or_admin),
    use_case=Depends(get_get_article_use_case),
):
    """Recupere un article (DEV-01)."""
    from ...application.use_cases.article_use_cases import ArticleNotFoundError

    try:
        result = use_case.execute(article_id)
        return result.to_dict()
    except ArticleNotFoundError:
        raise HTTPException(status_code=404, detail=f"Article {article_id} non trouve")
