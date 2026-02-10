"""Use Cases pour le Profit & Loss par chantier.

GAP #9: Vue P&L montrant CA, couts reels et marges par chantier.
"""

import logging
from decimal import Decimal
from typing import List, Optional

from shared.domain.calcul_financier import (
    calculer_marge_chantier,
    calculer_quote_part_frais_generaux,
    COUTS_FIXES_ANNUELS,
)

from ...domain.repositories.facture_repository import FactureRepository
from ...domain.repositories.achat_repository import AchatRepository
from ...domain.repositories.budget_repository import BudgetRepository
from ...domain.repositories.cout_main_oeuvre_repository import CoutMainOeuvreRepository
from ...domain.repositories.cout_materiel_repository import CoutMaterielRepository
from ...domain.value_objects.statut_achat import StatutAchat
from ..dtos.pnl_dtos import LignePnLDTO, PnLChantierDTO
from shared.application.ports.chantier_info_port import ChantierInfoPort


logger = logging.getLogger(__name__)

# Statuts de facture consideres comme CA (facture emise au client)
STATUTS_FACTURE_CA = {"emise", "envoyee", "payee"}


class PnLChantierNotFoundError(Exception):
    """Erreur levee quand le chantier n'a pas de budget pour le P&L."""

    def __init__(self, chantier_id: int):
        self.chantier_id = chantier_id
        super().__init__(
            f"Aucun budget trouve pour le chantier {chantier_id}"
        )


class GetPnLChantierUseCase:
    """Use case pour calculer le Profit & Loss d'un chantier.

    Agrege :
    - CA : somme des factures client emises (statut emise/envoyee/payee)
    - Couts achats : somme des achats factures (statut FACTURE)
    - Couts MO : pointages valides x taux horaire
    - Couts materiel : reservations x tarif journalier
    - Marge brute = CA - Total couts
    - Marge brute % = Marge brute / CA (0 si CA = 0)

    Attributes:
        _facture_repository: Repository des factures client.
        _achat_repository: Repository des achats.
        _budget_repository: Repository des budgets.
        _cout_mo_repository: Repository des couts main-d'oeuvre.
        _cout_materiel_repository: Repository des couts materiel.
        _chantier_info_port: Port pour les infos chantier (statut).
    """

    def __init__(
        self,
        facture_repository: FactureRepository,
        achat_repository: AchatRepository,
        budget_repository: BudgetRepository,
        cout_mo_repository: CoutMainOeuvreRepository,
        cout_materiel_repository: CoutMaterielRepository,
        chantier_info_port: Optional[ChantierInfoPort] = None,
    ):
        """Initialise le use case.

        Args:
            facture_repository: Repository des factures client.
            achat_repository: Repository des achats.
            budget_repository: Repository des budgets.
            cout_mo_repository: Repository des couts main-d'oeuvre.
            cout_materiel_repository: Repository des couts materiel.
            chantier_info_port: Port pour obtenir le statut du chantier.
        """
        self._facture_repository = facture_repository
        self._achat_repository = achat_repository
        self._budget_repository = budget_repository
        self._cout_mo_repository = cout_mo_repository
        self._cout_materiel_repository = cout_materiel_repository
        self._chantier_info_port = chantier_info_port

    def execute(
        self, chantier_id: int, ca_total_annee: Optional[Decimal] = None
    ) -> PnLChantierDTO:
        """Calcule le P&L d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            ca_total_annee: CA total annuel de l'entreprise pour repartition
                des couts fixes. Si None, les frais generaux ne sont pas repartis.

        Returns:
            Le P&L complet du chantier.

        Raises:
            PnLChantierNotFoundError: Si le chantier n'a pas de budget.
        """
        # 1. Recuperer le budget pour reference
        budget = self._budget_repository.find_by_chantier_id(chantier_id)
        if not budget:
            raise PnLChantierNotFoundError(chantier_id)

        budget_initial_ht = budget.montant_initial_ht
        budget_revise_ht = budget.montant_revise_ht

        # 2. Calculer le CA : somme des factures emises/envoyees/payees
        chiffre_affaires_ht = self._calculer_ca(chantier_id)

        # 3. Calculer les couts
        cout_achats = self._calculer_cout_achats(chantier_id)
        cout_mo = self._calculer_cout_main_oeuvre(chantier_id)
        cout_materiel = self._calculer_cout_materiel(chantier_id)

        total_couts = cout_achats + cout_mo + cout_materiel

        # 4. Calculer les marges (formule BTP unifiee via calcul_financier.py)
        # Quote-part frais generaux via fonction unifiee
        # ATTENTION: si ca_total_annee non fourni, marge surestimee (~14%)
        effective_ca_total = ca_total_annee or Decimal("0")
        if effective_ca_total <= Decimal("0"):
            logger.warning(
                "P&L chantier %d: ca_total_annee non fourni, "
                "frais generaux non repartis (marge potentiellement surestimee)",
                chantier_id,
            )
        quote_part = calculer_quote_part_frais_generaux(
            ca_chantier_ht=chiffre_affaires_ht,
            ca_total_annee=effective_ca_total,
            couts_fixes_annuels=COUTS_FIXES_ANNUELS,
        )
        marge_brute_ht = chiffre_affaires_ht - (total_couts + quote_part)
        marge_brute_pct = calculer_marge_chantier(
            ca_ht=chiffre_affaires_ht,
            cout_achats=cout_achats,
            cout_mo=cout_mo,
            cout_materiel=cout_materiel,
            quote_part_frais_generaux=quote_part,
        )
        if marge_brute_pct is None:
            marge_brute_pct = Decimal("0")

        # 5. Determiner si le chantier est ferme
        est_definitif = self._est_chantier_ferme(chantier_id)

        # 6. Construire les lignes de detail
        detail_couts = self._construire_detail_couts(
            chantier_id, cout_achats, cout_mo, cout_materiel
        )

        return PnLChantierDTO(
            chantier_id=chantier_id,
            chiffre_affaires_ht=str(chiffre_affaires_ht),
            total_couts=str(total_couts),
            cout_achats=str(cout_achats),
            cout_main_oeuvre=str(cout_mo),
            cout_materiel=str(cout_materiel),
            marge_brute_ht=str(marge_brute_ht),
            marge_brute_pct=str(marge_brute_pct),
            budget_initial_ht=str(budget_initial_ht),
            budget_revise_ht=str(budget_revise_ht),
            detail_couts=detail_couts,
            est_definitif=est_definitif,
        )

    def _calculer_ca(self, chantier_id: int) -> Decimal:
        """Calcule le chiffre d'affaires HT a partir des factures emises.

        Somme des montant_ht des factures avec statut emise, envoyee ou payee.
        Les factures brouillon et annulees sont exclues.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Le CA total HT.
        """
        factures = self._facture_repository.find_by_chantier_id(chantier_id)
        ca = Decimal("0")
        for facture in factures:
            if facture.statut in STATUTS_FACTURE_CA:
                ca += facture.montant_ht
        return ca

    def _calculer_cout_achats(self, chantier_id: int) -> Decimal:
        """Calcule le cout total des achats factures.

        Utilise somme_by_chantier avec le statut FACTURE (achats reellement payes).

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Le total des achats factures HT.
        """
        return self._achat_repository.somme_by_chantier(
            chantier_id, statuts=[StatutAchat.FACTURE]
        )

    def _calculer_cout_main_oeuvre(self, chantier_id: int) -> Decimal:
        """Calcule le cout total main-d'oeuvre.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Le cout total MO.
        """
        try:
            return self._cout_mo_repository.calculer_cout_chantier(chantier_id)
        except Exception:
            logger.warning(
                "Erreur calcul cout MO pour chantier %d, retour 0",
                chantier_id,
            )
            return Decimal("0")

    def _calculer_cout_materiel(self, chantier_id: int) -> Decimal:
        """Calcule le cout total materiel INTERNE (parc propre).

        Ce cout concerne uniquement le materiel du parc propre de l'entreprise
        (amortissement, location interne). Les achats de materiel chez
        des fournisseurs sont comptabilises dans _calculer_cout_achats
        via AchatRepository. Ne PAS confondre pour eviter double comptage.

        Note: le module logistique (table ressources) n'est pas encore
        implemente. Cette methode retourne 0 en cas d'erreur.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Le cout total materiel interne.
        """
        try:
            return self._cout_materiel_repository.calculer_cout_chantier(
                chantier_id
            )
        except Exception:
            logger.warning(
                "Erreur calcul cout materiel pour chantier %d, retour 0",
                chantier_id,
            )
            return Decimal("0")

    def _est_chantier_ferme(self, chantier_id: int) -> bool:
        """Determine si le chantier est ferme (P&L definitif).

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            True si le chantier est ferme.
        """
        if self._chantier_info_port is None:
            return False
        try:
            info = self._chantier_info_port.get_chantier_info(chantier_id)
            if info is not None:
                return info.statut == "ferme"
        except Exception:
            logger.warning(
                "Erreur acces info chantier %d, est_definitif=False",
                chantier_id,
            )
        return False

    def _construire_detail_couts(
        self,
        chantier_id: int,
        cout_achats: Decimal,
        cout_mo: Decimal,
        cout_materiel: Decimal,
    ) -> List[LignePnLDTO]:
        """Construit les lignes de detail du P&L.

        Args:
            chantier_id: L'ID du chantier.
            cout_achats: Cout total achats.
            cout_mo: Cout total main-d'oeuvre.
            cout_materiel: Cout total materiel.

        Returns:
            Liste des lignes de detail.
        """
        lignes: List[LignePnLDTO] = []

        if cout_achats > Decimal("0"):
            lignes.append(
                LignePnLDTO(
                    categorie="achats",
                    libelle="Achats factures",
                    montant=str(cout_achats),
                )
            )

        if cout_mo > Decimal("0"):
            lignes.append(
                LignePnLDTO(
                    categorie="main_oeuvre",
                    libelle="Main-d'oeuvre (pointages valides)",
                    montant=str(cout_mo),
                )
            )

        if cout_materiel > Decimal("0"):
            lignes.append(
                LignePnLDTO(
                    categorie="materiel",
                    libelle="Materiel (reservations)",
                    montant=str(cout_materiel),
                )
            )

        return lignes
