from .devis_dtos import (
    DevisDTO,
    DevisCreateDTO,
    DevisUpdateDTO,
    DevisDetailDTO,
)
from .lot_dtos import LotDevisDTO, LotDevisCreateDTO, LotDevisUpdateDTO
from .ligne_dtos import LigneDevisDTO, LigneDevisCreateDTO, LigneDevisUpdateDTO
from .debourse_dtos import DebourseDetailDTO, DebourseDetailCreateDTO
from .dashboard_dtos import KPIDevisDTO, DevisRecentDTO, DashboardDevisDTO
from .attestation_tva_dtos import AttestationTVACreateDTO, AttestationTVADTO, EligibiliteTVADTO
from .frais_chantier_dtos import FraisChantierCreateDTO, FraisChantierUpdateDTO, FraisChantierDTO
from .convertir_devis_dto import ConvertirDevisOptionsDTO, ConvertirDevisResultDTO
from .structure_dtos import (
    CreateDevisStructureDTO,
    LotStructureDTO,
    SousChapitreStructureDTO,
    LigneStructureDTO,
    ReorderItemDTO,
    ReorderRequestDTO,
    StructureDevisDTO,
)
from .decompose_debourse_dtos import (
    DecomposeDebourseDTO,
    DecomposeLotDTO,
    DecomposeDevisDTO,
)
from .marge_dtos import (
    AppliquerMargeGlobaleDTO,
    AppliquerMargeLotDTO,
    AppliquerMargeLigneDTO,
    MargeResolueDTO,
    MargesDevisDTO,
)

__all__ = [
    "DevisDTO",
    "DevisCreateDTO",
    "DevisUpdateDTO",
    "DevisDetailDTO",
    "LotDevisDTO",
    "LotDevisCreateDTO",
    "LotDevisUpdateDTO",
    "LigneDevisDTO",
    "LigneDevisCreateDTO",
    "LigneDevisUpdateDTO",
    "DebourseDetailDTO",
    "DebourseDetailCreateDTO",
    "KPIDevisDTO",
    "DevisRecentDTO",
    "DashboardDevisDTO",
    "AttestationTVACreateDTO",
    "AttestationTVADTO",
    "EligibiliteTVADTO",
    "FraisChantierCreateDTO",
    "FraisChantierUpdateDTO",
    "FraisChantierDTO",
    "ConvertirDevisOptionsDTO",
    "ConvertirDevisResultDTO",
    # DEV-03: Structure
    "CreateDevisStructureDTO",
    "LotStructureDTO",
    "SousChapitreStructureDTO",
    "LigneStructureDTO",
    "ReorderItemDTO",
    "ReorderRequestDTO",
    "StructureDevisDTO",
    # DEV-05: Decompose debourse
    "DecomposeDebourseDTO",
    "DecomposeLotDTO",
    "DecomposeDevisDTO",
    # DEV-06: Marges
    "AppliquerMargeGlobaleDTO",
    "AppliquerMargeLotDTO",
    "AppliquerMargeLigneDTO",
    "MargeResolueDTO",
    "MargesDevisDTO",
]
