"""Tests unitaires pour l'entity APIKey."""

from datetime import datetime, timedelta
from uuid import uuid4
import pytest

from modules.auth.domain.entities.api_key import APIKey


def test_is_expired_returns_true_when_expired():
    """Vérifie qu'une clé expirée retourne True."""
    # Arrange
    api_key = APIKey(
        id=uuid4(),
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description=None,
        scopes=["read"],
        rate_limit_per_hour=1000,
        is_active=True,
        last_used_at=None,
        expires_at=datetime.utcnow() - timedelta(days=1),  # Expiré depuis 1 jour
        created_at=datetime.utcnow() - timedelta(days=10),
    )

    # Act
    result = api_key.is_expired()

    # Assert
    assert result is True, "Une clé dont expires_at est passé devrait être expirée"


def test_is_expired_returns_false_when_not_expired():
    """Vérifie qu'une clé non expirée retourne False."""
    # Arrange
    api_key = APIKey(
        id=uuid4(),
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description=None,
        scopes=["read"],
        rate_limit_per_hour=1000,
        is_active=True,
        last_used_at=None,
        expires_at=datetime.utcnow() + timedelta(days=30),  # Expire dans 30 jours
        created_at=datetime.utcnow(),
    )

    # Act
    result = api_key.is_expired()

    # Assert
    assert result is False, "Une clé dont expires_at est dans le futur ne devrait pas être expirée"


def test_is_expired_returns_false_when_no_expiration():
    """Vérifie qu'une clé sans date d'expiration retourne False."""
    # Arrange
    api_key = APIKey(
        id=uuid4(),
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description=None,
        scopes=["read"],
        rate_limit_per_hour=1000,
        is_active=True,
        last_used_at=None,
        expires_at=None,  # Pas d'expiration
        created_at=datetime.utcnow(),
    )

    # Act
    result = api_key.is_expired()

    # Assert
    assert result is False, "Une clé sans expires_at ne devrait jamais être expirée"


def test_can_perform_exact_scope_match():
    """Vérifie que can_perform retourne True pour un scope exact."""
    # Arrange
    api_key = APIKey(
        id=uuid4(),
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description=None,
        scopes=["read", "chantiers:read"],
        rate_limit_per_hour=1000,
        is_active=True,
        last_used_at=None,
        expires_at=None,
        created_at=datetime.utcnow(),
    )

    # Act & Assert
    assert api_key.can_perform("read") is True, "Devrait avoir le scope 'read'"
    assert api_key.can_perform("chantiers:read") is True, "Devrait avoir le scope 'chantiers:read'"


def test_can_perform_wildcard_scope():
    """Vérifie que can_perform gère les wildcards."""
    # Arrange
    api_key = APIKey(
        id=uuid4(),
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description=None,
        scopes=["chantiers:*"],  # Wildcard
        rate_limit_per_hour=1000,
        is_active=True,
        last_used_at=None,
        expires_at=None,
        created_at=datetime.utcnow(),
    )

    # Act & Assert
    assert api_key.can_perform("chantiers:read") is True, "Wildcard 'chantiers:*' devrait autoriser 'chantiers:read'"
    assert api_key.can_perform("chantiers:write") is True, "Wildcard 'chantiers:*' devrait autoriser 'chantiers:write'"
    assert api_key.can_perform("planning:read") is False, "Wildcard 'chantiers:*' ne devrait pas autoriser 'planning:read'"


def test_can_perform_returns_false_when_inactive():
    """Vérifie que can_perform retourne False si la clé est inactive."""
    # Arrange
    api_key = APIKey(
        id=uuid4(),
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description=None,
        scopes=["read"],
        rate_limit_per_hour=1000,
        is_active=False,  # Inactive
        last_used_at=None,
        expires_at=None,
        created_at=datetime.utcnow(),
    )

    # Act
    result = api_key.can_perform("read")

    # Assert
    assert result is False, "Une clé inactive ne devrait autoriser aucun scope"


def test_can_perform_returns_false_when_expired():
    """Vérifie que can_perform retourne False si la clé est expirée."""
    # Arrange
    api_key = APIKey(
        id=uuid4(),
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description=None,
        scopes=["read"],
        rate_limit_per_hour=1000,
        is_active=True,
        last_used_at=None,
        expires_at=datetime.utcnow() - timedelta(days=1),  # Expirée
        created_at=datetime.utcnow() - timedelta(days=10),
    )

    # Act
    result = api_key.can_perform("read")

    # Assert
    assert result is False, "Une clé expirée ne devrait autoriser aucun scope"


def test_can_perform_returns_false_for_missing_scope():
    """Vérifie que can_perform retourne False si le scope n'est pas accordé."""
    # Arrange
    api_key = APIKey(
        id=uuid4(),
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description=None,
        scopes=["read"],
        rate_limit_per_hour=1000,
        is_active=True,
        last_used_at=None,
        expires_at=None,
        created_at=datetime.utcnow(),
    )

    # Act
    result = api_key.can_perform("write")

    # Assert
    assert result is False, "Ne devrait pas autoriser un scope non accordé"


def test_revoke_sets_is_active_to_false():
    """Vérifie que revoke() désactive la clé."""
    # Arrange
    api_key = APIKey(
        id=uuid4(),
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description=None,
        scopes=["read"],
        rate_limit_per_hour=1000,
        is_active=True,
        last_used_at=None,
        expires_at=None,
        created_at=datetime.utcnow(),
    )

    # Act
    api_key.revoke()

    # Assert
    assert api_key.is_active is False, "revoke() devrait mettre is_active à False"


def test_update_last_used_updates_timestamp():
    """Vérifie que update_last_used() met à jour last_used_at."""
    # Arrange
    api_key = APIKey(
        id=uuid4(),
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description=None,
        scopes=["read"],
        rate_limit_per_hour=1000,
        is_active=True,
        last_used_at=None,
        expires_at=None,
        created_at=datetime.utcnow(),
    )

    # Act
    before = datetime.utcnow()
    api_key.update_last_used()
    after = datetime.utcnow()

    # Assert
    assert api_key.last_used_at is not None, "last_used_at devrait être défini"
    assert before <= api_key.last_used_at <= after, "last_used_at devrait être entre avant/après l'appel"


def test_is_valid_for_auth_returns_true_when_active_and_not_expired():
    """Vérifie que is_valid_for_auth retourne True si active et non expirée."""
    # Arrange
    api_key = APIKey(
        id=uuid4(),
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description=None,
        scopes=["read"],
        rate_limit_per_hour=1000,
        is_active=True,
        last_used_at=None,
        expires_at=datetime.utcnow() + timedelta(days=30),
        created_at=datetime.utcnow(),
    )

    # Act
    result = api_key.is_valid_for_auth()

    # Assert
    assert result is True, "Une clé active et non expirée devrait être valide pour l'auth"


def test_is_valid_for_auth_returns_false_when_inactive():
    """Vérifie que is_valid_for_auth retourne False si inactive."""
    # Arrange
    api_key = APIKey(
        id=uuid4(),
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description=None,
        scopes=["read"],
        rate_limit_per_hour=1000,
        is_active=False,  # Inactive
        last_used_at=None,
        expires_at=None,
        created_at=datetime.utcnow(),
    )

    # Act
    result = api_key.is_valid_for_auth()

    # Assert
    assert result is False, "Une clé inactive ne devrait pas être valide pour l'auth"


def test_is_valid_for_auth_returns_false_when_expired():
    """Vérifie que is_valid_for_auth retourne False si expirée."""
    # Arrange
    api_key = APIKey(
        id=uuid4(),
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description=None,
        scopes=["read"],
        rate_limit_per_hour=1000,
        is_active=True,
        last_used_at=None,
        expires_at=datetime.utcnow() - timedelta(days=1),  # Expirée
        created_at=datetime.utcnow() - timedelta(days=10),
    )

    # Act
    result = api_key.is_valid_for_auth()

    # Assert
    assert result is False, "Une clé expirée ne devrait pas être valide pour l'auth"
