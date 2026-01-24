"""Value Object pour le statut de réservation.

LOG-11, LOG-12: Workflow de validation des réservations.
"""

from enum import Enum
from typing import List, Set


class StatutReservation(str, Enum):
    """Statuts possibles d'une réservation.

    LOG-11: Workflow validation - Demande 🟡 → Chef valide → Confirmée 🟢
    LOG-12: Statuts réservation - En attente 🟡 / Validée 🟢 / Refusée 🔴
    """

    EN_ATTENTE = "en_attente"
    VALIDEE = "validee"
    REFUSEE = "refusee"
    ANNULEE = "annulee"

    @property
    def label(self) -> str:
        """Retourne le libellé affichable du statut."""
        labels = {
            self.EN_ATTENTE: "En attente",
            self.VALIDEE: "Validée",
            self.REFUSEE: "Refusée",
            self.ANNULEE: "Annulée",
        }
        return labels[self]

    @property
    def emoji(self) -> str:
        """Retourne l'emoji associé au statut."""
        emojis = {
            self.EN_ATTENTE: "🟡",
            self.VALIDEE: "🟢",
            self.REFUSEE: "🔴",
            self.ANNULEE: "⚫",
        }
        return emojis[self]

    @property
    def couleur(self) -> str:
        """Retourne la couleur CSS associée au statut."""
        couleurs = {
            self.EN_ATTENTE: "#FFC107",  # Jaune
            self.VALIDEE: "#4CAF50",  # Vert
            self.REFUSEE: "#F44336",  # Rouge
            self.ANNULEE: "#9E9E9E",  # Gris
        }
        return couleurs[self]

    @property
    def est_active(self) -> bool:
        """Indique si la réservation est active (occupe le créneau)."""
        return self in {self.EN_ATTENTE, self.VALIDEE}

    @property
    def est_finale(self) -> bool:
        """Indique si le statut est final (pas de transition possible)."""
        return self in {self.REFUSEE, self.ANNULEE}

    def transitions_possibles(self) -> Set["StatutReservation"]:
        """Retourne les statuts vers lesquels on peut transitionner.

        Règles de transition:
        - EN_ATTENTE → VALIDEE, REFUSEE, ANNULEE
        - VALIDEE → ANNULEE
        - REFUSEE → (aucune)
        - ANNULEE → (aucune)
        """
        transitions = {
            self.EN_ATTENTE: {self.VALIDEE, self.REFUSEE, self.ANNULEE},
            self.VALIDEE: {self.ANNULEE},
            self.REFUSEE: set(),
            self.ANNULEE: set(),
        }
        return transitions[self]

    def peut_transitionner_vers(self, nouveau_statut: "StatutReservation") -> bool:
        """Vérifie si la transition vers le nouveau statut est autorisée."""
        return nouveau_statut in self.transitions_possibles()

    @classmethod
    def initial(cls) -> "StatutReservation":
        """Retourne le statut initial d'une nouvelle réservation."""
        return cls.EN_ATTENTE
