"""Tests unitaires pour SQLAlchemyEntityInfoService."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import logging

from shared.infrastructure.entity_info_impl import (
    SQLAlchemyEntityInfoService,
    get_entity_info_service,
)


class TestGetUserInfo:
    """Tests de get_user_info."""

    def test_returns_none_and_logs_warning_on_exception(self, caplog):
        """Test retourne None et log warning en cas d'erreur."""
        mock_session = Mock()
        mock_session.query.side_effect = Exception("DB error")

        service = SQLAlchemyEntityInfoService(mock_session)

        with caplog.at_level(logging.WARNING):
            result = service.get_user_info(1)

        assert result is None
        assert "Erreur recuperation user 1" in caplog.text

    def test_returns_none_for_nonexistent_user(self):
        """Test retourne None pour un utilisateur inexistant."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        service = SQLAlchemyEntityInfoService(mock_session)
        result = service.get_user_info(99999)
        assert result is None

    def test_returns_user_info_with_existing_user(self):
        """Test avec un utilisateur existant."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query

        mock_user = Mock()
        mock_user.id = 1
        mock_user.prenom = "Jean"
        mock_user.nom = "Dupont"
        mock_user.couleur = "#FF0000"
        mock_user.metier = "Macon"
        mock_user.metiers = ["Macon"]
        mock_user.role = "compagnon"
        mock_user.type_utilisateur = "salarie"
        mock_query.first.return_value = mock_user

        service = SQLAlchemyEntityInfoService(mock_session)
        result = service.get_user_info(1)

        assert result is not None
        assert result.id == 1
        assert result.nom == "Jean Dupont"
        assert result.couleur == "#FF0000"


class TestGetChantierInfo:
    """Tests de get_chantier_info."""

    def test_returns_none_and_logs_warning_on_exception(self, caplog):
        """Test retourne None et log warning en cas d'erreur."""
        mock_session = Mock()
        mock_session.query.side_effect = Exception("DB error")

        service = SQLAlchemyEntityInfoService(mock_session)

        with caplog.at_level(logging.WARNING):
            result = service.get_chantier_info(10)

        assert result is None
        assert "Erreur recuperation chantier 10" in caplog.text

    def test_returns_none_when_chantier_not_found(self):
        """Test retourne None quand chantier non trouve."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        service = SQLAlchemyEntityInfoService(mock_session)
        result = service.get_chantier_info(99999)
        assert result is None

    def test_returns_chantier_info_with_existing_chantier(self):
        """Test avec un chantier existant."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query

        mock_chantier = Mock()
        mock_chantier.id = 10
        mock_chantier.nom = "Chantier Tour Eiffel"
        mock_chantier.couleur = "#00FF00"
        mock_query.first.return_value = mock_chantier

        service = SQLAlchemyEntityInfoService(mock_session)
        result = service.get_chantier_info(10)

        assert result is not None
        assert result.id == 10
        assert result.nom == "Chantier Tour Eiffel"


class TestGetActiveUserIds:
    """Tests de get_active_user_ids."""

    def test_returns_empty_list_and_logs_warning_on_exception(self, caplog):
        """Test retourne liste vide et log warning en cas d'erreur."""
        mock_session = Mock()
        mock_session.query.side_effect = Exception("DB error")

        service = SQLAlchemyEntityInfoService(mock_session)

        with caplog.at_level(logging.WARNING):
            result = service.get_active_user_ids()

        assert result == []
        assert "Erreur recuperation users actifs" in caplog.text

    def test_returns_list_of_ids(self):
        """Test retourne une liste d'IDs."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query

        mock_row1 = Mock()
        mock_row1.id = 1
        mock_row2 = Mock()
        mock_row2.id = 2
        mock_query.all.return_value = [mock_row1, mock_row2]

        service = SQLAlchemyEntityInfoService(mock_session)
        result = service.get_active_user_ids()

        assert isinstance(result, list)
        assert result == [1, 2]


class TestGetUserChantierIds:
    """Tests de get_user_chantier_ids."""

    def test_returns_empty_list_and_logs_warning_on_exception(self, caplog):
        """Test retourne liste vide et log warning en cas d'erreur."""
        mock_session = Mock()
        mock_session.query.side_effect = Exception("DB error")

        service = SQLAlchemyEntityInfoService(mock_session)

        with caplog.at_level(logging.WARNING):
            result = service.get_user_chantier_ids(5)

        assert result == []
        assert "Erreur recuperation chantiers user 5" in caplog.text

    def test_returns_empty_list_for_nonexistent_user(self):
        """Test retourne liste vide pour utilisateur inexistant."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []

        service = SQLAlchemyEntityInfoService(mock_session)
        result = service.get_user_chantier_ids(99999)

        assert isinstance(result, list)
        assert result == []


class TestGetEntityInfoService:
    """Tests de la factory get_entity_info_service."""

    def test_returns_sqlalchemy_entity_info_service(self):
        """Test retourne une instance de SQLAlchemyEntityInfoService."""
        mock_session = Mock()

        service = get_entity_info_service(mock_session)

        assert isinstance(service, SQLAlchemyEntityInfoService)
        assert service._session == mock_session


class TestUserBasicInfoConstruction:
    """Tests de la construction de UserBasicInfo."""

    def test_handles_partial_name(self):
        """Test gere les noms partiels."""
        from shared.application.ports import UserBasicInfo

        # Test avec prenom seulement
        info = UserBasicInfo(
            id=1,
            nom="Jean",
            couleur=None,
            metier=None,
            role="compagnon",
            type_utilisateur="employe",
        )
        assert info.nom == "Jean"

    def test_handles_full_name(self):
        """Test gere les noms complets."""
        from shared.application.ports import UserBasicInfo

        info = UserBasicInfo(
            id=1,
            nom="Jean Dupont",
            couleur="#FF0000",
            metier="Macon",
            role="compagnon",
            type_utilisateur="employe",
        )
        assert info.id == 1
        assert info.nom == "Jean Dupont"
        assert info.couleur == "#FF0000"


class TestChantierBasicInfoConstruction:
    """Tests de la construction de ChantierBasicInfo."""

    def test_handles_complete_info(self):
        """Test gere les infos completes."""
        from shared.application.ports import ChantierBasicInfo

        info = ChantierBasicInfo(
            id=10,
            nom="Chantier Tour Eiffel",
            couleur="#00FF00",
        )
        assert info.id == 10
        assert info.nom == "Chantier Tour Eiffel"
        assert info.couleur == "#00FF00"

    def test_handles_minimal_info(self):
        """Test gere les infos minimales."""
        from shared.application.ports import ChantierBasicInfo

        info = ChantierBasicInfo(
            id=5,
            nom="Chantier Test",
            couleur=None,
        )
        assert info.id == 5
        assert info.couleur is None
