"""DTOs pour les pieces jointes de devis.

DEV-07: Insertion multimedia.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PieceJointeCreateDTO:
    """DTO pour creer une piece jointe."""

    devis_id: int
    document_id: int
    visible_client: bool = True
    lot_devis_id: Optional[int] = None
    ligne_devis_id: Optional[int] = None


@dataclass
class PieceJointeDTO:
    """DTO de sortie pour une piece jointe."""

    id: int
    devis_id: int
    document_id: Optional[int]
    lot_devis_id: Optional[int]
    ligne_devis_id: Optional[int]
    visible_client: bool
    ordre: int
    nom_fichier: Optional[str]
    type_fichier: Optional[str]
    taille_octets: Optional[int]
    mime_type: Optional[str]
    created_at: Optional[str]

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire pour serialisation JSON."""
        return {
            "id": self.id,
            "devis_id": self.devis_id,
            "document_id": self.document_id,
            "lot_devis_id": self.lot_devis_id,
            "ligne_devis_id": self.ligne_devis_id,
            "visible_client": self.visible_client,
            "ordre": self.ordre,
            "nom_fichier": self.nom_fichier,
            "type_fichier": self.type_fichier,
            "taille_octets": self.taille_octets,
            "mime_type": self.mime_type,
            "created_at": self.created_at,
        }
