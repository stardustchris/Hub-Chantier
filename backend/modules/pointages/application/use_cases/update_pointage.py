"""Use Case: Mettre à jour un pointage."""

from typing import Optional

from ...domain.entities import Pointage
from ...domain.repositories import PointageRepository
from ...domain.value_objects import Duree
from ...domain.events import PointageUpdatedEvent
from ..dtos import UpdatePointageDTO, PointageDTO
from ..ports import EventBus, NullEventBus


class UpdatePointageUseCase:
    """
    Met à jour un pointage existant.

    Le pointage doit être dans un état modifiable (brouillon ou rejeté).
    """

    def __init__(
        self,
        pointage_repo: PointageRepository,
        event_bus: Optional[EventBus] = None,
    ):
        """
        Initialise le use case.

        Args:
            pointage_repo: Repository des pointages.
            event_bus: Bus d'événements (optionnel).
        """
        self.pointage_repo = pointage_repo
        self.event_bus = event_bus or NullEventBus()

    def execute(self, dto: UpdatePointageDTO, updated_by: int) -> PointageDTO:
        """
        Exécute la mise à jour d'un pointage.

        Args:
            dto: Les données de mise à jour.
            updated_by: ID de l'utilisateur qui modifie.

        Returns:
            Le DTO du pointage mis à jour.

        Raises:
            ValueError: Si le pointage n'existe pas ou n'est pas modifiable.
        """
        # Récupère le pointage
        pointage = self.pointage_repo.find_by_id(dto.pointage_id)
        if not pointage:
            raise ValueError(f"Pointage {dto.pointage_id} non trouvé")

        # Vérifie qu'il est modifiable
        if not pointage.is_editable:
            raise ValueError(
                f"Le pointage ne peut pas être modifié (statut: {pointage.statut.value})"
            )

        # Met à jour les champs fournis
        heures_normales = None
        heures_supplementaires = None

        if dto.heures_normales is not None:
            heures_normales = Duree.from_string(dto.heures_normales)

        if dto.heures_supplementaires is not None:
            heures_supplementaires = Duree.from_string(dto.heures_supplementaires)

        # Applique les modifications
        pointage.set_heures(
            heures_normales=heures_normales,
            heures_supplementaires=heures_supplementaires,
        )

        if dto.commentaire is not None:
            pointage.commentaire = dto.commentaire

        # Persiste
        pointage = self.pointage_repo.save(pointage)

        # Publie l'événement
        event = PointageUpdatedEvent(
            pointage_id=pointage.id,
            utilisateur_id=pointage.utilisateur_id,
            chantier_id=pointage.chantier_id,
            date_pointage=pointage.date_pointage,
            heures_normales=str(pointage.heures_normales),
            heures_supplementaires=str(pointage.heures_supplementaires),
            updated_by=updated_by,
        )
        self.event_bus.publish(event)

        return self._to_dto(pointage)

    def _to_dto(self, pointage: Pointage) -> PointageDTO:
        """Convertit l'entité en DTO."""
        return PointageDTO(
            id=pointage.id,
            utilisateur_id=pointage.utilisateur_id,
            chantier_id=pointage.chantier_id,
            date_pointage=pointage.date_pointage,
            heures_normales=str(pointage.heures_normales),
            heures_supplementaires=str(pointage.heures_supplementaires),
            total_heures=str(pointage.total_heures),
            total_heures_decimal=pointage.total_heures_decimal,
            statut=pointage.statut.value,
            commentaire=pointage.commentaire,
            signature_utilisateur=pointage.signature_utilisateur,
            signature_date=pointage.signature_date,
            validateur_id=pointage.validateur_id,
            validation_date=pointage.validation_date,
            motif_rejet=pointage.motif_rejet,
            affectation_id=pointage.affectation_id,
            created_by=pointage.created_by,
            created_at=pointage.created_at,
            updated_at=pointage.updated_at,
            utilisateur_nom=pointage.utilisateur_nom,
            chantier_nom=pointage.chantier_nom,
            chantier_couleur=pointage.chantier_couleur,
        )
