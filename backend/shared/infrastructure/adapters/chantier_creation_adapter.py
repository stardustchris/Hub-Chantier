"""Adapter pour la creation d'un chantier depuis un devis.

Implementation concrete du ChantierCreationPort.
C'est dans cette couche Infrastructure que les imports cross-module sont autorises.

DEV-16: Conversion devis -> chantier.
"""

import logging
from decimal import Decimal

from shared.application.ports.chantier_creation_port import (
    ChantierCreationPort,
    ChantierCreationData,
    BudgetCreationData,
    LotBudgetaireCreationData,
    ConversionChantierResult,
)
from shared.infrastructure.connectors.security import sanitize_text

# Cross-module imports autorises en couche Infrastructure
from modules.chantiers.domain.entities import Chantier
from modules.chantiers.domain.repositories import ChantierRepository
from modules.chantiers.domain.value_objects import CodeChantier, StatutChantier
from modules.financier.domain.entities import Budget, LotBudgetaire
from modules.financier.domain.repositories.budget_repository import BudgetRepository
from modules.financier.domain.repositories.lot_budgetaire_repository import (
    LotBudgetaireRepository,
)
from modules.financier.domain.value_objects import UniteMesure

logger = logging.getLogger(__name__)


class ChantierCreationAdapter(ChantierCreationPort):
    """Implementation concrete du port de creation chantier.

    Utilise les repositories des modules chantiers et financier
    pour creer les entites. Les imports cross-module sont ici
    dans la couche Infrastructure, conformement a Clean Architecture.
    """

    def __init__(
        self,
        chantier_repo: ChantierRepository,
        budget_repo: BudgetRepository,
        lot_budgetaire_repo: LotBudgetaireRepository,
    ) -> None:
        """Initialise l'adapter.

        Args:
            chantier_repo: Repository chantiers (interface).
            budget_repo: Repository budgets (interface).
            lot_budgetaire_repo: Repository lots budgetaires (interface).
        """
        self._chantier_repo = chantier_repo
        self._budget_repo = budget_repo
        self._lot_budgetaire_repo = lot_budgetaire_repo

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
        # 1. Sanitizer les champs texte (DEFAUT 3)
        nom = sanitize_text(chantier_data.nom, max_length=200)
        adresse = sanitize_text(chantier_data.adresse, max_length=500)
        description = None
        if chantier_data.description:
            description = sanitize_text(chantier_data.description, max_length=2000)

        # 2. Generer le prochain code chantier
        last_code = self._chantier_repo.get_last_code()
        code = CodeChantier.generate_next(last_code)

        # 3. Creer l'entite Chantier
        chantier = Chantier(
            code=code,
            nom=nom,
            adresse=adresse,
            statut=StatutChantier.ouvert(),
            conducteur_ids=chantier_data.conducteur_ids,
            description=description,
        )
        chantier = self._chantier_repo.save(chantier)

        # 4. Creer le budget
        budget = Budget(
            chantier_id=chantier.id,
            montant_initial_ht=budget_data.montant_initial_ht,
            montant_avenants_ht=Decimal("0"),
            retenue_garantie_pct=budget_data.retenue_garantie_pct,
            seuil_alerte_pct=budget_data.seuil_alerte_pct,
            seuil_validation_achat=budget_data.seuil_validation_achat,
            notes=f"Budget initial depuis conversion devis",
        )
        budget = self._budget_repo.save(budget)

        # 5. Creer les lots budgetaires
        nb_lots = 0
        for lot_data in lots_data:
            lot_budgetaire = LotBudgetaire(
                budget_id=budget.id,
                devis_id=None,
                code_lot=lot_data.code_lot,
                libelle=lot_data.libelle,
                unite=UniteMesure.U,
                quantite_prevue=lot_data.quantite_prevue,
                prix_unitaire_ht=lot_data.prix_unitaire_ht,
                ordre=lot_data.ordre,
                prix_vente_ht=lot_data.prix_vente_ht,
            )
            self._lot_budgetaire_repo.save(lot_budgetaire)
            nb_lots += 1

        logger.info(
            "Chantier cree depuis devis via adapter",
            extra={
                "event": "adapter.chantier_creation.success",
                "chantier_id": chantier.id,
                "code_chantier": str(chantier.code),
                "budget_id": budget.id,
                "nb_lots": nb_lots,
            },
        )

        # 6. Retourner le resultat
        return ConversionChantierResult(
            chantier_id=chantier.id,
            code_chantier=str(chantier.code),
            budget_id=budget.id,
            nb_lots_transferes=nb_lots,
        )
