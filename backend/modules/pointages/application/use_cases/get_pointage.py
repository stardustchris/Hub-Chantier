"""Use Case: Récupérer un pointage."""

from typing import Optional

from ...domain.entities import Pointage
from ...domain.repositories import PointageRepository
from ..dtos import PointageDTO


class GetPointageUseCase:
    """
    Récupère un pointage par son ID.
    """

    def __init__(self, pointage_repo: PointageRepository):
        """
        Initialise le use case.

        Args:
            pointage_repo: Repository des pointages.
        """
        self.pointage_repo = pointage_repo

    def execute(self, pointage_id: int) -> Optional[PointageDTO]:
        """
        Exécute la récupération d'un pointage.

        Args:
            pointage_id: ID du pointage.

        Returns:
            Le DTO du pointage ou None si non trouvé.
        """
        pointage = self.pointage_repo.find_by_id(pointage_id)
        if not pointage:
            return None

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
