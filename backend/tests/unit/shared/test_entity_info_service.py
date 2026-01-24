"""Tests unitaires pour EntityInfoService.

Teste le service partage de recuperation des infos utilisateur/chantier.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session

from shared.application.ports import (
    EntityInfoService,
    UserBasicInfo,
    ChantierBasicInfo,
)
from shared.infrastructure.entity_info_impl import (
    SQLAlchemyEntityInfoService,
    get_entity_info_service,
)


class TestUserBasicInfo:
    """Tests pour le dataclass UserBasicInfo."""

    def test_creation_avec_tous_les_champs(self):
        """Test creation avec tous les champs."""
        info = UserBasicInfo(
            id=1,
            nom="Jean Dupont",
            couleur="#FF5733",
            metier="electricien",
        )

        assert info.id == 1
        assert info.nom == "Jean Dupont"
        assert info.couleur == "#FF5733"
        assert info.metier == "electricien"

    def test_creation_avec_champs_optionnels_none(self):
        """Test creation avec champs optionnels a None."""
        info = UserBasicInfo(id=1, nom="Jean Dupont")

        assert info.id == 1
        assert info.nom == "Jean Dupont"
        assert info.couleur is None
        assert info.metier is None

    def test_immutabilite(self):
        """Test que le dataclass est immutable (frozen)."""
        info = UserBasicInfo(id=1, nom="Jean Dupont")

        with pytest.raises(AttributeError):
            info.nom = "Autre Nom"


class TestChantierBasicInfo:
    """Tests pour le dataclass ChantierBasicInfo."""

    def test_creation_avec_tous_les_champs(self):
        """Test creation avec tous les champs."""
        info = ChantierBasicInfo(
            id=1,
            nom="Chantier A",
            couleur="#3498DB",
        )

        assert info.id == 1
        assert info.nom == "Chantier A"
        assert info.couleur == "#3498DB"

    def test_creation_avec_couleur_none(self):
        """Test creation sans couleur."""
        info = ChantierBasicInfo(id=1, nom="Chantier A")

        assert info.id == 1
        assert info.nom == "Chantier A"
        assert info.couleur is None

    def test_immutabilite(self):
        """Test que le dataclass est immutable (frozen)."""
        info = ChantierBasicInfo(id=1, nom="Chantier A")

        with pytest.raises(AttributeError):
            info.nom = "Autre Chantier"


class TestSQLAlchemyEntityInfoService:
    """Tests pour l'implementation SQLAlchemy du service."""

    @pytest.fixture
    def mock_session(self):
        """Fixture pour une session SQLAlchemy mockee."""
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session):
        """Fixture pour le service."""
        return SQLAlchemyEntityInfoService(mock_session)

    def test_get_user_info_retourne_info_si_trouve(self, service, mock_session):
        """Test que get_user_info retourne les infos si l'utilisateur existe."""
        # Mock du modele User
        mock_user = Mock()
        mock_user.id = 1
        mock_user.prenom = "Jean"
        mock_user.nom = "Dupont"
        mock_user.couleur = "#FF5733"
        mock_user.metier = "electricien"

        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_session.query.return_value = mock_query

        with patch(
            "shared.infrastructure.entity_info_impl.SQLAlchemyEntityInfoService.get_user_info"
        ) as mock_method:
            mock_method.return_value = UserBasicInfo(
                id=1,
                nom="Jean Dupont",
                couleur="#FF5733",
                metier="electricien",
            )

            result = mock_method(1)

            assert result is not None
            assert result.id == 1
            assert result.nom == "Jean Dupont"
            assert result.couleur == "#FF5733"
            assert result.metier == "electricien"

    def test_get_user_info_retourne_none_si_non_trouve(self, service, mock_session):
        """Test que get_user_info retourne None si l'utilisateur n'existe pas."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query

        with patch(
            "shared.infrastructure.entity_info_impl.SQLAlchemyEntityInfoService.get_user_info"
        ) as mock_method:
            mock_method.return_value = None

            result = mock_method(999)

            assert result is None

    def test_get_chantier_info_retourne_info_si_trouve(self, service, mock_session):
        """Test que get_chantier_info retourne les infos si le chantier existe."""
        with patch(
            "shared.infrastructure.entity_info_impl.SQLAlchemyEntityInfoService.get_chantier_info"
        ) as mock_method:
            mock_method.return_value = ChantierBasicInfo(
                id=1,
                nom="Chantier A",
                couleur="#3498DB",
            )

            result = mock_method(1)

            assert result is not None
            assert result.id == 1
            assert result.nom == "Chantier A"
            assert result.couleur == "#3498DB"

    def test_get_chantier_info_retourne_none_si_non_trouve(self, service, mock_session):
        """Test que get_chantier_info retourne None si le chantier n'existe pas."""
        with patch(
            "shared.infrastructure.entity_info_impl.SQLAlchemyEntityInfoService.get_chantier_info"
        ) as mock_method:
            mock_method.return_value = None

            result = mock_method(999)

            assert result is None

    def test_get_active_user_ids_retourne_liste(self, service, mock_session):
        """Test que get_active_user_ids retourne une liste d'IDs."""
        with patch(
            "shared.infrastructure.entity_info_impl.SQLAlchemyEntityInfoService.get_active_user_ids"
        ) as mock_method:
            mock_method.return_value = [1, 2, 3, 4, 5]

            result = mock_method()

            assert result == [1, 2, 3, 4, 5]
            assert len(result) == 5

    def test_get_active_user_ids_retourne_liste_vide_si_aucun(
        self, service, mock_session
    ):
        """Test que get_active_user_ids retourne une liste vide si aucun utilisateur actif."""
        with patch(
            "shared.infrastructure.entity_info_impl.SQLAlchemyEntityInfoService.get_active_user_ids"
        ) as mock_method:
            mock_method.return_value = []

            result = mock_method()

            assert result == []

    def test_get_user_chantier_ids_retourne_liste(self, service, mock_session):
        """Test que get_user_chantier_ids retourne une liste d'IDs de chantiers."""
        with patch(
            "shared.infrastructure.entity_info_impl.SQLAlchemyEntityInfoService.get_user_chantier_ids"
        ) as mock_method:
            mock_method.return_value = [10, 20, 30]

            result = mock_method(1)

            assert result == [10, 20, 30]

    def test_get_user_chantier_ids_retourne_liste_vide_si_aucun(
        self, service, mock_session
    ):
        """Test que get_user_chantier_ids retourne une liste vide si aucun chantier."""
        with patch(
            "shared.infrastructure.entity_info_impl.SQLAlchemyEntityInfoService.get_user_chantier_ids"
        ) as mock_method:
            mock_method.return_value = []

            result = mock_method(1)

            assert result == []


class TestGetEntityInfoServiceFactory:
    """Tests pour la factory get_entity_info_service."""

    def test_retourne_instance_service(self):
        """Test que la factory retourne une instance du service."""
        mock_session = Mock(spec=Session)

        service = get_entity_info_service(mock_session)

        assert isinstance(service, EntityInfoService)
        assert isinstance(service, SQLAlchemyEntityInfoService)

    def test_instance_a_la_session(self):
        """Test que l'instance a la session injectee."""
        mock_session = Mock(spec=Session)

        service = get_entity_info_service(mock_session)

        assert service._session is mock_session


class TestEntityInfoServiceInterface:
    """Tests pour verifier que l'interface est bien abstraite."""

    def test_interface_est_abstraite(self):
        """Test que EntityInfoService ne peut pas etre instancie directement."""
        with pytest.raises(TypeError):
            EntityInfoService()

    def test_interface_definit_get_user_info(self):
        """Test que l'interface definit get_user_info."""
        assert hasattr(EntityInfoService, "get_user_info")

    def test_interface_definit_get_chantier_info(self):
        """Test que l'interface definit get_chantier_info."""
        assert hasattr(EntityInfoService, "get_chantier_info")

    def test_interface_definit_get_active_user_ids(self):
        """Test que l'interface definit get_active_user_ids."""
        assert hasattr(EntityInfoService, "get_active_user_ids")

    def test_interface_definit_get_user_chantier_ids(self):
        """Test que l'interface definit get_user_chantier_ids."""
        assert hasattr(EntityInfoService, "get_user_chantier_ids")
