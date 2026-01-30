"""Value Object StatutChantier - Statut d'un chantier."""

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class StatutChantierEnum(Enum):
    """
    Enumération des statuts possibles d'un chantier.

    Selon CDC Section 4.4 - Statuts de chantier.
    """

    OUVERT = "ouvert"  # Chantier créé, en préparation
    EN_COURS = "en_cours"  # Travaux en cours d'exécution
    RECEPTIONNE = "receptionne"  # Travaux terminés, en attente clôture
    FERME = "ferme"  # Chantier clôturé définitivement


@dataclass(frozen=True)
class StatutChantier:
    """
    Value Object représentant le statut d'un chantier.

    Selon CDC Section 4.4:
    - Ouvert: Chantier créé, en préparation
    - En cours: Travaux en cours d'exécution
    - Réceptionné: Travaux terminés, en attente clôture
    - Fermé: Chantier clôturé définitivement

    Attributes:
        value: Le statut du chantier.
    """

    value: StatutChantierEnum

    # Mapping des icônes par statut (CDC Section 4.4)
    ICONS: ClassVar[dict[StatutChantierEnum, str]] = {
        StatutChantierEnum.OUVERT: "🔵",
        StatutChantierEnum.EN_COURS: "🟢",
        StatutChantierEnum.RECEPTIONNE: "🟡",
        StatutChantierEnum.FERME: "🔴",
    }

    # Transitions autorisées
    TRANSITIONS: ClassVar[dict[StatutChantierEnum, list[StatutChantierEnum]]] = {
        StatutChantierEnum.OUVERT: [StatutChantierEnum.EN_COURS, StatutChantierEnum.FERME],
        StatutChantierEnum.EN_COURS: [StatutChantierEnum.RECEPTIONNE, StatutChantierEnum.FERME],
        StatutChantierEnum.RECEPTIONNE: [StatutChantierEnum.EN_COURS, StatutChantierEnum.FERME],
        StatutChantierEnum.FERME: [],  # Pas de transition depuis fermé
    }

    def __str__(self) -> str:
        """Retourne la valeur du statut."""
        return self.value.value

    @property
    def icon(self) -> str:
        """Retourne l'icône associée au statut."""
        return self.ICONS[self.value]

    @property
    def display_name(self) -> str:
        """Retourne le nom d'affichage du statut."""
        names = {
            StatutChantierEnum.OUVERT: "Ouvert",
            StatutChantierEnum.EN_COURS: "En cours",
            StatutChantierEnum.RECEPTIONNE: "Réceptionné",
            StatutChantierEnum.FERME: "Fermé",
        }
        return names[self.value]

    def can_transition_to(self, new_statut: "StatutChantier") -> bool:
        """
        Vérifie si la transition vers un nouveau statut est autorisée.

        Args:
            new_statut: Le statut cible.

        Returns:
            True si la transition est autorisée.
        """
        return new_statut.value in self.TRANSITIONS[self.value]

    def is_active(self) -> bool:
        """Vérifie si le chantier est dans un état actif (non fermé)."""
        return self.value != StatutChantierEnum.FERME

    def allows_modifications(self) -> bool:
        """Vérifie si le statut permet des modifications opérationnelles."""
        return self.value in [StatutChantierEnum.OUVERT, StatutChantierEnum.EN_COURS, StatutChantierEnum.RECEPTIONNE]

    def allows_planning(self) -> bool:
        """Vérifie si le statut permet la planification d'équipes."""
        return self.value in [StatutChantierEnum.OUVERT, StatutChantierEnum.EN_COURS]

    @classmethod
    def ouvert(cls) -> "StatutChantier":
        """Crée un statut Ouvert."""
        return cls(StatutChantierEnum.OUVERT)

    @classmethod
    def en_cours(cls) -> "StatutChantier":
        """Crée un statut En cours."""
        return cls(StatutChantierEnum.EN_COURS)

    @classmethod
    def receptionne(cls) -> "StatutChantier":
        """Crée un statut Réceptionné."""
        return cls(StatutChantierEnum.RECEPTIONNE)

    @classmethod
    def ferme(cls) -> "StatutChantier":
        """Crée un statut Fermé."""
        return cls(StatutChantierEnum.FERME)

    @classmethod
    def from_string(cls, value: str) -> "StatutChantier":
        """
        Crée un StatutChantier à partir d'une chaîne.

        Args:
            value: Le statut sous forme de chaîne.

        Returns:
            L'instance StatutChantier correspondante.

        Raises:
            ValueError: Si le statut n'est pas valide.
        """
        value_lower = value.lower().strip()
        for statut in StatutChantierEnum:
            if statut.value == value_lower:
                return cls(statut)
        valid = [s.value for s in StatutChantierEnum]
        raise ValueError(f"Statut invalide: {value}. Valeurs valides: {valid}")

    @classmethod
    def all_statuts(cls) -> list[str]:
        """Retourne la liste de tous les statuts possibles."""
        return [s.value for s in StatutChantierEnum]
