"""Use Cases pour la vue consolidee multi-chantiers.

FIN-20 Phase 3: Vue consolidee des finances pour la page /finances.
Agrege les KPI financiers de plusieurs chantiers.
"""

from decimal import Decimal
from typing import Dict, List, Optional

from shared.application.ports.chantier_info_port import ChantierInfoPort, ChantierInfoDTO

from ...domain.repositories import (
    BudgetRepository,
    LotBudgetaireRepository,
    AchatRepository,
    AlerteRepository,
    SituationRepository,
    CoutMainOeuvreRepository,
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
        _chantier_info_port: Port pour acceder aux noms des chantiers.
    """

    def __init__(
        self,
        budget_repository: BudgetRepository,
        lot_repository: LotBudgetaireRepository,
        achat_repository: AchatRepository,
        alerte_repository: AlerteRepository,
        chantier_info_port: Optional[ChantierInfoPort] = None,
        situation_repository: Optional[SituationRepository] = None,
        cout_mo_repository: Optional[CoutMainOeuvreRepository] = None,
    ) -> None:
        """Initialise le use case.

        Args:
            budget_repository: Repository Budget (interface).
            lot_repository: Repository LotBudgetaire (interface).
            achat_repository: Repository Achat (interface).
            alerte_repository: Repository Alerte (interface).
            chantier_info_port: Port pour les infos chantiers (optionnel).
            situation_repository: Repository Situation pour prix de vente (optionnel).
            cout_mo_repository: Repository Cout MO pour calcul marge BTP (optionnel).
        """
        self._budget_repository = budget_repository
        self._lot_repository = lot_repository
        self._achat_repository = achat_repository
        self._alerte_repository = alerte_repository
        self._chantier_info_port = chantier_info_port
        self._situation_repository = situation_repository
        self._cout_mo_repository = cout_mo_repository

    def execute(
        self,
        user_accessible_chantier_ids: List[int],
        statut_chantier: Optional[str] = None,
    ) -> VueConsolideeDTO:
        """Construit la vue consolidee multi-chantiers.

        Pour chaque chantier accessible, recupere le budget et calcule
        les KPI (meme logique que GetDashboardFinancierUseCase).
        Agrege les totaux globaux et classe les chantiers.

        Args:
            user_accessible_chantier_ids: Liste des IDs de chantiers
                accessibles par l'utilisateur.
            statut_chantier: Filtre optionnel par statut operationnel du
                chantier (ouvert, en_cours, receptionne, ferme). Si None,
                tous les chantiers sont inclus. Ignore si chantier_info_port
                n'est pas disponible.

        Returns:
            VueConsolideeDTO avec KPI globaux, liste chantiers,
            top 3 rentables et top 3 derives.
        """
        chantiers_summaries: List[ChantierFinancierSummaryDTO] = []

        # Recuperer les noms des chantiers via le port (si disponible)
        chantiers_info: Dict[int, ChantierInfoDTO] = {}
        if self._chantier_info_port is not None:
            chantiers_info = self._chantier_info_port.get_chantiers_info_batch(
                user_accessible_chantier_ids
            )

        # Filtrer par statut chantier si demande
        if statut_chantier and self._chantier_info_port:
            filtered_ids = [
                cid for cid in user_accessible_chantier_ids
                if cid in chantiers_info and chantiers_info[cid].statut == statut_chantier
            ]
        else:
            filtered_ids = user_accessible_chantier_ids

        # Totaux globaux
        total_budget_revise = Decimal("0")
        total_engage = Decimal("0")
        total_realise = Decimal("0")
        total_reste = Decimal("0")
        # Marge moyenne ponderee par prix de vente
        total_prix_vente = Decimal("0")
        somme_marges_ponderees = Decimal("0")

        nb_ok = 0
        nb_attention = 0
        nb_depassement = 0

        for chantier_id in filtered_ids:
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

            # Infos chantier pour determiner si ferme
            chantier_info = chantiers_info.get(chantier_id)
            is_ferme = chantier_info is not None and chantier_info.statut == "ferme"

            # Pourcentages bases sur le budget
            if montant_revise > Decimal("0"):
                pct_engage = (engage / montant_revise) * Decimal("100")
                pct_realise = (realise / montant_revise) * Decimal("100")
            else:
                pct_engage = Decimal("0")
                pct_realise = Decimal("0")

            # Calcul de la marge BTP : (Prix Vente - Cout Revient) / Prix Vente
            # Prix Vente = situations de travaux facturees au client
            # Cout Revient = achats realises + cout main d'oeuvre
            prix_vente_ht = Decimal("0")
            cout_mo = Decimal("0")

            if self._situation_repository:
                derniere_situation = self._situation_repository.find_derniere_situation(chantier_id)
                if derniere_situation:
                    prix_vente_ht = Decimal(str(derniere_situation.montant_cumule_ht))

            if self._cout_mo_repository:
                cout_mo = self._cout_mo_repository.calculer_cout_chantier(chantier_id)

            cout_revient = realise + cout_mo

            if prix_vente_ht > Decimal("0"):
                # Formule BTP correcte : marge sur prix de vente
                marge_pct = ((prix_vente_ht - cout_revient) / prix_vente_ht) * Decimal("100")
            elif montant_revise > Decimal("0"):
                # Fallback si pas de facturation : ancienne formule basee sur le budget
                if is_ferme:
                    marge_pct = ((montant_revise - realise) / montant_revise) * Decimal("100")
                else:
                    marge_pct = ((montant_revise - engage) / montant_revise) * Decimal("100")
            else:
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

            # Nom et statut chantier : utiliser le port si disponible, sinon fallback
            nom_chantier = chantier_info.nom if chantier_info is not None else f"Chantier {chantier_id}"
            statut_ch = chantier_info.statut if chantier_info is not None else ""

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
                statut_chantier=statut_ch,
            )
            chantiers_summaries.append(summary)

            # Cumuler pour globaux
            total_budget_revise += montant_revise
            total_engage += engage
            total_realise += realise
            total_reste += reste

            # Pour marge moyenne ponderee par prix de vente
            # Utiliser prix_vente si disponible, sinon le budget
            poids = prix_vente_ht if prix_vente_ht > Decimal("0") else montant_revise
            total_prix_vente += poids
            somme_marges_ponderees += marge_pct * poids

        # Marge moyenne ponderee par prix de vente (ou budget si pas de situation)
        nb_chantiers = len(chantiers_summaries)
        marge_moyenne = (
            somme_marges_ponderees / total_prix_vente
            if total_prix_vente > Decimal("0")
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
