"""Entité Fournisseur - Représente un fournisseur BTP.

FIN-14: Répertoire fournisseurs - Base fournisseurs partagée.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..value_objects import TypeFournisseur


@dataclass
class Fournisseur:
    """Représente un fournisseur de l'entreprise.

    Un fournisseur peut être un négoce matériaux, un loueur,
    un sous-traitant ou un prestataire de services.
    """

    id: Optional[int] = None
    raison_sociale: str = ""
    type: TypeFournisseur = TypeFournisseur.NEGOCE_MATERIAUX
    siret: Optional[str] = None
    adresse: Optional[str] = None
    contact_principal: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    conditions_paiement: Optional[str] = None
    notes: Optional[str] = None
    actif: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    # H10: Soft delete fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation à la création."""
        if not self.raison_sociale or not self.raison_sociale.strip():
            raise ValueError("La raison sociale est obligatoire")
        if self.siret is not None and self.siret.strip():
            siret_clean = self.siret.strip().replace(" ", "")
            if not re.match(r"^\d{14}$", siret_clean):
                raise ValueError(
                    "Le SIRET doit comporter exactement 14 chiffres"
                )
        if self.email is not None and self.email.strip():
            if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", self.email.strip()):
                raise ValueError("Format d'email invalide")

    def activer(self) -> None:
        """Active le fournisseur."""
        self.actif = True
        self.updated_at = datetime.utcnow()

    def desactiver(self) -> None:
        """Désactive le fournisseur (ne peut plus être sélectionné)."""
        self.actif = False
        self.updated_at = datetime.utcnow()

    def modifier_contact(
        self,
        contact_principal: Optional[str] = None,
        telephone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        """Modifie les informations de contact du fournisseur.

        Args:
            contact_principal: Nom du contact principal.
            telephone: Numéro de téléphone.
            email: Adresse email.
        """
        if contact_principal is not None:
            self.contact_principal = contact_principal
        if telephone is not None:
            self.telephone = telephone
        if email is not None:
            if email.strip():
                if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()):
                    raise ValueError("Format d'email invalide")
            self.email = email
        self.updated_at = datetime.utcnow()

    @property
    def est_supprime(self) -> bool:
        """Vérifie si le fournisseur a été supprimé (soft delete)."""
        return self.deleted_at is not None

    def supprimer(self, deleted_by: int) -> None:
        """Marque le fournisseur comme supprimé (soft delete).

        Args:
            deleted_by: ID de l'utilisateur qui supprime.
        """
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    def to_dict(self) -> dict:
        """Convertit l'entité en dictionnaire."""
        return {
            "id": self.id,
            "raison_sociale": self.raison_sociale,
            "type": self.type.value,
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
