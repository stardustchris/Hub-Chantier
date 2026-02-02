"""Entite AttestationTVA - Attestation TVA reglementaire.

DEV-23: Generation attestation TVA selon taux applique.

En France, pour les travaux de renovation sur batiments de plus de 2 ans,
le client doit fournir une attestation TVA (CERFA 1300-SD ou 1301-SD)
pour beneficier d'un taux de TVA reduit.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


class AttestationTVAValidationError(Exception):
    """Erreur levee lors d'une validation metier sur une attestation TVA."""

    pass


@dataclass
class AttestationTVA:
    """Represente une attestation TVA reglementaire liee a un devis.

    L'attestation TVA est un document CERFA obligatoire pour l'application
    d'un taux de TVA reduit (5.5% ou 10%) sur des travaux de renovation
    de batiments de plus de 2 ans.

    Attributes:
        id: Identifiant unique (None si non persiste).
        devis_id: Reference au devis associe.
        type_cerfa: Type de formulaire CERFA ('1300-SD' ou '1301-SD').
        taux_tva: Taux de TVA applique (5.5 ou 10.0).
        nom_client: Nom du client/maitre d'ouvrage.
        adresse_client: Adresse du client.
        telephone_client: Telephone du client.
        adresse_immeuble: Adresse de l'immeuble concerne par les travaux.
        nature_immeuble: Type de l'immeuble ('maison', 'appartement', 'immeuble').
        date_construction_plus_2ans: L'immeuble a plus de 2 ans.
        description_travaux: Description des travaux a realiser.
        nature_travaux: Nature des travaux ('amelioration', 'entretien', 'transformation').
        atteste_par: Nom du signataire de l'attestation.
        date_attestation: Date de signature de l'attestation.
        generee_at: Date de generation automatique.
        created_at: Date de creation technique.
        updated_at: Date de derniere modification technique.
    """

    # Champs obligatoires
    devis_id: int
    type_cerfa: str
    taux_tva: float

    # Informations client
    nom_client: str = ""
    adresse_client: str = ""
    telephone_client: Optional[str] = None

    # Informations immeuble
    adresse_immeuble: str = ""
    nature_immeuble: str = "maison"
    date_construction_plus_2ans: bool = True

    # Nature des travaux
    description_travaux: str = ""
    nature_travaux: str = "amelioration"

    # Attestation
    atteste_par: str = ""
    date_attestation: Optional[datetime] = None
    generee_at: Optional[datetime] = None

    # Identifiant
    id: Optional[int] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Constantes de validation
    TYPES_CERFA_VALIDES = ("1300-SD", "1301-SD")
    TAUX_TVA_REDUITS = (5.5, 10.0)
    NATURES_IMMEUBLE_VALIDES = ("maison", "appartement", "immeuble")
    NATURES_TRAVAUX_VALIDES = ("amelioration", "entretien", "transformation")

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        if self.type_cerfa not in self.TYPES_CERFA_VALIDES:
            raise AttestationTVAValidationError(
                f"Type CERFA invalide: {self.type_cerfa}. "
                f"Valeurs autorisees: {', '.join(self.TYPES_CERFA_VALIDES)}"
            )

        if self.taux_tva not in self.TAUX_TVA_REDUITS:
            raise AttestationTVAValidationError(
                f"Taux TVA invalide pour attestation: {self.taux_tva}%. "
                f"Seuls les taux reduits (5.5%, 10%) necessitent une attestation."
            )

        if self.nature_immeuble not in self.NATURES_IMMEUBLE_VALIDES:
            raise AttestationTVAValidationError(
                f"Nature d'immeuble invalide: {self.nature_immeuble}. "
                f"Valeurs autorisees: {', '.join(self.NATURES_IMMEUBLE_VALIDES)}"
            )

        if self.nature_travaux not in self.NATURES_TRAVAUX_VALIDES:
            raise AttestationTVAValidationError(
                f"Nature de travaux invalide: {self.nature_travaux}. "
                f"Valeurs autorisees: {', '.join(self.NATURES_TRAVAUX_VALIDES)}"
            )

        # Coherence type CERFA / taux TVA
        if self.taux_tva == 5.5 and self.type_cerfa != "1301-SD":
            raise AttestationTVAValidationError(
                "Le taux 5.5% (travaux lourds) necessite le CERFA 1301-SD"
            )
        if self.taux_tva == 10.0 and self.type_cerfa != "1300-SD":
            raise AttestationTVAValidationError(
                "Le taux 10% (travaux simples) necessite le CERFA 1300-SD"
            )

    def est_valide(self) -> bool:
        """Verifie que tous les champs obligatoires sont remplis.

        Une attestation est valide si toutes les informations
        necessaires sont presentes pour la generer.

        Returns:
            True si tous les champs obligatoires sont remplis.
        """
        champs_obligatoires = [
            self.nom_client,
            self.adresse_client,
            self.adresse_immeuble,
            self.description_travaux,
            self.atteste_par,
        ]
        # Tous les champs texte doivent etre non-vides
        if not all(champ and champ.strip() for champ in champs_obligatoires):
            return False

        # L'immeuble doit avoir plus de 2 ans
        if not self.date_construction_plus_2ans:
            return False

        return True

    def signer(self, signataire: str) -> None:
        """Signe l'attestation.

        Args:
            signataire: Nom du signataire.

        Raises:
            AttestationTVAValidationError: Si l'attestation n'est pas valide.
        """
        self.atteste_par = signataire
        self.date_attestation = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        if not self.est_valide():
            raise AttestationTVAValidationError(
                "L'attestation ne peut pas etre signee: "
                "tous les champs obligatoires doivent etre remplis."
            )

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID (entite)."""
        if not isinstance(other, AttestationTVA):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "devis_id": self.devis_id,
            "type_cerfa": self.type_cerfa,
            "taux_tva": self.taux_tva,
            "nom_client": self.nom_client,
            "adresse_client": self.adresse_client,
            "telephone_client": self.telephone_client,
            "adresse_immeuble": self.adresse_immeuble,
            "nature_immeuble": self.nature_immeuble,
            "date_construction_plus_2ans": self.date_construction_plus_2ans,
            "description_travaux": self.description_travaux,
            "nature_travaux": self.nature_travaux,
            "atteste_par": self.atteste_par,
            "date_attestation": (
                self.date_attestation.isoformat()
                if self.date_attestation else None
            ),
            "generee_at": (
                self.generee_at.isoformat()
                if self.generee_at else None
            ),
            "created_at": (
                self.created_at.isoformat()
                if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at else None
            ),
        }
