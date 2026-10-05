"""Port vers un systeme de paie externe (Costructor, Graneet...)."""

from abc import ABC, abstractmethod
from datetime import date, time


class ErreurPaieExterne(Exception):
    """Echec d'un echange avec le systeme de paie externe."""


class ClientPaieExternePort(ABC):
    """Creation et suppression de saisies de temps dans la paie externe."""

    @abstractmethod
    def creer_saisie_travail(
        self,
        utilisateur_externe_id: str,
        chantier_externe_id: str,
        jour: date,
        debut: time,
        fin: time,
        notes: str,
    ) -> str:
        """Cree une saisie de travail.

        Args:
            utilisateur_externe_id: Compagnon, dans le systeme externe.
            chantier_externe_id: Chantier, dans le systeme externe.
            jour: Jour travaille.
            debut: Heure de debut du creneau.
            fin: Heure de fin du creneau.
            notes: Commentaire visible dans le systeme externe.

        Returns:
            L'identifiant de la saisie creee.

        Raises:
            ErreurPaieExterne: Si la creation echoue.
        """

    @abstractmethod
    def supprimer_saisie(self, saisie_id: str) -> None:
        """Supprime une saisie ; une saisie deja absente n'est pas une erreur.

        Raises:
            ErreurPaieExterne: Si la suppression echoue.
        """
