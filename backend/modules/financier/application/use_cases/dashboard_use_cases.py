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

import logging
from decimal import Decimal
from typing import Optional

from ...domain.repositories import (
    BudgetRepository,
    LotBudgetaireRepository,
    AchatRepository,
    SituationRepository,
    CoutMainOeuvreRepository,
    CoutMaterielRepository,
    FactureRepository,
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
    COUTS_FIXES_ANNUELS,
)

logger = logging.getLogger(__name__)

# Statuts de facture consideres comme CA (facture emise au client)
STATUTS_FACTURE_CA = {"emise", "envoyee", "payee"}


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
        facture_repository: FactureRepository = None,
    ):
        self._budget_repository = budget_repository
        self._lot_repository = lot_repository
        self._achat_repository = achat_repository
        self._situation_repository = situation_repository
        self._cout_mo_repository = cout_mo_repository
        self._cout_materiel_repository = cout_materiel_repository
        self._facture_repository = facture_repository

    def execute(
        self,
        chantier_id: int,
        ca_total_annee: Optional[Decimal] = None,
        couts_fixes_annuels: Optional[Decimal] = None,
    ) -> DashboardFinancierDTO:
        """Construit le tableau de bord financier d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            ca_total_annee: CA total facture sur l'annee pour repartition des couts fixes.
                Si None, les couts fixes ne sont pas repartis.
            couts_fixes_annuels: Couts fixes annuels de l'entreprise (optionnel).
                Si None, utilise la constante COUTS_FIXES_ANNUELS par defaut.

        Returns:
            Le DTO du dashboard complet.

        Raises:
            BudgetNotFoundError: Si aucun budget pour ce chantier.
        """
        effective_couts_fixes = couts_fixes_annuels if couts_fixes_annuels is not None else COUTS_FIXES_ANNUELS

        # P1-1: Auto-calcul ca_total_annee si non fourni
        # Somme des montant_ht de toutes les factures actives (emise/envoyee/payee)
        # pour repartir correctement les frais generaux (600k/an).
        if ca_total_annee is None and self._facture_repository is not None:
            try:
                factures_actives = self._facture_repository.find_all_active(
                    statuts=STATUTS_FACTURE_CA
                )
                ca_total_annee = sum(
                    (f.montant_ht for f in factures_actives), Decimal("0")
                )
                if ca_total_annee > Decimal("0"):
                    logger.info(
                        "Dashboard: ca_total_annee auto-calcule = %s EUR "
                        "(%d factures actives)",
                        ca_total_annee,
                        len(factures_actives),
                    )
            except Exception:
                logger.warning(
                    "Dashboard: impossible de calculer ca_total_annee "
                    "automatiquement, frais generaux non repartis",
                    exc_info=True,
                )

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
        # Couts MO et materiel (pour total realise COMPLET)
        cout_mo = Decimal("0")
        cout_materiel = Decimal("0")
        cout_mo_ok = bool(self._cout_mo_repository)
        cout_materiel_ok = bool(self._cout_materiel_repository)
        if self._cout_mo_repository:
            try:
                cout_mo = self._cout_mo_repository.calculer_cout_chantier(chantier_id)
            except (ValueError, TypeError, AttributeError, KeyError):
                logger.warning("Erreur calcul cout MO dashboard chantier %d", chantier_id, exc_info=True)
                cout_mo_ok = False
        if self._cout_materiel_repository:
            try:
                cout_materiel = self._cout_materiel_repository.calculer_cout_chantier(chantier_id)
            except (ValueError, TypeError, AttributeError, KeyError):
                logger.warning("Erreur calcul cout materiel dashboard chantier %d", chantier_id, exc_info=True)
                cout_materiel_ok = False

        # Total realise COMPLET = achats fournisseurs + MO + materiel interne
        # IMPORTANT: cout_materiel = parc materiel INTERNE (amortissement/location).
        # Les achats de materiel chez fournisseurs sont deja dans total_realise
        # via AchatRepository. Ne PAS confondre les deux pour eviter double comptage.
        total_realise_complet = total_realise + cout_mo + cout_materiel

        # Reste a depenser inclut MO + materiel (negatif = depassement budget)
        reste_a_depenser = arrondir_montant(montant_revise_ht - total_engage - cout_mo - cout_materiel)

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
        consommation_budgetaire_pct: Optional[Decimal] = None

        if self._situation_repository:
            derniere_situation = self._situation_repository.find_derniere_situation(
                chantier_id
            )
            if derniere_situation:
                prix_vente_ht = Decimal(str(derniere_situation.montant_cumule_ht))

        if prix_vente_ht > Decimal("0"):
            # Quote-part frais generaux via fonction unifiee
            # ATTENTION: si ca_total_annee non fourni, frais generaux = 0
            # et la marge sera surestimee (~14% sur 600k de frais fixes).
            effective_ca_total = ca_total_annee or Decimal("0")
            if effective_ca_total <= Decimal("0"):
                logger.warning(
                    "Dashboard chantier %d: ca_total_annee non fourni, "
                    "frais generaux non repartis (marge potentiellement surestimee)",
                    chantier_id,
                )
            quote_part = calculer_quote_part_frais_generaux(
                ca_chantier_ht=prix_vente_ht,
                ca_total_annee=effective_ca_total,
                couts_fixes_annuels=effective_couts_fixes,
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
        else:
            # Fallback: ecart budgetaire quand pas de CA reel (pas de situation)
            # ATTENTION: ceci n'est PAS une marge commerciale BTP.
            # C'est un indicateur de consommation budgetaire :
            # (Budget - Engage) / Budget. A ne pas confondre avec la marge.
            # P1-3: On ne met plus ce calcul dans marge_estimee (trompeur).
            # On utilise consommation_budgetaire_pct a la place.
            marge_estimee = None
            if montant_revise_ht > Decimal("0"):
                consommation_budgetaire_pct = arrondir_pct(
                    (montant_revise_ht - total_engage) / montant_revise_ht * Decimal("100")
                )
            else:
                consommation_budgetaire_pct = arrondir_pct(Decimal("0"))
            marge_statut = "estimee_budgetaire"

        # Si un calcul de cout a echoue et qu'on a une situation, marge partielle
        if not cout_mo_ok or not cout_materiel_ok:
            if prix_vente_ht > Decimal("0"):
                marge_statut = "partielle"

        # Indicateur fiabilite marge (score 0-100%)
        fiabilite = 0
        if prix_vente_ht > Decimal("0"):
            fiabilite += 30  # situation disponible
        if cout_mo_ok and cout_mo > Decimal("0"):
            fiabilite += 25  # MO calculee
        if cout_materiel_ok and cout_materiel > Decimal("0"):
            fiabilite += 25  # materiel avec donnees reelles
        effective_ca_for_fiab = ca_total_annee or Decimal("0")
        if effective_ca_for_fiab > Decimal("0"):
            fiabilite += 20  # frais generaux repartis

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
            fiabilite_marge=fiabilite,
            consommation_budgetaire_pct=(
                str(consommation_budgetaire_pct)
                if consommation_budgetaire_pct is not None
                else None
            ),
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
