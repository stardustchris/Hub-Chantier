"""Use Cases pour les affectations budget-tache.

FIN-03: Affectation budgets aux taches - Creation, suppression, consultation.
"""

import logging
from decimal import Decimal
from typing import List

from ...domain.entities.affectation_budget_tache import AffectationBudgetTache
from ...domain.repositories.affectation_repository import AffectationBudgetTacheRepository
from ...domain.repositories.lot_budgetaire_repository import LotBudgetaireRepository
from ..dtos.affectation_dtos import (
    AffectationAvecDetailsDTO,
    AffectationBudgetTacheDTO,
    CreateAffectationDTO,
)

logger = logging.getLogger(__name__)


class AffectationNotFoundError(Exception):
    """Exception lorsque l'affectation n'est pas trouvee."""

    def __init__(self, message: str = "Affectation non trouvee"):
        self.message = message
        super().__init__(self.message)


class AllocationDepasseError(Exception):
    """Exception lorsque la somme des allocations depasse 100% pour un lot."""

    def __init__(self, message: str = "La somme des allocations depasse 100%"):
        self.message = message
        super().__init__(self.message)


class LotBudgetaireIntrouvableError(Exception):
    """Exception lorsque le lot budgetaire n'existe pas."""

    def __init__(self, message: str = "Lot budgetaire non trouve"):
        self.message = message
        super().__init__(self.message)


class CreateAffectationBudgetTacheUseCase:
    """Cas d'utilisation : Creer une affectation budget-tache.

    Verifie que le lot budgetaire existe et que la somme des allocations
    pour ce lot ne depasse pas 100%.

    Attributes:
        affectation_repo: Repository pour les affectations.
        lot_repo: Repository pour les lots budgetaires.
    """

    def __init__(
        self,
        affectation_repo: AffectationBudgetTacheRepository,
        lot_repo: LotBudgetaireRepository,
    ):
        """Initialise le use case.

        Args:
            affectation_repo: Repository affectation (interface).
            lot_repo: Repository lot budgetaire (interface).
        """
        self.affectation_repo = affectation_repo
        self.lot_repo = lot_repo

    def execute(self, dto: CreateAffectationDTO) -> AffectationBudgetTacheDTO:
        """Execute la creation d'une affectation.

        Args:
            dto: Les donnees de creation.

        Returns:
            AffectationBudgetTacheDTO contenant l'affectation creee.

        Raises:
            LotBudgetaireIntrouvableError: Si le lot n'existe pas.
            AllocationDepasseError: Si la somme des allocations depasse 100%.
        """
        # 1. Verifier que le lot existe
        lot = self.lot_repo.find_by_id(dto.lot_budgetaire_id)
        if not lot:
            raise LotBudgetaireIntrouvableError(
                f"Lot budgetaire {dto.lot_budgetaire_id} non trouve"
            )

        # 2. Verifier la somme des allocations existantes
        existing = self.affectation_repo.find_by_lot(dto.lot_budgetaire_id)
        total_existant = sum(a.pourcentage_allocation for a in existing)
        if total_existant + dto.pourcentage_allocation > Decimal("100"):
            raise AllocationDepasseError(
                f"La somme des allocations pour le lot {dto.lot_budgetaire_id} "
                f"depasserait 100% ({total_existant} + {dto.pourcentage_allocation} "
                f"= {total_existant + dto.pourcentage_allocation}%)"
            )

        # 3. Creer l'entite
        affectation = AffectationBudgetTache(
            lot_budgetaire_id=dto.lot_budgetaire_id,
            tache_id=dto.tache_id,
            pourcentage_allocation=dto.pourcentage_allocation,
        )

        # 4. Persister
        affectation = self.affectation_repo.save(affectation)
        logger.info(
            "Affectation creee: lot=%s tache=%s pct=%s",
            dto.lot_budgetaire_id, dto.tache_id, dto.pourcentage_allocation,
        )

        return AffectationBudgetTacheDTO.from_entity(affectation)


class DeleteAffectationBudgetTacheUseCase:
    """Cas d'utilisation : Supprimer une affectation budget-tache.

    Attributes:
        affectation_repo: Repository pour les affectations.
    """

    def __init__(self, affectation_repo: AffectationBudgetTacheRepository):
        """Initialise le use case.

        Args:
            affectation_repo: Repository affectation (interface).
        """
        self.affectation_repo = affectation_repo

    def execute(self, affectation_id: int) -> None:
        """Execute la suppression d'une affectation.

        Args:
            affectation_id: L'ID de l'affectation a supprimer.

        Raises:
            AffectationNotFoundError: Si l'affectation n'existe pas.
        """
        existing = self.affectation_repo.find_by_id(affectation_id)
        if not existing:
            raise AffectationNotFoundError(
                f"Affectation {affectation_id} non trouvee"
            )
        self.affectation_repo.delete(affectation_id)
        logger.info("Affectation supprimee: id=%s", affectation_id)


class ListAffectationsByChantierUseCase:
    """Cas d'utilisation : Lister les affectations d'un chantier avec details lots.

    Attributes:
        affectation_repo: Repository pour les affectations.
        lot_repo: Repository pour les lots budgetaires.
    """

    def __init__(
        self,
        affectation_repo: AffectationBudgetTacheRepository,
        lot_repo: LotBudgetaireRepository,
    ):
        """Initialise le use case.

        Args:
            affectation_repo: Repository affectation (interface).
            lot_repo: Repository lot budgetaire (interface).
        """
        self.affectation_repo = affectation_repo
        self.lot_repo = lot_repo

    def execute(self, chantier_id: int) -> List[AffectationAvecDetailsDTO]:
        """Execute la liste des affectations d'un chantier avec details.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Liste des affectations avec details des lots.
        """
        affectations = self.affectation_repo.find_by_chantier(chantier_id)

        # Charger les details des lots
        lots_cache: dict = {}
        result: List[AffectationAvecDetailsDTO] = []

        for aff in affectations:
            if aff.lot_budgetaire_id not in lots_cache:
                lot = self.lot_repo.find_by_id(aff.lot_budgetaire_id)
                lots_cache[aff.lot_budgetaire_id] = lot

            lot = lots_cache.get(aff.lot_budgetaire_id)
            total_prevu = (
                lot.quantite_prevue * lot.prix_unitaire_ht
                if lot else Decimal("0")
            )

            result.append(
                AffectationAvecDetailsDTO(
                    id=aff.id,
                    lot_budgetaire_id=aff.lot_budgetaire_id,
                    tache_id=aff.tache_id,
                    pourcentage_allocation=str(aff.pourcentage_allocation),
                    code_lot=lot.code_lot if lot else "",
                    libelle_lot=lot.libelle if lot else "",
                    total_prevu_ht=str(total_prevu),
                    created_at=aff.created_at,
                    updated_at=aff.updated_at,
                )
            )

        return result


class GetAffectationsByTacheUseCase:
    """Cas d'utilisation : Recuperer les lots affectes a une tache.

    Attributes:
        affectation_repo: Repository pour les affectations.
        lot_repo: Repository pour les lots budgetaires.
    """

    def __init__(
        self,
        affectation_repo: AffectationBudgetTacheRepository,
        lot_repo: LotBudgetaireRepository,
    ):
        """Initialise le use case.

        Args:
            affectation_repo: Repository affectation (interface).
            lot_repo: Repository lot budgetaire (interface).
        """
        self.affectation_repo = affectation_repo
        self.lot_repo = lot_repo

    def execute(self, tache_id: int) -> List[AffectationAvecDetailsDTO]:
        """Execute la recuperation des lots affectes a une tache.

        Args:
            tache_id: L'ID de la tache.

        Returns:
            Liste des affectations avec details des lots.
        """
        affectations = self.affectation_repo.find_by_tache(tache_id)

        result: List[AffectationAvecDetailsDTO] = []
        for aff in affectations:
            lot = self.lot_repo.find_by_id(aff.lot_budgetaire_id)
            total_prevu = (
                lot.quantite_prevue * lot.prix_unitaire_ht
                if lot else Decimal("0")
            )

            result.append(
                AffectationAvecDetailsDTO(
                    id=aff.id,
                    lot_budgetaire_id=aff.lot_budgetaire_id,
                    tache_id=aff.tache_id,
                    pourcentage_allocation=str(aff.pourcentage_allocation),
                    code_lot=lot.code_lot if lot else "",
                    libelle_lot=lot.libelle if lot else "",
                    total_prevu_ht=str(total_prevu),
                    created_at=aff.created_at,
                    updated_at=aff.updated_at,
                )
            )

        return result
