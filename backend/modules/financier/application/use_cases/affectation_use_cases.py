"""Use Cases pour la gestion des affectations taches <-> lots budgetaires.

FIN-03: Affectation budgets aux taches.
"""

from datetime import datetime
from decimal import Decimal
from typing import List

from ..ports.event_bus import EventBus

from ...domain.entities.affectation_tache_lot import AffectationTacheLot
from ...domain.repositories.affectation_repository import AffectationRepository
from ...domain.repositories.avancement_tache_repository import AvancementTacheRepository
from ...domain.repositories import (
    LotBudgetaireRepository,
    JournalFinancierRepository,
    JournalEntry,
)
from ...domain.events import AffectationCreatedEvent, AffectationDeletedEvent
from ..dtos.affectation_dtos import (
    AffectationCreateDTO,
    AffectationDTO,
    SuiviAffectationDTO,
)


class AffectationNotFoundError(Exception):
    """Erreur levee quand une affectation n'est pas trouvee."""

    def __init__(self, affectation_id: int):
        self.affectation_id = affectation_id
        super().__init__(f"Affectation {affectation_id} non trouvee")


class AffectationAlreadyExistsError(Exception):
    """Erreur levee quand une affectation existe deja pour une tache/lot."""

    def __init__(self, tache_id: int, lot_id: int):
        self.tache_id = tache_id
        self.lot_id = lot_id
        super().__init__(
            f"Une affectation existe deja pour la tache {tache_id} "
            f"et le lot {lot_id}"
        )


class LotBudgetaireNotFoundForAffectationError(Exception):
    """Erreur levee quand le lot budgetaire n'existe pas."""

    def __init__(self, lot_id: int):
        self.lot_id = lot_id
        super().__init__(f"Lot budgetaire {lot_id} non trouve")


class CreateAffectationUseCase:
    """Use case pour creer une affectation tache/lot.

    FIN-03: Verifie que le lot existe et qu'il n'y a pas de doublon.
    """

    def __init__(
        self,
        affectation_repository: AffectationRepository,
        lot_repository: LotBudgetaireRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._affectation_repository = affectation_repository
        self._lot_repository = lot_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, dto: AffectationCreateDTO, created_by: int) -> AffectationDTO:
        """Cree une nouvelle affectation tache/lot.

        Args:
            dto: Les donnees de l'affectation a creer.
            created_by: L'ID de l'utilisateur createur.

        Returns:
            Le DTO de l'affectation creee.

        Raises:
            LotBudgetaireNotFoundForAffectationError: Si le lot n'existe pas.
            AffectationAlreadyExistsError: Si l'affectation existe deja.
        """
        # Verifier que le lot budgetaire existe
        lot = self._lot_repository.find_by_id(dto.lot_budgetaire_id)
        if not lot:
            raise LotBudgetaireNotFoundForAffectationError(dto.lot_budgetaire_id)

        # Verifier unicite tache/lot
        existing = self._affectation_repository.find_by_tache_and_lot(
            dto.tache_id, dto.lot_budgetaire_id
        )
        if existing:
            raise AffectationAlreadyExistsError(dto.tache_id, dto.lot_budgetaire_id)

        # Creer l'entite
        affectation = AffectationTacheLot(
            chantier_id=dto.chantier_id,
            tache_id=dto.tache_id,
            lot_budgetaire_id=dto.lot_budgetaire_id,
            pourcentage_affectation=dto.pourcentage_affectation,
            created_at=datetime.utcnow(),
            created_by=created_by,
        )

        # Persister
        affectation = self._affectation_repository.save(affectation)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="affectation",
                entite_id=affectation.id,
                chantier_id=affectation.chantier_id,
                action="creation",
                details=(
                    f"Affectation tache {affectation.tache_id} -> "
                    f"lot {affectation.lot_budgetaire_id} "
                    f"({affectation.pourcentage_affectation}%)"
                ),
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        # Publier l'event
        self._event_bus.publish(
            AffectationCreatedEvent(
                affectation_id=affectation.id,
                chantier_id=affectation.chantier_id,
                tache_id=affectation.tache_id,
                lot_budgetaire_id=affectation.lot_budgetaire_id,
                pourcentage_affectation=affectation.pourcentage_affectation,
                created_by=created_by,
            )
        )

        return AffectationDTO.from_entity(affectation)


class DeleteAffectationUseCase:
    """Use case pour supprimer une affectation tache/lot."""

    def __init__(
        self,
        affectation_repository: AffectationRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._affectation_repository = affectation_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, affectation_id: int, deleted_by: int) -> None:
        """Supprime une affectation.

        Args:
            affectation_id: L'ID de l'affectation a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Raises:
            AffectationNotFoundError: Si l'affectation n'existe pas.
        """
        affectation = self._affectation_repository.find_by_id(affectation_id)
        if not affectation:
            raise AffectationNotFoundError(affectation_id)

        self._affectation_repository.delete(affectation_id)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="affectation",
                entite_id=affectation_id,
                chantier_id=affectation.chantier_id,
                action="suppression",
                details=(
                    f"Suppression affectation tache {affectation.tache_id} -> "
                    f"lot {affectation.lot_budgetaire_id}"
                ),
                auteur_id=deleted_by,
                created_at=datetime.utcnow(),
            )
        )

        # Publier l'event
        self._event_bus.publish(
            AffectationDeletedEvent(
                affectation_id=affectation_id,
                chantier_id=affectation.chantier_id,
                tache_id=affectation.tache_id,
                lot_budgetaire_id=affectation.lot_budgetaire_id,
                deleted_by=deleted_by,
            )
        )


class ListAffectationsByChantierUseCase:
    """Use case pour lister les affectations d'un chantier."""

    def __init__(self, affectation_repository: AffectationRepository):
        self._affectation_repository = affectation_repository

    def execute(self, chantier_id: int) -> List[AffectationDTO]:
        """Liste les affectations d'un chantier.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Liste des DTOs d'affectation.
        """
        affectations = self._affectation_repository.find_by_chantier(chantier_id)
        return [AffectationDTO.from_entity(a) for a in affectations]


class ListAffectationsByTacheUseCase:
    """Use case pour lister les affectations d'une tache."""

    def __init__(self, affectation_repository: AffectationRepository):
        self._affectation_repository = affectation_repository

    def execute(self, tache_id: int) -> List[AffectationDTO]:
        """Liste les affectations d'une tache.

        Args:
            tache_id: L'ID de la tache.

        Returns:
            Liste des DTOs d'affectation.
        """
        affectations = self._affectation_repository.find_by_tache(tache_id)
        return [AffectationDTO.from_entity(a) for a in affectations]


class GetSuiviAvancementFinancierUseCase:
    """Use case pour le suivi croise avancement physique vs financier.

    FIN-03: Pour un chantier, retourne le suivi croise taches/lots
    avec l'avancement physique et le montant affecte.
    """

    def __init__(
        self,
        affectation_repository: AffectationRepository,
        avancement_repository: AvancementTacheRepository,
        lot_repository: LotBudgetaireRepository,
    ):
        self._affectation_repository = affectation_repository
        self._avancement_repository = avancement_repository
        self._lot_repository = lot_repository

    def execute(self, chantier_id: int) -> List[SuiviAffectationDTO]:
        """Retourne le suivi croise avancement/financier d'un chantier.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Liste des DTOs de suivi enrichis.
        """
        affectations = self._affectation_repository.find_by_chantier(chantier_id)
        if not affectations:
            return []

        # Charger les avancements des taches
        avancements = self._avancement_repository.get_avancements_chantier(chantier_id)
        avancements_map = {a.tache_id: a for a in avancements}

        # Charger les lots budgetaires
        lots_map = {}
        for affectation in affectations:
            if affectation.lot_budgetaire_id not in lots_map:
                lot = self._lot_repository.find_by_id(affectation.lot_budgetaire_id)
                if lot:
                    lots_map[affectation.lot_budgetaire_id] = lot

        result = []
        for affectation in affectations:
            avancement = avancements_map.get(affectation.tache_id)
            lot = lots_map.get(affectation.lot_budgetaire_id)

            if not lot:
                continue

            # Calculer le montant prevu du lot
            lot_montant = lot.quantite_prevue * lot.prix_unitaire_ht
            # Montant affecte = lot_montant * pourcentage / 100
            montant_affecte = (
                lot_montant * affectation.pourcentage_affectation / Decimal("100")
            )

            result.append(
                SuiviAffectationDTO(
                    affectation_id=affectation.id,
                    tache_id=affectation.tache_id,
                    tache_titre=avancement.titre if avancement else "Tache inconnue",
                    tache_statut=avancement.statut if avancement else "inconnu",
                    tache_progression_pct=str(avancement.progression_pct) if avancement else "0",
                    lot_budgetaire_id=affectation.lot_budgetaire_id,
                    lot_code=lot.code_lot,
                    lot_libelle=lot.libelle,
                    lot_montant_prevu_ht=str(lot_montant.quantize(Decimal("0.01"))),
                    pourcentage_affectation=str(affectation.pourcentage_affectation),
                    montant_affecte_ht=str(montant_affecte.quantize(Decimal("0.01"))),
                )
            )

        return result
