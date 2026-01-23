"""Use Case CreateTache - Creation d'une nouvelle tache (TAC-06, TAC-07)."""

from datetime import date
from typing import Optional, Callable

from ...domain.entities import Tache
from ...domain.repositories import TacheRepository
from ...domain.value_objects import UniteMesure
from ...domain.events import TacheCreatedEvent
from ..dtos import CreateTacheDTO, TacheDTO


class TacheAlreadyExistsError(Exception):
    """Exception levee si une tache similaire existe deja."""

    def __init__(self, message: str = "Une tache similaire existe deja"):
        self.message = message
        super().__init__(self.message)


class CreateTacheUseCase:
    """
    Cas d'utilisation : Creation d'une nouvelle tache.

    Selon CDC Section 13 - TAC-06 (creation manuelle) et TAC-07 (bouton +).

    Attributes:
        tache_repo: Repository pour acceder aux taches.
        event_publisher: Fonction pour publier les events (optionnel).
    """

    def __init__(
        self,
        tache_repo: TacheRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            tache_repo: Repository taches (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.tache_repo = tache_repo
        self.event_publisher = event_publisher

    def execute(self, dto: CreateTacheDTO) -> TacheDTO:
        """
        Execute la creation d'une tache.

        Args:
            dto: Les donnees de creation.

        Returns:
            TacheDTO de la tache creee.

        Raises:
            ValueError: Si les donnees sont invalides.
        """
        # Valider l'unite de mesure si fournie
        unite_mesure = None
        if dto.unite_mesure:
            unite_mesure = UniteMesure.from_string(dto.unite_mesure)

        # Convertir la date si fournie
        date_echeance = None
        if dto.date_echeance:
            try:
                date_echeance = date.fromisoformat(dto.date_echeance)
            except ValueError:
                raise ValueError(
                    f"Format de date invalide: {dto.date_echeance}. "
                    "Utilisez le format YYYY-MM-DD."
                )

        # Creer l'entite Tache
        tache = Tache(
            chantier_id=dto.chantier_id,
            titre=dto.titre,
            description=dto.description,
            parent_id=dto.parent_id,
            date_echeance=date_echeance,
            unite_mesure=unite_mesure,
            quantite_estimee=dto.quantite_estimee,
            heures_estimees=dto.heures_estimees,
        )

        # Determiner l'ordre si c'est une sous-tache
        if dto.parent_id:
            children = self.tache_repo.find_children(dto.parent_id)
            tache.ordre = len(children)
        else:
            # Tache racine : prendre le dernier ordre + 1
            taches = self.tache_repo.find_by_chantier(
                dto.chantier_id, include_sous_taches=False
            )
            if taches:
                tache.ordre = max(t.ordre for t in taches) + 1

        # Sauvegarder
        tache = self.tache_repo.save(tache)

        # Publier l'event
        if self.event_publisher:
            event = TacheCreatedEvent(
                tache_id=tache.id,
                chantier_id=tache.chantier_id,
                titre=tache.titre,
                parent_id=tache.parent_id,
            )
            self.event_publisher(event)

        return TacheDTO.from_entity(tache)
