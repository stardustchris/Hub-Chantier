"""Use Case ReorderTaches - Reorganiser les taches par drag & drop (TAC-15)."""

from typing import List

from ...domain.repositories import TacheRepository
from ..dtos import TacheDTO


class ReorderTachesUseCase:
    """
    Cas d'utilisation : Reorganiser les taches.

    Selon CDC Section 13 - TAC-15: Drag & drop pour reordonner.

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

    def execute(self, tache_id: int, nouvel_ordre: int) -> TacheDTO:
        """
        Deplace une tache vers une nouvelle position.

        Args:
            tache_id: ID de la tache a deplacer.
            nouvel_ordre: Nouvelle position.

        Returns:
            TacheDTO de la tache deplacee.

        Raises:
            TacheNotFoundError: Si la tache n'existe pas.
        """
        from .get_tache import TacheNotFoundError

        # Recuperer la tache
        tache = self.tache_repo.find_by_id(tache_id)
        if not tache:
            raise TacheNotFoundError(tache_id)

        # Reordonner
        self.tache_repo.reorder(tache_id, nouvel_ordre)

        # Recuperer la tache mise a jour
        tache = self.tache_repo.find_by_id(tache_id)

        return TacheDTO.from_entity(tache)

    def execute_batch(self, ordres: List[dict]) -> List[TacheDTO]:
        """
        Reordonne plusieurs taches en une fois.

        Args:
            ordres: Liste de {"tache_id": int, "ordre": int}.

        Returns:
            Liste des TacheDTO mis a jour.
        """
        results = []
        for item in ordres:
            tache_id = item.get("tache_id")
            ordre = item.get("ordre")
            if tache_id is not None and ordre is not None:
                dto = self.execute(tache_id, ordre)
                results.append(dto)
        return results
