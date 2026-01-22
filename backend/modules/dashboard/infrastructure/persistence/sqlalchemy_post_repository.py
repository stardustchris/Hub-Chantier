"""Implémentation SQLAlchemy du PostRepository."""

from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from ...domain.entities import Post
from ...domain.repositories import PostRepository
from ...domain.value_objects import PostTargeting, PostStatus, TargetType
from .models import PostModel


# Constante pour archivage automatique
ARCHIVE_AFTER_DAYS = 7


class SQLAlchemyPostRepository(PostRepository):
    """
    Implémentation du PostRepository utilisant SQLAlchemy.

    Fait le mapping entre l'entité Post (Domain) et PostModel (Infrastructure).
    """

    def __init__(self, session: Session):
        self.session = session

    def save(self, post: Post) -> Post:
        """Persiste un post."""
        if post.id:
            # Update
            model = self.session.query(PostModel).filter(PostModel.id == post.id).first()
            if model:
                model.content = post.content
                model.status = post.status.value
                model.is_urgent = post.is_urgent
                model.pinned_until = post.pinned_until
                model.target_type = post.targeting.target_type.value
                model.target_chantier_ids = self._ids_to_string(post.targeting.chantier_ids)
                model.target_user_ids = self._ids_to_string(post.targeting.user_ids)
                model.updated_at = post.updated_at
                model.archived_at = post.archived_at
        else:
            # Create
            model = self._to_model(post)
            self.session.add(model)

        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, post_id: int) -> Optional[Post]:
        """Trouve un post par son ID."""
        model = self.session.query(PostModel).filter(PostModel.id == post_id).first()
        return self._to_entity(model) if model else None

    def find_feed(
        self,
        user_id: int,
        user_chantier_ids: Optional[List[int]] = None,
        limit: int = 20,
        offset: int = 0,
        include_archived: bool = False,
    ) -> List[Post]:
        """
        Récupère le fil d'actualités pour un utilisateur.

        Posts filtrés selon ciblage, triés par:
        1. Épinglés en premier
        2. Date décroissante
        """
        query = self.session.query(PostModel)

        # Filtrer par statut
        if include_archived:
            query = query.filter(
                PostModel.status.in_([
                    PostStatus.PUBLISHED.value,
                    PostStatus.PINNED.value,
                    PostStatus.ARCHIVED.value,
                ])
            )
        else:
            query = query.filter(
                PostModel.status.in_([
                    PostStatus.PUBLISHED.value,
                    PostStatus.PINNED.value,
                ])
            )

        # Filtrer par ciblage (FEED-09)
        # L'utilisateur voit:
        # - Posts ciblant "everyone"
        # - Posts dont il est l'auteur
        # - Posts ciblant ses chantiers
        # - Posts le ciblant directement
        targeting_conditions = [
            PostModel.target_type == TargetType.EVERYONE.value,
            PostModel.author_id == user_id,
        ]

        # Ciblage par utilisateur - SÉCURISÉ contre SQL injection
        # On vérifie que l'ID est bien un élément complet, pas une sous-chaîne
        targeting_conditions.append(
            and_(
                PostModel.target_type == TargetType.SPECIFIC_PEOPLE.value,
                self._id_in_csv_column(PostModel.target_user_ids, user_id),
            )
        )

        # Ciblage par chantier - SÉCURISÉ contre SQL injection
        if user_chantier_ids:
            for chantier_id in user_chantier_ids:
                targeting_conditions.append(
                    and_(
                        PostModel.target_type == TargetType.SPECIFIC_CHANTIERS.value,
                        self._id_in_csv_column(PostModel.target_chantier_ids, chantier_id),
                    )
                )

        query = query.filter(or_(*targeting_conditions))

        # Tri: épinglés d'abord, puis par date
        query = query.order_by(
            PostModel.status.desc(),  # PINNED > PUBLISHED
            PostModel.created_at.desc(),
        )

        # Pagination
        query = query.offset(offset).limit(limit)

        models = query.all()
        return [self._to_entity(m) for m in models]

    def find_by_author(
        self,
        author_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Post]:
        """Récupère les posts d'un auteur."""
        models = (
            self.session.query(PostModel)
            .filter(PostModel.author_id == author_id)
            .filter(PostModel.status != PostStatus.DELETED.value)
            .order_by(PostModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_status(self, status: PostStatus) -> List[Post]:
        """Récupère les posts par statut."""
        models = (
            self.session.query(PostModel)
            .filter(PostModel.status == status.value)
            .order_by(PostModel.created_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_posts_to_archive(self) -> List[Post]:
        """Récupère les posts qui devraient être archivés (plus de 7 jours)."""
        archive_threshold = datetime.now() - timedelta(days=ARCHIVE_AFTER_DAYS)
        models = (
            self.session.query(PostModel)
            .filter(PostModel.status == PostStatus.PUBLISHED.value)
            .filter(PostModel.created_at < archive_threshold)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_expired_pins(self) -> List[Post]:
        """Récupère les posts épinglés dont la durée a expiré."""
        now = datetime.now()
        models = (
            self.session.query(PostModel)
            .filter(PostModel.status == PostStatus.PINNED.value)
            .filter(PostModel.pinned_until < now)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def count_by_author(self, author_id: int) -> int:
        """Compte les posts d'un auteur."""
        return (
            self.session.query(PostModel)
            .filter(PostModel.author_id == author_id)
            .filter(PostModel.status != PostStatus.DELETED.value)
            .count()
        )

    def delete(self, post_id: int) -> bool:
        """Supprime physiquement un post."""
        model = self.session.query(PostModel).filter(PostModel.id == post_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def _to_entity(self, model: PostModel) -> Post:
        """Convertit un modèle en entité."""
        targeting = self._build_targeting(
            model.target_type,
            model.target_chantier_ids,
            model.target_user_ids,
        )

        return Post(
            id=model.id,
            author_id=model.author_id,
            content=model.content,
            targeting=targeting,
            status=PostStatus(model.status),
            is_urgent=model.is_urgent,
            pinned_until=model.pinned_until,
            created_at=model.created_at,
            updated_at=model.updated_at,
            archived_at=model.archived_at,
        )

    def _to_model(self, post: Post) -> PostModel:
        """Convertit une entité en modèle."""
        return PostModel(
            id=post.id,
            author_id=post.author_id,
            content=post.content,
            status=post.status.value,
            is_urgent=post.is_urgent,
            pinned_until=post.pinned_until,
            target_type=post.targeting.target_type.value,
            target_chantier_ids=self._ids_to_string(post.targeting.chantier_ids),
            target_user_ids=self._ids_to_string(post.targeting.user_ids),
            created_at=post.created_at,
            updated_at=post.updated_at,
            archived_at=post.archived_at,
        )

    def _build_targeting(
        self,
        target_type: str,
        chantier_ids_str: Optional[str],
        user_ids_str: Optional[str],
    ) -> PostTargeting:
        """Construit le ciblage à partir des données du modèle."""
        target_type_enum = TargetType(target_type)

        if target_type_enum == TargetType.EVERYONE:
            return PostTargeting.everyone()

        if target_type_enum == TargetType.SPECIFIC_CHANTIERS:
            ids = self._string_to_ids(chantier_ids_str)
            return PostTargeting.for_chantiers(ids)

        if target_type_enum == TargetType.SPECIFIC_PEOPLE:
            ids = self._string_to_ids(user_ids_str)
            return PostTargeting.for_users(ids)

        return PostTargeting.everyone()

    def _ids_to_string(self, ids: Optional[tuple]) -> Optional[str]:
        """Convertit un tuple d'IDs en string."""
        if not ids:
            return None
        return ",".join(str(i) for i in ids)

    def _string_to_ids(self, ids_str: Optional[str]) -> List[int]:
        """Convertit une string d'IDs en liste avec gestion d'erreur."""
        if not ids_str:
            return []
        result = []
        for i in ids_str.split(","):
            if i.strip():
                try:
                    result.append(int(i.strip()))
                except ValueError:
                    # Ignorer les valeurs corrompues
                    continue
        return result

    def _id_in_csv_column(self, column, target_id: int):
        """
        Vérifie qu'un ID est présent dans une colonne CSV de manière sécurisée.

        Évite les faux positifs comme id=1 correspondant à "10,11,12".
        Vérifie: exactement la valeur, ou ,valeur, ou valeur, au début, ou ,valeur à la fin.
        """
        from sqlalchemy import or_
        str_id = str(target_id)
        return or_(
            column == str_id,                           # Exactement la valeur
            column.like(f"{str_id},%"),                 # Au début: "1,..."
            column.like(f"%,{str_id}"),                 # À la fin: "...,1"
            column.like(f"%,{str_id},%"),               # Au milieu: "...,1,..."
        )
