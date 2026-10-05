"""Entite SynchronisationPaie : suivi de l'envoi d'un pointage vers une paie externe."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class StatutSynchronisation(Enum):
    """Etat de l'envoi d'un pointage vers la paie externe."""

    ENVOYE = "envoye"  # Toutes les saisies ont ete creees
    ERREUR = "erreur"  # Echec technique, a relancer
    IGNORE = "ignore"  # Envoi impossible en l'etat (correspondance manquante, 0h)


@dataclass
class SynchronisationPaie:
    """Trace l'envoi d'un pointage valide vers un systeme de paie externe.

    Le systeme externe (Costructor) ne protege pas contre les doublons : renvoyer
    une saisie en cree une seconde. Cette entite memorise les identifiants des
    saisies creees, pour ne jamais envoyer deux fois le meme pointage et pour
    nettoyer un envoi partiel avant de le relancer.

    Attributes:
        pointage_id: Pointage synchronise (un seul suivi par pointage).
        statut: Etat de l'envoi.
        saisies_externes: Identifiants des saisies creees dans le systeme externe.
        message: Detail de l'erreur ou de la raison d'ignorer.
        tentatives: Nombre d'envois tentes.
        id: Identifiant technique.
        derniere_tentative: Date du dernier envoi tente.
    """

    pointage_id: int
    statut: StatutSynchronisation
    saisies_externes: list[str] = field(default_factory=list)
    message: str | None = None
    tentatives: int = 0
    id: int | None = None
    derniere_tentative: datetime | None = None

    @property
    def est_envoye(self) -> bool:
        """Le pointage est deja present dans le systeme externe."""
        return self.statut == StatutSynchronisation.ENVOYE

    def enregistrer_tentative(
        self,
        statut: StatutSynchronisation,
        saisies_externes: list[str],
        message: str | None = None,
    ) -> None:
        """Consigne le resultat d'un envoi.

        Args:
            statut: Resultat de l'envoi.
            saisies_externes: Saisies effectivement presentes dans le systeme
                externe apres l'envoi (y compris en cas d'echec partiel).
            message: Detail de l'erreur ou de la raison d'ignorer.
        """
        self.statut = statut
        self.saisies_externes = list(saisies_externes)
        self.message = message
        self.tentatives += 1
        self.derniere_tentative = datetime.now()
