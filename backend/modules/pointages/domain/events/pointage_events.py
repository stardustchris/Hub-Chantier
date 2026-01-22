"""Domain Events liés aux pointages et feuilles d'heures."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List

from ..value_objects import StatutPointage


@dataclass(frozen=True)
class PointageCreatedEvent:
    """
    Événement émis lors de la création d'un pointage.

    Attributes:
        pointage_id: ID du pointage créé.
        utilisateur_id: ID de l'utilisateur.
        chantier_id: ID du chantier.
        date_pointage: Date du pointage.
        heures_normales: Heures normales (format HH:MM).
        created_by: ID du créateur.
        affectation_id: ID de l'affectation source (si FDH-10).
        timestamp: Moment de l'événement.
    """

    pointage_id: int
    utilisateur_id: int
    chantier_id: int
    date_pointage: date
    heures_normales: str
    created_by: int
    affectation_id: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class PointageUpdatedEvent:
    """
    Événement émis lors de la mise à jour d'un pointage.

    Attributes:
        pointage_id: ID du pointage.
        utilisateur_id: ID de l'utilisateur.
        chantier_id: ID du chantier.
        date_pointage: Date du pointage.
        heures_normales: Nouvelles heures normales.
        heures_supplementaires: Nouvelles heures sup.
        updated_by: ID de l'utilisateur qui a modifié.
        timestamp: Moment de l'événement.
    """

    pointage_id: int
    utilisateur_id: int
    chantier_id: int
    date_pointage: date
    heures_normales: str
    heures_supplementaires: str
    updated_by: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class PointageSignedEvent:
    """
    Événement émis lors de la signature d'un pointage (FDH-12).

    Attributes:
        pointage_id: ID du pointage.
        utilisateur_id: ID de l'utilisateur qui a signé.
        signature: La signature électronique.
        timestamp: Moment de la signature.
    """

    pointage_id: int
    utilisateur_id: int
    signature: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class PointageSubmittedEvent:
    """
    Événement émis lors de la soumission d'un pointage pour validation.

    Attributes:
        pointage_id: ID du pointage.
        utilisateur_id: ID de l'utilisateur.
        chantier_id: ID du chantier.
        date_pointage: Date du pointage.
        timestamp: Moment de la soumission.
    """

    pointage_id: int
    utilisateur_id: int
    chantier_id: int
    date_pointage: date
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class PointageValidatedEvent:
    """
    Événement émis lors de la validation d'un pointage.

    Attributes:
        pointage_id: ID du pointage.
        utilisateur_id: ID de l'utilisateur pointé.
        chantier_id: ID du chantier.
        date_pointage: Date du pointage.
        validateur_id: ID du validateur.
        timestamp: Moment de la validation.
    """

    pointage_id: int
    utilisateur_id: int
    chantier_id: int
    date_pointage: date
    validateur_id: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class PointageRejectedEvent:
    """
    Événement émis lors du rejet d'un pointage.

    Attributes:
        pointage_id: ID du pointage.
        utilisateur_id: ID de l'utilisateur pointé.
        chantier_id: ID du chantier.
        date_pointage: Date du pointage.
        validateur_id: ID du validateur.
        motif: Motif du rejet.
        timestamp: Moment du rejet.
    """

    pointage_id: int
    utilisateur_id: int
    chantier_id: int
    date_pointage: date
    validateur_id: int
    motif: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class PointageDeletedEvent:
    """
    Événement émis lors de la suppression d'un pointage.

    Attributes:
        pointage_id: ID du pointage supprimé.
        utilisateur_id: ID de l'utilisateur.
        chantier_id: ID du chantier.
        date_pointage: Date du pointage.
        deleted_by: ID de l'utilisateur qui a supprimé.
        timestamp: Moment de la suppression.
    """

    pointage_id: int
    utilisateur_id: int
    chantier_id: int
    date_pointage: date
    deleted_by: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class PointageBulkCreatedEvent:
    """
    Événement émis lors de la création en masse depuis le planning (FDH-10).

    Attributes:
        pointage_ids: Liste des IDs de pointages créés.
        utilisateur_id: ID de l'utilisateur.
        semaine_debut: Date de début de la semaine.
        chantier_ids: Liste des chantiers concernés.
        source: Source de la création (ex: "planning").
        timestamp: Moment de la création.
    """

    pointage_ids: tuple  # Tuple pour être hashable
    utilisateur_id: int
    semaine_debut: date
    chantier_ids: tuple  # Tuple pour être hashable
    source: str = "planning"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class FeuilleHeuresCreatedEvent:
    """
    Événement émis lors de la création d'une feuille d'heures.

    Attributes:
        feuille_id: ID de la feuille.
        utilisateur_id: ID de l'utilisateur.
        semaine_debut: Date de début de semaine.
        numero_semaine: Numéro de la semaine.
        annee: Année.
        timestamp: Moment de la création.
    """

    feuille_id: int
    utilisateur_id: int
    semaine_debut: date
    numero_semaine: int
    annee: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class FeuilleHeuresExportedEvent:
    """
    Événement émis lors de l'export d'une feuille d'heures (FDH-03, FDH-17).

    Attributes:
        feuille_id: ID de la feuille.
        utilisateur_id: ID de l'utilisateur.
        semaine_debut: Date de début.
        format_export: Format d'export (csv, xlsx, pdf, erp).
        destination: Destination de l'export.
        exported_by: ID de l'exportateur.
        timestamp: Moment de l'export.
    """

    feuille_id: int
    utilisateur_id: int
    semaine_debut: date
    format_export: str
    destination: Optional[str] = None
    exported_by: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class VariablePaieCreatedEvent:
    """
    Événement émis lors de la création d'une variable de paie (FDH-13).

    Attributes:
        variable_id: ID de la variable.
        pointage_id: ID du pointage associé.
        type_variable: Type de variable.
        valeur: Valeur de la variable.
        date_application: Date d'application.
        timestamp: Moment de la création.
    """

    variable_id: int
    pointage_id: int
    type_variable: str
    valeur: str  # Decimal sérialisé en string
    date_application: date
    timestamp: datetime = field(default_factory=datetime.now)
