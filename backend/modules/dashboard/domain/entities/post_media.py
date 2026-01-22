"""Entité PostMedia - Représente un média attaché à un post."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class MediaType(str, Enum):
    """Type de média."""

    IMAGE = "image"

    def __str__(self) -> str:
        return self.value


# Constante selon CDC FEED-19
MAX_FILE_SIZE_MB = 2


@dataclass
class PostMedia:
    """
    Entité représentant un média (photo) attaché à un post.

    Selon CDC Section 2:
    - FEED-02: Ajout de photos (max 5 par post)
    - FEED-13: Chargement progressif des images
    - FEED-19: Compression auto (max 2 MB)

    Attributes:
        id: Identifiant unique (None si non persisté).
        post_id: ID du post associé.
        media_type: Type de média (image).
        file_url: URL du fichier stocké.
        thumbnail_url: URL de la miniature (FEED-13).
        original_filename: Nom original du fichier.
        file_size_bytes: Taille du fichier en octets.
        mime_type: Type MIME du fichier.
        width: Largeur en pixels.
        height: Hauteur en pixels.
        position: Position dans la galerie (0 = première).
        created_at: Date d'ajout.
    """

    post_id: int
    media_type: MediaType
    file_url: str
    id: Optional[int] = None
    thumbnail_url: Optional[str] = None
    original_filename: Optional[str] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    position: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Valide les données à la création."""
        if not self.file_url or not self.file_url.strip():
            raise ValueError("L'URL du fichier ne peut pas être vide")

    @property
    def file_size_mb(self) -> Optional[float]:
        """Retourne la taille du fichier en MB."""
        if self.file_size_bytes is None:
            return None
        return self.file_size_bytes / (1024 * 1024)

    @property
    def is_over_size_limit(self) -> bool:
        """Vérifie si le fichier dépasse la limite de taille (FEED-19)."""
        if self.file_size_bytes is None:
            return False
        return self.file_size_mb > MAX_FILE_SIZE_MB

    @property
    def aspect_ratio(self) -> Optional[float]:
        """Retourne le ratio largeur/hauteur."""
        if self.width is None or self.height is None or self.height == 0:
            return None
        return self.width / self.height

    def __eq__(self, other: object) -> bool:
        """Égalité basée sur l'ID (entité)."""
        if not isinstance(other, PostMedia):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
