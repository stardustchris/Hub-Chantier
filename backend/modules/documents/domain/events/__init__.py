"""Events du module Documents."""

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
]
