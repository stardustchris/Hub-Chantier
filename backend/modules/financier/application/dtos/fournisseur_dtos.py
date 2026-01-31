"""DTOs pour les fournisseurs.

FIN-14: Répertoire fournisseurs - Base fournisseurs partagée.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from ...domain.value_objects import TypeFournisseur

if TYPE_CHECKING:
    from ...domain.entities import Fournisseur


@dataclass
class FournisseurCreateDTO:
    """DTO pour la création d'un fournisseur."""

    raison_sociale: str
    type: TypeFournisseur = TypeFournisseur.NEGOCE_MATERIAUX
    siret: Optional[str] = None
    adresse: Optional[str] = None
    contact_principal: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    conditions_paiement: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class FournisseurUpdateDTO:
    """DTO pour la mise à jour d'un fournisseur."""

    raison_sociale: Optional[str] = None
    type: Optional[TypeFournisseur] = None
    siret: Optional[str] = None
    adresse: Optional[str] = None
    contact_principal: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    conditions_paiement: Optional[str] = None
    notes: Optional[str] = None
    actif: Optional[bool] = None


@dataclass
class FournisseurDTO:
    """DTO de sortie pour un fournisseur."""

    id: int
    raison_sociale: str
    type: str
    type_label: str
    siret: Optional[str]
    adresse: Optional[str]
    contact_principal: Optional[str]
    telephone: Optional[str]
    email: Optional[str]
    conditions_paiement: Optional[str]
    notes: Optional[str]
    actif: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[int]

    @classmethod
    def from_entity(cls, fournisseur: Fournisseur) -> FournisseurDTO:
        """Crée un DTO depuis une entité Fournisseur.

        Args:
            fournisseur: L'entité Fournisseur source.

        Returns:
            Le DTO de sortie.
        """
        return cls(
            id=fournisseur.id,
            raison_sociale=fournisseur.raison_sociale,
            type=fournisseur.type.value,
            type_label=fournisseur.type.label,
            siret=fournisseur.siret,
            adresse=fournisseur.adresse,
            contact_principal=fournisseur.contact_principal,
            telephone=fournisseur.telephone,
            email=fournisseur.email,
            conditions_paiement=fournisseur.conditions_paiement,
            notes=fournisseur.notes,
            actif=fournisseur.actif,
            created_at=fournisseur.created_at,
            updated_at=fournisseur.updated_at,
            created_by=fournisseur.created_by,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "raison_sociale": self.raison_sociale,
            "type": self.type,
            "type_label": self.type_label,
            "siret": self.siret,
            "adresse": self.adresse,
            "contact_principal": self.contact_principal,
            "telephone": self.telephone,
            "email": self.email,
            "conditions_paiement": self.conditions_paiement,
            "notes": self.notes,
            "actif": self.actif,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }


@dataclass
class FournisseurListDTO:
    """DTO pour une liste paginée de fournisseurs."""

    items: List[FournisseurDTO]
    total: int
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        """Indique s'il y a plus de résultats."""
        return self.offset + len(self.items) < self.total
