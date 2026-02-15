"""DTOs pour l'import DPGF (Decomposition Prix Global Forfaitaire).

DEV-21: Import automatique de fichiers DPGF Excel/CSV.
Mapping colonnes: lot, description, unite, quantite, PU.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional


@dataclass
class LigneDPGFDTO:
    """DTO pour une ligne lue depuis un fichier DPGF.

    Attributes:
        lot: Code ou numero du lot.
        description: Designation de la ligne.
        unite: Unite de mesure (U, m2, ml, m3, kg, h, forfait...).
        quantite: Quantite.
        prix_unitaire: Prix unitaire HT.
    """

    lot: str
    description: str
    unite: str = "U"
    quantite: Decimal = Decimal("0")
    prix_unitaire: Decimal = Decimal("0")


@dataclass
class ImportDPGFResultDTO:
    """DTO resultat d'un import DPGF.

    Attributes:
        devis_id: ID du devis cible.
        lots_crees: Nombre de lots crees.
        lignes_creees: Nombre de lignes creees.
        lignes_ignorees: Nombre de lignes ignorees (erreurs de parsing).
        erreurs: Liste des erreurs de parsing (ligne, message).
        lots: Details des lots crees avec leurs lignes.
    """

    devis_id: int
    lots_crees: int = 0
    lignes_creees: int = 0
    lignes_ignorees: int = 0
    erreurs: List[dict] = field(default_factory=list)
    lots: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "devis_id": self.devis_id,
            "lots_crees": self.lots_crees,
            "lignes_creees": self.lignes_creees,
            "lignes_ignorees": self.lignes_ignorees,
            "erreurs": self.erreurs,
            "lots": self.lots,
        }


@dataclass
class DPGFColumnMappingDTO:
    """DTO pour le mapping des colonnes du fichier DPGF.

    Permet au front de specifier quelles colonnes correspondent a quoi
    quand le format du fichier ne suit pas la convention standard.

    Attributes:
        col_lot: Index ou nom de la colonne lot (defaut: 0 / "lot").
        col_description: Index ou nom de la colonne description (defaut: 1 / "description").
        col_unite: Index ou nom de la colonne unite (defaut: 2 / "unite").
        col_quantite: Index ou nom de la colonne quantite (defaut: 3 / "quantite").
        col_prix_unitaire: Index ou nom de la colonne PU (defaut: 4 / "pu").
        ligne_debut: Premiere ligne de donnees (0-indexed, defaut: 1 = skip header).
        feuille: Nom ou index de la feuille Excel (defaut: 0 = premiere).
    """

    col_lot: int = 0
    col_description: int = 1
    col_unite: int = 2
    col_quantite: int = 3
    col_prix_unitaire: int = 4
    ligne_debut: int = 1
    feuille: int = 0
