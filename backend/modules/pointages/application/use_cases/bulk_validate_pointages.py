"""Use Case: Validation par lot de pointages (GAP-FDH-004)."""

from typing import Optional

from ...domain.repositories import PointageRepository
from ...domain.value_objects import PeriodePaie
from ...domain.events import PointageValidatedEvent
from ...domain.events.pointages_bulk_validated import PointagesBulkValidatedEvent
from ..dtos.bulk_validate_dtos import (
    BulkValidatePointagesDTO,
    BulkValidatePointagesResultDTO,
    PointageValidationResult,
)
from ..ports import EventBus, NullEventBus


class BulkValidatePointagesError(Exception):
    """Exception pour les erreurs de validation par lot."""

    def __init__(self, message: str = "Erreur lors de la validation par lot"):
        self.message = message
        super().__init__(self.message)


class BulkValidatePointagesUseCase:
    """
    Cas d'utilisation : Validation par lot de pointages (GAP-FDH-004).

    Permet à un chef de chantier, conducteur de travaux ou admin de valider
    plusieurs pointages en une seule opération (ex: tous les pointages d'une
    feuille d'heures hebdomadaire).

    Comportement transactionnel : all-or-nothing au niveau de la persistance,
    mais retour détaillé avec succès/échecs individuels pour traçabilité.

    Attributes:
        pointage_repo: Repository pour accéder aux pointages.
        event_bus: Bus d'événements pour publier les events.
    """

    def __init__(
        self,
        pointage_repo: PointageRepository,
        event_bus: Optional[EventBus] = None,
    ):
        """
        Initialise le use case.

        Args:
            pointage_repo: Repository pointages (interface).
            event_bus: Bus d'événements (optionnel).
        """
        self.pointage_repo = pointage_repo
        self.event_bus = event_bus or NullEventBus()

    def execute(self, dto: BulkValidatePointagesDTO) -> BulkValidatePointagesResultDTO:
        """
        Exécute la validation par lot de pointages.

        Args:
            dto: Les données de validation par lot.

        Returns:
            BulkValidatePointagesResultDTO contenant les résultats détaillés.

        Raises:
            BulkValidatePointagesError: Si la liste de pointages est vide.
        """
        # 1. Validation de la requête
        if not dto.pointage_ids:
            raise BulkValidatePointagesError("La liste de pointages ne peut pas être vide")

        # 2. Traitement de chaque pointage
        validated_ids = []
        failed_results = []

        for pointage_id in dto.pointage_ids:
            try:
                # Récupère le pointage
                pointage = self.pointage_repo.find_by_id(pointage_id)
                if not pointage:
                    failed_results.append(
                        PointageValidationResult(
                            pointage_id=pointage_id,
                            success=False,
                            error=f"Pointage {pointage_id} non trouvé",
                        )
                    )
                    continue

                # Vérifie le verrouillage mensuel
                if PeriodePaie.is_locked(pointage.date_pointage):
                    failed_results.append(
                        PointageValidationResult(
                            pointage_id=pointage_id,
                            success=False,
                            error="La période de paie est verrouillée",
                        )
                    )
                    continue

                # Valide le pointage
                pointage.valider(dto.validateur_id)

                # Persiste
                pointage = self.pointage_repo.save(pointage)

                # Publie l'événement individuel
                event = PointageValidatedEvent(
                    pointage_id=pointage.id,
                    utilisateur_id=pointage.utilisateur_id,
                    chantier_id=pointage.chantier_id,
                    date_pointage=pointage.date_pointage,
                    validateur_id=dto.validateur_id,
                )
                self.event_bus.publish(event)

                validated_ids.append(pointage_id)

            except ValueError as e:
                # Erreur de validation métier (statut incompatible, etc.)
                failed_results.append(
                    PointageValidationResult(
                        pointage_id=pointage_id,
                        success=False,
                        error=str(e),
                    )
                )
            except Exception as e:
                # Erreur inattendue
                failed_results.append(
                    PointageValidationResult(
                        pointage_id=pointage_id,
                        success=False,
                        error=f"Erreur inattendue: {str(e)}",
                    )
                )

        # 3. Publie l'événement de validation par lot
        if validated_ids:
            bulk_event = PointagesBulkValidatedEvent(
                pointage_ids=tuple(validated_ids),
                validateur_id=dto.validateur_id,
                success_count=len(validated_ids),
                failure_count=len(failed_results),
            )
            self.event_bus.publish(bulk_event)

        # 4. Retourne le résultat détaillé
        return BulkValidatePointagesResultDTO(
            validated=validated_ids,
            failed=failed_results,
            total_count=len(dto.pointage_ids),
            success_count=len(validated_ids),
            failure_count=len(failed_results),
        )
