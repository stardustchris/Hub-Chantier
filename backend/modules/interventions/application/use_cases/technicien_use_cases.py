"""Use Cases pour la gestion des techniciens sur les interventions."""

from typing import Optional, List

from ...domain.entities import AffectationIntervention
from ...domain.repositories import AffectationInterventionRepository
from ..dtos import AffecterTechnicienDTO


class AffecterTechnicienUseCase:
    """Use case pour affecter un technicien.

    INT-10: Affectation technicien
    INT-17: Affectation sous-traitants
    """

    def __init__(self, repository: AffectationInterventionRepository):
        self._repository = repository

    def execute(
        self,
        intervention_id: int,
        dto: AffecterTechnicienDTO,
        created_by: int,
    ) -> AffectationIntervention:
        """Affecte un technicien a une intervention."""
        # Verifier si deja affecte
        exists = self._repository.exists(intervention_id, dto.utilisateur_id)
        if exists:
            raise ValueError("Ce technicien est deja affecte a cette intervention")

        # Si principal demande, retirer le principal actuel
        if dto.est_principal:
            principal = self._repository.get_principal(intervention_id)
            if principal:
                principal.retirer_principal()
                self._repository.save(principal)

        affectation = AffectationIntervention(
            intervention_id=intervention_id,
            utilisateur_id=dto.utilisateur_id,
            est_principal=dto.est_principal,
            commentaire=dto.commentaire,
            created_by=created_by,
        )

        return self._repository.save(affectation)


class DesaffecterTechnicienUseCase:
    """Use case pour desaffecter un technicien."""

    def __init__(self, repository: AffectationInterventionRepository):
        self._repository = repository

    def execute(
        self, affectation_id: int, deleted_by: int
    ) -> bool:
        """Desaffecte un technicien d'une intervention."""
        return self._repository.delete(affectation_id, deleted_by)


class ListTechniciensInterventionUseCase:
    """Use case pour lister les techniciens d'une intervention."""

    def __init__(self, repository: AffectationInterventionRepository):
        self._repository = repository

    def execute(
        self, intervention_id: int
    ) -> List[AffectationIntervention]:
        """Liste les techniciens affectes a une intervention."""
        return self._repository.list_by_intervention(intervention_id)
