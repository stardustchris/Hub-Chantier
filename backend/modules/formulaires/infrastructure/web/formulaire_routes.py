"""Routes FastAPI pour le module Formulaires."""

from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from .dependencies import get_formulaire_controller, get_current_user_id
from ...adapters.controllers import FormulaireController


# ===== SCHEMAS PYDANTIC =====

class ChampTemplateSchema(BaseModel):
    """Schema pour un champ de template."""

    id: Optional[int] = None
    nom: str
    label: str
    type_champ: str
    obligatoire: bool = False
    ordre: int = 0
    placeholder: Optional[str] = None
    options: List[str] = Field(default_factory=list)
    valeur_defaut: Optional[str] = None
    validation_regex: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class CreateTemplateRequest(BaseModel):
    """Schema pour la creation d'un template."""

    nom: str
    categorie: str
    description: Optional[str] = None
    champs: List[ChampTemplateSchema] = Field(default_factory=list)


class UpdateTemplateRequest(BaseModel):
    """Schema pour la mise a jour d'un template."""

    nom: Optional[str] = None
    description: Optional[str] = None
    categorie: Optional[str] = None
    champs: Optional[List[ChampTemplateSchema]] = None
    is_active: Optional[bool] = None


class CreateFormulaireRequest(BaseModel):
    """Schema pour la creation d'un formulaire (FOR-11)."""

    template_id: int
    chantier_id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UpdateFormulaireRequest(BaseModel):
    """Schema pour la mise a jour d'un formulaire."""

    champs: Optional[List[dict]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AddPhotoRequest(BaseModel):
    """Schema pour l'ajout d'une photo (FOR-04)."""

    url: str
    nom_fichier: str
    champ_nom: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AddSignatureRequest(BaseModel):
    """Schema pour l'ajout d'une signature (FOR-05)."""

    signature_url: str
    signature_nom: str


class SubmitFormulaireRequest(BaseModel):
    """Schema pour la soumission d'un formulaire (FOR-07)."""

    signature_url: Optional[str] = None
    signature_nom: Optional[str] = None


class ValidateFormulaireRequest(BaseModel):
    """Schema pour la validation d'un formulaire."""

    pass  # Le valideur_id vient du current_user


# ===== ROUTERS =====

router = APIRouter(prefix="/formulaires", tags=["Formulaires"])
templates_router = APIRouter(prefix="/templates-formulaires", tags=["Templates Formulaires"])


# ===== TEMPLATE ROUTES =====

@templates_router.post("", status_code=status.HTTP_201_CREATED)
async def create_template(
    request: CreateTemplateRequest,
    controller: FormulaireController = Depends(get_formulaire_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Cree un template de formulaire (FOR-01)."""
    try:
        champs = [c.model_dump() for c in request.champs]
        result = controller.create_template(
            nom=request.nom,
            categorie=request.categorie,
            description=request.description,
            champs=champs,
            created_by=current_user_id,
        )
        return result
    except Exception as e:
        if "existe deja" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@templates_router.get("")
async def list_templates(
    query: Optional[str] = Query(None, description="Recherche textuelle"),
    categorie: Optional[str] = Query(None, description="Filtrer par categorie"),
    active_only: bool = Query(False, description="Templates actifs uniquement"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    controller: FormulaireController = Depends(get_formulaire_controller),
):
    """Liste les templates de formulaire (FOR-01)."""
    result = controller.list_templates(
        query=query,
        categorie=categorie,
        active_only=active_only,
        skip=skip,
        limit=limit,
    )
    return {
        "templates": result.templates,
        "total": result.total,
        "skip": result.skip,
        "limit": result.limit,
    }


@templates_router.get("/{template_id}")
async def get_template(
    template_id: int,
    controller: FormulaireController = Depends(get_formulaire_controller),
):
    """Recupere un template par ID."""
    try:
        return controller.get_template(template_id)
    except Exception as e:
        if "non trouve" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@templates_router.put("/{template_id}")
async def update_template(
    template_id: int,
    request: UpdateTemplateRequest,
    controller: FormulaireController = Depends(get_formulaire_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Met a jour un template de formulaire."""
    try:
        champs = [c.model_dump() for c in request.champs] if request.champs else None
        result = controller.update_template(
            template_id=template_id,
            nom=request.nom,
            description=request.description,
            categorie=request.categorie,
            champs=champs,
            is_active=request.is_active,
            updated_by=current_user_id,
        )
        return result
    except Exception as e:
        if "non trouve" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@templates_router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    controller: FormulaireController = Depends(get_formulaire_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Supprime un template de formulaire."""
    try:
        controller.delete_template(
            template_id=template_id,
            deleted_by=current_user_id,
        )
    except Exception as e:
        if "non trouve" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ===== FORMULAIRE ROUTES =====

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_formulaire(
    request: CreateFormulaireRequest,
    controller: FormulaireController = Depends(get_formulaire_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Cree un formulaire a remplir (FOR-11)."""
    try:
        result = controller.create_formulaire(
            template_id=request.template_id,
            chantier_id=request.chantier_id,
            user_id=current_user_id,
            latitude=request.latitude,
            longitude=request.longitude,
        )
        return result
    except Exception as e:
        if "non trouve" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "inactif" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("")
async def list_formulaires(
    chantier_id: Optional[int] = Query(None, description="Filtrer par chantier"),
    template_id: Optional[int] = Query(None, description="Filtrer par template"),
    user_id: Optional[int] = Query(None, description="Filtrer par utilisateur"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    date_debut: Optional[date] = Query(None, description="Date de debut"),
    date_fin: Optional[date] = Query(None, description="Date de fin"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    controller: FormulaireController = Depends(get_formulaire_controller),
):
    """Liste les formulaires avec filtres."""
    result = controller.list_formulaires(
        chantier_id=chantier_id,
        template_id=template_id,
        user_id=user_id,
        statut=statut,
        date_debut=date_debut,
        date_fin=date_fin,
        skip=skip,
        limit=limit,
    )
    return {
        "formulaires": result.formulaires,
        "total": result.total,
        "skip": result.skip,
        "limit": result.limit,
    }


@router.get("/chantier/{chantier_id}")
async def list_formulaires_by_chantier(
    chantier_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    controller: FormulaireController = Depends(get_formulaire_controller),
):
    """Liste les formulaires d'un chantier (FOR-10)."""
    return controller.list_formulaires_by_chantier(chantier_id, skip, limit)


@router.get("/{formulaire_id}")
async def get_formulaire(
    formulaire_id: int,
    controller: FormulaireController = Depends(get_formulaire_controller),
):
    """Recupere un formulaire par ID."""
    try:
        return controller.get_formulaire(formulaire_id)
    except Exception as e:
        if "non trouve" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{formulaire_id}/history")
async def get_formulaire_history(
    formulaire_id: int,
    controller: FormulaireController = Depends(get_formulaire_controller),
):
    """Recupere l'historique d'un formulaire (FOR-08)."""
    try:
        return controller.get_formulaire_history(formulaire_id)
    except Exception as e:
        if "non trouve" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{formulaire_id}")
async def update_formulaire(
    formulaire_id: int,
    request: UpdateFormulaireRequest,
    controller: FormulaireController = Depends(get_formulaire_controller),
):
    """Met a jour un formulaire."""
    try:
        result = controller.update_formulaire(
            formulaire_id=formulaire_id,
            champs=request.champs,
            latitude=request.latitude,
            longitude=request.longitude,
        )
        return result
    except Exception as e:
        if "non trouve" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "modifiable" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{formulaire_id}/photos")
async def add_photo(
    formulaire_id: int,
    request: AddPhotoRequest,
    controller: FormulaireController = Depends(get_formulaire_controller),
):
    """Ajoute une photo au formulaire (FOR-04)."""
    try:
        result = controller.add_photo(
            formulaire_id=formulaire_id,
            url=request.url,
            nom_fichier=request.nom_fichier,
            champ_nom=request.champ_nom,
            latitude=request.latitude,
            longitude=request.longitude,
        )
        return result
    except Exception as e:
        if "non trouve" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "modifiable" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{formulaire_id}/signature")
async def add_signature(
    formulaire_id: int,
    request: AddSignatureRequest,
    controller: FormulaireController = Depends(get_formulaire_controller),
):
    """Ajoute une signature au formulaire (FOR-05)."""
    try:
        result = controller.add_signature(
            formulaire_id=formulaire_id,
            signature_url=request.signature_url,
            signature_nom=request.signature_nom,
        )
        return result
    except Exception as e:
        if "non trouve" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "modifiable" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{formulaire_id}/submit")
async def submit_formulaire(
    formulaire_id: int,
    request: SubmitFormulaireRequest,
    controller: FormulaireController = Depends(get_formulaire_controller),
):
    """Soumet un formulaire avec horodatage (FOR-07)."""
    try:
        result = controller.submit_formulaire(
            formulaire_id=formulaire_id,
            signature_url=request.signature_url,
            signature_nom=request.signature_nom,
        )
        return result
    except Exception as e:
        if "non trouve" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "soumis" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{formulaire_id}/validate")
async def validate_formulaire(
    formulaire_id: int,
    controller: FormulaireController = Depends(get_formulaire_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Valide un formulaire soumis."""
    try:
        result = controller.validate_formulaire(
            formulaire_id=formulaire_id,
            valideur_id=current_user_id,
        )
        return result
    except Exception as e:
        if "non trouve" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{formulaire_id}/export")
async def export_pdf(
    formulaire_id: int,
    controller: FormulaireController = Depends(get_formulaire_controller),
):
    """Exporte un formulaire en PDF (FOR-09)."""
    try:
        return controller.export_pdf(formulaire_id)
    except Exception as e:
        if "non trouve" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
