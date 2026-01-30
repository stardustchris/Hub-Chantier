"""Use Case: Créer des pointages en masse depuis le planning (FDH-10)."""

from datetime import date, timedelta
from typing import Optional, List

from ...domain.entities import Pointage
from ...domain.repositories import PointageRepository, FeuilleHeuresRepository
from ...domain.value_objects import Duree
from ...domain.events import PointageBulkCreatedEvent
from ..dtos import BulkCreatePointageDTO, PointageDTO
from ..ports import EventBus, NullEventBus

# Chantiers système à exclure de la synchronisation Planning → Pointages
CHANTIERS_SYSTEME = {'CONGES', 'MALADIE', 'RTT', 'FORMATION'}


class BulkCreateFromPlanningUseCase:
    """
    Crée des pointages en masse depuis les affectations du planning.

    Implémente FDH-10: Création auto à l'affectation.
    Les lignes de feuille d'heures sont pré-remplies depuis le planning.
    """

    def __init__(
        self,
        pointage_repo: PointageRepository,
        feuille_repo: FeuilleHeuresRepository,
        event_bus: Optional[EventBus] = None,
        chantier_repo = None,  # Injection optionnelle pour filtrage chantiers système
    ):
        """
        Initialise le use case.

        Args:
            pointage_repo: Repository des pointages.
            feuille_repo: Repository des feuilles d'heures.
            event_bus: Bus d'événements (optionnel).
            chantier_repo: Repository des chantiers (optionnel, pour filtrage).
        """
        self.pointage_repo = pointage_repo
        self.feuille_repo = feuille_repo
        self.event_bus = event_bus or NullEventBus()
        self.chantier_repo = chantier_repo

    def execute(self, dto: BulkCreatePointageDTO, created_by: int) -> List[PointageDTO]:
        """
        Crée des pointages depuis les affectations du planning.

        Args:
            dto: Les données des affectations.
            created_by: ID de l'utilisateur créateur.

        Returns:
            Liste des DTOs des pointages créés.

        Note:
            Les pointages existants ne sont pas recréés.
        """
        pointages_to_save = []

        for affectation in dto.affectations:
            # Filtre les chantiers système (CONGES, MALADIE, RTT, FORMATION)
            # Gap 2: Ces chantiers ne doivent pas générer de pointages
            if self.chantier_repo:
                chantier = self.chantier_repo.find_by_id(affectation.chantier_id)
                if chantier and chantier.code in CHANTIERS_SYSTEME:
                    continue  # Skip les chantiers système

            # Vérifie qu'un pointage n'existe pas déjà pour cette affectation
            existing = self.pointage_repo.find_by_affectation(affectation.affectation_id)
            if existing:
                continue

            # Vérifie aussi par triplet utilisateur/chantier/date
            existing_triplet = self.pointage_repo.find_by_utilisateur_chantier_date(
                utilisateur_id=dto.utilisateur_id,
                chantier_id=affectation.chantier_id,
                date_pointage=affectation.date_affectation,
            )
            if existing_triplet:
                continue

            # Parse les heures prévues
            heures_prevues = Duree.from_string(affectation.heures_prevues)

            # Crée le pointage avec les heures prévues comme heures normales
            pointage = Pointage(
                utilisateur_id=dto.utilisateur_id,
                chantier_id=affectation.chantier_id,
                date_pointage=affectation.date_affectation,
                heures_normales=heures_prevues,
                affectation_id=affectation.affectation_id,
                created_by=created_by,
            )
            pointages_to_save.append(pointage)

        if not pointages_to_save:
            return []

        # Sauvegarde en masse
        pointages_saved = self.pointage_repo.bulk_save(pointages_to_save)

        # Assure l'existence de la feuille d'heures
        self.feuille_repo.get_or_create(
            utilisateur_id=dto.utilisateur_id,
            semaine_debut=dto.semaine_debut,
        )

        # Publie l'événement
        event = PointageBulkCreatedEvent(
            pointage_ids=tuple(p.id for p in pointages_saved),
            utilisateur_id=dto.utilisateur_id,
            semaine_debut=dto.semaine_debut,
            chantier_ids=tuple(set(p.chantier_id for p in pointages_saved)),
            source="planning",
        )
        self.event_bus.publish(event)

        return [self._to_dto(p) for p in pointages_saved]

    def execute_from_event(
        self,
        utilisateur_id: int,
        chantier_id: int,
        date_affectation: date,
        heures_prevues: str,
        affectation_id: int,
        created_by: int,
    ) -> Optional[PointageDTO]:
        """
        Crée un pointage depuis un événement d'affectation.

        Appelé par le handler d'événement AffectationCreatedEvent.

        Args:
            utilisateur_id: ID de l'utilisateur.
            chantier_id: ID du chantier.
            date_affectation: Date de l'affectation.
            heures_prevues: Heures prévues (format HH:MM).
            affectation_id: ID de l'affectation source.
            created_by: ID du créateur.

        Returns:
            DTO du pointage créé ou None si déjà existant ou chantier système.
        """
        # Filtre les chantiers système (CONGES, MALADIE, RTT, FORMATION)
        # Gap 2: Ces chantiers ne doivent pas générer de pointages
        if self.chantier_repo:
            chantier = self.chantier_repo.find_by_id(chantier_id)
            if chantier and chantier.code in CHANTIERS_SYSTEME:
                return None  # Pas de pointage pour les chantiers système

        # Vérifie qu'un pointage n'existe pas déjà
        existing = self.pointage_repo.find_by_affectation(affectation_id)
        if existing:
            return None

        existing_triplet = self.pointage_repo.find_by_utilisateur_chantier_date(
            utilisateur_id=utilisateur_id,
            chantier_id=chantier_id,
            date_pointage=date_affectation,
        )
        if existing_triplet:
            return None

        # Parse les heures
        heures = Duree.from_string(heures_prevues)

        # Crée le pointage
        pointage = Pointage(
            utilisateur_id=utilisateur_id,
            chantier_id=chantier_id,
            date_pointage=date_affectation,
            heures_normales=heures,
            affectation_id=affectation_id,
            created_by=created_by,
        )

        # Sauvegarde
        pointage = self.pointage_repo.save(pointage)

        # Assure l'existence de la feuille
        days_since_monday = date_affectation.weekday()
        semaine_debut = date_affectation - timedelta(days=days_since_monday)
        self.feuille_repo.get_or_create(
            utilisateur_id=utilisateur_id,
            semaine_debut=semaine_debut,
        )

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
