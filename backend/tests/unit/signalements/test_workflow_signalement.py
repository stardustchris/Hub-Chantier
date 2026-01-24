"""Tests unitaires pour les use cases de workflow signalement."""

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
    AssignerSignalementUseCase,
    DeleteSignalementUseCase,
    SignalementNotFoundError,
    InvalidStatusTransitionError,
    AccessDeniedError,
)


class TestMarquerTraiteUseCase:
    """Tests pour le use case MarquerTraite (SIG-08)."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_sig_repo = Mock(spec=SignalementRepository)
        self.mock_rep_repo = Mock(spec=ReponseRepository)
        self.mock_rep_repo.count_by_signalement.return_value = 0
        self.use_case = MarquerTraiteUseCase(
            signalement_repository=self.mock_sig_repo,
            reponse_repository=self.mock_rep_repo,
        )

    def _create_signalement(self, **kwargs) -> Signalement:
        """Crée un signalement de test."""
        defaults = {
            "id": 1,
            "chantier_id": 1,
            "titre": "Test",
            "description": "Description test",
            "cree_par": 10,
            "priorite": Priorite.MOYENNE,
            "statut": StatutSignalement.OUVERT,
        }
        defaults.update(kwargs)
        sig = Signalement(**{k: v for k, v in defaults.items() if k != "id"})
        sig.id = defaults["id"]
        return sig

    def test_marquer_traite_success(self):
        """Test: marquer traité avec succès."""
        signalement = self._create_signalement()
        self.mock_sig_repo.find_by_id.return_value = signalement
        self.mock_sig_repo.save.return_value = signalement

        result = self.use_case.execute(
            signalement_id=1,
            commentaire="Problème résolu par remplacement de la pièce",
            user_role="chef_chantier",
        )

        assert result.statut == "traite"
        assert result.commentaire_traitement == "Problème résolu par remplacement de la pièce"
        self.mock_sig_repo.save.assert_called_once()

    def test_marquer_traite_from_en_cours(self):
        """Test: marquer traité depuis EN_COURS."""
        signalement = self._create_signalement(statut=StatutSignalement.EN_COURS)
        self.mock_sig_repo.find_by_id.return_value = signalement
        self.mock_sig_repo.save.return_value = signalement

        result = self.use_case.execute(
            signalement_id=1,
            commentaire="Résolu",
            user_role="chef_chantier",
        )

        assert result.statut == "traite"

    def test_marquer_traite_not_found(self):
        """Test: erreur si signalement non trouvé."""
        self.mock_sig_repo.find_by_id.return_value = None

        with pytest.raises(SignalementNotFoundError):
            self.use_case.execute(
                signalement_id=999,
                commentaire="Commentaire",
                user_role="chef_chantier",
            )

    def test_marquer_traite_from_cloture_error(self):
        """Test: erreur si signalement déjà clôturé."""
        signalement = self._create_signalement(statut=StatutSignalement.CLOTURE)
        self.mock_sig_repo.find_by_id.return_value = signalement

        with pytest.raises(InvalidStatusTransitionError):
            self.use_case.execute(
                signalement_id=1,
                commentaire="Commentaire",
                user_role="chef_chantier",
            )


class TestCloturerSignalementUseCase:
    """Tests pour le use case CloturerSignalement (SIG-09)."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_sig_repo = Mock(spec=SignalementRepository)
        self.mock_rep_repo = Mock(spec=ReponseRepository)
        self.mock_rep_repo.count_by_signalement.return_value = 0
        self.use_case = CloturerSignalementUseCase(
            signalement_repository=self.mock_sig_repo,
            reponse_repository=self.mock_rep_repo,
        )

    def _create_signalement(self, **kwargs) -> Signalement:
        """Crée un signalement de test."""
        defaults = {
            "id": 1,
            "chantier_id": 1,
            "titre": "Test",
            "description": "Description test",
            "cree_par": 10,
            "priorite": Priorite.MOYENNE,
            "statut": StatutSignalement.TRAITE,
        }
        defaults.update(kwargs)
        sig = Signalement(**{k: v for k, v in defaults.items() if k != "id"})
        sig.id = defaults["id"]
        return sig

    def test_cloturer_success_from_traite(self):
        """Test: clôturer avec succès depuis TRAITE."""
        signalement = self._create_signalement(statut=StatutSignalement.TRAITE)
        self.mock_sig_repo.find_by_id.return_value = signalement
        self.mock_sig_repo.save.return_value = signalement

        result = self.use_case.execute(
            signalement_id=1,
            user_role="chef_chantier",
        )

        assert result.statut == "cloture"
        self.mock_sig_repo.save.assert_called_once()

    def test_cloturer_from_ouvert_raises_error(self):
        """Test: NE peut PAS clôturer directement depuis OUVERT (doit passer par TRAITE)."""
        signalement = self._create_signalement(statut=StatutSignalement.OUVERT)
        self.mock_sig_repo.find_by_id.return_value = signalement

        with pytest.raises(InvalidStatusTransitionError):
            self.use_case.execute(
                signalement_id=1,
                user_role="admin",
            )

    def test_cloturer_not_found(self):
        """Test: erreur si signalement non trouvé."""
        self.mock_sig_repo.find_by_id.return_value = None

        with pytest.raises(SignalementNotFoundError):
            self.use_case.execute(
                signalement_id=999,
                user_role="admin",
            )

    def test_cloturer_access_denied_compagnon(self):
        """Test: compagnon ne peut pas clôturer."""
        signalement = self._create_signalement(statut=StatutSignalement.TRAITE)
        self.mock_sig_repo.find_by_id.return_value = signalement

        with pytest.raises(AccessDeniedError):
            self.use_case.execute(
                signalement_id=1,
                user_role="compagnon",
            )

    def test_cloturer_admin_allowed(self):
        """Test: admin peut clôturer."""
        signalement = self._create_signalement(statut=StatutSignalement.TRAITE)
        self.mock_sig_repo.find_by_id.return_value = signalement
        self.mock_sig_repo.save.return_value = signalement

        result = self.use_case.execute(
            signalement_id=1,
            user_role="admin",
        )

        assert result.statut == "cloture"

    def test_cloturer_conducteur_allowed(self):
        """Test: conducteur peut clôturer."""
        signalement = self._create_signalement(statut=StatutSignalement.TRAITE)
        self.mock_sig_repo.find_by_id.return_value = signalement
        self.mock_sig_repo.save.return_value = signalement

        result = self.use_case.execute(
            signalement_id=1,
            user_role="conducteur",
        )

        assert result.statut == "cloture"


class TestReouvrirsignalementUseCase:
    """Tests pour le use case ReouvrirsignalementUseCase."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_sig_repo = Mock(spec=SignalementRepository)
        self.mock_rep_repo = Mock(spec=ReponseRepository)
        self.mock_rep_repo.count_by_signalement.return_value = 0
        self.use_case = ReouvrirsignalementUseCase(
            signalement_repository=self.mock_sig_repo,
            reponse_repository=self.mock_rep_repo,
        )

    def _create_signalement(self, **kwargs) -> Signalement:
        """Crée un signalement de test."""
        defaults = {
            "id": 1,
            "chantier_id": 1,
            "titre": "Test",
            "description": "Description test",
            "cree_par": 10,
            "priorite": Priorite.MOYENNE,
            "statut": StatutSignalement.CLOTURE,
        }
        defaults.update(kwargs)
        sig = Signalement(**{k: v for k, v in defaults.items() if k != "id"})
        sig.id = defaults["id"]
        return sig

    def test_reouvrir_success(self):
        """Test: réouvrir avec succès."""
        signalement = self._create_signalement(statut=StatutSignalement.CLOTURE)
        self.mock_sig_repo.find_by_id.return_value = signalement
        self.mock_sig_repo.save.return_value = signalement

        result = self.use_case.execute(
            signalement_id=1,
            user_role="admin",
        )

        assert result.statut == "ouvert"
        self.mock_sig_repo.save.assert_called_once()

    def test_reouvrir_not_found(self):
        """Test: erreur si signalement non trouvé."""
        self.mock_sig_repo.find_by_id.return_value = None

        with pytest.raises(SignalementNotFoundError):
            self.use_case.execute(
                signalement_id=999,
                user_role="admin",
            )

    def test_reouvrir_access_denied_compagnon(self):
        """Test: compagnon ne peut pas réouvrir."""
        signalement = self._create_signalement(statut=StatutSignalement.CLOTURE)
        self.mock_sig_repo.find_by_id.return_value = signalement

        with pytest.raises(AccessDeniedError):
            self.use_case.execute(
                signalement_id=1,
                user_role="compagnon",
            )

    def test_reouvrir_access_denied_chef_chantier(self):
        """Test: chef de chantier ne peut pas réouvrir."""
        signalement = self._create_signalement(statut=StatutSignalement.CLOTURE)
        self.mock_sig_repo.find_by_id.return_value = signalement

        with pytest.raises(AccessDeniedError):
            self.use_case.execute(
                signalement_id=1,
                user_role="chef_chantier",
            )

    def test_reouvrir_admin_allowed(self):
        """Test: admin peut réouvrir."""
        signalement = self._create_signalement(statut=StatutSignalement.CLOTURE)
        self.mock_sig_repo.find_by_id.return_value = signalement
        self.mock_sig_repo.save.return_value = signalement

        result = self.use_case.execute(
            signalement_id=1,
            user_role="admin",
        )

        assert result.statut == "ouvert"

    def test_reouvrir_conducteur_allowed(self):
        """Test: conducteur peut réouvrir."""
        signalement = self._create_signalement(statut=StatutSignalement.CLOTURE)
        self.mock_sig_repo.find_by_id.return_value = signalement
        self.mock_sig_repo.save.return_value = signalement

        result = self.use_case.execute(
            signalement_id=1,
            user_role="conducteur",
        )

        assert result.statut == "ouvert"


class TestAssignerSignalementUseCase:
    """Tests pour le use case AssignerSignalement."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_sig_repo = Mock(spec=SignalementRepository)
        self.mock_rep_repo = Mock(spec=ReponseRepository)
        self.mock_rep_repo.count_by_signalement.return_value = 0
        self.use_case = AssignerSignalementUseCase(
            signalement_repository=self.mock_sig_repo,
            reponse_repository=self.mock_rep_repo,
        )

    def _create_signalement(self, **kwargs) -> Signalement:
        """Crée un signalement de test."""
        defaults = {
            "id": 1,
            "chantier_id": 1,
            "titre": "Test",
            "description": "Description test",
            "cree_par": 10,
            "priorite": Priorite.MOYENNE,
            "statut": StatutSignalement.OUVERT,
        }
        defaults.update(kwargs)
        sig = Signalement(**{k: v for k, v in defaults.items() if k != "id"})
        sig.id = defaults["id"]
        return sig

    def test_assigner_success(self):
        """Test: assignation réussie."""
        signalement = self._create_signalement()
        self.mock_sig_repo.find_by_id.return_value = signalement
        self.mock_sig_repo.save.return_value = signalement

        result = self.use_case.execute(
            signalement_id=1,
            assigne_a=5,
            user_role="chef_chantier",
        )

        assert result.assigne_a == 5
        assert result.statut == "en_cours"  # Passe automatiquement en cours

    def test_assigner_not_found(self):
        """Test: erreur si signalement non trouvé."""
        self.mock_sig_repo.find_by_id.return_value = None

        with pytest.raises(SignalementNotFoundError):
            self.use_case.execute(
                signalement_id=999,
                assigne_a=5,
                user_role="admin",
            )

    def test_assigner_access_denied_compagnon(self):
        """Test: compagnon ne peut pas assigner."""
        signalement = self._create_signalement()
        self.mock_sig_repo.find_by_id.return_value = signalement

        with pytest.raises(AccessDeniedError):
            self.use_case.execute(
                signalement_id=1,
                assigne_a=5,
                user_role="compagnon",
            )


class TestDeleteSignalementUseCase:
    """Tests pour le use case DeleteSignalement (SIG-05)."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_sig_repo = Mock(spec=SignalementRepository)
        self.mock_rep_repo = Mock(spec=ReponseRepository)
        self.use_case = DeleteSignalementUseCase(
            signalement_repository=self.mock_sig_repo,
            reponse_repository=self.mock_rep_repo,
        )

    def _create_signalement(self, **kwargs) -> Signalement:
        """Crée un signalement de test."""
        defaults = {
            "id": 1,
            "chantier_id": 1,
            "titre": "Test",
            "description": "Description test",
            "cree_par": 10,
        }
        defaults.update(kwargs)
        sig = Signalement(**{k: v for k, v in defaults.items() if k != "id"})
        sig.id = defaults["id"]
        return sig

    def test_delete_success_admin(self):
        """Test: suppression réussie par admin."""
        signalement = self._create_signalement()
        self.mock_sig_repo.find_by_id.return_value = signalement
        self.mock_sig_repo.delete.return_value = True

        result = self.use_case.execute(
            signalement_id=1,
            user_id=1,
            user_role="admin",
        )

        assert result is True
        self.mock_rep_repo.delete_by_signalement.assert_called_once_with(1)
        self.mock_sig_repo.delete.assert_called_once_with(1)

    def test_delete_success_conducteur(self):
        """Test: suppression réussie par conducteur."""
        signalement = self._create_signalement()
        self.mock_sig_repo.find_by_id.return_value = signalement
        self.mock_sig_repo.delete.return_value = True

        result = self.use_case.execute(
            signalement_id=1,
            user_id=1,
            user_role="conducteur",
        )

        assert result is True

    def test_delete_not_found(self):
        """Test: erreur si signalement non trouvé."""
        self.mock_sig_repo.find_by_id.return_value = None

        with pytest.raises(SignalementNotFoundError):
            self.use_case.execute(
                signalement_id=999,
                user_id=1,
                user_role="admin",
            )

    def test_delete_access_denied_compagnon(self):
        """Test: compagnon ne peut pas supprimer."""
        signalement = self._create_signalement()
        self.mock_sig_repo.find_by_id.return_value = signalement

        with pytest.raises(AccessDeniedError):
            self.use_case.execute(
                signalement_id=1,
                user_id=10,
                user_role="compagnon",
            )

    def test_delete_access_denied_chef_chantier(self):
        """Test: chef de chantier ne peut pas supprimer."""
        signalement = self._create_signalement()
        self.mock_sig_repo.find_by_id.return_value = signalement

        with pytest.raises(AccessDeniedError):
            self.use_case.execute(
                signalement_id=1,
                user_id=10,
                user_role="chef_chantier",
            )
