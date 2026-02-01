"""Use Cases pour la recherche avancee de devis.

DEV-19: Filtres avances.
"""

from datetime import date
from decimal import Decimal
from typing import Optional, List

from ...domain.value_objects import StatutDevis
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
        statut: Optional[StatutDevis] = None,
        statuts: Optional[List[StatutDevis]] = None,
        date_creation_min: Optional[date] = None,
        date_creation_max: Optional[date] = None,
        montant_min: Optional[Decimal] = None,
        montant_max: Optional[Decimal] = None,
        commercial_id: Optional[int] = None,
        conducteur_id: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> DevisListDTO:
        """Recherche les devis avec filtres avances.

        Args:
            client_nom: Filtre par nom client (recherche partielle).
            statut: Filtre par statut unique.
            statuts: Filtre par liste de statuts.
            date_creation_min: Date de creation minimum.
            date_creation_max: Date de creation maximum.
            montant_min: Montant HT minimum.
            montant_max: Montant HT maximum.
            commercial_id: Filtre par commercial assigne.
            conducteur_id: Filtre par conducteur assigne.
            search: Recherche textuelle sur numero/client/objet.
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste paginee des devis correspondants.
        """
        devis_list = self._devis_repository.find_all(
            client_nom=client_nom,
            statut=statut,
            statuts=statuts,
            date_creation_min=date_creation_min,
            date_creation_max=date_creation_max,
            montant_min=montant_min,
            montant_max=montant_max,
            commercial_id=commercial_id,
            conducteur_id=conducteur_id,
            search=search,
            limit=limit,
            offset=offset,
        )
        total = self._devis_repository.count(
            statut=statut,
            statuts=statuts,
            commercial_id=commercial_id,
        )

        return DevisListDTO(
            items=[DevisDTO.from_entity(d) for d in devis_list],
            total=total,
            limit=limit,
            offset=offset,
        )
