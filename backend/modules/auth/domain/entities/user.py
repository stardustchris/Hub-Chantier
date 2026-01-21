"""Entité User - Représente un utilisateur du système."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..value_objects import Email, PasswordHash, Role


@dataclass
class User:
    """
    Entité représentant un utilisateur.

    L'utilisateur est identifié par son ID unique.
    Contient la logique métier liée à l'authentification.

    Attributes:
        id: Identifiant unique (None si non persisté).
        email: Adresse email (unique).
        password_hash: Hash du mot de passe.
        nom: Nom de famille.
        prenom: Prénom.
        role: Rôle dans l'application.
        is_active: Indique si le compte est actif.
        created_at: Date de création.
        updated_at: Date de dernière modification.
    """

    email: Email
    password_hash: PasswordHash
    nom: str
    prenom: str
    role: Role = Role.EMPLOYE
    id: Optional[int] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Valide les données à la création."""
        if not self.nom or not self.nom.strip():
            raise ValueError("Le nom ne peut pas être vide")
        if not self.prenom or not self.prenom.strip():
            raise ValueError("Le prénom ne peut pas être vide")

        # Normalisation
        self.nom = self.nom.strip().upper()
        self.prenom = self.prenom.strip().title()

    @property
    def nom_complet(self) -> str:
        """Retourne le nom complet de l'utilisateur."""
        return f"{self.prenom} {self.nom}"

    def has_permission(self, permission: str) -> bool:
        """
        Vérifie si l'utilisateur a une permission.

        Args:
            permission: La permission à vérifier.

        Returns:
            True si l'utilisateur a la permission et est actif.
        """
        if not self.is_active:
            return False
        return self.role.has_permission(permission)

    def is_admin(self) -> bool:
        """Vérifie si l'utilisateur est administrateur."""
        return self.role == Role.ADMIN

    def is_chef_chantier(self) -> bool:
        """Vérifie si l'utilisateur est chef de chantier."""
        return self.role == Role.CHEF_CHANTIER

    def deactivate(self) -> None:
        """Désactive le compte utilisateur."""
        self.is_active = False
        self.updated_at = datetime.now()

    def activate(self) -> None:
        """Active le compte utilisateur."""
        self.is_active = True
        self.updated_at = datetime.now()

    def change_role(self, new_role: Role) -> None:
        """
        Change le rôle de l'utilisateur.

        Args:
            new_role: Le nouveau rôle.
        """
        self.role = new_role
        self.updated_at = datetime.now()

    def update_password(self, new_password_hash: PasswordHash) -> None:
        """
        Met à jour le mot de passe.

        Args:
            new_password_hash: Le nouveau hash du mot de passe.
        """
        self.password_hash = new_password_hash
        self.updated_at = datetime.now()

    def __eq__(self, other: object) -> bool:
        """Égalité basée sur l'ID (entité)."""
        if not isinstance(other, User):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
