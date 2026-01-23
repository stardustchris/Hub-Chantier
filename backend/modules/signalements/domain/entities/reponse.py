"""Entité Reponse - Représente une réponse/commentaire sur un signalement."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Reponse:
    """
    Entité représentant une réponse à un signalement.

    Selon CDC SIG-07: Ajout de commentaires/réponses à un signalement.

    Attributes:
        id: Identifiant unique.
        signalement_id: Identifiant du signalement parent.
        contenu: Contenu de la réponse.
        auteur_id: ID de l'utilisateur auteur.
        photo_url: URL de la photo associée (optionnel).
        created_at: Date de création.
        updated_at: Date de dernière modification.
        est_resolution: Indique si cette réponse marque la résolution.
    """

    signalement_id: int
    contenu: str
    auteur_id: int
    id: Optional[int] = None
    photo_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    est_resolution: bool = False

    def __post_init__(self) -> None:
        """Valide les données à la création."""
        if not self.contenu or not self.contenu.strip():
            raise ValueError("Le contenu de la réponse ne peut pas être vide")

        self.contenu = self.contenu.strip()

    def modifier(self, nouveau_contenu: str) -> None:
        """
        Modifie le contenu de la réponse.

        Args:
            nouveau_contenu: Le nouveau contenu.

        Raises:
            ValueError: Si le contenu est vide.
        """
        if not nouveau_contenu or not nouveau_contenu.strip():
            raise ValueError("Le contenu de la réponse ne peut pas être vide")

        self.contenu = nouveau_contenu.strip()
        self.updated_at = datetime.now()

    def marquer_resolution(self) -> None:
        """Marque cette réponse comme réponse de résolution."""
        self.est_resolution = True
        self.updated_at = datetime.now()

    def peut_modifier(self, user_id: int, user_role: str) -> bool:
        """
        Vérifie si un utilisateur peut modifier cette réponse.

        Args:
            user_id: ID de l'utilisateur.
            user_role: Rôle de l'utilisateur.

        Returns:
            True si l'utilisateur peut modifier.
        """
        # Admin et Conducteur peuvent tout modifier
        if user_role in ("admin", "conducteur"):
            return True

        # Auteur peut modifier sa propre réponse
        return self.auteur_id == user_id

    def peut_supprimer(self, user_id: int, user_role: str) -> bool:
        """
        Vérifie si un utilisateur peut supprimer cette réponse.

        Args:
            user_id: ID de l'utilisateur.
            user_role: Rôle de l'utilisateur.

        Returns:
            True si l'utilisateur peut supprimer.
        """
        # Admin et Conducteur peuvent tout supprimer
        if user_role in ("admin", "conducteur"):
            return True

        # Chef de chantier peut supprimer
        if user_role == "chef_chantier":
            return True

        # Auteur peut supprimer sa propre réponse
        return self.auteur_id == user_id

    def __eq__(self, other: object) -> bool:
        """Égalité basée sur l'ID."""
        if not isinstance(other, Reponse):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
