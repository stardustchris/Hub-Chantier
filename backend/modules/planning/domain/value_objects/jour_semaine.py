"""Value Object JourSemaine - Represente un jour de la semaine pour la recurrence."""

from enum import IntEnum
from typing import List


class JourSemaine(IntEnum):
    """
    Enumeration des jours de la semaine.

    Utilise pour definir les patterns de recurrence des affectations.
    Les valeurs correspondent aux conventions Python (0=lundi, 6=dimanche).

    Attributes:
        LUNDI: Premier jour de la semaine (0).
        MARDI: Deuxieme jour (1).
        MERCREDI: Troisieme jour (2).
        JEUDI: Quatrieme jour (3).
        VENDREDI: Cinquieme jour (4).
        SAMEDI: Sixieme jour (5).
        DIMANCHE: Septieme jour (6).

    Example:
        >>> JourSemaine.LUNDI.value
        0
        >>> JourSemaine.LUNDI.nom_francais()
        'Lundi'
    """

    LUNDI = 0
    MARDI = 1
    MERCREDI = 2
    JEUDI = 3
    VENDREDI = 4
    SAMEDI = 5
    DIMANCHE = 6

    def __str__(self) -> str:
        """Retourne le nom du jour en francais."""
        return self.nom_francais()

    def nom_francais(self) -> str:
        """
        Retourne le nom du jour en francais.

        Returns:
            Le nom du jour (ex: "Lundi").
        """
        noms = {
            JourSemaine.LUNDI: "Lundi",
            JourSemaine.MARDI: "Mardi",
            JourSemaine.MERCREDI: "Mercredi",
            JourSemaine.JEUDI: "Jeudi",
            JourSemaine.VENDREDI: "Vendredi",
            JourSemaine.SAMEDI: "Samedi",
            JourSemaine.DIMANCHE: "Dimanche",
        }
        return noms[self]

    def nom_court(self) -> str:
        """
        Retourne l'abreviation du jour (3 lettres).

        Returns:
            L'abreviation (ex: "Lun").
        """
        noms_courts = {
            JourSemaine.LUNDI: "Lun",
            JourSemaine.MARDI: "Mar",
            JourSemaine.MERCREDI: "Mer",
            JourSemaine.JEUDI: "Jeu",
            JourSemaine.VENDREDI: "Ven",
            JourSemaine.SAMEDI: "Sam",
            JourSemaine.DIMANCHE: "Dim",
        }
        return noms_courts[self]

    def is_weekend(self) -> bool:
        """
        Verifie si le jour est un jour de weekend.

        Returns:
            True si samedi ou dimanche.
        """
        return self in (JourSemaine.SAMEDI, JourSemaine.DIMANCHE)

    def is_semaine(self) -> bool:
        """
        Verifie si le jour est un jour de semaine (lundi-vendredi).

        Returns:
            True si jour ouvre.
        """
        return not self.is_weekend()

    @classmethod
    def from_int(cls, value: int) -> "JourSemaine":
        """
        Cree un JourSemaine a partir d'un entier.

        Args:
            value: La valeur entiere du jour (0-6).

        Returns:
            L'instance JourSemaine correspondante.

        Raises:
            ValueError: Si la valeur est hors limites.

        Example:
            >>> JourSemaine.from_int(0)
            <JourSemaine.LUNDI: 0>
        """
        try:
            return cls(value)
        except ValueError:
            raise ValueError(
                f"Jour invalide: {value}. Valeurs valides: 0-6 (Lundi-Dimanche)"
            )

    @classmethod
    def from_string(cls, value: str) -> "JourSemaine":
        """
        Cree un JourSemaine a partir d'une chaine.

        Args:
            value: Le nom du jour (complet ou abrege, insensible a la casse).

        Returns:
            L'instance JourSemaine correspondante.

        Raises:
            ValueError: Si le nom ne correspond a aucun jour.

        Example:
            >>> JourSemaine.from_string("lundi")
            <JourSemaine.LUNDI: 0>
            >>> JourSemaine.from_string("Lun")
            <JourSemaine.LUNDI: 0>
        """
        value_lower = value.lower().strip()

        mappings = {
            "lundi": cls.LUNDI,
            "lun": cls.LUNDI,
            "mardi": cls.MARDI,
            "mar": cls.MARDI,
            "mercredi": cls.MERCREDI,
            "mer": cls.MERCREDI,
            "jeudi": cls.JEUDI,
            "jeu": cls.JEUDI,
            "vendredi": cls.VENDREDI,
            "ven": cls.VENDREDI,
            "samedi": cls.SAMEDI,
            "sam": cls.SAMEDI,
            "dimanche": cls.DIMANCHE,
            "dim": cls.DIMANCHE,
        }

        if value_lower in mappings:
            return mappings[value_lower]

        raise ValueError(
            f"Jour invalide: {value}. Valeurs valides: Lundi, Mardi, ..., Dimanche"
        )

    @classmethod
    def jours_semaine(cls) -> List["JourSemaine"]:
        """
        Retourne la liste des jours ouvrables (lundi-vendredi).

        Returns:
            Liste des jours de la semaine.
        """
        return [
            cls.LUNDI,
            cls.MARDI,
            cls.MERCREDI,
            cls.JEUDI,
            cls.VENDREDI,
        ]

    @classmethod
    def weekend(cls) -> List["JourSemaine"]:
        """
        Retourne la liste des jours de weekend.

        Returns:
            Liste contenant samedi et dimanche.
        """
        return [cls.SAMEDI, cls.DIMANCHE]

    @classmethod
    def tous(cls) -> List["JourSemaine"]:
        """
        Retourne la liste de tous les jours de la semaine.

        Returns:
            Liste de tous les jours (lundi-dimanche).
        """
        return list(cls)
