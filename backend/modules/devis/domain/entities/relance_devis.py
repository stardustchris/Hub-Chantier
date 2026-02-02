"""Entite RelanceDevis - Relances automatiques de devis.

DEV-24: Relances automatiques - Notifications push/email si delai
de reponse depasse (configurable : 7j, 15j, 30j) avec historique.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class RelanceDevisValidationError(Exception):
    """Erreur levee lors d'une validation metier sur une relance."""

    pass


TYPES_RELANCE_VALIDES = ("email", "push", "email_push")
STATUTS_RELANCE_VALIDES = ("planifiee", "envoyee", "annulee")


@dataclass
class RelanceDevis:
    """Represente une relance automatique pour un devis envoye.

    Une relance est une notification (email/push) envoyee au client
    si le delai de reponse configurable est depasse. Chaque devis
    peut avoir plusieurs relances planifiees (1ere, 2eme, 3eme...).

    Attributes:
        id: Identifiant unique (None si non persiste).
        devis_id: ID du devis concerne.
        numero_relance: Numero sequentiel de la relance (1, 2, 3...).
        type_relance: Type de notification ('email', 'push', 'email_push').
        date_envoi: Date reelle d'envoi de la relance (None si pas encore envoyee).
        date_prevue: Date prevue pour l'envoi de la relance.
        statut: Statut de la relance ('planifiee', 'envoyee', 'annulee').
        message_personnalise: Message personnalise optionnel.
        created_at: Date de creation de l'enregistrement.
    """

    devis_id: int
    numero_relance: int
    type_relance: str
    date_prevue: datetime

    id: Optional[int] = None
    date_envoi: Optional[datetime] = None
    statut: str = "planifiee"
    message_personnalise: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        if self.devis_id <= 0:
            raise RelanceDevisValidationError(
                "L'ID du devis est obligatoire et doit etre positif"
            )
        if self.numero_relance < 1:
            raise RelanceDevisValidationError(
                "Le numero de relance doit etre >= 1"
            )
        if self.type_relance not in TYPES_RELANCE_VALIDES:
            raise RelanceDevisValidationError(
                f"Type de relance invalide: {self.type_relance}. "
                f"Valeurs autorisees: {', '.join(TYPES_RELANCE_VALIDES)}"
            )
        if self.statut not in STATUTS_RELANCE_VALIDES:
            raise RelanceDevisValidationError(
                f"Statut de relance invalide: {self.statut}. "
                f"Valeurs autorisees: {', '.join(STATUTS_RELANCE_VALIDES)}"
            )

    @property
    def est_planifiee(self) -> bool:
        """Verifie si la relance est en attente d'envoi."""
        return self.statut == "planifiee"

    @property
    def est_envoyee(self) -> bool:
        """Verifie si la relance a ete envoyee."""
        return self.statut == "envoyee"

    @property
    def est_annulee(self) -> bool:
        """Verifie si la relance a ete annulee."""
        return self.statut == "annulee"

    @property
    def est_en_retard(self) -> bool:
        """Verifie si la relance planifiee a depasse sa date prevue."""
        if not self.est_planifiee:
            return False
        return datetime.utcnow() >= self.date_prevue

    def envoyer(self) -> None:
        """Marque la relance comme envoyee.

        Raises:
            RelanceDevisValidationError: Si la relance n'est pas planifiee.
        """
        if not self.est_planifiee:
            raise RelanceDevisValidationError(
                f"Impossible d'envoyer une relance en statut '{self.statut}'"
            )
        self.statut = "envoyee"
        self.date_envoi = datetime.utcnow()

    def annuler(self) -> None:
        """Annule la relance.

        Raises:
            RelanceDevisValidationError: Si la relance n'est pas planifiee.
        """
        if not self.est_planifiee:
            raise RelanceDevisValidationError(
                f"Impossible d'annuler une relance en statut '{self.statut}'"
            )
        self.statut = "annulee"

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "devis_id": self.devis_id,
            "numero_relance": self.numero_relance,
            "type_relance": self.type_relance,
            "date_envoi": (
                self.date_envoi.isoformat() if self.date_envoi else None
            ),
            "date_prevue": (
                self.date_prevue.isoformat() if self.date_prevue else None
            ),
            "statut": self.statut,
            "message_personnalise": self.message_personnalise,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
        }

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID (entite)."""
        if not isinstance(other, RelanceDevis):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
