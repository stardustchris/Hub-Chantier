"""Entité Comment - Représente un commentaire sur un post."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Comment:
    """
    Entité représentant un commentaire sur un post.

    Selon CDC Section 2 - FEED-05: Commentaires sur posts.

    Attributes:
        id: Identifiant unique (None si non persisté).
        post_id: ID du post commenté.
        author_id: ID de l'auteur du commentaire.
        content: Contenu du commentaire (supporte emojis FEED-10).
        created_at: Date de création (FEED-12).
        updated_at: Date de dernière modification.
        is_deleted: Indique si le commentaire a été supprimé.
    """

    post_id: int
    author_id: int
    content: str
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_deleted: bool = False

    def __post_init__(self) -> None:
        """Valide les données à la création."""
        if not self.content or not self.content.strip():
            raise ValueError("Le contenu du commentaire ne peut pas être vide")

        # Normalisation
        self.content = self.content.strip()

    def update_content(self, new_content: str) -> None:
        """Met à jour le contenu du commentaire."""
        if not new_content or not new_content.strip():
            raise ValueError("Le contenu du commentaire ne peut pas être vide")
        self.content = new_content.strip()
        self.updated_at = datetime.now()

    def delete(self) -> None:
        """Marque le commentaire comme supprimé."""
        self.is_deleted = True
        self.updated_at = datetime.now()

    @property
    def is_visible(self) -> bool:
        """Vérifie si le commentaire est visible."""
        return not self.is_deleted

    def __eq__(self, other: object) -> bool:
        """Égalité basée sur l'ID (entité)."""
        if not isinstance(other, Comment):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
