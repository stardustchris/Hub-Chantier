"""Value Object pour le statut d'une situation de travaux.

FIN-07: Situations de travaux - workflow de validation.
"""

import enum


class StatutSituation(str, enum.Enum):
    """Statuts possibles d'une situation de travaux.

    Workflow:
        brouillon -> en_validation -> emise -> validee -> facturee
    """

    BROUILLON = "brouillon"
    EN_VALIDATION = "en_validation"
    EMISE = "emise"
    VALIDEE = "validee"
    FACTUREE = "facturee"
