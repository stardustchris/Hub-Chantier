"""DTOs pour le verrouillage de période de paie (GAP-FDH-009)."""

from dataclasses import dataclass
from datetime import date
from typing import List


@dataclass
class LockMonthlyPeriodDTO:
    """
    DTO pour le verrouillage d'une période de paie.

    Attributes:
        year: Année.
        month: Mois (1-12).
    """

    year: int
    month: int


@dataclass
class LockMonthlyPeriodResultDTO:
    """
    Résultat du verrouillage d'une période de paie.

    Attributes:
        year: Année verrouillée.
        month: Mois verrouillé.
        lockdown_date: Date de verrouillage appliquée.
        success: True si le verrouillage a réussi.
        message: Message descriptif du résultat.
        notified_users: Liste des IDs utilisateurs notifiés.
    """

    year: int
    month: int
    lockdown_date: date
    success: bool
    message: str
    notified_users: List[int]
