"""Entite JournalDevis - Historique des modifications.

DEV-18: Historique modifications - Journal complet des changements
avec auteur, timestamp, type modification et details.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class JournalDevis:
    """Represente une entree du journal d'audit d'un devis.

    Table append-only : les entrees ne sont jamais modifiees ni supprimees.
    Chaque modification significative sur un devis genere une entree.
    """

    id: Optional[int] = None
    devis_id: int = 0
    action: str = ""
    auteur_id: Optional[int] = None
    details_json: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if self.devis_id <= 0:
            raise ValueError("L'ID du devis est obligatoire")
        if not self.action or not self.action.strip():
            raise ValueError("L'action est obligatoire")
        if self.auteur_id is not None and self.auteur_id <= 0:
            raise ValueError("L'ID de l'auteur doit etre positif ou None pour les actions systeme")

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "devis_id": self.devis_id,
            "action": self.action,
            "auteur_id": self.auteur_id,
            "details_json": self.details_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
