"""DTOs pour l'export comptable.

FIN-13: Export comptable - DTOs pour CSV et Excel.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class LigneExportComptableDTO:
    """DTO representant une ligne d'export comptable."""

    date: str  # ISO format
    type_document: str  # "achat", "situation", "facture", "avenant"
    numero: str
    tiers: str  # Nom fournisseur ou "Greg Construction"
    montant_ht: str  # Decimal converti en str
    montant_tva: str
    montant_ttc: str
    code_analytique: str  # "CHANT-{id}-LOT-{code_lot}"
    libelle: str
    reference_chantier: str
    statut: str

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "date": self.date,
            "type_document": self.type_document,
            "numero": self.numero,
            "tiers": self.tiers,
            "montant_ht": self.montant_ht,
            "montant_tva": self.montant_tva,
            "montant_ttc": self.montant_ttc,
            "code_analytique": self.code_analytique,
            "libelle": self.libelle,
            "reference_chantier": self.reference_chantier,
            "statut": self.statut,
        }


@dataclass
class ExportComptableDTO:
    """DTO representant un export comptable complet."""

    chantier_id: int
    nom_chantier: str
    date_export: str  # ISO format
    lignes: List[LigneExportComptableDTO] = field(default_factory=list)
    totaux: dict = field(default_factory=dict)  # total_ht, total_tva, total_ttc

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "chantier_id": self.chantier_id,
            "nom_chantier": self.nom_chantier,
            "date_export": self.date_export,
            "lignes": [ligne.to_dict() for ligne in self.lignes],
            "totaux": self.totaux,
            "nombre_lignes": len(self.lignes),
        }
