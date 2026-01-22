"""DTOs du module planning."""

from .create_affectation_dto import CreateAffectationDTO
from .update_affectation_dto import UpdateAffectationDTO
from .affectation_dto import AffectationDTO, AffectationListDTO
from .planning_filters_dto import PlanningFiltersDTO
from .duplicate_affectations_dto import DuplicateAffectationsDTO

__all__ = [
    "CreateAffectationDTO",
    "UpdateAffectationDTO",
    "AffectationDTO",
    "AffectationListDTO",
    "PlanningFiltersDTO",
    "DuplicateAffectationsDTO",
]
