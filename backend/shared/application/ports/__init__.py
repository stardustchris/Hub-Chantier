"""Ports (interfaces) for shared services."""

from .entity_info_service import (
    EntityInfoService,
    UserBasicInfo,
    ChantierBasicInfo,
)
from .pdf_generator import PdfGeneratorPort
from .audit import AuditPort
from .chantier_creation_port import (
    ChantierCreationPort,
    ChantierCreationData,
    BudgetCreationData,
    LotBudgetaireCreationData,
    ConversionChantierResult,
)
from .chantier_info_port import (
    ChantierInfoPort,
    ChantierInfoDTO,
)
from .chantier_cloture_check_port import (
    ChantierClotureCheckPort,
    ClotureCheckResult,
)
from .email_service import EmailServicePort

__all__ = [
    "EntityInfoService",
    "UserBasicInfo",
    "ChantierBasicInfo",
    "PdfGeneratorPort",
    "AuditPort",
    "ChantierCreationPort",
    "ChantierCreationData",
    "BudgetCreationData",
    "LotBudgetaireCreationData",
    "ConversionChantierResult",
    "ChantierInfoPort",
    "ChantierInfoDTO",
    "ChantierClotureCheckPort",
    "ClotureCheckResult",
    "EmailServicePort",
]
