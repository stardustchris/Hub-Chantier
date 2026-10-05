"""Routes d'administration de la synchronisation des heures avec Costructor."""

import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from shared.infrastructure.config import settings
from shared.infrastructure.database import get_db
from shared.infrastructure.web.dependencies import get_current_user_role

from ...domain.entities import StatutSynchronisation
from ..paie_externe import synchronisation
from ..persistence import (
    SQLAlchemyCorrespondanceExterneRepository,
    SQLAlchemySynchronisationPaieRepository,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/paie-externe", tags=["Paie externe (Costructor)"])

TypeEntite = Literal["utilisateur", "chantier"]


class CorrespondanceRequest(BaseModel):
    """Associe un compagnon ou un chantier a son identifiant Costructor."""

    type_entite: TypeEntite
    entite_id: int = Field(..., gt=0)
    identifiant_externe: str = Field(..., min_length=1, max_length=100)


class EnvoiRequest(BaseModel):
    """Pointages a envoyer explicitement (ex. heures validees avant l'activation)."""

    pointage_ids: list[int] = Field(..., min_length=1, max_length=1000)


def _exiger_actif() -> None:
    if not synchronisation.synchronisation_active():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Synchronisation Costructor désactivée : "
                   "définissez COSTRUCTOR_SYNC_ENABLED et COSTRUCTOR_API_KEY.",
        )


def _rapport(rapport) -> dict:
    return {
        "envoyes": rapport.envoyes,
        "deja_envoyes": rapport.deja_envoyes,
        "ignores": rapport.ignores,
        "erreurs": rapport.erreurs,
        "non_valides": rapport.non_valides,
    }


def _exiger_role(user_role: str, roles: tuple[str, ...]) -> None:
    if user_role not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé : " + ", ".join(roles),
        )


@router.get("/statut")
def statut_synchronisation(user_role: str = Depends(get_current_user_role)) -> dict:
    """Indique si l'envoi vers Costructor est actif, et avec quels horaires."""
    _exiger_role(user_role, ("admin", "conducteur"))
    return {
        "systeme": "costructor",
        "active": synchronisation.synchronisation_active(),
        "horaires": {
            "debut": settings.PAIE_HEURE_DEBUT,
            "pause_debut": settings.PAIE_PAUSE_DEBUT,
            "pause_fin": settings.PAIE_PAUSE_FIN,
        },
    }


@router.get("/synchronisations")
def lister_synchronisations(
    statut: Literal["envoye", "erreur", "ignore"] | None = Query(None),
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Liste les envois de pointages, filtrables par statut."""
    _exiger_role(user_role, ("admin", "conducteur"))
    statuts = [StatutSynchronisation(statut)] if statut else list(StatutSynchronisation)
    suivis = SQLAlchemySynchronisationPaieRepository(db).find_by_statuts(statuts)
    return [
        {
            "pointage_id": s.pointage_id,
            "statut": s.statut.value,
            "saisies_externes": s.saisies_externes,
            "message": s.message,
            "tentatives": s.tentatives,
            "derniere_tentative": s.derniere_tentative,
        }
        for s in suivis
    ]


@router.post("/synchronisations/relancer")
def relancer_synchronisations(user_role: str = Depends(get_current_user_role)) -> dict:
    """Renvoie les pointages en erreur et ceux ignores (correspondance ajoutee depuis)."""
    _exiger_role(user_role, ("admin", "conducteur"))
    _exiger_actif()
    return _rapport(synchronisation.synchroniser(None))


@router.post("/synchronisations/envoyer")
def envoyer_pointages(
    request: EnvoiRequest,
    user_role: str = Depends(get_current_user_role),
) -> dict:
    """Envoie des pointages precis, par exemple ceux valides avant l'activation.

    Sans risque de doublon : un pointage deja envoye est ignore, un pointage
    non valide n'est pas envoye.
    """
    _exiger_role(user_role, ("admin", "conducteur"))
    _exiger_actif()
    return _rapport(synchronisation.synchroniser(request.pointage_ids))


@router.get("/correspondances")
def lister_correspondances(
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Liste les identifiants Costructor des compagnons et chantiers."""
    _exiger_role(user_role, ("admin",))
    return [
        {"type_entite": t, "entite_id": i, "identifiant_externe": e}
        for t, i, e in SQLAlchemyCorrespondanceExterneRepository(db).lister()
    ]


@router.put("/correspondances", status_code=status.HTTP_204_NO_CONTENT)
def definir_correspondance(
    request: CorrespondanceRequest,
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db),
) -> None:
    """Associe un compagnon ou un chantier a son identifiant Costructor."""
    _exiger_role(user_role, ("admin",))
    SQLAlchemyCorrespondanceExterneRepository(db).definir(
        request.type_entite, request.entite_id, request.identifiant_externe.strip()
    )


@router.delete(
    "/correspondances/{type_entite}/{entite_id}", status_code=status.HTTP_204_NO_CONTENT
)
def supprimer_correspondance(
    type_entite: TypeEntite,
    entite_id: int,
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db),
) -> None:
    """Supprime la correspondance d'un compagnon ou d'un chantier."""
    _exiger_role(user_role, ("admin",))
    SQLAlchemyCorrespondanceExterneRepository(db).supprimer(type_entite, entite_id)
