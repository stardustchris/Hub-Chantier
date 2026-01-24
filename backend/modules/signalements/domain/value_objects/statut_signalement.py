"""Value Object StatutSignalement - États d'un signalement (SIG-08, SIG-09)."""

from enum import Enum


class StatutSignalement(Enum):
    """
    États possibles d'un signalement.

    Selon CDC:
    - SIG-08: Marquer comme "traité" avec date et commentaire
    - SIG-09: Clôture du signalement
    """

    OUVERT = "ouvert"  # État initial lors de la création
    EN_COURS = "en_cours"  # Prise en charge en cours
    TRAITE = "traite"  # Traité, en attente de validation/clôture
    CLOTURE = "cloture"  # Signalement clôturé définitivement

    @property
    def label(self) -> str:
        """Retourne le label d'affichage."""
        labels = {
            StatutSignalement.OUVERT: "Ouvert",
            StatutSignalement.EN_COURS: "En cours",
            StatutSignalement.TRAITE: "Traité",
            StatutSignalement.CLOTURE: "Clôturé",
        }
        return labels[self]

    @property
    def couleur(self) -> str:
        """Retourne la couleur associée."""
        couleurs = {
            StatutSignalement.OUVERT: "red",
            StatutSignalement.EN_COURS: "orange",
            StatutSignalement.TRAITE: "blue",
            StatutSignalement.CLOTURE: "green",
        }
        return couleurs[self]

    @property
    def icone(self) -> str:
        """Retourne l'icône associée."""
        icones = {
            StatutSignalement.OUVERT: "alert-circle",
            StatutSignalement.EN_COURS: "clock",
            StatutSignalement.TRAITE: "check",
            StatutSignalement.CLOTURE: "check-circle",
        }
        return icones[self]

    @property
    def est_actif(self) -> bool:
        """Indique si le signalement nécessite encore une action."""
        return self in (StatutSignalement.OUVERT, StatutSignalement.EN_COURS)

    @property
    def est_resolu(self) -> bool:
        """Indique si le signalement a été résolu."""
        return self in (StatutSignalement.TRAITE, StatutSignalement.CLOTURE)

    @property
    def peut_etre_modifie(self) -> bool:
        """Indique si le signalement peut encore être modifié."""
        return self != StatutSignalement.CLOTURE

    @property
    def ordre(self) -> int:
        """Retourne l'ordre de tri."""
        ordres = {
            StatutSignalement.OUVERT: 1,
            StatutSignalement.EN_COURS: 2,
            StatutSignalement.TRAITE: 3,
            StatutSignalement.CLOTURE: 4,
        }
        return ordres[self]

    def peut_transitionner_vers(self, nouveau_statut: "StatutSignalement") -> bool:
        """
        Vérifie si la transition vers un nouveau statut est valide.

        Transitions autorisées:
        - OUVERT -> EN_COURS, TRAITE (pas de clôture directe - doit traiter d'abord)
        - EN_COURS -> TRAITE, OUVERT (réouverture)
        - TRAITE -> CLOTURE, OUVERT (réouverture)
        - CLOTURE -> OUVERT (réouverture exceptionnelle)

        Args:
            nouveau_statut: Le statut cible.

        Returns:
            True si la transition est autorisée.
        """
        transitions = {
            StatutSignalement.OUVERT: [
                StatutSignalement.EN_COURS,
                StatutSignalement.TRAITE,
                # Pas de CLOTURE directe - doit passer par TRAITE d'abord
            ],
            StatutSignalement.EN_COURS: [
                StatutSignalement.OUVERT,
                StatutSignalement.TRAITE,
                # Pas de CLOTURE directe - doit passer par TRAITE d'abord
            ],
            StatutSignalement.TRAITE: [
                StatutSignalement.OUVERT,
                StatutSignalement.CLOTURE,
            ],
            StatutSignalement.CLOTURE: [
                StatutSignalement.OUVERT,
            ],
        }
        return nouveau_statut in transitions.get(self, [])

    @classmethod
    def from_string(cls, value: str) -> "StatutSignalement":
        """
        Convertit une chaîne en StatutSignalement.

        Args:
            value: La valeur à convertir.

        Returns:
            Le statut correspondant.

        Raises:
            ValueError: Si la valeur n'est pas valide.
        """
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(
                f"Statut invalide: {value}. "
                f"Valeurs acceptées: {', '.join(s.value for s in cls)}"
            )

    @classmethod
    def list_actifs(cls) -> list["StatutSignalement"]:
        """Retourne les statuts actifs (non résolus)."""
        return [s for s in cls if s.est_actif]

    @classmethod
    def list_all(cls) -> list["StatutSignalement"]:
        """Retourne tous les statuts triés par ordre."""
        return sorted(cls, key=lambda s: s.ordre)
