"""DTOs pour les versions et comparatifs de devis.

DEV-08: Variantes et revisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.devis import Devis
    from ...domain.entities.comparatif_devis import ComparatifDevis
    from ...domain.entities.comparatif_ligne import ComparatifLigne


@dataclass
class CreerRevisionDTO:
    """DTO d'entree pour creer une revision d'un devis."""

    commentaire: Optional[str] = None


@dataclass
class CreerVarianteDTO:
    """DTO d'entree pour creer une variante d'un devis."""

    label_variante: str = ""
    commentaire: Optional[str] = None


@dataclass
class FigerVersionDTO:
    """DTO d'entree pour figer une version de devis."""

    commentaire: Optional[str] = None


@dataclass
class VersionDTO:
    """DTO de sortie pour une version de devis (resume)."""

    id: int
    numero: str
    type_version: str
    numero_version: int
    label_variante: Optional[str]
    version_figee: bool
    version_figee_at: Optional[str]
    statut: str
    montant_total_ht: str
    montant_total_ttc: str
    devis_parent_id: Optional[int]
    version_commentaire: Optional[str]
    date_creation: Optional[str]

    @classmethod
    def from_entity(cls, devis: Devis) -> VersionDTO:
        """Cree un DTO version depuis une entite Devis."""
        return cls(
            id=devis.id,
            numero=devis.numero,
            type_version=devis.type_version.value,
            numero_version=devis.numero_version,
            label_variante=devis.label_variante,
            version_figee=devis.version_figee,
            version_figee_at=(
                devis.version_figee_at.isoformat()
                if devis.version_figee_at
                else None
            ),
            statut=devis.statut.value,
            montant_total_ht=str(devis.montant_total_ht),
            montant_total_ttc=str(devis.montant_total_ttc),
            devis_parent_id=devis.devis_parent_id,
            version_commentaire=devis.version_commentaire,
            date_creation=(
                devis.date_creation.isoformat()
                if devis.date_creation
                else None
            ),
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "numero": self.numero,
            "type_version": self.type_version,
            "numero_version": self.numero_version,
            "label_variante": self.label_variante,
            "version_figee": self.version_figee,
            "version_figee_at": self.version_figee_at,
            "statut": self.statut,
            "montant_total_ht": self.montant_total_ht,
            "montant_total_ttc": self.montant_total_ttc,
            "devis_parent_id": self.devis_parent_id,
            "version_commentaire": self.version_commentaire,
            "date_creation": self.date_creation,
        }


@dataclass
class ComparatifLigneDTO:
    """DTO de sortie pour une ligne de comparatif."""

    id: int
    type_ecart: str
    lot_titre: str
    designation: str
    article_id: Optional[int]
    source_quantite: Optional[str]
    source_prix_unitaire: Optional[str]
    source_montant_ht: Optional[str]
    source_debourse_sec: Optional[str]
    cible_quantite: Optional[str]
    cible_prix_unitaire: Optional[str]
    cible_montant_ht: Optional[str]
    cible_debourse_sec: Optional[str]
    ecart_quantite: Optional[str]
    ecart_prix_unitaire: Optional[str]
    ecart_montant_ht: Optional[str]
    ecart_debourse_sec: Optional[str]

    @classmethod
    def from_entity(cls, ligne: ComparatifLigne) -> ComparatifLigneDTO:
        """Cree un DTO depuis une entite ComparatifLigne."""
        return cls(
            id=ligne.id,
            type_ecart=ligne.type_ecart.value,
            lot_titre=ligne.lot_titre,
            designation=ligne.designation,
            article_id=ligne.article_id,
            source_quantite=str(ligne.source_quantite) if ligne.source_quantite is not None else None,
            source_prix_unitaire=str(ligne.source_prix_unitaire) if ligne.source_prix_unitaire is not None else None,
            source_montant_ht=str(ligne.source_montant_ht) if ligne.source_montant_ht is not None else None,
            source_debourse_sec=str(ligne.source_debourse_sec) if ligne.source_debourse_sec is not None else None,
            cible_quantite=str(ligne.cible_quantite) if ligne.cible_quantite is not None else None,
            cible_prix_unitaire=str(ligne.cible_prix_unitaire) if ligne.cible_prix_unitaire is not None else None,
            cible_montant_ht=str(ligne.cible_montant_ht) if ligne.cible_montant_ht is not None else None,
            cible_debourse_sec=str(ligne.cible_debourse_sec) if ligne.cible_debourse_sec is not None else None,
            ecart_quantite=str(ligne.ecart_quantite) if ligne.ecart_quantite is not None else None,
            ecart_prix_unitaire=str(ligne.ecart_prix_unitaire) if ligne.ecart_prix_unitaire is not None else None,
            ecart_montant_ht=str(ligne.ecart_montant_ht) if ligne.ecart_montant_ht is not None else None,
            ecart_debourse_sec=str(ligne.ecart_debourse_sec) if ligne.ecart_debourse_sec is not None else None,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "type_ecart": self.type_ecart,
            "lot_titre": self.lot_titre,
            "designation": self.designation,
            "article_id": self.article_id,
            "source_quantite": self.source_quantite,
            "source_prix_unitaire": self.source_prix_unitaire,
            "source_montant_ht": self.source_montant_ht,
            "source_debourse_sec": self.source_debourse_sec,
            "cible_quantite": self.cible_quantite,
            "cible_prix_unitaire": self.cible_prix_unitaire,
            "cible_montant_ht": self.cible_montant_ht,
            "cible_debourse_sec": self.cible_debourse_sec,
            "ecart_quantite": self.ecart_quantite,
            "ecart_prix_unitaire": self.ecart_prix_unitaire,
            "ecart_montant_ht": self.ecart_montant_ht,
            "ecart_debourse_sec": self.ecart_debourse_sec,
        }


@dataclass
class ComparatifDTO:
    """DTO de sortie pour un comparatif complet."""

    id: int
    devis_source_id: int
    devis_cible_id: int
    ecart_montant_ht: str
    ecart_montant_ttc: str
    ecart_marge_pct: str
    ecart_debourse_total: str
    nb_lignes_ajoutees: int
    nb_lignes_supprimees: int
    nb_lignes_modifiees: int
    nb_lignes_identiques: int
    nb_lignes_total: int
    a_des_ecarts: bool
    lignes: List[ComparatifLigneDTO]
    genere_par: Optional[int]
    created_at: Optional[str]

    @classmethod
    def from_entity(cls, comparatif: ComparatifDevis) -> ComparatifDTO:
        """Cree un DTO depuis une entite ComparatifDevis."""
        return cls(
            id=comparatif.id,
            devis_source_id=comparatif.devis_source_id,
            devis_cible_id=comparatif.devis_cible_id,
            ecart_montant_ht=str(comparatif.ecart_montant_ht),
            ecart_montant_ttc=str(comparatif.ecart_montant_ttc),
            ecart_marge_pct=str(comparatif.ecart_marge_pct),
            ecart_debourse_total=str(comparatif.ecart_debourse_total),
            nb_lignes_ajoutees=comparatif.nb_lignes_ajoutees,
            nb_lignes_supprimees=comparatif.nb_lignes_supprimees,
            nb_lignes_modifiees=comparatif.nb_lignes_modifiees,
            nb_lignes_identiques=comparatif.nb_lignes_identiques,
            nb_lignes_total=comparatif.nb_lignes_total,
            a_des_ecarts=comparatif.a_des_ecarts,
            lignes=[ComparatifLigneDTO.from_entity(l) for l in comparatif.lignes],
            genere_par=comparatif.genere_par,
            created_at=(
                comparatif.created_at.isoformat()
                if comparatif.created_at
                else None
            ),
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "devis_source_id": self.devis_source_id,
            "devis_cible_id": self.devis_cible_id,
            "ecart_montant_ht": self.ecart_montant_ht,
            "ecart_montant_ttc": self.ecart_montant_ttc,
            "ecart_marge_pct": self.ecart_marge_pct,
            "ecart_debourse_total": self.ecart_debourse_total,
            "nb_lignes_ajoutees": self.nb_lignes_ajoutees,
            "nb_lignes_supprimees": self.nb_lignes_supprimees,
            "nb_lignes_modifiees": self.nb_lignes_modifiees,
            "nb_lignes_identiques": self.nb_lignes_identiques,
            "nb_lignes_total": self.nb_lignes_total,
            "a_des_ecarts": self.a_des_ecarts,
            "lignes": [l.to_dict() for l in self.lignes],
            "genere_par": self.genere_par,
            "created_at": self.created_at,
        }
