"""Tests unitaires pour les Use Cases restants du module taches."""

import pytest
from unittest.mock import Mock

# Imports directs pour éviter le chargement de l'infrastructure via __init__.py
from modules.taches.domain.entities.tache import Tache
from modules.taches.domain.value_objects.statut_tache import StatutTache
from modules.taches.domain.repositories.tache_repository import TacheRepository
from modules.taches.domain.repositories.template_modele_repository import TemplateModeleRepository
from modules.taches.domain.repositories.feuille_tache_repository import FeuilleTacheRepository
from modules.taches.application.use_cases.create_template import (
    CreateTemplateUseCase,
    TemplateAlreadyExistsError,
)
from modules.taches.application.use_cases.export_pdf import ExportTachesPDFUseCase
from modules.taches.application.use_cases.get_tache_stats import GetTacheStatsUseCase
from modules.taches.application.use_cases.list_feuilles_taches import (
    ListFeuillesTachesUseCase,
)
from modules.taches.application.use_cases.list_templates import ListTemplatesUseCase
from modules.taches.application.use_cases.reorder_taches import ReorderTachesUseCase
from modules.taches.application.use_cases.get_tache import TacheNotFoundError
from modules.taches.application.dtos.template_modele_dto import CreateTemplateModeleDTO, SousTacheModeleDTO


class TestCreateTemplateUseCase:
    """Tests pour CreateTemplateUseCase (TAC-04)."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.template_repo = Mock(spec=TemplateModeleRepository)
        self.use_case = CreateTemplateUseCase(template_repo=self.template_repo)

    def test_create_template_success(self):
        """Test création réussie d'un template."""
        self.template_repo.exists_by_nom.return_value = False

        def save_template(t):
            t.id = 1
            return t

        self.template_repo.save.side_effect = save_template

        dto = CreateTemplateModeleDTO(
            nom="Coffrage voiles",
            description="Template pour coffrage de voiles",
            categorie="Gros oeuvre",
            heures_estimees_defaut=16.0,
            sous_taches=[],
        )

        result = self.use_case.execute(dto)

        assert result.id == 1
        assert result.nom == "Coffrage voiles"
        self.template_repo.save.assert_called_once()

    def test_create_template_already_exists(self):
        """Test création échoue si nom existe déjà."""
        self.template_repo.exists_by_nom.return_value = True

        dto = CreateTemplateModeleDTO(
            nom="Coffrage voiles",
            description="Test",
            sous_taches=[],
        )

        with pytest.raises(TemplateAlreadyExistsError) as exc_info:
            self.use_case.execute(dto)

        assert exc_info.value.nom == "Coffrage voiles"

    def test_create_template_with_sous_taches(self):
        """Test création avec sous-tâches."""
        self.template_repo.exists_by_nom.return_value = False

        def save_template(t):
            t.id = 1
            return t

        self.template_repo.save.side_effect = save_template

        dto = CreateTemplateModeleDTO(
            nom="Coffrage complet",
            description="Template complet",
            sous_taches=[
                SousTacheModeleDTO(titre="Préparation", ordre=0),
                SousTacheModeleDTO(titre="Installation", ordre=1),
                SousTacheModeleDTO(titre="Finition", ordre=2),
            ],
        )

        self.use_case.execute(dto)

        self.template_repo.save.assert_called_once()

    def test_create_template_with_unite_mesure(self):
        """Test création avec unité de mesure."""
        self.template_repo.exists_by_nom.return_value = False

        def save_template(t):
            t.id = 1
            return t

        self.template_repo.save.side_effect = save_template

        dto = CreateTemplateModeleDTO(
            nom="Coffrage m2",
            unite_mesure="m2",
            sous_taches=[],
        )

        self.use_case.execute(dto)

        self.template_repo.save.assert_called_once()


class TestExportTachesPDFUseCase:
    """Tests pour ExportTachesPDFUseCase (TAC-16)."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.tache_repo = Mock(spec=TacheRepository)
        self.pdf_service = Mock()
        self.pdf_service.generate_taches_pdf.return_value = b"PDF content"
        self.audit_service = Mock()
        self.use_case = ExportTachesPDFUseCase(
            tache_repo=self.tache_repo,
            pdf_service=self.pdf_service,
            audit_service=self.audit_service,
        )

    def test_export_pdf_success(self):
        """Test export PDF réussi."""
        tache = Mock()
        tache.titre = "Coffrage"
        tache.est_terminee = False
        tache.heures_estimees = 16.0
        tache.heures_realisees = 8.0
        tache.quantite_estimee = None
        tache.unite_mesure = None
        tache.date_echeance = None
        tache.sous_taches = []

        self.tache_repo.find_by_chantier.return_value = [tache]
        self.tache_repo.get_stats_chantier.return_value = {
            "total": 1,
            "terminees": 0,
            "en_retard": 0,
            "heures_estimees_total": 16.0,
            "heures_realisees_total": 8.0,
        }

        result = self.use_case.execute(
            chantier_id=1,
            chantier_nom="Chantier Test",
            current_user_id=1,
        )

        assert result is not None
        assert len(result) > 0  # Retourne des bytes
        # Vérifier que l'audit trail a été créé
        self.audit_service.log_pdf_exported.assert_called_once()

    def test_export_pdf_exclude_completed(self):
        """Test export PDF sans tâches terminées."""
        tache_en_cours = Mock()
        tache_en_cours.titre = "En cours"
        tache_en_cours.est_terminee = False
        tache_en_cours.heures_estimees = 8.0
        tache_en_cours.heures_realisees = 4.0
        tache_en_cours.quantite_estimee = None
        tache_en_cours.unite_mesure = None
        tache_en_cours.date_echeance = None
        tache_en_cours.sous_taches = []

        tache_terminee = Mock()
        tache_terminee.titre = "Terminée"
        tache_terminee.est_terminee = True

        self.tache_repo.find_by_chantier.return_value = [tache_en_cours, tache_terminee]
        self.tache_repo.get_stats_chantier.return_value = {
            "total": 2,
            "terminees": 1,
            "en_retard": 0,
            "heures_estimees_total": 16.0,
            "heures_realisees_total": 12.0,
        }

        result = self.use_case.execute(
            chantier_id=1,
            chantier_nom="Test",
            current_user_id=1,
            include_completed=False,
        )

        assert result is not None

    def test_export_pdf_empty_chantier(self):
        """Test export PDF chantier vide."""
        self.tache_repo.find_by_chantier.return_value = []
        self.tache_repo.get_stats_chantier.return_value = {
            "total": 0,
            "terminees": 0,
            "en_retard": 0,
            "heures_estimees_total": 0,
            "heures_realisees_total": 0,
        }

        result = self.use_case.execute(
            chantier_id=1,
            chantier_nom="Chantier Vide",
            current_user_id=1,
        )

        assert result is not None


class TestGetTacheStatsUseCase:
    """Tests pour GetTacheStatsUseCase (TAC-20)."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.tache_repo = Mock(spec=TacheRepository)
        self.use_case = GetTacheStatsUseCase(tache_repo=self.tache_repo)

    def test_get_stats_success(self):
        """Test récupération stats réussie."""
        self.tache_repo.get_stats_chantier.return_value = {
            "total": 10,
            "terminees": 5,
            "en_cours": 3,
            "en_retard": 2,
            "heures_estimees_total": 100.0,
            "heures_realisees_total": 60.0,
        }

        result = self.use_case.execute(chantier_id=1)

        assert result.chantier_id == 1
        assert result.total_taches == 10
        assert result.taches_terminees == 5
        assert result.taches_en_cours == 3
        assert result.taches_en_retard == 2
        assert result.heures_estimees_total == 100.0
        assert result.heures_realisees_total == 60.0
        assert result.progression_globale == 60.0

    def test_get_stats_empty_chantier(self):
        """Test stats chantier vide."""
        self.tache_repo.get_stats_chantier.return_value = {
            "total": 0,
            "terminees": 0,
            "en_cours": 0,
            "en_retard": 0,
            "heures_estimees_total": 0,
            "heures_realisees_total": 0,
        }

        result = self.use_case.execute(chantier_id=1)

        assert result.total_taches == 0
        assert result.progression_globale == 0.0

    def test_get_stats_progression_capped_at_100(self):
        """Test progression plafonnée à 100%."""
        self.tache_repo.get_stats_chantier.return_value = {
            "total": 1,
            "terminees": 1,
            "en_cours": 0,
            "en_retard": 0,
            "heures_estimees_total": 10.0,
            "heures_realisees_total": 15.0,  # Dépassement
        }

        result = self.use_case.execute(chantier_id=1)

        assert result.progression_globale == 100.0


class TestListFeuillesTachesUseCase:
    """Tests pour ListFeuillesTachesUseCase."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.feuille_repo = Mock(spec=FeuilleTacheRepository)
        self.use_case = ListFeuillesTachesUseCase(feuille_repo=self.feuille_repo)

    def test_list_by_tache_success(self):
        """Test liste par tâche réussie."""
        feuille = Mock()
        feuille.id = 1
        feuille.tache_id = 10
        feuille.heures_travaillees = 8.0
        feuille.quantite_realisee = 0.0

        self.feuille_repo.find_by_tache.return_value = [feuille]
        self.feuille_repo.count_by_tache.return_value = 1
        self.feuille_repo.get_total_heures_tache.return_value = 8.0
        self.feuille_repo.get_total_quantite_tache.return_value = 0.0

        result = self.use_case.execute_by_tache(tache_id=10)

        assert result.total == 1
        assert result.total_heures == 8.0

    def test_list_by_chantier_success(self):
        """Test liste par chantier réussie."""
        feuille = Mock()
        feuille.id = 1
        feuille.heures_travaillees = 8.0
        feuille.quantite_realisee = 5.0

        self.feuille_repo.find_by_chantier.return_value = [feuille]

        result = self.use_case.execute_by_chantier(chantier_id=1)

        assert len(result.items) == 1

    def test_list_by_chantier_with_date_filter(self):
        """Test liste avec filtre de dates."""
        self.feuille_repo.find_by_chantier.return_value = []

        result = self.use_case.execute_by_chantier(
            chantier_id=1,
            date_debut="2026-01-01",
            date_fin="2026-01-31",
        )

        assert result.total == 0

    def test_list_en_attente_success(self):
        """Test liste en attente de validation."""
        feuille = Mock()
        feuille.id = 1
        feuille.heures_travaillees = 4.0
        feuille.quantite_realisee = 0.0

        self.feuille_repo.find_en_attente_validation.return_value = [feuille]

        result = self.use_case.execute_en_attente()

        assert len(result.items) == 1

    def test_list_pagination(self):
        """Test pagination."""
        self.feuille_repo.find_by_tache.return_value = []
        self.feuille_repo.count_by_tache.return_value = 100
        self.feuille_repo.get_total_heures_tache.return_value = 0.0
        self.feuille_repo.get_total_quantite_tache.return_value = 0.0

        self.use_case.execute_by_tache(
            tache_id=10,
            page=3,
            size=10,
        )

        call_kwargs = self.feuille_repo.find_by_tache.call_args[1]
        assert call_kwargs["skip"] == 20  # (3-1) * 10


class TestListTemplatesUseCase:
    """Tests pour ListTemplatesUseCase (TAC-04)."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.template_repo = Mock(spec=TemplateModeleRepository)
        self.use_case = ListTemplatesUseCase(template_repo=self.template_repo)

    def test_list_templates_success(self):
        """Test liste réussie."""
        template = Mock()
        template.id = 1
        template.nom = "Coffrage"
        template.description = "Template coffrage"
        template.categorie = "Gros oeuvre"
        template.est_actif = True
        template.sous_taches = []

        self.template_repo.search.return_value = ([template], 1)
        self.template_repo.get_categories.return_value = ["Gros oeuvre"]

        result = self.use_case.execute()

        assert result.total == 1
        assert len(result.categories) == 1

    def test_list_templates_with_query(self):
        """Test liste avec recherche."""
        self.template_repo.search.return_value = ([], 0)
        self.template_repo.get_categories.return_value = []

        self.use_case.execute(query="Coffrage")

        call_kwargs = self.template_repo.search.call_args[1]
        assert call_kwargs["query"] == "Coffrage"

    def test_list_templates_by_categorie(self):
        """Test liste par catégorie."""
        self.template_repo.search.return_value = ([], 0)
        self.template_repo.get_categories.return_value = []

        self.use_case.execute(categorie="Gros oeuvre")

        call_kwargs = self.template_repo.search.call_args[1]
        assert call_kwargs["categorie"] == "Gros oeuvre"

    def test_list_templates_pagination(self):
        """Test pagination."""
        self.template_repo.search.return_value = ([], 100)
        self.template_repo.get_categories.return_value = []

        self.use_case.execute(page=3, size=10)

        call_kwargs = self.template_repo.search.call_args[1]
        assert call_kwargs["skip"] == 20
        assert call_kwargs["limit"] == 10


class TestReorderTachesUseCase:
    """Tests pour ReorderTachesUseCase (TAC-15)."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.tache_repo = Mock(spec=TacheRepository)
        self.use_case = ReorderTachesUseCase(tache_repo=self.tache_repo)

    def test_reorder_success(self):
        """Test réorganisation réussie."""
        tache = Tache(
            id=1,
            chantier_id=10,
            titre="Tâche test",
            statut=StatutTache.A_FAIRE,
            ordre=1,
        )
        self.tache_repo.find_by_id.return_value = tache

        self.use_case.execute(tache_id=1, nouvel_ordre=5)

        self.tache_repo.reorder.assert_called_once_with(1, 5)

    def test_reorder_not_found(self):
        """Test réorganisation échoue si tâche non trouvée."""
        self.tache_repo.find_by_id.return_value = None

        with pytest.raises(TacheNotFoundError):
            self.use_case.execute(tache_id=999, nouvel_ordre=5)

    def test_reorder_batch_success(self):
        """Test réorganisation en lot."""
        tache1 = Tache(id=1, chantier_id=10, titre="T1", statut=StatutTache.A_FAIRE, ordre=1)
        tache2 = Tache(id=2, chantier_id=10, titre="T2", statut=StatutTache.A_FAIRE, ordre=2)

        self.tache_repo.find_by_id.side_effect = lambda x: tache1 if x == 1 else tache2

        ordres = [
            {"tache_id": 1, "ordre": 2},
            {"tache_id": 2, "ordre": 1},
        ]

        results = self.use_case.execute_batch(ordres)

        assert len(results) == 2
        assert self.tache_repo.reorder.call_count == 2

    def test_reorder_batch_with_invalid_entries(self):
        """Test réorganisation en lot ignore les entrées invalides."""
        tache = Tache(id=1, chantier_id=10, titre="T1", statut=StatutTache.A_FAIRE, ordre=1)
        self.tache_repo.find_by_id.return_value = tache

        ordres = [
            {"tache_id": 1, "ordre": 2},
            {"tache_id": None, "ordre": 3},  # Invalide
            {"ordre": 1},  # Manque tache_id
        ]

        results = self.use_case.execute_batch(ordres)

        assert len(results) == 1
