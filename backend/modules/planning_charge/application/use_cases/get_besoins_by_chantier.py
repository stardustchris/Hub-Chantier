"""Use Case GetBesoinsByChantier - Recuperation des besoins d'un chantier."""

from typing import List

from ...domain.repositories import BesoinChargeRepository
from ...domain.value_objects import Semaine
from ..dtos import BesoinChargeDTO
from .exceptions import InvalidSemaineRangeError


class GetBesoinsByChantierUseCase:
    """
    Cas d'utilisation : Recuperation des besoins d'un chantier.

    Retourne tous les besoins pour un chantier sur une plage de semaines.

    Attributes:
        besoin_repo: Repository pour acceder aux besoins.
    """

    def __init__(self, besoin_repo: BesoinChargeRepository):
        """
        Initialise le use case.

        Args:
            besoin_repo: Repository besoins (interface).
        """
        self.besoin_repo = besoin_repo

    def execute(
        self,
        chantier_id: int,
        semaine_debut: str,
        semaine_fin: str,
    ) -> List[BesoinChargeDTO]:
        """
        Recupere les besoins d'un chantier.

        Args:
            chantier_id: ID du chantier.
            semaine_debut: Code de la semaine de debut (SXX-YYYY).
            semaine_fin: Code de la semaine de fin (SXX-YYYY).

        Returns:
            Liste des DTOs de besoins.

        Raises:
            InvalidSemaineRangeError: Si la plage de semaines est invalide.
        """
        # Parser les semaines
        debut = Semaine.from_code(semaine_debut)
        fin = Semaine.from_code(semaine_fin)

        # Verifier que debut <= fin
        if debut > fin:
            raise InvalidSemaineRangeError(
                f"La semaine de debut ({semaine_debut}) doit etre "
                f"anterieure ou egale a la semaine de fin ({semaine_fin})"
            )

        # Recuperer les besoins
        besoins = self.besoin_repo.find_by_chantier(
            chantier_id=chantier_id,
            semaine_debut=debut,
            semaine_fin=fin,
        )

        # Convertir en DTOs
        return [BesoinChargeDTO.from_entity(b) for b in besoins]
