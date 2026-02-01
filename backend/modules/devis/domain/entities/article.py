"""Entite Article - Bibliotheque de prix.

DEV-01: Bibliotheque d'articles et bordereaux - Base de donnees d'articles
avec prix unitaires, unites, codes et composants detailles.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from ..value_objects import CategorieArticle, UniteArticle


@dataclass
class Article:
    """Represente un article de la bibliotheque de prix.

    Un article est un element reutilisable (materiau, ouvrage, main d'oeuvre)
    avec un prix unitaire de reference. Les articles peuvent avoir des
    composants detailles (sous-articles) stockes en JSON.
    """

    id: Optional[int] = None
    code: str = ""
    libelle: str = ""
    description: Optional[str] = None
    unite: UniteArticle = UniteArticle.U
    prix_unitaire_ht: Decimal = Decimal("0")
    categorie: CategorieArticle = CategorieArticle.DIVERS
    composants_json: Optional[List[Dict[str, Any]]] = None
    actif: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    # H10: Soft delete fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if not self.code or not self.code.strip():
            raise ValueError("Le code de l'article est obligatoire")
        if not self.libelle or not self.libelle.strip():
            raise ValueError("Le libelle de l'article est obligatoire")
        if self.prix_unitaire_ht < Decimal("0"):
            raise ValueError("Le prix unitaire HT ne peut pas etre negatif")

    @property
    def est_supprime(self) -> bool:
        """Verifie si l'article a ete supprime (soft delete)."""
        return self.deleted_at is not None

    def desactiver(self) -> None:
        """Desactive l'article (n'apparait plus dans les recherches)."""
        self.actif = False
        self.updated_at = datetime.utcnow()

    def activer(self) -> None:
        """Active l'article."""
        self.actif = True
        self.updated_at = datetime.utcnow()

    def mettre_a_jour_prix(self, nouveau_prix: Decimal) -> None:
        """Met a jour le prix unitaire de l'article.

        Args:
            nouveau_prix: Le nouveau prix unitaire HT.

        Raises:
            ValueError: Si le prix est negatif.
        """
        if nouveau_prix < Decimal("0"):
            raise ValueError("Le prix unitaire HT ne peut pas etre negatif")
        self.prix_unitaire_ht = nouveau_prix
        self.updated_at = datetime.utcnow()

    def supprimer(self, deleted_by: int) -> None:
        """Marque l'article comme supprime (soft delete).

        Args:
            deleted_by: ID de l'utilisateur qui supprime.
        """
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "code": self.code,
            "libelle": self.libelle,
            "description": self.description,
            "unite": self.unite.value,
            "prix_unitaire_ht": str(self.prix_unitaire_ht),
            "categorie": self.categorie.value,
            "composants_json": self.composants_json,
            "actif": self.actif,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }
