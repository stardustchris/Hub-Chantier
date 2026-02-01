"""Use Cases pour la recherche avancee de devis.

DEV-19: Filtres avances.
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from ...domain.repositories.devis_repository import DevisRepository
from ..dtos.devis_dtos import DevisDTO, DevisListDTO


class SearchDevisUseCase:
    """Use case pour rechercher des devis avec filtres avances.

    DEV-19: Recherche par client, statut, date, montant, commercial.
    """

    def __init__(self, devis_repository: DevisRepository):
        self._devis_repository = devis_repository

    def execute(
        self,
        client_nom: Optional[str] = None,
        statut: Optional[str] = None,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        montant_min: Optional[Decimal] = None,
        montant_max: Optional[Decimal] = None,
        commercial_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> DevisListDTO:
        """Recherche les devis avec filtres avances.

        Args:
            client_nom: Filtre par nom client (recherche partielle).
            statut: Filtre par statut exact.
            date_debut: Date de creation minimum.
            date_fin: Date de creation maximum.
            montant_min: Montant HT minimum.
            montant_max: Montant HT maximum.
            commercial_id: Filtre par commercial assigne.
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste paginee des devis correspondants.
        """
        devis_list = self._devis_repository.search(
            client_nom=client_nom,
            statut=statut,
            date_debut=date_debut,
            date_fin=date_fin,
            montant_min=montant_min,
            montant_max=montant_max,
            commercial_id=commercial_id,
            skip=offset,
            limit=limit,
        )
        total = self._devis_repository.count_search(
            client_nom=client_nom,
            statut=statut,
            date_debut=date_debut,
            date_fin=date_fin,
            montant_min=montant_min,
            montant_max=montant_max,
            commercial_id=commercial_id,
        )

        return DevisListDTO(
            items=[DevisDTO.from_entity(d) for d in devis_list],
            total=total,
            limit=limit,
            offset=offset,
        )
