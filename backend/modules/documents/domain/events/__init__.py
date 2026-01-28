"""Événements de domaine pour le module documents."""

from .document_events import (
    DocumentEvent,
    DocumentUploaded,
    DocumentDeleted,
    DocumentMoved,
    DocumentRenamed,
    DossierEvent,
    DossierCreated,
    DossierDeleted,
    AutorisationEvent,
    AutorisationAccordee,
    AutorisationRevoquee,
)
from .document_uploaded import DocumentUploadedEvent
from .document_deleted import DocumentDeletedEvent

__all__ = [
    "DocumentEvent",
    "DocumentUploaded",
    "DocumentDeleted",
    "DocumentMoved",
    "DocumentRenamed",
    "DossierEvent",
    "DossierCreated",
    "DossierDeleted",
    "AutorisationEvent",
    "AutorisationAccordee",
    "AutorisationRevoquee",
    "DocumentUploadedEvent",
    "DocumentDeletedEvent",
]
