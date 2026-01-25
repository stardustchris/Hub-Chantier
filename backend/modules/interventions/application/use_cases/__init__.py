"""Use Cases du module Interventions."""

from .intervention_use_cases import (
    CreateInterventionUseCase,
    GetInterventionUseCase,
    ListInterventionsUseCase,
    UpdateInterventionUseCase,
    PlanifierInterventionUseCase,
    DemarrerInterventionUseCase,
    TerminerInterventionUseCase,
    AnnulerInterventionUseCase,
    DeleteInterventionUseCase,
)
from .technicien_use_cases import (
    AffecterTechnicienUseCase,
    DesaffecterTechnicienUseCase,
    ListTechniciensInterventionUseCase,
)
from .message_use_cases import (
    AddMessageUseCase,
    ListMessagesUseCase,
    ToggleRapportInclusionUseCase,
)
from .signature_use_cases import (
    AddSignatureUseCase,
    ListSignaturesUseCase,
)

__all__ = [
    # Intervention
    "CreateInterventionUseCase",
    "GetInterventionUseCase",
    "ListInterventionsUseCase",
    "UpdateInterventionUseCase",
    "PlanifierInterventionUseCase",
    "DemarrerInterventionUseCase",
    "TerminerInterventionUseCase",
    "AnnulerInterventionUseCase",
    "DeleteInterventionUseCase",
    # Techniciens
    "AffecterTechnicienUseCase",
    "DesaffecterTechnicienUseCase",
    "ListTechniciensInterventionUseCase",
    # Messages
    "AddMessageUseCase",
    "ListMessagesUseCase",
    "ToggleRapportInclusionUseCase",
    # Signatures
    "AddSignatureUseCase",
    "ListSignaturesUseCase",
]
