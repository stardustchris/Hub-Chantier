"""DTOs pour les attestations TVA.

DEV-23: Generation attestation TVA reglementaire.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.attestation_tva import AttestationTVA


@dataclass
class AttestationTVACreateDTO:
    """DTO pour la creation d'une attestation TVA.

    Contient toutes les informations necessaires pour generer
    l'attestation CERFA reglementaire.
    """

    # Informations client / maitre d'ouvrage
    nom_client: str
    adresse_client: str
    telephone_client: Optional[str] = None

    # Informations immeuble
    adresse_immeuble: str = ""
    nature_immeuble: str = "maison"
    date_construction_plus_2ans: bool = True

    # Nature des travaux
    description_travaux: str = ""
    nature_travaux: str = "amelioration"

    # Signataire
    atteste_par: str = ""


@dataclass
class AttestationTVADTO:
    """DTO de sortie pour une attestation TVA."""

    id: int
    devis_id: int
    type_cerfa: str
    taux_tva: float
    nom_client: str
    adresse_client: str
    telephone_client: Optional[str]
    adresse_immeuble: str
    nature_immeuble: str
    date_construction_plus_2ans: bool
    description_travaux: str
    nature_travaux: str
    atteste_par: str
    date_attestation: Optional[str]
    generee_at: Optional[str]
    est_valide: bool

    @classmethod
    def from_entity(cls, attestation: AttestationTVA) -> AttestationTVADTO:
        """Cree un DTO depuis une entite AttestationTVA.

        Args:
            attestation: L'entite source.

        Returns:
            Le DTO correspondant.
        """
        return cls(
            id=attestation.id,
            devis_id=attestation.devis_id,
            type_cerfa=attestation.type_cerfa,
            taux_tva=attestation.taux_tva,
            nom_client=attestation.nom_client,
            adresse_client=attestation.adresse_client,
            telephone_client=attestation.telephone_client,
            adresse_immeuble=attestation.adresse_immeuble,
            nature_immeuble=attestation.nature_immeuble,
            date_construction_plus_2ans=attestation.date_construction_plus_2ans,
            description_travaux=attestation.description_travaux,
            nature_travaux=attestation.nature_travaux,
            atteste_par=attestation.atteste_par,
            date_attestation=(
                attestation.date_attestation.isoformat()
                if attestation.date_attestation else None
            ),
            generee_at=(
                attestation.generee_at.isoformat()
                if attestation.generee_at else None
            ),
            est_valide=attestation.est_valide(),
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
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
            "date_attestation": self.date_attestation,
            "generee_at": self.generee_at,
            "est_valide": self.est_valide,
        }


@dataclass
class EligibiliteTVADTO:
    """DTO de sortie pour la verification d'eligibilite TVA reduite."""

    devis_id: int
    taux_tva_defaut: str
    est_eligible: bool
    type_cerfa: Optional[str]
    libelle_tva: str
    message: str

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "devis_id": self.devis_id,
            "taux_tva_defaut": self.taux_tva_defaut,
            "est_eligible": self.est_eligible,
            "type_cerfa": self.type_cerfa,
            "libelle_tva": self.libelle_tva,
            "message": self.message,
        }
