"""Use Cases du module Signalements."""

from .signalement_use_cases import (
    CreateSignalementUseCase,
    GetSignalementUseCase,
    ListSignalementsUseCase,
    SearchSignalementsUseCase,
    UpdateSignalementUseCase,
    DeleteSignalementUseCase,
    AssignerSignalementUseCase,
    MarquerTraiteUseCase,
    CloturerSignalementUseCase,
    ReouvrirsignalementUseCase,
    GetStatistiquesUseCase,
    GetSignalementsEnRetardUseCase,
    SignalementNotFoundError,
    InvalidStatusTransitionError,
    AccessDeniedError,
)
from .reponse_use_cases import (
    CreateReponseUseCase,
    ListReponsesUseCase,
    UpdateReponseUseCase,
    DeleteReponseUseCase,
    ReponseNotFoundError,
)

__all__ = [
    # Signalement Use Cases
    "CreateSignalementUseCase",
    "GetSignalementUseCase",
    "ListSignalementsUseCase",
    "SearchSignalementsUseCase",
    "UpdateSignalementUseCase",
    "DeleteSignalementUseCase",
    "AssignerSignalementUseCase",
    "MarquerTraiteUseCase",
    "CloturerSignalementUseCase",
    "ReouvrirsignalementUseCase",
    "GetStatistiquesUseCase",
    "GetSignalementsEnRetardUseCase",
    # Reponse Use Cases
    "CreateReponseUseCase",
    "ListReponsesUseCase",
    "UpdateReponseUseCase",
    "DeleteReponseUseCase",
    # Errors
    "SignalementNotFoundError",
    "ReponseNotFoundError",
    "InvalidStatusTransitionError",
    "AccessDeniedError",
]
