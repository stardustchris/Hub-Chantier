"""Use Cases pour la vue consolidee multi-chantiers.

FIN-20 Phase 3: Vue consolidee des finances pour la page /finances.
Agrege les KPI financiers de plusieurs chantiers.
"""

from decimal import Decimal
from typing import List

from ...domain.repositories import (
    BudgetRepository,
    LotBudgetaireRepository,
    AchatRepository,
    AlerteRepository,
)
from ...domain.value_objects.statuts_financiers import STATUTS_ENGAGES, STATUTS_REALISES
from ..dtos.consolidation_dtos import (
    ChantierFinancierSummaryDTO,
    KPIGlobauxDTO,
    VueConsolideeDTO,
)


class GetVueConsolideeFinancesUseCase:
    """Use case pour construire la vue consolidee multi-chantiers.

    FIN-20: Agrege les KPI financiers de tous les chantiers accessibles
    par l'utilisateur, calcule les totaux globaux, et identifie les
    top 3 rentables / top 3 derives.

    Attributes:
        _budget_repository: Repository pour acceder aux budgets.
        _lot_repository: Repository pour acceder aux lots budgetaires.
        _achat_repository: Repository pour acceder aux achats.
        _alerte_repository: Repository pour acceder aux alertes.
    """

    def __init__(
        self,
        budget_repository: BudgetRepository,
        lot_repository: LotBudgetaireRepository,
        achat_repository: AchatRepository,
        alerte_repository: AlerteRepository,
    ) -> None:
        """Initialise le use case.

        Args:
            budget_repository: Repository Budget (interface).
            lot_repository: Repository LotBudgetaire (interface).
            achat_repository: Repository Achat (interface).
            alerte_repository: Repository Alerte (interface).
        """
        self._budget_repository = budget_repository
        self._lot_repository = lot_repository
        self._achat_repository = achat_repository
        self._alerte_repository = alerte_repository

    def execute(
        self, user_accessible_chantier_ids: List[int]
    ) -> VueConsolideeDTO:
        """Construit la vue consolidee multi-chantiers.

        Pour chaque chantier accessible, recupere le budget et calcule
        les KPI (meme logique que GetDashboardFinancierUseCase).
        Agrege les totaux globaux et classe les chantiers.

        Args:
            user_accessible_chantier_ids: Liste des IDs de chantiers
                accessibles par l'utilisateur.

        Returns:
            VueConsolideeDTO avec KPI globaux, liste chantiers,
            top 3 rentables et top 3 derives.
        """
        chantiers_summaries: List[ChantierFinancierSummaryDTO] = []

        # Totaux globaux
        total_budget_revise = Decimal("0")
        total_engage = Decimal("0")
        total_realise = Decimal("0")
        total_reste = Decimal("0")
        somme_marges_pct = Decimal("0")

        nb_ok = 0
        nb_attention = 0
        nb_depassement = 0

        for chantier_id in user_accessible_chantier_ids:
            budget = self._budget_repository.find_by_chantier_id(chantier_id)
            if not budget:
                # Chantier sans budget, on l'ignore
                continue

            montant_revise = budget.montant_revise_ht

            engage = self._achat_repository.somme_by_chantier(
                chantier_id, statuts=STATUTS_ENGAGES
            )
            realise = self._achat_repository.somme_by_chantier(
                chantier_id, statuts=STATUTS_REALISES
            )
            reste = montant_revise - engage

            # Pourcentages
            if montant_revise > Decimal("0"):
                pct_engage = (engage / montant_revise) * Decimal("100")
                pct_realise = (realise / montant_revise) * Decimal("100")
                marge_pct = ((montant_revise - engage) / montant_revise) * Decimal("100")
            else:
                pct_engage = Decimal("0")
                pct_realise = Decimal("0")
                marge_pct = Decimal("0")

            # Classification
            if pct_engage > Decimal("100"):
                statut = "depassement"
                nb_depassement += 1
            elif pct_engage >= Decimal("80"):
                statut = "attention"
                nb_attention += 1
            else:
                statut = "ok"
                nb_ok += 1

            # Alertes non acquittees
            alertes = self._alerte_repository.find_non_acquittees(chantier_id)
            nb_alertes = len(alertes)

            # Nom chantier : on utilise l'ID comme fallback
            nom_chantier = f"Chantier {chantier_id}"

            summary = ChantierFinancierSummaryDTO(
                chantier_id=chantier_id,
                nom_chantier=nom_chantier,
                montant_revise_ht=str(montant_revise.quantize(Decimal("0.01"))),
                total_engage=str(engage.quantize(Decimal("0.01"))),
                total_realise=str(realise.quantize(Decimal("0.01"))),
                reste_a_depenser=str(reste.quantize(Decimal("0.01"))),
                marge_estimee_pct=str(marge_pct.quantize(Decimal("0.01"))),
                pct_engage=str(pct_engage.quantize(Decimal("0.01"))),
                pct_realise=str(pct_realise.quantize(Decimal("0.01"))),
                statut=statut,
                nb_alertes=nb_alertes,
            )
            chantiers_summaries.append(summary)

            # Cumuler pour globaux
            total_budget_revise += montant_revise
            total_engage += engage
            total_realise += realise
            total_reste += reste
            somme_marges_pct += marge_pct

        # Marge moyenne
        nb_chantiers = len(chantiers_summaries)
        marge_moyenne = (
            somme_marges_pct / Decimal(str(nb_chantiers))
            if nb_chantiers > 0
            else Decimal("0")
        )

        kpi_globaux = KPIGlobauxDTO(
            total_budget_revise=str(total_budget_revise.quantize(Decimal("0.01"))),
            total_engage=str(total_engage.quantize(Decimal("0.01"))),
            total_realise=str(total_realise.quantize(Decimal("0.01"))),
            total_reste_a_depenser=str(total_reste.quantize(Decimal("0.01"))),
            marge_moyenne_pct=str(marge_moyenne.quantize(Decimal("0.01"))),
            nb_chantiers=nb_chantiers,
            nb_chantiers_ok=nb_ok,
            nb_chantiers_attention=nb_attention,
            nb_chantiers_depassement=nb_depassement,
        )

        # Top 3 rentables (marge_estimee_pct desc)
        top_rentables = sorted(
            chantiers_summaries,
            key=lambda c: Decimal(c.marge_estimee_pct),
            reverse=True,
        )[:3]

        # Top 3 derives (pct_engage desc - les plus en depassement)
        top_derives = sorted(
            chantiers_summaries,
            key=lambda c: Decimal(c.pct_engage),
            reverse=True,
        )[:3]

        return VueConsolideeDTO(
            kpi_globaux=kpi_globaux,
            chantiers=chantiers_summaries,
            top_rentables=top_rentables,
            top_derives=top_derives,
        )
