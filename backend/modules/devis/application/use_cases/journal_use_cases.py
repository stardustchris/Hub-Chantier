"""Use Cases pour le journal d'audit des devis.

DEV-18: Historique modifications.
"""

from datetime import datetime
from typing import List

from ...domain.entities.journal_devis import JournalDevis
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ..dtos.journal_dtos import JournalDevisDTO


class LogJournalDevisUseCase:
    """Use case pour enregistrer une entree dans le journal.

    DEV-18: Chaque modification est tracee.
    """

    def __init__(self, journal_repository: JournalDevisRepository):
        self._journal_repository = journal_repository

    def execute(
        self,
        devis_id: int,
        action: str,
        details: str,
        auteur_id: int,
    ) -> JournalDevisDTO:
        """Enregistre une entree dans le journal.

        Args:
            devis_id: L'ID du devis concerne.
            action: Le type d'action (creation, modification, etc.).
            details: Description detaillee de la modification.
            auteur_id: L'ID de l'auteur de la modification.

        Returns:
            Le DTO de l'entree creee.
        """
        entry = JournalDevis(
            devis_id=devis_id,
            action=action,
            details_json={"message": details},
            auteur_id=auteur_id,
            created_at=datetime.utcnow(),
        )

        entry = self._journal_repository.save(entry)

        return JournalDevisDTO.from_entity(entry)


class GetJournalDevisUseCase:
    """Use case pour consulter le journal d'un devis."""

    def __init__(self, journal_repository: JournalDevisRepository):
        self._journal_repository = journal_repository

    def execute(
        self,
        devis_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """Recupere le journal d'un devis avec pagination.

        Returns:
            Dictionnaire avec items, total, limit et offset.
        """
        entries = self._journal_repository.find_by_devis(
            devis_id=devis_id,
            limit=limit,
            offset=offset,
        )
        total = self._journal_repository.count_by_devis(devis_id)

        return {
            "items": [JournalDevisDTO.from_entity(e) for e in entries],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
