"""Domain Event pour la validation par lot de pointages (GAP-FDH-004)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class PointagesBulkValidatedEvent:
    """
    Événement émis lors de la validation par lot de pointages.

    Cet événement est publié après la validation réussie d'un ensemble de pointages
    en une seule transaction. Il permet aux autres modules (notifications, dashboard)
    de réagir à cette validation groupée.

    Attributes:
        pointage_ids: Liste des IDs de pointages validés.
        validateur_id: ID du validateur (chef/conducteur/admin).
        success_count: Nombre de pointages validés avec succès.
        failure_count: Nombre de pointages en échec.
        timestamp: Moment de l'événement.
    """

    pointage_ids: tuple  # Tuple pour être hashable (frozen dataclass)
    validateur_id: int
    success_count: int
    failure_count: int
    timestamp: datetime = field(default_factory=datetime.now)
