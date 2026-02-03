"""Use Cases pour le tableau de bord financier.

FIN-11: Tableau de bord financier - Vue synthétique des KPI.

Formule de marge BTP :
    Marge = (Prix Vente - Coût Revient) / Prix Vente × 100

Où :
    - Prix Vente = situations de travaux facturées au client
    - Coût Revient = achats réalisés + coût MO + coûts fixes répartis

Coûts fixes société : 2 896 065 € / an (2024, 2025, 2026)
Répartition : au prorata du CA facturé (prix de vente)
"""

from decimal import Decimal
from typing import Optional

from ...domain.repositories import (
    BudgetRepository,
    LotBudgetaireRepository,
    AchatRepository,
    SituationRepository,
    CoutMainOeuvreRepository,
)
from ...domain.value_objects import StatutAchat
from ...domain.value_objects.statuts_financiers import STATUTS_ENGAGES, STATUTS_REALISES
from ..dtos.dashboard_dtos import (
    KPIFinancierDTO,
    DerniersAchatsDTO,
    RepartitionLotDTO,
    DashboardFinancierDTO,
)
from .budget_use_cases import BudgetNotFoundError

# Coûts fixes annuels de la société (frais généraux, administratifs, etc.)
# Note: Les 2 896 065 € initiaux incluent les salaires, déjà comptés dans le coût MO.
# Pour le calcul de marge BTP, on utilise uniquement les frais généraux hors salaires.
# Frais généraux BTP typiques : 10-15% du CA → ~600k€ pour CA de 4.3M€
COUTS_FIXES_ANNUELS = Decimal("600000")


class GetDashboardFinancierUseCase:
    """Use case pour construire le tableau de bord financier d'un chantier.

    FIN-11: Agrège les KPI, derniers achats et répartition par lot
    pour une vue synthétique de la santé financière d'un chantier.
    """

    def __init__(
        self,
        budget_repository: BudgetRepository,
        lot_repository: LotBudgetaireRepository,
        achat_repository: AchatRepository,
        situation_repository: SituationRepository = None,
        cout_mo_repository: CoutMainOeuvreRepository = None,
    ):
        self._budget_repository = budget_repository
        self._lot_repository = lot_repository
        self._achat_repository = achat_repository
        self._situation_repository = situation_repository
        self._cout_mo_repository = cout_mo_repository

    def execute(
        self, chantier_id: int, ca_total_annee: Optional[Decimal] = None
    ) -> DashboardFinancierDTO:
        """Construit le tableau de bord financier d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            ca_total_annee: CA total facturé sur l'année pour répartition des coûts fixes.
                Si None, les coûts fixes ne sont pas répartis.

        Returns:
            Le DTO du dashboard complet.

        Raises:
            BudgetNotFoundError: Si aucun budget pour ce chantier.
        """
        # Récupérer le budget
        budget = self._budget_repository.find_by_chantier_id(chantier_id)
        if not budget:
            raise BudgetNotFoundError(chantier_id=chantier_id)

        # Calculer les KPI
        montant_revise_ht = budget.montant_revise_ht

        total_engage = self._achat_repository.somme_by_chantier(
            chantier_id, statuts=STATUTS_ENGAGES
        )
        total_realise = self._achat_repository.somme_by_chantier(
            chantier_id, statuts=STATUTS_REALISES
        )
        reste_a_depenser = montant_revise_ht - total_engage

        # Pourcentages basés sur le budget
        if montant_revise_ht > Decimal("0"):
            pct_engage = (total_engage / montant_revise_ht) * Decimal("100")
            pct_realise = (total_realise / montant_revise_ht) * Decimal("100")
            pct_reste = (reste_a_depenser / montant_revise_ht) * Decimal("100")
        else:
            pct_engage = Decimal("0")
            pct_realise = Decimal("0")
            pct_reste = Decimal("0")

        # Calcul de la marge BTP : (Prix Vente - Coût Revient) / Prix Vente
        # Prix Vente = situations de travaux facturées au client
        # Coût Revient = achats réalisés + coût MO + coûts fixes répartis
        prix_vente_ht = Decimal("0")
        cout_mo = Decimal("0")
        marge_estimee: Optional[Decimal] = None
        marge_statut = "en_attente"

        if self._situation_repository:
            derniere_situation = self._situation_repository.find_derniere_situation(
                chantier_id
            )
            if derniere_situation:
                prix_vente_ht = Decimal(str(derniere_situation.montant_cumule_ht))

        if self._cout_mo_repository:
            cout_mo = self._cout_mo_repository.calculer_cout_chantier(chantier_id)

        # Calcul du coût de revient avec coûts fixes répartis au prorata du CA
        cout_revient = total_realise + cout_mo

        if prix_vente_ht > Decimal("0"):
            # Répartition des coûts fixes au prorata du CA
            if ca_total_annee and ca_total_annee > Decimal("0"):
                quote_part_couts_fixes = (
                    prix_vente_ht / ca_total_annee
                ) * COUTS_FIXES_ANNUELS
                cout_revient += quote_part_couts_fixes

            # Formule BTP correcte : marge sur prix de vente
            marge_estimee = (
                (prix_vente_ht - cout_revient) / prix_vente_ht
            ) * Decimal("100")
            marge_statut = "calculee"
        # Pas de fallback : si pas de situation, marge reste None et statut "en_attente"

        kpi = KPIFinancierDTO(
            montant_revise_ht=str(montant_revise_ht),
            total_engage=str(total_engage),
            total_realise=str(total_realise),
            marge_estimee=(
                str(marge_estimee.quantize(Decimal("0.01")))
                if marge_estimee is not None
                else None
            ),
            marge_statut=marge_statut,
            pct_engage=str(pct_engage.quantize(Decimal("0.01"))),
            pct_realise=str(pct_realise.quantize(Decimal("0.01"))),
            reste_a_depenser=str(reste_a_depenser),
            pct_reste=str(pct_reste.quantize(Decimal("0.01"))),
        )

        # Derniers achats (5)
        derniers = self._achat_repository.find_by_chantier(
            chantier_id=chantier_id,
            limit=5,
            offset=0,
        )
        derniers_achats = [
            DerniersAchatsDTO(
                id=a.id,
                libelle=a.libelle,
                fournisseur_nom=None,  # Enrichissement optionnel côté adapter
                total_ht=str(a.total_ht),
                statut=a.statut.value,
                statut_label=a.statut.label,
                statut_couleur=a.statut.couleur,
                created_at=a.created_at.isoformat() if a.created_at else None,
            )
            for a in derniers
        ]

        # Répartition par lot
        lots = self._lot_repository.find_by_budget_id(budget.id)
        repartition = []
        for lot in lots:
            lot_engage = self._achat_repository.somme_by_lot(
                lot.id, statuts=STATUTS_ENGAGES
            )
            lot_realise = self._achat_repository.somme_by_lot(
                lot.id, statuts=STATUTS_REALISES
            )
            ecart = lot.total_prevu_ht - lot_engage
            repartition.append(
                RepartitionLotDTO(
                    lot_id=lot.id,
                    code_lot=lot.code_lot,
                    libelle=lot.libelle,
                    total_prevu_ht=str(lot.total_prevu_ht),
                    engage=str(lot_engage),
                    realise=str(lot_realise),
                    ecart=str(ecart),
                )
            )

        return DashboardFinancierDTO(
            kpi=kpi,
            derniers_achats=derniers_achats,
            repartition_par_lot=repartition,
        )
