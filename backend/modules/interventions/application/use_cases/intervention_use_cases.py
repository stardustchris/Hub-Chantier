"""Use Cases pour les operations sur les Interventions."""

from typing import Optional, List

from ...domain.entities import Intervention
from ...domain.repositories import InterventionRepository, AffectationInterventionRepository
from ...domain.value_objects import StatutIntervention
from ..dtos import (
    CreateInterventionDTO,
    UpdateInterventionDTO,
    PlanifierInterventionDTO,
    DemarrerInterventionDTO,
    TerminerInterventionDTO,
    InterventionFiltersDTO,
)


class CreateInterventionUseCase:
    """Use case pour creer une intervention.

    INT-03: Creation intervention
    """

    def __init__(self, repository: InterventionRepository):
        self._repository = repository

    async def execute(
        self, dto: CreateInterventionDTO, created_by: int
    ) -> Intervention:
        """Cree une nouvelle intervention."""
        intervention = Intervention(
            type_intervention=dto.type_intervention,
            priorite=dto.priorite,
            client_nom=dto.client_nom,
            client_adresse=dto.client_adresse,
            client_telephone=dto.client_telephone,
            client_email=dto.client_email,
            description=dto.description,
            date_souhaitee=dto.date_souhaitee,
            chantier_origine_id=dto.chantier_origine_id,
            created_by=created_by,
        )

        return await self._repository.save(intervention)


class GetInterventionUseCase:
    """Use case pour recuperer une intervention."""

    def __init__(self, repository: InterventionRepository):
        self._repository = repository

    async def execute(self, intervention_id: int) -> Optional[Intervention]:
        """Recupere une intervention par son ID."""
        return await self._repository.get_by_id(intervention_id)

    async def by_code(self, code: str) -> Optional[Intervention]:
        """Recupere une intervention par son code."""
        return await self._repository.get_by_code(code)


class ListInterventionsUseCase:
    """Use case pour lister les interventions.

    INT-02: Liste des interventions
    """

    def __init__(self, repository: InterventionRepository):
        self._repository = repository

    async def execute(
        self, filters: InterventionFiltersDTO
    ) -> tuple[List[Intervention], int]:
        """Liste les interventions avec filtres et pagination."""
        interventions = await self._repository.list_all(
            statut=filters.statut,
            priorite=filters.priorite,
            type_intervention=filters.type_intervention,
            date_debut=filters.date_debut,
            date_fin=filters.date_fin,
            chantier_origine_id=filters.chantier_origine_id,
            limit=filters.limit,
            offset=filters.offset,
        )

        total = await self._repository.count(
            statut=filters.statut,
            priorite=filters.priorite,
            type_intervention=filters.type_intervention,
        )

        return interventions, total


class UpdateInterventionUseCase:
    """Use case pour modifier une intervention."""

    def __init__(self, repository: InterventionRepository):
        self._repository = repository

    async def execute(
        self, intervention_id: int, dto: UpdateInterventionDTO
    ) -> Optional[Intervention]:
        """Met a jour une intervention."""
        intervention = await self._repository.get_by_id(intervention_id)
        if not intervention:
            return None

        if not intervention.statut.est_modifiable:
            raise ValueError("Cette intervention ne peut plus etre modifiee")

        if dto.type_intervention is not None:
            intervention.type_intervention = dto.type_intervention

        if dto.priorite is not None:
            intervention.modifier_priorite(dto.priorite)

        if dto.client_nom is not None or dto.client_adresse is not None:
            intervention.modifier_client(
                nom=dto.client_nom,
                adresse=dto.client_adresse,
                telephone=dto.client_telephone,
                email=dto.client_email,
            )

        if dto.description is not None:
            intervention.modifier_description(dto.description)

        if dto.date_souhaitee is not None:
            intervention.date_souhaitee = dto.date_souhaitee

        if dto.travaux_realises is not None:
            intervention.travaux_realises = dto.travaux_realises

        if dto.anomalies is not None:
            intervention.anomalies = dto.anomalies

        return await self._repository.save(intervention)


class PlanifierInterventionUseCase:
    """Use case pour planifier une intervention.

    INT-05: Statuts intervention
    INT-06: Planning hebdomadaire
    """

    def __init__(
        self,
        repository: InterventionRepository,
        affectation_repository: AffectationInterventionRepository,
    ):
        self._repository = repository
        self._affectation_repository = affectation_repository

    async def execute(
        self, intervention_id: int, dto: PlanifierInterventionDTO, planned_by: int
    ) -> Optional[Intervention]:
        """Planifie une intervention avec date et techniciens."""
        intervention = await self._repository.get_by_id(intervention_id)
        if not intervention:
            return None

        intervention.planifier(
            date_planifiee=dto.date_planifiee,
            heure_debut=dto.heure_debut,
            heure_fin=dto.heure_fin,
        )

        # Affecter les techniciens si specifies
        from ...domain.entities import AffectationIntervention

        for i, tech_id in enumerate(dto.techniciens_ids):
            # Verifier si deja affecte
            exists = await self._affectation_repository.exists(
                intervention_id, tech_id
            )
            if not exists:
                affectation = AffectationIntervention(
                    intervention_id=intervention_id,
                    utilisateur_id=tech_id,
                    est_principal=(i == 0),  # Premier = principal
                    created_by=planned_by,
                )
                await self._affectation_repository.save(affectation)

        return await self._repository.save(intervention)


class DemarrerInterventionUseCase:
    """Use case pour demarrer une intervention."""

    def __init__(self, repository: InterventionRepository):
        self._repository = repository

    async def execute(
        self, intervention_id: int, dto: DemarrerInterventionDTO
    ) -> Optional[Intervention]:
        """Demarre une intervention."""
        intervention = await self._repository.get_by_id(intervention_id)
        if not intervention:
            return None

        intervention.demarrer(dto.heure_debut_reelle)

        return await self._repository.save(intervention)


class TerminerInterventionUseCase:
    """Use case pour terminer une intervention."""

    def __init__(self, repository: InterventionRepository):
        self._repository = repository

    async def execute(
        self, intervention_id: int, dto: TerminerInterventionDTO
    ) -> Optional[Intervention]:
        """Termine une intervention."""
        intervention = await self._repository.get_by_id(intervention_id)
        if not intervention:
            return None

        intervention.terminer(
            heure_fin_reelle=dto.heure_fin_reelle,
            travaux_realises=dto.travaux_realises,
            anomalies=dto.anomalies,
        )

        return await self._repository.save(intervention)


class AnnulerInterventionUseCase:
    """Use case pour annuler une intervention."""

    def __init__(self, repository: InterventionRepository):
        self._repository = repository

    async def execute(self, intervention_id: int) -> Optional[Intervention]:
        """Annule une intervention."""
        intervention = await self._repository.get_by_id(intervention_id)
        if not intervention:
            return None

        intervention.annuler()

        return await self._repository.save(intervention)


class DeleteInterventionUseCase:
    """Use case pour supprimer une intervention (soft delete)."""

    def __init__(self, repository: InterventionRepository):
        self._repository = repository

    async def execute(self, intervention_id: int, deleted_by: int) -> bool:
        """Supprime une intervention."""
        return await self._repository.delete(intervention_id, deleted_by)
