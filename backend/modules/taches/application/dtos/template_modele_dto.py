"""DTOs pour les templates de modeles."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from ...domain.entities import TemplateModele, SousTacheModele


@dataclass
class SousTacheModeleDTO:
    """DTO pour une sous-tache de modele."""

    titre: str
    description: Optional[str] = None
    ordre: int = 0
    unite_mesure: Optional[str] = None
    heures_estimees_defaut: Optional[float] = None

    @classmethod
    def from_entity(cls, sous_tache: SousTacheModele) -> "SousTacheModeleDTO":
        """Convertit une SousTacheModele en DTO."""
        return cls(
            titre=sous_tache.titre,
            description=sous_tache.description,
            ordre=sous_tache.ordre,
            unite_mesure=sous_tache.unite_mesure.value if sous_tache.unite_mesure else None,
            heures_estimees_defaut=sous_tache.heures_estimees_defaut,
        )


@dataclass
class TemplateModeleDTO:
    """DTO pour representer un template de taches (TAC-04)."""

    id: int
    nom: str
    description: Optional[str]
    categorie: Optional[str]
    unite_mesure: Optional[str]
    unite_mesure_display: Optional[str]
    heures_estimees_defaut: Optional[float]
    nombre_sous_taches: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    sous_taches: List[SousTacheModeleDTO] = field(default_factory=list)

    @classmethod
    def from_entity(cls, template: TemplateModele) -> "TemplateModeleDTO":
        """Convertit une entite TemplateModele en DTO."""

        unite_display = None
        if template.unite_mesure:
            unite_display = template.unite_mesure.display_name

        return cls(
            id=template.id,
            nom=template.nom,
            description=template.description,
            categorie=template.categorie,
            unite_mesure=template.unite_mesure.value if template.unite_mesure else None,
            unite_mesure_display=unite_display,
            heures_estimees_defaut=template.heures_estimees_defaut,
            nombre_sous_taches=template.nombre_sous_taches,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at,
            sous_taches=[SousTacheModeleDTO.from_entity(st) for st in template.sous_taches],
        )


@dataclass
class CreateTemplateModeleDTO:
    """DTO pour la creation d'un template."""

    nom: str
    description: Optional[str] = None
    categorie: Optional[str] = None
    unite_mesure: Optional[str] = None
    heures_estimees_defaut: Optional[float] = None
    sous_taches: List[SousTacheModeleDTO] = field(default_factory=list)


@dataclass
class UpdateTemplateModeleDTO:
    """DTO pour la mise a jour d'un template."""

    nom: Optional[str] = None
    description: Optional[str] = None
    categorie: Optional[str] = None
    unite_mesure: Optional[str] = None
    heures_estimees_defaut: Optional[float] = None
    is_active: Optional[bool] = None


@dataclass
class TemplateModeleListDTO:
    """DTO pour une liste paginee de templates."""

    items: List[TemplateModeleDTO]
    total: int
    page: int
    size: int
    pages: int
    categories: List[str] = field(default_factory=list)
