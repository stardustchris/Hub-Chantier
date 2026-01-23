"""Entité AutorisationDocument - Autorisations nominatives (GED-05, GED-10)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class TypeAutorisation(Enum):
    """Types d'autorisation possibles."""

    LECTURE = "lecture"
    ECRITURE = "ecriture"  # Inclut lecture + modification
    ADMIN = "admin"  # Inclut tout + suppression


@dataclass
class AutorisationDocument:
    """
    Entité représentant une autorisation nominative sur un dossier ou document.

    Selon CDC GED-05: Autorisations spécifiques - Permissions nominatives additionnelles.
    Selon CDC GED-10: Sélection droits à l'upload - Rôles + Utilisateurs nominatifs.

    Attributes:
        id: Identifiant unique.
        user_id: Utilisateur autorisé.
        type_autorisation: Type d'autorisation (lecture, écriture, admin).
        dossier_id: Dossier concerné (optionnel si document).
        document_id: Document concerné (optionnel si dossier).
        accorde_par: Utilisateur ayant accordé l'autorisation.
        created_at: Date de création.
        expire_at: Date d'expiration (optionnel).
    """

    user_id: int
    type_autorisation: TypeAutorisation
    accorde_par: int
    id: Optional[int] = None
    dossier_id: Optional[int] = None
    document_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    expire_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Valide les données à la création."""
        if self.dossier_id is None and self.document_id is None:
            raise ValueError("L'autorisation doit concerner un dossier ou un document")

        if self.dossier_id is not None and self.document_id is not None:
            raise ValueError("L'autorisation ne peut concerner qu'un seul élément")

    @property
    def est_valide(self) -> bool:
        """Vérifie si l'autorisation est toujours valide."""
        if self.expire_at is None:
            return True
        return datetime.now() < self.expire_at

    @property
    def cible(self) -> str:
        """Retourne le type de cible (dossier ou document)."""
        return "dossier" if self.dossier_id else "document"

    @property
    def cible_id(self) -> int:
        """Retourne l'ID de la cible."""
        return self.dossier_id if self.dossier_id else self.document_id  # type: ignore

    def peut_lire(self) -> bool:
        """Vérifie si l'autorisation permet la lecture."""
        return self.est_valide and self.type_autorisation in [
            TypeAutorisation.LECTURE,
            TypeAutorisation.ECRITURE,
            TypeAutorisation.ADMIN,
        ]

    def peut_ecrire(self) -> bool:
        """Vérifie si l'autorisation permet l'écriture."""
        return self.est_valide and self.type_autorisation in [
            TypeAutorisation.ECRITURE,
            TypeAutorisation.ADMIN,
        ]

    def peut_supprimer(self) -> bool:
        """Vérifie si l'autorisation permet la suppression."""
        return self.est_valide and self.type_autorisation == TypeAutorisation.ADMIN

    def revoquer(self) -> None:
        """Révoque l'autorisation en la faisant expirer immédiatement."""
        self.expire_at = datetime.now()

    @classmethod
    def creer_pour_dossier(
        cls,
        dossier_id: int,
        user_id: int,
        type_autorisation: TypeAutorisation,
        accorde_par: int,
        expire_at: Optional[datetime] = None,
    ) -> "AutorisationDocument":
        """
        Crée une autorisation pour un dossier.

        Args:
            dossier_id: ID du dossier.
            user_id: ID de l'utilisateur autorisé.
            type_autorisation: Type d'autorisation.
            accorde_par: ID de l'utilisateur accordant l'autorisation.
            expire_at: Date d'expiration optionnelle.

        Returns:
            L'autorisation créée.
        """
        return cls(
            dossier_id=dossier_id,
            user_id=user_id,
            type_autorisation=type_autorisation,
            accorde_par=accorde_par,
            expire_at=expire_at,
        )

    @classmethod
    def creer_pour_document(
        cls,
        document_id: int,
        user_id: int,
        type_autorisation: TypeAutorisation,
        accorde_par: int,
        expire_at: Optional[datetime] = None,
    ) -> "AutorisationDocument":
        """
        Crée une autorisation pour un document.

        Args:
            document_id: ID du document.
            user_id: ID de l'utilisateur autorisé.
            type_autorisation: Type d'autorisation.
            accorde_par: ID de l'utilisateur accordant l'autorisation.
            expire_at: Date d'expiration optionnelle.

        Returns:
            L'autorisation créée.
        """
        return cls(
            document_id=document_id,
            user_id=user_id,
            type_autorisation=type_autorisation,
            accorde_par=accorde_par,
            expire_at=expire_at,
        )

    def __eq__(self, other: object) -> bool:
        """Égalité basée sur l'ID."""
        if not isinstance(other, AutorisationDocument):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
