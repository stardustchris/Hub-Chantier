"""Tests unitaires pour les routes d'audit (sécurité RBAC)."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from modules.shared.infrastructure.web.audit_routes import router
from modules.shared.application.services.audit_service import AuditService
from modules.shared.application.dtos.audit_dtos import (
    AuditEntryDTO,
    AuditHistoryResponseDTO,
)


class TestAuditRoutesAuthentication:
    """Tests de sécurité pour les routes d'audit - Authentification."""

    @pytest.fixture
    def app(self):
        """App FastAPI de test."""
        app = FastAPI()
        app.include_router(router, prefix="/api")
        return app

    @pytest.fixture
    def client(self, app):
        """Client de test."""
        return TestClient(app)

    def test_get_history_without_authentication_returns_401(self, client):
        """Test: GET /audit/history sans authentification retourne 401."""
        # Act
        response = client.get("/api/audit/history/devis/123")

        # Assert
        assert response.status_code == 401
        assert "Non authentifié" in response.json()["detail"]

    def test_get_user_actions_without_authentication_returns_401(self, client):
        """Test: GET /audit/user sans authentification retourne 401."""
        # Act
        response = client.get("/api/audit/user/1")

        # Assert
        assert response.status_code == 401

    def test_get_recent_entries_without_authentication_returns_401(self, client):
        """Test: GET /audit/recent sans authentification retourne 401."""
        # Act
        response = client.get("/api/audit/recent")

        # Assert
        assert response.status_code == 401

    def test_search_audit_without_authentication_returns_401(self, client):
        """Test: GET /audit/search sans authentification retourne 401."""
        # Act
        response = client.get("/api/audit/search")

        # Assert
        assert response.status_code == 401


class TestAuditRoutesAuthorization:
    """Tests de sécurité pour les routes d'audit - Autorisation (RBAC)."""

    @pytest.fixture
    def mock_audit_service(self):
        """Mock du service d'audit."""
        service = Mock(spec=AuditService)
        # Mock des méthodes du service
        service.get_history.return_value = AuditHistoryResponseDTO(
            entries=[],
            total=0,
            limit=50,
            offset=0,
        )
        service.get_user_actions.return_value = []
        service.get_recent_entries.return_value = []
        service.search.return_value = AuditHistoryResponseDTO(
            entries=[],
            total=0,
            limit=100,
            offset=0,
        )
        return service

    @pytest.fixture
    def app_with_mocks(self, mock_audit_service):
        """App avec mocks des dépendances."""
        app = FastAPI()
        app.include_router(router, prefix="/api")

        # Override du service d'audit
        from modules.shared.infrastructure.web.audit_routes import get_audit_service
        app.dependency_overrides[get_audit_service] = lambda: mock_audit_service

        return app

    @pytest.fixture
    def client_with_mocks(self, app_with_mocks):
        """Client avec mocks."""
        return TestClient(app_with_mocks)

    def test_get_history_with_compagnon_role_returns_403(
        self, client_with_mocks, app_with_mocks
    ):
        """Test: GET /audit/history avec rôle compagnon retourne 403."""
        # Arrange - Mock des dépendances d'auth
        from shared.infrastructure.web.dependencies import (
            get_current_user_id,
            require_chef_or_above,
        )

        def mock_user_id():
            return 1

        def mock_role_compagnon():
            raise HTTPException(
                status_code=403,
                detail="Accès réservé aux chefs de chantier et supérieurs",
            )

        app_with_mocks.dependency_overrides[get_current_user_id] = mock_user_id
        app_with_mocks.dependency_overrides[require_chef_or_above] = mock_role_compagnon

        # Act
        response = client_with_mocks.get("/api/audit/history/devis/123")

        # Assert
        assert response.status_code == 403
        assert "chefs de chantier" in response.json()["detail"]

    def test_get_history_with_chef_chantier_role_returns_200(
        self, client_with_mocks, app_with_mocks
    ):
        """Test: GET /audit/history avec rôle chef_chantier retourne 200."""
        # Arrange - Mock des dépendances d'auth
        from shared.infrastructure.web.dependencies import (
            get_current_user_id,
            require_chef_or_above,
        )

        def mock_user_id():
            return 1

        def mock_role_chef():
            return "chef_chantier"

        app_with_mocks.dependency_overrides[get_current_user_id] = mock_user_id
        app_with_mocks.dependency_overrides[require_chef_or_above] = mock_role_chef

        # Act
        response = client_with_mocks.get("/api/audit/history/devis/123")

        # Assert
        assert response.status_code == 200
        assert "entries" in response.json()

    def test_get_history_with_conducteur_role_returns_200(
        self, client_with_mocks, app_with_mocks
    ):
        """Test: GET /audit/history avec rôle conducteur retourne 200."""
        # Arrange
        from shared.infrastructure.web.dependencies import (
            get_current_user_id,
            require_chef_or_above,
        )

        def mock_user_id():
            return 2

        def mock_role_conducteur():
            return "conducteur"

        app_with_mocks.dependency_overrides[get_current_user_id] = mock_user_id
        app_with_mocks.dependency_overrides[require_chef_or_above] = mock_role_conducteur

        # Act
        response = client_with_mocks.get("/api/audit/history/devis/123")

        # Assert
        assert response.status_code == 200

    def test_get_history_with_admin_role_returns_200(
        self, client_with_mocks, app_with_mocks
    ):
        """Test: GET /audit/history avec rôle admin retourne 200."""
        # Arrange
        from shared.infrastructure.web.dependencies import (
            get_current_user_id,
            require_chef_or_above,
        )

        def mock_user_id():
            return 3

        def mock_role_admin():
            return "admin"

        app_with_mocks.dependency_overrides[get_current_user_id] = mock_user_id
        app_with_mocks.dependency_overrides[require_chef_or_above] = mock_role_admin

        # Act
        response = client_with_mocks.get("/api/audit/history/devis/123")

        # Assert
        assert response.status_code == 200

    def test_get_user_actions_with_insufficient_role_returns_403(
        self, client_with_mocks, app_with_mocks
    ):
        """Test: GET /audit/user avec rôle insuffisant retourne 403."""
        # Arrange
        from shared.infrastructure.web.dependencies import (
            get_current_user_id,
            require_chef_or_above,
        )

        def mock_user_id():
            return 1

        def mock_role_insufficient():
            raise HTTPException(
                status_code=403,
                detail="Accès réservé aux chefs de chantier et supérieurs",
            )

        app_with_mocks.dependency_overrides[get_current_user_id] = mock_user_id
        app_with_mocks.dependency_overrides[require_chef_or_above] = (
            mock_role_insufficient
        )

        # Act
        response = client_with_mocks.get("/api/audit/user/1")

        # Assert
        assert response.status_code == 403

    def test_get_user_actions_with_authorized_role_returns_200(
        self, client_with_mocks, app_with_mocks
    ):
        """Test: GET /audit/user avec rôle autorisé retourne 200."""
        # Arrange
        from shared.infrastructure.web.dependencies import (
            get_current_user_id,
            require_chef_or_above,
        )

        def mock_user_id():
            return 1

        def mock_role_authorized():
            return "admin"

        app_with_mocks.dependency_overrides[get_current_user_id] = mock_user_id
        app_with_mocks.dependency_overrides[require_chef_or_above] = (
            mock_role_authorized
        )

        # Act
        response = client_with_mocks.get("/api/audit/user/1")

        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_recent_entries_with_insufficient_role_returns_403(
        self, client_with_mocks, app_with_mocks
    ):
        """Test: GET /audit/recent avec rôle insuffisant retourne 403."""
        # Arrange
        from shared.infrastructure.web.dependencies import (
            get_current_user_id,
            require_chef_or_above,
        )

        def mock_user_id():
            return 1

        def mock_role_insufficient():
            raise HTTPException(status_code=403, detail="Accès interdit")

        app_with_mocks.dependency_overrides[get_current_user_id] = mock_user_id
        app_with_mocks.dependency_overrides[require_chef_or_above] = (
            mock_role_insufficient
        )

        # Act
        response = client_with_mocks.get("/api/audit/recent")

        # Assert
        assert response.status_code == 403

    def test_get_recent_entries_with_authorized_role_returns_200(
        self, client_with_mocks, app_with_mocks
    ):
        """Test: GET /audit/recent avec rôle autorisé retourne 200."""
        # Arrange
        from shared.infrastructure.web.dependencies import (
            get_current_user_id,
            require_chef_or_above,
        )

        def mock_user_id():
            return 1

        def mock_role_authorized():
            return "conducteur"

        app_with_mocks.dependency_overrides[get_current_user_id] = mock_user_id
        app_with_mocks.dependency_overrides[require_chef_or_above] = (
            mock_role_authorized
        )

        # Act
        response = client_with_mocks.get("/api/audit/recent")

        # Assert
        assert response.status_code == 200

    def test_search_audit_with_insufficient_role_returns_403(
        self, client_with_mocks, app_with_mocks
    ):
        """Test: GET /audit/search avec rôle insuffisant retourne 403."""
        # Arrange
        from shared.infrastructure.web.dependencies import (
            get_current_user_id,
            require_chef_or_above,
        )

        def mock_user_id():
            return 1

        def mock_role_insufficient():
            raise HTTPException(status_code=403, detail="Accès interdit")

        app_with_mocks.dependency_overrides[get_current_user_id] = mock_user_id
        app_with_mocks.dependency_overrides[require_chef_or_above] = (
            mock_role_insufficient
        )

        # Act
        response = client_with_mocks.get("/api/audit/search")

        # Assert
        assert response.status_code == 403

    def test_search_audit_with_authorized_role_returns_200(
        self, client_with_mocks, app_with_mocks
    ):
        """Test: GET /audit/search avec rôle autorisé retourne 200."""
        # Arrange
        from shared.infrastructure.web.dependencies import (
            get_current_user_id,
            require_chef_or_above,
        )

        def mock_user_id():
            return 1

        def mock_role_authorized():
            return "admin"

        app_with_mocks.dependency_overrides[get_current_user_id] = mock_user_id
        app_with_mocks.dependency_overrides[require_chef_or_above] = (
            mock_role_authorized
        )

        # Act
        response = client_with_mocks.get("/api/audit/search")

        # Assert
        assert response.status_code == 200
        assert "entries" in response.json()
        assert "total" in response.json()
