"""Value Object pour le statut d'un devis.

DEV-15: Workflow statut devis - State machine complete.
"""

from enum import Enum
from typing import Set


class StatutDevis(str, Enum):
    """Statuts possibles d'un devis avec state machine.

    Workflow:
        brouillon -> en_validation
        en_validation -> brouillon, envoye
        envoye -> vu, en_negociation, accepte, refuse, expire
        vu -> en_negociation, accepte, refuse, expire
        en_negociation -> envoye (nouvelle version), accepte, refuse, perdu
        accepte -> (terminal)
        refuse -> (terminal)
        perdu -> (terminal)
        expire -> en_negociation
    """

    BROUILLON = "brouillon"
    EN_VALIDATION = "en_validation"
    ENVOYE = "envoye"
    VU = "vu"
    EN_NEGOCIATION = "en_negociation"
    ACCEPTE = "accepte"
    REFUSE = "refuse"
    PERDU = "perdu"
    EXPIRE = "expire"

    @property
    def label(self) -> str:
        """Retourne le libelle affichable du statut."""
        labels = {
            self.BROUILLON: "Brouillon",
            self.EN_VALIDATION: "En validation",
            self.ENVOYE: "Envoye",
            self.VU: "Vu",
            self.EN_NEGOCIATION: "En negociation",
            self.ACCEPTE: "Accepte",
            self.REFUSE: "Refuse",
            self.PERDU: "Perdu",
            self.EXPIRE: "Expire",
        }
        return labels[self]

    @property
    def couleur(self) -> str:
        """Retourne la couleur CSS associee au statut."""
        couleurs = {
            self.BROUILLON: "#9E9E9E",       # Gris
            self.EN_VALIDATION: "#FFC107",    # Jaune
            self.ENVOYE: "#2196F3",           # Bleu
            self.VU: "#9C27B0",               # Violet
            self.EN_NEGOCIATION: "#FF9800",   # Orange
            self.ACCEPTE: "#4CAF50",          # Vert
            self.REFUSE: "#F44336",           # Rouge
            self.PERDU: "#795548",            # Marron
            self.EXPIRE: "#607D8B",           # Gris bleu
        }
        return couleurs[self]

    @property
    def est_final(self) -> bool:
        """Indique si le statut est final (pas de transition possible)."""
        return self in {self.ACCEPTE, self.REFUSE, self.PERDU}

    @property
    def est_modifiable(self) -> bool:
        """Indique si le devis peut etre modifie dans ce statut."""
        return self in {self.BROUILLON, self.EN_NEGOCIATION}

    @property
    def est_actif(self) -> bool:
        """Indique si le devis est dans un statut actif (pipeline commercial)."""
        return self not in {self.REFUSE, self.PERDU, self.EXPIRE}

    def transitions_possibles(self) -> Set["StatutDevis"]:
        """Retourne les statuts vers lesquels on peut transitionner.

        Returns:
            Ensemble des statuts cibles autorises.
        """
        transitions = {
            self.BROUILLON: {self.EN_VALIDATION},
            self.EN_VALIDATION: {self.BROUILLON, self.ENVOYE},
            self.ENVOYE: {self.VU, self.EN_NEGOCIATION, self.ACCEPTE, self.REFUSE, self.EXPIRE},
            self.VU: {self.EN_NEGOCIATION, self.ACCEPTE, self.REFUSE, self.EXPIRE},
            self.EN_NEGOCIATION: {self.ENVOYE, self.ACCEPTE, self.REFUSE, self.PERDU},
            self.ACCEPTE: set(),
            self.REFUSE: set(),
            self.PERDU: set(),
            self.EXPIRE: {self.EN_NEGOCIATION},
        }
        return transitions[self]

    def peut_transitionner_vers(self, nouveau_statut: "StatutDevis") -> bool:
        """Verifie si la transition vers le nouveau statut est autorisee.

        Args:
            nouveau_statut: Le statut cible souhaite.

        Returns:
            True si la transition est autorisee.
        """
        return nouveau_statut in self.transitions_possibles()

    @classmethod
    def initial(cls) -> "StatutDevis":
        """Retourne le statut initial d'un nouveau devis."""
        return cls.BROUILLON
