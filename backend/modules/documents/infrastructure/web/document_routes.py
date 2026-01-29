"""Routes FastAPI pour le module Documents."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from shared.infrastructure.audit import AuditService
from .dependencies import get_document_controller, get_current_user_id
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
from ...domain.events.document_uploaded import DocumentUploadedEvent
from shared.infrastructure.event_bus.dependencies import get_event_bus
from shared.infrastructure.event_bus import EventBus


router = APIRouter(prefix="/documents", tags=["Documents"])


def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    """Factory pour le service d'audit."""
    return AuditService(db)


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
    """Response pour un document de la GED (Gestion Electronique de Documents)."""

    id: int = Field(..., description="Identifiant unique du document", example=127)
    chantier_id: int = Field(..., description="ID du chantier auquel appartient le document", example=42)
    dossier_id: int = Field(..., description="ID du dossier parent contenant le document", example=15)
    nom: str = Field(
        ...,
        description="Nom du fichier sur le serveur (unique)",
        example="plan-etage1_v2_20260128.pdf"
    )
    nom_original: str = Field(
        ...,
        description="Nom original du fichier uploadé par l'utilisateur",
        example="Plan étage 1 - Version finale.pdf"
    )
    type_document: str = Field(
        ...,
        description="Type de document (plan, facture, photo, etc.)",
        example="plan"
    )
    taille: int = Field(
        ...,
        description="Taille du fichier en octets",
        ge=0,
        example=2547891
    )
    taille_formatee: str = Field(
        ...,
        description="Taille du fichier formatée pour l'affichage (ex: 2.4 MB)",
        example="2.4 MB"
    )
    mime_type: str = Field(
        ...,
        description="Type MIME du fichier",
        example="application/pdf"
    )
    uploaded_by: int = Field(..., description="ID de l'utilisateur ayant uploadé le document", example=5)
    uploaded_by_nom: Optional[str] = Field(
        None,
        description="Nom complet de l'utilisateur ayant uploadé (enrichissement UI)",
        example="Sophie Martin"
    )
    uploaded_at: datetime = Field(
        ...,
        description="Date et heure d'upload du document (format ISO 8601)",
        example="2026-01-28T14:35:22Z"
    )
    description: Optional[str] = Field(
        None,
        description="Description ou commentaire sur le document",
        max_length=1000,
        example="Plan d'étage validé par l'architecte le 28/01/2026"
    )
    version: int = Field(
        ...,
        description="Numéro de version du document (auto-incrémenté)",
        ge=1,
        example=2
    )
    icone: str = Field(
        ...,
        description="Icône pour l'affichage UI (nom d'icône ou emoji)",
        example="📄"
    )
    extension: str = Field(
        ...,
        description="Extension du fichier (sans le point)",
        example="pdf"
    )
    niveau_acces: Optional[str] = Field(
        None,
        description="Niveau d'accès requis (public, conducteur, admin)",
        pattern="^(public|conducteur|admin)$",
        example="conducteur"
    )

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 127,
                "chantier_id": 42,
                "dossier_id": 15,
                "nom": "plan-etage1_v2_20260128.pdf",
                "nom_original": "Plan étage 1 - Version finale.pdf",
                "type_document": "plan",
                "taille": 2547891,
                "taille_formatee": "2.4 MB",
                "mime_type": "application/pdf",
                "uploaded_by": 5,
                "uploaded_by_nom": "Sophie Martin",
                "uploaded_at": "2026-01-28T14:35:22Z",
                "description": "Plan d'étage validé par l'architecte le 28/01/2026",
                "version": 2,
                "icone": "📄",
                "extension": "pdf",
                "niveau_acces": "conducteur"
            }
        }


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
    current_user_id: int = Depends(get_current_user_id),
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
    current_user_id: int = Depends(get_current_user_id),
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
    current_user_id: int = Depends(get_current_user_id),
):
    """Liste les dossiers d'un chantier."""
    return controller.list_dossiers(chantier_id, parent_id)


@router.get("/chantiers/{chantier_id}/arborescence")
def get_arborescence(
    chantier_id: int,
    controller: DocumentController = Depends(get_document_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Récupère l'arborescence complète d'un chantier (GED-02)."""
    return controller.get_arborescence(chantier_id)


@router.put("/dossiers/{dossier_id}", response_model=DossierResponse)
def update_dossier(
    dossier_id: int,
    request: DossierUpdateRequest,
    controller: DocumentController = Depends(get_document_controller),
    current_user_id: int = Depends(get_current_user_id),
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
    current_user_id: int = Depends(get_current_user_id),
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
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Initialise l'arborescence type d'un chantier (GED-02)."""
    result = controller.init_arborescence(chantier_id)
    db.commit()
    return result


# ============ DOCUMENTS ============

@router.post("/dossiers/{dossier_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    dossier_id: int,
    http_request: Request,
    chantier_id: int = Query(...),
    file: UploadFile = File(...),
    description: Optional[str] = Query(None),
    niveau_acces: Optional[str] = Query(None),
    event_bus: EventBus = Depends(get_event_bus),
    controller: DocumentController = Depends(get_document_controller),
    current_user_id: int = Depends(get_current_user_id),
    audit: AuditService = Depends(get_audit_service),
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
            uploaded_by=current_user_id,
            taille=taille,
            mime_type=file.content_type or "application/octet-stream",
            description=description,
            niveau_acces=niveau_acces,
        )

        # Audit Trail
        audit.log_action(
            entity_type="document",
            entity_id=result.id,
            action="uploaded",
            user_id=current_user_id,
            new_values={
                "nom": result.nom,
                "chantier_id": chantier_id,
                "dossier_id": dossier_id,
                "taille": taille,
                "type_document": result.type_document,
            },
            ip_address=http_request.client.host if http_request.client else None,
        )

        # Publish event after database commit
        await event_bus.publish(DocumentUploadedEvent(
            document_id=result.id,
            nom=result.nom,
            type_document=result.type_document,
            chantier_id=chantier_id,
            user_id=current_user_id,
        ))

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
    current_user_id: int = Depends(get_current_user_id),
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
    current_user_id: int = Depends(get_current_user_id),
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
    current_user_id: int = Depends(get_current_user_id),
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
    http_request: Request,
    request: DocumentUpdateRequest,
    controller: DocumentController = Depends(get_document_controller),
    current_user_id: int = Depends(get_current_user_id),
    audit: AuditService = Depends(get_audit_service),
):
    """Met à jour un document (GED-13)."""
    try:
        # Récupérer les anciennes valeurs pour audit
        old_doc = controller.get_document(document_id)
        old_values = {
            "nom": old_doc.get("nom"),
            "description": old_doc.get("description"),
            "dossier_id": old_doc.get("dossier_id"),
            "niveau_acces": old_doc.get("niveau_acces"),
        }

        dto = DocumentUpdateDTO(
            nom=request.nom,
            description=request.description,
            dossier_id=request.dossier_id,
            niveau_acces=request.niveau_acces,
        )
        result = controller.update_document(document_id, dto)

        # Audit Trail
        new_values = {
            "nom": result.get("nom"),
            "description": result.get("description"),
            "dossier_id": result.get("dossier_id"),
            "niveau_acces": result.get("niveau_acces"),
        }

        audit.log_action(
            entity_type="document",
            entity_id=document_id,
            action="updated",
            user_id=current_user_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=http_request.client.host if http_request.client else None,
        )

        return result
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DossierNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    http_request: Request,
    controller: DocumentController = Depends(get_document_controller),
    current_user_id: int = Depends(get_current_user_id),
    audit: AuditService = Depends(get_audit_service),
):
    """Supprime un document (GED-13)."""
    try:
        # Récupérer les valeurs pour audit avant suppression
        old_doc = controller.get_document(document_id)
        old_values = {
            "nom": old_doc.get("nom"),
            "chantier_id": old_doc.get("chantier_id"),
            "dossier_id": old_doc.get("dossier_id"),
            "type_document": old_doc.get("type_document"),
            "taille": old_doc.get("taille"),
        }

        controller.delete_document(document_id)

        # Audit Trail
        audit.log_action(
            entity_type="document",
            entity_id=document_id,
            action="deleted",
            user_id=current_user_id,
            old_values=old_values,
            ip_address=http_request.client.host if http_request.client else None,
        )
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/documents/{document_id}/download")
def download_document(
    document_id: int,
    controller: DocumentController = Depends(get_document_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Télécharge un document."""
    try:
        # Récupérer le chemin du fichier
        from modules.documents.infrastructure.persistence.document_repository import SQLAlchemyDocumentRepository
        from modules.documents.adapters.providers.local_file_storage import LocalFileStorageService
        from shared.infrastructure.database import get_db

        db = next(get_db())
        repo = SQLAlchemyDocumentRepository(db)
        document_entity = repo.find_by_id(document_id)

        if not document_entity:
            raise HTTPException(status_code=404, detail="Document non trouvé")

        # Ouvrir le fichier depuis le stockage
        storage = LocalFileStorageService()
        file_content = storage.get(document_entity.chemin_stockage)

        if not file_content:
            raise HTTPException(status_code=404, detail="Fichier non trouvé sur le disque")

        # Retourner le fichier en streaming
        return StreamingResponse(
            file_content,
            media_type=document_entity.mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{document_entity.nom}"'
            }
        )
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/documents/download-zip")
def download_documents_zip(
    request: DownloadZipRequest,
    controller: DocumentController = Depends(get_document_controller),
    current_user_id: int = Depends(get_current_user_id),
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
    current_user_id: int = Depends(get_current_user_id),
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
    current_user_id: int = Depends(get_current_user_id),
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
    http_request: Request,
    request: AutorisationCreateRequest,
    controller: DocumentController = Depends(get_document_controller),
    current_user_id: int = Depends(get_current_user_id),
    audit: AuditService = Depends(get_audit_service),
):
    """Crée une autorisation nominative (GED-05, GED-10)."""
    try:
        dto = AutorisationCreateDTO(
            user_id=request.user_id,
            type_autorisation=request.type_autorisation,
            accorde_par=current_user_id,
            dossier_id=request.dossier_id,
            document_id=request.document_id,
            expire_at=request.expire_at,
        )
        result = controller.create_autorisation(dto)

        # Audit Trail
        entity_type = "autorisation_document" if request.document_id else "autorisation_dossier"
        target_id = request.document_id or request.dossier_id

        audit.log_action(
            entity_type=entity_type,
            entity_id=result.get("id"),
            action="permissions_changed",
            user_id=current_user_id,
            new_values={
                "user_id": request.user_id,
                "type_autorisation": request.type_autorisation,
                "target_type": "document" if request.document_id else "dossier",
                "target_id": target_id,
            },
            ip_address=http_request.client.host if http_request.client else None,
        )

        return result
    except AutorisationAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dossiers/{dossier_id}/autorisations")
def list_autorisations_dossier(
    dossier_id: int,
    controller: DocumentController = Depends(get_document_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Liste les autorisations d'un dossier."""
    return controller.list_autorisations_by_dossier(dossier_id)


@router.get("/documents/{document_id}/autorisations")
def list_autorisations_document(
    document_id: int,
    controller: DocumentController = Depends(get_document_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """Liste les autorisations d'un document."""
    return controller.list_autorisations_by_document(document_id)


@router.delete("/autorisations/{autorisation_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_autorisation(
    autorisation_id: int,
    http_request: Request,
    controller: DocumentController = Depends(get_document_controller),
    current_user_id: int = Depends(get_current_user_id),
    audit: AuditService = Depends(get_audit_service),
):
    """Révoque une autorisation."""
    try:
        # Note: Nous ne pouvons pas récupérer les anciennes valeurs car le controller
        # ne fournit pas de méthode get_autorisation. L'audit sera simplifié.
        controller.revoke_autorisation(autorisation_id)

        # Audit Trail
        audit.log_action(
            entity_type="autorisation",
            entity_id=autorisation_id,
            action="permissions_revoked",
            user_id=current_user_id,
            ip_address=http_request.client.host if http_request.client else None,
        )
    except AutorisationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
