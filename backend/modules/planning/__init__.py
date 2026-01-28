"""Module Planning Operationnel.

Ce module implemente le planning des affectations utilisateurs aux chantiers
selon CDC Section 5 - Planning Operationnel (PLN-01 a PLN-28).

Fonctionnalites principales:
- Visualisation planning hebdomadaire/mensuel (PLN-01 a PLN-03)
- Creation/modification/suppression d'affectations (PLN-04 a PLN-09)
- Filtrage et recherche (PLN-10 a PLN-12)
- Duplication d'affectations (PLN-13, PLN-14)
- Affectations recurrentes (PLN-15 a PLN-17)

Architecture Clean Architecture:
- Domain: Entites, Value Objects, Events, Repository interfaces
- Application: Use Cases, DTOs, Ports
- Adapters: Controllers, Schemas
- Infrastructure: Persistence, Web, Event Bus
"""

# Domain Layer
from .domain.entities import Affectation
from .domain.value_objects import HeureAffectation, TypeAffectation, JourSemaine
from .domain.repositories import AffectationRepository
from .domain.events import (
    AffectationCreatedEvent,
    AffectationUpdatedEvent,
    AffectationDeletedEvent,
    AffectationBulkCreatedEvent,
    AffectationBulkDeletedEvent,
)

# Application Layer
from .application.use_cases import (
    CreateAffectationUseCase,
    UpdateAffectationUseCase,
    DeleteAffectationUseCase,
    GetPlanningUseCase,
    DuplicateAffectationsUseCase,
    GetNonPlanifiesUseCase,
    AffectationConflictError,
    AffectationNotFoundError,
    InvalidDateRangeError,
    NoAffectationsToDuplicateError,
)
from .application.dtos import (
    CreateAffectationDTO,
    UpdateAffectationDTO,
    AffectationDTO,
    AffectationListDTO,
    PlanningFiltersDTO,
    DuplicateAffectationsDTO,
)

# Adapters Layer
from .adapters.controllers import (
    PlanningController,
    CreateAffectationRequest,
    UpdateAffectationRequest,
    AffectationResponse,
    PlanningFiltersRequest,
    DuplicateAffectationsRequest,
    DeleteResponse,
    NonPlanifiesResponse,
)

# Infrastructure Layer
from .infrastructure import (
    AffectationModel,
    Base,
    SQLAlchemyAffectationRepository,
    EventBusImpl,
    NoOpEventBus,
    router,
    get_planning_controller,
)

__all__ = [
    # Domain - Entities
    "Affectation",
    # Domain - Value Objects
    "HeureAffectation",
    "TypeAffectation",
    "JourSemaine",
    # Domain - Repository Interface
    "AffectationRepository",
    # Domain - Events
    "AffectationCreatedEvent",
    "AffectationUpdatedEvent",
    "AffectationDeletedEvent",
    "AffectationBulkCreatedEvent",
    "AffectationBulkDeletedEvent",
    # Application - Use Cases
    "CreateAffectationUseCase",
    "UpdateAffectationUseCase",
    "DeleteAffectationUseCase",
    "GetPlanningUseCase",
    "DuplicateAffectationsUseCase",
    "GetNonPlanifiesUseCase",
    # Application - Exceptions
    "AffectationConflictError",
    "AffectationNotFoundError",
    "InvalidDateRangeError",
    "NoAffectationsToDuplicateError",
    # Application - DTOs
    "CreateAffectationDTO",
    "UpdateAffectationDTO",
    "AffectationDTO",
    "AffectationListDTO",
    "PlanningFiltersDTO",
    "DuplicateAffectationsDTO",
    # Adapters - Controller
    "PlanningController",
    # Adapters - Schemas
    "CreateAffectationRequest",
    "UpdateAffectationRequest",
    "AffectationResponse",
    "PlanningFiltersRequest",
    "DuplicateAffectationsRequest",
    "DeleteResponse",
    "NonPlanifiesResponse",
    # Infrastructure - Persistence
    "AffectationModel",
    "Base",
    "SQLAlchemyAffectationRepository",
    # Infrastructure - Event Bus
    "EventBusImpl",
    "NoOpEventBus",
    # Infrastructure - Web
    "router",
    "get_planning_controller",
]
