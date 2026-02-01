"""Use Cases pour le tableau de bord financier.

FIN-11: Tableau de bord financier - Vue synthétique des KPI.
"""

from decimal import Decimal
from typing import Optional

from ...domain.repositories import (
    BudgetRepository,
    LotBudgetaireRepository,
    AchatRepository,
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
    ):
        self._budget_repository = budget_repository
        self._lot_repository = lot_repository
        self._achat_repository = achat_repository

    def execute(self, chantier_id: int) -> DashboardFinancierDTO:
        """Construit le tableau de bord financier d'un chantier.

        Args:
            chantier_id: L'ID du chantier.

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

        # Pourcentages
        if montant_revise_ht > Decimal("0"):
            pct_engage = (total_engage / montant_revise_ht) * Decimal("100")
            pct_realise = (total_realise / montant_revise_ht) * Decimal("100")
            pct_reste = (reste_a_depenser / montant_revise_ht) * Decimal("100")
            marge_estimee = ((montant_revise_ht - total_engage) / montant_revise_ht) * Decimal("100")
        else:
            pct_engage = Decimal("0")
            pct_realise = Decimal("0")
            pct_reste = Decimal("0")
            marge_estimee = Decimal("0")

        kpi = KPIFinancierDTO(
            montant_revise_ht=str(montant_revise_ht),
            total_engage=str(total_engage),
            total_realise=str(total_realise),
            marge_estimee=str(marge_estimee.quantize(Decimal("0.01"))),
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
