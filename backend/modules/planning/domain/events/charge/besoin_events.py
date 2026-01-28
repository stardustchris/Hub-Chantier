"""Evenements domaine lies aux besoins de charge."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class BesoinChargeCreated:
    """
    Evenement emis lors de la creation d'un besoin de charge.

    Selon CDC Section 6 - Planning de Charge.
    """

    besoin_id: int
    chantier_id: int
    semaine_code: str
    type_metier: str
    besoin_heures: float
    created_by: int
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def event_type(self) -> str:
        """Retourne le type d'evenement."""
        return "besoin_charge.created"


@dataclass(frozen=True)
class BesoinChargeUpdated:
    """
    Evenement emis lors de la mise a jour d'un besoin de charge.
    """

    besoin_id: int
    chantier_id: int
    semaine_code: str
    type_metier: str
    ancien_besoin_heures: float
    nouveau_besoin_heures: float
    updated_by: int
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def event_type(self) -> str:
        """Retourne le type d'evenement."""
        return "besoin_charge.updated"

    @property
    def difference_heures(self) -> float:
        """Retourne la difference d'heures."""
        return self.nouveau_besoin_heures - self.ancien_besoin_heures


@dataclass(frozen=True)
class BesoinChargeDeleted:
    """
    Evenement emis lors de la suppression d'un besoin de charge.
    """

    besoin_id: int
    chantier_id: int
    semaine_code: str
    type_metier: str
    besoin_heures: float
    deleted_by: int
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def event_type(self) -> str:
        """Retourne le type d'evenement."""
        return "besoin_charge.deleted"
