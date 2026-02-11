"""Use Case GetBilanCloture - Bilan de cloture d'un chantier.

GAP #10: Agregation de toutes les informations financieres finales
pour produire un rapport recapitulatif de cloture.
"""

import logging
from decimal import Decimal
from typing import List, Optional

from ...domain.repositories.budget_repository import BudgetRepository
from ...domain.repositories.lot_budgetaire_repository import LotBudgetaireRepository
from ...domain.repositories.achat_repository import AchatRepository
from ...domain.repositories.avenant_repository import AvenantRepository
from ...domain.repositories.situation_repository import SituationRepository
from ...domain.repositories.facture_repository import FactureRepository
from ...domain.repositories.cout_main_oeuvre_repository import CoutMainOeuvreRepository
from ...domain.repositories.cout_materiel_repository import CoutMaterielRepository
from ...domain.value_objects import StatutAchat
from ...domain.value_objects.statuts_financiers import STATUTS_ENGAGES, STATUTS_REALISES
from ..dtos.bilan_cloture_dtos import BilanClotureDTO, EcartLotDTO
from shared.application.ports.chantier_info_port import ChantierInfoPort
from shared.domain.calcul_financier import (
    calculer_marge_chantier,
    calculer_quote_part_frais_generaux,
    arrondir_pct,
)

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
        facture_repository: Optional[FactureRepository] = None,
        cout_mo_repository: Optional[CoutMainOeuvreRepository] = None,
        cout_materiel_repository: Optional[CoutMaterielRepository] = None,
    ) -> None:
        """Initialise le use case.

        Args:
            budget_repository: Repository Budget (interface).
            lot_repository: Repository LotBudgetaire (interface).
            achat_repository: Repository Achat (interface).
            avenant_repository: Repository Avenant (interface).
            situation_repository: Repository Situation (interface).
            chantier_info_port: Port pour infos chantier (nom, statut).
            facture_repository: Repository Facture pour calcul CA reel.
            cout_mo_repository: Repository Cout MO pour marge reelle.
            cout_materiel_repository: Repository Cout materiel pour marge reelle.
        """
        self.budget_repository = budget_repository
        self.lot_repository = lot_repository
        self.achat_repository = achat_repository
        self.avenant_repository = avenant_repository
        self.situation_repository = situation_repository
        self.chantier_info_port = chantier_info_port
        self.facture_repository = facture_repository
        self.cout_mo_repository = cout_mo_repository
        self.cout_materiel_repository = cout_materiel_repository

    def execute(
        self, chantier_id: int,
    ) -> BilanClotureDTO:
        """Genere le bilan de cloture pour un chantier.

        Frais generaux : coefficient unique COEFF_FRAIS_GENERAUX applique
        sur le debourse sec. Source unique, pas de parametre externe.

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
        # Engage = achats valides/commandes/livres/factures (PAS les demandes)
        # Utilise les constantes partagees STATUTS_ENGAGES pour coherence systeme
        total_engage_ht = self.achat_repository.somme_by_chantier(
            chantier_id, statuts=STATUTS_ENGAGES
        )

        # Realise = achats factures uniquement (coherent avec dashboard et P&L)
        # Utilise les constantes partagees STATUTS_REALISES
        total_realise_ht = self.achat_repository.somme_by_chantier(
            chantier_id, statuts=STATUTS_REALISES
        )

        # 4bis. Couts MO et materiel pour marge reelle
        cout_mo = Decimal("0")
        cout_materiel = Decimal("0")
        if self.cout_mo_repository:
            try:
                cout_mo = self.cout_mo_repository.calculer_cout_chantier(chantier_id)
            except Exception:
                logger.warning("Erreur calcul cout MO bilan chantier %d", chantier_id)
        if self.cout_materiel_repository:
            try:
                cout_materiel = self.cout_materiel_repository.calculer_cout_chantier(chantier_id)
            except Exception:
                logger.warning("Erreur calcul cout materiel bilan chantier %d", chantier_id)

        # 5. Calculer le reste non depense et la marge REELLE
        reste_non_depense_ht = budget_revise_ht - total_engage_ht - cout_mo - cout_materiel

        # Marge reelle = basee sur CA reel (factures client), pas sur le budget
        # Formule BTP unifiee : (CA - Cout revient) / CA x 100
        ca_ht = self._calculer_ca_reel(chantier_id)
        # Quote-part FG = coefficient unique sur debourse sec
        debourse_sec = total_realise_ht + cout_mo + cout_materiel
        quote_part = calculer_quote_part_frais_generaux(debourse_sec)
        marge_finale_pct = calculer_marge_chantier(
            ca_ht=ca_ht,
            cout_achats=total_realise_ht,
            cout_mo=cout_mo,
            cout_materiel=cout_materiel,
            quote_part_frais_generaux=quote_part,
        )
        marge_finale_ht = ca_ht - (total_realise_ht + cout_mo + cout_materiel + quote_part)

        # DM-3: Si CA=0, marge inconnue → None (pas 0% qui signifierait "équilibre")
        # marge_finale_pct reste None si calculer_marge_chantier retourne None

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
            total_realise_ht=str(total_realise_ht + cout_mo + cout_materiel),
            reste_non_depense_ht=str(reste_non_depense_ht),
            marge_finale_ht=str(marge_finale_ht),
            marge_finale_pct=str(marge_finale_pct) if marge_finale_pct is not None else None,
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

        for lot in lots:
            if lot.id is None:
                continue

            prevu_ht = lot.total_prevu_ht

            # Realise par lot = achats factures (coherent STATUTS_REALISES)
            realise_ht = self.achat_repository.somme_by_lot(
                lot.id, statuts=STATUTS_REALISES
            )

            ecart_ht = prevu_ht - realise_ht

            if prevu_ht > Decimal("0"):
                ecart_pct = arrondir_pct(ecart_ht / prevu_ht * Decimal("100"))
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

    def _calculer_ca_reel(self, chantier_id: int) -> Decimal:
        """Calcule le CA reel HT depuis les factures client emises.

        Le CA reel est la somme des factures emises/envoyees/payees.
        Utilise le meme calcul que le P&L pour coherence.

        Args:
            chantier_id: ID du chantier.

        Returns:
            Le CA HT reel. Decimal("0") si pas de factures ou repo indisponible.
        """
        if not self.facture_repository:
            # Fallback : utiliser la derniere situation de travaux
            derniere = self.situation_repository.find_derniere_situation(chantier_id)
            if derniere:
                return Decimal(str(derniere.montant_cumule_ht))
            return Decimal("0")

        statuts_ca = {"emise", "envoyee", "payee"}
        factures = self.facture_repository.find_by_chantier_id(chantier_id)
        ca = Decimal("0")
        for facture in factures:
            if facture.statut in statuts_ca:
                ca += facture.montant_ht
        return ca
