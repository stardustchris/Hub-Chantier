"""DTOs pour les signatures electroniques de devis.

DEV-14: Signature electronique client.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.signature_devis import SignatureDevis


@dataclass
class SignatureCreateDTO:
    """DTO pour la creation d'une signature electronique.

    Contient les donnees fournies par le client lors de la signature.
    Les champs de tracabilite (IP, user-agent) sont injectes par le serveur.
    """

    type_signature: str
    signataire_nom: str
    signataire_email: str
    signature_data: str
    ip_adresse: str
    user_agent: str
    signataire_telephone: Optional[str] = None


@dataclass
class SignatureDTO:
    """DTO de sortie pour une signature electronique."""

    id: int
    devis_id: int
    type_signature: str
    signataire_nom: str
    signataire_email: str
    signataire_telephone: Optional[str]
    signature_data: str
    ip_adresse: str
    user_agent: str
    horodatage: str
    hash_document: str
    valide: bool
    est_valide: bool
    revoquee_at: Optional[str]
    revoquee_par: Optional[int]
    motif_revocation: Optional[str]
    created_at: Optional[str]

    @classmethod
    def from_entity(cls, signature: SignatureDevis) -> SignatureDTO:
        """Cree un DTO depuis une entite SignatureDevis.

        Args:
            signature: L'entite source.

        Returns:
            Le DTO correspondant.
        """
        return cls(
            id=signature.id,
            devis_id=signature.devis_id,
            type_signature=signature.type_signature.value,
            signataire_nom=signature.signataire_nom,
            signataire_email=signature.signataire_email,
            signataire_telephone=signature.signataire_telephone,
            signature_data=signature.signature_data,
            ip_adresse=signature.ip_adresse,
            user_agent=signature.user_agent,
            horodatage=(
                signature.horodatage.isoformat()
                if signature.horodatage else None
            ),
            hash_document=signature.hash_document,
            valide=signature.valide,
            est_valide=signature.est_valide,
            revoquee_at=(
                signature.revoquee_at.isoformat()
                if signature.revoquee_at else None
            ),
            revoquee_par=signature.revoquee_par,
            motif_revocation=signature.motif_revocation,
            created_at=(
                signature.created_at.isoformat()
                if signature.created_at else None
            ),
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "devis_id": self.devis_id,
            "type_signature": self.type_signature,
            "signataire_nom": self.signataire_nom,
            "signataire_email": self.signataire_email,
            "signataire_telephone": self.signataire_telephone,
            "signature_data": self.signature_data,
            "ip_adresse": self.ip_adresse,
            "user_agent": self.user_agent,
            "horodatage": self.horodatage,
            "hash_document": self.hash_document,
            "valide": self.valide,
            "est_valide": self.est_valide,
            "revoquee_at": self.revoquee_at,
            "revoquee_par": self.revoquee_par,
            "motif_revocation": self.motif_revocation,
            "created_at": self.created_at,
        }


@dataclass
class RevocationDTO:
    """DTO pour la revocation d'une signature electronique."""

    motif: str


@dataclass
class VerificationSignatureDTO:
    """DTO de sortie pour la verification d'une signature."""

    devis_id: int
    signature_id: Optional[int]
    est_signee: bool
    est_valide: bool
    hash_document_actuel: Optional[str]
    hash_document_signature: Optional[str]
    integrite_document: bool
    message: str

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "devis_id": self.devis_id,
            "signature_id": self.signature_id,
            "est_signee": self.est_signee,
            "est_valide": self.est_valide,
            "hash_document_actuel": self.hash_document_actuel,
            "hash_document_signature": self.hash_document_signature,
            "integrite_document": self.integrite_document,
            "message": self.message,
        }
