"""Entite SignatureIntervention.

INT-13: Signature client - Sur mobile avec stylet/doigt
INT-14: Rapport PDF - Signatures: Client + Technicien avec horodatage
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class TypeSignataire(str, Enum):
    """Types de signataires."""

    CLIENT = "client"
    TECHNICIEN = "technicien"

    @property
    def label(self) -> str:
        """Retourne le libelle affichable."""
        labels = {
            TypeSignataire.CLIENT: "Client",
            TypeSignataire.TECHNICIEN: "Technicien",
        }
        return labels[self]


@dataclass
class SignatureIntervention:
    """Represente une signature sur l'intervention.

    Selon le CDC Section 12:
    - INT-13: Signature client sur mobile avec stylet/doigt
    - Le rapport PDF inclut les signatures Client + Technicien avec horodatage

    Attributes:
        id: Identifiant unique.
        intervention_id: ID de l'intervention.
        type_signataire: Type (client ou technicien).
        nom_signataire: Nom du signataire.
        signature_data: Donnees de la signature (base64 ou URL).
        utilisateur_id: ID utilisateur si technicien.
        ip_address: Adresse IP pour tracabilite.
        user_agent: User agent du navigateur/app.
        latitude: Coordonnee GPS (optionnel).
        longitude: Coordonnee GPS (optionnel).
        signed_at: Date et heure de la signature.
    """

    intervention_id: int
    type_signataire: TypeSignataire
    nom_signataire: str
    signature_data: str

    id: Optional[int] = None
    utilisateur_id: Optional[int] = None  # Rempli si technicien
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    signed_at: datetime = field(default_factory=datetime.utcnow)
    # Soft delete
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if self.intervention_id <= 0:
            raise ValueError("L'ID de l'intervention doit etre positif")
        if not self.nom_signataire or not self.nom_signataire.strip():
            raise ValueError("Le nom du signataire est obligatoire")
        if not self.signature_data or not self.signature_data.strip():
            raise ValueError("Les donnees de signature sont obligatoires")

        self.nom_signataire = self.nom_signataire.strip()

        # Validation: si technicien, utilisateur_id obligatoire
        if self.type_signataire == TypeSignataire.TECHNICIEN:
            if not self.utilisateur_id or self.utilisateur_id <= 0:
                raise ValueError(
                    "L'ID utilisateur est obligatoire pour une signature technicien"
                )

    @property
    def est_supprimee(self) -> bool:
        """Verifie si la signature a ete supprimee (soft delete)."""
        return self.deleted_at is not None

    @property
    def est_signature_client(self) -> bool:
        """Verifie si c'est une signature client."""
        return self.type_signataire == TypeSignataire.CLIENT

    @property
    def est_signature_technicien(self) -> bool:
        """Verifie si c'est une signature technicien."""
        return self.type_signataire == TypeSignataire.TECHNICIEN

    @property
    def a_geolocalisation(self) -> bool:
        """Verifie si la signature a une geolocalisation."""
        return self.latitude is not None and self.longitude is not None

    @property
    def horodatage_str(self) -> str:
        """Retourne l'horodatage sous forme lisible."""
        return self.signed_at.strftime("%d/%m/%Y a %H:%M")

    def supprimer(self, deleted_by: int) -> None:
        """Marque la signature comme supprimee (soft delete)."""
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    @classmethod
    def creer_signature_client(
        cls,
        intervention_id: int,
        nom_client: str,
        signature_data: str,
        ip_address: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> "SignatureIntervention":
        """Factory pour creer une signature client."""
        return cls(
            intervention_id=intervention_id,
            type_signataire=TypeSignataire.CLIENT,
            nom_signataire=nom_client,
            signature_data=signature_data,
            ip_address=ip_address,
            latitude=latitude,
            longitude=longitude,
        )

    @classmethod
    def creer_signature_technicien(
        cls,
        intervention_id: int,
        utilisateur_id: int,
        nom_technicien: str,
        signature_data: str,
        ip_address: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> "SignatureIntervention":
        """Factory pour creer une signature technicien."""
        return cls(
            intervention_id=intervention_id,
            type_signataire=TypeSignataire.TECHNICIEN,
            nom_signataire=nom_technicien,
            signature_data=signature_data,
            utilisateur_id=utilisateur_id,
            ip_address=ip_address,
            latitude=latitude,
            longitude=longitude,
        )

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID."""
        if not isinstance(other, SignatureIntervention):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))

    def __str__(self) -> str:
        """Representation textuelle."""
        return f"Signature {self.type_signataire.label}: {self.nom_signataire} ({self.horodatage_str})"

    def __repr__(self) -> str:
        """Representation technique."""
        return (
            f"SignatureIntervention(id={self.id}, intervention_id={self.intervention_id}, "
            f"type={self.type_signataire.value}, nom='{self.nom_signataire}')"
        )
