"""Use Case ListFeuillesTaches - Liste des feuilles de taches."""

from datetime import date
from typing import Optional

from ...domain.repositories import FeuilleTacheRepository
from ...domain.entities.feuille_tache import StatutValidation
from ..dtos import FeuilleTacheDTO, FeuilleTacheListDTO


class ListFeuillesTachesUseCase:
    """
    Cas d'utilisation : Liste des feuilles de taches.

    Permet de lister les feuilles par tache, utilisateur ou chantier.

    Attributes:
        feuille_repo: Repository pour les feuilles de taches.
    """

    def __init__(self, feuille_repo: FeuilleTacheRepository):
        """
        Initialise le use case.

        Args:
            feuille_repo: Repository feuilles (interface).
        """
        self.feuille_repo = feuille_repo

    def execute_by_tache(
        self,
        tache_id: int,
        page: int = 1,
        size: int = 50,
    ) -> FeuilleTacheListDTO:
        """
        Liste les feuilles d'une tache.

        Args:
            tache_id: ID de la tache.
            page: Numero de page.
            size: Nombre d'elements par page.

        Returns:
            FeuilleTacheListDTO avec la liste paginee.
        """
        skip = (page - 1) * size

        feuilles = self.feuille_repo.find_by_tache(tache_id, skip=skip, limit=size)
        total = self.feuille_repo.count_by_tache(tache_id)
        total_heures = self.feuille_repo.get_total_heures_tache(tache_id)
        total_quantite = self.feuille_repo.get_total_quantite_tache(tache_id)

        items = [FeuilleTacheDTO.from_entity(f) for f in feuilles]
        pages = (total + size - 1) // size if size > 0 else 0

        return FeuilleTacheListDTO(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
            total_heures=total_heures,
            total_quantite=total_quantite,
        )

    def execute_by_chantier(
        self,
        chantier_id: int,
        date_debut: Optional[str] = None,
        date_fin: Optional[str] = None,
        statut: Optional[str] = None,
        page: int = 1,
        size: int = 50,
    ) -> FeuilleTacheListDTO:
        """
        Liste les feuilles d'un chantier.

        Args:
            chantier_id: ID du chantier.
            date_debut: Date de debut (ISO format).
            date_fin: Date de fin (ISO format).
            statut: Filtrer par statut de validation.
            page: Numero de page.
            size: Nombre d'elements par page.

        Returns:
            FeuilleTacheListDTO avec la liste paginee.
        """
        skip = (page - 1) * size

        # Convertir les dates
        dt_debut = date.fromisoformat(date_debut) if date_debut else None
        dt_fin = date.fromisoformat(date_fin) if date_fin else None

        # Convertir le statut
        statut_enum = None
        if statut:
            statut_enum = StatutValidation(statut)

        feuilles = self.feuille_repo.find_by_chantier(
            chantier_id=chantier_id,
            date_debut=dt_debut,
            date_fin=dt_fin,
            statut=statut_enum,
            skip=skip,
            limit=size,
        )

        # Calculer le total (approximatif pour la pagination)
        total = len(feuilles)
        if len(feuilles) == size:
            total = size * page + 1  # Indique qu'il y a plus de pages

        items = [FeuilleTacheDTO.from_entity(f) for f in feuilles]
        pages = (total + size - 1) // size if size > 0 else 0

        # Calculer les totaux
        total_heures = sum(f.heures_travaillees for f in feuilles)
        total_quantite = sum(f.quantite_realisee for f in feuilles)

        return FeuilleTacheListDTO(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
            total_heures=total_heures,
            total_quantite=total_quantite,
        )

    def execute_en_attente(
        self,
        chantier_id: Optional[int] = None,
        page: int = 1,
        size: int = 50,
    ) -> FeuilleTacheListDTO:
        """
        Liste les feuilles en attente de validation.

        Args:
            chantier_id: Filtrer par chantier (optionnel).
            page: Numero de page.
            size: Nombre d'elements par page.

        Returns:
            FeuilleTacheListDTO avec la liste paginee.
        """
        skip = (page - 1) * size

        feuilles = self.feuille_repo.find_en_attente_validation(
            chantier_id=chantier_id,
            skip=skip,
            limit=size,
        )

        total = len(feuilles)
        items = [FeuilleTacheDTO.from_entity(f) for f in feuilles]
        pages = (total + size - 1) // size if size > 0 else 0

        return FeuilleTacheListDTO(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
        )
