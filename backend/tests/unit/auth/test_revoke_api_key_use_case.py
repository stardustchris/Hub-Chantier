"""Tests unitaires pour RevokeAPIKeyUseCase."""

from unittest.mock import Mock, call
from datetime import datetime
from uuid import uuid4
import pytest

from modules.auth.application.use_cases.revoke_api_key import (
    RevokeAPIKeyUseCase,
    APIKeyNotFoundError,
    UnauthorizedRevokeError,
)
from modules.auth.application.dtos.api_key_dtos import RevokeAPIKeyDTO
from modules.auth.domain.entities.api_key import APIKey


def test_revoke_api_key_success():
    """Vérifie la révocation réussie d'une clé API."""
    # Arrange
    key_id = uuid4()
    api_key = APIKey(
        id=key_id,
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
    mock_repo.find_by_id.return_value = api_key
    use_case = RevokeAPIKeyUseCase(mock_repo)
    dto = RevokeAPIKeyDTO(api_key_id=key_id, user_id=1)

    # Act
    use_case.execute(dto)

    # Assert
    mock_repo.find_by_id.assert_called_once_with(key_id)
    mock_repo.save.assert_called_once()
    saved_key = mock_repo.save.call_args[0][0]
    assert saved_key.is_active is False, "La clé devrait être révoquée (is_active=False)"


def test_revoke_api_key_raises_not_found_error():
    """Vérifie qu'une APIKeyNotFoundError est levée si la clé n'existe pas."""
    # Arrange
    key_id = uuid4()
    mock_repo = Mock()
    mock_repo.find_by_id.return_value = None  # Clé non trouvée
    use_case = RevokeAPIKeyUseCase(mock_repo)
    dto = RevokeAPIKeyDTO(api_key_id=key_id, user_id=1)

    # Act & Assert
    with pytest.raises(APIKeyNotFoundError) as exc_info:
        use_case.execute(dto)

    assert str(key_id) in str(exc_info.value), "Le message devrait contenir l'ID de la clé"
    mock_repo.find_by_id.assert_called_once_with(key_id)
    mock_repo.save.assert_not_called()


def test_revoke_api_key_raises_unauthorized_error():
    """Vérifie qu'une UnauthorizedRevokeError est levée si l'utilisateur n'est pas propriétaire."""
    # Arrange
    key_id = uuid4()
    api_key = APIKey(
        id=key_id,
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=10,  # Propriétaire: user 10
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
    mock_repo.find_by_id.return_value = api_key
    use_case = RevokeAPIKeyUseCase(mock_repo)
    dto = RevokeAPIKeyDTO(api_key_id=key_id, user_id=42)  # Utilisateur différent

    # Act & Assert
    with pytest.raises(UnauthorizedRevokeError) as exc_info:
        use_case.execute(dto)

    assert "42" in str(exc_info.value), "Le message devrait contenir l'ID utilisateur"
    assert str(key_id) in str(exc_info.value), "Le message devrait contenir l'ID de la clé"
    mock_repo.find_by_id.assert_called_once_with(key_id)
    mock_repo.save.assert_not_called()


def test_revoke_api_key_calls_entity_revoke_method():
    """Vérifie que la méthode revoke() de l'entity est appelée."""
    # Arrange
    key_id = uuid4()
    api_key = APIKey(
        id=key_id,
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

    # Spy sur la méthode revoke()
    original_revoke = api_key.revoke
    revoke_called = False

    def revoke_spy():
        nonlocal revoke_called
        revoke_called = True
        original_revoke()

    api_key.revoke = revoke_spy

    mock_repo = Mock()
    mock_repo.find_by_id.return_value = api_key
    use_case = RevokeAPIKeyUseCase(mock_repo)
    dto = RevokeAPIKeyDTO(api_key_id=key_id, user_id=1)

    # Act
    use_case.execute(dto)

    # Assert
    assert revoke_called is True, "La méthode revoke() de l'entity devrait être appelée"
    assert api_key.is_active is False, "is_active devrait être False après revoke()"


def test_revoke_api_key_saves_revoked_key():
    """Vérifie que la clé révoquée est bien sauvegardée."""
    # Arrange
    key_id = uuid4()
    api_key = APIKey(
        id=key_id,
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
    mock_repo.find_by_id.return_value = api_key
    use_case = RevokeAPIKeyUseCase(mock_repo)
    dto = RevokeAPIKeyDTO(api_key_id=key_id, user_id=1)

    # Act
    use_case.execute(dto)

    # Assert
    mock_repo.save.assert_called_once()
    saved_key = mock_repo.save.call_args[0][0]
    assert saved_key == api_key, "La clé sauvegardée devrait être la même entity"
    assert saved_key.is_active is False, "La clé sauvegardée devrait être révoquée"


def test_revoke_api_key_does_not_modify_other_attributes():
    """Vérifie que seul is_active est modifié lors de la révocation."""
    # Arrange
    key_id = uuid4()
    created_at = datetime.utcnow()
    api_key = APIKey(
        id=key_id,
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description="Description",
        scopes=["read", "write"],
        rate_limit_per_hour=5000,
        is_active=True,
        last_used_at=None,
        expires_at=None,
        created_at=created_at,
    )

    mock_repo = Mock()
    mock_repo.find_by_id.return_value = api_key
    use_case = RevokeAPIKeyUseCase(mock_repo)
    dto = RevokeAPIKeyDTO(api_key_id=key_id, user_id=1)

    # Act
    use_case.execute(dto)

    # Assert
    saved_key = mock_repo.save.call_args[0][0]
    assert saved_key.id == key_id, "L'ID ne devrait pas changer"
    assert saved_key.key_hash == "a" * 64, "Le key_hash ne devrait pas changer"
    assert saved_key.key_prefix == "hbc_test", "Le key_prefix ne devrait pas changer"
    assert saved_key.user_id == 1, "Le user_id ne devrait pas changer"
    assert saved_key.nom == "Test Key", "Le nom ne devrait pas changer"
    assert saved_key.description == "Description", "La description ne devrait pas changer"
    assert saved_key.scopes == ["read", "write"], "Les scopes ne devraient pas changer"
    assert saved_key.rate_limit_per_hour == 5000, "Le rate_limit ne devrait pas changer"
    assert saved_key.last_used_at is None, "last_used_at ne devrait pas changer"
    assert saved_key.expires_at is None, "expires_at ne devrait pas changer"
    assert saved_key.created_at == created_at, "created_at ne devrait pas changer"


def test_revoke_already_revoked_key():
    """Vérifie que révoquer une clé déjà révoquée fonctionne sans erreur."""
    # Arrange
    key_id = uuid4()
    api_key = APIKey(
        id=key_id,
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description=None,
        scopes=["read"],
        rate_limit_per_hour=1000,
        is_active=False,  # Déjà révoquée
        last_used_at=None,
        expires_at=None,
        created_at=datetime.utcnow(),
    )

    mock_repo = Mock()
    mock_repo.find_by_id.return_value = api_key
    use_case = RevokeAPIKeyUseCase(mock_repo)
    dto = RevokeAPIKeyDTO(api_key_id=key_id, user_id=1)

    # Act - ne devrait pas lever d'exception
    use_case.execute(dto)

    # Assert
    saved_key = mock_repo.save.call_args[0][0]
    assert saved_key.is_active is False, "La clé devrait rester révoquée"


def test_revoke_api_key_with_correct_user_id():
    """Vérifie que la révocation fonctionne uniquement avec le bon user_id."""
    # Arrange
    key_id = uuid4()
    api_key = APIKey(
        id=key_id,
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=123,
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
    mock_repo.find_by_id.return_value = api_key
    use_case = RevokeAPIKeyUseCase(mock_repo)
    dto = RevokeAPIKeyDTO(api_key_id=key_id, user_id=123)  # Même user_id

    # Act
    use_case.execute(dto)

    # Assert
    mock_repo.save.assert_called_once()


def test_revoke_api_key_repository_calls():
    """Vérifie l'ordre et le nombre d'appels au repository."""
    # Arrange
    key_id = uuid4()
    api_key = APIKey(
        id=key_id,
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
    mock_repo.find_by_id.return_value = api_key
    use_case = RevokeAPIKeyUseCase(mock_repo)
    dto = RevokeAPIKeyDTO(api_key_id=key_id, user_id=1)

    # Act
    use_case.execute(dto)

    # Assert
    assert mock_repo.find_by_id.call_count == 1, "find_by_id devrait être appelé une fois"
    assert mock_repo.save.call_count == 1, "save devrait être appelé une fois"
    # Vérifier l'ordre des appels
    expected_calls = [
        call.find_by_id(key_id),
        call.save(api_key),
    ]
    assert mock_repo.method_calls == expected_calls, "L'ordre des appels devrait être: find_by_id puis save"


def test_revoke_api_key_error_messages():
    """Vérifie que les messages d'erreur sont informatifs."""
    # Arrange - Not Found
    key_id = uuid4()
    mock_repo = Mock()
    mock_repo.find_by_id.return_value = None
    use_case = RevokeAPIKeyUseCase(mock_repo)
    dto = RevokeAPIKeyDTO(api_key_id=key_id, user_id=1)

    # Act & Assert
    with pytest.raises(APIKeyNotFoundError) as exc_info:
        use_case.execute(dto)

    error_message = str(exc_info.value)
    assert "non trouvée" in error_message.lower() or "not found" in error_message.lower()


def test_revoke_api_key_unauthorized_error_message():
    """Vérifie le message d'erreur pour un accès non autorisé."""
    # Arrange
    key_id = uuid4()
    api_key = APIKey(
        id=key_id,
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=10,
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
    mock_repo.find_by_id.return_value = api_key
    use_case = RevokeAPIKeyUseCase(mock_repo)
    dto = RevokeAPIKeyDTO(api_key_id=key_id, user_id=42)

    # Act & Assert
    with pytest.raises(UnauthorizedRevokeError) as exc_info:
        use_case.execute(dto)

    error_message = str(exc_info.value)
    assert "propriétaire" in error_message.lower() or "owner" in error_message.lower()


def test_revoke_api_key_returns_none():
    """Vérifie que execute() ne retourne rien (None)."""
    # Arrange
    key_id = uuid4()
    api_key = APIKey(
        id=key_id,
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
    mock_repo.find_by_id.return_value = api_key
    use_case = RevokeAPIKeyUseCase(mock_repo)
    dto = RevokeAPIKeyDTO(api_key_id=key_id, user_id=1)

    # Act
    result = use_case.execute(dto)

    # Assert
    assert result is None, "execute() devrait retourner None"
