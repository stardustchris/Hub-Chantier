"""Événement de domaine : Escalade de signalement (SIG-17)."""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List

from shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class EscaladeSignalementEvent(DomainEvent):
    """
    Événement émis lors de l'escalade d'un signalement.

    Cet événement déclenche l'envoi de notifications push aux destinataires
    selon le niveau d'escalade atteint.

    Attributes:
        signalement_id: ID du signalement escaladé.
        chantier_id: ID du chantier concerné.
        niveau: Niveau d'escalade (chef_chantier, conducteur, admin).
        pourcentage_temps: % de temps écoulé au moment de l'escalade.
        titre: Titre du signalement.
        priorite: Priorité du signalement.
        destinataires_roles: Rôles à notifier.
    """

    def __init__(
        self,
        signalement_id: int,
        chantier_id: int,
        niveau: str,
        pourcentage_temps: float,
        titre: str,
        priorite: str,
        destinataires_roles: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            event_type="signalement.escaladed",
            aggregate_id=str(signalement_id),
            data={
                "signalement_id": signalement_id,
                "chantier_id": chantier_id,
                "niveau": niveau,
                "pourcentage_temps": pourcentage_temps,
                "titre": titre,
                "priorite": priorite,
                "destinataires_roles": destinataires_roles,
            },
            metadata=metadata or {},
        )
