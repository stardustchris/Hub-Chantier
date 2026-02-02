"""Entite SignatureDevis - Signature electronique client.

DEV-14: Signature electronique client.
Signature simple conforme eIDAS avec tracabilite complete
(horodatage, IP, user-agent, hash document).
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..value_objects.type_signature import TypeSignature


class SignatureDevisValidationError(Exception):
    """Erreur levee lors d'une validation metier sur une signature."""

    pass


@dataclass
class SignatureDevis:
    """Represente une signature electronique sur un devis.

    Conforme eIDAS (signature electronique simple) :
    - Tracabilite : IP, user agent, horodatage
    - Integrite : hash SHA-512 du document
    - Non-repudiation : donnees de signature conservees

    Attributes:
        id: Identifiant unique (None si non persiste).
        devis_id: Reference au devis signe.
        type_signature: Type de signature (dessin, upload, nom_prenom).
        signataire_nom: Nom complet du signataire.
        signataire_email: Email du signataire.
        signataire_telephone: Telephone du signataire (optionnel).
        signature_data: Donnees de signature (base64 PNG, path scan, texte).
        ip_adresse: Adresse IP du signataire (tracabilite eIDAS).
        user_agent: User-agent du navigateur (tracabilite eIDAS).
        horodatage: Date/heure exacte de la signature (tracabilite eIDAS).
        hash_document: Hash SHA-512 du document au moment de la signature.
        valide: Indique si la signature est valide (non revoquee).
        revoquee_at: Date de revocation (None si non revoquee).
        revoquee_par: ID utilisateur ayant revoque (None si non revoquee).
        motif_revocation: Motif de la revocation (None si non revoquee).
        created_at: Date de creation technique.
    """

    devis_id: int
    type_signature: TypeSignature
    signataire_nom: str
    signataire_email: str
    signature_data: str
    ip_adresse: str
    user_agent: str
    horodatage: datetime
    hash_document: str

    # Identifiant
    id: Optional[int] = None

    # Champs optionnels
    signataire_telephone: Optional[str] = None

    # Etat
    valide: bool = True

    # Revocation
    revoquee_at: Optional[datetime] = None
    revoquee_par: Optional[int] = None
    motif_revocation: Optional[str] = None

    # Timestamps
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if self.devis_id <= 0:
            raise SignatureDevisValidationError(
                "L'ID du devis est obligatoire"
            )
        if not self.signataire_nom or not self.signataire_nom.strip():
            raise SignatureDevisValidationError(
                "Le nom du signataire est obligatoire"
            )
        if not self.signataire_email or not self.signataire_email.strip():
            raise SignatureDevisValidationError(
                "L'email du signataire est obligatoire"
            )
        if not self.signature_data or not self.signature_data.strip():
            raise SignatureDevisValidationError(
                "Les donnees de signature sont obligatoires"
            )
        if not self.ip_adresse or len(self.ip_adresse) < 7:
            raise SignatureDevisValidationError(
                "L'adresse IP est obligatoire (tracabilite eIDAS)"
            )
        if not self.user_agent or not self.user_agent.strip():
            raise SignatureDevisValidationError(
                "Le user-agent est obligatoire (tracabilite eIDAS)"
            )
        if not self.hash_document or len(self.hash_document) != 128:
            raise SignatureDevisValidationError(
                "Le hash SHA-512 du document est obligatoire (128 caracteres hex)"
            )

    @property
    def est_valide(self) -> bool:
        """Verifie si la signature est valide.

        Une signature est valide si elle n'a pas ete revoquee
        et que son indicateur valide est True.

        Returns:
            True si la signature est valide et non revoquee.
        """
        return self.valide and self.revoquee_at is None

    def revoquer(self, par: int, motif: str) -> None:
        """Revoque la signature electronique.

        La revocation est irreversible. Elle invalide la signature
        et enregistre qui l'a revoquee et pourquoi.

        Args:
            par: ID de l'utilisateur qui revoque (admin).
            motif: Motif de la revocation (obligatoire).

        Raises:
            SignatureDevisValidationError: Si la signature est deja revoquee
                ou si le motif est vide.
        """
        if self.revoquee_at is not None:
            raise SignatureDevisValidationError(
                "La signature est deja revoquee"
            )
        if not motif or not motif.strip():
            raise SignatureDevisValidationError(
                "Le motif de revocation est obligatoire"
            )
        if par <= 0:
            raise SignatureDevisValidationError(
                "L'identifiant de l'utilisateur revoquant est obligatoire"
            )

        self.valide = False
        self.revoquee_at = datetime.utcnow()
        self.revoquee_par = par
        self.motif_revocation = motif.strip()

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "devis_id": self.devis_id,
            "type_signature": self.type_signature.value,
            "signataire_nom": self.signataire_nom,
            "signataire_email": self.signataire_email,
            "signataire_telephone": self.signataire_telephone,
            "signature_data": self.signature_data,
            "ip_adresse": self.ip_adresse,
            "user_agent": self.user_agent,
            "horodatage": (
                self.horodatage.isoformat()
                if self.horodatage else None
            ),
            "hash_document": self.hash_document,
            "valide": self.valide,
            "est_valide": self.est_valide,
            "revoquee_at": (
                self.revoquee_at.isoformat()
                if self.revoquee_at else None
            ),
            "revoquee_par": self.revoquee_par,
            "motif_revocation": self.motif_revocation,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at else None
            ),
        }
