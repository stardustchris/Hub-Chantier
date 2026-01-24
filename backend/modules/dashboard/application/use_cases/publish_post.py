"""Use Case PublishPost - Publication d'un nouveau post."""

from typing import Callable, Optional

from ...domain.entities import Post
from ...domain.repositories import PostRepository, PostMediaRepository
from ...domain.value_objects import PostTargeting, TargetType
from ...domain.events import PostPublishedEvent
from ..dtos import CreatePostDTO, PostDTO


class PostContentEmptyError(Exception):
    """Exception levée quand le contenu du post est vide."""

    def __init__(self):
        self.message = "Le contenu du post ne peut pas être vide"
        super().__init__(self.message)


class MaxPhotosExceededError(Exception):
    """Exception levée quand le nombre max de photos est dépassé."""

    def __init__(self, max_photos: int = 5):
        self.message = f"Un post ne peut pas contenir plus de {max_photos} photos"
        super().__init__(self.message)


class PublishPostUseCase:
    """
    Cas d'utilisation : Publication d'un nouveau post.

    Selon CDC Section 2:
    - FEED-01: Publication de messages texte
    - FEED-02: Ajout de photos (max 5)
    - FEED-03: Ciblage des destinataires
    - FEED-08: Posts urgents (épinglés 48h)

    Attributes:
        post_repo: Repository pour accéder aux posts.
        media_repo: Repository pour accéder aux médias (optionnel).
        event_publisher: Fonction pour publier les events.
    """

    MAX_PHOTOS = 5

    def __init__(
        self,
        post_repo: PostRepository,
        media_repo: Optional[PostMediaRepository] = None,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            post_repo: Repository posts (interface).
            media_repo: Repository médias (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.post_repo = post_repo
        self.media_repo = media_repo
        self.event_publisher = event_publisher

    def execute(self, dto: CreatePostDTO, author_id: int) -> PostDTO:
        """
        Exécute la publication d'un post.

        Args:
            dto: Les données du post.
            author_id: ID de l'auteur.

        Returns:
            PostDTO du post créé.

        Raises:
            PostContentEmptyError: Si le contenu est vide.
            ValueError: Si les données de ciblage sont invalides.
        """
        # Valider le contenu
        if not dto.content or not dto.content.strip():
            raise PostContentEmptyError()

        # Construire le ciblage
        targeting = self._build_targeting(dto)

        # Créer le post
        post = Post(
            author_id=author_id,
            content=dto.content,
            targeting=targeting,
        )

        # Épingler si urgent (FEED-08)
        if dto.is_urgent:
            post.pin()

        # Sauvegarder
        post = self.post_repo.save(post)

        # Publier l'event
        if self.event_publisher:
            event = PostPublishedEvent(
                post_id=post.id,
                author_id=author_id,
                target_type=targeting.target_type.value,
                chantier_ids=targeting.chantier_ids,
                user_ids=targeting.user_ids,
                is_urgent=dto.is_urgent,
            )
            self.event_publisher(event)

        # Retourner le DTO
        return PostDTO.from_entity(post)

    def _build_targeting(self, dto: CreatePostDTO) -> PostTargeting:
        """Construit le ciblage à partir du DTO."""
        target_type = TargetType(dto.target_type)

        if target_type == TargetType.EVERYONE:
            return PostTargeting.everyone()

        elif target_type == TargetType.SPECIFIC_CHANTIERS:
            if not dto.chantier_ids:
                raise ValueError(
                    "Au moins un chantier doit être spécifié pour le ciblage SPECIFIC_CHANTIERS"
                )
            return PostTargeting.for_chantiers(dto.chantier_ids)

        elif target_type == TargetType.SPECIFIC_PEOPLE:
            if not dto.user_ids:
                raise ValueError(
                    "Au moins un utilisateur doit être spécifié pour le ciblage SPECIFIC_PEOPLE"
                )
            return PostTargeting.for_users(dto.user_ids)

        raise ValueError(f"Type de ciblage inconnu: {dto.target_type}")
