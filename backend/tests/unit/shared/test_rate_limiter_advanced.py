"""Tests unitaires pour ExponentialBackoffLimiter et get_limit_for_endpoint."""

import time
from datetime import datetime, timedelta
from unittest.mock import patch

from shared.infrastructure.rate_limiter_advanced import (
    ExponentialBackoffLimiter,
    get_limit_for_endpoint,
    ENDPOINT_LIMITS,
)


class TestExponentialBackoffLimiter:
    """Tests pour le rate limiter avec backoff exponentiel."""

    def setup_method(self):
        self.limiter = ExponentialBackoffLimiter()

    def test_no_violation_not_blocked(self):
        """IP sans violation n'est pas bloquée."""
        is_blocked, retry = self.limiter.check_and_increment("1.2.3.4")
        assert is_blocked is False
        assert retry == 0

    def test_record_violation_returns_retry(self):
        """record_violation retourne un délai > 0."""
        retry = self.limiter.record_violation("1.2.3.4")
        assert retry == 30  # 30 * 2^0

    def test_second_violation_doubles_retry(self):
        """Deuxième violation double le délai."""
        self.limiter.record_violation("1.2.3.4")
        retry = self.limiter.record_violation("1.2.3.4")
        assert retry == 60  # 30 * 2^1

    def test_third_violation(self):
        """Troisième violation = 120s."""
        for _ in range(2):
            self.limiter.record_violation("1.2.3.4")
        retry = self.limiter.record_violation("1.2.3.4")
        assert retry == 120  # 30 * 2^2

    def test_max_backoff_capped_at_300(self):
        """Backoff plafonné à 300s."""
        for _ in range(10):
            self.limiter.record_violation("1.2.3.4")
        retry = self.limiter.record_violation("1.2.3.4")
        assert retry == 300

    def test_blocked_after_violation(self):
        """IP bloquée immédiatement après violation."""
        self.limiter.record_violation("1.2.3.4")
        is_blocked, retry = self.limiter.check_and_increment("1.2.3.4")
        assert is_blocked is True
        assert retry > 0

    def test_reset_clears_violations(self):
        """reset() supprime les violations."""
        self.limiter.record_violation("1.2.3.4")
        self.limiter.reset("1.2.3.4")
        is_blocked, retry = self.limiter.check_and_increment("1.2.3.4")
        assert is_blocked is False

    def test_reset_nonexistent_ip_no_error(self):
        """reset() sur IP inconnue ne lève pas d'erreur."""
        self.limiter.reset("unknown.ip")

    def test_different_ips_independent(self):
        """Les violations sont indépendantes par IP."""
        self.limiter.record_violation("1.1.1.1")
        is_blocked, _ = self.limiter.check_and_increment("2.2.2.2")
        assert is_blocked is False

    def test_violation_reset_after_one_hour(self):
        """Violations réinitialisées après 1h sans activité."""
        self.limiter.record_violation("1.2.3.4")
        # Simuler 1h+ passée
        self.limiter.last_violation["1.2.3.4"] = datetime.now() - timedelta(hours=2)
        is_blocked, retry = self.limiter.check_and_increment("1.2.3.4")
        assert is_blocked is False
        assert retry == 0

    def test_check_not_blocked_after_retry_period(self):
        """IP non bloquée après expiration du délai de retry."""
        self.limiter.record_violation("1.2.3.4")
        # Simuler expiration du délai (30s+)
        self.limiter.last_violation["1.2.3.4"] = datetime.now() - timedelta(seconds=31)
        is_blocked, retry = self.limiter.check_and_increment("1.2.3.4")
        assert is_blocked is False


class TestGetLimitForEndpoint:
    """Tests pour get_limit_for_endpoint."""

    def test_exact_match(self):
        """Match exact d'un endpoint connu."""
        assert get_limit_for_endpoint("/api/auth/login") == "5/minute"

    def test_prefix_match(self):
        """Match par préfixe."""
        assert get_limit_for_endpoint("/api/auth/login/extra") == "5/minute"

    def test_default_limit(self):
        """Endpoint inconnu retourne la limite par défaut."""
        assert get_limit_for_endpoint("/api/unknown/path") == "120/minute"

    def test_register_limit(self):
        """Limite de /api/auth/register."""
        assert get_limit_for_endpoint("/api/auth/register") == "3/hour"

    def test_upload_limit(self):
        """Limite de /api/upload."""
        assert get_limit_for_endpoint("/api/upload") == "10/minute"

    def test_dashboard_limit(self):
        """Limite de /api/dashboard/feed."""
        assert get_limit_for_endpoint("/api/dashboard/feed") == "100/minute"

    def test_export_limit(self):
        """Limite de /api/export/feuilles-heures."""
        assert get_limit_for_endpoint("/api/export/feuilles-heures") == "5/minute"
