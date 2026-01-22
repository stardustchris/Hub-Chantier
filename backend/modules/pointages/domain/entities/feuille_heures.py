"""Entité FeuilleHeures - Agrégat représentant une feuille d'heures hebdomadaire."""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
from decimal import Decimal

from ..value_objects import StatutPointage, Duree, TypeVariablePaie
from .pointage import Pointage
from .variable_paie import VariablePaie


@dataclass
class FeuilleHeures:
    """
    Représente une feuille d'heures hebdomadaire.

    Agrégat principal du module pointages selon CDC Section 7.
    Regroupe tous les pointages d'un utilisateur pour une semaine.

    Fonctionnalités couvertes:
    - FDH-02: Navigation par semaine
    - FDH-05: Vue tabulaire hebdomadaire (Lundi à Vendredi)
    - FDH-06: Multi-chantiers par utilisateur
    - FDH-08: Total par ligne
    - FDH-09: Total groupe
    - FDH-13: Variables de paie

    Attributes:
        id: Identifiant unique.
        utilisateur_id: ID de l'utilisateur.
        semaine_debut: Date du lundi de la semaine.
        annee: Année (ex: 2026).
        numero_semaine: Numéro de la semaine (1-53).
        pointages: Liste des pointages de la semaine.
        variables_paie: Variables de paie de la semaine.
        statut_global: Statut global de la feuille.
        commentaire_global: Commentaire de la feuille.
        created_at: Date de création.
        updated_at: Date de modification.
    """

    utilisateur_id: int
    semaine_debut: date  # Toujours un lundi
    annee: int
    numero_semaine: int

    # Collections
    pointages: List[Pointage] = field(default_factory=list)
    variables_paie: List[VariablePaie] = field(default_factory=list)

    # Statut global
    statut_global: StatutPointage = StatutPointage.BROUILLON
    commentaire_global: Optional[str] = None

    # Métadonnées
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Données chargées
    _utilisateur_nom: Optional[str] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Valide les données."""
        if self.utilisateur_id <= 0:
            raise ValueError("L'ID utilisateur doit être positif")

        # Vérifie que semaine_debut est un lundi
        if self.semaine_debut.weekday() != 0:
            raise ValueError("semaine_debut doit être un lundi")

        # Valide année et numéro de semaine
        if self.annee < 2000 or self.annee > 2100:
            raise ValueError("Année invalide")
        if self.numero_semaine < 1 or self.numero_semaine > 53:
            raise ValueError("Numéro de semaine invalide (1-53)")

    @classmethod
    def for_week(cls, utilisateur_id: int, date_in_week: date) -> "FeuilleHeures":
        """
        Crée une feuille pour la semaine contenant la date donnée.

        Args:
            utilisateur_id: ID de l'utilisateur.
            date_in_week: Une date dans la semaine désirée.

        Returns:
            Une nouvelle FeuilleHeures.
        """
        # Trouve le lundi de la semaine
        days_since_monday = date_in_week.weekday()
        monday = date_in_week - timedelta(days=days_since_monday)

        # Calcule le numéro de semaine ISO
        iso_calendar = monday.isocalendar()
        annee = iso_calendar[0]
        numero_semaine = iso_calendar[1]

        return cls(
            utilisateur_id=utilisateur_id,
            semaine_debut=monday,
            annee=annee,
            numero_semaine=numero_semaine,
        )

    @property
    def semaine_fin(self) -> date:
        """Retourne le dimanche de la semaine."""
        return self.semaine_debut + timedelta(days=6)

    @property
    def jours_semaine(self) -> List[date]:
        """Retourne les 7 jours de la semaine (lundi à dimanche)."""
        return [self.semaine_debut + timedelta(days=i) for i in range(7)]

    @property
    def jours_travailles(self) -> List[date]:
        """Retourne les 5 jours ouvrés (lundi à vendredi)."""
        return [self.semaine_debut + timedelta(days=i) for i in range(5)]

    @property
    def utilisateur_nom(self) -> Optional[str]:
        """Nom de l'utilisateur."""
        return self._utilisateur_nom

    @utilisateur_nom.setter
    def utilisateur_nom(self, value: str) -> None:
        """Définit le nom de l'utilisateur."""
        self._utilisateur_nom = value

    @property
    def label_semaine(self) -> str:
        """Retourne le label de la semaine (ex: 'Semaine 3 - 2026')."""
        return f"Semaine {self.numero_semaine} - {self.annee}"

    # ===== Calculs des totaux (FDH-08, FDH-09) =====

    @property
    def total_heures_normales(self) -> Duree:
        """Total des heures normales de la semaine."""
        total = Duree.zero()
        for p in self.pointages:
            total = total + p.heures_normales
        return total

    @property
    def total_heures_supplementaires(self) -> Duree:
        """Total des heures supplémentaires de la semaine."""
        total = Duree.zero()
        for p in self.pointages:
            total = total + p.heures_supplementaires
        return total

    @property
    def total_heures(self) -> Duree:
        """Total de toutes les heures de la semaine."""
        return self.total_heures_normales + self.total_heures_supplementaires

    @property
    def total_heures_decimal(self) -> float:
        """Total des heures en décimal."""
        return self.total_heures.decimal

    def total_heures_par_jour(self) -> Dict[date, Duree]:
        """
        Calcule le total des heures par jour.

        Returns:
            Dictionnaire date -> Duree.
        """
        totaux: Dict[date, Duree] = {}
        for jour in self.jours_semaine:
            totaux[jour] = Duree.zero()

        for p in self.pointages:
            if p.date_pointage in totaux:
                totaux[p.date_pointage] = totaux[p.date_pointage] + p.total_heures

        return totaux

    def total_heures_par_chantier(self) -> Dict[int, Duree]:
        """
        Calcule le total des heures par chantier (FDH-08).

        Returns:
            Dictionnaire chantier_id -> Duree.
        """
        totaux: Dict[int, Duree] = {}
        for p in self.pointages:
            if p.chantier_id not in totaux:
                totaux[p.chantier_id] = Duree.zero()
            totaux[p.chantier_id] = totaux[p.chantier_id] + p.total_heures
        return totaux

    def get_chantiers_ids(self) -> List[int]:
        """Retourne la liste des IDs de chantiers (FDH-06)."""
        return list(set(p.chantier_id for p in self.pointages))

    # ===== Variables de paie (FDH-13) =====

    def total_variable_paie(self, type_variable: TypeVariablePaie) -> Decimal:
        """
        Calcule le total d'un type de variable de paie.

        Args:
            type_variable: Le type de variable.

        Returns:
            Total de la variable.
        """
        total = Decimal("0")
        for v in self.variables_paie:
            if v.type_variable == type_variable:
                total += v.valeur
        return total

    def get_variables_par_type(self) -> Dict[TypeVariablePaie, Decimal]:
        """
        Retourne toutes les variables de paie par type.

        Returns:
            Dictionnaire type -> total.
        """
        totaux: Dict[TypeVariablePaie, Decimal] = {}
        for v in self.variables_paie:
            if v.type_variable not in totaux:
                totaux[v.type_variable] = Decimal("0")
            totaux[v.type_variable] += v.valeur
        return totaux

    # ===== Gestion des pointages =====

    def ajouter_pointage(self, pointage: Pointage) -> None:
        """
        Ajoute un pointage à la feuille.

        Args:
            pointage: Le pointage à ajouter.

        Raises:
            ValueError: Si le pointage n'appartient pas à cette semaine/utilisateur.
        """
        if pointage.utilisateur_id != self.utilisateur_id:
            raise ValueError("Le pointage n'appartient pas au même utilisateur")

        if not (self.semaine_debut <= pointage.date_pointage <= self.semaine_fin):
            raise ValueError(
                f"La date {pointage.date_pointage} n'est pas dans la semaine "
                f"({self.semaine_debut} - {self.semaine_fin})"
            )

        self.pointages.append(pointage)
        self.updated_at = datetime.now()

    def get_pointage(self, date_pointage: date, chantier_id: int) -> Optional[Pointage]:
        """
        Trouve un pointage par date et chantier.

        Args:
            date_pointage: La date du pointage.
            chantier_id: L'ID du chantier.

        Returns:
            Le pointage trouvé ou None.
        """
        for p in self.pointages:
            if p.date_pointage == date_pointage and p.chantier_id == chantier_id:
                return p
        return None

    def get_pointages_jour(self, date_pointage: date) -> List[Pointage]:
        """
        Retourne tous les pointages pour un jour donné.

        Args:
            date_pointage: La date.

        Returns:
            Liste des pointages du jour.
        """
        return [p for p in self.pointages if p.date_pointage == date_pointage]

    def get_pointages_chantier(self, chantier_id: int) -> List[Pointage]:
        """
        Retourne tous les pointages pour un chantier donné.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Liste des pointages du chantier.
        """
        return [p for p in self.pointages if p.chantier_id == chantier_id]

    # ===== Variables de paie =====

    def ajouter_variable_paie(self, variable: VariablePaie) -> None:
        """
        Ajoute une variable de paie.

        Args:
            variable: La variable à ajouter.
        """
        self.variables_paie.append(variable)
        self.updated_at = datetime.now()

    # ===== Workflow de validation =====

    @property
    def is_complete(self) -> bool:
        """Vérifie si tous les jours ouvrés ont au moins un pointage."""
        jours_pointes = set(p.date_pointage for p in self.pointages)
        for jour in self.jours_travailles:
            if jour not in jours_pointes:
                return False
        return True

    @property
    def is_all_validated(self) -> bool:
        """Vérifie si tous les pointages sont validés."""
        if not self.pointages:
            return False
        return all(p.is_validated for p in self.pointages)

    @property
    def has_pending_validation(self) -> bool:
        """Vérifie s'il y a des pointages en attente de validation."""
        return any(p.statut == StatutPointage.SOUMIS for p in self.pointages)

    @property
    def has_rejected(self) -> bool:
        """Vérifie s'il y a des pointages rejetés."""
        return any(p.statut == StatutPointage.REJETE for p in self.pointages)

    def calculer_statut_global(self) -> StatutPointage:
        """
        Calcule le statut global basé sur les pointages.

        Returns:
            Le statut global de la feuille.
        """
        if not self.pointages:
            return StatutPointage.BROUILLON

        statuts = [p.statut for p in self.pointages]

        # Tous validés = validé
        if all(s == StatutPointage.VALIDE for s in statuts):
            return StatutPointage.VALIDE

        # Au moins un rejeté = rejeté
        if any(s == StatutPointage.REJETE for s in statuts):
            return StatutPointage.REJETE

        # Au moins un soumis (et pas de rejeté) = soumis
        if any(s == StatutPointage.SOUMIS for s in statuts):
            return StatutPointage.SOUMIS

        # Sinon brouillon
        return StatutPointage.BROUILLON

    def mettre_a_jour_statut_global(self) -> None:
        """Met à jour le statut global basé sur les pointages."""
        self.statut_global = self.calculer_statut_global()
        self.updated_at = datetime.now()

    def __eq__(self, other: object) -> bool:
        """Égalité basée sur l'ID."""
        if not isinstance(other, FeuilleHeures):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
