"""Tests unitaires pour ListSignalementsUseCase."""

from unittest.mock import Mock
from datetime import datetime

from modules.signalements.domain.entities import Signalement
from modules.signalements.domain.value_objects import Priorite, StatutSignalement
from modules.signalements.domain.repositories import SignalementRepository, ReponseRepository
from modules.signalements.application.use_cases import ListSignalementsUseCase


class TestListSignalementsUseCase:
    """Tests pour le use case de liste des signalements (SIG-03)."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_signalement_repo = Mock(spec=SignalementRepository)
        self.mock_reponse_repo = Mock(spec=ReponseRepository)
        self.use_case = ListSignalementsUseCase(
            signalement_repository=self.mock_signalement_repo,
            reponse_repository=self.mock_reponse_repo,
        )

    def _create_signalement(self, id: int, titre: str, priorite: Priorite = Priorite.MOYENNE) -> Signalement:
        """Cree un signalement de test."""
        signalement = Signalement(
            chantier_id=1,
            titre=titre,
            description=f"Description {titre}",
            cree_par=10,
            priorite=priorite,
        )
        signalement.id = id
        signalement.created_at = datetime.now()
        signalement.updated_at = datetime.now()
        return signalement

    def test_list_signalements_success(self):
        """Test: liste reussie des signalements d'un chantier."""
        signalements = [
            self._create_signalement(1, "Signalement 1"),
            self._create_signalement(2, "Signalement 2"),
            self._create_signalement(3, "Signalement 3"),
        ]
        self.mock_signalement_repo.find_by_chantier.return_value = signalements
        self.mock_signalement_repo.count_by_chantier.return_value = 3
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        result = self.use_case.execute(chantier_id=1)

        assert result.total == 3
        assert len(result.signalements) == 3
        assert result.skip == 0
        assert result.limit == 100
        self.mock_signalement_repo.find_by_chantier.assert_called_once()

    def test_list_signalements_with_pagination(self):
        """Test: pagination de la liste."""
        signalements = [self._create_signalement(i, f"Sig {i}") for i in range(5)]
        self.mock_signalement_repo.find_by_chantier.return_value = signalements
        self.mock_signalement_repo.count_by_chantier.return_value = 100
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        result = self.use_case.execute(chantier_id=1, skip=10, limit=5)

        assert result.skip == 10
        assert result.limit == 5
        assert result.total == 100

    def test_list_signalements_filter_by_statut(self):
        """Test: filtre par statut."""
        signalement = self._create_signalement(1, "Test")
        self.mock_signalement_repo.find_by_chantier.return_value = [signalement]
        self.mock_signalement_repo.count_by_chantier.return_value = 1
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        self.use_case.execute(chantier_id=1, statut="ouvert")

        # Verifier que le repository est appele avec le bon statut
        call_args = self.mock_signalement_repo.find_by_chantier.call_args
        assert call_args[0][3] == StatutSignalement.OUVERT  # 4eme argument = statut

    def test_list_signalements_filter_by_priorite(self):
        """Test: filtre par priorite."""
        signalement = self._create_signalement(1, "Test", Priorite.HAUTE)
        self.mock_signalement_repo.find_by_chantier.return_value = [signalement]
        self.mock_signalement_repo.count_by_chantier.return_value = 1
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        self.use_case.execute(chantier_id=1, priorite="haute")

        # Verifier que le repository est appele avec la bonne priorite
        call_args = self.mock_signalement_repo.find_by_chantier.call_args
        assert call_args[0][4] == Priorite.HAUTE  # 5eme argument = priorite

    def test_list_signalements_empty(self):
        """Test: liste vide."""
        self.mock_signalement_repo.find_by_chantier.return_value = []
        self.mock_signalement_repo.count_by_chantier.return_value = 0

        result = self.use_case.execute(chantier_id=1)

        assert result.total == 0
        assert len(result.signalements) == 0

    def test_list_signalements_includes_reponse_count(self):
        """Test: chaque signalement inclut le nombre de reponses."""
        signalements = [
            self._create_signalement(1, "Sig 1"),
            self._create_signalement(2, "Sig 2"),
        ]
        self.mock_signalement_repo.find_by_chantier.return_value = signalements
        self.mock_signalement_repo.count_by_chantier.return_value = 2
        # Retourner des counts differents pour chaque signalement
        self.mock_reponse_repo.count_by_signalement.side_effect = [3, 7]

        result = self.use_case.execute(chantier_id=1)

        assert result.signalements[0].nb_reponses == 3
        assert result.signalements[1].nb_reponses == 7
