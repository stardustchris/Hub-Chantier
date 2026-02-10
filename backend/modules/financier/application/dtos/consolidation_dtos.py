"""DTOs pour la vue consolidee multi-chantiers.

FIN-20 Phase 3: Vue consolidee des finances pour la page /finances.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ChantierFinancierSummaryDTO:
    """Resume financier d'un chantier dans la vue consolidee.

    Attributes:
        chantier_id: Identifiant du chantier.
        nom_chantier: Nom du chantier.
        montant_revise_ht: Budget revise HT (Decimal->str).
        total_engage: Total engage (Decimal->str).
        total_realise: Total realise (Decimal->str).
        reste_a_depenser: Reste a depenser (Decimal->str).
        marge_estimee_pct: Marge estimee en pourcentage (None si en attente).
        marge_statut: 'calculee' ou 'en_attente' selon disponibilite situation.
        fiabilite_marge: Score de fiabilite de la marge (0-100%).
        pct_engage: Pourcentage engage (Decimal->str).
        pct_realise: Pourcentage realise (Decimal->str).
        statut: Statut financier du chantier ('ok' | 'attention' | 'depassement').
        nb_alertes: Nombre d'alertes non acquittees.
        statut_chantier: Statut operationnel du chantier
            ('ouvert' | 'en_cours' | 'receptionne' | 'ferme', vide si inconnu).
    """

    chantier_id: int
    nom_chantier: str
    montant_revise_ht: str
    total_engage: str
    total_realise: str
    reste_a_depenser: str
    marge_estimee_pct: Optional[str]  # None si pas de situation
    marge_statut: str  # "calculee" ou "en_attente"
    fiabilite_marge: int = 0  # Score 0-100%
    pct_engage: str = ""
    pct_realise: str = ""
    statut: str = ""
    nb_alertes: int = 0
    statut_chantier: str = ""

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "chantier_id": self.chantier_id,
            "nom_chantier": self.nom_chantier,
            "montant_revise_ht": self.montant_revise_ht,
            "total_engage": self.total_engage,
            "total_realise": self.total_realise,
            "reste_a_depenser": self.reste_a_depenser,
            "marge_estimee_pct": self.marge_estimee_pct,
            "marge_statut": self.marge_statut,
            "fiabilite_marge": self.fiabilite_marge,
            "pct_engage": self.pct_engage,
            "pct_realise": self.pct_realise,
            "statut": self.statut,
            "nb_alertes": self.nb_alertes,
            "statut_chantier": self.statut_chantier,
        }


@dataclass
class KPIGlobauxDTO:
    """KPI globaux agreges de tous les chantiers.

    Attributes:
        total_budget_revise: Somme des budgets revises (Decimal->str).
        total_engage: Somme des engages (Decimal->str).
        total_realise: Somme des realises (Decimal->str).
        total_reste_a_depenser: Somme des restes a depenser (Decimal->str).
        marge_moyenne_pct: Marge moyenne en pourcentage (None si aucune marge calculable).
        marge_statut: 'calculee', 'partielle' ou 'en_attente'.
        nb_chantiers: Nombre total de chantiers.
        nb_chantiers_ok: Nombre de chantiers en statut 'ok'.
        nb_chantiers_attention: Nombre de chantiers en statut 'attention'.
        nb_chantiers_depassement: Nombre de chantiers en statut 'depassement'.
        nb_chantiers_marge_en_attente: Nombre de chantiers sans marge calculable.
    """

    total_budget_revise: str
    total_engage: str
    total_realise: str
    total_reste_a_depenser: str
    marge_moyenne_pct: Optional[str]  # None si aucune situation
    marge_statut: str  # "calculee", "partielle", "en_attente"
    nb_chantiers: int
    nb_chantiers_ok: int
    nb_chantiers_attention: int
    nb_chantiers_depassement: int
    nb_chantiers_marge_en_attente: int = 0

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "total_budget_revise": self.total_budget_revise,
            "total_engage": self.total_engage,
            "total_realise": self.total_realise,
            "total_reste_a_depenser": self.total_reste_a_depenser,
            "marge_moyenne_pct": self.marge_moyenne_pct,
            "marge_statut": self.marge_statut,
            "nb_chantiers": self.nb_chantiers,
            "nb_chantiers_ok": self.nb_chantiers_ok,
            "nb_chantiers_attention": self.nb_chantiers_attention,
            "nb_chantiers_depassement": self.nb_chantiers_depassement,
            "nb_chantiers_marge_en_attente": self.nb_chantiers_marge_en_attente,
        }


@dataclass
class VueConsolideeDTO:
    """DTO principal de la vue consolidee multi-chantiers.

    FIN-20: Agrege les KPI globaux, la liste des chantiers,
    et les top 3 rentables / top 3 derives.

    Attributes:
        kpi_globaux: KPI agreges de tous les chantiers.
        chantiers: Liste des resumes financiers par chantier.
        top_rentables: Top 3 chantiers les plus rentables (marge desc).
        top_derives: Top 3 chantiers les plus en depassement (pct_engage desc).
    """

    kpi_globaux: KPIGlobauxDTO
    chantiers: List[ChantierFinancierSummaryDTO]
    top_rentables: List[ChantierFinancierSummaryDTO]
    top_derives: List[ChantierFinancierSummaryDTO]

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "kpi_globaux": self.kpi_globaux.to_dict(),
            "chantiers": [c.to_dict() for c in self.chantiers],
            "top_rentables": [c.to_dict() for c in self.top_rentables],
            "top_derives": [c.to_dict() for c in self.top_derives],
        }
