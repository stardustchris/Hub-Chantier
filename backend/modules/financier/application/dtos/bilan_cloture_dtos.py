"""DTOs pour le bilan de cloture d'un chantier.

GAP #10: Bilan de cloture - Rapport recapitulatif financier
lorsqu'un chantier est ferme ou en cours de cloture.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EcartLotDTO:
    """Ecart prevu/realise par lot budgetaire.

    Attributes:
        code_lot: Code du lot.
        libelle: Libelle du lot.
        prevu_ht: Montant prevu HT.
        realise_ht: Montant realise HT.
        ecart_ht: Ecart en valeur absolue (prevu - realise).
        ecart_pct: Ecart en pourcentage.
    """

    code_lot: str
    libelle: str
    prevu_ht: str
    realise_ht: str
    ecart_ht: str
    ecart_pct: str

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "code_lot": self.code_lot,
            "libelle": self.libelle,
            "prevu_ht": self.prevu_ht,
            "realise_ht": self.realise_ht,
            "ecart_ht": self.ecart_ht,
            "ecart_pct": self.ecart_pct,
        }


@dataclass
class BilanClotureDTO:
    """Bilan de cloture complet d'un chantier.

    Aggrege toutes les informations financieres finales
    d'un chantier pour produire un rapport recapitulatif.

    Attributes:
        chantier_id: ID du chantier.
        nom_chantier: Nom du chantier.
        statut_chantier: Statut actuel (devrait etre ferme pour un bilan definitif).
        budget_initial_ht: Budget initial HT.
        budget_revise_ht: Budget revise (initial + avenants valides).
        montant_avenants_ht: Total des avenants valides.
        nb_avenants: Nombre d'avenants (tous statuts).
        total_engage_ht: Total engage (somme des achats).
        total_realise_ht: Total realise (achats livres ou factures).
        reste_non_depense_ht: Reste non depense = budget_revise - total_engage.
        marge_finale_ht: Marge finale = budget_revise - total_realise.
        marge_finale_pct: Marge finale en pourcentage du budget revise.
        nb_achats: Nombre total d'achats.
        nb_situations: Nombre de situations emises.
        ecarts_par_lot: Detail des ecarts prevu/realise par lot budgetaire.
        devis_source_id: ID du devis source si conversion devis->chantier.
        est_definitif: True si le chantier est ferme (bilan final).
    """

    chantier_id: int
    nom_chantier: str
    statut_chantier: str
    budget_initial_ht: str
    budget_revise_ht: str
    montant_avenants_ht: str
    nb_avenants: int
    total_engage_ht: str
    total_realise_ht: str
    reste_non_depense_ht: str
    marge_finale_ht: str
    marge_finale_pct: Optional[str]
    nb_achats: int
    nb_situations: int
    ecarts_par_lot: List[EcartLotDTO] = field(default_factory=list)
    devis_source_id: Optional[int] = None
    est_definitif: bool = False

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "chantier_id": self.chantier_id,
            "nom_chantier": self.nom_chantier,
            "statut_chantier": self.statut_chantier,
            "budget_initial_ht": self.budget_initial_ht,
            "budget_revise_ht": self.budget_revise_ht,
            "montant_avenants_ht": self.montant_avenants_ht,
            "nb_avenants": self.nb_avenants,
            "total_engage_ht": self.total_engage_ht,
            "total_realise_ht": self.total_realise_ht,
            "reste_non_depense_ht": self.reste_non_depense_ht,
            "marge_finale_ht": self.marge_finale_ht,
            "marge_finale_pct": self.marge_finale_pct,
            "nb_achats": self.nb_achats,
            "nb_situations": self.nb_situations,
            "ecarts_par_lot": [e.to_dict() for e in self.ecarts_par_lot],
            "devis_source_id": self.devis_source_id,
            "est_definitif": self.est_definitif,
        }
