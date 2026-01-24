"""Tests unitaires pour GetSignalementUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.signalements.domain.entities import Signalement
from modules.signalements.domain.value_objects import Priorite, StatutSignalement
from modules.signalements.domain.repositories import SignalementRepository, ReponseRepository
from modules.signalements.application.use_cases import (
    GetSignalementUseCase,
    SignalementNotFoundError,
)


class TestGetSignalementUseCase:
    """Tests pour le use case de recuperation d'un signalement (SIG-02)."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_signalement_repo = Mock(spec=SignalementRepository)
        self.mock_reponse_repo = Mock(spec=ReponseRepository)
        self.use_case = GetSignalementUseCase(
            signalement_repository=self.mock_signalement_repo,
            reponse_repository=self.mock_reponse_repo,
        )

    def _create_signalement(self, id: int = 1) -> Signalement:
        """Cree un signalement de test."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test signalement",
            description="Description test",
            cree_par=10,
            priorite=Priorite.MOYENNE,
        )
        signalement.id = id
        signalement.created_at = datetime.now()
        signalement.updated_at = datetime.now()
        return signalement

    def test_get_signalement_success(self):
        """Test: recuperation reussie d'un signalement."""
        signalement = self._create_signalement(id=1)
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 5

        result = self.use_case.execute(signalement_id=1)

        assert result.id == 1
        assert result.titre == "Test signalement"
        assert result.nb_reponses == 5
        self.mock_signalement_repo.find_by_id.assert_called_once_with(1)
        self.mock_reponse_repo.count_by_signalement.assert_called_once_with(1)

    def test_get_signalement_not_found(self):
        """Test: erreur si signalement non trouve."""
        self.mock_signalement_repo.find_by_id.return_value = None

        with pytest.raises(SignalementNotFoundError) as exc_info:
            self.use_case.execute(signalement_id=999)

        assert "999" in str(exc_info.value)

    def test_get_signalement_with_user_name_resolver(self):
        """Test: recuperation avec resolution des noms d'utilisateurs."""
        signalement = self._create_signalement()
        signalement.assigne_a = 5
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        def get_user_name(user_id: int) -> str:
            names = {10: "Createur Test", 5: "Assigne Test"}
            return names.get(user_id, f"User #{user_id}")

        use_case = GetSignalementUseCase(
            signalement_repository=self.mock_signalement_repo,
            reponse_repository=self.mock_reponse_repo,
            get_user_name=get_user_name,
        )

        result = use_case.execute(signalement_id=1)

        assert result.cree_par_nom == "Createur Test"
        assert result.assigne_a_nom == "Assigne Test"

    def test_get_signalement_returns_all_fields(self):
        """Test: tous les champs sont retournes dans le DTO."""
        signalement = self._create_signalement()
        signalement.priorite = Priorite.CRITIQUE
        signalement.localisation = "Zone A"
        signalement.photo_url = "https://example.com/photo.jpg"
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 3

        result = self.use_case.execute(signalement_id=1)

        assert result.priorite == "critique"
        assert result.priorite_label == "Critique (4h)"
        assert result.priorite_couleur == "red"
        assert result.statut == "ouvert"
        assert result.localisation == "Zone A"
        assert result.photo_url == "https://example.com/photo.jpg"
        assert result.nb_reponses == 3

    def test_get_signalement_with_no_assignee(self):
        """Test: signalement sans assignation."""
        signalement = self._create_signalement()
        signalement.assigne_a = None
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        result = self.use_case.execute(signalement_id=1)

        assert result.assigne_a is None
        assert result.assigne_a_nom is None
