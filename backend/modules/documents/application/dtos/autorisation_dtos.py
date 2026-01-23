"""DTOs pour les autorisations."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class AutorisationDTO:
    """DTO représentant une autorisation."""

    id: int
    user_id: int
    user_nom: Optional[str]
    type_autorisation: str
    dossier_id: Optional[int]
    document_id: Optional[int]
    cible_nom: Optional[str]
    accorde_par: int
    accorde_par_nom: Optional[str]
    created_at: datetime
    expire_at: Optional[datetime]
    est_valide: bool


@dataclass
class AutorisationCreateDTO:
    """DTO pour la création d'une autorisation."""

    user_id: int
    type_autorisation: str
    accorde_par: int
    dossier_id: Optional[int] = None
    document_id: Optional[int] = None
    expire_at: Optional[datetime] = None


@dataclass
class AutorisationListDTO:
    """DTO pour la liste d'autorisations."""

    autorisations: List[AutorisationDTO]
    total: int
