"""Use Case ListAffectations - Liste des affectations avec filtres."""

from datetime import date
from typing import List, Optional

from ...domain.repositories import AffectationRepository
from ..dtos import ListAffectationsDTO, AffectationDTO, AffectationListDTO


class ListAffectationsUseCase:
    """
    Cas d'utilisation : Liste des affectations avec filtres et pagination.

    Permet de récupérer les affectations selon différents critères :
    - Par période (obligatoire)
    - Par utilisateur (PLN-02: Vue Utilisateurs)
    - Par chantier (PLN-01: Vue Chantiers)

    Attributes:
        affectation_repo: Repository pour accéder aux affectations.
    """

    def __init__(self, affectation_repo: AffectationRepository):
        """
        Initialise le use case.

        Args:
            affectation_repo: Repository affectations (interface).
        """
        self.affectation_repo = affectation_repo

    def execute(self, dto: ListAffectationsDTO) -> AffectationListDTO:
        """
        Liste les affectations selon les critères fournis.

        Args:
            dto: Critères de filtrage et pagination.

        Returns:
            AffectationListDTO avec la liste paginée des affectations.
        """
        # Parser les dates
        date_debut = date.fromisoformat(dto.date_debut)
        date_fin = date.fromisoformat(dto.date_fin)

        # Récupérer selon les filtres
        if dto.utilisateur_id:
            affectations = self.affectation_repo.find_by_utilisateur(
                utilisateur_id=dto.utilisateur_id,
                date_debut=date_debut,
                date_fin=date_fin,
            )
            total = len(affectations)
            # Appliquer pagination
            affectations = affectations[dto.skip : dto.skip + dto.limit]
        elif dto.chantier_id:
            affectations = self.affectation_repo.find_by_chantier(
                chantier_id=dto.chantier_id,
                date_debut=date_debut,
                date_fin=date_fin,
            )
            total = len(affectations)
            # Appliquer pagination
            affectations = affectations[dto.skip : dto.skip + dto.limit]
        else:
            # Toutes les affectations de la période
            affectations, total = self.affectation_repo.find_by_periode(
                date_debut=date_debut,
                date_fin=date_fin,
                skip=dto.skip,
                limit=dto.limit,
            )

        return AffectationListDTO(
            affectations=[AffectationDTO.from_entity(a) for a in affectations],
            total=total,
            skip=dto.skip,
            limit=dto.limit,
        )

    def get_by_date(self, date_affectation: str) -> AffectationListDTO:
        """
        Récupère toutes les affectations pour une date donnée.

        Args:
            date_affectation: Date au format ISO.

        Returns:
            AffectationListDTO avec toutes les affectations du jour.
        """
        date_parsed = date.fromisoformat(date_affectation)
        affectations = self.affectation_repo.find_by_date(date_parsed)

        return AffectationListDTO(
            affectations=[AffectationDTO.from_entity(a) for a in affectations],
            total=len(affectations),
            skip=0,
            limit=len(affectations),
        )

    def get_utilisateurs_non_planifies(self, date_affectation: str) -> List[int]:
        """
        Récupère les IDs des utilisateurs non planifiés pour une date (PLN-04, PLN-11).

        Args:
            date_affectation: Date au format ISO.

        Returns:
            Liste des IDs des utilisateurs sans affectation.
        """
        date_parsed = date.fromisoformat(date_affectation)
        return self.affectation_repo.find_utilisateurs_non_planifies(date_parsed)
