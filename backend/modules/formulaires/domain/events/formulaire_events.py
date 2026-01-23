"""Domain Events pour le module Formulaires."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class TemplateCreatedEvent:
    """Evenement emis lors de la creation d'un template."""

    template_id: int
    nom: str
    categorie: str
    created_by: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TemplateUpdatedEvent:
    """Evenement emis lors de la mise a jour d'un template."""

    template_id: int
    nom: str
    version: int
    updated_by: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TemplateDeletedEvent:
    """Evenement emis lors de la suppression d'un template."""

    template_id: int
    nom: str
    deleted_by: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FormulaireCreatedEvent:
    """Evenement emis lors de la creation d'un formulaire (FOR-11)."""

    formulaire_id: int
    template_id: int
    chantier_id: int
    user_id: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FormulaireSubmittedEvent:
    """Evenement emis lors de la soumission d'un formulaire (FOR-07)."""

    formulaire_id: int
    template_id: int
    chantier_id: int
    user_id: int
    soumis_at: datetime = field(default_factory=datetime.now)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FormulaireValidatedEvent:
    """Evenement emis lors de la validation d'un formulaire."""

    formulaire_id: int
    template_id: int
    chantier_id: int
    valide_by: int
    valide_at: datetime = field(default_factory=datetime.now)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FormulaireSignedEvent:
    """Evenement emis lors de la signature d'un formulaire (FOR-05)."""

    formulaire_id: int
    signature_nom: str
    signature_timestamp: datetime = field(default_factory=datetime.now)
    timestamp: datetime = field(default_factory=datetime.now)
