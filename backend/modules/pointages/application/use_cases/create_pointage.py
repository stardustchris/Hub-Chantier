"""Use Case: Créer un pointage."""

from datetime import datetime
from typing import Optional

from ...domain.entities import Pointage
from ...domain.repositories import PointageRepository, FeuilleHeuresRepository
from ...domain.value_objects import Duree, StatutPointage
from ...domain.events import PointageCreatedEvent
from ..dtos import CreatePointageDTO, PointageDTO
from ..ports import EventBus, NullEventBus


class CreatePointageUseCase:
    """
    Crée un nouveau pointage.

    Selon CDC Section 7 - Feuilles d'heures.
    """

    def __init__(
        self,
        pointage_repo: PointageRepository,
        feuille_repo: FeuilleHeuresRepository,
        event_bus: Optional[EventBus] = None,
    ):
        """
        Initialise le use case.

        Args:
            pointage_repo: Repository des pointages.
            feuille_repo: Repository des feuilles d'heures.
            event_bus: Bus d'événements (optionnel).
        """
        self.pointage_repo = pointage_repo
        self.feuille_repo = feuille_repo
        self.event_bus = event_bus or NullEventBus()

    def execute(self, dto: CreatePointageDTO, created_by: int) -> PointageDTO:
        """
        Exécute la création d'un pointage.

        Args:
            dto: Les données du pointage à créer.
            created_by: ID de l'utilisateur créateur.

        Returns:
            Le DTO du pointage créé.

        Raises:
            ValueError: Si les données sont invalides ou si le pointage existe déjà.
        """
        # Vérifie qu'un pointage n'existe pas déjà pour ce triplet
        existing = self.pointage_repo.find_by_utilisateur_chantier_date(
            utilisateur_id=dto.utilisateur_id,
            chantier_id=dto.chantier_id,
            date_pointage=dto.date_pointage,
        )
        if existing:
            raise ValueError(
                f"Un pointage existe déjà pour l'utilisateur {dto.utilisateur_id}, "
                f"chantier {dto.chantier_id}, date {dto.date_pointage}"
            )

        # Parse les durées
        heures_normales = Duree.from_string(dto.heures_normales)
        heures_supplementaires = Duree.from_string(dto.heures_supplementaires)

        # Crée l'entité
        pointage = Pointage(
            utilisateur_id=dto.utilisateur_id,
            chantier_id=dto.chantier_id,
            date_pointage=dto.date_pointage,
            heures_normales=heures_normales,
            heures_supplementaires=heures_supplementaires,
            commentaire=dto.commentaire,
            affectation_id=dto.affectation_id,
            created_by=created_by,
        )

        # Persiste
        pointage = self.pointage_repo.save(pointage)

        # Assure l'existence de la feuille d'heures pour la semaine
        self.feuille_repo.get_or_create(
            utilisateur_id=dto.utilisateur_id,
            semaine_debut=self._get_monday(dto.date_pointage),
        )

        # Publie l'événement
        event = PointageCreatedEvent(
            pointage_id=pointage.id,
            utilisateur_id=pointage.utilisateur_id,
            chantier_id=pointage.chantier_id,
            date_pointage=pointage.date_pointage,
            heures_normales=str(pointage.heures_normales),
            created_by=created_by,
            affectation_id=pointage.affectation_id,
        )
        self.event_bus.publish(event)

        return self._to_dto(pointage)

    def _get_monday(self, d) -> "date":
        """Retourne le lundi de la semaine."""
        from datetime import timedelta

        days_since_monday = d.weekday()
        return d - timedelta(days=days_since_monday)

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
