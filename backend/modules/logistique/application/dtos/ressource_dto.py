"""DTOs pour les ressources.

CDC Section 11 - LOG-01, LOG-02.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from ...domain.entities import Ressource
from ...domain.value_objects import TypeRessource


@dataclass(frozen=True)
class CreateRessourceDTO:
    """DTO pour la creation d'une ressource (LOG-01)."""
    code: str
    nom: str
    type_ressource: str
    description: Optional[str] = None
    photo_url: Optional[str] = None
    couleur: str = "#3498DB"
    plage_horaire_debut: str = "08:00"
    plage_horaire_fin: str = "18:00"
    validation_requise: bool = True


@dataclass(frozen=True)
class UpdateRessourceDTO:
    """DTO pour la mise a jour d'une ressource."""
    id: int
    nom: Optional[str] = None
    description: Optional[str] = None
    type_ressource: Optional[str] = None
    photo_url: Optional[str] = None
    couleur: Optional[str] = None
    plage_horaire_debut: Optional[str] = None
    plage_horaire_fin: Optional[str] = None
    validation_requise: Optional[bool] = None


@dataclass(frozen=True)
class RessourceDTO:
    """DTO de reponse pour une ressource (LOG-02)."""
    id: int
    code: str
    nom: str
    description: Optional[str]
    type_ressource: str
    type_ressource_label: str
    photo_url: Optional[str]
    couleur: str
    plage_horaire_debut: str
    plage_horaire_fin: str
    validation_requise: bool
    is_active: bool
    created_at: str
    updated_at: str

    @staticmethod
    def from_entity(ressource: Ressource) -> "RessourceDTO":
        """Convertit une entite en DTO."""
        return RessourceDTO(
            id=ressource.id,  # type: ignore
            code=ressource.code,
            nom=ressource.nom,
            description=ressource.description,
            type_ressource=ressource.type_ressource.value,
            type_ressource_label=ressource.type_ressource.label,
            photo_url=ressource.photo_url,
            couleur=ressource.couleur,
            plage_horaire_debut=ressource.plage_horaire_debut,
            plage_horaire_fin=ressource.plage_horaire_fin,
            validation_requise=ressource.validation_requise,
            is_active=ressource.is_active,
            created_at=ressource.created_at.isoformat(),
            updated_at=ressource.updated_at.isoformat(),
        )


@dataclass(frozen=True)
class RessourceListDTO:
    """DTO pour une liste paginee de ressources."""
    ressources: List[RessourceDTO]
    total: int
    skip: int
    limit: int

    @property
    def has_next(self) -> bool:
        """Indique s'il y a une page suivante."""
        return self.skip + self.limit < self.total

    @property
    def has_previous(self) -> bool:
        """Indique s'il y a une page precedente."""
        return self.skip > 0
