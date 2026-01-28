"""Tests unitaires pour les dependencies web partagees."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException

from shared.infrastructure.web.dependencies import (
    get_token_service,
    get_user_repository,
    get_token_from_cookie_or_header,
    get_current_user_id,
    get_current_user_role,
    get_is_moderator,
    require_admin,
    require_conducteur_or_admin,
    require_chef_or_above,
    get_current_user_chantier_ids,
    AUTH_COOKIE_NAME,
)


class TestGetTokenService:
    """Tests de get_token_service."""

    def test_returns_service(self):
        """Test que la factory retourne un service."""
        result = get_token_service()
        # Verifie que le service a la methode get_user_id
        assert hasattr(result, "get_user_id")
        assert callable(result.get_user_id)


class TestGetUserRepository:
    """Tests de get_user_repository."""

    def test_returns_repository(self):
        """Test que la factory retourne un repository."""
        from shared.infrastructure.database import SessionLocal
        db = SessionLocal()
        try:
            result = get_user_repository(db=db)
            # Verifie que le repo a la methode find_by_id
            assert hasattr(result, "find_by_id")
            assert callable(result.find_by_id)
        finally:
            db.close()


class TestGetTokenFromCookieOrHeader:
    """Tests de get_token_from_cookie_or_header."""

    def test_returns_cookie_token_if_present(self):
        """Test priorite au cookie."""
        mock_request = Mock()
        mock_request.cookies.get.return_value = "cookie_token"

        result = get_token_from_cookie_or_header(
            request=mock_request,
            authorization_token="header_token",
        )

        assert result == "cookie_token"
        mock_request.cookies.get.assert_called_once_with(AUTH_COOKIE_NAME)

    def test_returns_header_token_if_no_cookie(self):
        """Test fallback vers header."""
        mock_request = Mock()
        mock_request.cookies.get.return_value = None

        result = get_token_from_cookie_or_header(
            request=mock_request,
            authorization_token="header_token",
        )

        assert result == "header_token"

    def test_raises_401_if_no_token(self):
        """Test erreur 401 si aucun token."""
        mock_request = Mock()
        mock_request.cookies.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_token_from_cookie_or_header(
                request=mock_request,
                authorization_token=None,
            )

        assert exc_info.value.status_code == 401
        assert "Non authentifié" in exc_info.value.detail


class TestGetCurrentUserId:
    """Tests de get_current_user_id."""

    @patch("shared.infrastructure.web.dependencies.get_token_service")
    def test_returns_user_id_from_token(self, mock_get_service):
        """Test extraction user_id du token."""
        mock_service = Mock()
        mock_service.get_user_id.return_value = 42
        mock_get_service.return_value = mock_service

        result = get_current_user_id(token="valid_token")

        assert result == 42
        mock_service.get_user_id.assert_called_once_with("valid_token")

    @patch("shared.infrastructure.web.dependencies.get_token_service")
    def test_raises_401_if_invalid_token(self, mock_get_service):
        """Test erreur 401 si token invalide."""
        mock_service = Mock()
        mock_service.get_user_id.return_value = None
        mock_get_service.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            get_current_user_id(token="invalid_token")

        assert exc_info.value.status_code == 401
        assert "Token invalide" in exc_info.value.detail


class TestGetCurrentUserRole:
    """Tests de get_current_user_role."""

    @patch("shared.infrastructure.web.dependencies.get_user_repository")
    def test_returns_user_role(self, mock_get_repo):
        """Test retourne le role de l'utilisateur."""
        mock_user = Mock()
        mock_user.role.value = "admin"
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = mock_user
        mock_get_repo.return_value = mock_repo

        mock_db = Mock()
        result = get_current_user_role(current_user_id=42, db=mock_db)

        assert result == "admin"
        mock_repo.find_by_id.assert_called_once_with(42)

    @patch("shared.infrastructure.web.dependencies.get_user_repository")
    def test_raises_401_if_user_not_found(self, mock_get_repo):
        """Test erreur 401 si utilisateur non trouve."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None
        mock_get_repo.return_value = mock_repo

        with pytest.raises(HTTPException) as exc_info:
            get_current_user_role(current_user_id=999, db=Mock())

        assert exc_info.value.status_code == 401
        assert "Utilisateur non trouvé" in exc_info.value.detail


class TestGetIsModerator:
    """Tests de get_is_moderator."""

    def test_admin_is_moderator(self):
        """Test admin est moderateur."""
        assert get_is_moderator(current_user_role="admin") is True

    def test_conducteur_is_moderator(self):
        """Test conducteur est moderateur."""
        assert get_is_moderator(current_user_role="conducteur") is True

    def test_chef_chantier_is_not_moderator(self):
        """Test chef_chantier n'est pas moderateur."""
        assert get_is_moderator(current_user_role="chef_chantier") is False

    def test_compagnon_is_not_moderator(self):
        """Test compagnon n'est pas moderateur."""
        assert get_is_moderator(current_user_role="compagnon") is False


class TestRequireAdmin:
    """Tests de require_admin."""

    def test_allows_admin(self):
        """Test autorise admin."""
        result = require_admin(current_user_role="admin")
        assert result == "admin"

    def test_rejects_conducteur(self):
        """Test refuse conducteur."""
        with pytest.raises(HTTPException) as exc_info:
            require_admin(current_user_role="conducteur")

        assert exc_info.value.status_code == 403
        assert "administrateurs" in exc_info.value.detail

    def test_rejects_compagnon(self):
        """Test refuse compagnon."""
        with pytest.raises(HTTPException) as exc_info:
            require_admin(current_user_role="compagnon")

        assert exc_info.value.status_code == 403


class TestRequireConducteurOrAdmin:
    """Tests de require_conducteur_or_admin."""

    def test_allows_admin(self):
        """Test autorise admin."""
        result = require_conducteur_or_admin(current_user_role="admin")
        assert result == "admin"

    def test_allows_conducteur(self):
        """Test autorise conducteur."""
        result = require_conducteur_or_admin(current_user_role="conducteur")
        assert result == "conducteur"

    def test_rejects_chef_chantier(self):
        """Test refuse chef_chantier."""
        with pytest.raises(HTTPException) as exc_info:
            require_conducteur_or_admin(current_user_role="chef_chantier")

        assert exc_info.value.status_code == 403

    def test_rejects_compagnon(self):
        """Test refuse compagnon."""
        with pytest.raises(HTTPException) as exc_info:
            require_conducteur_or_admin(current_user_role="compagnon")

        assert exc_info.value.status_code == 403


class TestRequireChefOrAbove:
    """Tests de require_chef_or_above."""

    def test_allows_admin(self):
        """Test autorise admin."""
        result = require_chef_or_above(current_user_role="admin")
        assert result == "admin"

    def test_allows_conducteur(self):
        """Test autorise conducteur."""
        result = require_chef_or_above(current_user_role="conducteur")
        assert result == "conducteur"

    def test_allows_chef_chantier(self):
        """Test autorise chef_chantier."""
        result = require_chef_or_above(current_user_role="chef_chantier")
        assert result == "chef_chantier"

    def test_rejects_compagnon(self):
        """Test refuse compagnon."""
        with pytest.raises(HTTPException) as exc_info:
            require_chef_or_above(current_user_role="compagnon")

        assert exc_info.value.status_code == 403
        assert "chefs de chantier" in exc_info.value.detail


class TestGetCurrentUserChantierIds:
    """Tests de get_current_user_chantier_ids."""

    def test_admin_gets_none_for_all_access(self):
        """Test admin a acces a tous les chantiers (None)."""
        result = get_current_user_chantier_ids(
            current_user_id=1,
            current_user_role="admin",
            db=Mock(),
        )

        assert result is None

    def test_conducteur_gets_none_for_all_access(self):
        """Test conducteur a acces a tous les chantiers (None)."""
        result = get_current_user_chantier_ids(
            current_user_id=1,
            current_user_role="conducteur",
            db=Mock(),
        )

        assert result is None

    def test_compagnon_uses_db_query(self):
        """Test que compagnon fait une requete DB."""
        from unittest.mock import Mock, MagicMock

        # Mock de la session DB
        db = Mock()
        mock_query = MagicMock()
        mock_query.filter.return_value.filter.return_value.all.return_value = []
        db.query.return_value = mock_query

        # Le test verifie juste que ca ne plante pas et retourne une liste
        result = get_current_user_chantier_ids(
            current_user_id=99999,  # ID inexistant
            current_user_role="compagnon",
            db=db,
        )
        # Doit retourner une liste (vide pour un user inexistant)
        assert isinstance(result, list)
        assert result == []

    def test_chef_chantier_uses_db_query(self):
        """Test que chef_chantier fait une requete DB."""
        from unittest.mock import Mock, MagicMock

        # Mock de la session DB
        db = Mock()
        mock_query = MagicMock()
        mock_query.filter.return_value.filter.return_value.all.return_value = []
        db.query.return_value = mock_query

        result = get_current_user_chantier_ids(
            current_user_id=99999,
            current_user_role="chef_chantier",
            db=db,
        )
        assert isinstance(result, list)
        assert result == []
