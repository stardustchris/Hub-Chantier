"""Value Object pour le statut d'une facture client.

FIN-08: Factures client - workflow de facturation.
"""

import enum


class StatutFacture(str, enum.Enum):
    """Statuts possibles d'une facture client.

    Workflow:
        brouillon -> emise -> envoyee -> payee
        brouillon -> annulee
        emise -> annulee
    """

    BROUILLON = "brouillon"
    EMISE = "emise"
    ENVOYEE = "envoyee"
    PAYEE = "payee"
    ANNULEE = "annulee"
