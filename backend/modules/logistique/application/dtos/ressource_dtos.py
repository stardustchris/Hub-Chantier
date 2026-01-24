"""DTOs pour les ressources.

LOG-01: Référentiel matériel
LOG-02: Fiche ressource
"""

from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional, List

from ...domain.value_objects import CategorieRessource


@dataclass
class RessourceCreateDTO:
    """DTO pour la création d'une ressource."""

    nom: str
    code: str
    categorie: CategorieRessource
    photo_url: Optional[str] = None
    couleur: str = "#3B82F6"
    heure_debut_defaut: time = None
    heure_fin_defaut: time = None
    validation_requise: Optional[bool] = None
    description: Optional[str] = None

    def __post_init__(self) -> None:
        if self.heure_debut_defaut is None:
            self.heure_debut_defaut = time(8, 0)
        if self.heure_fin_defaut is None:
            self.heure_fin_defaut = time(18, 0)


@dataclass
class RessourceUpdateDTO:
    """DTO pour la mise à jour d'une ressource."""

    nom: Optional[str] = None
    code: Optional[str] = None
    categorie: Optional[CategorieRessource] = None
    photo_url: Optional[str] = None
    couleur: Optional[str] = None
    heure_debut_defaut: Optional[time] = None
    heure_fin_defaut: Optional[time] = None
    validation_requise: Optional[bool] = None
    actif: Optional[bool] = None
    description: Optional[str] = None


@dataclass
class RessourceDTO:
    """DTO de sortie pour une ressource."""

    id: int
    nom: str
    code: str
    categorie: str
    categorie_label: str
    photo_url: Optional[str]
    couleur: str
    heure_debut_defaut: str
    heure_fin_defaut: str
    validation_requise: bool
    actif: bool
    description: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[int]

    @classmethod
    def from_entity(cls, ressource) -> "RessourceDTO":
        """Crée un DTO depuis une entité Ressource."""
        return cls(
            id=ressource.id,
            nom=ressource.nom,
            code=ressource.code,
            categorie=ressource.categorie.value,
            categorie_label=ressource.categorie.label,
            photo_url=ressource.photo_url,
            couleur=ressource.couleur,
            heure_debut_defaut=ressource.plage_horaire_defaut.heure_debut.isoformat(),
            heure_fin_defaut=ressource.plage_horaire_defaut.heure_fin.isoformat(),
            validation_requise=ressource.validation_requise,
            actif=ressource.actif,
            description=ressource.description,
            created_at=ressource.created_at,
            updated_at=ressource.updated_at,
            created_by=ressource.created_by,
        )


@dataclass
class RessourceListDTO:
    """DTO pour une liste paginée de ressources."""

    items: List[RessourceDTO]
    total: int
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        """Indique s'il y a plus de résultats."""
        return self.offset + len(self.items) < self.total
