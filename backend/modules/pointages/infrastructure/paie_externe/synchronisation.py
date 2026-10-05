"""Assemblage et declenchement de la synchronisation des heures vers Costructor."""

import logging
from collections.abc import Iterable

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from shared.infrastructure.config import settings
from shared.infrastructure.database import SessionLocal

from ...application.ports import ClientPaieExternePort
from ...application.use_cases.synchroniser_heures_paie import (
    RapportSynchronisation,
    SynchroniserHeuresPaieUseCase,
)
from ...domain.services import HorairesReference
from ..persistence import (
    SQLAlchemyCorrespondanceExterneRepository,
    SQLAlchemyPointageRepository,
    SQLAlchemySynchronisationPaieRepository,
)
from .costructor_client import CostructorClient

logger = logging.getLogger(__name__)


def synchronisation_active() -> bool:
    """La synchronisation est activee et une cle d'API est configuree."""
    return settings.COSTRUCTOR_SYNC_ENABLED and bool(settings.COSTRUCTOR_API_KEY.strip())


def horaires_reference() -> HorairesReference:
    """Horaires de reference de l'entreprise, issus de la configuration."""
    return HorairesReference.depuis_texte(
        settings.PAIE_HEURE_DEBUT, settings.PAIE_PAUSE_DEBUT, settings.PAIE_PAUSE_FIN
    )


def construire_client() -> CostructorClient:
    """Client Costructor configure."""
    return CostructorClient(settings.COSTRUCTOR_API_KEY, base_url=settings.COSTRUCTOR_API_URL)


def construire_use_case(
    session: Session, client: ClientPaieExternePort
) -> SynchroniserHeuresPaieUseCase:
    """Assemble le use case de synchronisation sur une session donnee."""
    return SynchroniserHeuresPaieUseCase(
        pointage_repo=SQLAlchemyPointageRepository(session),
        synchronisation_repo=SQLAlchemySynchronisationPaieRepository(session),
        correspondance_repo=SQLAlchemyCorrespondanceExterneRepository(session),
        client=client,
        horaires=horaires_reference(),
    )


def synchroniser(pointage_ids: list[int] | None = None) -> RapportSynchronisation:
    """Envoie des pointages (ou relance les echecs si aucun n'est donne).

    Ouvre sa propre session : appele en arriere-plan, apres la fin de la
    requete HTTP qui a valide les heures.

    Args:
        pointage_ids: Pointages a envoyer ; None pour relancer erreurs et ignores.

    Returns:
        Le bilan de l'envoi.
    """
    session = SessionLocal()
    client = construire_client()
    try:
        use_case = construire_use_case(session, client)
        rapport = use_case.execute(pointage_ids) if pointage_ids is not None else use_case.relancer()
        logger.info(
            "Synchronisation Costructor : %d envoye(s), %d deja envoye(s), %d ignore(s), "
            "%d erreur(s), %d non valide(s)",
            len(rapport.envoyes), len(rapport.deja_envoyes), len(rapport.ignores),
            len(rapport.erreurs), len(rapport.non_valides),
        )
        return rapport
    finally:
        client.fermer()
        session.close()


def _synchroniser_sans_lever(pointage_ids: list[int]) -> None:
    try:
        synchroniser(pointage_ids)
    except Exception:  # jamais d'exception non geree dans une tache de fond
        logger.exception("Synchronisation Costructor en echec pour %s", pointage_ids)


def planifier_synchronisation(
    background_tasks: BackgroundTasks, pointage_ids: Iterable[int]
) -> None:
    """Programme l'envoi apres la reponse HTTP, si la synchronisation est active.

    La validation des heures ne depend jamais de Costructor : un echec d'envoi
    est consigne et pourra etre relance.

    Args:
        background_tasks: Taches de fond de la requete en cours.
        pointage_ids: Pointages qui viennent d'etre valides.
    """
    ids = [int(pid) for pid in pointage_ids if pid is not None]
    if ids and synchronisation_active():
        background_tasks.add_task(_synchroniser_sans_lever, ids)
