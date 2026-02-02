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
]
