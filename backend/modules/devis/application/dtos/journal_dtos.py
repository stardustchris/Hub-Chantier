"""DTOs pour le journal d'audit des devis.

DEV-18: Historique modifications.
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.journal_devis import JournalDevis


@dataclass
class JournalDevisDTO:
    """DTO de sortie pour une entree du journal devis."""

    id: int
    devis_id: int
    action: str
    details: Optional[str]
    auteur_id: Optional[int]
    created_at: Optional[str]

    @classmethod
    def from_entity(cls, journal: JournalDevis) -> JournalDevisDTO:
        """Cree un DTO depuis une entite JournalDevis."""
        # Convertir details_json en string lisible
        details_str: Optional[str] = None
        if journal.details_json is not None:
            if "message" in journal.details_json:
                details_str = journal.details_json["message"]
            else:
                details_str = json.dumps(journal.details_json, ensure_ascii=False)

        return cls(
            id=journal.id,
            devis_id=journal.devis_id,
            action=journal.action,
            details=details_str,
            auteur_id=journal.auteur_id,
            created_at=journal.created_at.isoformat() if journal.created_at else None,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "devis_id": self.devis_id,
            "action": self.action,
            "details": self.details,
            "auteur_id": self.auteur_id,
            "created_at": self.created_at,
        }
