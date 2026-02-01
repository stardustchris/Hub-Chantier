"""DTOs pour les articles de la bibliotheque.

DEV-01: Bibliotheque d'articles et bordereaux.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.article import Article


@dataclass
class ArticleCreateDTO:
    """DTO pour la creation d'un article."""

    designation: str
    unite: str = "U"
    prix_unitaire_ht: Decimal = Decimal("0")
    code: Optional[str] = None
    categorie: Optional[str] = None
    description: Optional[str] = None
    taux_tva: Decimal = Decimal("20")
    actif: bool = True


@dataclass
class ArticleUpdateDTO:
    """DTO pour la mise a jour d'un article."""

    designation: Optional[str] = None
    unite: Optional[str] = None
    prix_unitaire_ht: Optional[Decimal] = None
    code: Optional[str] = None
    categorie: Optional[str] = None
    description: Optional[str] = None
    taux_tva: Optional[Decimal] = None
    actif: Optional[bool] = None


@dataclass
class ArticleDTO:
    """DTO de sortie pour un article."""

    id: int
    designation: str
    unite: str
    prix_unitaire_ht: str
    code: Optional[str]
    categorie: Optional[str]
    description: Optional[str]
    taux_tva: str
    actif: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[int]

    @classmethod
    def from_entity(cls, article: Article) -> ArticleDTO:
        """Cree un DTO depuis une entite Article."""
        return cls(
            id=article.id,
            designation=article.libelle,
            unite=article.unite.value if hasattr(article.unite, 'value') else str(article.unite),
            prix_unitaire_ht=str(article.prix_unitaire_ht),
            code=article.code,
            categorie=article.categorie.value if hasattr(article.categorie, 'value') else str(article.categorie),
            description=article.description,
            taux_tva="20",  # TVA par defaut, pas de champ taux_tva sur l'entite Article
            actif=article.actif,
            created_at=article.created_at,
            updated_at=article.updated_at,
            created_by=article.created_by,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "designation": self.designation,
            "unite": self.unite,
            "prix_unitaire_ht": self.prix_unitaire_ht,
            "code": self.code,
            "categorie": self.categorie,
            "description": self.description,
            "taux_tva": self.taux_tva,
            "actif": self.actif,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }


@dataclass
class ArticleListDTO:
    """DTO pour la liste paginee d'articles."""

    items: List[ArticleDTO]
    total: int
    limit: int
    offset: int
