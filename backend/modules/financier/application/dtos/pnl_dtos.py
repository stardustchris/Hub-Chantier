"""DTOs pour le Profit & Loss par chantier.

GAP #9: Vue P&L montrant CA, couts reels et marges par chantier.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class LignePnLDTO:
    """Ligne de detail du P&L.

    Attributes:
        categorie: Categorie de la ligne (achats, main_oeuvre, materiel, sous_traitance).
        libelle: Libelle descriptif.
        montant: Montant en string (Decimal serialise).
    """

    categorie: str
    libelle: str
    montant: str

    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return {
            "categorie": self.categorie,
            "libelle": self.libelle,
            "montant": self.montant,
        }


@dataclass
class PnLChantierDTO:
    """Profit & Loss complet d'un chantier.

    Attributes:
        chantier_id: ID du chantier.
        chiffre_affaires_ht: CA total (factures emises).
        total_couts: Total des couts reels.
        cout_achats: Achats factures HT.
        cout_main_oeuvre: Couts MO (pointages valides x taux horaire).
        cout_materiel: Couts materiel (reservations x tarif journalier).
        marge_brute_ht: CA - Couts.
        marge_brute_pct: Marge brute en %.
        budget_initial_ht: Budget initial pour reference.
        budget_revise_ht: Budget revise pour reference.
        detail_couts: Lignes de detail.
        est_definitif: True si le chantier est ferme.
    """

    chantier_id: int
    chiffre_affaires_ht: str
    total_couts: str
    cout_achats: str
    cout_main_oeuvre: str
    cout_materiel: str
    marge_brute_ht: str
    marge_brute_pct: str
    budget_initial_ht: str
    budget_revise_ht: str
    detail_couts: List[LignePnLDTO]
    est_definitif: bool = False

    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return {
            "chantier_id": self.chantier_id,
            "chiffre_affaires_ht": self.chiffre_affaires_ht,
            "total_couts": self.total_couts,
            "cout_achats": self.cout_achats,
            "cout_main_oeuvre": self.cout_main_oeuvre,
            "cout_materiel": self.cout_materiel,
            "marge_brute_ht": self.marge_brute_ht,
            "marge_brute_pct": self.marge_brute_pct,
            "budget_initial_ht": self.budget_initial_ht,
            "budget_revise_ht": self.budget_revise_ht,
            "detail_couts": [d.to_dict() for d in self.detail_couts],
            "est_definitif": self.est_definitif,
        }
