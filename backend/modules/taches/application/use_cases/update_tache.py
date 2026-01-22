"""Use Case UpdateTache - Mise a jour d'une tache."""

from datetime import date
from typing import Optional, Callable

from ...domain.repositories import TacheRepository
from ...domain.value_objects import UniteMesure, StatutTache
from ...domain.events import TacheUpdatedEvent
from ..dtos import UpdateTacheDTO, TacheDTO


class UpdateTacheUseCase:
    """
    Cas d'utilisation : Mise a jour d'une tache existante.

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

    def execute(self, tache_id: int, dto: UpdateTacheDTO) -> TacheDTO:
        """
        Execute la mise a jour d'une tache.

        Args:
            tache_id: ID de la tache a modifier.
            dto: Les donnees de mise a jour.

        Returns:
            TacheDTO de la tache mise a jour.

        Raises:
            TacheNotFoundError: Si la tache n'existe pas.
            ValueError: Si les donnees sont invalides.
        """
        from .get_tache import TacheNotFoundError

        # Recuperer la tache existante
        tache = self.tache_repo.find_by_id(tache_id)
        if not tache:
            raise TacheNotFoundError(tache_id)

        updated_fields = []

        # Mettre a jour les champs fournis
        if dto.titre is not None:
            tache.update(titre=dto.titre)
            updated_fields.append("titre")

        if dto.description is not None:
            tache.update(description=dto.description)
            updated_fields.append("description")

        if dto.date_echeance is not None:
            date_echeance = date.fromisoformat(dto.date_echeance) if dto.date_echeance else None
            tache.update(date_echeance=date_echeance)
            updated_fields.append("date_echeance")

        if dto.unite_mesure is not None:
            unite_mesure = UniteMesure.from_string(dto.unite_mesure) if dto.unite_mesure else None
            tache.update(unite_mesure=unite_mesure)
            updated_fields.append("unite_mesure")

        if dto.quantite_estimee is not None:
            tache.update(quantite_estimee=dto.quantite_estimee)
            updated_fields.append("quantite_estimee")

        if dto.heures_estimees is not None:
            tache.update(heures_estimees=dto.heures_estimees)
            updated_fields.append("heures_estimees")

        if dto.statut is not None:
            statut = StatutTache.from_string(dto.statut)
            if statut == StatutTache.TERMINE:
                tache.terminer()
            else:
                tache.rouvrir()
            updated_fields.append("statut")

        if dto.ordre is not None:
            tache.modifier_ordre(dto.ordre)
            updated_fields.append("ordre")

        # Sauvegarder
        tache = self.tache_repo.save(tache)

        # Publier l'event
        if self.event_publisher and updated_fields:
            event = TacheUpdatedEvent(
                tache_id=tache.id,
                chantier_id=tache.chantier_id,
                updated_fields=updated_fields,
            )
            self.event_publisher(event)

        return TacheDTO.from_entity(tache)
