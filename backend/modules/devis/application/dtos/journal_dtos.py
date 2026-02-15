"""DTOs pour le journal d'audit des devis.

DEV-18: Historique modifications - Avec suivi avant/apres.
"""

from __future__ import annotations

import json

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.journal_devis import JournalDevis


@dataclass
class ChangementDTO:
    """DTO pour un changement individuel de champ (DEV-18).

    Attributes:
        champ: Le nom du champ modifie.
        avant: La valeur avant modification.
        apres: La valeur apres modification.
    """

    champ: str
    avant: Optional[str]
    apres: Optional[str]

    def to_dict(self) -> dict:
        return {
            "champ": self.champ,
            "avant": self.avant,
            "apres": self.apres,
        }


@dataclass
class JournalDevisDTO:
    """DTO de sortie pour une entree du journal devis.

    DEV-18: Inclut desormais les changements detailles (avant/apres)
    et les transitions de statut quand disponibles.
    """

    id: int
    devis_id: int
    action: str
    details: Optional[str]
    auteur_id: Optional[int]
    created_at: Optional[str]
    # DEV-18: Donnees structurees supplementaires
    changements: List[ChangementDTO] = field(default_factory=list)
    ancien_statut: Optional[str] = None
    nouveau_statut: Optional[str] = None
    motif: Optional[str] = None
    type_modification: Optional[str] = None

    @classmethod
    def from_entity(cls, journal: JournalDevis) -> JournalDevisDTO:
        """Cree un DTO depuis une entite JournalDevis.

        DEV-18: Extrait les changements avant/apres et les transitions
        de statut du details_json structure.
        """
        details_str: Optional[str] = None
        changements: List[ChangementDTO] = []
        ancien_statut: Optional[str] = None
        nouveau_statut: Optional[str] = None
        motif: Optional[str] = None
        type_modification: Optional[str] = None

        if journal.details_json is not None:
            dj = journal.details_json

            # Message lisible
            if "message" in dj:
                details_str = dj["message"]
            else:
                details_str = json.dumps(dj, ensure_ascii=False)

            # DEV-18: Extraire les changements avant/apres
            if "changements" in dj and isinstance(dj["changements"], dict):
                for champ, valeurs in dj["changements"].items():
                    changements.append(
                        ChangementDTO(
                            champ=champ,
                            avant=valeurs.get("avant"),
                            apres=valeurs.get("apres"),
                        )
                    )

            # DEV-15/18: Extraire transition de statut
            ancien_statut = dj.get("ancien_statut")
            nouveau_statut = dj.get("nouveau_statut")
            motif = dj.get("motif")
            type_modification = dj.get("type_modification")

        return cls(
            id=journal.id,
            devis_id=journal.devis_id,
            action=journal.action,
            details=details_str,
            auteur_id=journal.auteur_id,
            created_at=journal.created_at.isoformat() if journal.created_at else None,
            changements=changements,
            ancien_statut=ancien_statut,
            nouveau_statut=nouveau_statut,
            motif=motif,
            type_modification=type_modification,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        result = {
            "id": self.id,
            "devis_id": self.devis_id,
            "action": self.action,
            "details": self.details,
            "auteur_id": self.auteur_id,
            "created_at": self.created_at,
        }

        # DEV-18: Inclure les changements si presents
        if self.changements:
            result["changements"] = [c.to_dict() for c in self.changements]

        # DEV-15/18: Inclure la transition de statut si presente
        if self.ancien_statut:
            result["ancien_statut"] = self.ancien_statut
        if self.nouveau_statut:
            result["nouveau_statut"] = self.nouveau_statut
        if self.motif:
            result["motif"] = self.motif
        if self.type_modification:
            result["type_modification"] = self.type_modification

        return result
