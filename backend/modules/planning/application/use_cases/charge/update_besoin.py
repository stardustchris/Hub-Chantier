"""Use Case UpdateBesoin - Mise a jour d'un besoin de charge."""

from typing import Optional

from ....domain.repositories import BesoinChargeRepository
from ....domain.value_objects.charge import TypeMetier
from ....domain.events.charge import BesoinChargeUpdated
from ...dtos.charge import UpdateBesoinDTO, BesoinChargeDTO
from ...ports import EventBus
from .exceptions import BesoinNotFoundError


class UpdateBesoinUseCase:
    """
    Cas d'utilisation : Mise a jour d'un besoin de charge.

    Permet de modifier le nombre d'heures, la note ou le type de metier
    d'un besoin existant.

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

    def execute(
        self,
        besoin_id: int,
        dto: UpdateBesoinDTO,
        updated_by: int,
    ) -> BesoinChargeDTO:
        """
        Execute la mise a jour d'un besoin.

        Args:
            besoin_id: ID du besoin a modifier.
            dto: Les donnees de mise a jour.
            updated_by: ID de l'utilisateur qui modifie.

        Returns:
            Le DTO du besoin mis a jour.

        Raises:
            BesoinNotFoundError: Si le besoin n'existe pas.
            ValueError: Si les donnees sont invalides.
        """
        # Recuperer le besoin existant
        besoin = self.besoin_repo.find_by_id(besoin_id)
        if besoin is None:
            raise BesoinNotFoundError(besoin_id)

        # Conserver l'ancienne valeur pour l'evenement
        ancien_besoin_heures = besoin.besoin_heures

        # Appliquer les modifications
        if dto.besoin_heures is not None:
            besoin.modifier_besoin(dto.besoin_heures)

        if dto.note is not None:
            if dto.note.strip():
                besoin.ajouter_note(dto.note)
            else:
                besoin.supprimer_note()

        if dto.type_metier is not None:
            nouveau_type = TypeMetier.from_string(dto.type_metier)
            besoin.changer_type_metier(nouveau_type)

        # Sauvegarder
        besoin = self.besoin_repo.save(besoin)

        # Publier l'evenement
        if self.event_bus:
            event = BesoinChargeUpdated(
                besoin_id=besoin.id,
                chantier_id=besoin.chantier_id,
                semaine_code=besoin.semaine.code,
                type_metier=besoin.type_metier.value,
                ancien_besoin_heures=ancien_besoin_heures,
                nouveau_besoin_heures=besoin.besoin_heures,
                updated_by=updated_by,
            )
            self.event_bus.publish(event)

        return BesoinChargeDTO.from_entity(besoin)
