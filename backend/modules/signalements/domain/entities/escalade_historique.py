"""Entité EscaladeHistorique - Historique des escalades de signalements (SIG-17)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class EscaladeHistorique:
    """
    Enregistrement d'une escalade pour un signalement.

    Selon CDC SIG-17: Remontée hiérarchique progressive avec historique.

    Attributes:
        id: Identifiant unique.
        signalement_id: ID du signalement escaladé.
        niveau: Niveau d'escalade atteint (createur, chef_chantier, conducteur, admin).
        pourcentage_temps: Pourcentage de temps écoulé au moment de l'escalade.
        destinataires_roles: Rôles notifiés lors de cette escalade.
        message: Message de notification envoyé.
        created_at: Date de l'escalade.
    """

    signalement_id: int
    niveau: str
    pourcentage_temps: float
    destinataires_roles: List[str] = field(default_factory=list)
    message: Optional[str] = None
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Valide les données."""
        niveaux_valides = ("createur", "chef_chantier", "conducteur", "admin")
        if self.niveau not in niveaux_valides:
            raise ValueError(
                f"Niveau d'escalade invalide: {self.niveau}. "
                f"Valeurs acceptées: {', '.join(niveaux_valides)}"
            )
        if self.pourcentage_temps < 0:
            raise ValueError("Le pourcentage de temps ne peut pas être négatif")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EscaladeHistorique):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id) if self.id else hash(id(self))
