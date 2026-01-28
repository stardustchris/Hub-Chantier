"""Tests unitaires pour ListAPIKeysUseCase."""

from unittest.mock import Mock
from datetime import datetime, timedelta
from uuid import uuid4
import pytest

from modules.auth.application.use_cases.list_api_keys import ListAPIKeysUseCase
from modules.auth.domain.entities.api_key import APIKey


def test_list_api_keys_returns_empty_list_when_no_keys():
    """Vérifie qu'une liste vide est retournée quand l'utilisateur n'a pas de clés."""
    # Arrange
    mock_repo = Mock()
    mock_repo.find_by_user.return_value = []
    use_case = ListAPIKeysUseCase(mock_repo)

    # Act
    result = use_case.execute(user_id=1)

    # Assert
    assert result == [], "Devrait retourner une liste vide"
    mock_repo.find_by_user.assert_called_once_with(user_id=1, include_revoked=False)


def test_list_api_keys_returns_user_keys():
    """Vérifie que les clés de l'utilisateur sont retournées."""
    # Arrange
    key1 = APIKey(
        id=uuid4(),
        key_hash="a" * 64,
        key_prefix="hbc_aaa1",
        user_id=1,
        nom="Key 1",
        description="First key",
        scopes=["read"],
        rate_limit_per_hour=1000,
        is_active=True,
        last_used_at=None,
        expires_at=None,
        created_at=datetime.utcnow(),
    )
    key2 = APIKey(
        id=uuid4(),
        key_hash="b" * 64,
        key_prefix="hbc_bbb2",
        user_id=1,
        nom="Key 2",
        description="Second key",
        scopes=["read", "write"],
        rate_limit_per_hour=2000,
        is_active=True,
        last_used_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=30),
        created_at=datetime.utcnow(),
    )

    mock_repo = Mock()
    mock_repo.find_by_user.return_value = [key1, key2]
    use_case = ListAPIKeysUseCase(mock_repo)

    # Act
    result = use_case.execute(user_id=1)

    # Assert
    assert len(result) == 2, "Devrait retourner 2 clés"
    assert result[0].key_prefix == "hbc_aaa1"
    assert result[1].key_prefix == "hbc_bbb2"
    mock_repo.find_by_user.assert_called_once_with(user_id=1, include_revoked=False)


def test_list_api_keys_excludes_revoked_by_default():
    """Vérifie que les clés révoquées sont exclues par défaut."""
    # Arrange
    mock_repo = Mock()
    mock_repo.find_by_user.return_value = []
    use_case = ListAPIKeysUseCase(mock_repo)

    # Act
    result = use_case.execute(user_id=1)

    # Assert
    mock_repo.find_by_user.assert_called_once_with(user_id=1, include_revoked=False)


def test_list_api_keys_includes_revoked_when_requested():
    """Vérifie que les clés révoquées sont incluses si demandé."""
    # Arrange
    active_key = APIKey(
        id=uuid4(),
        key_hash="a" * 64,
        key_prefix="hbc_aaa1",
        user_id=1,
        nom="Active Key",
        description=None,
        scopes=["read"],
        rate_limit_per_hour=1000,
        is_active=True,
        last_used_at=None,
        expires_at=None,
        created_at=datetime.utcnow(),
    )
    revoked_key = APIKey(
        id=uuid4(),
        key_hash="b" * 64,
        key_prefix="hbc_bbb2",
        user_id=1,
        nom="Revoked Key",
        description=None,
        scopes=["read"],
        rate_limit_per_hour=1000,
        is_active=False,  # Révoquée
        last_used_at=None,
        expires_at=None,
        created_at=datetime.utcnow(),
    )

    mock_repo = Mock()
    mock_repo.find_by_user.return_value = [active_key, revoked_key]
    use_case = ListAPIKeysUseCase(mock_repo)

    # Act
    result = use_case.execute(user_id=1, include_revoked=True)

    # Assert
    assert len(result) == 2, "Devrait retourner 2 clés (active + révoquée)"
    assert result[0].is_active is True
    assert result[1].is_active is False
    mock_repo.find_by_user.assert_called_once_with(user_id=1, include_revoked=True)


def test_list_api_keys_converts_to_dto():
    """Vérifie que les entities sont correctement converties en DTOs."""
    # Arrange
    key_id = uuid4()
    created_at = datetime.utcnow()
    expires_at = datetime.utcnow() + timedelta(days=30)
    last_used_at = datetime.utcnow() - timedelta(hours=1)

    api_key = APIKey(
        id=key_id,
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description="Test description",
        scopes=["read", "write"],
        rate_limit_per_hour=5000,
        is_active=True,
        last_used_at=last_used_at,
        expires_at=expires_at,
        created_at=created_at,
    )

    mock_repo = Mock()
    mock_repo.find_by_user.return_value = [api_key]
    use_case = ListAPIKeysUseCase(mock_repo)

    # Act
    result = use_case.execute(user_id=1)

    # Assert
    assert len(result) == 1
    dto = result[0]
    assert dto.id == key_id, "L'ID devrait correspondre"
    assert dto.key_prefix == "hbc_test", "Le key_prefix devrait correspondre"
    assert dto.nom == "Test Key", "Le nom devrait correspondre"
    assert dto.description == "Test description", "La description devrait correspondre"
    assert dto.scopes == ["read", "write"], "Les scopes devraient correspondre"
    assert dto.rate_limit_per_hour == 5000, "Le rate_limit devrait correspondre"
    assert dto.is_active is True, "is_active devrait correspondre"
    assert dto.last_used_at == last_used_at, "last_used_at devrait correspondre"
    assert dto.expires_at == expires_at, "expires_at devrait correspondre"
    assert dto.created_at == created_at, "created_at devrait correspondre"


def test_list_api_keys_dto_does_not_contain_secret():
    """Vérifie que le DTO ne contient jamais le secret ou le hash."""
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

    mock_repo = Mock()
    mock_repo.find_by_user.return_value = [api_key]
    use_case = ListAPIKeysUseCase(mock_repo)

    # Act
    result = use_case.execute(user_id=1)

    # Assert
    dto = result[0]
    # Vérifier que le DTO n'a pas d'attribut 'key_hash' ou 'api_key'
    assert not hasattr(dto, 'key_hash'), "Le DTO ne devrait pas contenir key_hash"
    assert not hasattr(dto, 'api_key'), "Le DTO ne devrait pas contenir le secret"
    assert not hasattr(dto, 'secret'), "Le DTO ne devrait pas contenir le secret"


def test_list_api_keys_with_null_description():
    """Vérifie que les clés sans description sont correctement gérées."""
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

    mock_repo = Mock()
    mock_repo.find_by_user.return_value = [api_key]
    use_case = ListAPIKeysUseCase(mock_repo)

    # Act
    result = use_case.execute(user_id=1)

    # Assert
    dto = result[0]
    assert dto.description is None, "La description devrait être None"


def test_list_api_keys_with_null_expiration():
    """Vérifie que les clés sans expiration sont correctement gérées."""
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

    mock_repo = Mock()
    mock_repo.find_by_user.return_value = [api_key]
    use_case = ListAPIKeysUseCase(mock_repo)

    # Act
    result = use_case.execute(user_id=1)

    # Assert
    dto = result[0]
    assert dto.expires_at is None, "expires_at devrait être None"


def test_list_api_keys_with_null_last_used_at():
    """Vérifie que les clés jamais utilisées sont correctement gérées."""
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
        created_at=datetime.utcnow(),
        expires_at=None,
    )

    mock_repo = Mock()
    mock_repo.find_by_user.return_value = [api_key]
    use_case = ListAPIKeysUseCase(mock_repo)

    # Act
    result = use_case.execute(user_id=1)

    # Assert
    dto = result[0]
    assert dto.last_used_at is None, "last_used_at devrait être None pour une clé jamais utilisée"


def test_list_api_keys_preserves_order():
    """Vérifie que l'ordre des clés est préservé."""
    # Arrange
    keys = [
        APIKey(
            id=uuid4(),
            key_hash=f"{chr(97+i)}" * 64,
            key_prefix=f"hbc_{chr(97+i)}{chr(97+i)}{chr(97+i)}{i}",
            user_id=1,
            nom=f"Key {i}",
            description=None,
            scopes=["read"],
            rate_limit_per_hour=1000,
            is_active=True,
            last_used_at=None,
            expires_at=None,
            created_at=datetime.utcnow(),
        )
        for i in range(5)
    ]

    mock_repo = Mock()
    mock_repo.find_by_user.return_value = keys
    use_case = ListAPIKeysUseCase(mock_repo)

    # Act
    result = use_case.execute(user_id=1)

    # Assert
    assert len(result) == 5, "Devrait retourner 5 clés"
    for i, dto in enumerate(result):
        assert dto.nom == f"Key {i}", f"L'ordre devrait être préservé (index {i})"


def test_list_api_keys_for_different_users():
    """Vérifie que seules les clés du bon utilisateur sont retournées."""
    # Arrange
    mock_repo = Mock()
    mock_repo.find_by_user.return_value = []
    use_case = ListAPIKeysUseCase(mock_repo)

    # Act
    result = use_case.execute(user_id=42)

    # Assert
    mock_repo.find_by_user.assert_called_once_with(user_id=42, include_revoked=False)


def test_list_api_keys_with_various_scopes():
    """Vérifie que différents scopes sont correctement retournés."""
    # Arrange
    keys = [
        APIKey(
            id=uuid4(),
            key_hash="a" * 64,
            key_prefix="hbc_aaa1",
            user_id=1,
            nom="Read Only",
            description=None,
            scopes=["read"],
            rate_limit_per_hour=1000,
            is_active=True,
            last_used_at=None,
            expires_at=None,
            created_at=datetime.utcnow(),
        ),
        APIKey(
            id=uuid4(),
            key_hash="b" * 64,
            key_prefix="hbc_bbb2",
            user_id=1,
            nom="Read Write",
            description=None,
            scopes=["read", "write"],
            rate_limit_per_hour=1000,
            is_active=True,
            last_used_at=None,
            expires_at=None,
            created_at=datetime.utcnow(),
        ),
        APIKey(
            id=uuid4(),
            key_hash="c" * 64,
            key_prefix="hbc_ccc3",
            user_id=1,
            nom="Admin",
            description=None,
            scopes=["admin"],
            rate_limit_per_hour=1000,
            is_active=True,
            last_used_at=None,
            expires_at=None,
            created_at=datetime.utcnow(),
        ),
    ]

    mock_repo = Mock()
    mock_repo.find_by_user.return_value = keys
    use_case = ListAPIKeysUseCase(mock_repo)

    # Act
    result = use_case.execute(user_id=1)

    # Assert
    assert len(result) == 3
    assert result[0].scopes == ["read"]
    assert result[1].scopes == ["read", "write"]
    assert result[2].scopes == ["admin"]
