"""Tests unitaires pour CreateAPIKeyUseCase."""

from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from uuid import uuid4
import pytest

from modules.auth.application.use_cases.create_api_key import CreateAPIKeyUseCase
from modules.auth.application.dtos.api_key_dtos import CreateAPIKeyDTO
from modules.auth.domain.entities.api_key import APIKey


def test_create_api_key_generates_secure_secret_with_hbc_prefix():
    """Le secret doit commencer par 'hbc_' et avoir >40 caractères."""
    # Arrange
    mock_repo = Mock()
    mock_repo.save.return_value = APIKey(
        id=uuid4(),
        key_hash="a" * 64,
        key_prefix="hbc_xxxx",
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
    use_case = CreateAPIKeyUseCase(mock_repo)
    dto = CreateAPIKeyDTO(user_id=1, nom="Test Key")

    # Act
    result = use_case.execute(dto)

    # Assert
    assert result.api_key.startswith('hbc_'), "Le secret doit commencer par 'hbc_'"
    assert len(result.api_key) > 40, "Le secret doit avoir plus de 40 caractères pour être sécurisé"
    mock_repo.save.assert_called_once()


def test_create_api_key_hash_never_stored_plain():
    """Le secret ne doit jamais être stocké en clair en DB."""
    # Arrange
    mock_repo = Mock()
    use_case = CreateAPIKeyUseCase(mock_repo)
    dto = CreateAPIKeyDTO(user_id=1, nom="Test")

    # Act
    result = use_case.execute(dto)

    # Assert
    # Vérifier que save() n'a pas reçu le secret en clair
    saved_entity = mock_repo.save.call_args[0][0]
    assert saved_entity.key_hash != result.api_key, "Le hash ne doit pas être égal au secret"
    assert len(saved_entity.key_hash) == 64, "SHA256 hex devrait avoir 64 caractères"
    # Vérifier que c'est bien du hexadécimal
    try:
        int(saved_entity.key_hash, 16)
        is_hex = True
    except ValueError:
        is_hex = False
    assert is_hex, "Le hash devrait être en hexadécimal"


def test_create_api_key_with_expiration():
    """Vérifie la création d'une clé avec date d'expiration."""
    # Arrange
    mock_repo = Mock()
    use_case = CreateAPIKeyUseCase(mock_repo)
    dto = CreateAPIKeyDTO(user_id=1, nom="Test", expires_days=30)

    # Act
    before = datetime.utcnow()
    result = use_case.execute(dto)
    after = datetime.utcnow()

    # Assert
    saved_entity = mock_repo.save.call_args[0][0]
    assert saved_entity.expires_at is not None, "expires_at devrait être défini"
    # Vérifier que c'est environ 30 jours dans le futur
    expected_expiration = before + timedelta(days=30)
    assert saved_entity.expires_at >= expected_expiration - timedelta(seconds=5)
    assert saved_entity.expires_at <= after + timedelta(days=30) + timedelta(seconds=5)


def test_create_api_key_without_expiration():
    """Vérifie la création d'une clé sans date d'expiration."""
    # Arrange
    mock_repo = Mock()
    use_case = CreateAPIKeyUseCase(mock_repo)
    dto = CreateAPIKeyDTO(user_id=1, nom="Test", expires_days=None)

    # Act
    result = use_case.execute(dto)

    # Assert
    saved_entity = mock_repo.save.call_args[0][0]
    assert saved_entity.expires_at is None, "expires_at devrait être None"


def test_create_api_key_with_custom_scopes():
    """Vérifie la création d'une clé avec des scopes personnalisés."""
    # Arrange
    mock_repo = Mock()
    use_case = CreateAPIKeyUseCase(mock_repo)
    custom_scopes = ["read", "write", "chantiers:read"]
    dto = CreateAPIKeyDTO(user_id=1, nom="Test", scopes=custom_scopes)

    # Act
    result = use_case.execute(dto)

    # Assert
    saved_entity = mock_repo.save.call_args[0][0]
    assert saved_entity.scopes == custom_scopes, "Les scopes personnalisés devraient être sauvegardés"


def test_create_api_key_with_default_scopes():
    """Vérifie que les scopes par défaut sont ['read'] si non spécifiés."""
    # Arrange
    mock_repo = Mock()
    use_case = CreateAPIKeyUseCase(mock_repo)
    dto = CreateAPIKeyDTO(user_id=1, nom="Test", scopes=None)

    # Act
    result = use_case.execute(dto)

    # Assert
    saved_entity = mock_repo.save.call_args[0][0]
    assert saved_entity.scopes == ["read"], "Les scopes par défaut devraient être ['read']"


def test_create_api_key_validates_scopes():
    """Vérifie que les scopes sont validés."""
    # Arrange
    mock_repo = Mock()
    use_case = CreateAPIKeyUseCase(mock_repo)
    valid_scopes = ["read", "write", "chantiers:read"]
    dto = CreateAPIKeyDTO(user_id=1, nom="Test", scopes=valid_scopes)

    # Act & Assert - ne devrait pas lever d'exception
    try:
        result = use_case.execute(dto)
        validation_passed = True
    except ValueError:
        validation_passed = False

    assert validation_passed, "Les scopes valides ne devraient pas lever d'exception"


def test_create_api_key_raises_value_error_on_invalid_scope():
    """Vérifie qu'une ValueError est levée pour un scope invalide."""
    # Arrange
    mock_repo = Mock()
    use_case = CreateAPIKeyUseCase(mock_repo)
    invalid_scopes = ["read", "invalid_scope_xyz"]
    dto = CreateAPIKeyDTO(user_id=1, nom="Test", scopes=invalid_scopes)

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        use_case.execute(dto)

    assert "Scope invalide" in str(exc_info.value), "Le message d'erreur devrait mentionner 'Scope invalide'"
    assert "invalid_scope_xyz" in str(exc_info.value), "Le message devrait mentionner le scope invalide"


def test_key_prefix_is_first_8_chars():
    """Vérifie que le key_prefix est bien les 8 premiers caractères du secret."""
    # Arrange
    mock_repo = Mock()
    use_case = CreateAPIKeyUseCase(mock_repo)
    dto = CreateAPIKeyDTO(user_id=1, nom="Test")

    # Act
    result = use_case.execute(dto)

    # Assert
    saved_entity = mock_repo.save.call_args[0][0]
    expected_prefix = result.api_key[:8]
    assert saved_entity.key_prefix == expected_prefix, "key_prefix devrait être les 8 premiers caractères"
    assert saved_entity.key_prefix.startswith("hbc_"), "key_prefix devrait commencer par 'hbc_'"


def test_repository_save_called_once():
    """Vérifie que le repository.save() est appelé exactement une fois."""
    # Arrange
    mock_repo = Mock()
    use_case = CreateAPIKeyUseCase(mock_repo)
    dto = CreateAPIKeyDTO(user_id=1, nom="Test")

    # Act
    result = use_case.execute(dto)

    # Assert
    mock_repo.save.assert_called_once()


def test_create_api_key_sets_correct_user_id():
    """Vérifie que le user_id est correctement assigné."""
    # Arrange
    mock_repo = Mock()
    use_case = CreateAPIKeyUseCase(mock_repo)
    dto = CreateAPIKeyDTO(user_id=42, nom="Test")

    # Act
    result = use_case.execute(dto)

    # Assert
    saved_entity = mock_repo.save.call_args[0][0]
    assert saved_entity.user_id == 42, "Le user_id devrait être 42"


def test_create_api_key_sets_is_active_true():
    """Vérifie que la clé est créée active par défaut."""
    # Arrange
    mock_repo = Mock()
    use_case = CreateAPIKeyUseCase(mock_repo)
    dto = CreateAPIKeyDTO(user_id=1, nom="Test")

    # Act
    result = use_case.execute(dto)

    # Assert
    saved_entity = mock_repo.save.call_args[0][0]
    assert saved_entity.is_active is True, "La clé devrait être active à la création"


def test_create_api_key_sets_last_used_at_none():
    """Vérifie que last_used_at est None à la création."""
    # Arrange
    mock_repo = Mock()
    use_case = CreateAPIKeyUseCase(mock_repo)
    dto = CreateAPIKeyDTO(user_id=1, nom="Test")

    # Act
    result = use_case.execute(dto)

    # Assert
    saved_entity = mock_repo.save.call_args[0][0]
    assert saved_entity.last_used_at is None, "last_used_at devrait être None à la création"


def test_create_api_key_sets_created_at():
    """Vérifie que created_at est défini."""
    # Arrange
    mock_repo = Mock()
    use_case = CreateAPIKeyUseCase(mock_repo)
    dto = CreateAPIKeyDTO(user_id=1, nom="Test")

    # Act
    before = datetime.utcnow()
    result = use_case.execute(dto)
    after = datetime.utcnow()

    # Assert
    saved_entity = mock_repo.save.call_args[0][0]
    assert saved_entity.created_at is not None, "created_at devrait être défini"
    assert before <= saved_entity.created_at <= after, "created_at devrait être entre avant/après la création"


def test_create_api_key_with_description():
    """Vérifie que la description est sauvegardée."""
    # Arrange
    mock_repo = Mock()
    use_case = CreateAPIKeyUseCase(mock_repo)
    dto = CreateAPIKeyDTO(user_id=1, nom="Test", description="Ma description")

    # Act
    result = use_case.execute(dto)

    # Assert
    saved_entity = mock_repo.save.call_args[0][0]
    assert saved_entity.description == "Ma description", "La description devrait être sauvegardée"


def test_create_api_key_with_custom_rate_limit():
    """Vérifie que le rate_limit_per_hour personnalisé est appliqué."""
    # Arrange
    mock_repo = Mock()
    use_case = CreateAPIKeyUseCase(mock_repo)
    dto = CreateAPIKeyDTO(user_id=1, nom="Test", rate_limit_per_hour=5000)

    # Act
    result = use_case.execute(dto)

    # Assert
    saved_entity = mock_repo.save.call_args[0][0]
    assert saved_entity.rate_limit_per_hour == 5000, "Le rate_limit personnalisé devrait être appliqué"


def test_create_api_key_returns_correct_dto():
    """Vérifie que le DTO retourné contient les bonnes informations."""
    # Arrange
    mock_id = uuid4()
    mock_created_at = datetime.utcnow()
    mock_expires_at = datetime.utcnow() + timedelta(days=30)

    mock_repo = Mock()
    mock_repo.save.return_value = APIKey(
        id=mock_id,
        key_hash="a" * 64,
        key_prefix="hbc_test",
        user_id=1,
        nom="Test Key",
        description=None,
        scopes=["read"],
        rate_limit_per_hour=1000,
        is_active=True,
        last_used_at=None,
        expires_at=mock_expires_at,
        created_at=mock_created_at,
    )

    use_case = CreateAPIKeyUseCase(mock_repo)
    dto = CreateAPIKeyDTO(user_id=1, nom="Test Key", expires_days=30)

    # Act
    result = use_case.execute(dto)

    # Assert
    assert result.key_id == mock_id, "Le key_id devrait correspondre"
    assert result.key_prefix == "hbc_test", "Le key_prefix devrait correspondre"
    assert result.nom == "Test Key", "Le nom devrait correspondre"
    assert result.created_at == mock_created_at, "created_at devrait correspondre"
    assert result.expires_at == mock_expires_at, "expires_at devrait correspondre"
    assert result.api_key.startswith("hbc_"), "Le secret devrait être retourné"


def test_create_api_key_with_wildcard_scopes():
    """Vérifie la création avec des scopes wildcard."""
    # Arrange
    mock_repo = Mock()
    use_case = CreateAPIKeyUseCase(mock_repo)
    wildcard_scopes = ["chantiers:*", "planning:*"]
    dto = CreateAPIKeyDTO(user_id=1, nom="Test", scopes=wildcard_scopes)

    # Act
    result = use_case.execute(dto)

    # Assert
    saved_entity = mock_repo.save.call_args[0][0]
    assert saved_entity.scopes == wildcard_scopes, "Les scopes wildcard devraient être acceptés"
