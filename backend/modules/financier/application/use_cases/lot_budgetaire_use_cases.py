"""Use Cases pour la gestion des lots budgétaires.

FIN-02: Décomposition en lots - Structure arborescente du budget.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..ports.event_bus import EventBus

from ...domain.entities import LotBudgetaire
from ...domain.repositories import (
    LotBudgetaireRepository,
    BudgetRepository,
    AchatRepository,
    JournalFinancierRepository,
    JournalEntry,
)
from ...domain.value_objects import StatutAchat
from ...domain.value_objects.statuts_financiers import STATUTS_ENGAGES, STATUTS_REALISES
from ...domain.events import (
    LotBudgetaireCreatedEvent,
    LotBudgetaireUpdatedEvent,
    LotBudgetaireDeletedEvent,
)
from ..dtos import (
    LotBudgetaireCreateDTO,
    LotBudgetaireUpdateDTO,
    LotBudgetaireDTO,
    LotBudgetaireListDTO,
)
from .budget_use_cases import BudgetNotFoundError


class LotNotFoundError(Exception):
    """Erreur levée quand un lot budgétaire n'est pas trouvé."""

    def __init__(self, lot_id: int):
        self.lot_id = lot_id
        super().__init__(f"Lot budgétaire {lot_id} non trouvé")


class LotCodeExistsError(Exception):
    """Erreur levée quand un code de lot existe déjà dans le budget."""

    def __init__(self, code_lot: str, budget_id: int):
        self.code_lot = code_lot
        self.budget_id = budget_id
        super().__init__(
            f"Le code lot '{code_lot}' existe déjà dans le budget {budget_id}"
        )


def _calculer_engage_realise(
    achat_repository: AchatRepository, lot_id: int
) -> tuple:
    """Calcule les montants engagé et réalisé pour un lot.

    Args:
        achat_repository: Le repository des achats.
        lot_id: L'ID du lot budgétaire.

    Returns:
        Tuple (engage, realise) en Decimal.
    """
    engage = achat_repository.somme_by_lot(lot_id, statuts=STATUTS_ENGAGES)
    realise = achat_repository.somme_by_lot(lot_id, statuts=STATUTS_REALISES)
    return engage, realise


class CreateLotBudgetaireUseCase:
    """Use case pour créer un lot budgétaire.

    FIN-02: Chaque lot appartient à un budget et a un code unique.
    """

    def __init__(
        self,
        lot_repository: LotBudgetaireRepository,
        budget_repository: BudgetRepository,
        achat_repository: AchatRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._lot_repository = lot_repository
        self._budget_repository = budget_repository
        self._achat_repository = achat_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, dto: LotBudgetaireCreateDTO, created_by: int) -> LotBudgetaireDTO:
        """Crée un nouveau lot budgétaire.

        Args:
            dto: Les données du lot à créer.
            created_by: L'ID de l'utilisateur créateur.

        Returns:
            Le DTO du lot créé.

        Raises:
            BudgetNotFoundError: Si le budget n'existe pas.
            LotCodeExistsError: Si le code existe déjà dans le budget.
        """
        # Vérifier que le budget existe
        budget = self._budget_repository.find_by_id(dto.budget_id)
        if not budget:
            raise BudgetNotFoundError(budget_id=dto.budget_id)

        # Vérifier unicité du code dans le budget
        existing = self._lot_repository.find_by_code(dto.budget_id, dto.code_lot)
        if existing:
            raise LotCodeExistsError(dto.code_lot, dto.budget_id)

        # Créer l'entité
        lot = LotBudgetaire(
            budget_id=dto.budget_id,
            code_lot=dto.code_lot,
            libelle=dto.libelle,
            unite=dto.unite,
            quantite_prevue=dto.quantite_prevue,
            prix_unitaire_ht=dto.prix_unitaire_ht,
            parent_lot_id=dto.parent_lot_id,
            ordre=dto.ordre,
            created_at=datetime.utcnow(),
            created_by=created_by,
        )

        # Persister
        lot = self._lot_repository.save(lot)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="lot_budgetaire",
                entite_id=lot.id,
                chantier_id=budget.chantier_id,
                action="creation",
                details=(
                    f"Création du lot '{lot.code_lot} - {lot.libelle}' "
                    f"- Prévu: {lot.total_prevu_ht} EUR HT"
                ),
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        # Publier l'event
        self._event_bus.publish(
            LotBudgetaireCreatedEvent(
                lot_id=lot.id,
                budget_id=lot.budget_id,
                code_lot=lot.code_lot,
                libelle=lot.libelle,
                total_prevu_ht=lot.total_prevu_ht,
                created_by=created_by,
            )
        )

        return LotBudgetaireDTO.from_entity(lot)


class UpdateLotBudgetaireUseCase:
    """Use case pour mettre à jour un lot budgétaire."""

    def __init__(
        self,
        lot_repository: LotBudgetaireRepository,
        achat_repository: AchatRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._lot_repository = lot_repository
        self._achat_repository = achat_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(
        self, lot_id: int, dto: LotBudgetaireUpdateDTO, updated_by: int
    ) -> LotBudgetaireDTO:
        """Met à jour un lot budgétaire.

        Args:
            lot_id: L'ID du lot à mettre à jour.
            dto: Les données à mettre à jour.
            updated_by: L'ID de l'utilisateur.

        Returns:
            Le DTO du lot mis à jour.

        Raises:
            LotNotFoundError: Si le lot n'existe pas.
            LotCodeExistsError: Si le nouveau code existe déjà.
        """
        lot = self._lot_repository.find_by_id(lot_id)
        if not lot:
            raise LotNotFoundError(lot_id)

        modifications = []

        # Vérifier unicité du code si modifié
        if dto.code_lot is not None and dto.code_lot != lot.code_lot:
            existing = self._lot_repository.find_by_code(lot.budget_id, dto.code_lot)
            if existing and existing.id != lot_id:
                raise LotCodeExistsError(dto.code_lot, lot.budget_id)
            lot.code_lot = dto.code_lot
            modifications.append("code_lot")

        # Appliquer les modifications
        if dto.libelle is not None:
            lot.libelle = dto.libelle
            modifications.append("libelle")
        if dto.unite is not None:
            lot.unite = dto.unite
            modifications.append("unite")
        if dto.quantite_prevue is not None:
            lot.quantite_prevue = dto.quantite_prevue
            modifications.append("quantite_prevue")
        if dto.prix_unitaire_ht is not None:
            lot.prix_unitaire_ht = dto.prix_unitaire_ht
            modifications.append("prix_unitaire_ht")
        if dto.parent_lot_id is not None:
            lot.parent_lot_id = dto.parent_lot_id
            modifications.append("parent_lot_id")
        if dto.ordre is not None:
            lot.ordre = dto.ordre
            modifications.append("ordre")

        lot.updated_at = datetime.utcnow()

        # Persister
        lot = self._lot_repository.save(lot)

        # Journal
        for champ in modifications:
            self._journal_repository.save(
                JournalEntry(
                    entite_type="lot_budgetaire",
                    entite_id=lot.id,
                    action="modification",
                    details=f"Modification du champ '{champ}'",
                    auteur_id=updated_by,
                    created_at=datetime.utcnow(),
                )
            )

        # Publier l'event
        self._event_bus.publish(
            LotBudgetaireUpdatedEvent(
                lot_id=lot.id,
                budget_id=lot.budget_id,
                code_lot=lot.code_lot,
                total_prevu_ht=lot.total_prevu_ht,
                updated_by=updated_by,
            )
        )

        # Enrichir avec engage/realise
        engage, realise = _calculer_engage_realise(self._achat_repository, lot.id)

        return LotBudgetaireDTO.from_entity(lot, engage=engage, realise=realise)


class DeleteLotBudgetaireUseCase:
    """Use case pour supprimer un lot budgétaire (soft delete)."""

    def __init__(
        self,
        lot_repository: LotBudgetaireRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._lot_repository = lot_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, lot_id: int, deleted_by: int) -> bool:
        """Supprime un lot budgétaire (soft delete).

        Args:
            lot_id: L'ID du lot à supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprimé.

        Raises:
            LotNotFoundError: Si le lot n'existe pas.
        """
        lot = self._lot_repository.find_by_id(lot_id)
        if not lot:
            raise LotNotFoundError(lot_id)

        deleted = self._lot_repository.delete(lot_id, deleted_by=deleted_by)

        if deleted:
            # Journal
            self._journal_repository.save(
                JournalEntry(
                    entite_type="lot_budgetaire",
                    entite_id=lot_id,
                    action="suppression",
                    details=(
                        f"Suppression du lot '{lot.code_lot} - {lot.libelle}'"
                    ),
                    auteur_id=deleted_by,
                    created_at=datetime.utcnow(),
                )
            )

            # Event
            self._event_bus.publish(
                LotBudgetaireDeletedEvent(
                    lot_id=lot_id,
                    budget_id=lot.budget_id,
                    deleted_by=deleted_by,
                )
            )

        return deleted


class GetLotBudgetaireUseCase:
    """Use case pour récupérer un lot budgétaire avec enrichissement."""

    def __init__(
        self,
        lot_repository: LotBudgetaireRepository,
        achat_repository: AchatRepository,
    ):
        self._lot_repository = lot_repository
        self._achat_repository = achat_repository

    def execute(self, lot_id: int) -> LotBudgetaireDTO:
        """Récupère un lot budgétaire par son ID avec enrichissement.

        Args:
            lot_id: L'ID du lot.

        Returns:
            Le DTO du lot avec engage/realise calculés.

        Raises:
            LotNotFoundError: Si le lot n'existe pas.
        """
        lot = self._lot_repository.find_by_id(lot_id)
        if not lot:
            raise LotNotFoundError(lot_id)

        engage, realise = _calculer_engage_realise(self._achat_repository, lot.id)

        return LotBudgetaireDTO.from_entity(lot, engage=engage, realise=realise)


class ListLotsBudgetairesUseCase:
    """Use case pour lister les lots budgétaires d'un budget."""

    def __init__(
        self,
        lot_repository: LotBudgetaireRepository,
        achat_repository: AchatRepository,
    ):
        self._lot_repository = lot_repository
        self._achat_repository = achat_repository

    def execute(
        self,
        budget_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> LotBudgetaireListDTO:
        """Liste les lots budgétaires d'un budget avec enrichissement.

        Args:
            budget_id: L'ID du budget.
            limit: Nombre max de résultats.
            offset: Décalage pour pagination.

        Returns:
            Liste paginée de lots avec engage/realise.
        """
        lots = self._lot_repository.find_all_by_budget(
            budget_id=budget_id,
            limit=limit,
            offset=offset,
        )
        total = self._lot_repository.count_by_budget(budget_id)

        items = []
        for lot in lots:
            engage, realise = _calculer_engage_realise(
                self._achat_repository, lot.id
            )
            items.append(
                LotBudgetaireDTO.from_entity(lot, engage=engage, realise=realise)
            )

        return LotBudgetaireListDTO(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )
