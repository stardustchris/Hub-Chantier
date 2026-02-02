"""Port pour la creation d'un chantier depuis un devis.

Ce port permet au module devis de declencher la creation d'un chantier
sans dependre directement des modules chantiers/financier.

Conforme Clean Architecture:
- Interface definie dans Application layer (shared)
- Implementation dans Infrastructure layer (shared)
- Aucun import de modules specifiques
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class ChantierCreationData:
    """Donnees necessaires pour creer un chantier depuis un devis."""

    nom: str
    adresse: str
    description: Optional[str]
    conducteur_ids: list[int]
    statut: str = "OUVERT"


@dataclass
class BudgetCreationData:
    """Donnees necessaires pour creer un budget."""

    montant_initial_ht: Decimal
    retenue_garantie_pct: Decimal
    seuil_alerte_pct: Decimal = Decimal("80")
    seuil_validation_achat: Decimal = Decimal("5000")


@dataclass
class LotBudgetaireCreationData:
    """Donnees necessaires pour creer un lot budgetaire."""

    code_lot: str
    libelle: str
    unite: str
    quantite_prevue: Decimal
    prix_unitaire_ht: Decimal
    ordre: int
    prix_vente_ht: Optional[Decimal] = None


@dataclass
class ConversionChantierResult:
    """Resultat de la creation d'un chantier depuis un devis."""

    chantier_id: int
    code_chantier: str
    budget_id: int
    nb_lots_transferes: int


class ChantierCreationPort(ABC):
    """Port pour creer un chantier + budget + lots depuis le module devis.

    Ce port permet au module devis de declencher la creation d'un chantier
    sans dependre directement des modules chantiers/financier.
    """

    @abstractmethod
    def create_chantier_from_devis(
        self,
        chantier_data: ChantierCreationData,
        budget_data: BudgetCreationData,
        lots_data: list[LotBudgetaireCreationData],
    ) -> ConversionChantierResult:
        """Cree un chantier, un budget et des lots budgetaires.

        Args:
            chantier_data: Donnees du chantier a creer.
            budget_data: Donnees du budget a creer.
            lots_data: Donnees des lots budgetaires a creer.

        Returns:
            ConversionChantierResult avec les IDs crees.
        """
        ...
