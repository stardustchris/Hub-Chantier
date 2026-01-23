"""Routes FastAPI pour le module Documents."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from datetime import datetime

from .dependencies import get_document_controller, get_current_user
from ...adapters.controllers import DocumentController
from ...application.dtos import (
    DossierCreateDTO,
    DossierUpdateDTO,
    DocumentUpdateDTO,
    DocumentSearchDTO,
    AutorisationCreateDTO,
)
from ...application.use_cases import (
    DossierNotFoundError,
    DossierNotEmptyError,
    DuplicateDossierNameError,
    DocumentNotFoundError,
    FileTooLargeError,
    InvalidFileTypeError,
    AutorisationAlreadyExistsError,
    AutorisationNotFoundError,
)


router = APIRouter(prefix="/documents", tags=["Documents"])


# Pydantic models for request/response
class DossierCreateRequest(BaseModel):
    """Request pour créer un dossier."""

    chantier_id: int
    nom: str
    type_dossier: str = "custom"
    niveau_acces: str = "compagnon"
    parent_id: Optional[int] = None


class DossierUpdateRequest(BaseModel):
    """Request pour mettre à jour un dossier."""

    nom: Optional[str] = None
    niveau_acces: Optional[str] = None
    parent_id: Optional[int] = None


class DocumentUpdateRequest(BaseModel):
    """Request pour mettre à jour un document."""

    nom: Optional[str] = None
    description: Optional[str] = None
    dossier_id: Optional[int] = None
    niveau_acces: Optional[str] = None


class DownloadZipRequest(BaseModel):
    """Request pour téléchargement groupé ZIP (GED-16)."""

    document_ids: List[int]

    @classmethod
    def validate_max_documents(cls, v: List[int]) -> List[int]:
        """Valide la liste des IDs de documents (max 100)."""
        if len(v) > 100:
            raise ValueError("Maximum 100 documents par archive")
        if len(v) == 0:
            raise ValueError("Au moins un document requis")
        return v


class PreviewResponse(BaseModel):
    """Response pour la prévisualisation (GED-17)."""

    id: int
    nom: str
    type_document: str
    mime_type: str
    taille: int
    can_preview: bool
    preview_url: Optional[str] = None

    class Config:
        from_attributes = True


class AutorisationCreateRequest(BaseModel):
    """Request pour créer une autorisation."""

    user_id: int
    type_autorisation: str
    dossier_id: Optional[int] = None
    document_id: Optional[int] = None
    expire_at: Optional[datetime] = None


class DossierResponse(BaseModel):
    """Response pour un dossier."""

    id: int
    chantier_id: int
    nom: str
    type_dossier: str
    niveau_acces: str
    parent_id: Optional[int]
    ordre: int
    chemin_complet: str
    nombre_documents: int
    nombre_sous_dossiers: int
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """Response pour un document."""

    id: int
    chantier_id: int
    dossier_id: int
    nom: str
    nom_original: str
    type_document: str
    taille: int
    taille_formatee: str
    mime_type: str
    uploaded_by: int
    uploaded_by_nom: Optional[str]
    uploaded_at: datetime
    description: Optional[str]
    version: int
    icone: str
    extension: str
    niveau_acces: Optional[str]

    class Config:
        from_attributes = True


class AutorisationResponse(BaseModel):
    """Response pour une autorisation."""

    id: int
    user_id: int
    user_nom: Optional[str]
    type_autorisation: str
    dossier_id: Optional[int]
    document_id: Optional[int]
    cible_nom: Optional[str]
    accorde_par: int
    accorde_par_nom: Optional[str]
    created_at: datetime
    expire_at: Optional[datetime]
    est_valide: bool

    class Config:
        from_attributes = True


# ============ DOSSIERS ============

@router.post("/dossiers", response_model=DossierResponse, status_code=status.HTTP_201_CREATED)
def create_dossier(
    request: DossierCreateRequest,
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Crée un nouveau dossier."""
    try:
        dto = DossierCreateDTO(
            chantier_id=request.chantier_id,
            nom=request.nom,
            type_dossier=request.type_dossier,
            niveau_acces=request.niveau_acces,
            parent_id=request.parent_id,
        )
        result = controller.create_dossier(dto)
        return result
    except DuplicateDossierNameError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dossiers/{dossier_id}", response_model=DossierResponse)
def get_dossier(
    dossier_id: int,
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Récupère un dossier par son ID."""
    try:
        return controller.get_dossier(dossier_id)
    except DossierNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/chantiers/{chantier_id}/dossiers", response_model=List[DossierResponse])
def list_dossiers(
    chantier_id: int,
    parent_id: Optional[int] = Query(None),
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Liste les dossiers d'un chantier."""
    return controller.list_dossiers(chantier_id, parent_id)


@router.get("/chantiers/{chantier_id}/arborescence")
def get_arborescence(
    chantier_id: int,
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Récupère l'arborescence complète d'un chantier (GED-02)."""
    return controller.get_arborescence(chantier_id)


@router.put("/dossiers/{dossier_id}", response_model=DossierResponse)
def update_dossier(
    dossier_id: int,
    request: DossierUpdateRequest,
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Met à jour un dossier."""
    try:
        dto = DossierUpdateDTO(
            nom=request.nom,
            niveau_acces=request.niveau_acces,
            parent_id=request.parent_id,
        )
        return controller.update_dossier(dossier_id, dto)
    except DossierNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DuplicateDossierNameError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/dossiers/{dossier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dossier(
    dossier_id: int,
    force: bool = Query(False),
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Supprime un dossier."""
    try:
        controller.delete_dossier(dossier_id, force)
    except DossierNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DossierNotEmptyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/chantiers/{chantier_id}/init-arborescence", response_model=List[DossierResponse])
def init_arborescence(
    chantier_id: int,
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Initialise l'arborescence type d'un chantier (GED-02)."""
    return controller.init_arborescence(chantier_id)


# ============ DOCUMENTS ============

@router.post("/dossiers/{dossier_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    dossier_id: int,
    chantier_id: int = Query(...),
    file: UploadFile = File(...),
    description: Optional[str] = Query(None),
    niveau_acces: Optional[str] = Query(None),
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Upload un document (GED-06, GED-07, GED-08)."""
    try:
        # Lire le contenu du fichier
        content = await file.read()
        taille = len(content)

        # Reset du curseur pour le stockage
        await file.seek(0)

        result = controller.upload_document(
            file_content=file.file,
            filename=file.filename or "document",
            chantier_id=chantier_id,
            dossier_id=dossier_id,
            uploaded_by=current_user["id"],
            taille=taille,
            mime_type=file.content_type or "application/octet-stream",
            description=description,
            niveau_acces=niveau_acces,
        )
        return result
    except FileTooLargeError as e:
        raise HTTPException(status_code=413, detail=str(e))
    except InvalidFileTypeError as e:
        raise HTTPException(status_code=415, detail=str(e))
    except DossierNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Récupère un document par son ID."""
    try:
        return controller.get_document(document_id)
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/dossiers/{dossier_id}/documents")
def list_documents(
    dossier_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Liste les documents d'un dossier (GED-03)."""
    return controller.list_documents(dossier_id, skip, limit)


@router.get("/chantiers/{chantier_id}/documents/search")
def search_documents(
    chantier_id: int,
    query: Optional[str] = Query(None),
    type_document: Optional[str] = Query(None),
    dossier_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Recherche des documents."""
    search_dto = DocumentSearchDTO(
        chantier_id=chantier_id,
        query=query,
        type_document=type_document,
        dossier_id=dossier_id,
        skip=skip,
        limit=limit,
    )
    return controller.search_documents(search_dto)


@router.put("/documents/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    request: DocumentUpdateRequest,
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Met à jour un document (GED-13)."""
    try:
        dto = DocumentUpdateDTO(
            nom=request.nom,
            description=request.description,
            dossier_id=request.dossier_id,
            niveau_acces=request.niveau_acces,
        )
        return controller.update_document(document_id, dto)
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DossierNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Supprime un document (GED-13)."""
    try:
        controller.delete_document(document_id)
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/documents/{document_id}/download")
def download_document(
    document_id: int,
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Télécharge un document."""
    try:
        url, filename, mime_type = controller.download_document(document_id)
        return {"url": url, "filename": filename, "mime_type": mime_type}
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/documents/download-zip")
def download_documents_zip(
    request: DownloadZipRequest,
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Télécharge plusieurs documents en archive ZIP (GED-16)."""
    try:
        zip_content = controller.download_documents_zip(request.document_ids)
        return StreamingResponse(
            zip_content,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=documents.zip"},
        )
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/documents/{document_id}/preview", response_model=PreviewResponse)
def get_document_preview(
    document_id: int,
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Obtient les informations de prévisualisation d'un document (GED-17)."""
    try:
        return controller.get_document_preview(document_id)
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/documents/{document_id}/preview/content")
def get_document_preview_content(
    document_id: int,
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Récupère le contenu d'un document pour prévisualisation (GED-17)."""
    try:
        content, mime_type = controller.get_document_preview_content(document_id)
        return StreamingResponse(
            iter([content]),
            media_type=mime_type,
            headers={"Content-Disposition": "inline"},
        )
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileTooLargeError as e:
        raise HTTPException(status_code=413, detail=str(e))


# ============ AUTORISATIONS ============

@router.post("/autorisations", response_model=AutorisationResponse, status_code=status.HTTP_201_CREATED)
def create_autorisation(
    request: AutorisationCreateRequest,
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Crée une autorisation nominative (GED-05, GED-10)."""
    try:
        dto = AutorisationCreateDTO(
            user_id=request.user_id,
            type_autorisation=request.type_autorisation,
            accorde_par=current_user["id"],
            dossier_id=request.dossier_id,
            document_id=request.document_id,
            expire_at=request.expire_at,
        )
        return controller.create_autorisation(dto)
    except AutorisationAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dossiers/{dossier_id}/autorisations")
def list_autorisations_dossier(
    dossier_id: int,
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Liste les autorisations d'un dossier."""
    return controller.list_autorisations_by_dossier(dossier_id)


@router.get("/documents/{document_id}/autorisations")
def list_autorisations_document(
    document_id: int,
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Liste les autorisations d'un document."""
    return controller.list_autorisations_by_document(document_id)


@router.delete("/autorisations/{autorisation_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_autorisation(
    autorisation_id: int,
    controller: DocumentController = Depends(get_document_controller),
    current_user: dict = Depends(get_current_user),
):
    """Révoque une autorisation."""
    try:
        controller.revoke_autorisation(autorisation_id)
    except AutorisationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
