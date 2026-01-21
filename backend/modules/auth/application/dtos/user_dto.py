"""DTOs pour les utilisateurs."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ...domain.entities import User
from ...domain.value_objects import Role


@dataclass(frozen=True)
class UserDTO:
    """
    Data Transfer Object pour un utilisateur.

    Utilisé pour transférer les données utilisateur entre les couches.
    Ne contient JAMAIS le mot de passe.

    Attributes:
        id: Identifiant unique.
        email: Adresse email.
        nom: Nom de famille.
        prenom: Prénom.
        role: Rôle dans l'application.
        is_active: Statut du compte.
        created_at: Date de création.
    """

    id: int
    email: str
    nom: str
    prenom: str
    role: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> "UserDTO":
        """
        Crée un DTO à partir d'une entité User.

        Args:
            user: L'entité User source.

        Returns:
            Le DTO correspondant.
        """
        return cls(
            id=user.id,
            email=str(user.email),
            nom=user.nom,
            prenom=user.prenom,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )


@dataclass(frozen=True)
class LoginDTO:
    """
    DTO pour la requête de connexion.

    Attributes:
        email: Email de connexion.
        password: Mot de passe en clair.
    """

    email: str
    password: str


@dataclass(frozen=True)
class RegisterDTO:
    """
    DTO pour la requête d'inscription.

    Attributes:
        email: Email du nouvel utilisateur.
        password: Mot de passe en clair.
        nom: Nom de famille.
        prenom: Prénom.
        role: Rôle à assigner (optionnel, défaut: EMPLOYE).
    """

    email: str
    password: str
    nom: str
    prenom: str
    role: Optional[str] = None


@dataclass(frozen=True)
class TokenDTO:
    """
    DTO pour le token d'authentification.

    Attributes:
        access_token: Le JWT token.
        token_type: Type de token (bearer).
        expires_in: Durée de validité en secondes.
    """

    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


@dataclass(frozen=True)
class AuthResponseDTO:
    """
    DTO pour la réponse d'authentification complète.

    Attributes:
        user: Les informations utilisateur.
        token: Le token d'accès.
    """

    user: UserDTO
    token: TokenDTO
