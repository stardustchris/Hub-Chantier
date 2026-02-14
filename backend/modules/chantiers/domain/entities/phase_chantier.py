"""Entité PhaseChantier - Phase/étape d'un chantier."""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class PhaseChantierEntity:
    """Phase d'un chantier avec identité propre.

    Permet de découper un chantier en plusieurs étapes
    avec leurs propres dates et ordonnancement.
    """

    id: Optional[int]
    chantier_id: int
    nom: str
    description: Optional[str] = None
    ordre: int = 1
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
