"""Use Case CreateFeuilleTache - Creation d'une feuille de tache (TAC-18)."""

from datetime import date
from typing import Optional, Callable

from ...domain.entities import FeuilleTache
from ...domain.repositories import FeuilleTacheRepository, TacheRepository
from ...domain.events import FeuilleTacheCreatedEvent
from ..dtos import CreateFeuilleTacheDTO, FeuilleTacheDTO


class FeuilleTacheAlreadyExistsError(Exception):
    """Exception levee si une feuille existe deja pour cette combinaison."""

    def __init__(self, tache_id: int, utilisateur_id: int, date_travail: str):
        self.tache_id = tache_id
        self.utilisateur_id = utilisateur_id
        self.date_travail = date_travail
        self.message = (
            f"Une feuille de tache existe deja pour la tache {tache_id}, "
            f"l'utilisateur {utilisateur_id} et la date {date_travail}"
        )
        super().__init__(self.message)


class CreateFeuilleTacheUseCase:
    """
    Cas d'utilisation : Creation d'une feuille de tache.

    Selon CDC Section 13 - TAC-18: Feuilles de taches
    (Declaration quotidienne travail realise).

    Attributes:
        feuille_repo: Repository pour les feuilles de taches.
        tache_repo: Repository pour les taches.
        event_publisher: Fonction pour publier les events (optionnel).
    """

    def __init__(
        self,
        feuille_repo: FeuilleTacheRepository,
        tache_repo: TacheRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            feuille_repo: Repository feuilles (interface).
            tache_repo: Repository taches (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.feuille_repo = feuille_repo
        self.tache_repo = tache_repo
        self.event_publisher = event_publisher

    def execute(self, dto: CreateFeuilleTacheDTO) -> FeuilleTacheDTO:
        """
        Execute la creation d'une feuille de tache.

        Args:
            dto: Les donnees de creation.

        Returns:
            FeuilleTacheDTO de la feuille creee.

        Raises:
            FeuilleTacheAlreadyExistsError: Si une feuille existe deja.
            TacheNotFoundError: Si la tache n'existe pas.
            ValueError: Si les donnees sont invalides.
        """
        from .get_tache import TacheNotFoundError

        # Convertir la date
        date_travail = date.fromisoformat(dto.date_travail)

        # Verifier que la tache existe
        tache = self.tache_repo.find_by_id(dto.tache_id)
        if not tache:
            raise TacheNotFoundError(dto.tache_id)

        # Verifier qu'une feuille n'existe pas deja pour cette combinaison
        if self.feuille_repo.exists_for_date(
            dto.tache_id, dto.utilisateur_id, date_travail
        ):
            raise FeuilleTacheAlreadyExistsError(
                dto.tache_id, dto.utilisateur_id, dto.date_travail
            )

        # Creer la feuille
        feuille = FeuilleTache(
            tache_id=dto.tache_id,
            utilisateur_id=dto.utilisateur_id,
            chantier_id=dto.chantier_id,
            date_travail=date_travail,
            heures_travaillees=dto.heures_travaillees,
            quantite_realisee=dto.quantite_realisee,
            commentaire=dto.commentaire,
        )

        # Sauvegarder
        feuille = self.feuille_repo.save(feuille)

        # Publier l'event
        if self.event_publisher:
            event = FeuilleTacheCreatedEvent(
                feuille_id=feuille.id,
                tache_id=feuille.tache_id,
                utilisateur_id=feuille.utilisateur_id,
                chantier_id=feuille.chantier_id,
                heures_travaillees=feuille.heures_travaillees,
                quantite_realisee=feuille.quantite_realisee,
                date_travail=feuille.date_travail.isoformat(),
            )
            self.event_publisher(event)

        return FeuilleTacheDTO.from_entity(feuille)
