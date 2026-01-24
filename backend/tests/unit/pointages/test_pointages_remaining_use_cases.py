"""Tests unitaires pour les Use Cases restants du module pointages."""

import pytest
from datetime import date
from unittest.mock import Mock

from modules.pointages.application.use_cases.create_variable_paie import (
    CreateVariablePaieUseCase,
)
from modules.pointages.application.use_cases.get_pointage import GetPointageUseCase
from modules.pointages.application.use_cases.get_vue_semaine import GetVueSemaineUseCase
from modules.pointages.application.use_cases.list_feuilles_heures import (
    ListFeuillesHeuresUseCase,
)
from modules.pointages.application.use_cases.submit_pointage import SubmitPointageUseCase
from modules.pointages.application.dtos import (
    CreateVariablePaieDTO,
    FeuilleHeuresSearchDTO,
)
from modules.pointages.domain.entities import Pointage
from modules.pointages.domain.value_objects import StatutPointage, Duree
from modules.pointages.application.ports import NullEventBus


class TestCreateVariablePaieUseCase:
    """Tests pour CreateVariablePaieUseCase (FDH-13)."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.variable_repo = Mock()
        self.pointage_repo = Mock()
        self.event_bus = NullEventBus()
        self.use_case = CreateVariablePaieUseCase(
            self.variable_repo, self.pointage_repo, self.event_bus
        )

    def test_create_variable_paie_success(self):
        """Test création réussie d'une variable de paie."""
        # Mock: pointage existe
        pointage = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
        )
        self.pointage_repo.find_by_id.return_value = pointage

        # Mock: save
        def save_variable(v):
            v.id = 1
            return v

        self.variable_repo.save.side_effect = save_variable

        dto = CreateVariablePaieDTO(
            pointage_id=1,
            type_variable="panier_repas",
            valeur=15.5,
            date_application=date(2026, 1, 20),
            commentaire="Panier repas",
        )

        result = self.use_case.execute(dto)

        assert result.id == 1
        assert result.type_variable == "panier_repas"
        assert result.valeur == "15.5"
        self.variable_repo.save.assert_called_once()

    def test_create_variable_paie_pointage_not_found(self):
        """Test création échoue si pointage non trouvé."""
        self.pointage_repo.find_by_id.return_value = None

        dto = CreateVariablePaieDTO(
            pointage_id=999,
            type_variable="panier",
            valeur=15.5,
            date_application=date(2026, 1, 20),
        )

        with pytest.raises(ValueError, match="non trouvé"):
            self.use_case.execute(dto)

    def test_create_variable_transport(self):
        """Test création variable transport."""
        pointage = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
        )
        self.pointage_repo.find_by_id.return_value = pointage

        def save_variable(v):
            v.id = 2
            return v

        self.variable_repo.save.side_effect = save_variable

        dto = CreateVariablePaieDTO(
            pointage_id=1,
            type_variable="indemnite_transport",
            valeur=25.0,
            date_application=date(2026, 1, 20),
        )

        result = self.use_case.execute(dto)

        assert result.type_variable == "indemnite_transport"


class TestGetPointageUseCase:
    """Tests pour GetPointageUseCase."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.pointage_repo = Mock()
        self.use_case = GetPointageUseCase(self.pointage_repo)

    def test_get_pointage_success(self):
        """Test récupération réussie."""
        pointage = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            heures_normales=Duree(8, 0),
        )
        self.pointage_repo.find_by_id.return_value = pointage

        result = self.use_case.execute(1)

        assert result is not None
        assert result.id == 1
        assert result.heures_normales == "08:00"

    def test_get_pointage_not_found(self):
        """Test retourne None si non trouvé."""
        self.pointage_repo.find_by_id.return_value = None

        result = self.use_case.execute(999)

        assert result is None

    def test_get_pointage_with_signature(self):
        """Test récupération avec signature."""
        pointage = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            signature_utilisateur="sig_hash_123",
        )
        self.pointage_repo.find_by_id.return_value = pointage

        result = self.use_case.execute(1)

        assert result.signature_utilisateur == "sig_hash_123"


class TestGetVueSemaineUseCase:
    """Tests pour GetVueSemaineUseCase (FDH-01)."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.pointage_repo = Mock()
        self.use_case = GetVueSemaineUseCase(self.pointage_repo)

    def test_get_vue_chantiers_success(self):
        """Test vue chantiers réussie."""
        # Mock pointages
        total_heures = Mock()
        total_heures.total_minutes = 480

        pointage = Mock()
        pointage.id = 1
        pointage.chantier_id = 10
        pointage.chantier_nom = "Chantier A"
        pointage.chantier_couleur = "#FF5733"
        pointage.utilisateur_id = 1
        pointage.utilisateur_nom = "Jean DUPONT"
        pointage.date_pointage = date(2026, 1, 20)
        pointage.heures_normales = Duree(8, 0)
        pointage.heures_supplementaires = Duree(0, 0)
        pointage.total_heures = total_heures
        pointage.statut = StatutPointage.BROUILLON

        self.pointage_repo.search.return_value = ([pointage], 1)

        result = self.use_case.get_vue_chantiers(
            semaine_debut=date(2026, 1, 19),  # Lundi
        )

        assert len(result) == 1
        assert result[0].chantier_id == 10
        assert result[0].chantier_nom == "Chantier A"

    def test_get_vue_chantiers_adjusts_to_monday(self):
        """Test que la vue ajuste au lundi."""
        self.pointage_repo.search.return_value = ([], 0)

        # Passer un jeudi
        self.use_case.get_vue_chantiers(
            semaine_debut=date(2026, 1, 22),  # Jeudi
        )

        # Vérifier que search est appelé avec le lundi
        call_kwargs = self.pointage_repo.search.call_args[1]
        assert call_kwargs["date_debut"].weekday() == 0  # Lundi

    def test_get_vue_compagnons_success(self):
        """Test vue compagnons réussie."""
        total_heures = Mock()
        total_heures.total_minutes = 480

        pointage = Mock()
        pointage.id = 1
        pointage.utilisateur_id = 1
        pointage.utilisateur_nom = "Jean DUPONT"
        pointage.chantier_id = 10
        pointage.chantier_nom = "Chantier A"
        pointage.chantier_couleur = "#FF5733"
        pointage.date_pointage = date(2026, 1, 20)
        pointage.total_heures = total_heures

        self.pointage_repo.search.return_value = ([pointage], 1)

        result = self.use_case.get_vue_compagnons(
            semaine_debut=date(2026, 1, 19),
        )

        assert len(result) == 1
        assert result[0].utilisateur_id == 1
        assert result[0].utilisateur_nom == "Jean DUPONT"

    def test_get_vue_chantiers_empty(self):
        """Test vue chantiers vide."""
        self.pointage_repo.search.return_value = ([], 0)

        result = self.use_case.get_vue_chantiers(
            semaine_debut=date(2026, 1, 19),
        )

        assert result == []

    def test_get_vue_with_filter_chantier(self):
        """Test vue avec filtre par chantier."""
        self.pointage_repo.search.return_value = ([], 0)

        result = self.use_case.get_vue_chantiers(
            semaine_debut=date(2026, 1, 19),
            chantier_ids=[10, 20],
        )

        assert result == []


class TestListFeuillesHeuresUseCase:
    """Tests pour ListFeuillesHeuresUseCase."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.feuille_repo = Mock()
        self.pointage_repo = Mock()
        self.use_case = ListFeuillesHeuresUseCase(
            self.feuille_repo, self.pointage_repo
        )

    def test_list_feuilles_success(self):
        """Test liste réussie."""
        feuille = Mock()
        feuille.id = 1
        feuille.utilisateur_id = 1
        feuille.semaine_debut = date(2026, 1, 19)
        feuille.semaine_fin = date(2026, 1, 25)
        feuille.annee = 2026
        feuille.numero_semaine = 4
        feuille.label_semaine = "Semaine 4"
        feuille.total_heures_normales = Duree.from_minutes(35 * 60)
        feuille.total_heures_supplementaires = Duree(0, 0)
        feuille.total_heures = Duree.from_minutes(35 * 60)
        feuille.total_heures_decimal = 35.0
        feuille.commentaire_global = None
        feuille.is_complete = True
        feuille.is_all_validated = False
        feuille.created_at = None
        feuille.updated_at = None
        feuille.utilisateur_nom = "Jean"
        feuille.calculer_statut_global.return_value = StatutPointage.BROUILLON

        self.feuille_repo.search.return_value = ([feuille], 1)
        self.pointage_repo.find_by_utilisateur_and_semaine.return_value = []

        dto = FeuilleHeuresSearchDTO(page=1, page_size=20)

        result = self.use_case.execute(dto)

        assert result.total == 1
        assert len(result.items) == 1
        assert result.page == 1

    def test_list_feuilles_with_filters(self):
        """Test liste avec filtres."""
        self.feuille_repo.search.return_value = ([], 0)

        dto = FeuilleHeuresSearchDTO(
            utilisateur_id=1,
            annee=2026,
            numero_semaine=4,
            page=1,
            page_size=20,
        )

        self.use_case.execute(dto)

        call_kwargs = self.feuille_repo.search.call_args[1]
        assert call_kwargs["utilisateur_id"] == 1
        assert call_kwargs["annee"] == 2026
        assert call_kwargs["numero_semaine"] == 4

    def test_list_feuilles_pagination(self):
        """Test pagination."""
        self.feuille_repo.search.return_value = ([], 100)

        dto = FeuilleHeuresSearchDTO(page=3, page_size=10)

        self.use_case.execute(dto)

        call_kwargs = self.feuille_repo.search.call_args[1]
        assert call_kwargs["skip"] == 20  # (3-1) * 10
        assert call_kwargs["limit"] == 10


class TestSubmitPointageUseCase:
    """Tests pour SubmitPointageUseCase."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.pointage_repo = Mock()
        self.event_bus = NullEventBus()
        self.use_case = SubmitPointageUseCase(self.pointage_repo, self.event_bus)

    def test_submit_success(self):
        """Test soumission réussie."""
        pointage = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            statut=StatutPointage.BROUILLON,
        )
        self.pointage_repo.find_by_id.return_value = pointage
        self.pointage_repo.save.return_value = pointage

        result = self.use_case.execute(1)

        assert result.statut == "soumis"
        self.pointage_repo.save.assert_called_once()

    def test_submit_not_found(self):
        """Test soumission pointage non trouvé."""
        self.pointage_repo.find_by_id.return_value = None

        with pytest.raises(ValueError, match="non trouvé"):
            self.use_case.execute(999)

    def test_submit_already_soumis_raises(self):
        """Test soumission d'un pointage déjà soumis."""
        pointage = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            statut=StatutPointage.SOUMIS,
        )
        self.pointage_repo.find_by_id.return_value = pointage

        with pytest.raises(ValueError):
            self.use_case.execute(1)

    def test_submit_publishes_event(self):
        """Test publication event après soumission."""
        mock_event_bus = Mock()
        use_case = SubmitPointageUseCase(self.pointage_repo, mock_event_bus)

        pointage = Pointage(
            id=1,
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            statut=StatutPointage.BROUILLON,
        )
        self.pointage_repo.find_by_id.return_value = pointage
        self.pointage_repo.save.return_value = pointage

        use_case.execute(1)

        mock_event_bus.publish.assert_called_once()
        event = mock_event_bus.publish.call_args[0][0]
        assert event.pointage_id == 1
