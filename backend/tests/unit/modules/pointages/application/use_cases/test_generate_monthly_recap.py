"""Tests unitaires pour GenerateMonthlyRecapUseCase (GAP-FDH-008)."""

import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch, PropertyMock

from modules.pointages.application.use_cases.generate_monthly_recap import (
    GenerateMonthlyRecapUseCase,
    GenerateMonthlyRecapError,
)
from modules.pointages.application.dtos.monthly_recap_dtos import (
    GenerateMonthlyRecapDTO,
)
from modules.pointages.domain.entities.pointage import Pointage
from modules.pointages.domain.entities.variable_paie import VariablePaie
from modules.pointages.domain.value_objects import Duree, StatutPointage


class TestGenerateMonthlyRecapUseCase:
    """Tests pour le use case de récapitulatif mensuel."""

    def setup_method(self):
        """Configure les mocks pour chaque test."""
        self.pointage_repo = Mock()
        self.variable_paie_repo = Mock()
        self.use_case = GenerateMonthlyRecapUseCase(
            pointage_repo=self.pointage_repo,
            variable_paie_repo=self.variable_paie_repo,
        )

    def test_generate_recap_success_simple(self):
        """Test nominal: génération réussie d'un récapitulatif simple."""
        # Arrange
        pointages = [
            Pointage(
                id=1,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 1, 6),  # Lundi semaine 2
                heures_normales=Duree(7, 30),
                heures_supplementaires=Duree(0, 0),
                statut=StatutPointage.VALIDE,
            ),
            Pointage(
                id=2,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 1, 7),  # Mardi semaine 2
                heures_normales=Duree(8, 0),
                heures_supplementaires=Duree(1, 0),
                statut=StatutPointage.VALIDE,
            ),
        ]

        self.pointage_repo.search.return_value = (pointages, 2)
        self.variable_paie_repo.find_by_pointage.return_value = []

        dto = GenerateMonthlyRecapDTO(utilisateur_id=7, year=2026, month=1)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.utilisateur_id == 7
        assert result.year == 2026
        assert result.month == 1
        assert result.month_label == "Janvier 2026"
        assert result.heures_normales_total == "15:30"
        assert result.heures_supplementaires_total == "01:00"
        assert result.total_heures_month == "16:30"
        assert result.all_validated is True
        assert len(result.weekly_summaries) == 1
        assert result.weekly_summaries[0].numero_semaine == 2
        assert result.weekly_summaries[0].heures_normales == "15:30"
        assert result.weekly_summaries[0].statut == "valide"
        assert result.pdf_path is None

    def test_generate_recap_invalid_month(self):
        """Test: erreur si mois invalide."""
        # Arrange
        dto = GenerateMonthlyRecapDTO(utilisateur_id=7, year=2026, month=13)

        # Act & Assert
        with pytest.raises(GenerateMonthlyRecapError) as exc_info:
            self.use_case.execute(dto)

        assert "mois doit être compris entre 1 et 12" in str(exc_info.value).lower()

    def test_generate_recap_invalid_year(self):
        """Test: erreur si année invalide."""
        # Arrange
        dto = GenerateMonthlyRecapDTO(utilisateur_id=7, year=1999, month=1)

        # Act & Assert
        with pytest.raises(GenerateMonthlyRecapError) as exc_info:
            self.use_case.execute(dto)

        assert "année doit être comprise entre 2000 et 2100" in str(exc_info.value).lower()

    def test_generate_recap_no_pointages(self):
        """Test: récapitulatif vide si aucun pointage."""
        # Arrange
        self.pointage_repo.search.return_value = ([], 0)

        dto = GenerateMonthlyRecapDTO(utilisateur_id=7, year=2026, month=1)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.utilisateur_id == 7
        assert result.heures_normales_total == "00:00"
        assert result.heures_supplementaires_total == "00:00"
        assert result.total_heures_month == "00:00"
        assert len(result.weekly_summaries) == 0
        assert result.all_validated is True  # Vide = tout est validé

    def test_generate_recap_multiple_weeks(self):
        """Test: récapitulatif avec plusieurs semaines."""
        # Arrange
        pointages = [
            # Semaine 1 (5-11 janvier)
            Pointage(
                id=1,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 1, 5),  # Lundi semaine 1
                heures_normales=Duree(7, 0),
                heures_supplementaires=Duree(0, 0),
                statut=StatutPointage.VALIDE,
            ),
            # Semaine 2 (12-18 janvier)
            Pointage(
                id=2,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 1, 13),  # Mardi semaine 2
                heures_normales=Duree(8, 0),
                heures_supplementaires=Duree(0, 0),
                statut=StatutPointage.VALIDE,
            ),
            # Semaine 3 (19-25 janvier)
            Pointage(
                id=3,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 1, 20),  # Mardi semaine 3
                heures_normales=Duree(7, 30),
                heures_supplementaires=Duree(1, 30),
                statut=StatutPointage.VALIDE,
            ),
        ]

        self.pointage_repo.search.return_value = (pointages, 3)
        self.variable_paie_repo.find_by_pointage.return_value = []

        dto = GenerateMonthlyRecapDTO(utilisateur_id=7, year=2026, month=1)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert len(result.weekly_summaries) == 3
        assert result.weekly_summaries[0].numero_semaine == 2
        assert result.weekly_summaries[1].numero_semaine == 3
        assert result.weekly_summaries[2].numero_semaine == 4
        assert result.heures_normales_total == "22:30"
        assert result.heures_supplementaires_total == "01:30"
        assert result.total_heures_month == "24:00"

    def test_generate_recap_mixed_statuses(self):
        """Test: statut de semaine avec pointages de statuts différents."""
        # Arrange
        pointages = [
            Pointage(
                id=1,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 1, 5),
                heures_normales=Duree(7, 0),
                heures_supplementaires=Duree(0, 0),
                statut=StatutPointage.BROUILLON,
            ),
            Pointage(
                id=2,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 1, 6),
                heures_normales=Duree(8, 0),
                heures_supplementaires=Duree(0, 0),
                statut=StatutPointage.VALIDE,
            ),
        ]

        self.pointage_repo.search.return_value = (pointages, 2)
        self.variable_paie_repo.find_by_pointage.return_value = []

        dto = GenerateMonthlyRecapDTO(utilisateur_id=7, year=2026, month=1)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.all_validated is False
        # Statut de la semaine = brouillon (car has_brouillon)
        assert result.weekly_summaries[0].statut == "brouillon"

    def test_generate_recap_with_rejected_pointages(self):
        """Test: statut de semaine avec pointages rejetés."""
        # Arrange
        pointages = [
            Pointage(
                id=1,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 1, 5),
                heures_normales=Duree(7, 0),
                heures_supplementaires=Duree(0, 0),
                statut=StatutPointage.REJETE,
            ),
            Pointage(
                id=2,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 1, 6),
                heures_normales=Duree(8, 0),
                heures_supplementaires=Duree(0, 0),
                statut=StatutPointage.VALIDE,
            ),
        ]

        self.pointage_repo.search.return_value = (pointages, 2)
        self.variable_paie_repo.find_by_pointage.return_value = []

        dto = GenerateMonthlyRecapDTO(utilisateur_id=7, year=2026, month=1)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        # Statut de la semaine = rejete (prioritaire)
        assert result.weekly_summaries[0].statut == "rejete"

    @patch("modules.pointages.application.use_cases.generate_monthly_recap.TypeVariablePaie")
    def test_generate_recap_with_variables_paie(self, mock_type_var_class):
        """Test: récapitulatif avec variables de paie."""
        # Mock TypeVariablePaie.from_string et la property is_amount
        mock_type_instance = Mock()
        mock_type_instance.is_amount = True
        mock_type_instance.is_absence = False
        mock_type_instance.libelle = "Panier repas"
        mock_type_var_class.from_string.return_value = mock_type_instance

        # Arrange
        pointages = [
            Pointage(
                id=1,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 1, 5),
                heures_normales=Duree(7, 0),
                heures_supplementaires=Duree(0, 0),
                statut=StatutPointage.VALIDE,
            ),
            Pointage(
                id=2,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 1, 6),
                heures_normales=Duree(8, 0),
                heures_supplementaires=Duree(0, 0),
                statut=StatutPointage.VALIDE,
            ),
        ]

        # Variables de paie
        variables = [
            VariablePaie(
                id=1,
                pointage_id=1,
                type_variable="panier_repas",
                valeur=Decimal("10.00"),
                date_application=date(2026, 1, 5),
            ),
            VariablePaie(
                id=2,
                pointage_id=2,
                type_variable="panier_repas",
                valeur=Decimal("10.00"),
                date_application=date(2026, 1, 6),
            ),
        ]

        self.pointage_repo.search.return_value = (pointages, 2)
        # find_by_pointage est appelé 4 fois : 2 pour variables_paie, 2 pour absences
        self.variable_paie_repo.find_by_pointage.side_effect = [
            [variables[0]], [variables[1]],  # Pour _build_variables_paie_summaries
            [variables[0]], [variables[1]],  # Pour _build_absences_summaries
        ]

        dto = GenerateMonthlyRecapDTO(utilisateur_id=7, year=2026, month=1)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert len(result.variables_paie) == 1
        assert result.variables_paie[0].type_variable == "panier_repas"
        assert result.variables_paie[0].nombre_occurrences == 2
        assert result.variables_paie[0].valeur_unitaire == Decimal("10.00")
        assert result.variables_paie[0].montant_total == Decimal("20.00")
        assert result.variables_paie_total == Decimal("20.00")

    @patch("modules.pointages.application.use_cases.generate_monthly_recap.TypeVariablePaie")
    def test_generate_recap_with_absences(self, mock_type_var_class):
        """Test: récapitulatif avec absences."""
        # Mock TypeVariablePaie.from_string
        mock_type_instance = Mock()
        mock_type_instance.is_amount = False
        mock_type_instance.is_absence = True
        mock_type_instance.libelle = "Congés payés"
        mock_type_var_class.from_string.return_value = mock_type_instance

        # Arrange
        pointages = [
            Pointage(
                id=1,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 1, 5),
                heures_normales=Duree(7, 0),
                heures_supplementaires=Duree(0, 0),
                statut=StatutPointage.VALIDE,
            ),
        ]

        # Variable de paie de type absence
        variables = [
            VariablePaie(
                id=1,
                pointage_id=1,
                type_variable="conges_payes",
                valeur=Decimal("7.00"),  # 7 heures d'absence
                date_application=date(2026, 1, 5),
            ),
        ]

        self.pointage_repo.search.return_value = (pointages, 1)
        self.variable_paie_repo.find_by_pointage.return_value = variables

        dto = GenerateMonthlyRecapDTO(utilisateur_id=7, year=2026, month=1)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert len(result.absences) == 1
        assert result.absences[0].type_absence == "conges_payes"
        assert result.absences[0].nombre_jours == 1
        assert result.absences[0].total_heures == "07:00"
        assert result.absences[0].total_heures_decimal == 7.0

    def test_generate_recap_export_pdf_false(self):
        """Test: export_pdf=False ne génère pas de PDF."""
        # Arrange
        self.pointage_repo.search.return_value = ([], 0)

        dto = GenerateMonthlyRecapDTO(utilisateur_id=7, year=2026, month=1, export_pdf=False)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.pdf_path is None

    def test_generate_recap_weekly_grouping_across_months(self):
        """Test: regroupement hebdomadaire correct pour semaines à cheval sur 2 mois."""
        # Arrange - Janvier se termine un vendredi (31/01/2026)
        # Semaine contenant le 31/01 commence le lundi 26/01
        pointages = [
            Pointage(
                id=1,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 1, 26),  # Lundi de la dernière semaine
                heures_normales=Duree(8, 0),
                heures_supplementaires=Duree(0, 0),
                statut=StatutPointage.VALIDE,
            ),
            Pointage(
                id=2,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 1, 30),  # Vendredi
                heures_normales=Duree(7, 0),
                heures_supplementaires=Duree(0, 0),
                statut=StatutPointage.VALIDE,
            ),
        ]

        self.pointage_repo.search.return_value = (pointages, 2)
        self.variable_paie_repo.find_by_pointage.return_value = []

        dto = GenerateMonthlyRecapDTO(utilisateur_id=7, year=2026, month=1)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        # Les deux pointages doivent être dans la même semaine
        assert len(result.weekly_summaries) == 1
        assert result.weekly_summaries[0].heures_normales == "15:00"

    def test_generate_recap_decimal_calculations(self):
        """Test: calculs décimaux corrects."""
        # Arrange
        pointages = [
            Pointage(
                id=1,
                utilisateur_id=7,
                chantier_id=1,
                date_pointage=date(2026, 1, 5),
                heures_normales=Duree(7, 30),  # 7.5h
                heures_supplementaires=Duree(1, 15),  # 1.25h
                statut=StatutPointage.VALIDE,
            ),
        ]

        self.pointage_repo.search.return_value = (pointages, 1)
        self.variable_paie_repo.find_by_pointage.return_value = []

        dto = GenerateMonthlyRecapDTO(utilisateur_id=7, year=2026, month=1)

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.heures_normales_total_decimal == 7.5
        assert result.heures_supplementaires_total_decimal == 1.25
        assert result.total_heures_month_decimal == 8.75
        assert result.weekly_summaries[0].heures_normales_decimal == 7.5
        assert result.weekly_summaries[0].heures_supplementaires_decimal == 1.25
        assert result.weekly_summaries[0].total_heures_decimal == 8.75
