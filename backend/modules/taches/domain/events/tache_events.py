"""Domain Events pour le module Taches."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class TacheCreatedEvent:
    """Event emis lors de la creation d'une tache (TAC-06, TAC-07)."""

    tache_id: int
    chantier_id: int
    titre: str
    parent_id: Optional[int] = None
    template_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TacheUpdatedEvent:
    """Event emis lors de la mise a jour d'une tache."""

    tache_id: int
    chantier_id: int
    updated_fields: List[str] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class TacheDeletedEvent:
    """Event emis lors de la suppression d'une tache."""

    tache_id: int
    chantier_id: int
    titre: str
    deleted_at: datetime = field(default_factory=datetime.now)


@dataclass
class TacheTermineeEvent:
    """Event emis quand une tache est marquee terminee (TAC-13)."""

    tache_id: int
    chantier_id: int
    titre: str
    heures_realisees: float
    quantite_realisee: float
    completed_at: datetime = field(default_factory=datetime.now)


@dataclass
class SousTacheAddedEvent:
    """Event emis lors de l'ajout d'une sous-tache (TAC-02)."""

    sous_tache_id: int
    parent_id: int
    chantier_id: int
    titre: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FeuilleTacheCreatedEvent:
    """Event emis lors de la creation d'une feuille de tache (TAC-18)."""

    feuille_id: int
    tache_id: int
    utilisateur_id: int
    chantier_id: int
    heures_travaillees: float
    quantite_realisee: float
    date_travail: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FeuilleTacheValidatedEvent:
    """Event emis lors de la validation d'une feuille (TAC-19)."""

    feuille_id: int
    tache_id: int
    utilisateur_id: int
    validateur_id: int
    heures_travaillees: float
    validated_at: datetime = field(default_factory=datetime.now)


@dataclass
class FeuilleTacheRejectedEvent:
    """Event emis lors du rejet d'une feuille."""

    feuille_id: int
    tache_id: int
    utilisateur_id: int
    validateur_id: int
    motif: str
    rejected_at: datetime = field(default_factory=datetime.now)


@dataclass
class TachesImportedFromTemplateEvent:
    """Event emis lors de l'import d'un modele (TAC-05)."""

    template_id: int
    chantier_id: int
    taches_creees: List[int] = field(default_factory=list)
    imported_at: datetime = field(default_factory=datetime.now)
