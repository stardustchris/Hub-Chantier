"""Entité Reservation - Représente une réservation de ressource.

LOG-07: Demande de réservation - Depuis mobile ou web
LOG-08: Sélection chantier - Association obligatoire au projet
LOG-09: Sélection créneau - Date + heure début / heure fin
LOG-11: Workflow validation - Demande 🟡 → Chef valide → Confirmée 🟢
LOG-16: Motif de refus - Champ texte optionnel
LOG-17: Conflit de réservation - Alerte si créneau déjà occupé
"""

from dataclasses import dataclass
from datetime import datetime, date, time
from typing import Optional

from ..value_objects import StatutReservation, PlageHoraire


class ReservationConflitError(Exception):
    """Erreur levée quand une réservation entre en conflit avec une autre."""

    def __init__(self, ressource_id: int, date_reservation: date, plage: PlageHoraire):
        self.ressource_id = ressource_id
        self.date_reservation = date_reservation
        self.plage = plage
        super().__init__(
            f"Conflit de réservation pour la ressource {ressource_id} "
            f"le {date_reservation} de {plage.format_display()}"
        )


class TransitionStatutInvalideError(Exception):
    """Erreur levée lors d'une transition de statut invalide."""

    def __init__(
        self, statut_actuel: StatutReservation, statut_cible: StatutReservation
    ):
        self.statut_actuel = statut_actuel
        self.statut_cible = statut_cible
        super().__init__(
            f"Transition invalide: {statut_actuel.label} → {statut_cible.label}"
        )


@dataclass
class Reservation:
    """Représente une réservation de ressource.

    Une réservation lie une ressource à un chantier pour une date
    et un créneau horaire spécifiques.
    """

    id: Optional[int] = None
    ressource_id: int = 0
    chantier_id: int = 0
    demandeur_id: int = 0
    date_reservation: date = None
    heure_debut: time = None
    heure_fin: time = None
    statut: StatutReservation = StatutReservation.EN_ATTENTE
    motif_refus: Optional[str] = None
    commentaire: Optional[str] = None
    valideur_id: Optional[int] = None
    validated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # H10: Soft delete fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation à la création."""
        if self.ressource_id <= 0:
            raise ValueError("L'ID de la ressource est obligatoire")
        if self.chantier_id <= 0:
            raise ValueError("L'ID du chantier est obligatoire (LOG-08)")
        if self.demandeur_id <= 0:
            raise ValueError("L'ID du demandeur est obligatoire")
        if self.date_reservation is None:
            raise ValueError("La date de réservation est obligatoire")
        if self.heure_debut is None or self.heure_fin is None:
            raise ValueError("Les heures de début et fin sont obligatoires (LOG-09)")
        if self.heure_fin <= self.heure_debut:
            raise ValueError("L'heure de fin doit être après l'heure de début")

    @property
    def plage_horaire(self) -> PlageHoraire:
        """Retourne la plage horaire de la réservation."""
        return PlageHoraire(heure_debut=self.heure_debut, heure_fin=self.heure_fin)

    @property
    def est_en_attente(self) -> bool:
        """Vérifie si la réservation est en attente de validation."""
        return self.statut == StatutReservation.EN_ATTENTE

    @property
    def est_validee(self) -> bool:
        """Vérifie si la réservation est validée."""
        return self.statut == StatutReservation.VALIDEE

    @property
    def est_active(self) -> bool:
        """Vérifie si la réservation occupe le créneau."""
        return self.statut.est_active and not self.est_supprimee

    @property
    def est_supprimee(self) -> bool:
        """Vérifie si la réservation a été supprimée (soft delete)."""
        return self.deleted_at is not None

    def supprimer(self, deleted_by: int) -> None:
        """Marque la réservation comme supprimée (soft delete)."""
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    @property
    def est_passee(self) -> bool:
        """Vérifie si la réservation est dans le passé."""
        return self.date_reservation < date.today()

    @property
    def est_demain(self) -> bool:
        """Vérifie si la réservation est pour demain (LOG-15: Rappel J-1)."""
        from datetime import timedelta

        demain = date.today() + timedelta(days=1)
        return self.date_reservation == demain

    def valider(self, valideur_id: int) -> None:
        """Valide la réservation.

        LOG-11: Workflow validation - Chef valide → Confirmée 🟢

        Args:
            valideur_id: ID de l'utilisateur qui valide

        Raises:
            TransitionStatutInvalideError: Si la transition n'est pas autorisée
        """
        if not self.statut.peut_transitionner_vers(StatutReservation.VALIDEE):
            raise TransitionStatutInvalideError(self.statut, StatutReservation.VALIDEE)

        self.statut = StatutReservation.VALIDEE
        self.valideur_id = valideur_id
        self.validated_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def refuser(self, valideur_id: int, motif: Optional[str] = None) -> None:
        """Refuse la réservation.

        LOG-16: Motif de refus - Champ texte optionnel

        Args:
            valideur_id: ID de l'utilisateur qui refuse
            motif: Raison du refus (optionnel)

        Raises:
            TransitionStatutInvalideError: Si la transition n'est pas autorisée
        """
        if not self.statut.peut_transitionner_vers(StatutReservation.REFUSEE):
            raise TransitionStatutInvalideError(self.statut, StatutReservation.REFUSEE)

        self.statut = StatutReservation.REFUSEE
        self.valideur_id = valideur_id
        self.motif_refus = motif
        self.validated_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def annuler(self) -> None:
        """Annule la réservation.

        Raises:
            TransitionStatutInvalideError: Si la transition n'est pas autorisée
        """
        if not self.statut.peut_transitionner_vers(StatutReservation.ANNULEE):
            raise TransitionStatutInvalideError(self.statut, StatutReservation.ANNULEE)

        self.statut = StatutReservation.ANNULEE
        self.updated_at = datetime.utcnow()

    def chevauche(self, autre: "Reservation") -> bool:
        """Vérifie si cette réservation chevauche une autre.

        LOG-17: Conflit de réservation - Alerte si créneau déjà occupé.

        Deux réservations sont en conflit si:
        - Elles concernent la même ressource
        - Elles sont à la même date
        - Leurs créneaux horaires se chevauchent
        - Les deux sont actives (non annulées/refusées)
        """
        if self.ressource_id != autre.ressource_id:
            return False
        if self.date_reservation != autre.date_reservation:
            return False
        if not self.est_active or not autre.est_active:
            return False
        if self.id and autre.id and self.id == autre.id:
            return False

        return self.plage_horaire.chevauche(autre.plage_horaire)

    def to_dict(self) -> dict:
        """Convertit l'entité en dictionnaire."""
        return {
            "id": self.id,
            "ressource_id": self.ressource_id,
            "chantier_id": self.chantier_id,
            "demandeur_id": self.demandeur_id,
            "date_reservation": self.date_reservation.isoformat()
            if self.date_reservation
            else None,
            "heure_debut": self.heure_debut.isoformat() if self.heure_debut else None,
            "heure_fin": self.heure_fin.isoformat() if self.heure_fin else None,
            "statut": self.statut.value,
            "motif_refus": self.motif_refus,
            "commentaire": self.commentaire,
            "valideur_id": self.valideur_id,
            "validated_at": self.validated_at.isoformat()
            if self.validated_at
            else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
