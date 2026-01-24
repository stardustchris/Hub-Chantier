"""Événements domaine du module Chantiers."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ChantierCreatedEvent:
    """
    Événement émis lors de la création d'un chantier.

    Attributes:
        chantier_id: ID du chantier créé.
        code: Code du chantier (ex: A001).
        nom: Nom du chantier.
        statut: Statut initial.
        conducteur_ids: IDs des conducteurs assignés.
        chef_chantier_ids: IDs des chefs de chantier assignés.
        timestamp: Date/heure de l'événement.
    """

    chantier_id: int
    code: str
    nom: str
    statut: str
    conducteur_ids: tuple[int, ...]
    chef_chantier_ids: tuple[int, ...]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ChantierUpdatedEvent:
    """
    Événement émis lors de la mise à jour d'un chantier.

    Attributes:
        chantier_id: ID du chantier mis à jour.
        code: Code du chantier.
        changes: Dictionnaire des champs modifiés.
        timestamp: Date/heure de l'événement.
    """

    chantier_id: int
    code: str
    changes: tuple[tuple[str, str], ...]  # Tuple de (champ, nouvelle_valeur)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ChantierStatutChangedEvent:
    """
    Événement émis lors d'un changement de statut.

    Attributes:
        chantier_id: ID du chantier.
        code: Code du chantier.
        ancien_statut: Ancien statut.
        nouveau_statut: Nouveau statut.
        timestamp: Date/heure de l'événement.
    """

    chantier_id: int
    code: str
    ancien_statut: str
    nouveau_statut: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ChantierDeletedEvent:
    """
    Événement émis lors de la suppression d'un chantier.

    Attributes:
        chantier_id: ID du chantier supprimé.
        code: Code du chantier.
        nom: Nom du chantier.
        timestamp: Date/heure de l'événement.
    """

    chantier_id: int
    code: str
    nom: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ConducteurAssigneEvent:
    """
    Événement émis lors de l'assignation d'un conducteur.

    Attributes:
        chantier_id: ID du chantier.
        code: Code du chantier.
        conducteur_id: ID du conducteur assigné.
        timestamp: Date/heure de l'événement.
    """

    chantier_id: int
    code: str
    conducteur_id: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ChefChantierAssigneEvent:
    """
    Événement émis lors de l'assignation d'un chef de chantier.

    Attributes:
        chantier_id: ID du chantier.
        code: Code du chantier.
        chef_id: ID du chef de chantier assigné.
        timestamp: Date/heure de l'événement.
    """

    chantier_id: int
    code: str
    chef_id: int
    timestamp: datetime = field(default_factory=datetime.now)
