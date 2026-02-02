"""DTOs pour la conversion devis -> chantier.

DEV-16: Conversion en chantier - Donnees de sortie pour orchestrer
la creation de chantier par les modules externes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.devis import Devis
    from ...domain.entities.lot_devis import LotDevis


@dataclass
class LotConversionDTO:
    """Donnees d'un lot pour la conversion."""

    code_lot: str
    libelle: str
    montant_debourse_ht: str
    montant_vente_ht: str
    montant_vente_ttc: str
    ordre: int

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "code_lot": self.code_lot,
            "libelle": self.libelle,
            "montant_debourse_ht": self.montant_debourse_ht,
            "montant_vente_ht": self.montant_vente_ht,
            "montant_vente_ttc": self.montant_vente_ttc,
            "ordre": self.ordre,
        }


@dataclass
class ConversionDevisDTO:
    """DTO contenant toutes les donnees pour creer un chantier.

    Ce DTO est retourne par le use case de conversion et contient
    toutes les informations necessaires pour que les modules chantier
    et financier puissent creer leurs entites.
    """

    devis_id: int
    devis_numero: str
    client_nom: str
    client_adresse: Optional[str]
    client_email: Optional[str]
    client_telephone: Optional[str]
    objet: Optional[str]
    montant_total_ht: str
    montant_total_ttc: str
    retenue_garantie_pct: str
    montant_retenue_garantie: str
    montant_net_a_payer: str
    lots: List[LotConversionDTO]
    commercial_id: Optional[int]
    conducteur_id: Optional[int]
    date_conversion: str
    converti: bool = True

    @classmethod
    def from_entities(
        cls,
        devis: Devis,
        lots: List[LotDevis],
        date_conversion: datetime,
    ) -> ConversionDevisDTO:
        """Construit le DTO depuis les entites du domaine.

        Args:
            devis: L'entite Devis source.
            lots: Les lots du devis.
            date_conversion: Date/heure de la conversion.

        Returns:
            Le DTO de conversion complet.
        """
        lots_dto = [
            LotConversionDTO(
                code_lot=lot.code_lot,
                libelle=lot.libelle,
                montant_debourse_ht=str(lot.montant_debourse_ht),
                montant_vente_ht=str(lot.montant_vente_ht),
                montant_vente_ttc=str(lot.montant_vente_ttc),
                ordre=lot.ordre,
            )
            for lot in lots
            if not lot.est_supprime
        ]

        return cls(
            devis_id=devis.id,
            devis_numero=devis.numero,
            client_nom=devis.client_nom,
            client_adresse=devis.client_adresse,
            client_email=devis.client_email,
            client_telephone=devis.client_telephone,
            objet=devis.objet,
            montant_total_ht=str(devis.montant_total_ht),
            montant_total_ttc=str(devis.montant_total_ttc),
            retenue_garantie_pct=str(devis.retenue_garantie_pct),
            montant_retenue_garantie=str(devis.montant_retenue_garantie),
            montant_net_a_payer=str(devis.montant_net_a_payer),
            lots=lots_dto,
            commercial_id=devis.commercial_id,
            conducteur_id=devis.conducteur_id,
            date_conversion=date_conversion.isoformat(),
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "devis_id": self.devis_id,
            "devis_numero": self.devis_numero,
            "client_nom": self.client_nom,
            "client_adresse": self.client_adresse,
            "client_email": self.client_email,
            "client_telephone": self.client_telephone,
            "objet": self.objet,
            "montant_total_ht": self.montant_total_ht,
            "montant_total_ttc": self.montant_total_ttc,
            "retenue_garantie_pct": self.retenue_garantie_pct,
            "montant_retenue_garantie": self.montant_retenue_garantie,
            "montant_net_a_payer": self.montant_net_a_payer,
            "lots": [lot.to_dict() for lot in self.lots],
            "commercial_id": self.commercial_id,
            "conducteur_id": self.conducteur_id,
            "date_conversion": self.date_conversion,
            "converti": self.converti,
        }


@dataclass
class ConversionInfoDTO:
    """DTO retourne par GetConversionInfoUseCase.

    Indique si la conversion est possible et les pre-requis manquants.
    """

    devis_id: int
    devis_numero: str
    conversion_possible: bool
    deja_converti: bool
    converti_en_chantier_id: Optional[int]
    statut_actuel: str
    est_accepte: bool
    est_signe: bool
    pre_requis_manquants: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "devis_id": self.devis_id,
            "devis_numero": self.devis_numero,
            "conversion_possible": self.conversion_possible,
            "deja_converti": self.deja_converti,
            "converti_en_chantier_id": self.converti_en_chantier_id,
            "statut_actuel": self.statut_actuel,
            "est_accepte": self.est_accepte,
            "est_signe": self.est_signe,
            "pre_requis_manquants": self.pre_requis_manquants,
        }
