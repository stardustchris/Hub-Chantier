"""Tests unitaires pour les use cases de reponses aux signalements (SIG-06, SIG-07)."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.signalements.domain.entities import Signalement, Reponse
from modules.signalements.domain.value_objects import Priorite
from modules.signalements.domain.repositories import SignalementRepository, ReponseRepository
from modules.signalements.application.dtos import ReponseCreateDTO, ReponseUpdateDTO
from modules.signalements.application.use_cases.reponse_use_cases import (
    CreateReponseUseCase,
    ListReponsesUseCase,
    UpdateReponseUseCase,
    DeleteReponseUseCase,
    ReponseNotFoundError,
    SignalementNotFoundError,
    AccessDeniedError,
)


class TestCreateReponseUseCase:
    """Tests pour le use case de creation de reponse (SIG-07)."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_signalement_repo = Mock(spec=SignalementRepository)
        self.mock_reponse_repo = Mock(spec=ReponseRepository)
        self.use_case = CreateReponseUseCase(
            signalement_repository=self.mock_signalement_repo,
            reponse_repository=self.mock_reponse_repo,
        )

    def _create_signalement(self, id: int = 1) -> Signalement:
        """Cree un signalement de test."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Desc",
            cree_par=10,
            priorite=Priorite.MOYENNE,
        )
        signalement.id = id
        signalement.created_at = datetime.now()
        signalement.updated_at = datetime.now()
        return signalement

    def _create_reponse(self, id: int = 1, signalement_id: int = 1) -> Reponse:
        """Cree une reponse de test."""
        reponse = Reponse(
            signalement_id=signalement_id,
            contenu="Reponse test",
            auteur_id=20,
        )
        reponse.id = id
        reponse.created_at = datetime.now()
        reponse.updated_at = datetime.now()
        return reponse

    def test_create_reponse_success(self):
        """Test: creation reussie d'une reponse."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement

        def save_reponse(reponse: Reponse) -> Reponse:
            reponse.id = 1
            reponse.created_at = datetime.now()
            reponse.updated_at = datetime.now()
            return reponse

        self.mock_reponse_repo.save.side_effect = save_reponse

        dto = ReponseCreateDTO(
            signalement_id=1,
            contenu="Ma reponse au signalement",
            auteur_id=20,
        )
        result = self.use_case.execute(dto)

        assert result.id == 1
        assert result.contenu == "Ma reponse au signalement"
        assert result.signalement_id == 1
        assert result.auteur_id == 20

    def test_create_reponse_signalement_not_found(self):
        """Test: erreur si signalement n'existe pas."""
        self.mock_signalement_repo.find_by_id.return_value = None

        dto = ReponseCreateDTO(
            signalement_id=999,
            contenu="Test",
            auteur_id=20,
        )

        with pytest.raises(SignalementNotFoundError):
            self.use_case.execute(dto)

    def test_create_reponse_with_photo(self):
        """Test: creation avec photo."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement

        def save_reponse(reponse: Reponse) -> Reponse:
            reponse.id = 1
            reponse.created_at = datetime.now()
            reponse.updated_at = datetime.now()
            return reponse

        self.mock_reponse_repo.save.side_effect = save_reponse

        dto = ReponseCreateDTO(
            signalement_id=1,
            contenu="Voici une photo",
            auteur_id=20,
            photo_url="https://example.com/photo.jpg",
        )
        result = self.use_case.execute(dto)

        assert result.photo_url == "https://example.com/photo.jpg"

    def test_create_reponse_with_user_name_resolver(self):
        """Test: creation avec resolution des noms."""
        signalement = self._create_signalement()
        self.mock_signalement_repo.find_by_id.return_value = signalement

        def save_reponse(reponse: Reponse) -> Reponse:
            reponse.id = 1
            reponse.created_at = datetime.now()
            reponse.updated_at = datetime.now()
            return reponse

        self.mock_reponse_repo.save.side_effect = save_reponse

        def get_user_name(user_id: int) -> str:
            return "Jean Technicien"

        use_case = CreateReponseUseCase(
            signalement_repository=self.mock_signalement_repo,
            reponse_repository=self.mock_reponse_repo,
            get_user_name=get_user_name,
        )

        dto = ReponseCreateDTO(
            signalement_id=1,
            contenu="Test",
            auteur_id=20,
        )
        result = use_case.execute(dto)

        assert result.auteur_nom == "Jean Technicien"


class TestListReponsesUseCase:
    """Tests pour le use case de liste des reponses."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_reponse_repo = Mock(spec=ReponseRepository)
        self.use_case = ListReponsesUseCase(
            reponse_repository=self.mock_reponse_repo,
        )

    def _create_reponse(self, id: int, contenu: str) -> Reponse:
        """Cree une reponse de test."""
        reponse = Reponse(
            signalement_id=1,
            contenu=contenu,
            auteur_id=20,
        )
        reponse.id = id
        reponse.created_at = datetime.now()
        reponse.updated_at = datetime.now()
        return reponse

    def test_list_reponses_success(self):
        """Test: liste reussie des reponses."""
        reponses = [
            self._create_reponse(1, "Reponse 1"),
            self._create_reponse(2, "Reponse 2"),
            self._create_reponse(3, "Reponse 3"),
        ]
        self.mock_reponse_repo.find_by_signalement.return_value = reponses
        self.mock_reponse_repo.count_by_signalement.return_value = 3

        result = self.use_case.execute(signalement_id=1)

        assert result.total == 3
        assert len(result.reponses) == 3
        assert result.reponses[0].contenu == "Reponse 1"

    def test_list_reponses_with_pagination(self):
        """Test: pagination de la liste."""
        reponses = [self._create_reponse(i, f"Rep {i}") for i in range(5)]
        self.mock_reponse_repo.find_by_signalement.return_value = reponses
        self.mock_reponse_repo.count_by_signalement.return_value = 50

        result = self.use_case.execute(signalement_id=1, skip=10, limit=5)

        assert result.skip == 10
        assert result.limit == 5
        assert result.total == 50

    def test_list_reponses_empty(self):
        """Test: liste vide."""
        self.mock_reponse_repo.find_by_signalement.return_value = []
        self.mock_reponse_repo.count_by_signalement.return_value = 0

        result = self.use_case.execute(signalement_id=1)

        assert result.total == 0
        assert len(result.reponses) == 0


class TestUpdateReponseUseCase:
    """Tests pour le use case de mise a jour de reponse."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_reponse_repo = Mock(spec=ReponseRepository)
        self.use_case = UpdateReponseUseCase(
            reponse_repository=self.mock_reponse_repo,
        )

    def _create_reponse(self, id: int = 1, auteur_id: int = 20) -> Reponse:
        """Cree une reponse de test."""
        reponse = Reponse(
            signalement_id=1,
            contenu="Contenu original",
            auteur_id=auteur_id,
        )
        reponse.id = id
        reponse.created_at = datetime.now()
        reponse.updated_at = datetime.now()
        return reponse

    def test_update_reponse_success(self):
        """Test: mise a jour reussie."""
        reponse = self._create_reponse()
        self.mock_reponse_repo.find_by_id.return_value = reponse
        self.mock_reponse_repo.save.return_value = reponse

        dto = ReponseUpdateDTO(contenu="Contenu modifie")
        result = self.use_case.execute(
            reponse_id=1,
            dto=dto,
            user_id=20,  # Auteur
            user_role="compagnon",
        )

        assert result.contenu == "Contenu modifie"

    def test_update_reponse_not_found(self):
        """Test: erreur si reponse non trouvee."""
        self.mock_reponse_repo.find_by_id.return_value = None

        dto = ReponseUpdateDTO(contenu="Test")
        with pytest.raises(ReponseNotFoundError):
            self.use_case.execute(
                reponse_id=999,
                dto=dto,
                user_id=20,
                user_role="admin",
            )

    def test_update_reponse_access_denied(self):
        """Test: acces refuse."""
        reponse = self._create_reponse(auteur_id=20)
        self.mock_reponse_repo.find_by_id.return_value = reponse

        dto = ReponseUpdateDTO(contenu="Test")
        with pytest.raises(AccessDeniedError):
            self.use_case.execute(
                reponse_id=1,
                dto=dto,
                user_id=99,  # Pas l'auteur
                user_role="compagnon",  # Pas admin
            )


class TestDeleteReponseUseCase:
    """Tests pour le use case de suppression de reponse."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_reponse_repo = Mock(spec=ReponseRepository)
        self.use_case = DeleteReponseUseCase(
            reponse_repository=self.mock_reponse_repo,
        )

    def _create_reponse(self, id: int = 1, auteur_id: int = 20) -> Reponse:
        """Cree une reponse de test."""
        reponse = Reponse(
            signalement_id=1,
            contenu="Test",
            auteur_id=auteur_id,
        )
        reponse.id = id
        reponse.created_at = datetime.now()
        reponse.updated_at = datetime.now()
        return reponse

    def test_delete_reponse_success_as_author(self):
        """Test: suppression reussie par l'auteur."""
        reponse = self._create_reponse()
        self.mock_reponse_repo.find_by_id.return_value = reponse
        self.mock_reponse_repo.delete.return_value = True

        result = self.use_case.execute(
            reponse_id=1,
            user_id=20,  # Auteur
            user_role="compagnon",
        )

        assert result is True
        self.mock_reponse_repo.delete.assert_called_once_with(1)

    def test_delete_reponse_success_as_admin(self):
        """Test: suppression reussie par admin."""
        reponse = self._create_reponse(auteur_id=20)
        self.mock_reponse_repo.find_by_id.return_value = reponse
        self.mock_reponse_repo.delete.return_value = True

        result = self.use_case.execute(
            reponse_id=1,
            user_id=99,  # Pas l'auteur
            user_role="admin",
        )

        assert result is True

    def test_delete_reponse_not_found(self):
        """Test: erreur si reponse non trouvee."""
        self.mock_reponse_repo.find_by_id.return_value = None

        with pytest.raises(ReponseNotFoundError):
            self.use_case.execute(
                reponse_id=999,
                user_id=20,
                user_role="admin",
            )

    def test_delete_reponse_access_denied(self):
        """Test: acces refuse."""
        reponse = self._create_reponse(auteur_id=20)
        self.mock_reponse_repo.find_by_id.return_value = reponse

        with pytest.raises(AccessDeniedError):
            self.use_case.execute(
                reponse_id=1,
                user_id=99,  # Pas l'auteur
                user_role="compagnon",  # Pas admin/conducteur
            )
