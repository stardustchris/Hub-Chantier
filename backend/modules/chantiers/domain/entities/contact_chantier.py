"""Entité ContactChantier - Contact associé à un chantier (CHT-07)."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ContactChantierEntity:
    """Contact sur place d'un chantier avec identité propre.

    Distinct du value object ContactChantier (contact unique legacy).
    Représente les multi-contacts de la table contacts_chantier.
    """

    id: Optional[int]
    chantier_id: int
    nom: str
    telephone: str
    profession: Optional[str] = None
