"""DTOs pour l'export comptable.

FIN-13: Export comptable CSV/Excel.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ExportLigneComptableDTO:
    """DTO pour une ligne d'ecriture comptable.

    Chaque ligne correspond a une ecriture dans le journal comptable
    (debit ou credit).
    """

    date: str  # YYYY-MM-DD
    code_journal: str  # "HA" (achats), "VE" (ventes/factures), "OD" (operations diverses)
    numero_piece: str  # numero facture ou reference
    code_analytique: str  # code chantier
    libelle: str
    compte_general: str  # ex: "601000" (achats materiaux), "706000" (ventes)
    debit: str  # montant en Decimal -> str avec 2 decimales
    credit: str  # montant en Decimal -> str avec 2 decimales
    tva_code: str  # "20", "10", "5.5", "0"

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "date": self.date,
            "code_journal": self.code_journal,
            "numero_piece": self.numero_piece,
            "code_analytique": self.code_analytique,
            "libelle": self.libelle,
            "compte_general": self.compte_general,
            "debit": self.debit,
            "credit": self.credit,
            "tva_code": self.tva_code,
        }


@dataclass
class ExportComptableDTO:
    """DTO pour un export comptable complet."""

    chantier_id: Optional[int]
    date_debut: str
    date_fin: str
    lignes: List[ExportLigneComptableDTO] = field(default_factory=list)
    total_debit: str = "0.00"
    total_credit: str = "0.00"
    nombre_lignes: int = 0

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "chantier_id": self.chantier_id,
            "date_debut": self.date_debut,
            "date_fin": self.date_fin,
            "lignes": [l.to_dict() for l in self.lignes],
            "total_debit": self.total_debit,
            "total_credit": self.total_credit,
            "nombre_lignes": self.nombre_lignes,
        }
