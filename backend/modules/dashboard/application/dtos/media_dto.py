"""DTOs pour les médias."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ...domain.entities import PostMedia


@dataclass(frozen=True)
class MediaDTO:
    """
    Data Transfer Object pour un média.

    Selon CDC Section 2:
    - FEED-02: Ajout de photos
    - FEED-13: Chargement progressif des images
    """

    id: int
    post_id: int
    media_type: str
    file_url: str
    thumbnail_url: Optional[str]
    original_filename: Optional[str]
    file_size_bytes: Optional[int]
    width: Optional[int]
    height: Optional[int]
    position: int

    @classmethod
    def from_entity(cls, media: PostMedia) -> "MediaDTO":
        """
        Crée un DTO à partir d'une entité PostMedia.

        Args:
            media: L'entité PostMedia source.

        Returns:
            Le DTO correspondant.
        """
        return cls(
            id=media.id,
            post_id=media.post_id,
            media_type=media.media_type.value,
            file_url=media.file_url,
            thumbnail_url=media.thumbnail_url,
            original_filename=media.original_filename,
            file_size_bytes=media.file_size_bytes,
            width=media.width,
            height=media.height,
            position=media.position,
        )


@dataclass(frozen=True)
class CreateMediaDTO:
    """
    DTO pour l'ajout d'un média à un post.

    Selon CDC Section 2 - FEED-02, FEED-19.
    """

    post_id: int
    file_url: str
    thumbnail_url: Optional[str] = None
    original_filename: Optional[str] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    position: int = 0
