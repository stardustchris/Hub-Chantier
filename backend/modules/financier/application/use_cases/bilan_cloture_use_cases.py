"""Use Case GetBilanCloture - Bilan de cloture d'un chantier.

GAP #10: Agregation de toutes les informations financieres finales
pour produire un rapport recapitulatif de cloture.
"""

import logging
from decimal import Decimal
from typing import List

from ...domain.repositories.budget_repository import BudgetRepository
from ...domain.repositories.lot_budgetaire_repository import LotBudgetaireRepository
from ...domain.repositories.achat_repository import AchatRepository
from ...domain.repositories.avenant_repository import AvenantRepository
from ...domain.repositories.situation_repository import SituationRepository
from ...domain.value_objects import StatutAchat
from ..dtos.bilan_cloture_dtos import BilanClotureDTO, EcartLotDTO
from shared.application.ports.chantier_info_port import ChantierInfoPort

logger = logging.getLogger(__name__)


class BilanClotureError(Exception):
    """Exception pour les erreurs lors du calcul du bilan de cloture."""

    def __init__(self, message: str = "Erreur lors du calcul du bilan de cloture"):
        self.message = message
        super().__init__(self.message)


class BudgetNonTrouveError(BilanClotureError):
    """Aucun budget trouve pour le chantier."""

    def __init__(self, chantier_id: int):
        super().__init__(f"Aucun budget trouve pour le chantier {chantier_id}")


class ChantierNonTrouveError(BilanClotureError):
    """Chantier non trouve."""

    def __init__(self, chantier_id: int):
        super().__init__(f"Chantier {chantier_id} non trouve")


class GetBilanClotureUseCase:
    """Cas d'utilisation : Generer le bilan de cloture d'un chantier.

    Recupere et agregue toutes les donnees financieres d'un chantier :
    - Budget initial et revise (avec avenants)
    - Totaux engages et realises
    - Ecarts prevu/realise par lot budgetaire
    - Nombre d'achats, situations et avenants
    - Tracabilite vers le devis source

    Le bilan est disponible pour tout chantier (pas seulement les fermes),
    mais le champ ``est_definitif`` indique si c'est un bilan final (chantier ferme).

    Attributes:
        budget_repository: Repository pour les budgets.
        lot_repository: Repository pour les lots budgetaires.
        achat_repository: Repository pour les achats.
        avenant_repository: Repository pour les avenants.
        situation_repository: Repository pour les situations.
        chantier_info_port: Port pour les infos du chantier.
    """

    def __init__(
        self,
        budget_repository: BudgetRepository,
        lot_repository: LotBudgetaireRepository,
        achat_repository: AchatRepository,
        avenant_repository: AvenantRepository,
        situation_repository: SituationRepository,
        chantier_info_port: ChantierInfoPort,
    ) -> None:
        """Initialise le use case.

        Args:
            budget_repository: Repository Budget (interface).
            lot_repository: Repository LotBudgetaire (interface).
            achat_repository: Repository Achat (interface).
            avenant_repository: Repository Avenant (interface).
            situation_repository: Repository Situation (interface).
            chantier_info_port: Port pour infos chantier (nom, statut).
        """
        self.budget_repository = budget_repository
        self.lot_repository = lot_repository
        self.achat_repository = achat_repository
        self.avenant_repository = avenant_repository
        self.situation_repository = situation_repository
        self.chantier_info_port = chantier_info_port

    def execute(self, chantier_id: int) -> BilanClotureDTO:
        """Genere le bilan de cloture pour un chantier.

        Args:
            chantier_id: ID du chantier.

        Returns:
            BilanClotureDTO contenant le bilan complet.

        Raises:
            BudgetNonTrouveError: Si aucun budget n'existe pour le chantier.
            ChantierNonTrouveError: Si le chantier n'existe pas.
        """
        # 1. Recuperer les infos du chantier via le port
        chantier_info = self.chantier_info_port.get_chantier_info(chantier_id)
        if chantier_info is None:
            raise ChantierNonTrouveError(chantier_id)

        nom_chantier = chantier_info.nom
        statut_chantier = chantier_info.statut
        est_definitif = statut_chantier == "ferme"

        # 2. Recuperer le budget du chantier
        budget = self.budget_repository.find_by_chantier_id(chantier_id)
        if budget is None:
            raise BudgetNonTrouveError(chantier_id)

        budget_initial_ht = budget.montant_initial_ht
        budget_revise_ht = budget.montant_revise_ht
        montant_avenants_ht = budget.montant_avenants_ht
        devis_source_id = budget.devis_id

        # 3. Compter et sommer les avenants
        nb_avenants = self.avenant_repository.count_by_budget_id(budget.id)

        # 4. Calculer les engages et realises globaux
        # Engage = tous les achats non refuses (demande + valide + commande + livre + facture)
        statuts_engages = [
            StatutAchat.DEMANDE,
            StatutAchat.VALIDE,
            StatutAchat.COMMANDE,
            StatutAchat.LIVRE,
            StatutAchat.FACTURE,
        ]
        total_engage_ht = self.achat_repository.somme_by_chantier(
            chantier_id, statuts=statuts_engages
        )

        # Realise = achats livres ou factures
        statuts_realises = [
            StatutAchat.LIVRE,
            StatutAchat.FACTURE,
        ]
        total_realise_ht = self.achat_repository.somme_by_chantier(
            chantier_id, statuts=statuts_realises
        )

        # 5. Calculer le reste non depense et la marge
        reste_non_depense_ht = budget_revise_ht - total_engage_ht
        marge_finale_ht = budget_revise_ht - total_realise_ht

        if budget_revise_ht > Decimal("0"):
            marge_finale_pct = (marge_finale_ht / budget_revise_ht * Decimal("100")).quantize(
                Decimal("0.01")
            )
        else:
            marge_finale_pct = Decimal("0")

        # 6. Compter les achats et situations
        nb_achats = self.achat_repository.count_by_chantier(chantier_id)
        nb_situations = self.situation_repository.count_by_chantier_id(chantier_id)

        # 7. Calculer les ecarts par lot budgetaire
        ecarts_par_lot = self._calculer_ecarts_par_lot(budget.id, chantier_id)

        return BilanClotureDTO(
            chantier_id=chantier_id,
            nom_chantier=nom_chantier,
            statut_chantier=statut_chantier,
            budget_initial_ht=str(budget_initial_ht),
            budget_revise_ht=str(budget_revise_ht),
            montant_avenants_ht=str(montant_avenants_ht),
            nb_avenants=nb_avenants,
            total_engage_ht=str(total_engage_ht),
            total_realise_ht=str(total_realise_ht),
            reste_non_depense_ht=str(reste_non_depense_ht),
            marge_finale_ht=str(marge_finale_ht),
            marge_finale_pct=str(marge_finale_pct),
            nb_achats=nb_achats,
            nb_situations=nb_situations,
            ecarts_par_lot=ecarts_par_lot,
            devis_source_id=devis_source_id,
            est_definitif=est_definitif,
        )

    def _calculer_ecarts_par_lot(
        self, budget_id: int, chantier_id: int
    ) -> List[EcartLotDTO]:
        """Calcule les ecarts prevu/realise pour chaque lot budgetaire.

        Args:
            budget_id: ID du budget.
            chantier_id: ID du chantier (pour filtrer les achats).

        Returns:
            Liste des ecarts par lot.
        """
        lots = self.lot_repository.find_by_budget_id(budget_id)
        ecarts: List[EcartLotDTO] = []

        statuts_realises = [
            StatutAchat.LIVRE,
            StatutAchat.FACTURE,
        ]

        for lot in lots:
            if lot.id is None:
                continue

            prevu_ht = lot.total_prevu_ht

            # Realise par lot = somme des achats livres/factures rattaches au lot
            realise_ht = self.achat_repository.somme_by_lot(
                lot.id, statuts=statuts_realises
            )

            ecart_ht = prevu_ht - realise_ht

            if prevu_ht > Decimal("0"):
                ecart_pct = (ecart_ht / prevu_ht * Decimal("100")).quantize(
                    Decimal("0.01")
                )
            else:
                ecart_pct = Decimal("0")

            ecarts.append(
                EcartLotDTO(
                    code_lot=lot.code_lot,
                    libelle=lot.libelle,
                    prevu_ht=str(prevu_ht),
                    realise_ht=str(realise_ht),
                    ecart_ht=str(ecart_ht),
                    ecart_pct=str(ecart_pct),
                )
            )

        return ecarts
