"""Use Case DupliquerAffectations - Duplication des affectations (PLN-16)."""

from datetime import date, timedelta, datetime
from typing import Optional, Callable, List

from ...domain.entities import Affectation
from ...domain.repositories import AffectationRepository
from ...domain.events import AffectationsDupliquéesEvent
from ..dtos import DupliquerAffectationsDTO, AffectationDTO


class DupliquerAffectationsUseCase:
    """
    Cas d'utilisation : Duplication des affectations d'une période (PLN-16).

    Permet de dupliquer les affectations d'un utilisateur d'une semaine
    vers une autre semaine.

    Attributes:
        affectation_repo: Repository pour accéder aux affectations.
        event_publisher: Fonction pour publier les events (optionnel).
    """

    def __init__(
        self,
        affectation_repo: AffectationRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            affectation_repo: Repository affectations (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.affectation_repo = affectation_repo
        self.event_publisher = event_publisher

    def execute(self, dto: DupliquerAffectationsDTO, created_by: Optional[int] = None) -> List[AffectationDTO]:
        """
        Duplique les affectations d'une période vers une autre.

        Args:
            dto: Données de duplication.
            created_by: ID de l'utilisateur qui duplique.

        Returns:
            Liste des AffectationDTO créées.
        """
        # Parser les dates
        date_source_debut = date.fromisoformat(dto.date_source_debut)
        date_source_fin = date.fromisoformat(dto.date_source_fin)
        date_cible_debut = date.fromisoformat(dto.date_cible_debut)

        # Récupérer les affectations sources
        affectations_sources = self.affectation_repo.find_by_utilisateur(
            utilisateur_id=dto.utilisateur_id,
            date_debut=date_source_debut,
            date_fin=date_source_fin,
        )

        # Calculer le décalage en jours
        decalage = (date_cible_debut - date_source_debut).days

        # Créer les nouvelles affectations
        nouvelles_affectations = []
        for affectation_source in affectations_sources:
            # Calculer la nouvelle date
            nouvelle_date = affectation_source.date_affectation + timedelta(days=decalage)

            # Vérifier si une affectation existe déjà
            if self.affectation_repo.exists_for_utilisateur_chantier_date(
                utilisateur_id=dto.utilisateur_id,
                chantier_id=affectation_source.chantier_id,
                date_affectation=nouvelle_date,
            ):
                # Skip si existe déjà
                continue

            # Dupliquer
            nouvelle_affectation = affectation_source.dupliquer_pour_date(nouvelle_date)
            nouvelle_affectation = Affectation(
                utilisateur_id=nouvelle_affectation.utilisateur_id,
                chantier_id=nouvelle_affectation.chantier_id,
                date_affectation=nouvelle_affectation.date_affectation,
                creneau=nouvelle_affectation.creneau,
                note=nouvelle_affectation.note,
                recurrence=nouvelle_affectation.recurrence,
                created_by=created_by,
                created_at=datetime.now(),
            )

            # Sauvegarder
            nouvelle_affectation = self.affectation_repo.save(nouvelle_affectation)
            nouvelles_affectations.append(nouvelle_affectation)

        # Publier l'événement
        if self.event_publisher and nouvelles_affectations:
            event = AffectationsDupliquéesEvent(
                source_utilisateur_id=dto.utilisateur_id,
                date_source_debut=date_source_debut,
                date_source_fin=date_source_fin,
                date_cible_debut=date_cible_debut,
                nb_affectations=len(nouvelles_affectations),
                created_by=created_by,
            )
            self.event_publisher(event)

        return [AffectationDTO.from_entity(a) for a in nouvelles_affectations]
