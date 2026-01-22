"""Domain Events lies aux affectations du planning."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class AffectationCreatedEvent:
    """
    Evenement emis lors de la creation d'une affectation.

    Cet evenement est publie quand un utilisateur est affecte a un chantier.
    Il peut etre utilise pour notifier l'utilisateur concerne ou mettre
    a jour des statistiques.

    Attributes:
        affectation_id: ID de l'affectation creee.
        utilisateur_id: ID de l'utilisateur affecte.
        chantier_id: ID du chantier concerne.
        date: Date de l'affectation.
        created_by: ID de l'utilisateur qui a cree l'affectation.
        timestamp: Moment de l'evenement.

    Example:
        >>> event = AffectationCreatedEvent(
        ...     affectation_id=1,
        ...     utilisateur_id=5,
        ...     chantier_id=10,
        ...     date=date(2026, 1, 22),
        ...     created_by=3
        ... )
    """

    affectation_id: int
    utilisateur_id: int
    chantier_id: int
    date: date
    created_by: int
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'evenement en dictionnaire.

        Returns:
            Dictionnaire representant l'evenement.
        """
        return {
            "event_type": "AffectationCreated",
            "affectation_id": self.affectation_id,
            "utilisateur_id": self.utilisateur_id,
            "chantier_id": self.chantier_id,
            "date": self.date.isoformat(),
            "created_by": self.created_by,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class AffectationUpdatedEvent:
    """
    Evenement emis lors de la modification d'une affectation.

    Contient les changements effectues pour permettre un audit complet.

    Attributes:
        affectation_id: ID de l'affectation modifiee.
        utilisateur_id: ID de l'utilisateur affecte.
        chantier_id: ID du chantier concerne.
        changes: Dictionnaire des modifications (cle: nouveau valeur).
        updated_by: ID de l'utilisateur qui a effectue la modification.
        timestamp: Moment de l'evenement.

    Example:
        >>> event = AffectationUpdatedEvent(
        ...     affectation_id=1,
        ...     utilisateur_id=5,
        ...     chantier_id=10,
        ...     changes={"heure_debut": "08:00", "heure_fin": "17:00"},
        ...     updated_by=3
        ... )
    """

    affectation_id: int
    utilisateur_id: int
    chantier_id: int
    changes: Dict[str, Any]
    updated_by: int
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'evenement en dictionnaire.

        Returns:
            Dictionnaire representant l'evenement.
        """
        return {
            "event_type": "AffectationUpdated",
            "affectation_id": self.affectation_id,
            "utilisateur_id": self.utilisateur_id,
            "chantier_id": self.chantier_id,
            "changes": self.changes,
            "updated_by": self.updated_by,
            "timestamp": self.timestamp.isoformat(),
        }

    @property
    def changed_fields(self) -> list:
        """
        Retourne la liste des champs modifies.

        Returns:
            Liste des noms de champs modifies.
        """
        return list(self.changes.keys())

    def has_changed(self, field_name: str) -> bool:
        """
        Verifie si un champ specifique a ete modifie.

        Args:
            field_name: Nom du champ a verifier.

        Returns:
            True si le champ fait partie des modifications.
        """
        return field_name in self.changes


@dataclass(frozen=True)
class AffectationDeletedEvent:
    """
    Evenement emis lors de la suppression d'une affectation.

    Utile pour notifier l'utilisateur ou mettre a jour les statistiques.

    Attributes:
        affectation_id: ID de l'affectation supprimee.
        utilisateur_id: ID de l'utilisateur qui etait affecte.
        chantier_id: ID du chantier concerne.
        date: Date de l'affectation supprimee.
        deleted_by: ID de l'utilisateur qui a supprime l'affectation.
        timestamp: Moment de l'evenement.

    Example:
        >>> event = AffectationDeletedEvent(
        ...     affectation_id=1,
        ...     utilisateur_id=5,
        ...     chantier_id=10,
        ...     date=date(2026, 1, 22),
        ...     deleted_by=3
        ... )
    """

    affectation_id: int
    utilisateur_id: int
    chantier_id: int
    date: date
    deleted_by: int
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'evenement en dictionnaire.

        Returns:
            Dictionnaire representant l'evenement.
        """
        return {
            "event_type": "AffectationDeleted",
            "affectation_id": self.affectation_id,
            "utilisateur_id": self.utilisateur_id,
            "chantier_id": self.chantier_id,
            "date": self.date.isoformat(),
            "deleted_by": self.deleted_by,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class AffectationBulkCreatedEvent:
    """
    Evenement emis lors de la creation en masse d'affectations.

    Utile pour les affectations recurrentes ou les copies multiples.

    Attributes:
        affectation_ids: Liste des IDs d'affectations creees.
        utilisateur_id: ID de l'utilisateur affecte.
        chantier_id: ID du chantier concerne.
        date_debut: Date de debut de la plage.
        date_fin: Date de fin de la plage.
        created_by: ID de l'utilisateur qui a cree les affectations.
        count: Nombre d'affectations creees.
        timestamp: Moment de l'evenement.
    """

    affectation_ids: tuple  # Utilise tuple pour frozen=True
    utilisateur_id: int
    chantier_id: int
    date_debut: date
    date_fin: date
    created_by: int
    count: int
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'evenement en dictionnaire.

        Returns:
            Dictionnaire representant l'evenement.
        """
        return {
            "event_type": "AffectationBulkCreated",
            "affectation_ids": list(self.affectation_ids),
            "utilisateur_id": self.utilisateur_id,
            "chantier_id": self.chantier_id,
            "date_debut": self.date_debut.isoformat(),
            "date_fin": self.date_fin.isoformat(),
            "created_by": self.created_by,
            "count": self.count,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class AffectationBulkDeletedEvent:
    """
    Evenement emis lors de la suppression en masse d'affectations.

    Attributes:
        utilisateur_id: ID de l'utilisateur concerne (optionnel).
        chantier_id: ID du chantier concerne (optionnel).
        date_debut: Date de debut de la plage.
        date_fin: Date de fin de la plage.
        deleted_by: ID de l'utilisateur qui a supprime les affectations.
        count: Nombre d'affectations supprimees.
        timestamp: Moment de l'evenement.
    """

    date_debut: date
    date_fin: date
    deleted_by: int
    count: int
    utilisateur_id: Optional[int] = None
    chantier_id: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'evenement en dictionnaire.

        Returns:
            Dictionnaire representant l'evenement.
        """
        return {
            "event_type": "AffectationBulkDeleted",
            "utilisateur_id": self.utilisateur_id,
            "chantier_id": self.chantier_id,
            "date_debut": self.date_debut.isoformat(),
            "date_fin": self.date_fin.isoformat(),
            "deleted_by": self.deleted_by,
            "count": self.count,
            "timestamp": self.timestamp.isoformat(),
        }
