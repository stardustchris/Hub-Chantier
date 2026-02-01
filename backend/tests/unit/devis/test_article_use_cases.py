"""Tests unitaires pour les Use Cases de gestion des articles.

DEV-01: Bibliotheque d'articles et bordereaux.
Couche Application - article_use_cases.py
"""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.devis.domain.entities.article import Article
from modules.devis.domain.value_objects.categorie_article import CategorieArticle
from modules.devis.domain.value_objects.unite_article import UniteArticle
from modules.devis.domain.repositories.article_repository import ArticleRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.article_use_cases import (
    CreateArticleUseCase,
    UpdateArticleUseCase,
    GetArticleUseCase,
    ListArticlesUseCase,
    DeleteArticleUseCase,
    ArticleNotFoundError,
    ArticleCodeExistsError,
)
from modules.devis.application.dtos.article_dtos import (
    ArticleCreateDTO,
    ArticleUpdateDTO,
    ArticleDTO,
    ArticleListDTO,
)


def _make_article(**kwargs):
    """Cree un article valide."""
    defaults = {
        "id": 1,
        "code": "ART-001",
        "libelle": "Beton C25/30",
        "unite": UniteArticle.M3,
        "prix_unitaire_ht": Decimal("95.50"),
        "categorie": CategorieArticle.GROS_OEUVRE,
        "actif": True,
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
        "created_by": 1,
    }
    defaults.update(kwargs)
    return Article(**defaults)


class TestCreateArticleUseCase:
    """Tests pour la creation d'articles."""

    def setup_method(self):
        self.mock_article_repo = Mock(spec=ArticleRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = CreateArticleUseCase(
            article_repository=self.mock_article_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_create_article_success(self):
        """Test: creation reussie."""
        self.mock_article_repo.find_by_code.return_value = None
        saved_article = _make_article()
        self.mock_article_repo.save.return_value = saved_article

        dto = ArticleCreateDTO(
            designation="Beton C25/30",
            code="ART-001",
            unite="m3",
            prix_unitaire_ht=Decimal("95.50"),
            categorie="gros_oeuvre",
        )
        result = self.use_case.execute(dto, created_by=1)

        assert isinstance(result, ArticleDTO)
        assert result.designation == "Beton C25/30"
        self.mock_article_repo.save.assert_called_once()

    def test_create_article_code_exists(self):
        """Test: erreur si code deja utilise."""
        existing = _make_article()
        self.mock_article_repo.find_by_code.return_value = existing

        dto = ArticleCreateDTO(designation="Nouveau", code="ART-001")
        with pytest.raises(ArticleCodeExistsError) as exc_info:
            self.use_case.execute(dto, created_by=1)
        assert exc_info.value.code == "ART-001"

    def test_create_article_sans_code(self):
        """Test: code auto-genere si non fourni."""
        self.mock_article_repo.save.return_value = _make_article(code="ART-20260115")

        dto = ArticleCreateDTO(designation="Article sans code")
        result = self.use_case.execute(dto, created_by=1)

        # Pas de verification find_by_code car code est None/vide
        assert isinstance(result, ArticleDTO)

    def test_create_article_unite_invalide_fallback(self):
        """Test: unite invalide tombe sur U par defaut."""
        self.mock_article_repo.find_by_code.return_value = None
        self.mock_article_repo.save.return_value = _make_article(unite=UniteArticle.U)

        dto = ArticleCreateDTO(
            designation="Test",
            code="ART-002",
            unite="invalid",
        )
        self.use_case.execute(dto, created_by=1)

        article_saved = self.mock_article_repo.save.call_args[0][0]
        assert article_saved.unite == UniteArticle.U

    def test_create_article_categorie_invalide_fallback(self):
        """Test: categorie invalide tombe sur DIVERS par defaut."""
        self.mock_article_repo.find_by_code.return_value = None
        self.mock_article_repo.save.return_value = _make_article(categorie=CategorieArticle.DIVERS)

        dto = ArticleCreateDTO(
            designation="Test",
            code="ART-003",
            categorie="invalid_category",
        )
        self.use_case.execute(dto, created_by=1)

        article_saved = self.mock_article_repo.save.call_args[0][0]
        assert article_saved.categorie == CategorieArticle.DIVERS


class TestUpdateArticleUseCase:
    """Tests pour la mise a jour d'articles."""

    def setup_method(self):
        self.mock_article_repo = Mock(spec=ArticleRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = UpdateArticleUseCase(
            article_repository=self.mock_article_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_update_article_success(self):
        """Test: mise a jour reussie."""
        article = _make_article()
        self.mock_article_repo.find_by_id.return_value = article
        self.mock_article_repo.save.return_value = article

        dto = ArticleUpdateDTO(designation="Nouveau libelle")
        result = self.use_case.execute(article_id=1, dto=dto, updated_by=1)

        assert isinstance(result, ArticleDTO)
        assert article.libelle == "Nouveau libelle"

    def test_update_article_not_found(self):
        """Test: erreur si article non trouve."""
        self.mock_article_repo.find_by_id.return_value = None

        dto = ArticleUpdateDTO(designation="Nouveau")
        with pytest.raises(ArticleNotFoundError) as exc_info:
            self.use_case.execute(article_id=999, dto=dto, updated_by=1)
        assert exc_info.value.article_id == 999

    def test_update_article_code_exists(self):
        """Test: erreur si nouveau code deja utilise."""
        article = _make_article(code="ART-001")
        existing = _make_article(id=2, code="ART-002")
        self.mock_article_repo.find_by_id.return_value = article
        self.mock_article_repo.find_by_code.return_value = existing

        dto = ArticleUpdateDTO(code="ART-002")
        with pytest.raises(ArticleCodeExistsError):
            self.use_case.execute(article_id=1, dto=dto, updated_by=1)

    def test_update_article_same_code_no_error(self):
        """Test: pas d'erreur si le code ne change pas."""
        article = _make_article(code="ART-001")
        self.mock_article_repo.find_by_id.return_value = article
        self.mock_article_repo.save.return_value = article

        dto = ArticleUpdateDTO(code="ART-001")
        result = self.use_case.execute(article_id=1, dto=dto, updated_by=1)

        assert isinstance(result, ArticleDTO)

    def test_update_article_multiple_fields(self):
        """Test: mise a jour de plusieurs champs."""
        article = _make_article()
        self.mock_article_repo.find_by_id.return_value = article
        self.mock_article_repo.save.return_value = article

        dto = ArticleUpdateDTO(
            designation="Nouveau libelle",
            prix_unitaire_ht=Decimal("120"),
            actif=False,
        )
        self.use_case.execute(article_id=1, dto=dto, updated_by=1)

        assert article.libelle == "Nouveau libelle"
        assert article.prix_unitaire_ht == Decimal("120")
        assert article.actif is False


class TestGetArticleUseCase:
    """Tests pour la recuperation d'un article."""

    def setup_method(self):
        self.mock_article_repo = Mock(spec=ArticleRepository)
        self.use_case = GetArticleUseCase(
            article_repository=self.mock_article_repo,
        )

    def test_get_article_success(self):
        """Test: recuperation reussie."""
        article = _make_article()
        self.mock_article_repo.find_by_id.return_value = article

        result = self.use_case.execute(article_id=1)

        assert isinstance(result, ArticleDTO)
        assert result.id == 1

    def test_get_article_not_found(self):
        """Test: erreur si article non trouve."""
        self.mock_article_repo.find_by_id.return_value = None

        with pytest.raises(ArticleNotFoundError):
            self.use_case.execute(article_id=999)


class TestListArticlesUseCase:
    """Tests pour le listage des articles."""

    def setup_method(self):
        self.mock_article_repo = Mock(spec=ArticleRepository)
        self.use_case = ListArticlesUseCase(
            article_repository=self.mock_article_repo,
        )

    def test_list_articles_success(self):
        """Test: listage avec pagination."""
        articles = [_make_article(id=i, code=f"ART-{i:03d}") for i in range(1, 4)]
        self.mock_article_repo.find_all.return_value = articles
        self.mock_article_repo.count.return_value = 3

        result = self.use_case.execute()

        assert isinstance(result, ArticleListDTO)
        assert len(result.items) == 3
        assert result.total == 3

    def test_list_articles_empty(self):
        """Test: listage vide."""
        self.mock_article_repo.find_all.return_value = []
        self.mock_article_repo.count.return_value = 0

        result = self.use_case.execute()

        assert len(result.items) == 0

    def test_list_articles_by_categorie(self):
        """Test: filtrage par categorie."""
        self.mock_article_repo.find_all.return_value = []
        self.mock_article_repo.count.return_value = 0

        result = self.use_case.execute(categorie="gros_oeuvre")

        call_kwargs = self.mock_article_repo.find_all.call_args[1]
        assert call_kwargs["categorie"] == CategorieArticle.GROS_OEUVRE

    def test_list_articles_categorie_invalide(self):
        """Test: categorie invalide est ignoree."""
        self.mock_article_repo.find_all.return_value = []
        self.mock_article_repo.count.return_value = 0

        result = self.use_case.execute(categorie="invalid_cat")

        call_kwargs = self.mock_article_repo.find_all.call_args[1]
        assert call_kwargs["categorie"] is None

    def test_list_articles_actif_seulement(self):
        """Test: filtrage articles actifs seulement."""
        self.mock_article_repo.find_all.return_value = []
        self.mock_article_repo.count.return_value = 0

        result = self.use_case.execute(actif_seulement=True)

        call_kwargs = self.mock_article_repo.find_all.call_args[1]
        assert call_kwargs["actif_only"] is True

    def test_list_articles_avec_recherche(self):
        """Test: recherche textuelle."""
        self.mock_article_repo.find_all.return_value = []
        self.mock_article_repo.count.return_value = 0

        result = self.use_case.execute(search="beton")

        call_kwargs = self.mock_article_repo.find_all.call_args[1]
        assert call_kwargs["search"] == "beton"

    def test_list_articles_pagination(self):
        """Test: pagination personnalisee."""
        self.mock_article_repo.find_all.return_value = []
        self.mock_article_repo.count.return_value = 50

        result = self.use_case.execute(limit=10, offset=20)

        assert result.limit == 10
        assert result.offset == 20


class TestDeleteArticleUseCase:
    """Tests pour la suppression d'articles."""

    def setup_method(self):
        self.mock_article_repo = Mock(spec=ArticleRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = DeleteArticleUseCase(
            article_repository=self.mock_article_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_delete_article_success(self):
        """Test: suppression reussie."""
        article = _make_article()
        self.mock_article_repo.find_by_id.return_value = article

        self.use_case.execute(article_id=1, deleted_by=1)

        self.mock_article_repo.delete.assert_called_once_with(1)

    def test_delete_article_not_found(self):
        """Test: erreur si article non trouve."""
        self.mock_article_repo.find_by_id.return_value = None

        with pytest.raises(ArticleNotFoundError):
            self.use_case.execute(article_id=999, deleted_by=1)
