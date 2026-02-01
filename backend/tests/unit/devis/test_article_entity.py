"""Tests unitaires pour l'entite Article.

DEV-01: Bibliotheque d'articles et bordereaux.
"""

import pytest
from datetime import datetime
from decimal import Decimal

from modules.devis.domain.entities.article import Article
from modules.devis.domain.value_objects.categorie_article import CategorieArticle
from modules.devis.domain.value_objects.unite_article import UniteArticle


class TestArticleCreation:
    """Tests pour la creation d'un article."""

    def test_create_article_valid(self):
        """Test: creation d'un article valide."""
        article = Article(
            id=1,
            code="ART-001",
            libelle="Beton C25/30",
            unite=UniteArticle.M3,
            prix_unitaire_ht=Decimal("95.50"),
            categorie=CategorieArticle.GROS_OEUVRE,
        )
        assert article.id == 1
        assert article.code == "ART-001"
        assert article.libelle == "Beton C25/30"
        assert article.unite == UniteArticle.M3
        assert article.prix_unitaire_ht == Decimal("95.50")
        assert article.categorie == CategorieArticle.GROS_OEUVRE
        assert article.actif is True

    def test_create_article_minimal(self):
        """Test: creation d'un article avec le minimum requis."""
        article = Article(code="ART-001", libelle="Test")
        assert article.code == "ART-001"
        assert article.libelle == "Test"
        assert article.unite == UniteArticle.U  # default
        assert article.prix_unitaire_ht == Decimal("0")
        assert article.categorie == CategorieArticle.DIVERS  # default
        assert article.actif is True

    def test_create_article_code_vide(self):
        """Test: erreur si code vide."""
        with pytest.raises(ValueError) as exc_info:
            Article(code="", libelle="Test")
        assert "code" in str(exc_info.value).lower()

    def test_create_article_code_espaces(self):
        """Test: erreur si code uniquement espaces."""
        with pytest.raises(ValueError):
            Article(code="   ", libelle="Test")

    def test_create_article_libelle_vide(self):
        """Test: erreur si libelle vide."""
        with pytest.raises(ValueError) as exc_info:
            Article(code="ART-001", libelle="")
        assert "libelle" in str(exc_info.value).lower()

    def test_create_article_libelle_espaces(self):
        """Test: erreur si libelle uniquement espaces."""
        with pytest.raises(ValueError):
            Article(code="ART-001", libelle="   ")

    def test_create_article_prix_negatif(self):
        """Test: erreur si prix unitaire negatif."""
        with pytest.raises(ValueError) as exc_info:
            Article(
                code="ART-001",
                libelle="Test",
                prix_unitaire_ht=Decimal("-1"),
            )
        assert "prix" in str(exc_info.value).lower()

    def test_create_article_prix_zero(self):
        """Test: prix unitaire a zero est accepte."""
        article = Article(
            code="ART-001",
            libelle="Test",
            prix_unitaire_ht=Decimal("0"),
        )
        assert article.prix_unitaire_ht == Decimal("0")

    def test_create_article_avec_composants(self):
        """Test: creation d'un article avec composants JSON."""
        composants = [
            {"ref": "MAT-001", "quantite": 2.5, "prix": 10.0},
            {"ref": "MO-001", "quantite": 1.0, "prix": 45.0},
        ]
        article = Article(
            code="ART-001",
            libelle="Ouvrage compose",
            composants_json=composants,
        )
        assert article.composants_json is not None
        assert len(article.composants_json) == 2


class TestArticleProprietes:
    """Tests pour les proprietes de l'article."""

    def _make_article(self, **kwargs):
        """Cree un article valide avec valeurs par defaut."""
        defaults = {"code": "ART-001", "libelle": "Test article"}
        defaults.update(kwargs)
        return Article(**defaults)

    def test_est_supprime_non(self):
        """Test: article non supprime."""
        article = self._make_article()
        assert article.est_supprime is False

    def test_est_supprime_oui(self):
        """Test: article supprime."""
        article = self._make_article(deleted_at=datetime.utcnow())
        assert article.est_supprime is True


class TestArticleActions:
    """Tests pour les actions sur un article."""

    def _make_article(self, **kwargs):
        """Cree un article valide avec valeurs par defaut."""
        defaults = {"code": "ART-001", "libelle": "Test article"}
        defaults.update(kwargs)
        return Article(**defaults)

    def test_desactiver(self):
        """Test: desactivation d'un article."""
        article = self._make_article(actif=True)
        article.desactiver()
        assert article.actif is False
        assert article.updated_at is not None

    def test_activer(self):
        """Test: activation d'un article."""
        article = self._make_article(actif=False)
        article.activer()
        assert article.actif is True
        assert article.updated_at is not None

    def test_mettre_a_jour_prix(self):
        """Test: mise a jour du prix unitaire."""
        article = self._make_article(prix_unitaire_ht=Decimal("50"))
        article.mettre_a_jour_prix(Decimal("75.50"))
        assert article.prix_unitaire_ht == Decimal("75.50")
        assert article.updated_at is not None

    def test_mettre_a_jour_prix_zero(self):
        """Test: mise a jour du prix a zero est acceptee."""
        article = self._make_article(prix_unitaire_ht=Decimal("50"))
        article.mettre_a_jour_prix(Decimal("0"))
        assert article.prix_unitaire_ht == Decimal("0")

    def test_mettre_a_jour_prix_negatif(self):
        """Test: erreur si nouveau prix negatif."""
        article = self._make_article()
        with pytest.raises(ValueError) as exc_info:
            article.mettre_a_jour_prix(Decimal("-10"))
        assert "prix" in str(exc_info.value).lower()

    def test_supprimer(self):
        """Test: suppression en soft delete."""
        article = self._make_article()
        assert article.est_supprime is False
        article.supprimer(deleted_by=1)
        assert article.est_supprime is True
        assert article.deleted_at is not None
        assert article.deleted_by == 1


class TestArticleToDict:
    """Tests pour la conversion en dictionnaire."""

    def test_to_dict(self):
        """Test: conversion en dictionnaire."""
        now = datetime.utcnow()
        article = Article(
            id=1,
            code="ART-001",
            libelle="Beton C25/30",
            unite=UniteArticle.M3,
            prix_unitaire_ht=Decimal("95.50"),
            categorie=CategorieArticle.GROS_OEUVRE,
            actif=True,
            created_at=now,
        )
        d = article.to_dict()
        assert d["id"] == 1
        assert d["code"] == "ART-001"
        assert d["libelle"] == "Beton C25/30"
        assert d["unite"] == "m3"
        assert d["prix_unitaire_ht"] == "95.50"
        assert d["categorie"] == "gros_oeuvre"
        assert d["actif"] is True
        assert d["created_at"] == now.isoformat()
