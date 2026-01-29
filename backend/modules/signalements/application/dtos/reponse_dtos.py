"""DTOs pour les réponses aux signalements."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities import Reponse


@dataclass
class ReponseDTO:
    """DTO représentant une réponse."""

    id: int
    signalement_id: int
    contenu: str
    auteur_id: int
    auteur_nom: Optional[str]
    photo_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    est_resolution: bool

    @classmethod
    def from_entity(
        cls,
        entity: Reponse,
        get_user_name: Optional[Callable[[int], Optional[str]]] = None,
    ) -> ReponseDTO:
        """Convertit une entité Reponse en DTO.

        Args:
            entity: L'entité Reponse source.
            get_user_name: Fonction optionnelle pour résoudre les noms d'utilisateurs.

        Returns:
            Le DTO correspondant.
        """
        auteur_nom = None
        if get_user_name:
            auteur_nom = get_user_name(entity.auteur_id)

        return cls(
            id=entity.id,  # type: ignore
            signalement_id=entity.signalement_id,
            contenu=entity.contenu,
            auteur_id=entity.auteur_id,
            auteur_nom=auteur_nom,
            photo_url=entity.photo_url,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            est_resolution=entity.est_resolution,
        )


@dataclass
class ReponseCreateDTO:
    """DTO pour la création d'une réponse."""

    signalement_id: int
    contenu: str
    auteur_id: int
    photo_url: Optional[str] = None
    est_resolution: bool = False


@dataclass
class ReponseUpdateDTO:
    """DTO pour la mise à jour d'une réponse."""

    contenu: Optional[str] = None
    photo_url: Optional[str] = None


@dataclass
class ReponseListDTO:
    """DTO pour la liste de réponses avec pagination."""

    reponses: List[ReponseDTO]
    total: int
    skip: int
    limit: int
