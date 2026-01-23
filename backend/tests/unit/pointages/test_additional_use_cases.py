"""Tests unitaires supplémentaires pour les Use Cases du module pointages."""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, MagicMock
import io

from modules.pointages.application.use_cases.bulk_create_from_planning import (
    BulkCreateFromPlanningUseCase,
)
from modules.pointages.application.use_cases.compare_equipes import (
    CompareEquipesUseCase,
)
from modules.pointages.application.use_cases.get_jauge_avancement import (
    GetJaugeAvancementUseCase,
)
from modules.pointages.application.use_cases.list_pointages import (
    ListPointagesUseCase,
)
from modules.pointages.application.use_cases.delete_pointage import (
    DeletePointageUseCase,
)
from modules.pointages.application.use_cases.export_feuille_heures import (
    ExportFeuilleHeuresUseCase,
)
from modules.pointages.application.dtos import (
    BulkCreatePointageDTO,
    AffectationSourceDTO,
    PointageSearchDTO,
    ExportFeuilleHeuresDTO,
    FormatExport,
)
from modules.pointages.domain.entities import Pointage
from modules.pointages.domain.value_objects import StatutPointage, Duree
from modules.pointages.application.ports import NullEventBus


class TestBulkCreateFromPlanningUseCase:
    """Tests pour BulkCreateFromPlanningUseCase (FDH-10)."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.pointage_repo = Mock()
        self.feuille_repo = Mock()
        self.event_bus = NullEventBus()
        self.use_case = BulkCreateFromPlanningUseCase(
            self.pointage_repo, self.feuille_repo, self.event_bus
        )

    def test_bulk_create_success(self):
        """Test création en masse réussie."""
        semaine_debut = date(2026, 1, 19)  # Lundi

        dto = BulkCreatePointageDTO(
            utilisateur_id=1,
            semaine_debut=semaine_debut,
            affectations=[
                AffectationSourceDTO(
                    affectation_id=100,
                    chantier_id=10,
                    date_affectation=date(2026, 1, 20),
                    heures_prevues="08:00",
                ),
            ],
        )

        # Mock: pas de pointage existant
        self.pointage_repo.find_by_affectation.return_value = None
        self.pointage_repo.find_by_utilisateur_chantier_date.return_value = None

        # Mock: bulk_save
        def bulk_save(pointages):
            for i, p in enumerate(pointages):
                p.id = i + 1
            return pointages

        self.pointage_repo.bulk_save.side_effect = bulk_save
        self.feuille_repo.get_or_create.return_value = (Mock(), True)

        result = self.use_case.execute(dto, created_by=1)

        assert len(result) == 1
        assert result[0].chantier_id == 10

    def test_bulk_create_skip_existing(self):
        """Test création en masse ignore les existants."""
        semaine_debut = date(2026, 1, 19)

        dto = BulkCreatePointageDTO(
            utilisateur_id=1,
            semaine_debut=semaine_debut,
            affectations=[
                AffectationSourceDTO(
                    affectation_id=100,
                    chantier_id=10,
                    date_affectation=date(2026, 1, 20),
                    heures_prevues="08:00",
                ),
            ],
        )

        # Mock: pointage déjà existant
        existing = Mock()
        self.pointage_repo.find_by_affectation.return_value = existing

        result = self.use_case.execute(dto, created_by=1)

        assert result == []

    def test_execute_from_event_success(self):
        """Test création depuis événement."""
        self.pointage_repo.find_by_affectation.return_value = None
        self.pointage_repo.find_by_utilisateur_chantier_date.return_value = None

        def save(p):
            p.id = 1
            return p

        self.pointage_repo.save.side_effect = save
        self.feuille_repo.get_or_create.return_value = (Mock(), True)

        result = self.use_case.execute_from_event(
            utilisateur_id=1,
            chantier_id=10,
            date_affectation=date(2026, 1, 20),
            heures_prevues="08:00",
            affectation_id=100,
            created_by=1,
        )

        assert result is not None
        assert result.utilisateur_id == 1


class TestCompareEquipesUseCase:
    """Tests pour CompareEquipesUseCase (FDH-15)."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.pointage_repo = Mock()
        self.use_case = CompareEquipesUseCase(self.pointage_repo)

    def test_compare_equipes_success(self):
        """Test comparaison réussie."""
        # Mock pointages avec total_heures - utilise Mock pour total_heures
        total_heures1 = Mock()
        total_heures1.total_minutes = 480

        pointage1 = Mock()
        pointage1.chantier_id = 10
        pointage1.chantier_nom = "Chantier A"
        pointage1.utilisateur_id = 1
        pointage1.total_heures = total_heures1

        total_heures2 = Mock()
        total_heures2.total_minutes = 450

        pointage2 = Mock()
        pointage2.chantier_id = 10
        pointage2.chantier_nom = "Chantier A"
        pointage2.utilisateur_id = 2
        pointage2.total_heures = total_heures2

        self.pointage_repo.search.return_value = ([pointage1, pointage2], 2)

        result = self.use_case.execute(
            semaine_debut=date(2026, 1, 19),
        )

        assert "Semaine" in result.semaine
        assert len(result.equipes) == 1
        assert result.equipes[0].chantier_id == 10

    def test_compare_equipes_with_ecarts(self):
        """Test détection des écarts."""
        total_heures = Mock()
        total_heures.total_minutes = 600  # 10h

        pointage = Mock()
        pointage.chantier_id = 10
        pointage.chantier_nom = "Chantier A"
        pointage.utilisateur_id = 1
        pointage.total_heures = total_heures

        self.pointage_repo.search.return_value = ([pointage], 1)

        result = self.use_case.execute(
            semaine_debut=date(2026, 1, 19),
            heures_planifiees_par_chantier={10: 35.0},  # 35h planifiées
            seuil_ecart_pourcentage=10.0,
        )

        # 10h réalisées vs 35h planifiées = 28.5% completion = écart de 71.5%
        assert len(result.ecarts_detectes) == 1
        assert result.ecarts_detectes[0].type_ecart == "deficit"

    def test_compare_equipes_empty(self):
        """Test sans pointages."""
        self.pointage_repo.search.return_value = ([], 0)

        result = self.use_case.execute(semaine_debut=date(2026, 1, 19))

        assert result.equipes == []
        assert result.ecarts_detectes == []


class TestGetJaugeAvancementUseCase:
    """Tests pour GetJaugeAvancementUseCase (FDH-14)."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.pointage_repo = Mock()
        self.use_case = GetJaugeAvancementUseCase(self.pointage_repo)

    def test_jauge_normal(self):
        """Test jauge dans la normale (90-110%)."""
        total_heures = Mock()
        total_heures.total_minutes = 35 * 60  # 35h = 2100 minutes

        pointage = Mock()
        pointage.total_heures = total_heures

        self.pointage_repo.find_by_utilisateur_and_semaine.return_value = [pointage]

        result = self.use_case.execute(
            utilisateur_id=1,
            semaine_debut=date(2026, 1, 19),
            heures_planifiees=35.0,
        )

        assert result.status == "normal"
        assert result.taux_completion == 100.0

    def test_jauge_en_retard(self):
        """Test jauge en retard (<90%)."""
        total_heures = Mock()
        total_heures.total_minutes = 25 * 60  # 25h = 1500 minutes

        pointage = Mock()
        pointage.total_heures = total_heures

        self.pointage_repo.find_by_utilisateur_and_semaine.return_value = [pointage]

        result = self.use_case.execute(
            utilisateur_id=1,
            semaine_debut=date(2026, 1, 19),
            heures_planifiees=35.0,
        )

        assert result.status == "en_retard"
        assert result.taux_completion < 90

    def test_jauge_en_avance(self):
        """Test jauge en avance (>110%)."""
        total_heures = Mock()
        total_heures.total_minutes = 40 * 60  # 40h = 2400 minutes

        pointage = Mock()
        pointage.total_heures = total_heures

        self.pointage_repo.find_by_utilisateur_and_semaine.return_value = [pointage]

        result = self.use_case.execute(
            utilisateur_id=1,
            semaine_debut=date(2026, 1, 19),
            heures_planifiees=35.0,
        )

        assert result.status == "en_avance"
        assert result.taux_completion > 110

    def test_jauge_default_planifie(self):
        """Test jauge avec heures planifiées par défaut (35h)."""
        self.pointage_repo.find_by_utilisateur_and_semaine.return_value = []

        result = self.use_case.execute(
            utilisateur_id=1,
            semaine_debut=date(2026, 1, 19),
        )

        assert result.heures_planifiees == 35.0


class TestListPointagesUseCase:
    """Tests pour ListPointagesUseCase (FDH-04)."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.pointage_repo = Mock()
        self.use_case = ListPointagesUseCase(self.pointage_repo)

    def test_list_success(self):
        """Test liste réussie."""
        pointage = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            heures_normales=Duree(8, 0),
        )
        self.pointage_repo.search.return_value = ([pointage], 1)

        dto = PointageSearchDTO(page=1, page_size=20)

        result = self.use_case.execute(dto)

        assert result.total == 1
        assert len(result.items) == 1
        assert result.page == 1

    def test_list_with_filters(self):
        """Test liste avec filtres."""
        self.pointage_repo.search.return_value = ([], 0)

        dto = PointageSearchDTO(
            utilisateur_id=1,
            chantier_id=10,
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
            statut="brouillon",
            page=1,
            page_size=20,
        )

        result = self.use_case.execute(dto)

        call_kwargs = self.pointage_repo.search.call_args[1]
        assert call_kwargs["utilisateur_id"] == 1
        assert call_kwargs["chantier_id"] == 10
        assert call_kwargs["statut"] == StatutPointage.BROUILLON

    def test_list_pagination(self):
        """Test pagination."""
        self.pointage_repo.search.return_value = ([], 100)

        dto = PointageSearchDTO(page=3, page_size=10)

        result = self.use_case.execute(dto)

        call_kwargs = self.pointage_repo.search.call_args[1]
        assert call_kwargs["skip"] == 20  # (3-1) * 10
        assert call_kwargs["limit"] == 10


class TestDeletePointageUseCase:
    """Tests pour DeletePointageUseCase."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.pointage_repo = Mock()
        self.event_bus = NullEventBus()
        self.use_case = DeletePointageUseCase(self.pointage_repo, self.event_bus)

    def test_delete_success(self):
        """Test suppression réussie."""
        existing = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            statut=StatutPointage.BROUILLON,
        )
        self.pointage_repo.find_by_id.return_value = existing

        result = self.use_case.execute(pointage_id=1, deleted_by=1)

        assert result is True
        self.pointage_repo.delete.assert_called_once_with(1)

    def test_delete_not_found_raises(self):
        """Test suppression pointage inexistant."""
        self.pointage_repo.find_by_id.return_value = None

        with pytest.raises(ValueError, match="non trouvé"):
            self.use_case.execute(pointage_id=999, deleted_by=1)

    def test_delete_not_editable_raises(self):
        """Test suppression pointage non modifiable."""
        existing = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            statut=StatutPointage.VALIDE,
        )
        self.pointage_repo.find_by_id.return_value = existing

        with pytest.raises(ValueError, match="brouillon"):
            self.use_case.execute(pointage_id=1, deleted_by=1)


class TestExportFeuilleHeuresUseCase:
    """Tests pour ExportFeuilleHeuresUseCase (FDH-03, FDH-17)."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.feuille_repo = Mock()
        self.pointage_repo = Mock()
        self.event_bus = NullEventBus()
        self.use_case = ExportFeuilleHeuresUseCase(
            self.feuille_repo, self.pointage_repo, self.event_bus
        )

    def test_export_csv_success(self):
        """Test export CSV réussi."""
        pointage = Mock()
        pointage.date_pointage = date(2026, 1, 20)
        pointage.utilisateur_id = 1
        pointage.utilisateur_nom = "Jean DUPONT"
        pointage.chantier_id = 10
        pointage.chantier_nom = "Chantier A"
        pointage.heures_normales = Duree(8, 0)
        pointage.heures_supplementaires = Duree(1, 0)
        pointage.total_heures = Duree(9, 0)
        pointage.statut = StatutPointage.VALIDE
        pointage.signature_utilisateur = None
        pointage.signature_date = None

        self.pointage_repo.search.return_value = ([pointage], 1)
        self.feuille_repo.find_by_utilisateur_and_semaine.return_value = Mock(id=1)

        dto = ExportFeuilleHeuresDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 24),
            format_export=FormatExport.CSV,
        )

        result = self.use_case.execute(dto, exported_by=1)

        assert result.success is True
        assert result.format_export == "csv"
        assert result.records_count == 1
        assert result.file_content is not None

    def test_export_empty_data(self):
        """Test export sans données."""
        self.pointage_repo.search.return_value = ([], 0)

        dto = ExportFeuilleHeuresDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 24),
            format_export=FormatExport.CSV,
        )

        result = self.use_case.execute(dto, exported_by=1)

        assert result.success is False
        assert "Aucune donnée" in result.error_message

    def test_export_with_filters(self):
        """Test export avec filtres utilisateurs et chantiers."""
        pointage = Mock()
        pointage.date_pointage = date(2026, 1, 20)
        pointage.utilisateur_id = 1
        pointage.utilisateur_nom = "Jean"
        pointage.chantier_id = 10
        pointage.chantier_nom = "Chantier"
        pointage.heures_normales = Duree(8, 0)
        pointage.heures_supplementaires = Duree(0, 0)
        pointage.total_heures = Duree(8, 0)
        pointage.statut = StatutPointage.VALIDE
        pointage.signature_utilisateur = None
        pointage.signature_date = None

        self.pointage_repo.search.return_value = ([pointage], 1)
        self.feuille_repo.find_by_utilisateur_and_semaine.return_value = Mock(id=1)

        dto = ExportFeuilleHeuresDTO(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 24),
            format_export=FormatExport.CSV,
            utilisateur_ids=[1],
            chantier_ids=[10],
        )

        result = self.use_case.execute(dto, exported_by=1)

        assert result.success is True

    def test_generate_feuille_route(self):
        """Test génération feuille de route (FDH-19)."""
        total_heures = Mock()
        total_heures.total_minutes = 480

        pointage = Mock()
        pointage.date_pointage = date(2026, 1, 20)
        pointage.chantier_id = 10
        pointage.chantier_nom = "Chantier A"
        pointage.utilisateur_nom = "Jean DUPONT"
        pointage.total_heures = total_heures

        self.pointage_repo.find_by_utilisateur_and_semaine.return_value = [pointage]

        result = self.use_case.generate_feuille_route(
            utilisateur_id=1,
            semaine_debut=date(2026, 1, 19),
        )

        assert result.utilisateur_id == 1
        assert len(result.chantiers) == 1
        assert result.chantiers[0].chantier_id == 10
