"""Use Cases pour la vue consolidee multi-chantiers.

FIN-20 Phase 3: Vue consolidee des finances pour la page /finances.
Agrege les KPI financiers de plusieurs chantiers.

Formule de marge BTP :
    Marge = (Prix Vente - Coût Revient) / Prix Vente × 100

Où :
    - Prix Vente = situations de travaux facturées au client
    - Coût Revient = achats réalisés + coût MO + coûts fixes répartis

Coûts fixes société : 2 896 065 € / an (2024, 2025, 2026)
Répartition : au prorata du CA facturé (prix de vente)
"""

from decimal import Decimal
from typing import Dict, List, Optional

# Coûts fixes annuels de la société (frais généraux, administratifs, etc.)
# Note: 2 896 065 € = charges totales incluant salaires
# Pour le calcul de marge, on utilise uniquement les frais généraux hors salaires
# qui sont déjà comptés dans le coût MO des pointages.
# Frais généraux BTP typiques : 10-15% du CA → ~600k€ pour CA de 4.3M€
COUTS_FIXES_ANNUELS = Decimal("600000")

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
        ca_total_entreprise: Optional[Decimal] = None,
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
            ca_total_entreprise: CA total annuel de l'entreprise pour la
                répartition des coûts fixes. Si None, utilise le CA des
                chantiers visibles (peut donner des marges incorrectes si
                l'entreprise a d'autres chantiers non visibles).

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
        nb_marge_en_attente = 0

        # Phase 1 : calculer le CA total pour répartition des coûts fixes
        # Si ca_total_entreprise est fourni, on l'utilise (recommandé)
        # Sinon on calcule à partir des chantiers visibles (peut être incomplet)
        if ca_total_entreprise is not None and ca_total_entreprise > Decimal("0"):
            ca_total_annee = ca_total_entreprise
        else:
            ca_total_annee = Decimal("0")
            for chantier_id in filtered_ids:
                if self._situation_repository:
                    derniere_sit = self._situation_repository.find_derniere_situation(chantier_id)
                    if derniere_sit:
                        ca_total_annee += Decimal(str(derniere_sit.montant_cumule_ht))

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

            # Calcul de la marge BTP : (Prix Vente - Coût Revient) / Prix Vente
            # Prix Vente = situations de travaux facturées au client
            # Coût Revient = achats réalisés + coût MO + coûts fixes répartis
            prix_vente_ht = Decimal("0")
            cout_mo = Decimal("0")
            marge_pct: Optional[Decimal] = None
            marge_statut_chantier = "en_attente"

            if self._situation_repository:
                derniere_situation = self._situation_repository.find_derniere_situation(chantier_id)
                if derniere_situation:
                    prix_vente_ht = Decimal(str(derniere_situation.montant_cumule_ht))

            if self._cout_mo_repository:
                cout_mo = self._cout_mo_repository.calculer_cout_chantier(chantier_id)

            # Coût de revient = achats réalisés + MO + coûts fixes répartis
            cout_revient = realise + cout_mo

            if prix_vente_ht > Decimal("0"):
                # Répartition des coûts fixes au prorata du CA
                if ca_total_annee > Decimal("0"):
                    quote_part_couts_fixes = (prix_vente_ht / ca_total_annee) * COUTS_FIXES_ANNUELS
                    cout_revient += quote_part_couts_fixes

                # Formule BTP correcte : marge sur prix de vente
                marge_pct = ((prix_vente_ht - cout_revient) / prix_vente_ht) * Decimal("100")
                marge_statut_chantier = "calculee"
            else:
                # Pas de situation = pas de marge calculable, on reste "en_attente"
                nb_marge_en_attente += 1

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
                marge_estimee_pct=(
                    str(marge_pct.quantize(Decimal("0.01")))
                    if marge_pct is not None
                    else None
                ),
                marge_statut=marge_statut_chantier,
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

            # Pour marge moyenne pondérée par prix de vente
            # Seulement si marge calculée (pas "en_attente")
            if marge_pct is not None and prix_vente_ht > Decimal("0"):
                total_prix_vente += prix_vente_ht
                somme_marges_ponderees += marge_pct * prix_vente_ht

        # Marge moyenne pondérée par prix de vente
        nb_chantiers = len(chantiers_summaries)

        # Déterminer le statut de la marge moyenne
        nb_avec_marge = nb_chantiers - nb_marge_en_attente
        if nb_avec_marge == 0:
            marge_statut_global = "en_attente"
            marge_moyenne: Optional[Decimal] = None
        elif nb_marge_en_attente > 0:
            marge_statut_global = "partielle"
            marge_moyenne = (
                somme_marges_ponderees / total_prix_vente
                if total_prix_vente > Decimal("0")
                else None
            )
        else:
            marge_statut_global = "calculee"
            marge_moyenne = (
                somme_marges_ponderees / total_prix_vente
                if total_prix_vente > Decimal("0")
                else None
            )

        kpi_globaux = KPIGlobauxDTO(
            total_budget_revise=str(total_budget_revise.quantize(Decimal("0.01"))),
            total_engage=str(total_engage.quantize(Decimal("0.01"))),
            total_realise=str(total_realise.quantize(Decimal("0.01"))),
            total_reste_a_depenser=str(total_reste.quantize(Decimal("0.01"))),
            marge_moyenne_pct=(
                str(marge_moyenne.quantize(Decimal("0.01")))
                if marge_moyenne is not None
                else None
            ),
            marge_statut=marge_statut_global,
            nb_chantiers=nb_chantiers,
            nb_chantiers_ok=nb_ok,
            nb_chantiers_attention=nb_attention,
            nb_chantiers_depassement=nb_depassement,
            nb_chantiers_marge_en_attente=nb_marge_en_attente,
        )

        # Top 3 rentables (marge_estimee_pct desc, seulement ceux avec marge > 5%)
        chantiers_rentables = [
            c for c in chantiers_summaries
            if c.marge_estimee_pct is not None and Decimal(c.marge_estimee_pct) > Decimal("5")
        ]
        top_rentables = sorted(
            chantiers_rentables,
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
