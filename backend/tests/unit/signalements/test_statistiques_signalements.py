"""Tests unitaires pour GetStatistiquesUseCase et GetSignalementsEnRetardUseCase."""

from unittest.mock import Mock
from datetime import datetime, timedelta

from modules.signalements.domain.entities import Signalement
from modules.signalements.domain.value_objects import Priorite
from modules.signalements.domain.repositories import SignalementRepository, ReponseRepository
from modules.signalements.application.use_cases import (
    GetStatistiquesUseCase,
    GetSignalementsEnRetardUseCase,
)


class TestGetStatistiquesUseCase:
    """Tests pour le use case de statistiques (SIG-18)."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=SignalementRepository)
        self.use_case = GetStatistiquesUseCase(
            signalement_repository=self.mock_repo,
        )

    def test_get_statistiques_success(self):
        """Test: recuperation des statistiques globales."""
        stats_data = {
            "total": 100,
            "par_statut": {
                "ouvert": 50,
                "traite": 30,
                "cloture": 20,
            },
            "par_priorite": {
                "critique": 10,
                "haute": 25,
                "moyenne": 45,
                "basse": 20,
            },
            "en_retard": 5,
            "traites_cette_semaine": 15,
            "temps_moyen_resolution": 48.5,
            "taux_resolution": 0.5,
        }
        self.mock_repo.get_statistiques.return_value = stats_data

        result = self.use_case.execute()

        assert result.total == 100
        assert result.par_statut["ouvert"] == 50
        assert result.par_priorite["critique"] == 10
        assert result.en_retard == 5
        assert result.traites_cette_semaine == 15
        assert result.temps_moyen_resolution == 48.5
        assert result.taux_resolution == 0.5

    def test_get_statistiques_by_chantier(self):
        """Test: statistiques pour un chantier specifique."""
        stats_data = {
            "total": 25,
            "par_statut": {"ouvert": 10, "traite": 10, "cloture": 5},
            "par_priorite": {"haute": 5, "moyenne": 15, "basse": 5},
            "en_retard": 2,
            "traites_cette_semaine": 3,
            "temps_moyen_resolution": 24.0,
            "taux_resolution": 0.6,
        }
        self.mock_repo.get_statistiques.return_value = stats_data

        result = self.use_case.execute(chantier_id=1)

        assert result.total == 25
        self.mock_repo.get_statistiques.assert_called_once_with(1, None, None)

    def test_get_statistiques_with_date_range(self):
        """Test: statistiques avec plage de dates."""
        stats_data = {
            "total": 30,
            "par_statut": {},
            "par_priorite": {},
            "en_retard": 0,
            "traites_cette_semaine": 5,
            "temps_moyen_resolution": None,
            "taux_resolution": 0.0,
        }
        self.mock_repo.get_statistiques.return_value = stats_data

        date_debut = datetime(2026, 1, 1)
        date_fin = datetime(2026, 1, 31)
        result = self.use_case.execute(date_debut=date_debut, date_fin=date_fin)

        assert result.total == 30
        self.mock_repo.get_statistiques.assert_called_once_with(None, date_debut, date_fin)

    def test_get_statistiques_empty(self):
        """Test: statistiques avec aucun signalement."""
        stats_data = {
            "total": 0,
            "par_statut": {},
            "par_priorite": {},
            "en_retard": 0,
            "traites_cette_semaine": 0,
            "temps_moyen_resolution": None,
            "taux_resolution": 0.0,
        }
        self.mock_repo.get_statistiques.return_value = stats_data

        result = self.use_case.execute()

        assert result.total == 0
        assert result.en_retard == 0
        assert result.taux_resolution == 0.0

    def test_get_statistiques_handles_missing_keys(self):
        """Test: gestion des cles manquantes dans les stats."""
        # Repository retourne des donnees partielles
        stats_data = {
            "total": 10,
        }
        self.mock_repo.get_statistiques.return_value = stats_data

        result = self.use_case.execute()

        assert result.total == 10
        assert result.par_statut == {}
        assert result.par_priorite == {}
        assert result.en_retard == 0


class TestGetSignalementsEnRetardUseCase:
    """Tests pour le use case des signalements en retard (SIG-16)."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_signalement_repo = Mock(spec=SignalementRepository)
        self.mock_reponse_repo = Mock(spec=ReponseRepository)
        self.use_case = GetSignalementsEnRetardUseCase(
            signalement_repository=self.mock_signalement_repo,
            reponse_repository=self.mock_reponse_repo,
        )

    def _create_signalement_en_retard(self, id: int, titre: str) -> Signalement:
        """Cree un signalement en retard."""
        signalement = Signalement(
            chantier_id=1,
            titre=titre,
            description="Description",
            cree_par=10,
            priorite=Priorite.CRITIQUE,
        )
        signalement.id = id
        # Cree il y a plus de 4 heures (delai critique)
        signalement.created_at = datetime.now() - timedelta(hours=5)
        signalement.updated_at = signalement.created_at
        return signalement

    def test_get_signalements_en_retard_success(self):
        """Test: recuperation des signalements en retard."""
        signalements = [
            self._create_signalement_en_retard(1, "Urgence 1"),
            self._create_signalement_en_retard(2, "Urgence 2"),
        ]
        self.mock_signalement_repo.find_en_retard.return_value = signalements
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        result = self.use_case.execute()

        assert result.total == 2
        assert len(result.signalements) == 2
        self.mock_signalement_repo.find_en_retard.assert_called_once()

    def test_get_signalements_en_retard_by_chantier(self):
        """Test: signalements en retard pour un chantier."""
        signalements = [self._create_signalement_en_retard(1, "Test")]
        self.mock_signalement_repo.find_en_retard.return_value = signalements
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        self.use_case.execute(chantier_id=5)

        self.mock_signalement_repo.find_en_retard.assert_called_once_with(5, 0, 100)

    def test_get_signalements_en_retard_with_pagination(self):
        """Test: pagination des signalements en retard."""
        signalements = [
            self._create_signalement_en_retard(i, f"Sig {i}") for i in range(5)
        ]
        self.mock_signalement_repo.find_en_retard.return_value = signalements
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        result = self.use_case.execute(skip=10, limit=5)

        assert result.skip == 10
        assert result.limit == 5
        self.mock_signalement_repo.find_en_retard.assert_called_once_with(None, 10, 5)

    def test_get_signalements_en_retard_empty(self):
        """Test: aucun signalement en retard."""
        self.mock_signalement_repo.find_en_retard.return_value = []

        result = self.use_case.execute()

        assert result.total == 0
        assert len(result.signalements) == 0

    def test_get_signalements_en_retard_includes_reponse_count(self):
        """Test: le nombre de reponses est inclus."""
        signalements = [
            self._create_signalement_en_retard(1, "Test 1"),
            self._create_signalement_en_retard(2, "Test 2"),
        ]
        self.mock_signalement_repo.find_en_retard.return_value = signalements
        # Differents nombres de reponses
        self.mock_reponse_repo.count_by_signalement.side_effect = [3, 7]

        result = self.use_case.execute()

        assert result.signalements[0].nb_reponses == 3
        assert result.signalements[1].nb_reponses == 7

    def test_get_signalements_en_retard_shows_delay_info(self):
        """Test: les informations de retard sont presentes."""
        signalement = self._create_signalement_en_retard(1, "Test")
        self.mock_signalement_repo.find_en_retard.return_value = [signalement]
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        result = self.use_case.execute()

        # Le signalement devrait indiquer qu'il est en retard
        assert result.signalements[0].est_en_retard is True
        assert result.signalements[0].pourcentage_temps > 100
