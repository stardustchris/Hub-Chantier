"""Value Object pour le type de facture client.

FIN-08: Factures client - types de facturation.
"""

import enum


class TypeFacture(str, enum.Enum):
    """Types de factures client."""

    ACOMPTE = "acompte"
    SITUATION = "situation"
    SOLDE = "solde"
