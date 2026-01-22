"""Use Case ListTaches - Liste des taches d'un chantier (TAC-01)."""

from typing import Optional

from ...domain.repositories import TacheRepository
from ...domain.value_objects import StatutTache
from ..dtos import TacheDTO, TacheListDTO


class ListTachesUseCase:
    """
    Cas d'utilisation : Liste des taches d'un chantier.

    Selon CDC Section 13 - TAC-01 (onglet Taches par chantier),
    TAC-02 (structure hierarchique), TAC-14 (recherche).

    Attributes:
        tache_repo: Repository pour acceder aux taches.
    """

    def __init__(self, tache_repo: TacheRepository):
        """
        Initialise le use case.

        Args:
            tache_repo: Repository taches (interface).
        """
        self.tache_repo = tache_repo

    def execute(
        self,
        chantier_id: int,
        query: Optional[str] = None,
        statut: Optional[str] = None,
        page: int = 1,
        size: int = 50,
        include_sous_taches: bool = True,
    ) -> TacheListDTO:
        """
        Execute la liste des taches.

        Args:
            chantier_id: ID du chantier.
            query: Recherche textuelle (TAC-14).
            statut: Filtrer par statut.
            page: Numero de page.
            size: Nombre d'elements par page.
            include_sous_taches: Inclure les sous-taches (TAC-02).

        Returns:
            TacheListDTO avec la liste paginee.
        """
        skip = (page - 1) * size

        # Convertir le statut si fourni
        statut_enum = None
        if statut:
            statut_enum = StatutTache.from_string(statut)

        # Rechercher avec filtres
        if query or statut_enum:
            taches, total = self.tache_repo.search(
                chantier_id=chantier_id,
                query=query,
                statut=statut_enum,
                skip=skip,
                limit=size,
            )
        else:
            # Recuperer les taches racines (parent_id = None)
            taches = self.tache_repo.find_by_chantier(
                chantier_id=chantier_id,
                include_sous_taches=include_sous_taches,
                skip=skip,
                limit=size,
            )
            total = self.tache_repo.count_by_chantier(chantier_id)

        # Charger les sous-taches pour chaque tache racine
        if include_sous_taches:
            for tache in taches:
                if tache.id:
                    sous_taches = self.tache_repo.find_children(tache.id)
                    tache.sous_taches = sous_taches

        # Convertir en DTOs
        items = [TacheDTO.from_entity(t) for t in taches]

        # Calculer le nombre de pages
        pages = (total + size - 1) // size if size > 0 else 0

        return TacheListDTO(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
        )
