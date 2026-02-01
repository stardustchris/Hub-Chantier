"""DTOs pour les utilisateurs."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from ...domain.entities import User


@dataclass(frozen=True)
class UserDTO:
    """
    Data Transfer Object pour un utilisateur.

    Utilisé pour transférer les données utilisateur entre les couches.
    Ne contient JAMAIS le mot de passe.

    Selon CDC Section 3 - Gestion des Utilisateurs (USR-01 à USR-13).
    """

    id: int
    email: str
    nom: str
    prenom: str
    nom_complet: str
    initiales: str
    role: str
    type_utilisateur: str
    is_active: bool
    couleur: str
    photo_profil: Optional[str]
    code_utilisateur: Optional[str]
    telephone: Optional[str]
    metiers: Optional[List[str]]
    taux_horaire: Optional[Decimal]
    contact_urgence_nom: Optional[str]
    contact_urgence_tel: Optional[str]
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
            nom_complet=user.nom_complet,
            initiales=user.initiales,
            role=user.role.value,
            type_utilisateur=user.type_utilisateur.value,
            is_active=user.is_active,
            couleur=str(user.couleur) if user.couleur else "#3498DB",
            photo_profil=user.photo_profil,
            code_utilisateur=user.code_utilisateur,
            telephone=user.telephone,
            metiers=user.metiers,
            taux_horaire=user.taux_horaire,
            contact_urgence_nom=user.contact_urgence_nom,
            contact_urgence_tel=user.contact_urgence_tel,
            created_at=user.created_at,
        )


@dataclass(frozen=True)
class UserListDTO:
    """
    DTO pour une liste paginée d'utilisateurs (USR-09).
    """

    users: List[UserDTO]
    total: int
    skip: int
    limit: int

    @property
    def has_next(self) -> bool:
        """Indique s'il y a une page suivante."""
        return self.skip + self.limit < self.total

    @property
    def has_previous(self) -> bool:
        """Indique s'il y a une page précédente."""
        return self.skip > 0


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
    DTO pour la requête d'inscription (self-registration).

    Le rôle est forcé à COMPAGNON côté serveur (sécurité).
    Seul un admin peut attribuer un rôle supérieur via PUT /users/{id}.
    """

    email: str
    password: str
    nom: str
    prenom: str
    type_utilisateur: Optional[str] = None
    telephone: Optional[str] = None
    metiers: Optional[List[str]] = None
    taux_horaire: Optional[Decimal] = None
    code_utilisateur: Optional[str] = None
    couleur: Optional[str] = None


@dataclass(frozen=True)
class UpdateUserDTO:
    """
    DTO pour la mise à jour d'un utilisateur.

    Tous les champs sont optionnels - seuls ceux fournis seront mis à jour.
    """

    nom: Optional[str] = None
    prenom: Optional[str] = None
    telephone: Optional[str] = None
    metiers: Optional[List[str]] = None
    taux_horaire: Optional[Decimal] = None
    couleur: Optional[str] = None
    photo_profil: Optional[str] = None
    contact_urgence_nom: Optional[str] = None
    contact_urgence_tel: Optional[str] = None
    role: Optional[str] = None
    type_utilisateur: Optional[str] = None
    code_utilisateur: Optional[str] = None


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
