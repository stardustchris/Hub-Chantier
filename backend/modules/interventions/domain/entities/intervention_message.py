"""Entite InterventionMessage.

INT-11: Fil d'actualite - Timeline actions, photos, commentaires
INT-12: Chat intervention - Discussion instantanee equipe
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TypeMessage(str, Enum):
    """Types de messages dans le fil d'activite."""

    COMMENTAIRE = "commentaire"
    PHOTO = "photo"
    ACTION = "action"
    SYSTEME = "systeme"

    @property
    def label(self) -> str:
        """Retourne le libelle affichable."""
        labels = {
            TypeMessage.COMMENTAIRE: "Commentaire",
            TypeMessage.PHOTO: "Photo",
            TypeMessage.ACTION: "Action",
            TypeMessage.SYSTEME: "Systeme",
        }
        return labels[self]


@dataclass
class InterventionMessage:
    """Represente un message dans le fil d'activite de l'intervention.

    Les messages peuvent etre:
    - Des commentaires texte (INT-12: Chat)
    - Des photos avec description (INT-11: Photos)
    - Des actions (demarrage, fin, signature)
    - Des messages systeme (changements de statut)

    Attributes:
        id: Identifiant unique.
        intervention_id: ID de l'intervention.
        auteur_id: ID de l'utilisateur auteur.
        type_message: Type de message.
        contenu: Contenu textuel du message.
        photos_urls: Liste des URLs des photos jointes.
        metadata: Donnees supplementaires en JSON.
        inclure_rapport: Si ce message doit etre inclus dans le rapport PDF.
        created_at: Date de creation.
    """

    intervention_id: int
    auteur_id: int
    type_message: TypeMessage
    contenu: str

    id: Optional[int] = None
    photos_urls: List[str] = field(default_factory=list)
    metadata: Optional[dict] = None
    inclure_rapport: bool = True  # INT-15: Selection posts pour rapport
    created_at: datetime = field(default_factory=datetime.utcnow)
    # Soft delete
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if self.intervention_id <= 0:
            raise ValueError("L'ID de l'intervention doit etre positif")
        # auteur_id peut etre 0 pour les messages systeme
        if self.auteur_id < 0:
            raise ValueError("L'ID de l'auteur ne peut pas etre negatif")
        if self.auteur_id == 0 and self.type_message != TypeMessage.SYSTEME:
            raise ValueError("L'ID de l'auteur doit etre positif pour les messages non-systeme")
        if not self.contenu or not self.contenu.strip():
            raise ValueError("Le contenu ne peut pas etre vide")

        self.contenu = self.contenu.strip()

    @property
    def est_supprime(self) -> bool:
        """Verifie si le message a ete supprime (soft delete)."""
        return self.deleted_at is not None

    @property
    def a_photos(self) -> bool:
        """Verifie si le message contient des photos."""
        return len(self.photos_urls) > 0

    @property
    def est_commentaire(self) -> bool:
        """Verifie si c'est un commentaire."""
        return self.type_message == TypeMessage.COMMENTAIRE

    @property
    def est_photo(self) -> bool:
        """Verifie si c'est une photo."""
        return self.type_message == TypeMessage.PHOTO

    def ajouter_photo(self, url: str) -> None:
        """Ajoute une photo au message."""
        if url and url.strip():
            self.photos_urls.append(url.strip())

    def exclure_du_rapport(self) -> None:
        """Exclut ce message du rapport PDF."""
        self.inclure_rapport = False

    def inclure_dans_rapport(self) -> None:
        """Inclut ce message dans le rapport PDF."""
        self.inclure_rapport = True

    def supprimer(self, deleted_by: int) -> None:
        """Marque le message comme supprime (soft delete)."""
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    @classmethod
    def creer_commentaire(
        cls,
        intervention_id: int,
        auteur_id: int,
        contenu: str,
    ) -> "InterventionMessage":
        """Factory pour creer un message de type commentaire."""
        return cls(
            intervention_id=intervention_id,
            auteur_id=auteur_id,
            type_message=TypeMessage.COMMENTAIRE,
            contenu=contenu,
        )

    @classmethod
    def creer_photo(
        cls,
        intervention_id: int,
        auteur_id: int,
        description: str,
        photos_urls: List[str],
    ) -> "InterventionMessage":
        """Factory pour creer un message de type photo."""
        return cls(
            intervention_id=intervention_id,
            auteur_id=auteur_id,
            type_message=TypeMessage.PHOTO,
            contenu=description,
            photos_urls=photos_urls,
        )

    @classmethod
    def creer_action(
        cls,
        intervention_id: int,
        auteur_id: int,
        action: str,
        metadata: Optional[dict] = None,
    ) -> "InterventionMessage":
        """Factory pour creer un message de type action."""
        return cls(
            intervention_id=intervention_id,
            auteur_id=auteur_id,
            type_message=TypeMessage.ACTION,
            contenu=action,
            metadata=metadata,
            inclure_rapport=False,
        )

    @classmethod
    def creer_systeme(
        cls,
        intervention_id: int,
        message: str,
    ) -> "InterventionMessage":
        """Factory pour creer un message systeme."""
        return cls(
            intervention_id=intervention_id,
            auteur_id=0,  # Systeme n'a pas d'auteur
            type_message=TypeMessage.SYSTEME,
            contenu=message,
            inclure_rapport=False,
        )

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID."""
        if not isinstance(other, InterventionMessage):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))

    def __str__(self) -> str:
        """Representation textuelle."""
        return f"Message {self.type_message.label}: {self.contenu[:50]}..."

    def __repr__(self) -> str:
        """Representation technique."""
        return (
            f"InterventionMessage(id={self.id}, intervention_id={self.intervention_id}, "
            f"type={self.type_message.value})"
        )
