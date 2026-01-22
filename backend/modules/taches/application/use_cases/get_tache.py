"""Use Case GetTache - Recuperation d'une tache par ID."""

from ...domain.repositories import TacheRepository
from ..dtos import TacheDTO


class TacheNotFoundError(Exception):
    """Exception levee quand une tache n'est pas trouvee."""

    def __init__(self, tache_id: int):
        self.tache_id = tache_id
        self.message = f"Tache {tache_id} non trouvee"
        super().__init__(self.message)


class GetTacheUseCase:
    """
    Cas d'utilisation : Recuperation d'une tache par ID.

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

    def execute(self, tache_id: int, include_sous_taches: bool = True) -> TacheDTO:
        """
        Execute la recuperation d'une tache.

        Args:
            tache_id: ID de la tache.
            include_sous_taches: Inclure les sous-taches (TAC-02).

        Returns:
            TacheDTO de la tache trouvee.

        Raises:
            TacheNotFoundError: Si la tache n'existe pas.
        """
        tache = self.tache_repo.find_by_id(tache_id)
        if not tache:
            raise TacheNotFoundError(tache_id)

        # Charger les sous-taches si demande
        if include_sous_taches:
            sous_taches = self.tache_repo.find_children(tache_id)
            tache.sous_taches = sous_taches

        return TacheDTO.from_entity(tache)
