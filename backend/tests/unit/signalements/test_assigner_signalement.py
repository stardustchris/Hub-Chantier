"""Tests unitaires pour AssignerSignalementUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.signalements.domain.entities import Signalement
from modules.signalements.domain.value_objects import Priorite
from modules.signalements.domain.repositories import SignalementRepository, ReponseRepository
from modules.signalements.application.use_cases import (
    AssignerSignalementUseCase,
    SignalementNotFoundError,
    AccessDeniedError,
)


class TestAssignerSignalementUseCase:
    """Tests pour le use case d'assignation d'un signalement."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_signalement_repo = Mock(spec=SignalementRepository)
        self.mock_reponse_repo = Mock(spec=ReponseRepository)
        self.use_case = AssignerSignalementUseCase(
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

    def test_assigner_signalement_success_as_admin(self):
        """Test: assignation reussie en tant qu'admin."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.save.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        result = self.use_case.execute(
            signalement_id=1,
            assigne_a=25,
            user_role="admin",
        )

        assert result.assigne_a == 25
        self.mock_signalement_repo.save.assert_called_once()

    def test_assigner_signalement_success_as_conducteur(self):
        """Test: assignation reussie en tant que conducteur."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.save.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        result = self.use_case.execute(
            signalement_id=1,
            assigne_a=30,
            user_role="conducteur",
        )

        assert result.assigne_a == 30

    def test_assigner_signalement_success_as_chef_chantier(self):
        """Test: assignation reussie en tant que chef de chantier."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.save.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        result = self.use_case.execute(
            signalement_id=1,
            assigne_a=35,
            user_role="chef_chantier",
        )

        assert result.assigne_a == 35

    def test_assigner_signalement_not_found(self):
        """Test: erreur si signalement non trouve."""
        self.mock_signalement_repo.find_by_id.return_value = None

        with pytest.raises(SignalementNotFoundError):
            self.use_case.execute(
                signalement_id=999,
                assigne_a=25,
                user_role="admin",
            )

    def test_assigner_signalement_access_denied_as_compagnon(self):
        """Test: acces refuse pour un compagnon."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement

        with pytest.raises(AccessDeniedError) as exc_info:
            self.use_case.execute(
                signalement_id=1,
                assigne_a=25,
                user_role="compagnon",
            )

        assert "droits pour assigner" in str(exc_info.value)

    def test_assigner_signalement_with_user_name_resolver(self):
        """Test: assignation avec resolution des noms."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.save.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        def get_user_name(user_id: int) -> str:
            names = {10: "Createur", 25: "Technicien Test"}
            return names.get(user_id, f"User #{user_id}")

        use_case = AssignerSignalementUseCase(
            signalement_repository=self.mock_signalement_repo,
            reponse_repository=self.mock_reponse_repo,
            get_user_name=get_user_name,
        )

        result = use_case.execute(
            signalement_id=1,
            assigne_a=25,
            user_role="admin",
        )

        assert result.assigne_a == 25
        assert result.assigne_a_nom == "Technicien Test"
