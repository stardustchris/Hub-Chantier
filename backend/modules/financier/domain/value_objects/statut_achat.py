"""Value Object pour le statut d'un achat.

FIN-05, FIN-06: Workflow de suivi des achats avec state machine.
"""

from enum import Enum
from typing import Set


class StatutAchat(str, Enum):
    """Statuts possibles d'un achat avec state machine.

    Workflow:
        demande -> valide, refuse
        valide -> commande, refuse (annulation)
        refuse -> (terminal)
        commande -> livre
        livre -> facture
        facture -> (terminal)
    """

    DEMANDE = "demande"
    VALIDE = "valide"
    REFUSE = "refuse"
    COMMANDE = "commande"
    LIVRE = "livre"
    FACTURE = "facture"

    @property
    def label(self) -> str:
        """Retourne le libellé affichable du statut."""
        labels = {
            self.DEMANDE: "Demande",
            self.VALIDE: "Validé",
            self.REFUSE: "Refusé",
            self.COMMANDE: "Commandé",
            self.LIVRE: "Livré",
            self.FACTURE: "Facturé",
        }
        return labels[self]

    @property
    def couleur(self) -> str:
        """Retourne la couleur CSS associée au statut."""
        couleurs = {
            self.DEMANDE: "#FFC107",   # Jaune
            self.VALIDE: "#2196F3",    # Bleu
            self.REFUSE: "#F44336",    # Rouge
            self.COMMANDE: "#FF9800",  # Orange
            self.LIVRE: "#8BC34A",     # Vert clair
            self.FACTURE: "#4CAF50",   # Vert
        }
        return couleurs[self]

    @property
    def emoji(self) -> str:
        """Retourne l'emoji associé au statut."""
        emojis = {
            self.DEMANDE: "🟡",
            self.VALIDE: "🔵",
            self.REFUSE: "🔴",
            self.COMMANDE: "🟠",
            self.LIVRE: "📦",
            self.FACTURE: "✅",
        }
        return emojis[self]

    @property
    def est_final(self) -> bool:
        """Indique si le statut est final (pas de transition possible)."""
        return self in {self.REFUSE, self.FACTURE}

    @property
    def est_actif(self) -> bool:
        """Indique si l'achat est actif (non refusé, non terminal négatif)."""
        return self not in {self.REFUSE}

    def transitions_possibles(self) -> Set["StatutAchat"]:
        """Retourne les statuts vers lesquels on peut transitionner.

        Returns:
            Ensemble des statuts cibles autorisés.
        """
        transitions = {
            self.DEMANDE: {self.VALIDE, self.REFUSE},
            self.VALIDE: {self.COMMANDE, self.REFUSE},
            self.REFUSE: set(),
            self.COMMANDE: {self.LIVRE},
            self.LIVRE: {self.FACTURE},
            self.FACTURE: set(),
        }
        return transitions[self]

    def peut_transitionner_vers(self, nouveau_statut: "StatutAchat") -> bool:
        """Vérifie si la transition vers le nouveau statut est autorisée.

        Args:
            nouveau_statut: Le statut cible souhaité.

        Returns:
            True si la transition est autorisée.
        """
        return nouveau_statut in self.transitions_possibles()

    @classmethod
    def initial(cls) -> "StatutAchat":
        """Retourne le statut initial d'un nouvel achat."""
        return cls.DEMANDE
