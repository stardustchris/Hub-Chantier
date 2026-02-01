"""Use Cases pour la gestion des articles.

DEV-01: Bibliotheque d'articles et bordereaux.
"""

from datetime import datetime
from typing import Optional

from ...domain.entities.article import Article
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

        article = Article(
            designation=dto.designation,
            unite=dto.unite,
            prix_unitaire_ht=dto.prix_unitaire_ht,
            code=dto.code,
            categorie=dto.categorie,
            description=dto.description,
            taux_tva=dto.taux_tva,
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
            article.designation = dto.designation
        if dto.unite is not None:
            article.unite = dto.unite
        if dto.prix_unitaire_ht is not None:
            article.prix_unitaire_ht = dto.prix_unitaire_ht
        if dto.code is not None:
            article.code = dto.code
        if dto.categorie is not None:
            article.categorie = dto.categorie
        if dto.description is not None:
            article.description = dto.description
        if dto.taux_tva is not None:
            article.taux_tva = dto.taux_tva
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
        articles = self._article_repository.find_all(
            categorie=categorie,
            actif_seulement=actif_seulement,
            search=search,
            skip=offset,
            limit=limit,
        )
        total = self._article_repository.count(
            categorie=categorie,
            actif_seulement=actif_seulement,
            search=search,
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
