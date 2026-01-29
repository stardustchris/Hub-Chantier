"""DTOs pour les signalements."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities import Signalement


@dataclass
class SignalementDTO:
    """DTO représentant un signalement."""

    id: int
    chantier_id: int
    titre: str
    description: str
    priorite: str
    priorite_label: str
    priorite_couleur: str
    statut: str
    statut_label: str
    statut_couleur: str
    cree_par: int
    cree_par_nom: Optional[str]
    assigne_a: Optional[int]
    assigne_a_nom: Optional[str]
    date_resolution_souhaitee: Optional[datetime]
    date_traitement: Optional[datetime]
    date_cloture: Optional[datetime]
    commentaire_traitement: Optional[str]
    photo_url: Optional[str]
    localisation: Optional[str]
    created_at: datetime
    updated_at: datetime
    est_en_retard: bool
    temps_restant: Optional[str]
    pourcentage_temps: float
    nb_reponses: int
    nb_escalades: int

    @classmethod
    def from_entity(
        cls,
        entity: Signalement,
        nb_reponses: int = 0,
        get_user_name: Optional[Callable[[int], Optional[str]]] = None,
    ) -> SignalementDTO:
        """Convertit une entité Signalement en DTO.

        Args:
            entity: L'entité Signalement source.
            nb_reponses: Nombre de réponses associées.
            get_user_name: Fonction optionnelle pour résoudre les noms d'utilisateurs.

        Returns:
            Le DTO correspondant.
        """
        cree_par_nom = None
        assigne_a_nom = None
        if get_user_name:
            cree_par_nom = get_user_name(entity.cree_par)
            if entity.assigne_a:
                assigne_a_nom = get_user_name(entity.assigne_a)

        return cls(
            id=entity.id,  # type: ignore
            chantier_id=entity.chantier_id,
            titre=entity.titre,
            description=entity.description,
            priorite=entity.priorite.value,
            priorite_label=entity.priorite.label,
            priorite_couleur=entity.priorite.couleur,
            statut=entity.statut.value,
            statut_label=entity.statut.label,
            statut_couleur=entity.statut.couleur,
            cree_par=entity.cree_par,
            cree_par_nom=cree_par_nom,
            assigne_a=entity.assigne_a,
            assigne_a_nom=assigne_a_nom,
            date_resolution_souhaitee=entity.date_resolution_souhaitee,
            date_traitement=entity.date_traitement,
            date_cloture=entity.date_cloture,
            commentaire_traitement=entity.commentaire_traitement,
            photo_url=entity.photo_url,
            localisation=entity.localisation,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            est_en_retard=entity.est_en_retard,
            temps_restant=entity.temps_restant_formatte if not entity.statut.est_resolu else None,
            pourcentage_temps=entity.pourcentage_temps_ecoule,
            nb_reponses=nb_reponses,
            nb_escalades=entity.nb_escalades,
        )


@dataclass
class SignalementCreateDTO:
    """DTO pour la création d'un signalement."""

    chantier_id: int
    titre: str
    description: str
    cree_par: int
    priorite: str = "moyenne"
    assigne_a: Optional[int] = None
    date_resolution_souhaitee: Optional[datetime] = None
    photo_url: Optional[str] = None
    localisation: Optional[str] = None


@dataclass
class SignalementUpdateDTO:
    """DTO pour la mise à jour d'un signalement."""

    titre: Optional[str] = None
    description: Optional[str] = None
    priorite: Optional[str] = None
    assigne_a: Optional[int] = None
    date_resolution_souhaitee: Optional[datetime] = None
    photo_url: Optional[str] = None
    localisation: Optional[str] = None


@dataclass
class SignalementListDTO:
    """DTO pour la liste de signalements avec pagination."""

    signalements: List[SignalementDTO]
    total: int
    skip: int
    limit: int


@dataclass
class SignalementSearchDTO:
    """DTO pour la recherche de signalements (SIG-10, SIG-19, SIG-20)."""

    query: Optional[str] = None
    chantier_id: Optional[int] = None
    chantier_ids: Optional[List[int]] = None
    statut: Optional[str] = None
    priorite: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    cree_par: Optional[int] = None
    assigne_a: Optional[int] = None
    en_retard_only: bool = False
    skip: int = 0
    limit: int = 100


@dataclass
class SignalementStatsDTO:
    """DTO pour les statistiques des signalements (SIG-18)."""

    total: int
    par_statut: dict
    par_priorite: dict
    en_retard: int
    traites_cette_semaine: int
    temps_moyen_resolution: Optional[float]  # en heures
    taux_resolution: float  # pourcentage
