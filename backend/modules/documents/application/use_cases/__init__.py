"""Use Cases du module Documents."""

from .dossier_use_cases import (
    CreateDossierUseCase,
    GetDossierUseCase,
    ListDossiersUseCase,
    GetArborescenceUseCase,
    UpdateDossierUseCase,
    DeleteDossierUseCase,
    InitArborescenceUseCase,
    DossierNotFoundError,
    DossierNotEmptyError,
    DuplicateDossierNameError,
)
from .document_use_cases import (
    UploadDocumentUseCase,
    GetDocumentUseCase,
    ListDocumentsUseCase,
    SearchDocumentsUseCase,
    UpdateDocumentUseCase,
    DeleteDocumentUseCase,
    DownloadDocumentUseCase,
    DocumentNotFoundError,
    FileTooLargeError,
    InvalidFileTypeError,
    DuplicateDocumentNameError,
    AccessDeniedError,
)
from .autorisation_use_cases import (
    CreateAutorisationUseCase,
    ListAutorisationsUseCase,
    RevokeAutorisationUseCase,
    CheckAccessUseCase,
    AutorisationAlreadyExistsError,
    AutorisationNotFoundError,
    InvalidTargetError,
)

__all__ = [
    # Dossier Use Cases
    "CreateDossierUseCase",
    "GetDossierUseCase",
    "ListDossiersUseCase",
    "GetArborescenceUseCase",
    "UpdateDossierUseCase",
    "DeleteDossierUseCase",
    "InitArborescenceUseCase",
    # Document Use Cases
    "UploadDocumentUseCase",
    "GetDocumentUseCase",
    "ListDocumentsUseCase",
    "SearchDocumentsUseCase",
    "UpdateDocumentUseCase",
    "DeleteDocumentUseCase",
    "DownloadDocumentUseCase",
    # Autorisation Use Cases
    "CreateAutorisationUseCase",
    "ListAutorisationsUseCase",
    "RevokeAutorisationUseCase",
    "CheckAccessUseCase",
    # Exceptions
    "DossierNotFoundError",
    "DossierNotEmptyError",
    "DuplicateDossierNameError",
    "DocumentNotFoundError",
    "FileTooLargeError",
    "InvalidFileTypeError",
    "DuplicateDocumentNameError",
    "AccessDeniedError",
    "AutorisationAlreadyExistsError",
    "AutorisationNotFoundError",
    "InvalidTargetError",
]
