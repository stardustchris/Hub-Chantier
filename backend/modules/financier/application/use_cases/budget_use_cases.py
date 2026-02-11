"""Use Cases pour la gestion des budgets.

FIN-01: Budget prévisionnel - Enveloppe budgétaire par chantier.
"""

from datetime import datetime
from typing import Optional

from ..ports.event_bus import EventBus

from ...domain.entities import Budget
from ...domain.repositories import (
    BudgetRepository,
    JournalFinancierRepository,
    JournalEntry,
)
from ...domain.events import BudgetCreatedEvent, BudgetUpdatedEvent
from ..dtos import BudgetCreateDTO, BudgetUpdateDTO, BudgetDTO


class BudgetNotFoundError(Exception):
    """Erreur levée quand un budget n'est pas trouvé."""

    def __init__(self, budget_id: int = 0, chantier_id: int = 0):
        self.budget_id = budget_id
        self.chantier_id = chantier_id
        if budget_id:
            super().__init__(f"Budget {budget_id} non trouvé")
        else:
            super().__init__(f"Budget du chantier {chantier_id} non trouvé")


class BudgetAlreadyExistsError(Exception):
    """Erreur levée quand un budget existe déjà pour un chantier."""

    def __init__(self, chantier_id: int):
        self.chantier_id = chantier_id
        super().__init__(
            f"Un budget existe déjà pour le chantier {chantier_id}"
        )


class CreateBudgetUseCase:
    """Use case pour créer un budget.

    FIN-01: Un seul budget par chantier.
    """

    def __init__(
        self,
        budget_repository: BudgetRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._budget_repository = budget_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, dto: BudgetCreateDTO, created_by: int) -> BudgetDTO:
        """Crée un nouveau budget pour un chantier.

        Args:
            dto: Les données du budget à créer.
            created_by: L'ID de l'utilisateur créateur.

        Returns:
            Le DTO du budget créé.

        Raises:
            BudgetAlreadyExistsError: Si un budget existe déjà pour ce chantier.
        """
        # Vérifier unicité par chantier
        existing = self._budget_repository.find_by_chantier_id(dto.chantier_id)
        if existing:
            raise BudgetAlreadyExistsError(dto.chantier_id)

        # Créer l'entité
        budget = Budget(
            chantier_id=dto.chantier_id,
            montant_initial_ht=dto.montant_initial_ht,
            retenue_garantie_pct=dto.retenue_garantie_pct,
            seuil_alerte_pct=dto.seuil_alerte_pct,
            seuil_validation_achat=dto.seuil_validation_achat,
            notes=dto.notes,
            created_at=datetime.utcnow(),
            created_by=created_by,
        )

        # Persister
        budget = self._budget_repository.save(budget)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="budget",
                entite_id=budget.id,
                chantier_id=budget.chantier_id,
                action="creation",
                details=(
                    f"Création du budget - Montant initial: "
                    f"{budget.montant_initial_ht} EUR HT"
                ),
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        # Publier l'event
        self._event_bus.publish(
            BudgetCreatedEvent(
                budget_id=budget.id,
                chantier_id=budget.chantier_id,
                montant_initial_ht=budget.montant_initial_ht,
                created_by=created_by,
            )
        )

        return BudgetDTO.from_entity(budget)


class UpdateBudgetUseCase:
    """Use case pour mettre à jour un budget."""

    def __init__(
        self,
        budget_repository: BudgetRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._budget_repository = budget_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(
        self, budget_id: int, dto: BudgetUpdateDTO, updated_by: int
    ) -> BudgetDTO:
        """Met à jour un budget.

        Args:
            budget_id: L'ID du budget à mettre à jour.
            dto: Les données à mettre à jour.
            updated_by: L'ID de l'utilisateur.

        Returns:
            Le DTO du budget mis à jour.

        Raises:
            BudgetNotFoundError: Si le budget n'existe pas.
        """
        budget = self._budget_repository.find_by_id(budget_id)
        if not budget:
            raise BudgetNotFoundError(budget_id=budget_id)

        modifications = []

        # Appliquer les modifications
        if dto.montant_initial_ht is not None:
            budget.montant_initial_ht = dto.montant_initial_ht
            modifications.append("montant_initial_ht")
        if dto.retenue_garantie_pct is not None:
            budget.modifier_retenue_garantie(dto.retenue_garantie_pct)
            modifications.append("retenue_garantie_pct")
        if dto.seuil_alerte_pct is not None:
            budget.seuil_alerte_pct = dto.seuil_alerte_pct
            modifications.append("seuil_alerte_pct")
        if dto.seuil_validation_achat is not None:
            budget.seuil_validation_achat = dto.seuil_validation_achat
            modifications.append("seuil_validation_achat")
        if dto.notes is not None:
            budget.notes = dto.notes
            modifications.append("notes")

        budget.updated_at = datetime.utcnow()

        # Persister
        budget = self._budget_repository.save(budget)

        # Journal
        for champ in modifications:
            self._journal_repository.save(
                JournalEntry(
                    entite_type="budget",
                    entite_id=budget.id,
                    chantier_id=budget.chantier_id,
                    action="modification",
                    details=f"Modification du champ '{champ}'",
                    auteur_id=updated_by,
                    created_at=datetime.utcnow(),
                )
            )

        # Publier l'event
        self._event_bus.publish(
            BudgetUpdatedEvent(
                budget_id=budget.id,
                chantier_id=budget.chantier_id,
                montant_revise_ht=budget.montant_revise_ht,
                updated_by=updated_by,
            )
        )

        return BudgetDTO.from_entity(budget)


class GetBudgetUseCase:
    """Use case pour récupérer un budget."""

    def __init__(self, budget_repository: BudgetRepository):
        self._budget_repository = budget_repository

    def execute(self, budget_id: int) -> BudgetDTO:
        """Récupère un budget par son ID.

        Args:
            budget_id: L'ID du budget.

        Returns:
            Le DTO du budget.

        Raises:
            BudgetNotFoundError: Si le budget n'existe pas.
        """
        budget = self._budget_repository.find_by_id(budget_id)
        if not budget:
            raise BudgetNotFoundError(budget_id=budget_id)

        return BudgetDTO.from_entity(budget)


class GetBudgetByChantierUseCase:
    """Use case pour récupérer le budget d'un chantier."""

    def __init__(self, budget_repository: BudgetRepository):
        self._budget_repository = budget_repository

    def execute(self, chantier_id: int) -> BudgetDTO:
        """Récupère le budget d'un chantier.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Le DTO du budget.

        Raises:
            BudgetNotFoundError: Si aucun budget pour ce chantier.
        """
        budget = self._budget_repository.find_by_chantier_id(chantier_id)
        if not budget:
            raise BudgetNotFoundError(chantier_id=chantier_id)

        return BudgetDTO.from_entity(budget)
