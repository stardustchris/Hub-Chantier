"""Use Case DeleteChantier - Suppression d'un chantier."""

import logging
from typing import Optional, Callable

from ...domain.repositories import ChantierRepository

logger = logging.getLogger(__name__)
from ...domain.events import ChantierDeletedEvent
from .get_chantier import ChantierNotFoundError


class ChantierActifError(Exception):
    """Exception levée quand on essaie de supprimer un chantier actif."""

    def __init__(self, chantier_id: int) -> None:
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
    ) -> None:
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
        # Logging structured (GAP-CHT-006)
        logger.info(
            "Use case execution started",
            extra={
                "event": "chantier.use_case.started",
                "use_case": "DeleteChantierUseCase",
                "chantier_id": chantier_id,
                "operation": "delete",
                "force": force,
            }
        )

        try:
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

            logger.info(
                "Use case execution succeeded",
                extra={
                    "event": "chantier.use_case.succeeded",
                    "use_case": "DeleteChantierUseCase",
                    "chantier_id": chantier_id,
                    "chantier_code": code,
                }
            )

            return result

        except Exception as e:
            logger.error(
                "Use case execution failed",
                extra={
                    "event": "chantier.use_case.failed",
                    "use_case": "DeleteChantierUseCase",
                    "chantier_id": chantier_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
            )
            raise
