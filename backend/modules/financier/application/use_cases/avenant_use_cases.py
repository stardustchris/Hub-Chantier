"""Use Cases pour la gestion des avenants budgétaires.

FIN-04: Avenants budgétaires - Modifications du budget initial.
"""

from datetime import datetime
from typing import List

from ..ports.event_bus import EventBus

from ...domain.entities.avenant_budgetaire import AvenantBudgetaire
from ...domain.repositories import (
    BudgetRepository,
    JournalFinancierRepository,
    JournalEntry,
)
from ...domain.repositories.avenant_repository import AvenantRepository
from ...domain.events import AvenantCreatedEvent, AvenantValideEvent
from ..dtos.avenant_dtos import AvenantCreateDTO, AvenantUpdateDTO, AvenantDTO


class AvenantNotFoundError(Exception):
    """Erreur levée quand un avenant n'est pas trouvé."""

    def __init__(self, avenant_id: int):
        self.avenant_id = avenant_id
        super().__init__(f"Avenant {avenant_id} non trouvé")


class AvenantAlreadyValideError(Exception):
    """Erreur levée quand un avenant est déjà validé."""

    def __init__(self, avenant_id: int):
        self.avenant_id = avenant_id
        super().__init__(f"Avenant {avenant_id} est déjà validé")


class CreateAvenantUseCase:
    """Use case pour créer un avenant budgétaire.

    FIN-04: Numérotation automatique AVN-YYYY-NN.
    """

    def __init__(
        self,
        avenant_repository: AvenantRepository,
        budget_repository: BudgetRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._avenant_repository = avenant_repository
        self._budget_repository = budget_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, dto: AvenantCreateDTO, created_by: int) -> AvenantDTO:
        """Crée un nouvel avenant budgétaire.

        Args:
            dto: Les données de l'avenant à créer.
            created_by: L'ID de l'utilisateur créateur.

        Returns:
            Le DTO de l'avenant créé.

        Raises:
            ValueError: Si le budget n'existe pas.
        """
        # Vérifier que le budget existe
        budget = self._budget_repository.find_by_id(dto.budget_id)
        if not budget:
            raise ValueError(f"Budget {dto.budget_id} non trouvé")

        # Générer le numéro automatiquement: AVN-YYYY-NN
        count = self._avenant_repository.count_by_budget_id(dto.budget_id)
        year = datetime.utcnow().year
        numero = f"AVN-{year}-{count + 1:02d}"

        # Créer l'entité
        avenant = AvenantBudgetaire(
            budget_id=dto.budget_id,
            numero=numero,
            motif=dto.motif,
            montant_ht=dto.montant_ht,
            impact_description=dto.impact_description,
            statut="brouillon",
            created_by=created_by,
            created_at=datetime.utcnow(),
        )

        # Persister
        avenant = self._avenant_repository.save(avenant)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="avenant",
                entite_id=avenant.id,
                chantier_id=budget.chantier_id,
                action="creation",
                details=(
                    f"Création de l'avenant {avenant.numero} - "
                    f"Montant: {avenant.montant_ht} EUR HT - "
                    f"Motif: {avenant.motif}"
                ),
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        # Publier l'event
        self._event_bus.publish(
            AvenantCreatedEvent(
                avenant_id=avenant.id,
                budget_id=avenant.budget_id,
                montant_ht=avenant.montant_ht,
                motif=avenant.motif,
                created_by=created_by,
            )
        )

        return AvenantDTO.from_entity(avenant)


class UpdateAvenantUseCase:
    """Use case pour mettre à jour un avenant budgétaire."""

    def __init__(
        self,
        avenant_repository: AvenantRepository,
        budget_repository: BudgetRepository,
        journal_repository: JournalFinancierRepository,
    ):
        self._avenant_repository = avenant_repository
        self._budget_repository = budget_repository
        self._journal_repository = journal_repository

    def execute(
        self, avenant_id: int, dto: AvenantUpdateDTO, updated_by: int
    ) -> AvenantDTO:
        """Met à jour un avenant budgétaire.

        Args:
            avenant_id: L'ID de l'avenant à mettre à jour.
            dto: Les données à mettre à jour.
            updated_by: L'ID de l'utilisateur.

        Returns:
            Le DTO de l'avenant mis à jour.

        Raises:
            AvenantNotFoundError: Si l'avenant n'existe pas.
            AvenantAlreadyValideError: Si l'avenant est déjà validé.
        """
        avenant = self._avenant_repository.find_by_id(avenant_id)
        if not avenant:
            raise AvenantNotFoundError(avenant_id)

        if avenant.est_valide:
            raise AvenantAlreadyValideError(avenant_id)

        budget = self._budget_repository.find_by_id(avenant.budget_id)
        modifications = []

        # Appliquer les modifications
        if dto.motif is not None:
            avenant.motif = dto.motif
            modifications.append("motif")
        if dto.montant_ht is not None:
            avenant.montant_ht = dto.montant_ht
            modifications.append("montant_ht")
        if dto.impact_description is not None:
            avenant.impact_description = dto.impact_description
            modifications.append("impact_description")

        avenant.updated_at = datetime.utcnow()

        # Persister
        avenant = self._avenant_repository.save(avenant)

        # Journal
        chantier_id = budget.chantier_id if budget else None
        for champ in modifications:
            self._journal_repository.save(
                JournalEntry(
                    entite_type="avenant",
                    entite_id=avenant.id,
                    chantier_id=chantier_id,
                    action="modification",
                    details=f"Modification du champ '{champ}'",
                    auteur_id=updated_by,
                    created_at=datetime.utcnow(),
                )
            )

        return AvenantDTO.from_entity(avenant)


class ValiderAvenantUseCase:
    """Use case pour valider un avenant budgétaire.

    FIN-04: La validation met à jour le montant_avenants_ht du budget.
    """

    def __init__(
        self,
        avenant_repository: AvenantRepository,
        budget_repository: BudgetRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._avenant_repository = avenant_repository
        self._budget_repository = budget_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, avenant_id: int, validated_by: int) -> AvenantDTO:
        """Valide un avenant budgétaire et met à jour le budget.

        Args:
            avenant_id: L'ID de l'avenant à valider.
            validated_by: L'ID de l'utilisateur valideur.

        Returns:
            Le DTO de l'avenant validé.

        Raises:
            AvenantNotFoundError: Si l'avenant n'existe pas.
            AvenantAlreadyValideError: Si l'avenant est déjà validé.
            ValueError: Si le budget associé n'existe pas.
        """
        avenant = self._avenant_repository.find_by_id(avenant_id)
        if not avenant:
            raise AvenantNotFoundError(avenant_id)

        if avenant.est_valide:
            raise AvenantAlreadyValideError(avenant_id)

        # Valider l'avenant
        avenant.valider(validated_by)

        # Persister l'avenant
        avenant = self._avenant_repository.save(avenant)

        # Mettre à jour le budget avec la somme des avenants validés
        budget = self._budget_repository.find_by_id(avenant.budget_id)
        if not budget:
            raise ValueError(f"Budget {avenant.budget_id} non trouvé")

        somme_avenants = self._avenant_repository.somme_avenants_valides(
            avenant.budget_id
        )
        budget.montant_avenants_ht = somme_avenants
        budget.updated_at = datetime.utcnow()
        self._budget_repository.save(budget)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="avenant",
                entite_id=avenant.id,
                chantier_id=budget.chantier_id,
                action="validation",
                details=(
                    f"Validation de l'avenant {avenant.numero} - "
                    f"Montant: {avenant.montant_ht} EUR HT - "
                    f"Nouveau montant avenants budget: {somme_avenants} EUR HT"
                ),
                auteur_id=validated_by,
                created_at=datetime.utcnow(),
            )
        )

        # Publier l'event
        self._event_bus.publish(
            AvenantValideEvent(
                avenant_id=avenant.id,
                budget_id=avenant.budget_id,
                montant_ht=avenant.montant_ht,
                validated_by=validated_by,
            )
        )

        return AvenantDTO.from_entity(avenant)


class GetAvenantUseCase:
    """Use case pour récupérer un avenant budgétaire."""

    def __init__(self, avenant_repository: AvenantRepository):
        self._avenant_repository = avenant_repository

    def execute(self, avenant_id: int) -> AvenantDTO:
        """Récupère un avenant par son ID.

        Args:
            avenant_id: L'ID de l'avenant.

        Returns:
            Le DTO de l'avenant.

        Raises:
            AvenantNotFoundError: Si l'avenant n'existe pas.
        """
        avenant = self._avenant_repository.find_by_id(avenant_id)
        if not avenant:
            raise AvenantNotFoundError(avenant_id)

        return AvenantDTO.from_entity(avenant)


class ListAvenantsUseCase:
    """Use case pour lister les avenants d'un budget."""

    def __init__(self, avenant_repository: AvenantRepository):
        self._avenant_repository = avenant_repository

    def execute(self, budget_id: int) -> List[AvenantDTO]:
        """Liste les avenants d'un budget.

        Args:
            budget_id: L'ID du budget.

        Returns:
            Liste des DTOs d'avenants.
        """
        avenants = self._avenant_repository.find_by_budget_id(budget_id)
        return [AvenantDTO.from_entity(a) for a in avenants]


class DeleteAvenantUseCase:
    """Use case pour supprimer un avenant budgétaire."""

    def __init__(
        self,
        avenant_repository: AvenantRepository,
        budget_repository: BudgetRepository,
        journal_repository: JournalFinancierRepository,
    ):
        self._avenant_repository = avenant_repository
        self._budget_repository = budget_repository
        self._journal_repository = journal_repository

    def execute(self, avenant_id: int, deleted_by: int) -> None:
        """Supprime un avenant budgétaire (soft delete).

        Args:
            avenant_id: L'ID de l'avenant à supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Raises:
            AvenantNotFoundError: Si l'avenant n'existe pas.
            AvenantAlreadyValideError: Si l'avenant est déjà validé.
        """
        avenant = self._avenant_repository.find_by_id(avenant_id)
        if not avenant:
            raise AvenantNotFoundError(avenant_id)

        if avenant.est_valide:
            raise AvenantAlreadyValideError(avenant_id)

        budget = self._budget_repository.find_by_id(avenant.budget_id)

        # Supprimer (soft delete)
        self._avenant_repository.delete(avenant_id, deleted_by)

        # Journal
        chantier_id = budget.chantier_id if budget else None
        self._journal_repository.save(
            JournalEntry(
                entite_type="avenant",
                entite_id=avenant.id,
                chantier_id=chantier_id,
                action="suppression",
                details=(
                    f"Suppression de l'avenant {avenant.numero} - "
                    f"Montant: {avenant.montant_ht} EUR HT"
                ),
                auteur_id=deleted_by,
                created_at=datetime.utcnow(),
            )
        )
