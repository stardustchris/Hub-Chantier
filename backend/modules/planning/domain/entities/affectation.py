"""Entité Affectation - Représente une affectation d'un utilisateur à un chantier."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List

from ..value_objects import CreneauHoraire, TypeRecurrence


@dataclass
class Affectation:
    """
    Entité représentant une affectation d'un utilisateur à un chantier.

    Selon CDC Section 5 - Planning Opérationnel (PLN-01 à PLN-28).
    Section 5.4 - Structure d'une affectation.

    Attributes:
        id: Identifiant unique (None si non persisté).
        utilisateur_id: ID de l'utilisateur affecté (obligatoire).
        chantier_id: ID du chantier d'affectation (obligatoire).
        date_affectation: Jour de l'affectation (obligatoire).
        creneau: Créneau horaire (heure début/fin, optionnel).
        note: Commentaire privé pour l'affecté (PLN-25).
        recurrence: Type de récurrence (unique par défaut).
        jours_recurrence: Jours de répétition si récurrence hebdomadaire (0=lundi, 6=dimanche).
        date_fin_recurrence: Date de fin de la récurrence (optionnel).
        created_by: ID de l'utilisateur qui a créé l'affectation.
        created_at: Date de création.
        updated_at: Date de dernière modification.
    """

    # Champs obligatoires
    utilisateur_id: int
    chantier_id: int
    date_affectation: date

    # Champs optionnels
    id: Optional[int] = None
    creneau: Optional[CreneauHoraire] = None
    note: Optional[str] = None
    recurrence: TypeRecurrence = TypeRecurrence.UNIQUE
    jours_recurrence: List[int] = field(default_factory=list)
    date_fin_recurrence: Optional[date] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validation des données."""
        if self.utilisateur_id <= 0:
            raise ValueError("L'ID de l'utilisateur doit être positif")
        if self.chantier_id <= 0:
            raise ValueError("L'ID du chantier doit être positif")

        # Valider les jours de récurrence (0-6)
        for jour in self.jours_recurrence:
            if jour < 0 or jour > 6:
                raise ValueError(
                    f"Jour de récurrence invalide: {jour}. "
                    "Doit être entre 0 (lundi) et 6 (dimanche)"
                )

        # Si récurrence avec date fin, vérifier cohérence
        if self.date_fin_recurrence and self.date_fin_recurrence < self.date_affectation:
            raise ValueError(
                "La date de fin de récurrence ne peut pas être "
                "antérieure à la date d'affectation"
            )

    def est_recurrente(self) -> bool:
        """Vérifie si l'affectation est récurrente."""
        return self.recurrence != TypeRecurrence.UNIQUE

    def modifier_creneau(self, creneau: CreneauHoraire) -> "Affectation":
        """
        Modifie le créneau horaire de l'affectation.

        Args:
            creneau: Nouveau créneau horaire.

        Returns:
            Nouvelle instance avec le créneau modifié.
        """
        return Affectation(
            id=self.id,
            utilisateur_id=self.utilisateur_id,
            chantier_id=self.chantier_id,
            date_affectation=self.date_affectation,
            creneau=creneau,
            note=self.note,
            recurrence=self.recurrence,
            jours_recurrence=self.jours_recurrence,
            date_fin_recurrence=self.date_fin_recurrence,
            created_by=self.created_by,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def ajouter_note(self, note: str) -> "Affectation":
        """
        Ajoute ou modifie la note de l'affectation (PLN-25).

        Args:
            note: Commentaire privé pour l'affecté.

        Returns:
            Nouvelle instance avec la note modifiée.
        """
        return Affectation(
            id=self.id,
            utilisateur_id=self.utilisateur_id,
            chantier_id=self.chantier_id,
            date_affectation=self.date_affectation,
            creneau=self.creneau,
            note=note,
            recurrence=self.recurrence,
            jours_recurrence=self.jours_recurrence,
            date_fin_recurrence=self.date_fin_recurrence,
            created_by=self.created_by,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def deplacer(self, nouvelle_date: date, nouveau_chantier_id: Optional[int] = None) -> "Affectation":
        """
        Déplace l'affectation (PLN-27: Drag & Drop).

        Args:
            nouvelle_date: Nouvelle date d'affectation.
            nouveau_chantier_id: Nouvel ID de chantier (optionnel).

        Returns:
            Nouvelle instance avec la date/chantier modifiés.
        """
        return Affectation(
            id=self.id,
            utilisateur_id=self.utilisateur_id,
            chantier_id=nouveau_chantier_id or self.chantier_id,
            date_affectation=nouvelle_date,
            creneau=self.creneau,
            note=self.note,
            recurrence=TypeRecurrence.UNIQUE,  # Déplacement = plus de récurrence
            jours_recurrence=[],
            date_fin_recurrence=None,
            created_by=self.created_by,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def dupliquer_pour_date(self, nouvelle_date: date) -> "Affectation":
        """
        Duplique l'affectation pour une autre date (PLN-16).

        Args:
            nouvelle_date: Date de la nouvelle affectation.

        Returns:
            Nouvelle instance (sans ID) pour la nouvelle date.
        """
        return Affectation(
            utilisateur_id=self.utilisateur_id,
            chantier_id=self.chantier_id,
            date_affectation=nouvelle_date,
            creneau=self.creneau,
            note=self.note,
            recurrence=TypeRecurrence.UNIQUE,
            created_by=self.created_by,
        )

    def __eq__(self, other: object) -> bool:
        """Deux affectations sont égales si elles ont le même ID."""
        if not isinstance(other, Affectation):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id) if self.id else hash(
            (self.utilisateur_id, self.chantier_id, self.date_affectation)
        )
