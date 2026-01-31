"""Value Object pour le type d'alerte de dépassement budgétaire.

FIN-12: Alertes dépassement budget.
"""

import enum


class TypeAlerte(str, enum.Enum):
    """Types d'alertes de dépassement budgétaire."""

    SEUIL_ENGAGE = "seuil_engage"
    SEUIL_REALISE = "seuil_realise"
    DEPASSEMENT_LOT = "depassement_lot"
