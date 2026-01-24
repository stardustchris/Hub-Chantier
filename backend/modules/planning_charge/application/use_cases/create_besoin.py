"""Use Case CreateBesoin - Creation d'un besoin de charge."""

from typing import Optional

from ...domain.entities import BesoinCharge
from ...domain.repositories import BesoinChargeRepository
from ...domain.value_objects import Semaine, TypeMetier
from ...domain.events import BesoinChargeCreated
from ..dtos import CreateBesoinDTO, BesoinChargeDTO
from ..ports import EventBus
from .exceptions import BesoinAlreadyExistsError


class CreateBesoinUseCase:
    """
    Cas d'utilisation : Creation d'un besoin de charge.

    Cree un besoin en main d'oeuvre pour un chantier, une semaine
    et un type de metier donnes (PDC-16: Modal Planification besoins).

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

    def execute(self, dto: CreateBesoinDTO, created_by: int) -> BesoinChargeDTO:
        """
        Execute la creation d'un besoin.

        Args:
            dto: Les donnees de creation.
            created_by: ID de l'utilisateur createur.

        Returns:
            Le DTO du besoin cree.

        Raises:
            BesoinAlreadyExistsError: Si un besoin existe deja pour cette combinaison.
            ValueError: Si les donnees sont invalides.
        """
        # Parser les value objects
        semaine = Semaine.from_code(dto.semaine_code)
        type_metier = TypeMetier.from_string(dto.type_metier)

        # Verifier qu'un besoin n'existe pas deja
        if self.besoin_repo.exists(
            chantier_id=dto.chantier_id,
            semaine=semaine,
            type_metier=type_metier,
        ):
            raise BesoinAlreadyExistsError(
                chantier_id=dto.chantier_id,
                semaine_code=dto.semaine_code,
                type_metier=dto.type_metier,
            )

        # Creer l'entite
        besoin = BesoinCharge(
            chantier_id=dto.chantier_id,
            semaine=semaine,
            type_metier=type_metier,
            besoin_heures=dto.besoin_heures,
            note=dto.note,
            created_by=created_by,
        )

        # Sauvegarder
        besoin = self.besoin_repo.save(besoin)

        # Publier l'evenement
        if self.event_bus:
            event = BesoinChargeCreated(
                besoin_id=besoin.id,
                chantier_id=besoin.chantier_id,
                semaine_code=besoin.semaine.code,
                type_metier=besoin.type_metier.value,
                besoin_heures=besoin.besoin_heures,
                created_by=created_by,
            )
            self.event_bus.publish(event)

        return BesoinChargeDTO.from_entity(besoin)
