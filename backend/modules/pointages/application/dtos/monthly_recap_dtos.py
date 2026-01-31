"""DTOs pour le récapitulatif mensuel (GAP-FDH-008)."""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional
from decimal import Decimal


@dataclass
class GenerateMonthlyRecapDTO:
    """
    DTO pour la génération d'un récapitulatif mensuel.

    Attributes:
        utilisateur_id: ID de l'utilisateur.
        year: Année.
        month: Mois (1-12).
        export_pdf: True pour générer un export PDF (optionnel).
    """

    utilisateur_id: int
    year: int
    month: int
    export_pdf: bool = False


@dataclass
class WeeklySummary:
    """
    Résumé hebdomadaire pour le récapitulatif mensuel.

    Attributes:
        semaine_debut: Date du lundi de la semaine.
        numero_semaine: Numéro de la semaine ISO.
        heures_normales: Total heures normales (format HH:MM).
        heures_supplementaires: Total heures sup (format HH:MM).
        total_heures: Total général (format HH:MM).
        heures_normales_decimal: Heures normales en décimal.
        heures_supplementaires_decimal: Heures sup en décimal.
        total_heures_decimal: Total en décimal.
        statut: Statut global de la semaine.
    """

    semaine_debut: date
    numero_semaine: int
    heures_normales: str
    heures_supplementaires: str
    total_heures: str
    heures_normales_decimal: float
    heures_supplementaires_decimal: float
    total_heures_decimal: float
    statut: str


@dataclass
class VariablePaieSummary:
    """
    Résumé d'une variable de paie pour le mois.

    Attributes:
        type_variable: Type de variable.
        type_variable_libelle: Libellé de la variable.
        nombre_occurrences: Nombre de fois où la variable apparaît.
        valeur_unitaire: Valeur unitaire (si constante).
        montant_total: Montant total pour le mois.
    """

    type_variable: str
    type_variable_libelle: str
    nombre_occurrences: int
    valeur_unitaire: Optional[Decimal]
    montant_total: Decimal


@dataclass
class AbsenceSummary:
    """
    Résumé des absences pour le mois.

    Attributes:
        type_absence: Type d'absence.
        type_absence_libelle: Libellé de l'absence.
        nombre_jours: Nombre de jours d'absence.
        total_heures: Total heures d'absence (format HH:MM).
        total_heures_decimal: Total heures en décimal.
    """

    type_absence: str
    type_absence_libelle: str
    nombre_jours: int
    total_heures: str
    total_heures_decimal: float


@dataclass
class MonthlyRecapDTO:
    """
    Récapitulatif mensuel complet.

    Attributes:
        utilisateur_id: ID de l'utilisateur.
        utilisateur_nom: Nom complet de l'utilisateur.
        year: Année.
        month: Mois.
        month_label: Libellé du mois (ex: "Janvier 2026").
        weekly_summaries: Résumés hebdomadaires.
        heures_normales_total: Total heures normales (format HH:MM).
        heures_supplementaires_total: Total heures sup (format HH:MM).
        total_heures_month: Total général (format HH:MM).
        heures_normales_total_decimal: Heures normales en décimal.
        heures_supplementaires_total_decimal: Heures sup en décimal.
        total_heures_month_decimal: Total en décimal.
        variables_paie: Résumé des variables de paie.
        variables_paie_total: Montant total des variables.
        absences: Résumé des absences.
        all_validated: True si tous les pointages sont validés.
        pdf_path: Chemin du PDF généré (si export_pdf=True).
    """

    utilisateur_id: int
    utilisateur_nom: str
    year: int
    month: int
    month_label: str
    weekly_summaries: List[WeeklySummary]
    heures_normales_total: str
    heures_supplementaires_total: str
    total_heures_month: str
    heures_normales_total_decimal: float
    heures_supplementaires_total_decimal: float
    total_heures_month_decimal: float
    variables_paie: List[VariablePaieSummary]
    variables_paie_total: Decimal
    absences: List[AbsenceSummary]
    all_validated: bool
    pdf_path: Optional[str] = None
