"""Domain Events liés aux utilisateurs."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..value_objects import Role


@dataclass(frozen=True)
class UserCreatedEvent:
    """
    Événement émis lors de la création d'un utilisateur.

    Attributes:
        user_id: ID de l'utilisateur créé.
        email: Email de l'utilisateur.
        nom: Nom de l'utilisateur.
        prenom: Prénom de l'utilisateur.
        role: Rôle assigné.
        timestamp: Moment de l'événement.
    """

    user_id: int
    email: str
    nom: str
    prenom: str
    role: Role
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class UserUpdatedEvent:
    """
    Événement émis lors de la mise à jour d'un utilisateur.

    Attributes:
        user_id: ID de l'utilisateur mis à jour.
        email: Email de l'utilisateur.
        nom: Nom de l'utilisateur.
        prenom: Prénom de l'utilisateur.
        timestamp: Moment de l'événement.
    """

    user_id: int
    email: str
    nom: str
    prenom: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class UserLoggedInEvent:
    """
    Événement émis lors de la connexion d'un utilisateur.

    Attributes:
        user_id: ID de l'utilisateur connecté.
        email: Email utilisé pour la connexion.
        timestamp: Moment de la connexion.
    """

    user_id: int
    email: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class UserDeactivatedEvent:
    """
    Événement émis lors de la désactivation d'un compte (USR-10).

    Attributes:
        user_id: ID de l'utilisateur désactivé.
        email: Email de l'utilisateur.
        deactivated_by: ID de l'admin qui a désactivé (optionnel).
        reason: Raison de la désactivation (optionnel).
        timestamp: Moment de la désactivation.
    """

    user_id: int
    email: str
    deactivated_by: Optional[int] = None
    reason: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class UserActivatedEvent:
    """
    Événement émis lors de la réactivation d'un compte.

    Attributes:
        user_id: ID de l'utilisateur activé.
        email: Email de l'utilisateur.
        activated_by: ID de l'admin qui a activé (optionnel).
        timestamp: Moment de l'activation.
    """

    user_id: int
    email: str
    activated_by: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class UserRoleChangedEvent:
    """
    Événement émis lors du changement de rôle d'un utilisateur.

    Attributes:
        user_id: ID de l'utilisateur.
        old_role: Ancien rôle.
        new_role: Nouveau rôle.
        changed_by: ID de l'admin qui a changé le rôle.
        timestamp: Moment du changement.
    """

    user_id: int
    old_role: Role
    new_role: Role
    changed_by: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
