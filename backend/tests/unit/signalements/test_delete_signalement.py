"""Tests unitaires pour DeleteSignalementUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.signalements.domain.entities import Signalement
from modules.signalements.domain.value_objects import Priorite
from modules.signalements.domain.repositories import SignalementRepository, ReponseRepository
from modules.signalements.application.use_cases import (
    DeleteSignalementUseCase,
    SignalementNotFoundError,
    AccessDeniedError,
)


class TestDeleteSignalementUseCase:
    """Tests pour le use case de suppression d'un signalement (SIG-05)."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_signalement_repo = Mock(spec=SignalementRepository)
        self.mock_reponse_repo = Mock(spec=ReponseRepository)
        self.use_case = DeleteSignalementUseCase(
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

    def test_delete_signalement_success_as_admin(self):
        """Test: suppression reussie en tant qu'admin."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.delete.return_value = True

        result = self.use_case.execute(
            signalement_id=1,
            user_id=99,
            user_role="admin",
        )

        assert result is True
        self.mock_reponse_repo.delete_by_signalement.assert_called_once_with(1)
        self.mock_signalement_repo.delete.assert_called_once_with(1)

    def test_delete_signalement_success_as_conducteur(self):
        """Test: suppression reussie en tant que conducteur."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.delete.return_value = True

        result = self.use_case.execute(
            signalement_id=1,
            user_id=99,
            user_role="conducteur",
        )

        assert result is True

    def test_delete_signalement_not_found(self):
        """Test: erreur si signalement non trouve."""
        self.mock_signalement_repo.find_by_id.return_value = None

        with pytest.raises(SignalementNotFoundError):
            self.use_case.execute(
                signalement_id=999,
                user_id=1,
                user_role="admin",
            )

    def test_delete_signalement_access_denied_as_compagnon(self):
        """Test: acces refuse pour un compagnon."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement

        with pytest.raises(AccessDeniedError) as exc_info:
            self.use_case.execute(
                signalement_id=1,
                user_id=10,
                user_role="compagnon",
            )

        assert "administrateurs et conducteurs" in str(exc_info.value)

    def test_delete_signalement_access_denied_as_chef_chantier(self):
        """Test: acces refuse pour un chef de chantier."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement

        with pytest.raises(AccessDeniedError):
            self.use_case.execute(
                signalement_id=1,
                user_id=10,
                user_role="chef_chantier",
            )

    def test_delete_signalement_deletes_reponses_first(self):
        """Test: les reponses sont supprimees avant le signalement."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.delete.return_value = True

        self.use_case.execute(
            signalement_id=1,
            user_id=1,
            user_role="admin",
        )

        # Verifier l'ordre des appels
        self.mock_reponse_repo.delete_by_signalement.assert_called_once_with(1)
        self.mock_signalement_repo.delete.assert_called_once_with(1)
