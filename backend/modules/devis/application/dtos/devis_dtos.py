"""DTOs pour les devis.

DEV-03: Creation devis structure.
DEV-08: Variantes et revisions.
DEV-15: Suivi statut devis.
DEV-22: Retenue de garantie.
DEV-TVA: Ventilation TVA multi-taux et mention TVA reduite.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

from .lot_dtos import LotDevisDTO
from ...domain.value_objects.retenue_garantie import RetenueGarantie, RetenueGarantieInvalideError

if TYPE_CHECKING:
    from ...domain.entities.devis import Devis


# DEV-TVA: Mention legale TVA reduite (reforme 01/2025, remplace CERFA 1300-SD/1301-SD)
MENTION_TVA_REDUITE = (
    "Le signataire atteste que les travaux vises portent sur un immeuble acheve "
    "depuis plus de deux ans a la date de commencement des travaux et sont affectes "
    "a l'habitation. Ces travaux ne repondent pas aux criteres d'exclusion prevus "
    "par la reglementation et remplissent les conditions d'application du taux "
    "reduit de TVA."
)


@dataclass
class VentilationTVADTO:
    """DEV-TVA: Ventilation TVA par taux applicable.

    Obligation legale: art. 242 nonies A du CGI - la facture doit mentionner
    par taux d'imposition le total HT et le montant de TVA correspondant.
    """

    taux: str          # "5.5", "10.0", "20.0"
    base_ht: str       # Montant HT soumis a ce taux
    montant_tva: str   # Montant TVA calcule

    def to_dict(self) -> dict:
        return {
            "taux": self.taux,
            "base_ht": self.base_ht,
            "montant_tva": self.montant_tva,
        }


@dataclass
class DevisCreateDTO:
    """DTO pour la creation d'un devis."""

    client_nom: str
    objet: str
    chantier_ref: Optional[str] = None
    client_adresse: Optional[str] = None
    client_email: Optional[str] = None
    client_telephone: Optional[str] = None
    date_validite: Optional[date] = None
    taux_tva_defaut: Decimal = Decimal("20")
    taux_marge_global: Decimal = Decimal("15")
    taux_marge_moe: Optional[Decimal] = None
    taux_marge_materiaux: Optional[Decimal] = None
    taux_marge_sous_traitance: Optional[Decimal] = None
    taux_marge_materiel: Optional[Decimal] = None
    taux_marge_deplacement: Optional[Decimal] = None
    coefficient_frais_generaux: Decimal = Decimal("12")
    retenue_garantie_pct: Decimal = Decimal("0")
    notes: Optional[str] = None
    commercial_id: Optional[int] = None
    conducteur_id: Optional[int] = None

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        # DEV-22: Validation stricte retenue de garantie
        try:
            RetenueGarantie(self.retenue_garantie_pct)
        except RetenueGarantieInvalideError as e:
            raise ValueError(str(e))


@dataclass
class DevisUpdateDTO:
    """DTO pour la mise a jour d'un devis."""

    client_nom: Optional[str] = None
    objet: Optional[str] = None
    chantier_ref: Optional[str] = None
    client_adresse: Optional[str] = None
    client_email: Optional[str] = None
    client_telephone: Optional[str] = None
    date_validite: Optional[date] = None
    taux_tva_defaut: Optional[Decimal] = None
    taux_marge_global: Optional[Decimal] = None
    taux_marge_moe: Optional[Decimal] = None
    taux_marge_materiaux: Optional[Decimal] = None
    taux_marge_sous_traitance: Optional[Decimal] = None
    taux_marge_materiel: Optional[Decimal] = None
    taux_marge_deplacement: Optional[Decimal] = None
    coefficient_frais_generaux: Optional[Decimal] = None
    retenue_garantie_pct: Optional[Decimal] = None
    notes: Optional[str] = None
    commercial_id: Optional[int] = None
    conducteur_id: Optional[int] = None

    def __post_init__(self) -> None:
        """Valide les donnees a la mise a jour."""
        # DEV-22: Validation stricte retenue de garantie (si fourni)
        if self.retenue_garantie_pct is not None:
            try:
                RetenueGarantie(self.retenue_garantie_pct)
            except RetenueGarantieInvalideError as e:
                raise ValueError(str(e))


@dataclass
class DevisDTO:
    """DTO de sortie resume pour un devis (liste)."""

    id: int
    numero: str
    client_nom: str
    objet: str
    statut: str
    montant_total_ht: str
    montant_total_ttc: str
    # DEV-22: Montants retenue de garantie
    retenue_garantie_pct: str
    montant_retenue_garantie: str
    montant_net_a_payer: str
    date_creation: Optional[str]
    date_validite: Optional[str]
    commercial_id: Optional[int]
    chantier_ref: Optional[str]
    # DEV-08: Versioning
    type_version: str = "originale"
    numero_version: int = 1
    version_figee: bool = False
    devis_parent_id: Optional[int] = None
    label_variante: Optional[str] = None

    @classmethod
    def from_entity(cls, devis: Devis) -> DevisDTO:
        """Cree un DTO resume depuis une entite Devis."""
        return cls(
            id=devis.id,
            numero=devis.numero,
            client_nom=devis.client_nom,
            objet=devis.objet,
            statut=devis.statut.value,
            montant_total_ht=str(devis.montant_total_ht),
            montant_total_ttc=str(devis.montant_total_ttc),
            retenue_garantie_pct=str(devis.retenue_garantie_pct),
            montant_retenue_garantie=str(devis.montant_retenue_garantie),
            montant_net_a_payer=str(devis.montant_net_a_payer),
            date_creation=devis.date_creation.isoformat() if devis.date_creation else None,
            date_validite=devis.date_validite.isoformat() if devis.date_validite else None,
            commercial_id=devis.commercial_id,
            chantier_ref=devis.chantier_ref,
            type_version=devis.type_version.value,
            numero_version=devis.numero_version,
            version_figee=devis.version_figee,
            devis_parent_id=devis.devis_parent_id,
            label_variante=devis.label_variante,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "numero": self.numero,
            "client_nom": self.client_nom,
            "objet": self.objet,
            "statut": self.statut,
            "montant_total_ht": self.montant_total_ht,
            "montant_total_ttc": self.montant_total_ttc,
            "retenue_garantie_pct": self.retenue_garantie_pct,
            "montant_retenue_garantie": self.montant_retenue_garantie,
            "montant_net_a_payer": self.montant_net_a_payer,
            "date_creation": self.date_creation,
            "date_validite": self.date_validite,
            "commercial_id": self.commercial_id,
            "chantier_ref": self.chantier_ref,
            "type_version": self.type_version,
            "numero_version": self.numero_version,
            "version_figee": self.version_figee,
            "devis_parent_id": self.devis_parent_id,
            "label_variante": self.label_variante,
        }


@dataclass
class DevisDetailDTO:
    """DTO de sortie detaille pour un devis (avec lots et lignes)."""

    id: int
    numero: str
    client_nom: str
    client_adresse: Optional[str]
    client_email: Optional[str]
    client_telephone: Optional[str]
    objet: str
    statut: str
    montant_total_ht: str
    montant_total_ttc: str
    taux_marge_global: str
    taux_marge_moe: Optional[str]
    taux_marge_materiaux: Optional[str]
    taux_marge_sous_traitance: Optional[str]
    taux_marge_materiel: Optional[str]
    taux_marge_deplacement: Optional[str]
    coefficient_frais_generaux: str
    retenue_garantie_pct: str
    montant_retenue_garantie: str
    montant_net_a_payer: str
    taux_tva_defaut: str
    date_creation: Optional[str]
    date_validite: Optional[str]
    updated_at: Optional[str]
    commercial_id: Optional[int]
    conducteur_id: Optional[int]
    chantier_ref: Optional[str]
    created_by: Optional[int]
    notes: Optional[str]
    conditions_generales: Optional[str]
    lots: List[LotDevisDTO]
    # DEV-08: Versioning
    type_version: str = "originale"
    numero_version: int = 1
    version_figee: bool = False
    version_figee_at: Optional[str] = None
    devis_parent_id: Optional[int] = None
    label_variante: Optional[str] = None
    version_commentaire: Optional[str] = None
    # DEV-TVA: Ventilation TVA multi-taux
    ventilation_tva: List[VentilationTVADTO] = field(default_factory=list)
    # DEV-TVA: Mention legale TVA reduite (reforme 01/2025)
    mention_tva_reduite: Optional[str] = None

    @classmethod
    def from_entity(
        cls,
        devis: Devis,
        lots: Optional[List[LotDevisDTO]] = None,
    ) -> DevisDetailDTO:
        """Cree un DTO detaille depuis une entite Devis."""
        return cls(
            id=devis.id,
            numero=devis.numero,
            client_nom=devis.client_nom,
            client_adresse=devis.client_adresse,
            client_email=devis.client_email,
            client_telephone=devis.client_telephone,
            objet=devis.objet,
            statut=devis.statut.value,
            montant_total_ht=str(devis.montant_total_ht),
            montant_total_ttc=str(devis.montant_total_ttc),
            taux_marge_global=str(devis.taux_marge_global),
            taux_marge_moe=str(devis.taux_marge_moe) if devis.taux_marge_moe is not None else None,
            taux_marge_materiaux=str(devis.taux_marge_materiaux) if devis.taux_marge_materiaux is not None else None,
            taux_marge_sous_traitance=str(devis.taux_marge_sous_traitance) if devis.taux_marge_sous_traitance is not None else None,
            taux_marge_materiel=str(devis.taux_marge_materiel) if devis.taux_marge_materiel is not None else None,
            taux_marge_deplacement=str(devis.taux_marge_deplacement) if devis.taux_marge_deplacement is not None else None,
            coefficient_frais_generaux=str(devis.coefficient_frais_generaux),
            retenue_garantie_pct=str(devis.retenue_garantie_pct),
            montant_retenue_garantie=str(devis.montant_retenue_garantie),
            montant_net_a_payer=str(devis.montant_net_a_payer),
            taux_tva_defaut=str(devis.taux_tva_defaut),
            date_creation=devis.date_creation.isoformat() if devis.date_creation else None,
            date_validite=devis.date_validite.isoformat() if devis.date_validite else None,
            updated_at=devis.updated_at.isoformat() if devis.updated_at else None,
            commercial_id=devis.commercial_id,
            conducteur_id=devis.conducteur_id,
            chantier_ref=devis.chantier_ref,
            created_by=devis.created_by,
            notes=devis.notes,
            conditions_generales=devis.conditions_generales,
            lots=lots or [],
            # DEV-08: Versioning
            type_version=devis.type_version.value,
            numero_version=devis.numero_version,
            version_figee=devis.version_figee,
            version_figee_at=devis.version_figee_at.isoformat() if devis.version_figee_at else None,
            devis_parent_id=devis.devis_parent_id,
            label_variante=devis.label_variante,
            version_commentaire=devis.version_commentaire,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "numero": self.numero,
            "client_nom": self.client_nom,
            "client_adresse": self.client_adresse,
            "client_email": self.client_email,
            "client_telephone": self.client_telephone,
            "objet": self.objet,
            "statut": self.statut,
            "montant_total_ht": self.montant_total_ht,
            "montant_total_ttc": self.montant_total_ttc,
            "taux_marge_global": self.taux_marge_global,
            "taux_marge_moe": self.taux_marge_moe,
            "taux_marge_materiaux": self.taux_marge_materiaux,
            "taux_marge_sous_traitance": self.taux_marge_sous_traitance,
            "taux_marge_materiel": self.taux_marge_materiel,
            "taux_marge_deplacement": self.taux_marge_deplacement,
            "coefficient_frais_generaux": self.coefficient_frais_generaux,
            "retenue_garantie_pct": self.retenue_garantie_pct,
            "montant_retenue_garantie": self.montant_retenue_garantie,
            "montant_net_a_payer": self.montant_net_a_payer,
            "taux_tva_defaut": self.taux_tva_defaut,
            "date_creation": self.date_creation,
            "date_validite": self.date_validite,
            "updated_at": self.updated_at,
            "commercial_id": self.commercial_id,
            "conducteur_id": self.conducteur_id,
            "chantier_ref": self.chantier_ref,
            "created_by": self.created_by,
            "notes": self.notes,
            "conditions_generales": self.conditions_generales,
            "lots": [l.to_dict() for l in self.lots],
            "type_version": self.type_version,
            "numero_version": self.numero_version,
            "version_figee": self.version_figee,
            "version_figee_at": self.version_figee_at,
            "devis_parent_id": self.devis_parent_id,
            "label_variante": self.label_variante,
            "version_commentaire": self.version_commentaire,
            "ventilation_tva": [v.to_dict() for v in self.ventilation_tva],
            "mention_tva_reduite": self.mention_tva_reduite,
        }


@dataclass
class DevisListDTO:
    """DTO pour la liste paginee de devis."""

    items: List[DevisDTO]
    total: int
    limit: int
    offset: int
