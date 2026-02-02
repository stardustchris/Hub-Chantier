"""DTOs pour les relances automatiques de devis.

DEV-24: Relances automatiques.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.relance_devis import RelanceDevis


@dataclass
class ConfigRelancesDTO:
    """DTO pour la configuration des relances d'un devis."""

    delais: List[int]
    actif: bool
    type_relance_defaut: str

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le DTO en dictionnaire."""
        return {
            "delais": self.delais,
            "actif": self.actif,
            "type_relance_defaut": self.type_relance_defaut,
        }


@dataclass
class UpdateConfigRelancesDTO:
    """DTO d'entree pour modifier la configuration des relances."""

    delais: Optional[List[int]] = None
    actif: Optional[bool] = None
    type_relance_defaut: Optional[str] = None


@dataclass
class PlanifierRelancesDTO:
    """DTO d'entree pour planifier les relances d'un devis."""

    message_personnalise: Optional[str] = None


@dataclass
class RelanceDTO:
    """DTO de sortie pour une relance de devis."""

    id: int
    devis_id: int
    numero_relance: int
    type_relance: str
    date_envoi: Optional[str]
    date_prevue: Optional[str]
    statut: str
    message_personnalise: Optional[str]
    created_at: Optional[str]

    @classmethod
    def from_entity(cls, relance: RelanceDevis) -> RelanceDTO:
        """Cree un DTO depuis une entite RelanceDevis.

        Args:
            relance: L'entite source.

        Returns:
            Le DTO correspondant.
        """
        return cls(
            id=relance.id,
            devis_id=relance.devis_id,
            numero_relance=relance.numero_relance,
            type_relance=relance.type_relance,
            date_envoi=(
                relance.date_envoi.isoformat() if relance.date_envoi else None
            ),
            date_prevue=(
                relance.date_prevue.isoformat() if relance.date_prevue else None
            ),
            statut=relance.statut,
            message_personnalise=relance.message_personnalise,
            created_at=(
                relance.created_at.isoformat() if relance.created_at else None
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "devis_id": self.devis_id,
            "numero_relance": self.numero_relance,
            "type_relance": self.type_relance,
            "date_envoi": self.date_envoi,
            "date_prevue": self.date_prevue,
            "statut": self.statut,
            "message_personnalise": self.message_personnalise,
            "created_at": self.created_at,
        }


@dataclass
class RelancesHistoriqueDTO:
    """DTO de sortie pour l'historique des relances d'un devis."""

    devis_id: int
    config: ConfigRelancesDTO
    relances: List[RelanceDTO]
    nb_planifiees: int
    nb_envoyees: int
    nb_annulees: int

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le DTO en dictionnaire."""
        return {
            "devis_id": self.devis_id,
            "config": self.config.to_dict(),
            "relances": [r.to_dict() for r in self.relances],
            "nb_planifiees": self.nb_planifiees,
            "nb_envoyees": self.nb_envoyees,
            "nb_annulees": self.nb_annulees,
        }


@dataclass
class ExecutionRelancesResultDTO:
    """DTO de sortie pour le resultat de l'execution batch des relances."""

    nb_relances_envoyees: int
    nb_erreurs: int
    details: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le DTO en dictionnaire."""
        return {
            "nb_relances_envoyees": self.nb_relances_envoyees,
            "nb_erreurs": self.nb_erreurs,
            "details": self.details,
        }
