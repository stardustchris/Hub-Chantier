"""Service de guards pour le workflow des devis.

DEV-15: Suivi statut devis - Qui peut changer quoi.
Voir SPECIFICATIONS.md section 20.5 (Matrice des droits).
"""

from typing import Optional

from ..value_objects.statut_devis import StatutDevis


class TransitionNonAutoriseeError(Exception):
    """Erreur levee quand un utilisateur n'a pas le droit d'effectuer une transition."""

    def __init__(self, role: str, transition: str, raison: str):
        self.role = role
        self.transition = transition
        self.raison = raison
        super().__init__(
            f"Transition '{transition}' non autorisee pour le role '{role}': {raison}"
        )


class WorkflowGuards:
    """Guards metier pour les transitions de statut.

    DEV-15 + Section 20.5: Matrice des droits.
    Les guards verifient si un utilisateur avec un role donne
    peut effectuer une transition de statut specifique.

    Roles autorises pour le module devis:
    - admin: Toutes les transitions
    - conducteur: La plupart des transitions (sauf validation >= 50k EUR sans admin)
    - commercial: Soumission, envoi (pas de conversion)
    - chef_chantier: Aucune transition (lecture seule via metres)
    - compagnon: Aucun acces
    """

    # Roles autorises par type de transition
    TRANSITIONS_PAR_ROLE = {
        "soumettre": {"admin", "conducteur", "commercial"},
        "valider": {"admin", "conducteur", "commercial"},
        "retourner_brouillon": {"admin", "conducteur"},
        "envoyer": {"admin", "conducteur", "commercial"},
        "marquer_vu": {"admin", "conducteur", "commercial"},  # Aussi action systeme
        "negociation": {"admin", "conducteur", "commercial"},
        "accepter": {"admin", "conducteur"},
        "refuser": {"admin", "conducteur", "commercial"},
        "perdu": {"admin", "conducteur"},
        "expirer": {"admin"},  # Action systeme principalement
        "convertir": {"admin", "conducteur"},
    }

    # Seuil montant HT pour validation Direction obligatoire (defaut 50k EUR)
    SEUIL_VALIDATION_DIRECTION = 50_000

    @classmethod
    def verifier_transition(
        cls,
        role: str,
        transition: str,
        montant_ht: Optional[float] = None,
    ) -> None:
        """Verifie si le role peut effectuer la transition.

        Args:
            role: Le role de l'utilisateur (admin, conducteur, commercial...).
            transition: Le type de transition (soumettre, valider, accepter...).
            montant_ht: Montant HT du devis (pour validation >= 50k EUR).

        Raises:
            TransitionNonAutoriseeError: Si le role n'est pas autorise.
        """
        roles_autorises = cls.TRANSITIONS_PAR_ROLE.get(transition)
        if roles_autorises is None:
            raise TransitionNonAutoriseeError(
                role, transition, f"Transition '{transition}' inconnue"
            )

        if role not in roles_autorises:
            raise TransitionNonAutoriseeError(
                role, transition,
                f"Seuls les roles {', '.join(sorted(roles_autorises))} peuvent effectuer cette action"
            )

        # Guard specifique: validation devis >= 50k EUR -> admin uniquement
        if transition == "valider" and montant_ht is not None:
            if montant_ht >= cls.SEUIL_VALIDATION_DIRECTION and role != "admin":
                raise TransitionNonAutoriseeError(
                    role, transition,
                    f"La validation d'un devis >= {cls.SEUIL_VALIDATION_DIRECTION} EUR HT "
                    f"necessite le role admin (Direction)"
                )

    @classmethod
    def peut_effectuer_transition(
        cls,
        role: str,
        transition: str,
        montant_ht: Optional[float] = None,
    ) -> bool:
        """Verifie si le role peut effectuer la transition (sans lever d'exception).

        Returns:
            True si la transition est autorisee.
        """
        try:
            cls.verifier_transition(role, transition, montant_ht)
            return True
        except TransitionNonAutoriseeError:
            return False
