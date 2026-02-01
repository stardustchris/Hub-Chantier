"""Use Cases pour l'evolution financiere temporelle.

FIN-17 Phase 2: Endpoint d'evolution mensuelle pour graphique Recharts.
Calcule les courbes prevu/engage/realise cumules par mois.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List

from ...domain.repositories import BudgetRepository, AchatRepository
from ...domain.value_objects.statuts_financiers import STATUTS_ENGAGES, STATUTS_REALISES
from ..dtos.evolution_dtos import EvolutionMensuelleDTO, EvolutionFinanciereDTO
from .budget_use_cases import BudgetNotFoundError


class GetEvolutionFinanciereUseCase:
    """Use case pour calculer l'evolution financiere mensuelle d'un chantier.

    FIN-17: Recupere les achats d'un chantier, les agrege par mois,
    et calcule les cumuls engage/realise avec le prevu lineaire.

    Attributes:
        _budget_repository: Repository pour acceder aux budgets.
        _achat_repository: Repository pour acceder aux achats.
    """

    def __init__(
        self,
        budget_repository: BudgetRepository,
        achat_repository: AchatRepository,
    ) -> None:
        """Initialise le use case.

        Args:
            budget_repository: Repository Budget (interface).
            achat_repository: Repository Achat (interface).
        """
        self._budget_repository = budget_repository
        self._achat_repository = achat_repository

    def execute(self, chantier_id: int) -> EvolutionFinanciereDTO:
        """Calcule l'evolution financiere mensuelle d'un chantier.

        Genere une serie temporelle mensuelle avec :
        - prevu_cumule : repartition lineaire du budget revise
        - engage_cumule : somme cumulee des achats engages
        - realise_cumule : somme cumulee des achats realises

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            EvolutionFinanciereDTO avec la liste des points mensuels.

        Raises:
            BudgetNotFoundError: Si aucun budget pour ce chantier.
        """
        # 1. Recuperer le budget
        budget = self._budget_repository.find_by_chantier_id(chantier_id)
        if not budget:
            raise BudgetNotFoundError(chantier_id=chantier_id)

        montant_revise = budget.montant_revise_ht

        # 2. Recuperer tous les achats du chantier
        achats = self._achat_repository.find_by_chantier(
            chantier_id=chantier_id,
            limit=10000,
            offset=0,
        )

        # 3. Determiner la plage de mois
        today = date.today()
        date_debut = self._determiner_date_debut(achats, budget.created_at)

        if date_debut is None:
            # Aucun achat et pas de created_at sur le budget -> mois courant seul
            date_debut = today

        mois_list = self._generer_mois(date_debut, today)

        if not mois_list:
            return EvolutionFinanciereDTO(
                chantier_id=chantier_id,
                points=[],
            )

        # 4. Calculer le prevu lineaire par mois
        nb_mois = len(mois_list)
        prevu_par_mois = (
            montant_revise / Decimal(str(nb_mois))
            if nb_mois > 0
            else Decimal("0")
        )

        # 5. Construire les points mensuels
        points: List[EvolutionMensuelleDTO] = []
        prevu_cumule = Decimal("0")
        engage_cumule = Decimal("0")
        realise_cumule = Decimal("0")

        for annee, mois_num in mois_list:
            prevu_cumule += prevu_par_mois

            # Fin du mois pour comparaison
            fin_mois = self._fin_du_mois(annee, mois_num)

            # Calculer engage et realise du mois
            engage_mois = Decimal("0")
            realise_mois = Decimal("0")

            for achat in achats:
                if achat.created_at is None:
                    continue

                achat_date = (
                    achat.created_at.date()
                    if isinstance(achat.created_at, datetime)
                    else achat.created_at
                )

                if achat_date.year == annee and achat_date.month == mois_num:
                    if achat.statut in STATUTS_ENGAGES:
                        engage_mois += achat.total_ht
                    if achat.statut in STATUTS_REALISES:
                        realise_mois += achat.total_ht

            engage_cumule += engage_mois
            realise_cumule += realise_mois

            mois_label = f"{mois_num:02d}/{annee}"

            points.append(
                EvolutionMensuelleDTO(
                    mois=mois_label,
                    prevu_cumule=str(prevu_cumule.quantize(Decimal("0.01"))),
                    engage_cumule=str(engage_cumule.quantize(Decimal("0.01"))),
                    realise_cumule=str(realise_cumule.quantize(Decimal("0.01"))),
                )
            )

        return EvolutionFinanciereDTO(
            chantier_id=chantier_id,
            points=points,
        )

    @staticmethod
    def _determiner_date_debut(
        achats: list,
        budget_created_at: datetime | None,
    ) -> date | None:
        """Determine la date de debut pour la serie temporelle.

        Utilise la date du premier achat ou du budget, la plus ancienne.

        Args:
            achats: Liste des achats du chantier.
            budget_created_at: Date de creation du budget (optionnel).

        Returns:
            La date de debut ou None si aucune date disponible.
        """
        dates: List[date] = []

        for achat in achats:
            if achat.created_at is not None:
                if isinstance(achat.created_at, datetime):
                    dates.append(achat.created_at.date())
                else:
                    dates.append(achat.created_at)

        if budget_created_at is not None:
            if isinstance(budget_created_at, datetime):
                dates.append(budget_created_at.date())
            else:
                dates.append(budget_created_at)

        if not dates:
            return None

        return min(dates)

    @staticmethod
    def _generer_mois(
        date_debut: date,
        date_fin: date,
    ) -> List[tuple[int, int]]:
        """Genere la liste ordonnee des mois entre deux dates.

        Args:
            date_debut: Date de debut (incluse).
            date_fin: Date de fin (incluse).

        Returns:
            Liste de tuples (annee, mois) ordonnee chronologiquement.
        """
        mois_list: List[tuple[int, int]] = []
        annee = date_debut.year
        mois = date_debut.month

        while (annee, mois) <= (date_fin.year, date_fin.month):
            mois_list.append((annee, mois))
            if mois == 12:
                annee += 1
                mois = 1
            else:
                mois += 1

        return mois_list

    @staticmethod
    def _fin_du_mois(annee: int, mois: int) -> date:
        """Retourne le dernier jour du mois.

        Args:
            annee: L'annee.
            mois: Le mois (1-12).

        Returns:
            La date du dernier jour du mois.
        """
        if mois == 12:
            return date(annee + 1, 1, 1)
        return date(annee, mois + 1, 1)
