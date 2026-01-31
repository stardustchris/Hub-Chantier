"""DTOs pour les achats.

FIN-05: Saisie achat - Formulaire de saisie des achats.
FIN-06: Suivi achat - Workflow de validation et suivi.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

from ...domain.value_objects import TypeAchat, StatutAchat, UniteMesure

if TYPE_CHECKING:
    from ...domain.entities import Achat


@dataclass
class AchatCreateDTO:
    """DTO pour la création d'un achat."""

    chantier_id: int
    libelle: str
    quantite: Decimal
    prix_unitaire_ht: Decimal
    fournisseur_id: Optional[int] = None
    lot_budgetaire_id: Optional[int] = None
    type_achat: TypeAchat = TypeAchat.MATERIAU
    unite: UniteMesure = UniteMesure.U
    taux_tva: Decimal = Decimal("20")
    date_commande: Optional[date] = None
    date_livraison_prevue: Optional[date] = None
    commentaire: Optional[str] = None


@dataclass
class AchatUpdateDTO:
    """DTO pour la mise à jour d'un achat.

    Seulement modifiable si le statut est 'demande'.
    """

    fournisseur_id: Optional[int] = None
    lot_budgetaire_id: Optional[int] = None
    type_achat: Optional[TypeAchat] = None
    libelle: Optional[str] = None
    quantite: Optional[Decimal] = None
    unite: Optional[UniteMesure] = None
    prix_unitaire_ht: Optional[Decimal] = None
    taux_tva: Optional[Decimal] = None
    date_commande: Optional[date] = None
    date_livraison_prevue: Optional[date] = None
    commentaire: Optional[str] = None


@dataclass
class AchatDTO:
    """DTO de sortie pour un achat.

    Inclut les montants calculés et les informations enrichies.
    """

    id: int
    chantier_id: int
    fournisseur_id: Optional[int]
    fournisseur_nom: Optional[str]
    lot_budgetaire_id: Optional[int]
    lot_code: Optional[str]
    chantier_nom: Optional[str]
    type_achat: str
    type_achat_label: str
    libelle: str
    quantite: str
    unite: str
    unite_label: str
    prix_unitaire_ht: str
    taux_tva: str
    total_ht: str
    montant_tva: str
    total_ttc: str
    date_commande: Optional[str]
    date_livraison_prevue: Optional[str]
    statut: str
    statut_label: str
    statut_couleur: str
    numero_facture: Optional[str]
    motif_refus: Optional[str]
    commentaire: Optional[str]
    demandeur_id: Optional[int]
    demandeur_nom: Optional[str]
    valideur_id: Optional[int]
    valideur_nom: Optional[str]
    validated_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[int]

    @classmethod
    def from_entity(
        cls,
        achat: Achat,
        fournisseur_nom: Optional[str] = None,
        chantier_nom: Optional[str] = None,
        lot_code: Optional[str] = None,
        demandeur_nom: Optional[str] = None,
        valideur_nom: Optional[str] = None,
    ) -> AchatDTO:
        """Crée un DTO depuis une entité Achat.

        Args:
            achat: L'entité Achat source.
            fournisseur_nom: Nom du fournisseur (enrichissement).
            chantier_nom: Nom du chantier (enrichissement).
            lot_code: Code du lot budgétaire (enrichissement).
            demandeur_nom: Nom du demandeur (enrichissement).
            valideur_nom: Nom du valideur (enrichissement).

        Returns:
            Le DTO de sortie.
        """
        return cls(
            id=achat.id,
            chantier_id=achat.chantier_id,
            fournisseur_id=achat.fournisseur_id,
            fournisseur_nom=fournisseur_nom,
            lot_budgetaire_id=achat.lot_budgetaire_id,
            lot_code=lot_code,
            chantier_nom=chantier_nom,
            type_achat=achat.type_achat.value,
            type_achat_label=achat.type_achat.label,
            libelle=achat.libelle,
            quantite=str(achat.quantite),
            unite=achat.unite.value,
            unite_label=achat.unite.label,
            prix_unitaire_ht=str(achat.prix_unitaire_ht),
            taux_tva=str(achat.taux_tva),
            total_ht=str(achat.total_ht),
            montant_tva=str(achat.montant_tva),
            total_ttc=str(achat.total_ttc),
            date_commande=achat.date_commande.isoformat()
            if achat.date_commande
            else None,
            date_livraison_prevue=achat.date_livraison_prevue.isoformat()
            if achat.date_livraison_prevue
            else None,
            statut=achat.statut.value,
            statut_label=achat.statut.label,
            statut_couleur=achat.statut.couleur,
            numero_facture=achat.numero_facture,
            motif_refus=achat.motif_refus,
            commentaire=achat.commentaire,
            demandeur_id=achat.demandeur_id,
            demandeur_nom=demandeur_nom,
            valideur_id=achat.valideur_id,
            valideur_nom=valideur_nom,
            validated_at=achat.validated_at,
            created_at=achat.created_at,
            updated_at=achat.updated_at,
            created_by=achat.created_by,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "chantier_id": self.chantier_id,
            "fournisseur_id": self.fournisseur_id,
            "fournisseur_nom": self.fournisseur_nom,
            "lot_budgetaire_id": self.lot_budgetaire_id,
            "lot_code": self.lot_code,
            "chantier_nom": self.chantier_nom,
            "type_achat": self.type_achat,
            "type_achat_label": self.type_achat_label,
            "libelle": self.libelle,
            "quantite": self.quantite,
            "unite": self.unite,
            "unite_label": self.unite_label,
            "prix_unitaire_ht": self.prix_unitaire_ht,
            "taux_tva": self.taux_tva,
            "total_ht": self.total_ht,
            "montant_tva": self.montant_tva,
            "total_ttc": self.total_ttc,
            "date_commande": self.date_commande,
            "date_livraison_prevue": self.date_livraison_prevue,
            "statut": self.statut,
            "statut_label": self.statut_label,
            "statut_couleur": self.statut_couleur,
            "numero_facture": self.numero_facture,
            "motif_refus": self.motif_refus,
            "commentaire": self.commentaire,
            "demandeur_id": self.demandeur_id,
            "demandeur_nom": self.demandeur_nom,
            "valideur_id": self.valideur_id,
            "valideur_nom": self.valideur_nom,
            "validated_at": self.validated_at.isoformat()
            if self.validated_at
            else None,
            "created_at": self.created_at.isoformat()
            if self.created_at
            else None,
            "updated_at": self.updated_at.isoformat()
            if self.updated_at
            else None,
            "created_by": self.created_by,
        }


@dataclass
class AchatListDTO:
    """DTO pour une liste paginée d'achats."""

    items: List[AchatDTO]
    total: int
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        """Indique s'il y a plus de résultats."""
        return self.offset + len(self.items) < self.total


@dataclass
class AchatValidationDTO:
    """DTO pour la validation d'un achat."""

    achat_id: int


@dataclass
class AchatRefusDTO:
    """DTO pour le refus d'un achat."""

    achat_id: int
    motif: str
