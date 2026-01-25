"""Entite Intervention.

INT-01 a INT-17: Gestion des interventions ponctuelles (SAV, maintenance, depannages).
"""

from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import Optional, List

from ..value_objects import StatutIntervention, PrioriteIntervention, TypeIntervention


class TransitionStatutInvalideError(Exception):
    """Erreur levee lors d'une transition de statut invalide."""

    def __init__(
        self, statut_actuel: StatutIntervention, statut_cible: StatutIntervention
    ):
        self.statut_actuel = statut_actuel
        self.statut_cible = statut_cible
        super().__init__(
            f"Transition invalide: {statut_actuel.label} -> {statut_cible.label}"
        )


@dataclass
class Intervention:
    """Entite representant une intervention ponctuelle.

    Selon CDC Section 12 - Gestion des Interventions (INT-01 a INT-17).
    Une intervention est distincte d'un chantier: duree courte (heures/jours),
    1-2 techniciens, ponctuelle, utilisee pour SAV/maintenance/depannage.

    Attributes:
        id: Identifiant unique.
        code: Code unique de l'intervention (ex: INT-2026-0001).
        type_intervention: Type (SAV, maintenance, depannage, etc.).
        statut: Statut actuel de l'intervention.
        priorite: Niveau de priorite.
        client_nom: Nom du client.
        client_adresse: Adresse complete.
        client_telephone: Telephone du contact.
        client_email: Email du contact (optionnel).
        description: Description du motif de l'intervention.
        date_souhaitee: Date souhaitee pour l'intervention.
        date_planifiee: Date effectivement planifiee.
        heure_debut: Heure de debut planifiee.
        heure_fin: Heure de fin planifiee.
        heure_debut_reelle: Heure de debut effective.
        heure_fin_reelle: Heure de fin effective.
        travaux_realises: Detail des travaux effectues.
        anomalies: Problemes constates non resolus.
        chantier_origine_id: ID du chantier d'origine (optionnel, pour SAV).
        created_by: ID de l'utilisateur createur.
        created_at: Date de creation.
        updated_at: Date de derniere modification.
    """

    # Champs obligatoires
    type_intervention: TypeIntervention
    client_nom: str
    client_adresse: str
    description: str
    created_by: int

    # Champs avec valeurs par defaut
    id: Optional[int] = None
    code: Optional[str] = None
    statut: StatutIntervention = StatutIntervention.A_PLANIFIER
    priorite: PrioriteIntervention = PrioriteIntervention.NORMALE
    client_telephone: Optional[str] = None
    client_email: Optional[str] = None
    date_souhaitee: Optional[date] = None
    date_planifiee: Optional[date] = None
    heure_debut: Optional[time] = None
    heure_fin: Optional[time] = None
    heure_debut_reelle: Optional[time] = None
    heure_fin_reelle: Optional[time] = None
    travaux_realises: Optional[str] = None
    anomalies: Optional[str] = None
    chantier_origine_id: Optional[int] = None
    rapport_genere: bool = False
    rapport_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    # Soft delete
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if not self.client_nom or not self.client_nom.strip():
            raise ValueError("Le nom du client est obligatoire")
        if not self.client_adresse or not self.client_adresse.strip():
            raise ValueError("L'adresse du client est obligatoire")
        if not self.description or not self.description.strip():
            raise ValueError("La description est obligatoire")
        if self.created_by <= 0:
            raise ValueError("L'ID du createur doit etre positif")

        # Normalisation
        self.client_nom = self.client_nom.strip()
        self.client_adresse = self.client_adresse.strip()
        self.description = self.description.strip()

        # Validation horaires
        if self.heure_debut and self.heure_fin:
            if self.heure_fin <= self.heure_debut:
                raise ValueError(
                    "L'heure de fin doit etre posterieure a l'heure de debut"
                )

    @property
    def est_planifiee(self) -> bool:
        """Verifie si l'intervention a ete planifiee."""
        return self.date_planifiee is not None

    @property
    def est_terminee(self) -> bool:
        """Verifie si l'intervention est terminee."""
        return self.statut == StatutIntervention.TERMINEE

    @property
    def est_annulee(self) -> bool:
        """Verifie si l'intervention est annulee."""
        return self.statut == StatutIntervention.ANNULEE

    @property
    def est_active(self) -> bool:
        """Verifie si l'intervention est active."""
        return self.statut.est_active and not self.est_supprimee

    @property
    def est_supprimee(self) -> bool:
        """Verifie si l'intervention a ete supprimee (soft delete)."""
        return self.deleted_at is not None

    @property
    def duree_prevue_minutes(self) -> Optional[int]:
        """Calcule la duree prevue en minutes."""
        if not self.heure_debut or not self.heure_fin:
            return None
        debut = datetime.combine(date.today(), self.heure_debut)
        fin = datetime.combine(date.today(), self.heure_fin)
        return int((fin - debut).total_seconds() / 60)

    @property
    def duree_reelle_minutes(self) -> Optional[int]:
        """Calcule la duree reelle en minutes."""
        if not self.heure_debut_reelle or not self.heure_fin_reelle:
            return None
        debut = datetime.combine(date.today(), self.heure_debut_reelle)
        fin = datetime.combine(date.today(), self.heure_fin_reelle)
        return int((fin - debut).total_seconds() / 60)

    @property
    def horaires_str(self) -> Optional[str]:
        """Retourne les horaires planifies sous forme de chaine."""
        if not self.heure_debut or not self.heure_fin:
            return None
        return f"{self.heure_debut.strftime('%H:%M')} - {self.heure_fin.strftime('%H:%M')}"

    def planifier(
        self,
        date_planifiee: date,
        heure_debut: Optional[time] = None,
        heure_fin: Optional[time] = None,
    ) -> None:
        """Planifie l'intervention.

        INT-05: Transition A_PLANIFIER -> PLANIFIEE

        Args:
            date_planifiee: Date de l'intervention.
            heure_debut: Heure de debut (optionnel).
            heure_fin: Heure de fin (optionnel).
        """
        if heure_debut and heure_fin and heure_fin <= heure_debut:
            raise ValueError(
                "L'heure de fin doit etre posterieure a l'heure de debut"
            )

        self.date_planifiee = date_planifiee
        self.heure_debut = heure_debut
        self.heure_fin = heure_fin

        if self.statut == StatutIntervention.A_PLANIFIER:
            self.statut = StatutIntervention.PLANIFIEE

        self.updated_at = datetime.utcnow()

    def demarrer(self, heure_debut_reelle: Optional[time] = None) -> None:
        """Demarre l'intervention.

        INT-05: Transition PLANIFIEE -> EN_COURS
        """
        if not self.statut.peut_transitionner_vers(StatutIntervention.EN_COURS):
            raise TransitionStatutInvalideError(
                self.statut, StatutIntervention.EN_COURS
            )

        self.statut = StatutIntervention.EN_COURS
        self.heure_debut_reelle = heure_debut_reelle or datetime.utcnow().time()
        self.updated_at = datetime.utcnow()

    def terminer(
        self,
        heure_fin_reelle: Optional[time] = None,
        travaux_realises: Optional[str] = None,
        anomalies: Optional[str] = None,
    ) -> None:
        """Termine l'intervention.

        INT-05: Transition EN_COURS -> TERMINEE

        Args:
            heure_fin_reelle: Heure de fin effective.
            travaux_realises: Description des travaux realises.
            anomalies: Problemes constates non resolus.
        """
        if not self.statut.peut_transitionner_vers(StatutIntervention.TERMINEE):
            raise TransitionStatutInvalideError(
                self.statut, StatutIntervention.TERMINEE
            )

        self.statut = StatutIntervention.TERMINEE
        self.heure_fin_reelle = heure_fin_reelle or datetime.utcnow().time()
        if travaux_realises:
            self.travaux_realises = travaux_realises.strip()
        if anomalies:
            self.anomalies = anomalies.strip()
        self.updated_at = datetime.utcnow()

    def annuler(self) -> None:
        """Annule l'intervention.

        INT-05: Transition vers ANNULEE
        """
        if not self.statut.peut_transitionner_vers(StatutIntervention.ANNULEE):
            raise TransitionStatutInvalideError(
                self.statut, StatutIntervention.ANNULEE
            )

        self.statut = StatutIntervention.ANNULEE
        self.updated_at = datetime.utcnow()

    def supprimer(self, deleted_by: int) -> None:
        """Marque l'intervention comme supprimee (soft delete)."""
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    def marquer_rapport_genere(self, rapport_url: str) -> None:
        """Marque le rapport comme genere.

        INT-14: Rapport PDF - Generation automatique
        """
        self.rapport_genere = True
        self.rapport_url = rapport_url
        self.updated_at = datetime.utcnow()

    def modifier_priorite(self, nouvelle_priorite: PrioriteIntervention) -> None:
        """Modifie la priorite de l'intervention."""
        self.priorite = nouvelle_priorite
        self.updated_at = datetime.utcnow()

    def modifier_description(self, description: str) -> None:
        """Modifie la description de l'intervention."""
        if not description or not description.strip():
            raise ValueError("La description ne peut pas etre vide")
        self.description = description.strip()
        self.updated_at = datetime.utcnow()

    def modifier_client(
        self,
        nom: Optional[str] = None,
        adresse: Optional[str] = None,
        telephone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        """Modifie les informations client."""
        if nom is not None:
            if not nom.strip():
                raise ValueError("Le nom du client ne peut pas etre vide")
            self.client_nom = nom.strip()
        if adresse is not None:
            if not adresse.strip():
                raise ValueError("L'adresse ne peut pas etre vide")
            self.client_adresse = adresse.strip()
        if telephone is not None:
            self.client_telephone = telephone.strip() if telephone.strip() else None
        if email is not None:
            self.client_email = email.strip() if email.strip() else None
        self.updated_at = datetime.utcnow()

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID."""
        if not isinstance(other, Intervention):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))

    def __str__(self) -> str:
        """Representation textuelle."""
        return (
            f"Intervention {self.code or 'N/A'}: {self.type_intervention.label} - "
            f"{self.client_nom} ({self.statut.label})"
        )

    def __repr__(self) -> str:
        """Representation technique."""
        return (
            f"Intervention(id={self.id}, code={self.code}, "
            f"type={self.type_intervention.value}, statut={self.statut.value})"
        )
