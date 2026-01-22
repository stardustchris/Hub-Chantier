"""Entité Post - Représente une publication dans le fil d'actualités."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List

from ..value_objects import PostTargeting, PostStatus, TargetType


# Constantes selon CDC Section 2
MAX_PHOTOS_PER_POST = 5  # FEED-02
URGENT_PIN_DURATION_HOURS = 48  # FEED-08
ARCHIVE_AFTER_DAYS = 7  # FEED-20


@dataclass
class Post:
    """
    Entité représentant une publication dans le fil d'actualités.

    Selon CDC Section 2 - Tableau de Bord (FEED-01 à FEED-20).

    Attributes:
        id: Identifiant unique (None si non persisté).
        author_id: ID de l'auteur du post.
        content: Contenu textuel du post (FEED-01, FEED-10, FEED-11).
        targeting: Ciblage du post (FEED-03).
        status: Statut du post (published, pinned, archived, deleted).
        is_urgent: Marque le post comme urgent (FEED-08).
        pinned_until: Date/heure de fin d'épinglage (FEED-08).
        created_at: Date de création (FEED-12).
        updated_at: Date de dernière modification.
        archived_at: Date d'archivage (FEED-20).
    """

    author_id: int
    content: str
    targeting: PostTargeting = field(default_factory=PostTargeting.everyone)
    id: Optional[int] = None
    status: PostStatus = PostStatus.PUBLISHED
    is_urgent: bool = False
    pinned_until: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    archived_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Valide les données à la création."""
        if not self.content or not self.content.strip():
            raise ValueError("Le contenu du post ne peut pas être vide")

        # Normalisation du contenu
        self.content = self.content.strip()

    @property
    def is_pinned(self) -> bool:
        """Vérifie si le post est actuellement épinglé."""
        if self.status != PostStatus.PINNED:
            return False
        if self.pinned_until is None:
            return False
        return datetime.now() < self.pinned_until

    @property
    def is_archived(self) -> bool:
        """Vérifie si le post est archivé."""
        return self.status == PostStatus.ARCHIVED

    @property
    def is_visible(self) -> bool:
        """Vérifie si le post est visible dans le fil."""
        return self.status.is_visible()

    @property
    def should_archive(self) -> bool:
        """Vérifie si le post devrait être archivé (plus de 7 jours)."""
        if self.status != PostStatus.PUBLISHED:
            return False
        archive_threshold = self.created_at + timedelta(days=ARCHIVE_AFTER_DAYS)
        return datetime.now() > archive_threshold

    @property
    def target_display(self) -> str:
        """Retourne le texte d'affichage du ciblage (FEED-07)."""
        return self.targeting.get_display_text()

    def pin(self, duration_hours: int = URGENT_PIN_DURATION_HOURS) -> None:
        """
        Épingle le post en haut du fil (FEED-08).

        Args:
            duration_hours: Durée d'épinglage en heures (max 48h).
        """
        if duration_hours > URGENT_PIN_DURATION_HOURS:
            duration_hours = URGENT_PIN_DURATION_HOURS

        self.status = PostStatus.PINNED
        self.is_urgent = True
        self.pinned_until = datetime.now() + timedelta(hours=duration_hours)
        self.updated_at = datetime.now()

    def unpin(self) -> None:
        """Retire l'épinglage du post."""
        if self.status == PostStatus.PINNED:
            self.status = PostStatus.PUBLISHED
            self.is_urgent = False
            self.pinned_until = None
            self.updated_at = datetime.now()

    def archive(self) -> None:
        """Archive le post (FEED-20)."""
        self.status = PostStatus.ARCHIVED
        self.archived_at = datetime.now()
        self.updated_at = datetime.now()

    def delete(self) -> None:
        """Supprime le post par modération (FEED-16)."""
        self.status = PostStatus.DELETED
        self.updated_at = datetime.now()

    def update_content(self, new_content: str) -> None:
        """Met à jour le contenu du post."""
        if not new_content or not new_content.strip():
            raise ValueError("Le contenu du post ne peut pas être vide")
        self.content = new_content.strip()
        self.updated_at = datetime.now()

    def update_targeting(self, new_targeting: PostTargeting) -> None:
        """Met à jour le ciblage du post."""
        self.targeting = new_targeting
        self.updated_at = datetime.now()

    def is_visible_to_user(
        self, user_id: int, user_chantier_ids: Optional[List[int]] = None
    ) -> bool:
        """
        Vérifie si le post est visible pour un utilisateur donné (FEED-09).

        Args:
            user_id: ID de l'utilisateur.
            user_chantier_ids: IDs des chantiers de l'utilisateur.

        Returns:
            True si le post est visible pour l'utilisateur.
        """
        if not self.status.is_consultable():
            return False

        # L'auteur peut toujours voir son post
        if self.author_id == user_id:
            return True

        # Vérification selon le type de ciblage
        if self.targeting.target_type == TargetType.EVERYONE:
            return True

        if self.targeting.target_type == TargetType.SPECIFIC_PEOPLE:
            return self.targeting.includes_user(user_id)

        if self.targeting.target_type == TargetType.SPECIFIC_CHANTIERS:
            if user_chantier_ids:
                for chantier_id in user_chantier_ids:
                    if self.targeting.includes_chantier(chantier_id):
                        return True
            return False

        return False

    def __eq__(self, other: object) -> bool:
        """Égalité basée sur l'ID (entité)."""
        if not isinstance(other, Post):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
