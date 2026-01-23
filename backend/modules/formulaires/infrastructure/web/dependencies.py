"""Dependencies FastAPI pour le module Formulaires."""

from fastapi import Depends
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from modules.auth.infrastructure.web.dependencies import get_current_user_id
from ...adapters.controllers import FormulaireController
from ...application.use_cases import (
    CreateTemplateUseCase,
    UpdateTemplateUseCase,
    DeleteTemplateUseCase,
    GetTemplateUseCase,
    ListTemplatesUseCase,
    CreateFormulaireUseCase,
    UpdateFormulaireUseCase,
    SubmitFormulaireUseCase,
    GetFormulaireUseCase,
    ListFormulairesUseCase,
    GetFormulaireHistoryUseCase,
    ExportFormulairePDFUseCase,
)
from ..persistence import (
    SQLAlchemyTemplateFormulaireRepository,
    SQLAlchemyFormulaireRempliRepository,
)


def get_template_repository(db: Session = Depends(get_db)):
    """Fournit le repository des templates."""
    return SQLAlchemyTemplateFormulaireRepository(db)


def get_formulaire_repository(db: Session = Depends(get_db)):
    """Fournit le repository des formulaires."""
    return SQLAlchemyFormulaireRempliRepository(db)


def get_formulaire_controller(
    db: Session = Depends(get_db),
) -> FormulaireController:
    """Fournit le controller des formulaires."""
    template_repo = SQLAlchemyTemplateFormulaireRepository(db)
    formulaire_repo = SQLAlchemyFormulaireRempliRepository(db)

    return FormulaireController(
        create_template_uc=CreateTemplateUseCase(template_repo),
        update_template_uc=UpdateTemplateUseCase(template_repo),
        delete_template_uc=DeleteTemplateUseCase(template_repo),
        get_template_uc=GetTemplateUseCase(template_repo),
        list_templates_uc=ListTemplatesUseCase(template_repo),
        create_formulaire_uc=CreateFormulaireUseCase(formulaire_repo, template_repo),
        update_formulaire_uc=UpdateFormulaireUseCase(formulaire_repo),
        submit_formulaire_uc=SubmitFormulaireUseCase(formulaire_repo),
        get_formulaire_uc=GetFormulaireUseCase(formulaire_repo),
        list_formulaires_uc=ListFormulairesUseCase(formulaire_repo),
        get_history_uc=GetFormulaireHistoryUseCase(formulaire_repo),
        export_pdf_uc=ExportFormulairePDFUseCase(formulaire_repo, template_repo),
    )
