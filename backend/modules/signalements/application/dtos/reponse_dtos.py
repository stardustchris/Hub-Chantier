"""DTOs pour les réponses aux signalements."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class ReponseDTO:
    """DTO représentant une réponse."""

    id: int
    signalement_id: int
    contenu: str
    auteur_id: int
    auteur_nom: Optional[str]
    photo_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    est_resolution: bool


@dataclass
class ReponseCreateDTO:
    """DTO pour la création d'une réponse."""

    signalement_id: int
    contenu: str
    auteur_id: int
    photo_url: Optional[str] = None
    est_resolution: bool = False


@dataclass
class ReponseUpdateDTO:
    """DTO pour la mise à jour d'une réponse."""

    contenu: Optional[str] = None
    photo_url: Optional[str] = None


@dataclass
class ReponseListDTO:
    """DTO pour la liste de réponses avec pagination."""

    reponses: List[ReponseDTO]
    total: int
    skip: int
    limit: int
