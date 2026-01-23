"""Dépendances FastAPI pour le module Documents."""

from fastapi import Depends
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from modules.auth.infrastructure.web.dependencies import get_current_user_id

from ...adapters.controllers import DocumentController
from ...adapters.providers import LocalFileStorageService
from ...application.use_cases import (
    UploadDocumentUseCase,
    GetDocumentUseCase,
    ListDocumentsUseCase,
    SearchDocumentsUseCase,
    UpdateDocumentUseCase,
    DeleteDocumentUseCase,
    DownloadDocumentUseCase,
    DownloadMultipleDocumentsUseCase,
    GetDocumentPreviewUseCase,
    GetDocumentPreviewContentUseCase,
    CreateDossierUseCase,
    GetDossierUseCase,
    ListDossiersUseCase,
    GetArborescenceUseCase,
    UpdateDossierUseCase,
    DeleteDossierUseCase,
    InitArborescenceUseCase,
    CreateAutorisationUseCase,
    ListAutorisationsUseCase,
    RevokeAutorisationUseCase,
    CheckAccessUseCase,
)
from ..persistence import (
    SQLAlchemyDossierRepository,
    SQLAlchemyDocumentRepository,
    SQLAlchemyAutorisationRepository,
)


def get_file_storage() -> LocalFileStorageService:
    """Retourne le service de stockage de fichiers."""
    return LocalFileStorageService(base_path="uploads")


def get_document_controller(
    db: Session = Depends(get_db),
    file_storage: LocalFileStorageService = Depends(get_file_storage),
) -> DocumentController:
    """
    Factory pour créer le DocumentController avec ses dépendances.

    Args:
        db: Session SQLAlchemy.
        file_storage: Service de stockage de fichiers.

    Returns:
        Instance de DocumentController.
    """
    # Repositories
    dossier_repo = SQLAlchemyDossierRepository(db)
    document_repo = SQLAlchemyDocumentRepository(db)
    autorisation_repo = SQLAlchemyAutorisationRepository(db)

    # Use Cases - Documents
    upload_document = UploadDocumentUseCase(document_repo, dossier_repo, file_storage)
    get_document = GetDocumentUseCase(document_repo)
    list_documents = ListDocumentsUseCase(document_repo)
    search_documents = SearchDocumentsUseCase(document_repo)
    update_document = UpdateDocumentUseCase(document_repo, dossier_repo)
    delete_document = DeleteDocumentUseCase(document_repo, file_storage, autorisation_repo)
    download_document = DownloadDocumentUseCase(document_repo, file_storage)
    download_multiple_documents = DownloadMultipleDocumentsUseCase(document_repo, file_storage)
    get_document_preview = GetDocumentPreviewUseCase(document_repo, file_storage)
    get_document_preview_content = GetDocumentPreviewContentUseCase(document_repo, file_storage)

    # Use Cases - Dossiers
    create_dossier = CreateDossierUseCase(dossier_repo, document_repo)
    get_dossier = GetDossierUseCase(dossier_repo, document_repo)
    list_dossiers = ListDossiersUseCase(dossier_repo, document_repo)
    get_arborescence = GetArborescenceUseCase(dossier_repo, document_repo)
    update_dossier = UpdateDossierUseCase(dossier_repo, document_repo)
    delete_dossier = DeleteDossierUseCase(dossier_repo)
    init_arborescence = InitArborescenceUseCase(dossier_repo)

    # Use Cases - Autorisations
    create_autorisation = CreateAutorisationUseCase(
        autorisation_repo, dossier_repo, document_repo
    )
    list_autorisations = ListAutorisationsUseCase(autorisation_repo)
    revoke_autorisation = RevokeAutorisationUseCase(autorisation_repo)
    check_access = CheckAccessUseCase(autorisation_repo, dossier_repo, document_repo)

    return DocumentController(
        upload_document=upload_document,
        get_document=get_document,
        list_documents=list_documents,
        search_documents=search_documents,
        update_document=update_document,
        delete_document=delete_document,
        download_document=download_document,
        download_multiple_documents=download_multiple_documents,
        get_document_preview=get_document_preview,
        get_document_preview_content=get_document_preview_content,
        create_dossier=create_dossier,
        get_dossier=get_dossier,
        list_dossiers=list_dossiers,
        get_arborescence=get_arborescence,
        update_dossier=update_dossier,
        delete_dossier=delete_dossier,
        init_arborescence=init_arborescence,
        create_autorisation=create_autorisation,
        list_autorisations=list_autorisations,
        revoke_autorisation=revoke_autorisation,
        check_access=check_access,
    )


# Re-export get_current_user_id
__all__ = ["get_document_controller", "get_current_user_id", "get_file_storage"]
