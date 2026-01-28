"""Use Case DeleteBesoin - Suppression d'un besoin de charge."""

from typing import Optional

from ....domain.repositories import BesoinChargeRepository
from ....domain.events.charge import BesoinChargeDeleted
from ...ports import EventBus
from .exceptions import BesoinNotFoundError


class DeleteBesoinUseCase:
    """
    Cas d'utilisation : Suppression d'un besoin de charge.

    Supprime un besoin existant et publie un evenement.

    Attributes:
        besoin_repo: Repository pour acceder aux besoins.
        event_bus: Bus d'evenements pour publier les domain events.
    """

    def __init__(
        self,
        besoin_repo: BesoinChargeRepository,
        event_bus: Optional[EventBus] = None,
    ):
        """
        Initialise le use case.

        Args:
            besoin_repo: Repository besoins (interface).
            event_bus: Bus d'evenements (optionnel).
        """
        self.besoin_repo = besoin_repo
        self.event_bus = event_bus

    def execute(self, besoin_id: int, deleted_by: int) -> bool:
        """
        Execute la suppression d'un besoin.

        Args:
            besoin_id: ID du besoin a supprimer.
            deleted_by: ID de l'utilisateur qui supprime.

        Returns:
            True si supprime avec succes.

        Raises:
            BesoinNotFoundError: Si le besoin n'existe pas.
        """
        # Recuperer le besoin pour l'evenement
        besoin = self.besoin_repo.find_by_id(besoin_id)
        if besoin is None:
            raise BesoinNotFoundError(besoin_id)

        # Conserver les infos pour l'evenement
        chantier_id = besoin.chantier_id
        semaine_code = besoin.semaine.code
        type_metier = besoin.type_metier.value
        besoin_heures = besoin.besoin_heures

        # Supprimer
        result = self.besoin_repo.delete(besoin_id)

        # Publier l'evenement
        if self.event_bus and result:
            event = BesoinChargeDeleted(
                besoin_id=besoin_id,
                chantier_id=chantier_id,
                semaine_code=semaine_code,
                type_metier=type_metier,
                besoin_heures=besoin_heures,
                deleted_by=deleted_by,
            )
            self.event_bus.publish(event)

        return result
