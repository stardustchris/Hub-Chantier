"""Implementation SQLAlchemy du repository Article.

DEV-01: Bibliotheque d'articles - CRUD et recherche d'articles.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from ...domain.entities import Article
from ...domain.repositories.article_repository import ArticleRepository
from ...domain.value_objects import CategorieArticle, UniteArticle
from .models import ArticleDevisModel


class SQLAlchemyArticleRepository(ArticleRepository):
    """Implementation SQLAlchemy du repository Article."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: ArticleDevisModel) -> Article:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite Article correspondante.
        """
        return Article(
            id=model.id,
            code=model.code or "",
            libelle=model.designation,
            description=model.description,
            unite=UniteArticle(model.unite),
            prix_unitaire_ht=Decimal(str(model.prix_unitaire_ht)),
            categorie=(
                CategorieArticle(model.categorie)
                if model.categorie is not None
                else CategorieArticle.DIVERS
            ),
            composants_json=model.composants_json,
            actif=model.actif,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )

    def save(self, article: Article) -> Article:
        """Persiste un article (creation ou mise a jour).

        Args:
            article: L'article a persister.

        Returns:
            L'article avec son ID attribue.
        """
        if article.id:
            model = (
                self._session.query(ArticleDevisModel)
                .filter(ArticleDevisModel.id == article.id)
                .first()
            )
            if model:
                model.code = article.code
                model.designation = article.libelle
                model.description = article.description
                model.unite = article.unite.value
                model.prix_unitaire_ht = article.prix_unitaire_ht
                model.categorie = article.categorie.value
                model.composants_json = article.composants_json
                model.actif = article.actif
                model.updated_at = datetime.utcnow()
        else:
            model = ArticleDevisModel(
                code=article.code,
                designation=article.libelle,
                description=article.description,
                unite=article.unite.value,
                prix_unitaire_ht=article.prix_unitaire_ht,
                categorie=article.categorie.value,
                composants_json=article.composants_json,
                taux_tva=Decimal("20"),
                actif=article.actif,
                created_at=article.created_at or datetime.utcnow(),
                created_by=article.created_by,
            )
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def find_by_id(self, article_id: int) -> Optional[Article]:
        """Recherche un article par son ID (exclut les supprimes).

        Args:
            article_id: L'ID de l'article.

        Returns:
            L'article ou None si non trouve.
        """
        model = (
            self._session.query(ArticleDevisModel)
            .filter(ArticleDevisModel.id == article_id)
            .filter(ArticleDevisModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_code(self, code: str) -> Optional[Article]:
        """Recherche un article par son code (exclut les supprimes).

        Args:
            code: Le code de l'article.

        Returns:
            L'article ou None si non trouve.
        """
        model = (
            self._session.query(ArticleDevisModel)
            .filter(ArticleDevisModel.code == code)
            .filter(ArticleDevisModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_all(
        self,
        categorie: Optional[CategorieArticle] = None,
        actif_only: bool = True,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Article]:
        """Liste les articles avec filtres optionnels (exclut les supprimes).

        Args:
            categorie: Filtrer par categorie (optionnel).
            actif_only: Ne retourner que les articles actifs.
            search: Recherche textuelle sur code/libelle (optionnel).
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des articles.
        """
        query = self._session.query(ArticleDevisModel).filter(
            ArticleDevisModel.deleted_at.is_(None)
        )

        if categorie is not None:
            query = query.filter(
                ArticleDevisModel.categorie == categorie.value
            )

        if actif_only:
            query = query.filter(ArticleDevisModel.actif.is_(True))

        if search is not None:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    ArticleDevisModel.code.ilike(search_pattern),
                    ArticleDevisModel.designation.ilike(search_pattern),
                )
            )

        query = query.order_by(ArticleDevisModel.designation)
        query = query.offset(offset).limit(limit)

        return [self._to_entity(model) for model in query.all()]

    def count(
        self,
        categorie: Optional[CategorieArticle] = None,
        actif_only: bool = True,
    ) -> int:
        """Compte le nombre d'articles (exclut les supprimes).

        Args:
            categorie: Filtrer par categorie (optionnel).
            actif_only: Ne compter que les articles actifs.

        Returns:
            Le nombre d'articles.
        """
        query = self._session.query(ArticleDevisModel).filter(
            ArticleDevisModel.deleted_at.is_(None)
        )

        if categorie is not None:
            query = query.filter(
                ArticleDevisModel.categorie == categorie.value
            )

        if actif_only:
            query = query.filter(ArticleDevisModel.actif.is_(True))

        return query.count()

    def delete(self, article_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime un article (soft delete - H10).

        Args:
            article_id: L'ID de l'article a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprime, False si non trouve.
        """
        model = (
            self._session.query(ArticleDevisModel)
            .filter(ArticleDevisModel.id == article_id)
            .filter(ArticleDevisModel.deleted_at.is_(None))
            .first()
        )
        if not model:
            return False

        model.deleted_at = datetime.utcnow()
        model.deleted_by = deleted_by
        self._session.flush()
        return True
