"""DTOs pour les taches."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List

from ...domain.entities import Tache
from ...domain.value_objects import StatutTache, UniteMesure, CouleurProgression


@dataclass
class TacheDTO:
    """DTO pour representer une tache."""

    id: int
    chantier_id: int
    titre: str
    description: Optional[str]
    parent_id: Optional[int]
    ordre: int
    statut: str
    statut_display: str
    statut_icon: str
    date_echeance: Optional[str]
    unite_mesure: Optional[str]
    unite_mesure_display: Optional[str]
    quantite_estimee: Optional[float]
    quantite_realisee: float
    heures_estimees: Optional[float]
    heures_realisees: float
    progression_heures: float
    progression_quantite: float
    couleur_progression: str
    couleur_hex: str
    est_terminee: bool
    est_en_retard: bool
    a_sous_taches: bool
    nombre_sous_taches: int
    nombre_sous_taches_terminees: int
    template_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    sous_taches: List["TacheDTO"] = field(default_factory=list)

    @classmethod
    def from_entity(cls, tache: Tache) -> "TacheDTO":
        """Convertit une entite Tache en DTO."""
        couleur = tache.couleur_progression

        return cls(
            id=tache.id,
            chantier_id=tache.chantier_id,
            titre=tache.titre,
            description=tache.description,
            parent_id=tache.parent_id,
            ordre=tache.ordre,
            statut=tache.statut.value,
            statut_display=tache.statut.display_name,
            statut_icon=tache.statut.icon,
            date_echeance=tache.date_echeance.isoformat() if tache.date_echeance else None,
            unite_mesure=tache.unite_mesure.value if tache.unite_mesure else None,
            unite_mesure_display=tache.unite_mesure.display_name if tache.unite_mesure else None,
            quantite_estimee=tache.quantite_estimee,
            quantite_realisee=tache.quantite_realisee,
            heures_estimees=tache.heures_estimees,
            heures_realisees=tache.heures_realisees,
            progression_heures=tache.progression_heures,
            progression_quantite=tache.progression_quantite,
            couleur_progression=couleur.value,
            couleur_hex=couleur.hex_code,
            est_terminee=tache.est_terminee,
            est_en_retard=tache.est_en_retard,
            a_sous_taches=tache.a_sous_taches,
            nombre_sous_taches=tache.nombre_sous_taches,
            nombre_sous_taches_terminees=tache.nombre_sous_taches_terminees,
            template_id=tache.template_id,
            created_at=tache.created_at,
            updated_at=tache.updated_at,
            sous_taches=[cls.from_entity(st) for st in tache.sous_taches],
        )


@dataclass
class CreateTacheDTO:
    """DTO pour la creation d'une tache (TAC-06, TAC-07)."""

    chantier_id: int
    titre: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    date_echeance: Optional[str] = None
    unite_mesure: Optional[str] = None
    quantite_estimee: Optional[float] = None
    heures_estimees: Optional[float] = None


@dataclass
class UpdateTacheDTO:
    """DTO pour la mise a jour d'une tache."""

    titre: Optional[str] = None
    description: Optional[str] = None
    date_echeance: Optional[str] = None
    unite_mesure: Optional[str] = None
    quantite_estimee: Optional[float] = None
    heures_estimees: Optional[float] = None
    statut: Optional[str] = None
    ordre: Optional[int] = None


@dataclass
class TacheListDTO:
    """DTO pour une liste paginee de taches."""

    items: List[TacheDTO]
    total: int
    page: int
    size: int
    pages: int


@dataclass
class TacheStatsDTO:
    """DTO pour les statistiques des taches d'un chantier."""

    chantier_id: int
    total_taches: int
    taches_terminees: int
    taches_en_cours: int
    taches_en_retard: int
    heures_estimees_total: float
    heures_realisees_total: float
    progression_globale: float
