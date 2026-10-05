"""Decoupage d'une duree de travail en creneaux horaires.

Un pointage ne stocke qu'une duree. Certains logiciels de paie (Costructor)
exigent pourtant une heure de debut et de fin, et comptent toute l'amplitude
sans deduire de pause. Pour transmettre un total exact, la journee est donc
reconstituee en creneaux qui encadrent le repas, a partir des horaires de
reference de l'entreprise.
"""

from dataclasses import dataclass
from datetime import time

MINUTES_PAR_JOUR = 24 * 60


def _en_minutes(heure: time) -> int:
    return heure.hour * 60 + heure.minute


def _depuis_minutes(minutes: int) -> time:
    return time(minutes // 60, minutes % 60)


@dataclass(frozen=True)
class Creneau:
    """Plage horaire de travail continue."""

    debut: time
    fin: time

    @property
    def duree_minutes(self) -> int:
        """Duree du creneau en minutes."""
        return _en_minutes(self.fin) - _en_minutes(self.debut)


@dataclass(frozen=True)
class HorairesReference:
    """Horaires de reference d'une journee : debut et pause repas.

    Raises:
        ValueError: Si la pause ne suit pas le debut de journee.
    """

    debut: time
    pause_debut: time
    pause_fin: time

    def __post_init__(self) -> None:
        if not self.debut < self.pause_debut <= self.pause_fin:
            raise ValueError(
                "Horaires incoherents : il faut debut < debut de pause <= fin de pause "
                f"(recu {self.debut}, {self.pause_debut}, {self.pause_fin})."
            )

    @classmethod
    def depuis_texte(cls, debut: str, pause_debut: str, pause_fin: str) -> "HorairesReference":
        """Construit les horaires depuis des chaines "HH:MM".

        Args:
            debut: Heure de debut de journee.
            pause_debut: Debut de la pause repas.
            pause_fin: Fin de la pause repas.

        Returns:
            Les horaires de reference.
        """
        return cls(
            debut=time.fromisoformat(debut),
            pause_debut=time.fromisoformat(pause_debut),
            pause_fin=time.fromisoformat(pause_fin),
        )


def decouper_en_creneaux(duree_minutes: int, horaires: HorairesReference) -> list[Creneau]:
    """Reconstitue une journee de travail en creneaux encadrant le repas.

    La matinee court du debut de journee au debut de pause ; le reste de la
    duree est place apres la pause. La somme des creneaux est toujours egale
    a la duree, sans pause comptee.

    Exemples avec 8h00 et un repas de 12h00 a 13h00 :
        7h  -> 08:00-12:00 + 13:00-16:00
        3h  -> 08:00-11:00

    Args:
        duree_minutes: Duree de travail a repartir, en minutes.
        horaires: Horaires de reference de l'entreprise.

    Returns:
        Les creneaux, vide si la duree est nulle.

    Raises:
        ValueError: Si la duree est negative ou deborde au-dela de minuit.
    """
    if duree_minutes < 0:
        raise ValueError(f"Duree negative : {duree_minutes} minutes.")
    if duree_minutes == 0:
        return []

    debut = _en_minutes(horaires.debut)
    capacite_matin = _en_minutes(horaires.pause_debut) - debut

    if duree_minutes <= capacite_matin:
        return [Creneau(horaires.debut, _depuis_minutes(debut + duree_minutes))]

    reste = duree_minutes - capacite_matin
    fin_apres_midi = _en_minutes(horaires.pause_fin) + reste
    if fin_apres_midi >= MINUTES_PAR_JOUR:
        raise ValueError(
            f"Duree de {duree_minutes // 60}h{duree_minutes % 60:02d} trop longue : "
            "l'apres-midi depasserait minuit."
        )

    return [
        Creneau(horaires.debut, horaires.pause_debut),
        Creneau(horaires.pause_fin, _depuis_minutes(fin_apres_midi)),
    ]
