"""DTOs pour les feuilles de taches."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from ...domain.entities import FeuilleTache
from ...domain.entities.feuille_tache import StatutValidation


@dataclass
class FeuilleTacheDTO:
    """DTO pour representer une feuille de tache (TAC-18)."""

    id: int
    tache_id: int
    utilisateur_id: int
    chantier_id: int
    date_travail: str
    heures_travaillees: float
    quantite_realisee: float
    commentaire: Optional[str]
    statut_validation: str
    statut_display: str
    est_validee: bool
    est_en_attente: bool
    est_rejetee: bool
    validateur_id: Optional[int]
    date_validation: Optional[datetime]
    motif_rejet: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, feuille: FeuilleTache) -> "FeuilleTacheDTO":
        """Convertit une entite FeuilleTache en DTO."""
        statut_display_mapping = {
            StatutValidation.EN_ATTENTE: "En attente",
            StatutValidation.VALIDEE: "Validee",
            StatutValidation.REJETEE: "Rejetee",
        }

        return cls(
            id=feuille.id,
            tache_id=feuille.tache_id,
            utilisateur_id=feuille.utilisateur_id,
            chantier_id=feuille.chantier_id,
            date_travail=feuille.date_travail.isoformat(),
            heures_travaillees=feuille.heures_travaillees,
            quantite_realisee=feuille.quantite_realisee,
            commentaire=feuille.commentaire,
            statut_validation=feuille.statut_validation.value,
            statut_display=statut_display_mapping.get(
                feuille.statut_validation, feuille.statut_validation.value
            ),
            est_validee=feuille.est_validee,
            est_en_attente=feuille.est_en_attente,
            est_rejetee=feuille.est_rejetee,
            validateur_id=feuille.validateur_id,
            date_validation=feuille.date_validation,
            motif_rejet=feuille.motif_rejet,
            created_at=feuille.created_at,
            updated_at=feuille.updated_at,
        )


@dataclass
class CreateFeuilleTacheDTO:
    """DTO pour la creation d'une feuille de tache (TAC-18)."""

    tache_id: int
    utilisateur_id: int
    chantier_id: int
    date_travail: str  # Format ISO: YYYY-MM-DD
    heures_travaillees: float = 0.0
    quantite_realisee: float = 0.0
    commentaire: Optional[str] = None


@dataclass
class UpdateFeuilleTacheDTO:
    """DTO pour la mise a jour d'une feuille de tache."""

    heures_travaillees: Optional[float] = None
    quantite_realisee: Optional[float] = None
    commentaire: Optional[str] = None


@dataclass
class ValidateFeuilleTacheDTO:
    """DTO pour la validation/rejet d'une feuille (TAC-19)."""

    validateur_id: int
    valider: bool  # True = valider, False = rejeter
    motif_rejet: Optional[str] = None  # Requis si valider = False


@dataclass
class FeuilleTacheListDTO:
    """DTO pour une liste paginee de feuilles de taches."""

    items: List[FeuilleTacheDTO]
    total: int
    page: int
    size: int
    pages: int
    total_heures: float = 0.0
    total_quantite: float = 0.0
