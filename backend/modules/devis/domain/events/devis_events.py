"""Domain Events pour le module Devis.

DEV-16: Conversion en chantier - DevisConvertEvent.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional


@dataclass(frozen=True)
class LotConversionData:
    """Donnees d'un lot pour la conversion devis -> chantier.

    Contient les informations necessaires pour creer un lot budgetaire
    dans le module chantier/financier.
    """

    code_lot: str
    libelle: str
    montant_debourse_ht: Decimal
    montant_vente_ht: Decimal


@dataclass(frozen=True)
class DevisConvertEvent:
    """Event emis lorsqu'un devis accepte est converti en chantier.

    DEV-16: Cet event contient toutes les donnees necessaires pour que
    les modules chantier et financier puissent creer le chantier et
    le budget associe, SANS import cross-module.

    Les modules abonnes (chantiers, financier) reagissent a cet event
    pour creer leurs propres entites.

    Attributes:
        devis_id: ID du devis converti.
        numero: Numero du devis (ex: DEV-2026-042).
        client_nom: Nom du client.
        client_adresse: Adresse du client.
        client_email: Email du client.
        objet: Objet / description du devis.
        montant_total_ht: Montant total HT du devis.
        montant_total_ttc: Montant total TTC du devis.
        retenue_garantie_pct: Pourcentage de retenue de garantie (0, 5 ou 10).
        lots: Liste des lots avec leurs montants debourses et vente.
        commercial_id: ID du commercial assigne (optionnel).
        conducteur_id: ID du conducteur de travaux assigne (optionnel).
        date_conversion: Date/heure de la conversion.
    """

    devis_id: int
    numero: str
    client_nom: str
    client_adresse: Optional[str]
    client_email: Optional[str]
    objet: Optional[str]
    montant_total_ht: Decimal
    montant_total_ttc: Decimal
    retenue_garantie_pct: Decimal
    lots: List[LotConversionData]
    commercial_id: Optional[int]
    conducteur_id: Optional[int]
    date_conversion: datetime

    def to_dict(self) -> dict:
        """Serialise l'event en dictionnaire pour stockage/transport."""
        return {
            "event_type": "DevisConvertEvent",
            "devis_id": self.devis_id,
            "numero": self.numero,
            "client_nom": self.client_nom,
            "client_adresse": self.client_adresse,
            "client_email": self.client_email,
            "objet": self.objet,
            "montant_total_ht": str(self.montant_total_ht),
            "montant_total_ttc": str(self.montant_total_ttc),
            "retenue_garantie_pct": str(self.retenue_garantie_pct),
            "lots": [
                {
                    "code_lot": lot.code_lot,
                    "libelle": lot.libelle,
                    "montant_debourse_ht": str(lot.montant_debourse_ht),
                    "montant_vente_ht": str(lot.montant_vente_ht),
                }
                for lot in self.lots
            ],
            "commercial_id": self.commercial_id,
            "conducteur_id": self.conducteur_id,
            "date_conversion": self.date_conversion.isoformat(),
        }
