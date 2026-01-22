"""Module Planning - Gestion des affectations.

Selon CDC Section 5 - Planning Opérationnel (PLN-01 à PLN-28).
"""

from .domain import (
    Affectation,
    CreneauHoraire,
    TypeRecurrence,
    AffectationRepository,
    AffectationCreatedEvent,
    AffectationUpdatedEvent,
    AffectationDeletedEvent,
)
from .application import (
    CreateAffectationUseCase,
    GetAffectationUseCase,
    ListAffectationsUseCase,
    UpdateAffectationUseCase,
    DeleteAffectationUseCase,
    DeplacerAffectationUseCase,
    DupliquerAffectationsUseCase,
    AffectationDTO,
    AffectationListDTO,
)
from .infrastructure import router

__all__ = [
    # Domain
    "Affectation",
    "CreneauHoraire",
    "TypeRecurrence",
    "AffectationRepository",
    "AffectationCreatedEvent",
    "AffectationUpdatedEvent",
    "AffectationDeletedEvent",
    # Application
    "CreateAffectationUseCase",
    "GetAffectationUseCase",
    "ListAffectationsUseCase",
    "UpdateAffectationUseCase",
    "DeleteAffectationUseCase",
    "DeplacerAffectationUseCase",
    "DupliquerAffectationsUseCase",
    "AffectationDTO",
    "AffectationListDTO",
    # Infrastructure
    "router",
]
