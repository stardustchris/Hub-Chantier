"""Use Case: Signer un pointage (FDH-12)."""

from typing import Optional

from ...domain.entities import Pointage
from ...domain.repositories import PointageRepository
from ...domain.events import PointageSignedEvent
from ..dtos import SignPointageDTO, PointageDTO
from ..ports import EventBus, NullEventBus


class SignPointageUseCase:
    """
    Signe électroniquement un pointage (FDH-12).

    La signature valide les heures déclarées par le compagnon.
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

    def execute(self, dto: SignPointageDTO) -> PointageDTO:
        """
        Exécute la signature d'un pointage.

        Args:
            dto: Les données de signature.

        Returns:
            Le DTO du pointage signé.

        Raises:
            ValueError: Si le pointage n'existe pas ou ne peut pas être signé.
        """
        # Récupère le pointage
        pointage = self.pointage_repo.find_by_id(dto.pointage_id)
        if not pointage:
            raise ValueError(f"Pointage {dto.pointage_id} non trouvé")

        # Valide la signature (non vide)
        if not dto.signature or not dto.signature.strip():
            raise ValueError("La signature ne peut pas être vide")

        # Signe le pointage
        pointage.signer(dto.signature)

        # Persiste
        pointage = self.pointage_repo.save(pointage)

        # Publie l'événement
        event = PointageSignedEvent(
            pointage_id=pointage.id,
            utilisateur_id=pointage.utilisateur_id,
            signature=dto.signature,
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
