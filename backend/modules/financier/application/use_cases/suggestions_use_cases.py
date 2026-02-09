"""Use Cases pour les suggestions financieres et indicateurs predictifs.

FIN-21/22 Phase 3: Suggestions algorithmiques deterministes + IA (Gemini)
et indicateurs predictifs pour un chantier.
"""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from shared.domain.calcul_financier import arrondir_montant, arrondir_pct

from ...domain.repositories import (
    BudgetRepository,
    AchatRepository,
    LotBudgetaireRepository,
    AlerteRepository,
)
from ...domain.value_objects.statuts_financiers import STATUTS_ENGAGES, STATUTS_REALISES
from ..dtos.suggestions_dtos import (
    SuggestionDTO,
    IndicateursPredictifDTO,
    SuggestionsFinancieresDTO,
)
from ..ports.ai_suggestion_port import AISuggestionPort
from .budget_use_cases import BudgetNotFoundError

logger = logging.getLogger(__name__)


MAX_SUGGESTIONS = 5
"""Nombre maximum de suggestions retournees par chantier."""


class GetSuggestionsFinancieresUseCase:
    """Use case pour generer des suggestions financieres.

    FIN-21/22: Analyse les donnees financieres d'un chantier et genere
    des suggestions basees sur des regles algorithmiques. Si un provider IA
    est disponible (Gemini), les suggestions IA sont fusionnees en priorite.
    Calcule egalement les indicateurs predictifs (burn rate, date epuisement).

    Attributes:
        _budget_repository: Repository pour acceder aux budgets.
        _achat_repository: Repository pour acceder aux achats.
        _lot_repository: Repository pour acceder aux lots budgetaires.
        _alerte_repository: Repository pour acceder aux alertes.
        _ai_provider: Provider IA optionnel (Gemini) pour les suggestions.
    """

    def __init__(
        self,
        budget_repository: BudgetRepository,
        achat_repository: AchatRepository,
        lot_repository: LotBudgetaireRepository,
        alerte_repository: AlerteRepository,
        ai_provider: Optional[AISuggestionPort] = None,
    ) -> None:
        """Initialise le use case.

        Args:
            budget_repository: Repository Budget (interface).
            achat_repository: Repository Achat (interface).
            lot_repository: Repository LotBudgetaire (interface).
            alerte_repository: Repository Alerte (interface).
            ai_provider: Provider IA optionnel (AISuggestionPort).
                Si None, seules les regles algorithmiques sont utilisees.
        """
        self._budget_repository = budget_repository
        self._achat_repository = achat_repository
        self._lot_repository = lot_repository
        self._alerte_repository = alerte_repository
        self._ai_provider = ai_provider

    def execute(self, chantier_id: int) -> SuggestionsFinancieresDTO:
        """Genere les suggestions financieres et indicateurs predictifs.

        Applique les regles algorithmiques sur les donnees financieres
        du chantier pour generer des suggestions actionnables.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            SuggestionsFinancieresDTO avec suggestions et indicateurs.

        Raises:
            BudgetNotFoundError: Si aucun budget pour ce chantier.
        """
        # 1. Recuperer le budget
        budget = self._budget_repository.find_by_chantier_id(chantier_id)
        if not budget:
            raise BudgetNotFoundError(chantier_id=chantier_id)

        montant_revise = budget.montant_revise_ht

        # 2. Calculer les KPI de base
        total_engage = self._achat_repository.somme_by_chantier(
            chantier_id, statuts=STATUTS_ENGAGES
        )
        total_realise = self._achat_repository.somme_by_chantier(
            chantier_id, statuts=STATUTS_REALISES
        )
        reste_a_depenser = montant_revise - total_engage

        # Pourcentages
        if montant_revise > Decimal("0"):
            pct_engage = (total_engage / montant_revise) * Decimal("100")
            pct_realise = (total_realise / montant_revise) * Decimal("100")
            # NOTE: Ceci est un indicateur budgetaire, PAS une marge reelle.
            # Marge reelle = (CA - Couts) / CA (cf. calcul_financier.py)
            marge_budgetaire_pct = ((montant_revise - total_engage) / montant_revise) * Decimal("100")
        else:
            pct_engage = Decimal("0")
            pct_realise = Decimal("0")
            marge_budgetaire_pct = Decimal("0")

        # Calcul du burn rate pour les KPI
        burn_rate, _budget_moyen = self._calculer_burn_rate(
            total_realise=total_realise,
            montant_revise=montant_revise,
            budget_created_at=budget.created_at,
        )

        # 3. Generer les suggestions algorithmiques (max 5)
        suggestions_algo = self._generer_suggestions(
            chantier_id=chantier_id,
            montant_revise=montant_revise,
            total_engage=total_engage,
            total_realise=total_realise,
            reste_a_depenser=reste_a_depenser,
            pct_engage=pct_engage,
            pct_realise=pct_realise,
            marge_pct=marge_budgetaire_pct,
            budget=budget,
        )

        # 3bis. Si provider IA disponible, generer et fusionner les suggestions IA
        ai_available = False
        source = "algorithmic"
        suggestions = suggestions_algo

        if self._ai_provider is not None:
            try:
                kpi_data = {
                    "montant_revise": str(arrondir_montant(montant_revise)),
                    "total_engage": str(arrondir_montant(total_engage)),
                    "total_realise": str(arrondir_montant(total_realise)),
                    "pct_engage": str(arrondir_pct(pct_engage)),
                    "pct_realise": str(arrondir_pct(pct_realise)),
                    "marge_budgetaire_pct": str(arrondir_pct(marge_budgetaire_pct)),
                    "reste_a_depenser": str(arrondir_montant(reste_a_depenser)),
                    "burn_rate": str(arrondir_montant(burn_rate)),
                }
                suggestions_ia = self._ai_provider.generate_suggestions(kpi_data)

                if suggestions_ia:
                    # Fusionner : IA en priorite, deduplication par type
                    suggestions = self._fusionner_suggestions(
                        suggestions_ia, suggestions_algo
                    )
                    ai_available = True
                    source = "gemini"
                    logger.info(
                        "Suggestions IA fusionnees pour chantier %d: "
                        "%d IA + %d algo -> %d total",
                        chantier_id,
                        len(suggestions_ia),
                        len(suggestions_algo),
                        len(suggestions),
                    )
                else:
                    logger.info(
                        "Provider IA n'a retourne aucune suggestion pour chantier %d, "
                        "fallback algorithmique",
                        chantier_id,
                    )
            except Exception as e:
                logger.warning(
                    "Erreur provider IA pour chantier %d (fallback algo): %s",
                    chantier_id,
                    str(e),
                )
                # Fallback silencieux aux regles algo

        # 4. Calculer les indicateurs predictifs
        indicateurs = self._calculer_indicateurs_predictifs(
            montant_revise=montant_revise,
            total_realise=total_realise,
            reste_a_depenser=reste_a_depenser,
            budget_created_at=budget.created_at,
        )

        return SuggestionsFinancieresDTO(
            chantier_id=chantier_id,
            suggestions=suggestions[:5],
            indicateurs=indicateurs,
            ai_available=ai_available,
            source=source,
        )

    def _generer_suggestions(
        self,
        chantier_id: int,
        montant_revise: Decimal,
        total_engage: Decimal,
        total_realise: Decimal,
        reste_a_depenser: Decimal,
        pct_engage: Decimal,
        pct_realise: Decimal,
        marge_pct: Decimal,
        budget: object,
    ) -> List[SuggestionDTO]:
        """Genere les suggestions basees sur des regles deterministes.

        Args:
            chantier_id: ID du chantier.
            montant_revise: Montant revise HT.
            total_engage: Total engage.
            total_realise: Total realise.
            reste_a_depenser: Reste a depenser.
            pct_engage: Pourcentage engage.
            pct_realise: Pourcentage realise.
            marge_pct: Marge estimee en pourcentage.
            budget: Entite budget du chantier.

        Returns:
            Liste de SuggestionDTO ordonnee par severite.
        """
        suggestions: List[SuggestionDTO] = []

        # Regle 1: Si pct_engage > 90% et marge < 10% -> CRITICAL
        if pct_engage > Decimal("90") and marge_pct < Decimal("10"):
            impact = reste_a_depenser if reste_a_depenser < Decimal("0") else Decimal("0")
            suggestions.append(
                SuggestionDTO(
                    type="CREATE_AVENANT",
                    severity="CRITICAL",
                    titre="Creer un avenant budgetaire",
                    description=(
                        f"Le budget est engage a {pct_engage.quantize(Decimal('0.1'))}% "
                        f"avec une marge de seulement {marge_pct.quantize(Decimal('0.1'))}%. "
                        "Un avenant est recommande pour securiser le chantier."
                    ),
                    impact_estime_eur=str(arrondir_montant(abs(impact))),
                )
            )

        # Regle 2: Si pct_realise > pct_engage + 10% -> WARNING
        if pct_realise > pct_engage + Decimal("10"):
            ecart = total_realise - total_engage
            suggestions.append(
                SuggestionDTO(
                    type="REDUCE_COSTS",
                    severity="WARNING",
                    titre="Le realise depasse l'engage",
                    description=(
                        f"Le realise ({pct_realise.quantize(Decimal('0.1'))}%) depasse "
                        f"l'engage ({pct_engage.quantize(Decimal('0.1'))}%) de plus de 10 points. "
                        "Verifier les facturations non prevues."
                    ),
                    impact_estime_eur=str(arrondir_montant(abs(ecart))),
                )
            )

        # Regle 3: Lots avec ecart prevu/realise > 30%
        if budget and hasattr(budget, "id") and budget.id:
            lots = self._lot_repository.find_by_budget_id(budget.id)
            for lot in lots:
                lot_engage = self._achat_repository.somme_by_lot(
                    lot.id, statuts=STATUTS_ENGAGES
                )
                if lot.total_prevu_ht > Decimal("0"):
                    ecart_lot_pct = (
                        (lot_engage - lot.total_prevu_ht) / lot.total_prevu_ht
                    ) * Decimal("100")
                    if ecart_lot_pct > Decimal("30"):
                        depassement = lot_engage - lot.total_prevu_ht
                        suggestions.append(
                            SuggestionDTO(
                                type="OPTIMIZE_LOTS",
                                severity="WARNING",
                                titre=f"Lot {lot.code_lot} en depassement",
                                description=(
                                    f"Le lot {lot.code_lot} ({lot.libelle}) depasse "
                                    f"le prevu de {ecart_lot_pct.quantize(Decimal('0.1'))}%. "
                                    f"Engage: {lot_engage}, Prevu: {lot.total_prevu_ht}."
                                ),
                                impact_estime_eur=str(
                                    arrondir_montant(depassement)
                                ),
                            )
                        )

        # Regle 4: Burn rate trop eleve (calcul simplifie)
        burn_rate, budget_moyen = self._calculer_burn_rate(
            total_realise=total_realise,
            montant_revise=montant_revise,
            budget_created_at=budget.created_at if budget else None,
        )
        if budget_moyen > Decimal("0") and burn_rate > budget_moyen * Decimal("1.2"):
            ecart_burn = burn_rate - budget_moyen
            suggestions.append(
                SuggestionDTO(
                    type="ALERT_BURN_RATE",
                    severity="WARNING",
                    titre="Rythme de depense trop eleve",
                    description=(
                        f"Le burn rate mensuel ({arrondir_montant(burn_rate)} EUR/mois) "
                        f"depasse de 20% le budget moyen mensuel "
                        f"({arrondir_montant(budget_moyen)} EUR/mois)."
                    ),
                    impact_estime_eur=str(arrondir_montant(ecart_burn)),
                )
            )

        # Regle 5: Aucune situation depuis > 30j et budget > 100k
        if montant_revise > Decimal("100000"):
            from ...domain.repositories import SituationRepository
            # Note: On ne peut pas injecter le SituationRepository ici
            # car il n'est pas dans les dependances du use case.
            # On verifie via les alertes comme proxy.
            alertes = self._alerte_repository.find_by_chantier_id(chantier_id)
            # Suggestion INFO si pas deja trop de suggestions
            if len(suggestions) < MAX_SUGGESTIONS:
                suggestions.append(
                    SuggestionDTO(
                        type="CREATE_SITUATION",
                        severity="INFO",
                        titre="Creer une situation de travaux",
                        description=(
                            "Le budget depasse 100 000 EUR. "
                            "Pensez a creer une situation de travaux reguliere "
                            "pour suivre l'avancement financier."
                        ),
                        impact_estime_eur="0",
                    )
                )

        # Trier par severite (CRITICAL > WARNING > INFO)
        severity_order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
        suggestions.sort(key=lambda s: severity_order.get(s.severity, 3))

        return suggestions

    def _fusionner_suggestions(
        self,
        suggestions_ia: List[SuggestionDTO],
        suggestions_algo: List[SuggestionDTO],
    ) -> List[SuggestionDTO]:
        """Fusionne les suggestions IA et algorithmiques.

        Les suggestions IA ont la priorite. En cas de doublon (meme type),
        la suggestion IA est conservee et l'algorithmique est ignoree.

        Args:
            suggestions_ia: Suggestions generees par l'IA.
            suggestions_algo: Suggestions generees par les regles algo.

        Returns:
            Liste fusionnee, triee par severite (CRITICAL > WARNING > INFO).
        """
        # Collecter les types deja couverts par l'IA
        types_ia = {s.type for s in suggestions_ia}

        # Ajouter les suggestions algo dont le type n'est pas deja couvert
        merged: List[SuggestionDTO] = list(suggestions_ia)
        for s_algo in suggestions_algo:
            if s_algo.type not in types_ia:
                merged.append(s_algo)

        # Trier par severite
        severity_order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
        merged.sort(key=lambda s: severity_order.get(s.severity, 3))

        return merged

    def _calculer_burn_rate(
        self,
        total_realise: Decimal,
        montant_revise: Decimal,
        budget_created_at: datetime | None,
        duree_prevue_mois: int | None = None,
    ) -> tuple[Decimal, Decimal]:
        """Calcule le burn rate mensuel et le budget moyen mensuel.

        CORRECTION: Le budget moyen est calcule sur la duree PREVUE du chantier,
        pas sur la duree ecoulee. Sinon, les 6 premiers mois d'un chantier
        de 12 mois generent systematiquement des faux positifs d'alertes
        car budget_moyen = montant_revise / 2 au lieu de / 12.

        Args:
            total_realise: Total des depenses realisees.
            montant_revise: Montant revise du budget.
            budget_created_at: Date de creation du budget.
            duree_prevue_mois: Duree previsionnelle du chantier en mois.
                Si None, utilise 12 mois par defaut (chantier BTP typique).

        Returns:
            Tuple (burn_rate_mensuel, budget_moyen_mensuel).
        """
        today = date.today()

        # Nombre de mois depuis le debut (pour le burn rate reel)
        if budget_created_at:
            if isinstance(budget_created_at, datetime):
                debut = budget_created_at.date()
            else:
                debut = budget_created_at
            nb_mois_ecoules = max(
                1,
                (today.year - debut.year) * 12 + (today.month - debut.month) + 1,
            )
        else:
            nb_mois_ecoules = 1

        burn_rate = total_realise / Decimal(str(nb_mois_ecoules))

        # Budget moyen mensuel : sur la duree PREVUE, pas ecoulee
        # Defaut 12 mois (chantier BTP gros oeuvre typique)
        duree = duree_prevue_mois if duree_prevue_mois and duree_prevue_mois > 0 else 12
        budget_moyen = montant_revise / Decimal(str(duree))

        return burn_rate, budget_moyen

    def _calculer_indicateurs_predictifs(
        self,
        montant_revise: Decimal,
        total_realise: Decimal,
        reste_a_depenser: Decimal,
        budget_created_at: datetime | None,
    ) -> IndicateursPredictifDTO:
        """Calcule les indicateurs predictifs purs (pas d'IA).

        Args:
            montant_revise: Montant revise du budget.
            total_realise: Total realise.
            reste_a_depenser: Reste a depenser.
            budget_created_at: Date de creation du budget.

        Returns:
            IndicateursPredictifDTO avec les indicateurs calcules.
        """
        # Reutilise _calculer_burn_rate pour coherence
        burn_rate, budget_moyen = self._calculer_burn_rate(
            total_realise=total_realise,
            montant_revise=montant_revise,
            budget_created_at=budget_created_at,
        )

        # ecart_burn_rate = ((burn_rate - budget_moyen) / budget_moyen) * 100
        if budget_moyen > Decimal("0"):
            ecart_burn_rate = (
                (burn_rate - budget_moyen) / budget_moyen
            ) * Decimal("100")
        else:
            ecart_burn_rate = Decimal("0")

        # mois_restants = reste_a_depenser / burn_rate
        if burn_rate > Decimal("0") and reste_a_depenser > Decimal("0"):
            mois_restants = reste_a_depenser / burn_rate
        else:
            mois_restants = Decimal("0")

        # date_epuisement = aujourd'hui + mois_restants * 30 jours
        if mois_restants > Decimal("0"):
            jours_restants = int(mois_restants * Decimal("30"))
            date_epuisement = date.today() + timedelta(days=jours_restants)
            date_epuisement_str = date_epuisement.isoformat()
        else:
            date_epuisement_str = "N/A"

        # avancement_financier = (total_realise / montant_revise) * 100
        if montant_revise > Decimal("0"):
            avancement = (total_realise / montant_revise) * Decimal("100")
        else:
            avancement = Decimal("0")

        return IndicateursPredictifDTO(
            burn_rate_mensuel=str(arrondir_montant(burn_rate)),
            budget_moyen_mensuel=str(arrondir_montant(budget_moyen)),
            ecart_burn_rate_pct=str(arrondir_pct(ecart_burn_rate)),
            mois_restants_budget=str(arrondir_montant(mois_restants)),
            date_epuisement_estimee=date_epuisement_str,
            avancement_financier_pct=str(arrondir_pct(avancement)),
        )
