"""Tests unitaires pour JWTTokenService."""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from modules.auth.adapters.providers.jwt_token_service import JWTTokenService
from modules.auth.domain.value_objects import Role


class MockUser:
    """Mock utilisateur pour les tests."""

    def __init__(self, user_id: int = 1, email: str = "test@test.com", role: str = "compagnon"):
        self.id = user_id
        self.email = Mock()
        self.email.__str__ = Mock(return_value=email)
        self.role = Mock()
        self.role.value = role


class TestJWTTokenServiceInit:
    """Tests d'initialisation."""

    def test_init_with_valid_secret(self):
        """Test init avec secret valide."""
        service = JWTTokenService(
            secret_key="a" * 32,  # 32 caractères minimum
            algorithm="HS256",
            expires_minutes=60,
        )
        assert service.secret_key == "a" * 32
        assert service.algorithm == "HS256"
        assert service.expires_minutes == 60

    def test_init_short_secret_raises_error(self):
        """Test secret trop court lève une erreur."""
        with pytest.raises(ValueError) as exc:
            JWTTokenService(secret_key="short")
        assert "32 caractères" in str(exc.value)

    def test_init_empty_secret_raises_error(self):
        """Test secret vide lève une erreur."""
        with pytest.raises(ValueError):
            JWTTokenService(secret_key="")

    def test_init_with_defaults(self):
        """Test init avec valeurs par défaut."""
        service = JWTTokenService(secret_key="a" * 32)
        assert service.algorithm == "HS256"
        assert service.expires_minutes == 60


class TestJWTGenerate:
    """Tests de generate."""

    def test_generate_returns_string_token(self):
        """Test generate retourne un string."""
        service = JWTTokenService(secret_key="a" * 32)
        user = MockUser()

        token = service.generate(user)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_has_three_parts(self):
        """Test token JWT a 3 parties (header.payload.signature)."""
        service = JWTTokenService(secret_key="a" * 32)
        user = MockUser()

        token = service.generate(user)
        parts = token.split(".")

        assert len(parts) == 3

    def test_generate_different_users_different_tokens(self):
        """Test utilisateurs différents ont tokens différents."""
        service = JWTTokenService(secret_key="a" * 32)
        user1 = MockUser(user_id=1)
        user2 = MockUser(user_id=2)

        token1 = service.generate(user1)
        token2 = service.generate(user2)

        assert token1 != token2


class TestJWTVerify:
    """Tests de verify."""

    def test_verify_valid_token(self):
        """Test vérification token valide."""
        service = JWTTokenService(secret_key="a" * 32)
        user = MockUser(user_id=42, email="user@test.com", role="admin")

        token = service.generate(user)
        payload = service.verify(token)

        assert payload is not None
        assert payload.user_id == 42
        assert payload.email == "user@test.com"
        assert payload.role == "admin"

    def test_verify_invalid_token_returns_none(self):
        """Test token invalide retourne None."""
        service = JWTTokenService(secret_key="a" * 32)

        payload = service.verify("invalid.token.here")

        assert payload is None

    def test_verify_wrong_secret_returns_none(self):
        """Test token avec mauvais secret retourne None."""
        service1 = JWTTokenService(secret_key="a" * 32)
        service2 = JWTTokenService(secret_key="b" * 32)
        user = MockUser()

        token = service1.generate(user)
        payload = service2.verify(token)

        assert payload is None

    def test_verify_malformed_token_returns_none(self):
        """Test token malformé retourne None."""
        service = JWTTokenService(secret_key="a" * 32)

        payload = service.verify("not-a-jwt")

        assert payload is None

    def test_verify_empty_token_returns_none(self):
        """Test token vide retourne None."""
        service = JWTTokenService(secret_key="a" * 32)

        payload = service.verify("")

        assert payload is None


class TestJWTGetUserId:
    """Tests de get_user_id."""

    def test_get_user_id_valid_token(self):
        """Test extraction ID depuis token valide."""
        service = JWTTokenService(secret_key="a" * 32)
        user = MockUser(user_id=123)

        token = service.generate(user)
        user_id = service.get_user_id(token)

        assert user_id == 123

    def test_get_user_id_invalid_token_returns_none(self):
        """Test token invalide retourne None."""
        service = JWTTokenService(secret_key="a" * 32)

        user_id = service.get_user_id("invalid.token")

        assert user_id is None


class TestJWTExpiration:
    """Tests d'expiration."""

    def test_token_has_expiration(self):
        """Test token a une expiration."""
        service = JWTTokenService(secret_key="a" * 32, expires_minutes=30)
        user = MockUser()

        token = service.generate(user)
        payload = service.verify(token)

        assert payload is not None
        assert payload.exp is not None

    def test_custom_expiration_time(self):
        """Test durée d'expiration personnalisée."""
        service = JWTTokenService(secret_key="a" * 32, expires_minutes=120)
        user = MockUser()

        token = service.generate(user)
        payload = service.verify(token)

        # Le token devrait être valide pendant 2 heures
        assert payload is not None


class TestJWTRoundtrip:
    """Tests de cycle complet."""

    def test_roundtrip_preserves_all_claims(self):
        """Test cycle complet préserve toutes les claims."""
        service = JWTTokenService(secret_key="secure_secret_key_for_testing_123")
        user = MockUser(user_id=999, email="complete@test.com", role="conducteur")

        token = service.generate(user)
        payload = service.verify(token)

        assert payload.user_id == 999
        assert payload.email == "complete@test.com"
        assert payload.role == "conducteur"
