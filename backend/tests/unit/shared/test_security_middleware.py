"""Tests unitaires pour SecurityHeadersMiddleware."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from starlette.requests import Request
from starlette.responses import Response
from starlette.testclient import TestClient
from fastapi import FastAPI

from shared.infrastructure.web.security_middleware import (
    SecurityHeadersMiddleware,
    CSP_PRODUCTION,
    CSP_DEVELOPMENT,
)


class TestSecurityHeadersMiddlewareHeaders:
    """Tests des en-tetes de securite."""

    @pytest.fixture
    def app(self):
        """Cree une app FastAPI de test."""
        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)

        @app.get("/test")
        def test_route():
            return {"message": "test"}

        @app.get("/api/data")
        def api_route():
            return {"data": "sensitive"}

        return app

    @pytest.fixture
    def client(self, app):
        return TestClient(app)

    def test_x_frame_options_header(self, client):
        """Test en-tete X-Frame-Options."""
        response = client.get("/test")

        assert response.headers["X-Frame-Options"] == "DENY"

    def test_x_content_type_options_header(self, client):
        """Test en-tete X-Content-Type-Options."""
        response = client.get("/test")

        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_x_xss_protection_header(self, client):
        """Test en-tete X-XSS-Protection."""
        response = client.get("/test")

        assert response.headers["X-XSS-Protection"] == "1; mode=block"

    def test_strict_transport_security_header(self, client):
        """Test en-tete HSTS."""
        response = client.get("/test")

        hsts = response.headers["Strict-Transport-Security"]
        assert "max-age=31536000" in hsts
        assert "includeSubDomains" in hsts
        assert "preload" in hsts

    def test_referrer_policy_header(self, client):
        """Test en-tete Referrer-Policy."""
        response = client.get("/test")

        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    def test_permissions_policy_header(self, client):
        """Test en-tete Permissions-Policy."""
        response = client.get("/test")

        permissions = response.headers["Permissions-Policy"]
        assert "camera=()" in permissions
        assert "microphone=()" in permissions
        assert "geolocation=(self)" in permissions
        assert "payment=()" in permissions

    def test_content_security_policy_header_exists(self, client):
        """Test que CSP existe."""
        response = client.get("/test")

        assert "Content-Security-Policy" in response.headers


class TestSecurityHeadersMiddlewareCSP:
    """Tests specifiques pour Content-Security-Policy."""

    @pytest.fixture
    def app_debug(self):
        """App en mode debug."""
        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)

        @app.get("/test")
        def test_route():
            return {"message": "test"}

        return app

    def test_csp_production_no_unsafe_inline(self):
        """Test CSP production sans unsafe-inline."""
        assert "unsafe-inline" not in CSP_PRODUCTION
        assert "unsafe-eval" not in CSP_PRODUCTION

    def test_csp_development_allows_inline(self):
        """Test CSP dev permet inline."""
        assert "unsafe-inline" in CSP_DEVELOPMENT
        assert "unsafe-eval" in CSP_DEVELOPMENT

    def test_csp_frame_ancestors_none(self):
        """Test frame-ancestors deny."""
        assert "frame-ancestors 'none'" in CSP_PRODUCTION
        assert "frame-ancestors 'none'" in CSP_DEVELOPMENT

    def test_csp_base_uri_self(self):
        """Test base-uri self."""
        assert "base-uri 'self'" in CSP_PRODUCTION
        assert "base-uri 'self'" in CSP_DEVELOPMENT

    @patch("shared.infrastructure.web.security_middleware.settings")
    def test_uses_production_csp_when_not_debug(self, mock_settings):
        """Test utilisation CSP production."""
        mock_settings.DEBUG = False

        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)

        @app.get("/test")
        def test_route():
            return {"test": True}

        client = TestClient(app)
        response = client.get("/test")

        csp = response.headers["Content-Security-Policy"]
        assert "unsafe-inline" not in csp

    @patch("shared.infrastructure.web.security_middleware.settings")
    def test_uses_dev_csp_when_debug(self, mock_settings):
        """Test utilisation CSP dev."""
        mock_settings.DEBUG = True

        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)

        @app.get("/test")
        def test_route():
            return {"test": True}

        client = TestClient(app)
        response = client.get("/test")

        csp = response.headers["Content-Security-Policy"]
        assert "unsafe-inline" in csp


class TestSecurityHeadersMiddlewareAPICache:
    """Tests du cache pour les routes API."""

    @pytest.fixture
    def app(self):
        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)

        @app.get("/api/sensitive")
        def api_route():
            return {"secret": "data"}

        @app.get("/public")
        def public_route():
            return {"public": "data"}

        return app

    @pytest.fixture
    def client(self, app):
        return TestClient(app)

    def test_api_routes_no_cache(self, client):
        """Test que les routes API ont no-cache."""
        response = client.get("/api/sensitive")

        assert response.headers["Cache-Control"] == "no-store, no-cache, must-revalidate"
        assert response.headers["Pragma"] == "no-cache"

    def test_non_api_routes_no_cache_headers(self, client):
        """Test que les routes non-API n'ont pas les headers de cache."""
        response = client.get("/public")

        # Les headers de cache ne sont pas ajoutes pour les routes non-API
        # Sauf si Cache-Control est explicitement set ailleurs
        cache_control = response.headers.get("Cache-Control", "")
        assert "no-store" not in cache_control or "/api/" in str(response.request.url)


class TestSecurityHeadersMiddlewareAsync:
    """Tests du comportement asynchrone du middleware."""

    @pytest.mark.asyncio
    async def test_dispatch_calls_next(self):
        """Test que dispatch appelle le prochain handler."""
        middleware = SecurityHeadersMiddleware(app=Mock())

        mock_request = Mock(spec=Request)
        mock_request.url.path = "/test"

        mock_response = Response(content="test")
        mock_call_next = AsyncMock(return_value=mock_response)

        result = await middleware.dispatch(mock_request, mock_call_next)

        mock_call_next.assert_awaited_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_dispatch_adds_headers_to_response(self):
        """Test que dispatch ajoute les headers."""
        middleware = SecurityHeadersMiddleware(app=Mock())

        mock_request = Mock(spec=Request)
        mock_request.url.path = "/test"

        mock_response = Response(content="test")
        mock_call_next = AsyncMock(return_value=mock_response)

        result = await middleware.dispatch(mock_request, mock_call_next)

        assert "X-Frame-Options" in result.headers
        assert "X-Content-Type-Options" in result.headers


class TestCSPPolicies:
    """Tests des politiques CSP specifiques."""

    def test_csp_production_restricts_img_src(self):
        """Test que img-src est restreint en prod."""
        # Pas de https: pour eviter exfiltration
        assert "img-src 'self' data: blob:" in CSP_PRODUCTION
        assert "https:" not in CSP_PRODUCTION.split("img-src")[1].split(";")[0]

    def test_csp_development_allows_websocket(self):
        """Test que dev permet websocket pour HMR."""
        assert "ws:" in CSP_DEVELOPMENT
        assert "wss:" in CSP_DEVELOPMENT

    def test_csp_form_action_self(self):
        """Test form-action limite a self."""
        assert "form-action 'self'" in CSP_PRODUCTION
        assert "form-action 'self'" in CSP_DEVELOPMENT
