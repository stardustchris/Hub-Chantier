"""Use Cases pour la gestion des articles.

DEV-01: Bibliotheque d'articles et bordereaux.
"""

from datetime import datetime
from typing import Optional

from ...domain.entities.article import Article
from ...domain.value_objects import CategorieArticle, UniteArticle
from ...domain.repositories.article_repository import ArticleRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ...domain.entities.journal_devis import JournalDevis
from ..dtos.article_dtos import ArticleCreateDTO, ArticleUpdateDTO, ArticleDTO, ArticleListDTO


class ArticleNotFoundError(Exception):
    """Erreur levee quand un article n'est pas trouve."""

    def __init__(self, article_id: int):
        self.article_id = article_id
        super().__init__(f"Article {article_id} non trouve")


class ArticleCodeExistsError(Exception):
    """Erreur levee quand un code article existe deja."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(f"Un article avec le code '{code}' existe deja")


class CreateArticleUseCase:
    """Use case pour creer un article dans la bibliotheque.

    DEV-01: Bibliotheque d'articles.
    """

    def __init__(
        self,
        article_repository: ArticleRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._article_repository = article_repository
        self._journal_repository = journal_repository

    def execute(self, dto: ArticleCreateDTO, created_by: int) -> ArticleDTO:
        """Cree un nouvel article.

        Args:
            dto: Les donnees de l'article a creer.
            created_by: L'ID de l'utilisateur createur.

        Returns:
            Le DTO de l'article cree.

        Raises:
            ArticleCodeExistsError: Si le code existe deja.
        """
        # Verifier unicite du code
        if dto.code:
            existing = self._article_repository.find_by_code(dto.code)
            if existing:
                raise ArticleCodeExistsError(dto.code)

        # Convertir unite et categorie string en enum
        try:
            unite_enum = UniteArticle(dto.unite.lower()) if dto.unite else UniteArticle.U
        except ValueError:
            unite_enum = UniteArticle.U

        try:
            categorie_enum = CategorieArticle(dto.categorie.lower()) if dto.categorie else CategorieArticle.DIVERS
        except ValueError:
            categorie_enum = CategorieArticle.DIVERS

        article = Article(
            libelle=dto.designation,
            unite=unite_enum,
            prix_unitaire_ht=dto.prix_unitaire_ht,
            code=dto.code or f"ART-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            categorie=categorie_enum,
            description=dto.description,
            actif=dto.actif,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=created_by,
        )

        article = self._article_repository.save(article)

        return ArticleDTO.from_entity(article)


class UpdateArticleUseCase:
    """Use case pour mettre a jour un article."""

    def __init__(
        self,
        article_repository: ArticleRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._article_repository = article_repository
        self._journal_repository = journal_repository

    def execute(
        self, article_id: int, dto: ArticleUpdateDTO, updated_by: int
    ) -> ArticleDTO:
        """Met a jour un article.

        Args:
            article_id: L'ID de l'article.
            dto: Les donnees a mettre a jour.
            updated_by: L'ID de l'utilisateur.

        Returns:
            Le DTO de l'article mis a jour.

        Raises:
            ArticleNotFoundError: Si l'article n'existe pas.
            ArticleCodeExistsError: Si le nouveau code existe deja.
        """
        article = self._article_repository.find_by_id(article_id)
        if not article:
            raise ArticleNotFoundError(article_id)

        # Verifier unicite du code si modifie
        if dto.code is not None and dto.code != article.code:
            existing = self._article_repository.find_by_code(dto.code)
            if existing:
                raise ArticleCodeExistsError(dto.code)

        if dto.designation is not None:
            article.libelle = dto.designation
        if dto.unite is not None:
            try:
                article.unite = UniteArticle(dto.unite.lower())
            except ValueError:
                article.unite = UniteArticle.U
        if dto.prix_unitaire_ht is not None:
            article.prix_unitaire_ht = dto.prix_unitaire_ht
        if dto.code is not None:
            article.code = dto.code
        if dto.categorie is not None:
            try:
                article.categorie = CategorieArticle(dto.categorie.lower())
            except ValueError:
                article.categorie = CategorieArticle.DIVERS
        if dto.description is not None:
            article.description = dto.description
        if dto.actif is not None:
            article.actif = dto.actif

        article.updated_at = datetime.utcnow()

        article = self._article_repository.save(article)

        return ArticleDTO.from_entity(article)


class GetArticleUseCase:
    """Use case pour recuperer un article."""

    def __init__(self, article_repository: ArticleRepository):
        self._article_repository = article_repository

    def execute(self, article_id: int) -> ArticleDTO:
        """Recupere un article par son ID.

        Raises:
            ArticleNotFoundError: Si l'article n'existe pas.
        """
        article = self._article_repository.find_by_id(article_id)
        if not article:
            raise ArticleNotFoundError(article_id)
        return ArticleDTO.from_entity(article)


class ListArticlesUseCase:
    """Use case pour lister les articles avec filtres."""

    def __init__(self, article_repository: ArticleRepository):
        self._article_repository = article_repository

    def execute(
        self,
        categorie: Optional[str] = None,
        actif_seulement: bool = True,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> ArticleListDTO:
        """Liste les articles avec pagination et filtres."""
        # Convertir categorie string en enum si fournie
        categorie_enum = None
        if categorie:
            try:
                categorie_enum = CategorieArticle(categorie.lower())
            except ValueError:
                categorie_enum = None

        articles = self._article_repository.find_all(
            categorie=categorie_enum,
            actif_only=actif_seulement,
            search=search,
            offset=offset,
            limit=limit,
        )
        total = self._article_repository.count(
            categorie=categorie_enum,
            actif_only=actif_seulement,
        )
        return ArticleListDTO(
            items=[ArticleDTO.from_entity(a) for a in articles],
            total=total,
            limit=limit,
            offset=offset,
        )


class DeleteArticleUseCase:
    """Use case pour supprimer un article (soft delete)."""

    def __init__(
        self,
        article_repository: ArticleRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._article_repository = article_repository
        self._journal_repository = journal_repository

    def execute(self, article_id: int, deleted_by: int) -> None:
        """Supprime un article (soft delete).

        Raises:
            ArticleNotFoundError: Si l'article n'existe pas.
        """
        article = self._article_repository.find_by_id(article_id)
        if not article:
            raise ArticleNotFoundError(article_id)

        self._article_repository.delete(article_id)
