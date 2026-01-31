"""Use Case: Générer un récapitulatif mensuel (GAP-FDH-008)."""

import calendar
from datetime import date, timedelta
from typing import Optional, Dict, List
from decimal import Decimal
from collections import defaultdict

from ...domain.repositories import PointageRepository, VariablePaieRepository
from ...domain.entities import Pointage
from ...domain.value_objects import Duree, StatutPointage, TypeVariablePaie
from ..dtos.monthly_recap_dtos import (
    GenerateMonthlyRecapDTO,
    MonthlyRecapDTO,
    WeeklySummary,
    VariablePaieSummary,
    AbsenceSummary,
)


class GenerateMonthlyRecapError(Exception):
    """Exception pour les erreurs de génération de récapitulatif."""

    def __init__(self, message: str = "Erreur lors de la génération du récapitulatif"):
        self.message = message
        super().__init__(self.message)


class GenerateMonthlyRecapUseCase:
    """
    Cas d'utilisation : Génération du récapitulatif mensuel (GAP-FDH-008).

    Permet de générer un récapitulatif complet des heures travaillées,
    heures supplémentaires, variables de paie et absences pour un
    utilisateur sur un mois donné.

    Le récapitulatif peut optionnellement être exporté en PDF.

    Attributes:
        pointage_repo: Repository pour accéder aux pointages.
        variable_paie_repo: Repository pour les variables de paie.
    """

    MONTH_LABELS = [
        "",
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre",
    ]

    def __init__(
        self,
        pointage_repo: PointageRepository,
        variable_paie_repo: VariablePaieRepository,
    ):
        """
        Initialise le use case.

        Args:
            pointage_repo: Repository pointages (interface).
            variable_paie_repo: Repository variables de paie (interface).
        """
        self.pointage_repo = pointage_repo
        self.variable_paie_repo = variable_paie_repo

    def execute(self, dto: GenerateMonthlyRecapDTO) -> MonthlyRecapDTO:
        """
        Exécute la génération du récapitulatif mensuel.

        Args:
            dto: Les données de génération.

        Returns:
            MonthlyRecapDTO contenant le récapitulatif complet.

        Raises:
            GenerateMonthlyRecapError: Si les paramètres sont invalides.
        """
        # 1. Validation des paramètres
        if dto.month < 1 or dto.month > 12:
            raise GenerateMonthlyRecapError("Le mois doit être compris entre 1 et 12")
        if dto.year < 2000 or dto.year > 2100:
            raise GenerateMonthlyRecapError("L'année doit être comprise entre 2000 et 2100")

        # 2. Calcule les dates de début et fin du mois
        date_debut = date(dto.year, dto.month, 1)
        last_day = calendar.monthrange(dto.year, dto.month)[1]
        date_fin = date(dto.year, dto.month, last_day)

        # 3. Récupère tous les pointages du mois
        pointages, _ = self.pointage_repo.search(
            utilisateur_id=dto.utilisateur_id,
            date_debut=date_debut,
            date_fin=date_fin,
            skip=0,
            limit=10000,  # Aucune limite pour le récap mensuel
        )

        # 4. Groupe les pointages par semaine
        weekly_summaries = self._build_weekly_summaries(pointages, dto.year, dto.month)

        # 5. Calcule les totaux mensuels
        heures_normales_total = Duree.zero()
        heures_supplementaires_total = Duree.zero()

        for summary in weekly_summaries:
            heures_normales_total += Duree.from_string(summary.heures_normales)
            heures_supplementaires_total += Duree.from_string(summary.heures_supplementaires)

        total_heures_month = heures_normales_total + heures_supplementaires_total

        # 6. Récupère et agrège les variables de paie
        variables_paie_summaries, variables_total = self._build_variables_paie_summaries(
            pointages
        )

        # 7. Récupère et agrège les absences
        absences_summaries = self._build_absences_summaries(pointages)

        # 8. Vérifie si tous les pointages sont validés
        all_validated = all(p.statut == StatutPointage.VALIDE for p in pointages)

        # 9. Génère le PDF si demandé
        pdf_path = None
        if dto.export_pdf:
            pdf_path = self._generate_pdf(
                dto.utilisateur_id,
                dto.year,
                dto.month,
                weekly_summaries,
                variables_paie_summaries,
                absences_summaries,
            )

        # 10. Construit le DTO de sortie
        return MonthlyRecapDTO(
            utilisateur_id=dto.utilisateur_id,
            utilisateur_nom=self._get_user_name(dto.utilisateur_id),
            year=dto.year,
            month=dto.month,
            month_label=f"{self.MONTH_LABELS[dto.month]} {dto.year}",
            weekly_summaries=weekly_summaries,
            heures_normales_total=str(heures_normales_total),
            heures_supplementaires_total=str(heures_supplementaires_total),
            total_heures_month=str(total_heures_month),
            heures_normales_total_decimal=heures_normales_total.decimal,
            heures_supplementaires_total_decimal=heures_supplementaires_total.decimal,
            total_heures_month_decimal=total_heures_month.decimal,
            variables_paie=variables_paie_summaries,
            variables_paie_total=variables_total,
            absences=absences_summaries,
            all_validated=all_validated,
            pdf_path=pdf_path,
        )

    def _build_weekly_summaries(
        self, pointages: List[Pointage], year: int, month: int
    ) -> List[WeeklySummary]:
        """
        Construit les résumés hebdomadaires à partir des pointages.

        Args:
            pointages: Liste des pointages du mois.
            year: Année.
            month: Mois.

        Returns:
            Liste des résumés hebdomadaires.
        """
        # Groupe les pointages par semaine
        weeks_dict: Dict[date, List[Pointage]] = defaultdict(list)

        for pointage in pointages:
            # Calcule le lundi de la semaine du pointage
            semaine_debut = self._get_monday(pointage.date_pointage)
            weeks_dict[semaine_debut].append(pointage)

        # Construit les résumés
        summaries = []
        for semaine_debut in sorted(weeks_dict.keys()):
            pointages_semaine = weeks_dict[semaine_debut]

            heures_normales = Duree.zero()
            heures_sup = Duree.zero()

            for p in pointages_semaine:
                heures_normales += p.heures_normales
                heures_sup += p.heures_supplementaires

            total_heures = heures_normales + heures_sup

            # Détermine le statut global de la semaine
            statut = self._calculate_weekly_status(pointages_semaine)

            summaries.append(
                WeeklySummary(
                    semaine_debut=semaine_debut,
                    numero_semaine=semaine_debut.isocalendar()[1],
                    heures_normales=str(heures_normales),
                    heures_supplementaires=str(heures_sup),
                    total_heures=str(total_heures),
                    heures_normales_decimal=heures_normales.decimal,
                    heures_supplementaires_decimal=heures_sup.decimal,
                    total_heures_decimal=total_heures.decimal,
                    statut=statut,
                )
            )

        return summaries

    def _build_variables_paie_summaries(
        self, pointages: List[Pointage]
    ) -> tuple[List[VariablePaieSummary], Decimal]:
        """
        Construit les résumés des variables de paie.

        Args:
            pointages: Liste des pointages du mois.

        Returns:
            Tuple (liste des résumés, montant total).
        """
        # Récupère toutes les variables de paie pour les pointages du mois
        pointage_ids = [p.id for p in pointages if p.id]
        if not pointage_ids:
            return [], Decimal("0.00")

        variables_dict: Dict[str, Dict] = defaultdict(
            lambda: {"count": 0, "values": [], "total": Decimal("0.00")}
        )

        for pointage_id in pointage_ids:
            variables = self.variable_paie_repo.find_by_pointage(pointage_id)
            for var in variables:
                # Ne comptabiliser que les variables de type montant (pas heures)
                type_var = TypeVariablePaie.from_string(var.type_variable)
                if type_var.is_amount:
                    variables_dict[var.type_variable]["count"] += 1
                    variables_dict[var.type_variable]["values"].append(var.valeur)
                    variables_dict[var.type_variable]["total"] += var.valeur

        # Construit les résumés
        summaries = []
        montant_total = Decimal("0.00")

        for type_var, data in sorted(variables_dict.items()):
            type_vo = TypeVariablePaie.from_string(type_var)

            # Vérifie si la valeur unitaire est constante
            values = data["values"]
            valeur_unitaire = values[0] if len(set(values)) == 1 else None

            summaries.append(
                VariablePaieSummary(
                    type_variable=type_var,
                    type_variable_libelle=type_vo.libelle,
                    nombre_occurrences=data["count"],
                    valeur_unitaire=valeur_unitaire,
                    montant_total=data["total"],
                )
            )

            montant_total += data["total"]

        return summaries, montant_total

    def _build_absences_summaries(self, pointages: List[Pointage]) -> List[AbsenceSummary]:
        """
        Construit les résumés des absences.

        Args:
            pointages: Liste des pointages du mois.

        Returns:
            Liste des résumés d'absences.
        """
        # Récupère toutes les variables de paie de type absence
        pointage_ids = [p.id for p in pointages if p.id]
        if not pointage_ids:
            return []

        absences_dict: Dict[str, Dict] = defaultdict(
            lambda: {"count": 0, "total_heures": Duree.zero()}
        )

        for pointage_id in pointage_ids:
            variables = self.variable_paie_repo.find_by_pointage(pointage_id)
            for var in variables:
                type_var = TypeVariablePaie.from_string(var.type_variable)
                if type_var.is_absence:
                    absences_dict[var.type_variable]["count"] += 1
                    # Convertit la valeur en Duree (valeur stockée en décimal)
                    heures = Duree.from_decimal(float(var.valeur))
                    absences_dict[var.type_variable]["total_heures"] += heures

        # Construit les résumés
        summaries = []
        for type_abs, data in sorted(absences_dict.items()):
            type_vo = TypeVariablePaie.from_string(type_abs)

            summaries.append(
                AbsenceSummary(
                    type_absence=type_abs,
                    type_absence_libelle=type_vo.libelle,
                    nombre_jours=data["count"],
                    total_heures=str(data["total_heures"]),
                    total_heures_decimal=data["total_heures"].decimal,
                )
            )

        return summaries

    def _calculate_weekly_status(self, pointages: List[Pointage]) -> str:
        """Calcule le statut global d'une semaine selon les règles métier."""
        if not pointages:
            return "vide"

        has_rejected = any(p.statut == StatutPointage.REJETE for p in pointages)
        has_brouillon = any(p.statut == StatutPointage.BROUILLON for p in pointages)
        has_soumis = any(p.statut == StatutPointage.SOUMIS for p in pointages)
        all_validated = all(p.statut == StatutPointage.VALIDE for p in pointages)

        if has_rejected:
            return "rejete"
        if has_brouillon:
            return "brouillon"
        if has_soumis:
            return "soumis"
        if all_validated:
            return "valide"
        return "inconnu"

    def _get_monday(self, d: date) -> date:
        """Retourne le lundi de la semaine contenant la date donnée."""
        # weekday(): 0 = lundi, 6 = dimanche
        days_since_monday = d.weekday()
        return d - timedelta(days=days_since_monday)

    def _get_user_name(self, utilisateur_id: int) -> str:
        """Récupère le nom complet d'un utilisateur."""
        # TODO: Implémenter via EntityInfoService quand disponible
        return f"Utilisateur {utilisateur_id}"

    def _generate_pdf(
        self,
        utilisateur_id: int,
        year: int,
        month: int,
        weekly_summaries: List[WeeklySummary],
        variables_paie: List[VariablePaieSummary],
        absences: List[AbsenceSummary],
    ) -> Optional[str]:
        """
        Génère un export PDF du récapitulatif.

        Args:
            utilisateur_id: ID de l'utilisateur.
            year: Année.
            month: Mois.
            weekly_summaries: Résumés hebdomadaires.
            variables_paie: Variables de paie.
            absences: Absences.

        Returns:
            Chemin du fichier PDF généré.

        Note:
            Pour l'instant, retourne None (fonctionnalité optionnelle à implémenter).
            Peut utiliser reportlab ou weasyprint pour la génération PDF.
        """
        # TODO: Implémenter génération PDF avec reportlab ou weasyprint
        # Exemple: /tmp/recap_mensuel_user7_2026_01.pdf
        return None
