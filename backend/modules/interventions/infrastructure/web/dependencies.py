"""Dependencies injection pour le module Interventions."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from shared.infrastructure.database import get_async_session
from ...domain.repositories import (
    InterventionRepository,
    AffectationInterventionRepository,
    InterventionMessageRepository,
    SignatureInterventionRepository,
)
from ..persistence import (
    SQLAlchemyInterventionRepository,
    SQLAlchemyAffectationInterventionRepository,
    SQLAlchemyInterventionMessageRepository,
    SQLAlchemySignatureInterventionRepository,
)
from ...application.use_cases import (
    CreateInterventionUseCase,
    GetInterventionUseCase,
    ListInterventionsUseCase,
    UpdateInterventionUseCase,
    PlanifierInterventionUseCase,
    DemarrerInterventionUseCase,
    TerminerInterventionUseCase,
    AnnulerInterventionUseCase,
    DeleteInterventionUseCase,
    AffecterTechnicienUseCase,
    DesaffecterTechnicienUseCase,
    ListTechniciensInterventionUseCase,
    AddMessageUseCase,
    ListMessagesUseCase,
    ToggleRapportInclusionUseCase,
    AddSignatureUseCase,
    ListSignaturesUseCase,
)


async def get_intervention_repository(
    session: AsyncSession,
) -> InterventionRepository:
    """Factory pour le repository Intervention."""
    return SQLAlchemyInterventionRepository(session)


async def get_affectation_repository(
    session: AsyncSession,
) -> AffectationInterventionRepository:
    """Factory pour le repository AffectationIntervention."""
    return SQLAlchemyAffectationInterventionRepository(session)


async def get_message_repository(
    session: AsyncSession,
) -> InterventionMessageRepository:
    """Factory pour le repository InterventionMessage."""
    return SQLAlchemyInterventionMessageRepository(session)


async def get_signature_repository(
    session: AsyncSession,
) -> SignatureInterventionRepository:
    """Factory pour le repository SignatureIntervention."""
    return SQLAlchemySignatureInterventionRepository(session)


# Use Case factories

async def get_create_intervention_use_case(
    session: AsyncSession,
) -> CreateInterventionUseCase:
    """Factory pour CreateInterventionUseCase."""
    repo = await get_intervention_repository(session)
    return CreateInterventionUseCase(repo)


async def get_get_intervention_use_case(
    session: AsyncSession,
) -> GetInterventionUseCase:
    """Factory pour GetInterventionUseCase."""
    repo = await get_intervention_repository(session)
    return GetInterventionUseCase(repo)


async def get_list_interventions_use_case(
    session: AsyncSession,
) -> ListInterventionsUseCase:
    """Factory pour ListInterventionsUseCase."""
    repo = await get_intervention_repository(session)
    return ListInterventionsUseCase(repo)


async def get_update_intervention_use_case(
    session: AsyncSession,
) -> UpdateInterventionUseCase:
    """Factory pour UpdateInterventionUseCase."""
    repo = await get_intervention_repository(session)
    return UpdateInterventionUseCase(repo)


async def get_planifier_intervention_use_case(
    session: AsyncSession,
) -> PlanifierInterventionUseCase:
    """Factory pour PlanifierInterventionUseCase."""
    intervention_repo = await get_intervention_repository(session)
    affectation_repo = await get_affectation_repository(session)
    return PlanifierInterventionUseCase(intervention_repo, affectation_repo)


async def get_demarrer_intervention_use_case(
    session: AsyncSession,
) -> DemarrerInterventionUseCase:
    """Factory pour DemarrerInterventionUseCase."""
    repo = await get_intervention_repository(session)
    return DemarrerInterventionUseCase(repo)


async def get_terminer_intervention_use_case(
    session: AsyncSession,
) -> TerminerInterventionUseCase:
    """Factory pour TerminerInterventionUseCase."""
    repo = await get_intervention_repository(session)
    return TerminerInterventionUseCase(repo)


async def get_annuler_intervention_use_case(
    session: AsyncSession,
) -> AnnulerInterventionUseCase:
    """Factory pour AnnulerInterventionUseCase."""
    repo = await get_intervention_repository(session)
    return AnnulerInterventionUseCase(repo)


async def get_delete_intervention_use_case(
    session: AsyncSession,
) -> DeleteInterventionUseCase:
    """Factory pour DeleteInterventionUseCase."""
    repo = await get_intervention_repository(session)
    return DeleteInterventionUseCase(repo)


async def get_affecter_technicien_use_case(
    session: AsyncSession,
) -> AffecterTechnicienUseCase:
    """Factory pour AffecterTechnicienUseCase."""
    repo = await get_affectation_repository(session)
    return AffecterTechnicienUseCase(repo)


async def get_desaffecter_technicien_use_case(
    session: AsyncSession,
) -> DesaffecterTechnicienUseCase:
    """Factory pour DesaffecterTechnicienUseCase."""
    repo = await get_affectation_repository(session)
    return DesaffecterTechnicienUseCase(repo)


async def get_list_techniciens_use_case(
    session: AsyncSession,
) -> ListTechniciensInterventionUseCase:
    """Factory pour ListTechniciensInterventionUseCase."""
    repo = await get_affectation_repository(session)
    return ListTechniciensInterventionUseCase(repo)


async def get_add_message_use_case(
    session: AsyncSession,
) -> AddMessageUseCase:
    """Factory pour AddMessageUseCase."""
    repo = await get_message_repository(session)
    return AddMessageUseCase(repo)


async def get_list_messages_use_case(
    session: AsyncSession,
) -> ListMessagesUseCase:
    """Factory pour ListMessagesUseCase."""
    repo = await get_message_repository(session)
    return ListMessagesUseCase(repo)


async def get_toggle_rapport_use_case(
    session: AsyncSession,
) -> ToggleRapportInclusionUseCase:
    """Factory pour ToggleRapportInclusionUseCase."""
    repo = await get_message_repository(session)
    return ToggleRapportInclusionUseCase(repo)


async def get_add_signature_use_case(
    session: AsyncSession,
) -> AddSignatureUseCase:
    """Factory pour AddSignatureUseCase."""
    repo = await get_signature_repository(session)
    return AddSignatureUseCase(repo)


async def get_list_signatures_use_case(
    session: AsyncSession,
) -> ListSignaturesUseCase:
    """Factory pour ListSignaturesUseCase."""
    repo = await get_signature_repository(session)
    return ListSignaturesUseCase(repo)
