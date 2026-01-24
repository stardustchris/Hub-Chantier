"""Entite Reservation - Reservation d'une ressource pour un chantier.

CDC Section 11 - LOG-07 a LOG-12, LOG-16 a LOG-18.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

from ..value_objects import StatutReservation


@dataclass
class Reservation:
    """
    Entite representant une reservation de ressource.

    Selon CDC Section 11:
    - LOG-07: Demande de reservation
    - LOG-08: Selection chantier (obligatoire)
    - LOG-09: Selection creneau (date + heures)
    - LOG-11: Workflow validation
    - LOG-12: Statuts reservation
    - LOG-16: Motif de refus
    - LOG-17: Detection conflits
    - LOG-18: Historique

    Workflow LOG-11:
    1. Demande creee -> EN_ATTENTE
    2. Si validation_requise:
       - Chef/Conducteur valide -> VALIDEE
       - Chef/Conducteur refuse -> REFUSEE
    3. Sinon:
       - Reservation directe -> VALIDEE
    """

    # Identifiant (genere par la DB)
    id: Optional[int] = None

    # Relations obligatoires
    ressource_id: int = 0
    chantier_id: int = 0
    demandeur_id: int = 0

    # Valideur (null si pas encore traite)
    valideur_id: Optional[int] = None

    # Creneau de reservation (LOG-09)
    date_debut: date = field(default_factory=date.today)
    date_fin: date = field(default_factory=date.today)
    heure_debut: str = "08:00"
    heure_fin: str = "18:00"

    # Statut (LOG-11, LOG-12)
    statut: StatutReservation = StatutReservation.EN_ATTENTE

    # Motif de refus (LOG-16)
    motif_refus: Optional[str] = None

    # Note du demandeur
    note: Optional[str] = None

    # Horodatages des actions
    validated_at: Optional[datetime] = None
    refused_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validation apres initialisation."""
        if self.ressource_id <= 0:
            raise ValueError("ressource_id est obligatoire")
        if self.chantier_id <= 0:
            raise ValueError("chantier_id est obligatoire (LOG-08)")
        if self.demandeur_id <= 0:
            raise ValueError("demandeur_id est obligatoire")
        if self.date_fin < self.date_debut:
            raise ValueError("date_fin doit etre >= date_debut")

    @property
    def is_active(self) -> bool:
        """Indique si la reservation est active."""
        return self.statut.is_active

    @property
    def is_pending(self) -> bool:
        """Indique si la reservation est en attente de validation."""
        return self.statut == StatutReservation.EN_ATTENTE

    @property
    def is_validated(self) -> bool:
        """Indique si la reservation est validee."""
        return self.statut == StatutReservation.VALIDEE

    @property
    def is_refused(self) -> bool:
        """Indique si la reservation est refusee."""
        return self.statut == StatutReservation.REFUSEE

    @property
    def is_cancelled(self) -> bool:
        """Indique si la reservation est annulee."""
        return self.statut == StatutReservation.ANNULEE

    def valider(self, valideur_id: int) -> None:
        """
        Valide la reservation.

        Args:
            valideur_id: ID de l'utilisateur qui valide.

        Raises:
            ValueError: Si la transition n'est pas permise.
        """
        if not self.statut.peut_transitionner_vers(StatutReservation.VALIDEE):
            raise ValueError(
                f"Impossible de valider une reservation au statut {self.statut.label}"
            )

        self.statut = StatutReservation.VALIDEE
        self.valideur_id = valideur_id
        self.validated_at = datetime.now()
        self.updated_at = datetime.now()

    def refuser(self, valideur_id: int, motif: Optional[str] = None) -> None:
        """
        Refuse la reservation.

        Args:
            valideur_id: ID de l'utilisateur qui refuse.
            motif: Motif du refus (LOG-16).

        Raises:
            ValueError: Si la transition n'est pas permise.
        """
        if not self.statut.peut_transitionner_vers(StatutReservation.REFUSEE):
            raise ValueError(
                f"Impossible de refuser une reservation au statut {self.statut.label}"
            )

        self.statut = StatutReservation.REFUSEE
        self.valideur_id = valideur_id
        self.motif_refus = motif
        self.refused_at = datetime.now()
        self.updated_at = datetime.now()

    def annuler(self) -> None:
        """
        Annule la reservation (par le demandeur).

        Raises:
            ValueError: Si la transition n'est pas permise.
        """
        if not self.statut.peut_transitionner_vers(StatutReservation.ANNULEE):
            raise ValueError(
                f"Impossible d'annuler une reservation au statut {self.statut.label}"
            )

        self.statut = StatutReservation.ANNULEE
        self.cancelled_at = datetime.now()
        self.updated_at = datetime.now()

    def chevauche(self, autre: "Reservation") -> bool:
        """
        Verifie si cette reservation chevauche une autre.

        Utilise pour la detection de conflits (LOG-17).

        Args:
            autre: L'autre reservation a comparer.

        Returns:
            True si les reservations se chevauchent.
        """
        # Verifier le chevauchement de dates
        if self.date_fin < autre.date_debut or self.date_debut > autre.date_fin:
            return False

        # Si meme jour(s), verifier le chevauchement d'heures
        # Note: Simplifie pour le cas ou les dates se chevauchent
        # En realite, il faudrait verifier chaque jour
        if self.heure_fin <= autre.heure_debut or self.heure_debut >= autre.heure_fin:
            return False

        return True

    def __repr__(self) -> str:
        return (
            f"<Reservation(id={self.id}, "
            f"ressource_id={self.ressource_id}, "
            f"chantier_id={self.chantier_id}, "
            f"statut={self.statut.value})>"
        )
