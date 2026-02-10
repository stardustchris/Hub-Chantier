"""Use Cases pour la vue consolidee multi-chantiers.

FIN-20 Phase 3: Vue consolidee des finances pour la page /finances.
Agrege les KPI financiers de plusieurs chantiers.

Formule de marge BTP :
    Marge = (Prix Vente - Coût Revient) / Prix Vente × 100

Où :
    - Prix Vente = situations de travaux facturées au client
    - Coût Revient = achats réalisés + coût MO + coûts fixes répartis

Coûts fixes société : 600 000 € / an (frais généraux hors salaires)
Répartition : au prorata du CA facturé (prix de vente)
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional

from shared.domain.calcul_financier import (
    calculer_marge_chantier,
    calculer_quote_part_frais_generaux,
    arrondir_pct,
    arrondir_montant,
    COUTS_FIXES_ANNUELS,
)

logger = logging.getLogger(__name__)

from shared.application.ports.chantier_info_port import ChantierInfoPort, ChantierInfoDTO

from ...domain.repositories import (
    BudgetRepository,
    LotBudgetaireRepository,
    AchatRepository,
    AlerteRepository,
    SituationRepository,
    CoutMainOeuvreRepository,
    CoutMaterielRepository,
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
        cout_materiel_repository: Optional[CoutMaterielRepository] = None,
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
            cout_materiel_repository: Repository Cout materiel pour calcul marge BTP (optionnel).
        """
        self._budget_repository = budget_repository
        self._lot_repository = lot_repository
        self._achat_repository = achat_repository
        self._alerte_repository = alerte_repository
        self._chantier_info_port = chantier_info_port
        self._situation_repository = situation_repository
        self._cout_mo_repository = cout_mo_repository
        self._cout_materiel_repository = cout_materiel_repository

    def execute(
        self,
        user_accessible_chantier_ids: List[int],
        statut_chantier: Optional[str] = None,
        ca_total_entreprise: Optional[Decimal] = None,
        couts_fixes_annuels: Optional[Decimal] = None,
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
                repartition des couts fixes. Si None, utilise le CA des
                chantiers visibles (peut donner des marges incorrectes si
                l'entreprise a d'autres chantiers non visibles).
            couts_fixes_annuels: Couts fixes annuels de l'entreprise (optionnel).
                Si None, utilise la constante COUTS_FIXES_ANNUELS par defaut.

        Returns:
            VueConsolideeDTO avec KPI globaux, liste chantiers,
            top 3 rentables et top 3 derives.
        """
        effective_couts_fixes = couts_fixes_annuels or COUTS_FIXES_ANNUELS
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
        # Marge moyenne ponderee (par prix de vente ou montant revise en fallback)
        total_poids_marge = Decimal("0")
        somme_marges_ponderees = Decimal("0")

        nb_ok = 0
        nb_attention = 0
        nb_depassement = 0
        nb_marge_en_attente = 0

        # CA total pour répartition des coûts fixes
        # Si ca_total_entreprise est fourni, on l'utilise (recommandé)
        # Sinon 0 = pas de répartition (même pattern que dashboard)
        ca_total_annee = ca_total_entreprise if (
            ca_total_entreprise is not None and ca_total_entreprise > Decimal("0")
        ) else Decimal("0")

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
            # Fallback : (Budget - Engagé) / Budget si pas de situation
            prix_vente_ht = Decimal("0")
            cout_mo = Decimal("0")
            cout_materiel = Decimal("0")
            marge_pct: Optional[Decimal] = None
            marge_statut_chantier = "estimee"
            poids_marge = Decimal("0")

            if self._situation_repository:
                derniere_situation = self._situation_repository.find_derniere_situation(chantier_id)
                if derniere_situation:
                    prix_vente_ht = Decimal(str(derniere_situation.montant_cumule_ht))

            cout_mo_ok = True
            cout_materiel_ok = True

            if self._cout_mo_repository:
                try:
                    cout_mo = self._cout_mo_repository.calculer_cout_chantier(chantier_id)
                except (ValueError, TypeError, AttributeError, KeyError):
                    logger.warning("Erreur calcul cout MO consolidation chantier %d", chantier_id, exc_info=True)
                    cout_mo_ok = False

            if self._cout_materiel_repository:
                try:
                    # cout_materiel = parc materiel INTERNE (amortissement/location).
                    # Les achats materiel fournisseurs sont deja dans `realise`
                    # via AchatRepository. Ne PAS confondre pour eviter double comptage.
                    cout_materiel = self._cout_materiel_repository.calculer_cout_chantier(chantier_id)
                except (ValueError, TypeError, AttributeError, KeyError):
                    logger.warning("Erreur calcul cout materiel consolidation chantier %d", chantier_id, exc_info=True)
                    cout_materiel_ok = False

            if prix_vente_ht > Decimal("0"):
                # Marge BTP réelle (situations disponibles)
                quote_part = calculer_quote_part_frais_generaux(
                    ca_chantier_ht=prix_vente_ht,
                    ca_total_annee=ca_total_annee,
                    couts_fixes_annuels=effective_couts_fixes,
                )
                marge_pct = calculer_marge_chantier(
                    ca_ht=prix_vente_ht,
                    cout_achats=realise,
                    cout_mo=cout_mo,
                    cout_materiel=cout_materiel,
                    quote_part_frais_generaux=quote_part,
                )
                marge_statut_chantier = "calculee"
                poids_marge = prix_vente_ht
            elif montant_revise > Decimal("0"):
                # Fallback budget : ecart budgetaire (PAS une marge commerciale)
                # ATTENTION: ceci est un indicateur de consommation budgetaire,
                # pas une marge BTP. Chantier ferme → base sur realise, sinon engage.
                marge_statut_chantier = "estimee_budgetaire"
                cout_ref = realise if is_ferme else engage
                marge_pct = arrondir_pct(
                    ((montant_revise - cout_ref) / montant_revise) * Decimal("100")
                )
                poids_marge = montant_revise
            else:
                # Budget = 0
                marge_pct = Decimal("0")

            # Marquer partielle si un calcul de cout a echoue (ne pas ecraser si fallback budgetaire)
            if not cout_mo_ok or not cout_materiel_ok:
                if prix_vente_ht > Decimal("0"):
                    marge_statut_chantier = "partielle"

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

            # Compteur marge en attente / partielle
            if marge_pct is None or marge_statut_chantier in ("en_attente", "partielle"):
                nb_marge_en_attente += 1

            # Indicateur fiabilite marge (score 0-100%)
            fiabilite = 0
            if prix_vente_ht > Decimal("0"):
                fiabilite += 30  # situation disponible
            if cout_mo_ok and cout_mo > Decimal("0"):
                fiabilite += 25  # MO calculee
            if cout_materiel_ok and cout_materiel >= Decimal("0"):
                fiabilite += 25  # materiel OK (0 est valide si pas de parc)
            if ca_total_annee > Decimal("0"):
                fiabilite += 20  # frais generaux repartis

            # Alertes non acquittees
            alertes = self._alerte_repository.find_non_acquittees(chantier_id)
            nb_alertes = len(alertes)

            # Nom et statut chantier : utiliser le port si disponible, sinon fallback
            nom_chantier = chantier_info.nom if chantier_info is not None else f"Chantier {chantier_id}"
            statut_ch = chantier_info.statut if chantier_info is not None else ""

            summary = ChantierFinancierSummaryDTO(
                chantier_id=chantier_id,
                nom_chantier=nom_chantier,
                montant_revise_ht=str(arrondir_montant(montant_revise)),
                total_engage=str(arrondir_montant(engage)),
                total_realise=str(arrondir_montant(realise + cout_mo + cout_materiel)),
                reste_a_depenser=str(arrondir_montant(reste)),
                marge_estimee_pct=(
                    str(arrondir_pct(marge_pct))
                    if marge_pct is not None
                    else None
                ),
                marge_statut=marge_statut_chantier,
                fiabilite_marge=fiabilite,
                pct_engage=str(arrondir_pct(pct_engage)),
                pct_realise=str(arrondir_pct(pct_realise)),
                statut=statut,
                nb_alertes=nb_alertes,
                statut_chantier=statut_ch,
            )
            chantiers_summaries.append(summary)

            # Cumuler pour globaux
            total_budget_revise += montant_revise
            total_engage += engage
            total_realise += realise + cout_mo + cout_materiel
            total_reste += reste

            # Pour marge moyenne pondérée
            if marge_pct is not None and poids_marge > Decimal("0"):
                total_poids_marge += poids_marge
                somme_marges_ponderees += marge_pct * poids_marge

        # Marge moyenne pondérée
        nb_chantiers = len(chantiers_summaries)

        # Determiner marge_statut_global
        if nb_chantiers > 0 and nb_marge_en_attente >= nb_chantiers:
            marge_statut_global = "en_attente"
        elif nb_marge_en_attente > 0:
            marge_statut_global = "partielle"
        else:
            marge_statut_global = "calculee"

        if total_poids_marge > Decimal("0"):
            marge_moyenne: Optional[Decimal] = (
                somme_marges_ponderees / total_poids_marge
            )
        else:
            marge_moyenne = Decimal("0")

        kpi_globaux = KPIGlobauxDTO(
            total_budget_revise=str(arrondir_montant(total_budget_revise)),
            total_engage=str(arrondir_montant(total_engage)),
            total_realise=str(arrondir_montant(total_realise)),
            total_reste_a_depenser=str(arrondir_montant(total_reste)),
            marge_moyenne_pct=(
                str(arrondir_pct(marge_moyenne))
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
