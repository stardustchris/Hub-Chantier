"""Tests unitaires pour CSRFMiddleware."""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from fastapi import Request, Response
from starlette.datastructures import URL, Headers

from shared.infrastructure.web.csrf_middleware import CSRFMiddleware


def _make_request(method: str = "GET", path: str = "/api/test", headers: dict = None, cookies: dict = None):
    """Crée un mock Request."""
    request = Mock(spec=Request)
    request.method = method
    request.url = URL(f"http://localhost{path}")
    request.headers = Headers(headers or {})
    request.cookies = cookies or {}
    return request


class TestCSRFMiddlewareExemptions:
    """Tests des exemptions CSRF."""

    def test_exempt_paths(self):
        """Les chemins exemptés sont correctement définis."""
        middleware = CSRFMiddleware(app=Mock())
        assert "/api/auth/login" in middleware.EXEMPT_PATHS
        assert "/api/auth/register" in middleware.EXEMPT_PATHS
        assert "/health" in middleware.EXEMPT_PATHS

    def test_safe_methods(self):
        """Les méthodes safe sont correctement définies."""
        middleware = CSRFMiddleware(app=Mock())
        assert "GET" in middleware.SAFE_METHODS
        assert "HEAD" in middleware.SAFE_METHODS
        assert "OPTIONS" in middleware.SAFE_METHODS

    @pytest.mark.asyncio
    async def test_exempt_path_skips_validation(self):
        """Un chemin exempté passe sans validation CSRF."""
        middleware = CSRFMiddleware(app=Mock())
        request = _make_request(method="POST", path="/api/auth/login")
        mock_response = Response(status_code=200)
        call_next = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(request, call_next)

        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_get_request_passes_and_sets_cookie(self):
        """GET passe et ajoute un cookie CSRF."""
        middleware = CSRFMiddleware(app=Mock())
        request = _make_request(method="GET", path="/api/chantiers")
        mock_response = Mock(spec=Response)
        mock_response.set_cookie = Mock()
        call_next = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(request, call_next)

        call_next.assert_called_once()
        mock_response.set_cookie.assert_called_once()
        call_args = mock_response.set_cookie.call_args
        assert call_args.kwargs["key"] == "csrf_token"
        assert call_args.kwargs["httponly"] is False  # Accessible en JS

    @pytest.mark.asyncio
    async def test_post_without_csrf_token_returns_403(self):
        """POST sans token CSRF retourne 403."""
        middleware = CSRFMiddleware(app=Mock())
        request = _make_request(method="POST", path="/api/chantiers")
        call_next = AsyncMock()

        response = await middleware.dispatch(request, call_next)

        assert response.status_code == 403
        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_post_with_mismatched_token_returns_403(self):
        """POST avec token CSRF non-concordant retourne 403."""
        middleware = CSRFMiddleware(app=Mock())
        request = _make_request(
            method="POST",
            path="/api/chantiers",
            headers={"X-CSRF-Token": "token_a"},
            cookies={"csrf_token": "token_b"},
        )
        call_next = AsyncMock()

        response = await middleware.dispatch(request, call_next)

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_post_with_valid_token_passes(self):
        """POST avec token CSRF valide passe."""
        middleware = CSRFMiddleware(app=Mock())
        token = "valid_csrf_token_123"
        request = _make_request(
            method="POST",
            path="/api/chantiers",
            headers={"X-CSRF-Token": token},
            cookies={"csrf_token": token},
        )
        mock_response = Mock(spec=Response)
        mock_response.set_cookie = Mock()
        call_next = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(request, call_next)

        call_next.assert_called_once_with(request)
        # Token renouvelé après requête mutable
        mock_response.set_cookie.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_with_only_header_returns_403(self):
        """POST avec header mais pas de cookie retourne 403."""
        middleware = CSRFMiddleware(app=Mock())
        request = _make_request(
            method="POST",
            path="/api/chantiers",
            headers={"X-CSRF-Token": "token"},
            cookies={},
        )
        call_next = AsyncMock()

        response = await middleware.dispatch(request, call_next)

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_put_delete_patch_also_checked(self):
        """PUT, DELETE, PATCH sont aussi vérifiés."""
        middleware = CSRFMiddleware(app=Mock())
        for method in ["PUT", "DELETE", "PATCH"]:
            request = _make_request(method=method, path="/api/chantiers/1")
            call_next = AsyncMock()
            response = await middleware.dispatch(request, call_next)
            assert response.status_code == 403
