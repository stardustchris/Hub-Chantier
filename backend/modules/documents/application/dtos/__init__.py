"""DTOs du module Documents."""

from .document_dtos import (
    DocumentDTO,
    DocumentCreateDTO,
    DocumentUpdateDTO,
    DocumentListDTO,
    DocumentSearchDTO,
)
from .dossier_dtos import (
    DossierDTO,
    DossierCreateDTO,
    DossierUpdateDTO,
    DossierTreeDTO,
    ArborescenceDTO,
)
from .autorisation_dtos import (
    AutorisationDTO,
    AutorisationCreateDTO,
    AutorisationListDTO,
)

__all__ = [
    # Document DTOs
    "DocumentDTO",
    "DocumentCreateDTO",
    "DocumentUpdateDTO",
    "DocumentListDTO",
    "DocumentSearchDTO",
    # Dossier DTOs
    "DossierDTO",
    "DossierCreateDTO",
    "DossierUpdateDTO",
    "DossierTreeDTO",
    "ArborescenceDTO",
    # Autorisation DTOs
    "AutorisationDTO",
    "AutorisationCreateDTO",
    "AutorisationListDTO",
]
