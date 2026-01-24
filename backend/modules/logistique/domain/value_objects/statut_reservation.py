"""Value Object pour le statut de reservation.

CDC Section 11 - LOG-11, LOG-12.
"""
from enum import Enum


class StatutReservation(str, Enum):
    """
    Statuts possibles pour une reservation.

    Workflow LOG-11:
    1. Demande creee -> EN_ATTENTE (jaune)
    2. Chef/Conducteur valide -> VALIDEE (vert)
    3. Chef/Conducteur refuse -> REFUSEE (rouge)
    4. Demandeur annule -> ANNULEE

    Si validation_requise = False sur la ressource:
    - Reservation passe directement a VALIDEE
    """

    EN_ATTENTE = "en_attente"
    """Demande en attente de validation (LOG-12: jaune)."""

    VALIDEE = "validee"
    """Reservation validee/confirmee (LOG-12: vert)."""

    REFUSEE = "refusee"
    """Reservation refusee (LOG-12: rouge)."""

    ANNULEE = "annulee"
    """Reservation annulee par le demandeur."""

    @property
    def couleur(self) -> str:
        """
        Code couleur associe au statut.

        Returns:
            Code couleur hexadecimal.
        """
        couleurs = {
            StatutReservation.EN_ATTENTE: "#F1C40F",  # Jaune
            StatutReservation.VALIDEE: "#2ECC71",      # Vert
            StatutReservation.REFUSEE: "#E74C3C",      # Rouge
            StatutReservation.ANNULEE: "#95A5A6",      # Gris
        }
        return couleurs.get(self, "#FFFFFF")

    @property
    def emoji(self) -> str:
        """
        Emoji associe au statut.

        Returns:
            Emoji unicode.
        """
        emojis = {
            StatutReservation.EN_ATTENTE: "🟡",
            StatutReservation.VALIDEE: "🟢",
            StatutReservation.REFUSEE: "🔴",
            StatutReservation.ANNULEE: "⚪",
        }
        return emojis.get(self, "")

    @property
    def label(self) -> str:
        """
        Libelle affichable du statut.

        Returns:
            Le libelle en francais.
        """
        labels = {
            StatutReservation.EN_ATTENTE: "En attente",
            StatutReservation.VALIDEE: "Validee",
            StatutReservation.REFUSEE: "Refusee",
            StatutReservation.ANNULEE: "Annulee",
        }
        return labels.get(self, self.value)

    @property
    def is_active(self) -> bool:
        """
        Indique si le statut represente une reservation active.

        Returns:
            True si la reservation est active (en attente ou validee).
        """
        return self in (StatutReservation.EN_ATTENTE, StatutReservation.VALIDEE)

    def peut_transitionner_vers(self, nouveau_statut: "StatutReservation") -> bool:
        """
        Verifie si une transition vers le nouveau statut est permise.

        Args:
            nouveau_statut: Le statut cible.

        Returns:
            True si la transition est permise.
        """
        transitions_permises = {
            StatutReservation.EN_ATTENTE: {
                StatutReservation.VALIDEE,
                StatutReservation.REFUSEE,
                StatutReservation.ANNULEE,
            },
            StatutReservation.VALIDEE: {
                StatutReservation.ANNULEE,
            },
            StatutReservation.REFUSEE: set(),  # Terminal
            StatutReservation.ANNULEE: set(),  # Terminal
        }
        return nouveau_statut in transitions_permises.get(self, set())
