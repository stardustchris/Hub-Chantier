"""Use Cases pour le tableau de bord financier.

FIN-11: Tableau de bord financier - Vue synthétique des KPI.

Formule de marge BTP :
    Marge = (Prix Vente - Coût Revient) / Prix Vente × 100

Où :
    - Prix Vente = situations de travaux facturées au client
    - Coût Revient = achats réalisés + coût MO + coûts fixes répartis

Coûts fixes société : 600 000 € / an (frais généraux hors salaires)
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
    CoutMaterielRepository,
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
from shared.domain.calcul_financier import (
    calculer_marge_chantier,
    calculer_quote_part_frais_generaux,
    arrondir_pct,
    arrondir_montant,
)

# Coûts fixes annuels de la société (frais généraux hors salaires).
# Frais généraux BTP typiques : 10-15% du CA -> ~600k EUR pour CA de 4.3M EUR
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
        cout_materiel_repository: CoutMaterielRepository = None,
    ):
        self._budget_repository = budget_repository
        self._lot_repository = lot_repository
        self._achat_repository = achat_repository
        self._situation_repository = situation_repository
        self._cout_mo_repository = cout_mo_repository
        self._cout_materiel_repository = cout_materiel_repository

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

        # Couts MO et materiel (pour total realise COMPLET)
        cout_mo = Decimal("0")
        cout_materiel = Decimal("0")
        if self._cout_mo_repository:
            try:
                cout_mo = self._cout_mo_repository.calculer_cout_chantier(chantier_id)
            except Exception:
                pass
        if self._cout_materiel_repository:
            try:
                cout_materiel = self._cout_materiel_repository.calculer_cout_chantier(chantier_id)
            except Exception:
                pass

        # Total realise COMPLET = achats factures + MO + materiel
        total_realise_complet = total_realise + cout_mo + cout_materiel

        # Pourcentages basés sur le budget
        if montant_revise_ht > Decimal("0"):
            pct_engage = (total_engage / montant_revise_ht) * Decimal("100")
            pct_realise = (total_realise_complet / montant_revise_ht) * Decimal("100")
            pct_reste = (reste_a_depenser / montant_revise_ht) * Decimal("100")
        else:
            pct_engage = Decimal("0")
            pct_realise = Decimal("0")
            pct_reste = Decimal("0")

        # Calcul de la marge BTP unifiee via formule partagee
        # Prix Vente = situations de travaux facturees au client
        prix_vente_ht = Decimal("0")
        marge_estimee: Optional[Decimal] = None
        marge_statut = "en_attente"

        if self._situation_repository:
            derniere_situation = self._situation_repository.find_derniere_situation(
                chantier_id
            )
            if derniere_situation:
                prix_vente_ht = Decimal(str(derniere_situation.montant_cumule_ht))

        if prix_vente_ht > Decimal("0"):
            # Quote-part frais generaux via fonction unifiee
            quote_part = calculer_quote_part_frais_generaux(
                ca_chantier_ht=prix_vente_ht,
                ca_total_annee=ca_total_annee or Decimal("0"),
                couts_fixes_annuels=COUTS_FIXES_ANNUELS,
            )

            # Marge BTP unifiee (formule partagee avec P&L et bilan)
            marge_estimee = calculer_marge_chantier(
                ca_ht=prix_vente_ht,
                cout_achats=total_realise,
                cout_mo=cout_mo,
                cout_materiel=cout_materiel,
                quote_part_frais_generaux=quote_part,
            )
            marge_statut = "calculee"

        kpi = KPIFinancierDTO(
            montant_revise_ht=str(montant_revise_ht),
            total_engage=str(total_engage),
            total_realise=str(total_realise_complet),
            marge_estimee=(
                str(marge_estimee)
                if marge_estimee is not None
                else None
            ),
            marge_statut=marge_statut,
            pct_engage=str(arrondir_pct(pct_engage)),
            pct_realise=str(arrondir_pct(pct_realise)),
            reste_a_depenser=str(reste_a_depenser),
            pct_reste=str(arrondir_pct(pct_reste)),
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
