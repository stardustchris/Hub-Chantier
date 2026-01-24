"""Tests unitaires pour UpdateSignalementUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from modules.signalements.domain.entities import Signalement
from modules.signalements.domain.value_objects import Priorite, StatutSignalement
from modules.signalements.domain.repositories import SignalementRepository, ReponseRepository
from modules.signalements.application.dtos import SignalementUpdateDTO
from modules.signalements.application.use_cases import (
    UpdateSignalementUseCase,
    SignalementNotFoundError,
    AccessDeniedError,
)


class TestUpdateSignalementUseCase:
    """Tests pour le use case de mise a jour d'un signalement (SIG-04)."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_signalement_repo = Mock(spec=SignalementRepository)
        self.mock_reponse_repo = Mock(spec=ReponseRepository)
        self.use_case = UpdateSignalementUseCase(
            signalement_repository=self.mock_signalement_repo,
            reponse_repository=self.mock_reponse_repo,
        )

    def _create_signalement(self, id: int = 1, cree_par: int = 10) -> Signalement:
        """Cree un signalement de test."""
        signalement = Signalement(
            chantier_id=1,
            titre="Titre original",
            description="Description originale",
            cree_par=cree_par,
            priorite=Priorite.MOYENNE,
        )
        signalement.id = id
        signalement.created_at = datetime.now()
        signalement.updated_at = datetime.now()
        return signalement

    def test_update_signalement_success(self):
        """Test: mise a jour reussie."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.save.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        dto = SignalementUpdateDTO(
            titre="Nouveau titre",
            description="Nouvelle description",
        )
        result = self.use_case.execute(
            signalement_id=1,
            dto=dto,
            user_id=10,  # Createur
            user_role="compagnon",
        )

        assert result.titre == "Nouveau titre"
        assert result.description == "Nouvelle description"
        self.mock_signalement_repo.save.assert_called_once()

    def test_update_signalement_not_found(self):
        """Test: erreur si signalement non trouve."""
        self.mock_signalement_repo.find_by_id.return_value = None

        dto = SignalementUpdateDTO(titre="Test")
        with pytest.raises(SignalementNotFoundError):
            self.use_case.execute(
                signalement_id=999,
                dto=dto,
                user_id=10,
                user_role="admin",
            )

    def test_update_signalement_access_denied(self):
        """Test: acces refuse pour un utilisateur non autorise."""
        signalement = self._create_signalement(cree_par=10)
        self.mock_signalement_repo.find_by_id.return_value = signalement

        dto = SignalementUpdateDTO(titre="Test")
        with pytest.raises(AccessDeniedError):
            self.use_case.execute(
                signalement_id=1,
                dto=dto,
                user_id=99,  # Pas le createur
                user_role="compagnon",  # Pas admin/conducteur
            )

    def test_update_signalement_as_admin(self):
        """Test: admin peut modifier n'importe quel signalement."""
        signalement = self._create_signalement(cree_par=10)
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.save.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        dto = SignalementUpdateDTO(titre="Modifie par admin")
        result = self.use_case.execute(
            signalement_id=1,
            dto=dto,
            user_id=99,  # Pas le createur
            user_role="admin",  # Mais admin
        )

        assert result.titre == "Modifie par admin"

    def test_update_signalement_priorite(self):
        """Test: mise a jour de la priorite."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.save.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        dto = SignalementUpdateDTO(priorite="critique")
        result = self.use_case.execute(
            signalement_id=1,
            dto=dto,
            user_id=10,
            user_role="compagnon",
        )

        assert result.priorite == "critique"

    def test_update_signalement_assignation(self):
        """Test: assignation a un utilisateur."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.save.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        dto = SignalementUpdateDTO(assigne_a=25)
        result = self.use_case.execute(
            signalement_id=1,
            dto=dto,
            user_id=10,
            user_role="admin",
        )

        assert result.assigne_a == 25

    def test_update_signalement_date_resolution(self):
        """Test: mise a jour de la date de resolution souhaitee."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.save.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        date_resolution = datetime.now() + timedelta(days=3)
        dto = SignalementUpdateDTO(date_resolution_souhaitee=date_resolution)
        result = self.use_case.execute(
            signalement_id=1,
            dto=dto,
            user_id=10,
            user_role="admin",
        )

        assert result.date_resolution_souhaitee == date_resolution

    def test_update_signalement_partial(self):
        """Test: mise a jour partielle (seuls les champs fournis)."""
        signalement = self._create_signalement()
        signalement.localisation = "Zone A"
        self.mock_signalement_repo.find_by_id.return_value = signalement
        self.mock_signalement_repo.save.return_value = signalement
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        # Mise a jour uniquement du titre
        dto = SignalementUpdateDTO(titre="Titre modifie")
        result = self.use_case.execute(
            signalement_id=1,
            dto=dto,
            user_id=10,
            user_role="admin",
        )

        # La localisation doit etre conservee
        assert result.titre == "Titre modifie"
        assert result.localisation == "Zone A"
