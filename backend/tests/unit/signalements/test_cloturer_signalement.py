"""Tests unitaires pour CloturerSignalementUseCase et ReouvrirsignalementUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.signalements.domain.entities import Signalement
from modules.signalements.domain.value_objects import Priorite, StatutSignalement
from modules.signalements.domain.repositories import SignalementRepository, ReponseRepository
from modules.signalements.application.use_cases import (
    MarquerTraiteUseCase,
    CloturerSignalementUseCase,
    ReouvrirsignalementUseCase,
    SignalementNotFoundError,
    InvalidStatusTransitionError,
    AccessDeniedError,
)


class TestMarquerTraiteUseCase:
    """Tests pour le use case de marquage comme traite (SIG-08)."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_signalement_repo = Mock(spec=SignalementRepository)
        self.mock_reponse_repo = Mock(spec=ReponseRepository)
        self.use_case = MarquerTraiteUseCase(
            signalement_repository=self.mock_signalement_repo,
            reponse_repository=self.mock_reponse_repo,
        )

    def _create_signalement(self, id: int = 1, statut: StatutSignalement = StatutSignalement.OUVERT) -> Signalement:
        """Cree un signalement de test."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test signalement",
            description="Description test",
            cree_par=10,
            priorite=Priorite.MOYENNE,
        )
        signalement.id = id
        signalement.statut = statut
        signalement.created_at = datetime.now()
        signalement.updated_at = datetime.now()
        return signalement

    def test_marquer_traite_success(self):
        """Test: marquage comme traite reussi."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.save.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        result = self.use_case.execute(
            signalement_id=1,
            commentaire="Probleme resolu en remplacant le joint",
            user_role="admin",
        )

        assert result.statut == "traite"
        assert result.commentaire_traitement is not None
        self.mock_signalement_repo.save.assert_called_once()

    def test_marquer_traite_not_found(self):
        """Test: erreur si signalement non trouve."""
        self.mock_signalement_repo.find_by_id.return_value = None

        with pytest.raises(SignalementNotFoundError):
            self.use_case.execute(
                signalement_id=999,
                commentaire="Test",
                user_role="admin",
            )

    def test_marquer_traite_already_cloture(self):
        """Test: erreur si deja cloture."""
        signalement = self._create_signalement(statut=StatutSignalement.CLOTURE)
        self.mock_signalement_repo.find_by_id.return_value = signalement

        with pytest.raises(InvalidStatusTransitionError):
            self.use_case.execute(
                signalement_id=1,
                commentaire="Test",
                user_role="admin",
            )


class TestCloturerSignalementUseCase:
    """Tests pour le use case de cloture d'un signalement (SIG-09)."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_signalement_repo = Mock(spec=SignalementRepository)
        self.mock_reponse_repo = Mock(spec=ReponseRepository)
        self.use_case = CloturerSignalementUseCase(
            signalement_repository=self.mock_signalement_repo,
            reponse_repository=self.mock_reponse_repo,
        )

    def _create_signalement_traite(self, id: int = 1) -> Signalement:
        """Cree un signalement traite."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test signalement",
            description="Description test",
            cree_par=10,
            priorite=Priorite.MOYENNE,
        )
        signalement.id = id
        signalement.statut = StatutSignalement.TRAITE
        signalement.date_traitement = datetime.now()
        signalement.commentaire_traitement = "Resolu"
        signalement.created_at = datetime.now()
        signalement.updated_at = datetime.now()
        return signalement

    def test_cloturer_success(self):
        """Test: cloture reussie."""
        signalement = self._create_signalement_traite()
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.save.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        result = self.use_case.execute(
            signalement_id=1,
            user_role="admin",
        )

        assert result.statut == "cloture"
        assert result.date_cloture is not None

    def test_cloturer_not_found(self):
        """Test: erreur si signalement non trouve."""
        self.mock_signalement_repo.find_by_id.return_value = None

        with pytest.raises(SignalementNotFoundError):
            self.use_case.execute(signalement_id=999, user_role="admin")

    def test_cloturer_access_denied_as_compagnon(self):
        """Test: acces refuse pour un compagnon."""
        signalement = self._create_signalement_traite()
        self.mock_signalement_repo.find_by_id.return_value = signalement

        with pytest.raises(AccessDeniedError):
            self.use_case.execute(
                signalement_id=1,
                user_role="compagnon",
            )

    def test_cloturer_already_cloture(self):
        """Test: erreur si deja cloture (cloture -> cloture)."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Desc",
            cree_par=10,
            priorite=Priorite.MOYENNE,
        )
        signalement.id = 1
        signalement.statut = StatutSignalement.CLOTURE
        signalement.date_cloture = datetime.now()
        signalement.created_at = datetime.now()
        signalement.updated_at = datetime.now()
        self.mock_signalement_repo.find_by_id.return_value = signalement

        with pytest.raises(InvalidStatusTransitionError):
            self.use_case.execute(signalement_id=1, user_role="admin")


class TestReouvrirsignalementUseCase:
    """Tests pour le use case de reouverture d'un signalement."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_signalement_repo = Mock(spec=SignalementRepository)
        self.mock_reponse_repo = Mock(spec=ReponseRepository)
        self.use_case = ReouvrirsignalementUseCase(
            signalement_repository=self.mock_signalement_repo,
            reponse_repository=self.mock_reponse_repo,
        )

    def _create_signalement_cloture(self, id: int = 1) -> Signalement:
        """Cree un signalement cloture."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test signalement",
            description="Description test",
            cree_par=10,
            priorite=Priorite.MOYENNE,
        )
        signalement.id = id
        signalement.statut = StatutSignalement.CLOTURE
        signalement.date_traitement = datetime.now()
        signalement.date_cloture = datetime.now()
        signalement.commentaire_traitement = "Resolu"
        signalement.created_at = datetime.now()
        signalement.updated_at = datetime.now()
        return signalement

    def test_reouvrir_success_as_admin(self):
        """Test: reouverture reussie en tant qu'admin."""
        signalement = self._create_signalement_cloture()
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.save.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        result = self.use_case.execute(
            signalement_id=1,
            user_role="admin",
        )

        assert result.statut == "ouvert"

    def test_reouvrir_success_as_conducteur(self):
        """Test: reouverture reussie en tant que conducteur."""
        signalement = self._create_signalement_cloture()
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.save.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        result = self.use_case.execute(
            signalement_id=1,
            user_role="conducteur",
        )

        assert result.statut == "ouvert"

    def test_reouvrir_access_denied_as_chef_chantier(self):
        """Test: acces refuse pour un chef de chantier."""
        signalement = self._create_signalement_cloture()
        self.mock_signalement_repo.find_by_id.return_value = signalement

        with pytest.raises(AccessDeniedError):
            self.use_case.execute(
                signalement_id=1,
                user_role="chef_chantier",
            )

    def test_reouvrir_not_found(self):
        """Test: erreur si signalement non trouve."""
        self.mock_signalement_repo.find_by_id.return_value = None

        with pytest.raises(SignalementNotFoundError):
            self.use_case.execute(signalement_id=999, user_role="admin")

    def test_reouvrir_invalid_transition_from_ouvert(self):
        """Test: erreur si deja ouvert."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Desc",
            cree_par=10,
            priorite=Priorite.MOYENNE,
        )
        signalement.id = 1
        signalement.statut = StatutSignalement.OUVERT
        signalement.created_at = datetime.now()
        signalement.updated_at = datetime.now()
        self.mock_signalement_repo.find_by_id.return_value = signalement

        with pytest.raises(InvalidStatusTransitionError):
            self.use_case.execute(signalement_id=1, user_role="admin")
