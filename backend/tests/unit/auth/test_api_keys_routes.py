"""Tests unitaires pour les routes FastAPI des clés API."""

from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from modules.auth.infrastructure.web.api_keys_routes import router
from modules.auth.application.dtos.api_key_dtos import (
    APIKeyCreatedDTO,
    APIKeyInfoDTO,
)
from modules.auth.application.use_cases.revoke_api_key import (
    APIKeyNotFoundError,
    UnauthorizedRevokeError,
)
from modules.auth.infrastructure.persistence.user_model import UserModel


# Mock FastAPI app pour tester les routes
@pytest.fixture
def mock_current_user():
    """Fixture pour mocker l'utilisateur authentifié."""
    user = Mock(spec=UserModel)
    user.id = 1
    user.email = "test@example.com"
    return user


@pytest.fixture
def mock_db():
    """Fixture pour mocker la session DB."""
    return Mock()


@pytest.mark.asyncio
async def test_create_api_key_returns_secret_once():
    """Vérifie que le secret est retourné dans la réponse."""
    # Arrange
    mock_use_case = Mock()
    mock_use_case.execute.return_value = APIKeyCreatedDTO(
        api_key="hbc_test_secret_1234567890123456789012345678901234567890",
        key_id=uuid4(),
        key_prefix="hbc_test",
        nom="Test Key",
        created_at=datetime.utcnow(),
        expires_at=None,
    )

    with patch(
        "modules.auth.infrastructure.web.api_keys_routes.CreateAPIKeyUseCase"
    ) as MockUseCase:
        MockUseCase.return_value = mock_use_case

        # Import après le patch pour capturer le mock
        from modules.auth.infrastructure.web.api_keys_routes import create_api_key

        # Act
        result = await create_api_key(
            request=Mock(nom="Test Key", description=None, scopes=["read"], expires_days=90),
            current_user=Mock(id=1),
            db=Mock(),
        )

        # Assert
        assert result.api_key.startswith("hbc_"), "Le secret doit être retourné avec le préfixe hbc_"
        assert len(result.api_key) > 40, "Le secret doit être long"


@pytest.mark.asyncio
async def test_create_api_key_requires_authentication():
    """Vérifie que l'endpoint nécessite une authentification."""
    # Cet aspect est géré par FastAPI Depends(get_current_user)
    # Le test vérifie que le paramètre current_user est requis
    from modules.auth.infrastructure.web.api_keys_routes import create_api_key
    import inspect

    sig = inspect.signature(create_api_key)
    assert "current_user" in sig.parameters, "current_user devrait être un paramètre"
    # Vérifier que c'est une dépendance
    param = sig.parameters["current_user"]
    assert param.default != inspect.Parameter.empty, "current_user devrait avoir un default (Depends)"


@pytest.mark.asyncio
async def test_create_api_key_with_invalid_scopes_returns_400():
    """Vérifie qu'un scope invalide retourne une erreur 400."""
    # Arrange
    mock_use_case = Mock()
    mock_use_case.execute.side_effect = ValueError("Scope invalide: invalid_scope")

    with patch(
        "modules.auth.infrastructure.web.api_keys_routes.CreateAPIKeyUseCase"
    ) as MockUseCase:
        MockUseCase.return_value = mock_use_case

        from modules.auth.infrastructure.web.api_keys_routes import create_api_key

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await create_api_key(
                request=Mock(nom="Test", description=None, scopes=["invalid_scope"], expires_days=90),
                current_user=Mock(id=1),
                db=Mock(),
            )

        assert exc_info.value.status_code == 400, "Devrait retourner 400 pour scope invalide"
        assert "Scope invalide" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_create_api_key_handles_general_exception():
    """Vérifie la gestion des exceptions générales."""
    # Arrange
    mock_use_case = Mock()
    mock_use_case.execute.side_effect = Exception("Erreur DB")

    with patch(
        "modules.auth.infrastructure.web.api_keys_routes.CreateAPIKeyUseCase"
    ) as MockUseCase:
        MockUseCase.return_value = mock_use_case

        from modules.auth.infrastructure.web.api_keys_routes import create_api_key

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await create_api_key(
                request=Mock(nom="Test", description=None, scopes=["read"], expires_days=90),
                current_user=Mock(id=1),
                db=Mock(),
            )

        assert exc_info.value.status_code == 500, "Devrait retourner 500 pour erreur générale"


@pytest.mark.asyncio
async def test_list_api_keys_returns_user_keys_only():
    """Vérifie que seules les clés de l'utilisateur authentifié sont retournées."""
    # Arrange
    key_id = uuid4()
    mock_use_case = Mock()
    mock_use_case.execute.return_value = [
        APIKeyInfoDTO(
            id=key_id,
            key_prefix="hbc_test",
            nom="Test Key",
            description=None,
            scopes=["read"],
            rate_limit_per_hour=1000,
            is_active=True,
            last_used_at=None,
            expires_at=None,
            created_at=datetime.utcnow(),
        )
    ]

    with patch(
        "modules.auth.infrastructure.web.api_keys_routes.ListAPIKeysUseCase"
    ) as MockUseCase:
        MockUseCase.return_value = mock_use_case

        from modules.auth.infrastructure.web.api_keys_routes import list_api_keys

        # Act
        result = await list_api_keys(
            include_revoked=False,
            current_user=Mock(id=1),
            db=Mock(),
        )

        # Assert
        assert len(result) == 1, "Devrait retourner 1 clé"
        assert result[0].key_prefix == "hbc_test"
        # Vérifier que le use case a été appelé avec le bon user_id
        mock_use_case.execute.assert_called_once_with(user_id=1, include_revoked=False)


@pytest.mark.asyncio
async def test_list_api_keys_requires_authentication():
    """Vérifie que l'endpoint nécessite une authentification."""
    from modules.auth.infrastructure.web.api_keys_routes import list_api_keys
    import inspect

    sig = inspect.signature(list_api_keys)
    assert "current_user" in sig.parameters, "current_user devrait être un paramètre"


@pytest.mark.asyncio
async def test_list_api_keys_handles_exception():
    """Vérifie la gestion des exceptions lors du listing."""
    # Arrange
    mock_use_case = Mock()
    mock_use_case.execute.side_effect = Exception("Erreur DB")

    with patch(
        "modules.auth.infrastructure.web.api_keys_routes.ListAPIKeysUseCase"
    ) as MockUseCase:
        MockUseCase.return_value = mock_use_case

        from modules.auth.infrastructure.web.api_keys_routes import list_api_keys

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await list_api_keys(
                include_revoked=False,
                current_user=Mock(id=1),
                db=Mock(),
            )

        assert exc_info.value.status_code == 500, "Devrait retourner 500 pour erreur"


@pytest.mark.asyncio
async def test_list_api_keys_with_include_revoked():
    """Vérifie que le paramètre include_revoked est passé au use case."""
    # Arrange
    mock_use_case = Mock()
    mock_use_case.execute.return_value = []

    with patch(
        "modules.auth.infrastructure.web.api_keys_routes.ListAPIKeysUseCase"
    ) as MockUseCase:
        MockUseCase.return_value = mock_use_case

        from modules.auth.infrastructure.web.api_keys_routes import list_api_keys

        # Act
        await list_api_keys(
            include_revoked=True,
            current_user=Mock(id=1),
            db=Mock(),
        )

        # Assert
        mock_use_case.execute.assert_called_once_with(user_id=1, include_revoked=True)


@pytest.mark.asyncio
async def test_revoke_api_key_success_returns_204():
    """Vérifie qu'une révocation réussie retourne None (204 No Content)."""
    # Arrange
    key_id = uuid4()
    mock_use_case = Mock()
    mock_use_case.execute.return_value = None

    with patch(
        "modules.auth.infrastructure.web.api_keys_routes.RevokeAPIKeyUseCase"
    ) as MockUseCase:
        MockUseCase.return_value = mock_use_case

        from modules.auth.infrastructure.web.api_keys_routes import revoke_api_key

        # Act
        result = await revoke_api_key(
            key_id=key_id,
            current_user=Mock(id=1),
            db=Mock(),
        )

        # Assert
        assert result is None, "Devrait retourner None pour 204 No Content"
        mock_use_case.execute.assert_called_once()


@pytest.mark.asyncio
async def test_revoke_api_key_not_found_returns_404():
    """Vérifie qu'une clé non trouvée retourne 404."""
    # Arrange
    key_id = uuid4()
    mock_use_case = Mock()
    mock_use_case.execute.side_effect = APIKeyNotFoundError("Not found")

    with patch(
        "modules.auth.infrastructure.web.api_keys_routes.RevokeAPIKeyUseCase"
    ) as MockUseCase:
        MockUseCase.return_value = mock_use_case

        from modules.auth.infrastructure.web.api_keys_routes import revoke_api_key

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await revoke_api_key(
                key_id=key_id,
                current_user=Mock(id=1),
                db=Mock(),
            )

        assert exc_info.value.status_code == 404, "Devrait retourner 404"
        assert "non trouvée" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_revoke_api_key_unauthorized_returns_403():
    """Vérifie qu'un accès non autorisé retourne 403."""
    # Arrange
    key_id = uuid4()
    mock_use_case = Mock()
    mock_use_case.execute.side_effect = UnauthorizedRevokeError("Not owner")

    with patch(
        "modules.auth.infrastructure.web.api_keys_routes.RevokeAPIKeyUseCase"
    ) as MockUseCase:
        MockUseCase.return_value = mock_use_case

        from modules.auth.infrastructure.web.api_keys_routes import revoke_api_key

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await revoke_api_key(
                key_id=key_id,
                current_user=Mock(id=1),
                db=Mock(),
            )

        assert exc_info.value.status_code == 403, "Devrait retourner 403"
        assert "propriétaire" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_revoke_api_key_handles_general_exception():
    """Vérifie la gestion des exceptions générales lors de la révocation."""
    # Arrange
    key_id = uuid4()
    mock_use_case = Mock()
    mock_use_case.execute.side_effect = Exception("Erreur DB")

    with patch(
        "modules.auth.infrastructure.web.api_keys_routes.RevokeAPIKeyUseCase"
    ) as MockUseCase:
        MockUseCase.return_value = mock_use_case

        from modules.auth.infrastructure.web.api_keys_routes import revoke_api_key

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await revoke_api_key(
                key_id=key_id,
                current_user=Mock(id=1),
                db=Mock(),
            )

        assert exc_info.value.status_code == 500, "Devrait retourner 500"


@pytest.mark.asyncio
async def test_create_api_key_dto_mapping():
    """Vérifie que le DTO est correctement créé à partir de la requête."""
    # Arrange
    mock_use_case = Mock()
    mock_use_case.execute.return_value = APIKeyCreatedDTO(
        api_key="hbc_test",
        key_id=uuid4(),
        key_prefix="hbc_test",
        nom="Test",
        created_at=datetime.utcnow(),
        expires_at=None,
    )

    with patch(
        "modules.auth.infrastructure.web.api_keys_routes.CreateAPIKeyUseCase"
    ) as MockUseCase:
        MockUseCase.return_value = mock_use_case

        from modules.auth.infrastructure.web.api_keys_routes import create_api_key

        request = Mock(
            nom="My Key",
            description="My Description",
            scopes=["read", "write"],
            expires_days=30,
        )

        # Act
        await create_api_key(
            request=request,
            current_user=Mock(id=42),
            db=Mock(),
        )

        # Assert
        # Vérifier que execute a été appelé avec les bonnes valeurs
        call_args = mock_use_case.execute.call_args[0][0]
        assert call_args.user_id == 42
        assert call_args.nom == "My Key"
        assert call_args.description == "My Description"
        assert call_args.scopes == ["read", "write"]
        assert call_args.expires_days == 30


@pytest.mark.asyncio
async def test_list_api_keys_response_format():
    """Vérifie le format de la réponse de list_api_keys."""
    # Arrange
    key_id = uuid4()
    created_at = datetime.utcnow()
    expires_at = datetime.utcnow() + timedelta(days=30)
    last_used_at = datetime.utcnow() - timedelta(hours=1)

    mock_use_case = Mock()
    mock_use_case.execute.return_value = [
        APIKeyInfoDTO(
            id=key_id,
            key_prefix="hbc_test",
            nom="Test Key",
            description="Description",
            scopes=["read", "write"],
            rate_limit_per_hour=5000,
            is_active=True,
            last_used_at=last_used_at,
            expires_at=expires_at,
            created_at=created_at,
        )
    ]

    with patch(
        "modules.auth.infrastructure.web.api_keys_routes.ListAPIKeysUseCase"
    ) as MockUseCase:
        MockUseCase.return_value = mock_use_case

        from modules.auth.infrastructure.web.api_keys_routes import list_api_keys

        # Act
        result = await list_api_keys(
            include_revoked=False,
            current_user=Mock(id=1),
            db=Mock(),
        )

        # Assert
        assert len(result) == 1
        response = result[0]
        assert response.id == str(key_id)
        assert response.key_prefix == "hbc_test"
        assert response.nom == "Test Key"
        assert response.description == "Description"
        assert response.scopes == ["read", "write"]
        assert response.rate_limit_per_hour == 5000
        assert response.is_active is True
        assert response.last_used_at == last_used_at.isoformat()
        assert response.expires_at == expires_at.isoformat()
        assert response.created_at == created_at.isoformat()


@pytest.mark.asyncio
async def test_create_api_key_response_format():
    """Vérifie le format de la réponse de create_api_key."""
    # Arrange
    key_id = uuid4()
    created_at = datetime.utcnow()
    expires_at = datetime.utcnow() + timedelta(days=90)

    mock_use_case = Mock()
    mock_use_case.execute.return_value = APIKeyCreatedDTO(
        api_key="hbc_test_secret_123456789012345678901234567890",
        key_id=key_id,
        key_prefix="hbc_test",
        nom="Test Key",
        created_at=created_at,
        expires_at=expires_at,
    )

    with patch(
        "modules.auth.infrastructure.web.api_keys_routes.CreateAPIKeyUseCase"
    ) as MockUseCase:
        MockUseCase.return_value = mock_use_case

        from modules.auth.infrastructure.web.api_keys_routes import create_api_key

        # Act
        result = await create_api_key(
            request=Mock(nom="Test", description=None, scopes=["read"], expires_days=90),
            current_user=Mock(id=1),
            db=Mock(),
        )

        # Assert
        assert result.api_key == "hbc_test_secret_123456789012345678901234567890"
        assert result.key_id == str(key_id)
        assert result.key_prefix == "hbc_test"
        assert result.nom == "Test Key"
        assert result.created_at == created_at.isoformat()
        assert result.expires_at == expires_at.isoformat()


@pytest.mark.asyncio
async def test_list_api_keys_handles_null_optional_fields():
    """Vérifie la gestion des champs optionnels null dans la réponse."""
    # Arrange
    key_id = uuid4()
    created_at = datetime.utcnow()

    mock_use_case = Mock()
    mock_use_case.execute.return_value = [
        APIKeyInfoDTO(
            id=key_id,
            key_prefix="hbc_test",
            nom="Test Key",
            description=None,  # Null
            scopes=["read"],
            rate_limit_per_hour=1000,
            is_active=True,
            last_used_at=None,  # Null
            expires_at=None,  # Null
            created_at=created_at,
        )
    ]

    with patch(
        "modules.auth.infrastructure.web.api_keys_routes.ListAPIKeysUseCase"
    ) as MockUseCase:
        MockUseCase.return_value = mock_use_case

        from modules.auth.infrastructure.web.api_keys_routes import list_api_keys

        # Act
        result = await list_api_keys(
            include_revoked=False,
            current_user=Mock(id=1),
            db=Mock(),
        )

        # Assert
        response = result[0]
        assert response.description is None
        assert response.last_used_at is None
        assert response.expires_at is None


@pytest.mark.asyncio
async def test_revoke_api_key_passes_correct_dto():
    """Vérifie que le DTO de révocation est correctement créé."""
    # Arrange
    key_id = uuid4()
    mock_use_case = Mock()
    mock_use_case.execute.return_value = None

    with patch(
        "modules.auth.infrastructure.web.api_keys_routes.RevokeAPIKeyUseCase"
    ) as MockUseCase:
        MockUseCase.return_value = mock_use_case

        from modules.auth.infrastructure.web.api_keys_routes import revoke_api_key

        # Act
        await revoke_api_key(
            key_id=key_id,
            current_user=Mock(id=42),
            db=Mock(),
        )

        # Assert
        call_args = mock_use_case.execute.call_args[0][0]
        assert call_args.api_key_id == key_id
        assert call_args.user_id == 42
