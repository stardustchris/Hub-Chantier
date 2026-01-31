"""Domain Event pour le verrouillage de période de paie (GAP-FDH-009)."""

from dataclasses import dataclass, field
from datetime import datetime, date


@dataclass(frozen=True)
class PeriodePaieLockedEvent:
    """
    Événement émis lors du verrouillage d'une période de paie.

    Cet événement est publié lorsqu'une période de paie mensuelle est
    automatiquement verrouillée (le dernier vendredi avant la dernière
    semaine du mois à 23:59).

    Il permet aux autres modules (notifications, dashboard, export paie)
    de réagir à ce verrouillage.

    Attributes:
        year: Année de la période verrouillée.
        month: Mois de la période verrouillée (1-12).
        lockdown_date: Date de verrouillage effective.
        auto_locked: True si verrouillage automatique (scheduler).
        locked_by: ID de l'utilisateur ayant déclenché le verrouillage (None si auto).
        timestamp: Moment de l'événement.
    """

    year: int
    month: int
    lockdown_date: date
    auto_locked: bool = True
    locked_by: int | None = None
    timestamp: datetime = field(default_factory=datetime.now)
