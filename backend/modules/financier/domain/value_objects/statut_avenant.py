"""Value Object pour le statut d'un avenant budgétaire.

FIN-04: Avenants budgétaires - brouillon ou validé.
"""

import enum


class StatutAvenant(str, enum.Enum):
    """Statuts possibles d'un avenant budgétaire.

    Workflow:
        brouillon -> valide
        valide -> (terminal)
    """

    BROUILLON = "brouillon"
    VALIDE = "valide"
