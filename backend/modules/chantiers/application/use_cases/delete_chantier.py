"""Use Case DeleteChantier - Suppression d'un chantier."""

from typing import Optional, Callable

from ...domain.repositories import ChantierRepository
from ...domain.events import ChantierDeletedEvent


class ChantierNotFoundError(Exception):
    """Exception levée quand le chantier n'est pas trouvé."""

    def __init__(self, chantier_id: int):
        self.chantier_id = chantier_id
        self.message = f"Chantier non trouvé: {chantier_id}"
        super().__init__(self.message)


class ChantierActifError(Exception):
    """Exception levée quand on essaie de supprimer un chantier actif."""

    def __init__(self, chantier_id: int):
        self.chantier_id = chantier_id
        self.message = (
            f"Impossible de supprimer le chantier {chantier_id}: "
            f"il doit d'abord être fermé"
        )
        super().__init__(self.message)


class DeleteChantierUseCase:
    """
    Cas d'utilisation : Suppression d'un chantier.

    Un chantier ne peut être supprimé que s'il est fermé.
    Note: En pratique, on préférera souvent archiver plutôt que supprimer.

    Attributes:
        chantier_repo: Repository pour accéder aux chantiers.
        event_publisher: Fonction pour publier les events (optionnel).
    """

    def __init__(
        self,
        chantier_repo: ChantierRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            chantier_repo: Repository chantiers (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.chantier_repo = chantier_repo
        self.event_publisher = event_publisher

    def execute(self, chantier_id: int, force: bool = False) -> bool:
        """
        Exécute la suppression du chantier.

        Args:
            chantier_id: L'ID du chantier à supprimer.
            force: Si True, permet de supprimer même un chantier actif.

        Returns:
            True si la suppression a réussi.

        Raises:
            ChantierNotFoundError: Si le chantier n'existe pas.
            ChantierActifError: Si le chantier est actif et force=False.
        """
        # Récupérer le chantier
        chantier = self.chantier_repo.find_by_id(chantier_id)
        if not chantier:
            raise ChantierNotFoundError(chantier_id)

        # Vérifier que le chantier est fermé (sauf si force)
        if chantier.is_active and not force:
            raise ChantierActifError(chantier_id)

        # Sauvegarder les infos pour l'event
        code = str(chantier.code)
        nom = chantier.nom

        # Supprimer
        result = self.chantier_repo.delete(chantier_id)

        # Publier l'event
        if result and self.event_publisher:
            event = ChantierDeletedEvent(
                chantier_id=chantier_id,
                code=code,
                nom=nom,
            )
            self.event_publisher(event)

        return result
