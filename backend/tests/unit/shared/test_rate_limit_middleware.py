"""Tests unitaires pour RateLimitMiddleware."""

import os
import pytest
from unittest.mock import AsyncMock, Mock, patch, PropertyMock
from fastapi import Request, Response
from starlette.datastructures import Headers

from shared.infrastructure.web.rate_limit_middleware import (
    RateLimitMiddleware,
    _load_trusted_proxies,
    create_rate_limit_info_endpoint,
)


def _make_request(path: str = "/api/test", client_host: str = "1.2.3.4", headers: dict = None):
    """Crée un mock Request."""
    request = Mock(spec=Request)
    request.url = Mock()
    request.url.path = path
    request.method = "POST"
    request.headers = Headers(headers or {})
    client = Mock()
    client.host = client_host
    request.client = client
    return request


class TestLoadTrustedProxies:
    """Tests pour _load_trusted_proxies."""

    def test_default_proxies(self):
        """Défaut: localhost + Docker bridge."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove TRUSTED_PROXIES if exists
            os.environ.pop("TRUSTED_PROXIES", None)
            proxies = _load_trusted_proxies()
        assert "127.0.0.1" in proxies
        assert "::1" in proxies

    def test_custom_proxies_from_env(self):
        """Proxies personnalisés via env."""
        with patch.dict(os.environ, {"TRUSTED_PROXIES": "10.0.0.1,192.168.1.1"}):
            proxies = _load_trusted_proxies()
        assert proxies == {"10.0.0.1", "192.168.1.1"}

    def test_whitespace_stripped(self):
        """Les espaces sont nettoyés."""
        with patch.dict(os.environ, {"TRUSTED_PROXIES": " 10.0.0.1 , 10.0.0.2 "}):
            proxies = _load_trusted_proxies()
        assert "10.0.0.1" in proxies
        assert "10.0.0.2" in proxies

    def test_empty_entries_filtered(self):
        """Les entrées vides sont ignorées."""
        with patch.dict(os.environ, {"TRUSTED_PROXIES": "10.0.0.1,,10.0.0.2,"}):
            proxies = _load_trusted_proxies()
        assert "" not in proxies
        assert len(proxies) == 2


class TestRateLimitMiddleware:
    """Tests pour RateLimitMiddleware."""

    @pytest.mark.asyncio
    async def test_not_blocked_passes_through(self):
        """IP non bloquée passe la requête."""
        middleware = RateLimitMiddleware(app=Mock())
        request = _make_request()
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}
        call_next = AsyncMock(return_value=mock_response)

        with patch("shared.infrastructure.web.rate_limit_middleware.backoff_limiter") as mock_limiter:
            mock_limiter.check_and_increment.return_value = (False, 0)
            mock_limiter.reset = Mock()
            response = await middleware.dispatch(request, call_next)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_blocked_returns_429(self):
        """IP bloquée retourne 429."""
        middleware = RateLimitMiddleware(app=Mock())
        request = _make_request()
        call_next = AsyncMock()

        with patch("shared.infrastructure.web.rate_limit_middleware.backoff_limiter") as mock_limiter:
            mock_limiter.check_and_increment.return_value = (True, 60)
            mock_limiter.violations = {"1.2.3.4": 3}
            response = await middleware.dispatch(request, call_next)

        assert response.status_code == 429
        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_sensitive_endpoint_401_records_violation(self):
        """401 sur endpoint sensible enregistre une violation."""
        middleware = RateLimitMiddleware(app=Mock())
        request = _make_request(path="/api/auth/login")
        mock_response = Mock(spec=Response)
        mock_response.status_code = 401
        mock_response.headers = {}
        call_next = AsyncMock(return_value=mock_response)

        with patch("shared.infrastructure.web.rate_limit_middleware.backoff_limiter") as mock_limiter:
            mock_limiter.check_and_increment.return_value = (False, 0)
            mock_limiter.record_violation.return_value = 30
            response = await middleware.dispatch(request, call_next)

        mock_limiter.record_violation.assert_called_once()

    @pytest.mark.asyncio
    async def test_sensitive_endpoint_200_resets(self):
        """200 sur endpoint sensible reset les violations."""
        middleware = RateLimitMiddleware(app=Mock())
        request = _make_request(path="/api/auth/login")
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}
        call_next = AsyncMock(return_value=mock_response)

        with patch("shared.infrastructure.web.rate_limit_middleware.backoff_limiter") as mock_limiter:
            mock_limiter.check_and_increment.return_value = (False, 0)
            mock_limiter.reset = Mock()
            response = await middleware.dispatch(request, call_next)

        mock_limiter.reset.assert_called_once()

    def test_get_client_ip_direct(self):
        """IP directe sans proxy."""
        middleware = RateLimitMiddleware(app=Mock())
        request = _make_request(client_host="5.6.7.8")
        ip = middleware._get_client_ip(request)
        assert ip == "5.6.7.8"

    def test_get_client_ip_trusted_proxy_forwarded_for(self):
        """X-Forwarded-For honoré depuis proxy de confiance."""
        middleware = RateLimitMiddleware(app=Mock())
        # Temporarily set trusted proxies
        original = middleware.TRUSTED_PROXIES
        middleware.TRUSTED_PROXIES = {"127.0.0.1"}
        try:
            request = _make_request(
                client_host="127.0.0.1",
                headers={"X-Forwarded-For": "10.20.30.40, 127.0.0.1"},
            )
            ip = middleware._get_client_ip(request)
            assert ip == "10.20.30.40"
        finally:
            middleware.TRUSTED_PROXIES = original

    def test_get_client_ip_untrusted_proxy_ignores_header(self):
        """X-Forwarded-For ignoré depuis IP non-confiance."""
        middleware = RateLimitMiddleware(app=Mock())
        request = _make_request(
            client_host="evil.attacker.ip",
            headers={"X-Forwarded-For": "spoofed.ip"},
        )
        ip = middleware._get_client_ip(request)
        assert ip == "evil.attacker.ip"

    def test_is_sensitive_endpoint(self):
        """Endpoints sensibles identifiés correctement."""
        middleware = RateLimitMiddleware(app=Mock())
        assert middleware._is_sensitive_endpoint("/api/auth/login") is True
        assert middleware._is_sensitive_endpoint("/api/auth/register") is True
        assert middleware._is_sensitive_endpoint("/api/documents/upload") is True
        assert middleware._is_sensitive_endpoint("/api/chantiers") is False
        assert middleware._is_sensitive_endpoint("/api/planning") is False


class TestCreateRateLimitInfoEndpoint:
    """Tests pour create_rate_limit_info_endpoint."""

    def test_returns_dict_with_limits(self):
        """Retourne un dict avec les limites."""
        info = create_rate_limit_info_endpoint()
        assert "limits" in info
        assert "backoff_strategy" in info
        assert "sensitive_endpoints" in info

    def test_backoff_strategy(self):
        """Stratégie de backoff correcte."""
        info = create_rate_limit_info_endpoint()
        strategy = info["backoff_strategy"]
        assert strategy["reset_after_hours"] == 1
        assert 300 in strategy["retry_after_seconds"]
