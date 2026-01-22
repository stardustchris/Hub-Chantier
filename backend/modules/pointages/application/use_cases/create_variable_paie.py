"""Use Case: Créer une variable de paie (FDH-13)."""

from typing import Optional
from decimal import Decimal

from ...domain.entities import VariablePaie
from ...domain.repositories import VariablePaieRepository, PointageRepository
from ...domain.value_objects import TypeVariablePaie
from ...domain.events import VariablePaieCreatedEvent
from ..dtos import CreateVariablePaieDTO, VariablePaieDTO
from ..ports import EventBus, NullEventBus


class CreateVariablePaieUseCase:
    """
    Crée une variable de paie.

    Implémente FDH-13: Variables de paie (Panier, transport, congés, primes, absences).
    """

    def __init__(
        self,
        variable_repo: VariablePaieRepository,
        pointage_repo: PointageRepository,
        event_bus: Optional[EventBus] = None,
    ):
        """
        Initialise le use case.

        Args:
            variable_repo: Repository des variables de paie.
            pointage_repo: Repository des pointages.
            event_bus: Bus d'événements (optionnel).
        """
        self.variable_repo = variable_repo
        self.pointage_repo = pointage_repo
        self.event_bus = event_bus or NullEventBus()

    def execute(self, dto: CreateVariablePaieDTO) -> VariablePaieDTO:
        """
        Crée une variable de paie.

        Args:
            dto: Les données de la variable.

        Returns:
            Le DTO de la variable créée.

        Raises:
            ValueError: Si le pointage n'existe pas ou si le type est invalide.
        """
        # Vérifie que le pointage existe
        pointage = self.pointage_repo.find_by_id(dto.pointage_id)
        if not pointage:
            raise ValueError(f"Pointage {dto.pointage_id} non trouvé")

        # Parse le type de variable
        type_variable = TypeVariablePaie.from_string(dto.type_variable)

        # Crée l'entité
        variable = VariablePaie(
            pointage_id=dto.pointage_id,
            type_variable=type_variable,
            valeur=Decimal(str(dto.valeur)),
            date_application=dto.date_application,
            commentaire=dto.commentaire,
        )

        # Persiste
        variable = self.variable_repo.save(variable)

        # Publie l'événement
        event = VariablePaieCreatedEvent(
            variable_id=variable.id,
            pointage_id=variable.pointage_id,
            type_variable=variable.type_variable.value,
            valeur=str(variable.valeur),
            date_application=variable.date_application,
        )
        self.event_bus.publish(event)

        return self._to_dto(variable)

    def _to_dto(self, variable: VariablePaie) -> VariablePaieDTO:
        """Convertit l'entité en DTO."""
        return VariablePaieDTO(
            id=variable.id,
            pointage_id=variable.pointage_id,
            type_variable=variable.type_variable.value,
            type_variable_libelle=variable.type_variable.libelle,
            valeur=str(variable.valeur),
            date_application=variable.date_application,
            commentaire=variable.commentaire,
            created_at=variable.created_at,
        )
