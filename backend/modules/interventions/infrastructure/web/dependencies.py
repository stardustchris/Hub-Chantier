"""Dependencies injection pour le module Interventions."""

from fastapi import Depends
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from shared.infrastructure.pdf import PdfGeneratorService
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
    GenerateInterventionPDFUseCase,
)


def get_intervention_repository(
    db: Session = Depends(get_db),
) -> InterventionRepository:
    """Factory pour le repository Intervention."""
    return SQLAlchemyInterventionRepository(db)


def get_affectation_repository(
    db: Session = Depends(get_db),
) -> AffectationInterventionRepository:
    """Factory pour le repository AffectationIntervention."""
    return SQLAlchemyAffectationInterventionRepository(db)


def get_message_repository(
    db: Session = Depends(get_db),
) -> InterventionMessageRepository:
    """Factory pour le repository InterventionMessage."""
    return SQLAlchemyInterventionMessageRepository(db)


def get_signature_repository(
    db: Session = Depends(get_db),
) -> SignatureInterventionRepository:
    """Factory pour le repository SignatureIntervention."""
    return SQLAlchemySignatureInterventionRepository(db)


# Use Case factories

def get_create_intervention_use_case(
    repo: InterventionRepository = Depends(get_intervention_repository),
) -> CreateInterventionUseCase:
    """Factory pour CreateInterventionUseCase."""
    return CreateInterventionUseCase(repo)


def get_get_intervention_use_case(
    repo: InterventionRepository = Depends(get_intervention_repository),
) -> GetInterventionUseCase:
    """Factory pour GetInterventionUseCase."""
    return GetInterventionUseCase(repo)


def get_list_interventions_use_case(
    repo: InterventionRepository = Depends(get_intervention_repository),
) -> ListInterventionsUseCase:
    """Factory pour ListInterventionsUseCase."""
    return ListInterventionsUseCase(repo)


def get_update_intervention_use_case(
    repo: InterventionRepository = Depends(get_intervention_repository),
) -> UpdateInterventionUseCase:
    """Factory pour UpdateInterventionUseCase."""
    return UpdateInterventionUseCase(repo)


def get_planifier_intervention_use_case(
    intervention_repo: InterventionRepository = Depends(get_intervention_repository),
    affectation_repo: AffectationInterventionRepository = Depends(get_affectation_repository),
) -> PlanifierInterventionUseCase:
    """Factory pour PlanifierInterventionUseCase."""
    return PlanifierInterventionUseCase(intervention_repo, affectation_repo)


def get_demarrer_intervention_use_case(
    repo: InterventionRepository = Depends(get_intervention_repository),
) -> DemarrerInterventionUseCase:
    """Factory pour DemarrerInterventionUseCase."""
    return DemarrerInterventionUseCase(repo)


def get_terminer_intervention_use_case(
    repo: InterventionRepository = Depends(get_intervention_repository),
) -> TerminerInterventionUseCase:
    """Factory pour TerminerInterventionUseCase."""
    return TerminerInterventionUseCase(repo)


def get_annuler_intervention_use_case(
    repo: InterventionRepository = Depends(get_intervention_repository),
) -> AnnulerInterventionUseCase:
    """Factory pour AnnulerInterventionUseCase."""
    return AnnulerInterventionUseCase(repo)


def get_delete_intervention_use_case(
    repo: InterventionRepository = Depends(get_intervention_repository),
) -> DeleteInterventionUseCase:
    """Factory pour DeleteInterventionUseCase."""
    return DeleteInterventionUseCase(repo)


def get_affecter_technicien_use_case(
    repo: AffectationInterventionRepository = Depends(get_affectation_repository),
) -> AffecterTechnicienUseCase:
    """Factory pour AffecterTechnicienUseCase."""
    return AffecterTechnicienUseCase(repo)


def get_desaffecter_technicien_use_case(
    repo: AffectationInterventionRepository = Depends(get_affectation_repository),
) -> DesaffecterTechnicienUseCase:
    """Factory pour DesaffecterTechnicienUseCase."""
    return DesaffecterTechnicienUseCase(repo)


def get_list_techniciens_use_case(
    repo: AffectationInterventionRepository = Depends(get_affectation_repository),
) -> ListTechniciensInterventionUseCase:
    """Factory pour ListTechniciensInterventionUseCase."""
    return ListTechniciensInterventionUseCase(repo)


def get_add_message_use_case(
    repo: InterventionMessageRepository = Depends(get_message_repository),
) -> AddMessageUseCase:
    """Factory pour AddMessageUseCase."""
    return AddMessageUseCase(repo)


def get_list_messages_use_case(
    repo: InterventionMessageRepository = Depends(get_message_repository),
) -> ListMessagesUseCase:
    """Factory pour ListMessagesUseCase."""
    return ListMessagesUseCase(repo)


def get_toggle_rapport_use_case(
    repo: InterventionMessageRepository = Depends(get_message_repository),
) -> ToggleRapportInclusionUseCase:
    """Factory pour ToggleRapportInclusionUseCase."""
    return ToggleRapportInclusionUseCase(repo)


def get_add_signature_use_case(
    repo: SignatureInterventionRepository = Depends(get_signature_repository),
) -> AddSignatureUseCase:
    """Factory pour AddSignatureUseCase."""
    return AddSignatureUseCase(repo)


def get_list_signatures_use_case(
    repo: SignatureInterventionRepository = Depends(get_signature_repository),
) -> ListSignaturesUseCase:
    """Factory pour ListSignaturesUseCase."""
    return ListSignaturesUseCase(repo)


# ─────────────────────────────────────────────────────────────────────────────
# Use Case - Generation PDF (INT-14, INT-15)
# ─────────────────────────────────────────────────────────────────────────────

def get_generate_intervention_pdf_use_case(
    intervention_repo: InterventionRepository = Depends(get_intervention_repository),
    affectation_repo: AffectationInterventionRepository = Depends(get_affectation_repository),
    message_repo: InterventionMessageRepository = Depends(get_message_repository),
    signature_repo: SignatureInterventionRepository = Depends(get_signature_repository),
) -> GenerateInterventionPDFUseCase:
    """Factory pour GenerateInterventionPDFUseCase.

    INT-14: Rapport PDF - Generation automatique.
    """
    pdf_generator = PdfGeneratorService()
    return GenerateInterventionPDFUseCase(
        intervention_repo=intervention_repo,
        affectation_repo=affectation_repo,
        message_repo=message_repo,
        signature_repo=signature_repo,
        pdf_generator=pdf_generator,
    )
