"""Interface du repository pour les articles.

DEV-01: Bibliotheque d'articles - CRUD et recherche d'articles.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import Article
from ..value_objects import CategorieArticle


class ArticleRepository(ABC):
    """Interface abstraite pour la persistence des articles."""

    @abstractmethod
    def save(self, article: Article) -> Article:
        """Persiste un article (creation ou mise a jour).

        Args:
            article: L'article a persister.

        Returns:
            L'article avec son ID attribue.
        """
        pass

    @abstractmethod
    def find_by_id(self, article_id: int) -> Optional[Article]:
        """Recherche un article par son ID.

        Args:
            article_id: L'ID de l'article.

        Returns:
            L'article ou None si non trouve.
        """
        pass

    @abstractmethod
    def find_by_code(self, code: str) -> Optional[Article]:
        """Recherche un article par son code.

        Args:
            code: Le code de l'article.

        Returns:
            L'article ou None si non trouve.
        """
        pass

    @abstractmethod
    def find_all(
        self,
        categorie: Optional[CategorieArticle] = None,
        actif_only: bool = True,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Article]:
        """Liste les articles avec filtres optionnels.

        Args:
            categorie: Filtrer par categorie (optionnel).
            actif_only: Ne retourner que les articles actifs.
            search: Recherche textuelle sur code/libelle (optionnel).
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des articles.
        """
        pass

    @abstractmethod
    def count(
        self,
        categorie: Optional[CategorieArticle] = None,
        actif_only: bool = True,
    ) -> int:
        """Compte le nombre d'articles.

        Args:
            categorie: Filtrer par categorie (optionnel).
            actif_only: Ne compter que les articles actifs.

        Returns:
            Le nombre d'articles.
        """
        pass

    @abstractmethod
    def delete(self, article_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime un article (soft delete - H10).

        Args:
            article_id: L'ID de l'article a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprime, False si non trouve.
        """
        pass
