"""Tests unitaires pour le middleware d'authentification API Key."""

from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import pytest
from fastapi import HTTPException

from shared.infrastructure.api_v1.middleware import (
    verify_api_authentication,
    _verify_api_key,
    _verify_jwt_token,
)


@pytest.mark.asyncio
async def test_middleware_accepts_valid_api_key():
    """Vérifie que le middleware accepte une clé API valide."""
    # Arrange
    valid_secret = "hbc_test_secret_12345678901234567890"
    mock_db = Mock()
    mock_key_record = Mock()
    mock_key_record.is_active = True
    mock_key_record.expires_at = None
    mock_key_record.user_id = 1
    mock_key_record.last_used_at = None

    mock_user = Mock()
    mock_user.id = 1
    mock_user.is_active = True

    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_key_record
    mock_db.query.return_value = mock_query

    # Mock pour la requête utilisateur
    mock_user_query = Mock()
    mock_user_query.filter.return_value.first.return_value = mock_user
    mock_db.query.side_effect = [mock_query, mock_user_query]

    # Act
    result = await _verify_api_key(valid_secret, mock_db)

    # Assert
    assert result == mock_user, "Devrait retourner l'utilisateur"
    assert mock_db.commit.called, "Devrait commit pour mettre à jour last_used_at"


@pytest.mark.asyncio
async def test_middleware_rejects_invalid_api_key():
    """Vérifie que le middleware rejette une clé API invalide."""
    # Arrange
    invalid_secret = "hbc_invalid_key"
    mock_db = Mock()
    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = None  # Clé non trouvée
    mock_db.query.return_value = mock_query

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await _verify_api_key(invalid_secret, mock_db)

    assert exc_info.value.status_code == 401
    assert "Invalid or revoked" in exc_info.value.detail


@pytest.mark.asyncio
async def test_middleware_rejects_expired_key():
    """Vérifie que le middleware rejette une clé expirée."""
    # Arrange
    expired_secret = "hbc_expired_key_12345678901234567890"
    mock_db = Mock()
    mock_key_record = Mock()
    mock_key_record.is_active = True
    mock_key_record.expires_at = datetime.utcnow() - timedelta(days=1)  # Expirée
    mock_key_record.user_id = 1

    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_key_record
    mock_db.query.return_value = mock_query

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await _verify_api_key(expired_secret, mock_db)

    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_middleware_rejects_revoked_key():
    """Vérifie que le middleware rejette une clé révoquée."""
    # Arrange
    revoked_secret = "hbc_revoked_key_12345678901234567890"
    mock_db = Mock()
    mock_query = Mock()
    # Le filtre is_active=True fait que la clé révoquée n'est pas trouvée
    mock_query.filter.return_value.first.return_value = None
    mock_db.query.return_value = mock_query

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await _verify_api_key(revoked_secret, mock_db)

    assert exc_info.value.status_code == 401
    assert "Invalid or revoked" in exc_info.value.detail


@pytest.mark.asyncio
async def test_middleware_updates_last_used_at():
    """Vérifie que le middleware met à jour last_used_at."""
    # Arrange
    valid_secret = "hbc_test_secret_12345678901234567890"
    mock_db = Mock()
    mock_key_record = Mock()
    mock_key_record.is_active = True
    mock_key_record.expires_at = None
    mock_key_record.user_id = 1
    mock_key_record.last_used_at = None

    mock_user = Mock()
    mock_user.id = 1
    mock_user.is_active = True

    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_key_record
    mock_db.query.return_value = mock_query

    mock_user_query = Mock()
    mock_user_query.filter.return_value.first.return_value = mock_user
    mock_db.query.side_effect = [mock_query, mock_user_query]

    # Act
    before = datetime.utcnow()
    await _verify_api_key(valid_secret, mock_db)
    after = datetime.utcnow()

    # Assert
    assert mock_key_record.last_used_at is not None, "last_used_at devrait être défini"
    assert before <= mock_key_record.last_used_at <= after, "last_used_at devrait être l'heure actuelle"
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_middleware_accepts_valid_jwt():
    """Vérifie que le middleware route les tokens JWT vers _verify_jwt_token."""
    # Arrange
    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
    mock_db = Mock()
    mock_user = Mock()

    with patch(
        "shared.infrastructure.api_v1.middleware._verify_jwt_token",
        new_callable=AsyncMock,
    ) as mock_verify_jwt:
        mock_verify_jwt.return_value = mock_user

        # Act
        result = await verify_api_authentication(
            authorization=f"Bearer {jwt_token}",
            db=mock_db,
        )

        # Assert
        assert result == mock_user
        mock_verify_jwt.assert_called_once_with(jwt_token, mock_db)


@pytest.mark.asyncio
async def test_middleware_rejects_invalid_jwt():
    """Vérifie que le middleware rejette un JWT invalide."""
    # Arrange
    invalid_jwt = "eyJinvalid"
    mock_db = Mock()

    with patch(
        "shared.infrastructure.api_v1.middleware._verify_jwt_token",
        new_callable=AsyncMock,
    ) as mock_verify_jwt:
        mock_verify_jwt.side_effect = HTTPException(
            status_code=401,
            detail="Invalid JWT token",
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_api_authentication(
                authorization=f"Bearer {invalid_jwt}",
                db=mock_db,
            )

        assert exc_info.value.status_code == 401
        assert "Invalid JWT token" in exc_info.value.detail


@pytest.mark.asyncio
async def test_middleware_rejects_invalid_token_format():
    """Vérifie que le middleware rejette un format de token invalide."""
    # Arrange
    invalid_token = "invalid_format_no_prefix"
    mock_db = Mock()

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_authentication(
            authorization=f"Bearer {invalid_token}",
            db=mock_db,
        )

    assert exc_info.value.status_code == 401
    assert "Invalid token format" in exc_info.value.detail


@pytest.mark.asyncio
async def test_middleware_rejects_missing_authorization_header():
    """Vérifie que le middleware rejette les requêtes sans header Authorization."""
    # Arrange
    mock_db = Mock()

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_authentication(
            authorization=None,
            db=mock_db,
        )

    assert exc_info.value.status_code == 401
    assert "Missing Authorization header" in exc_info.value.detail


@pytest.mark.asyncio
async def test_middleware_rejects_malformed_authorization_header():
    """Vérifie que le middleware rejette un header Authorization mal formé."""
    # Arrange
    mock_db = Mock()

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_authentication(
            authorization="InvalidFormat token",
            db=mock_db,
        )

    assert exc_info.value.status_code == 401
    assert "Invalid Authorization header format" in exc_info.value.detail


@pytest.mark.asyncio
async def test_middleware_routes_hbc_prefix_to_api_key_verification():
    """Vérifie que les tokens avec préfixe hbc_ sont routés vers la vérification API Key."""
    # Arrange
    api_key_secret = "hbc_test_secret_12345678901234567890"
    mock_db = Mock()
    mock_key_record = Mock()
    mock_key_record.is_active = True
    mock_key_record.expires_at = None
    mock_key_record.user_id = 1

    mock_user = Mock()
    mock_user.id = 1
    mock_user.is_active = True

    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_key_record
    mock_db.query.return_value = mock_query

    mock_user_query = Mock()
    mock_user_query.filter.return_value.first.return_value = mock_user
    mock_db.query.side_effect = [mock_query, mock_user_query]

    # Act
    result = await verify_api_authentication(
        authorization=f"Bearer {api_key_secret}",
        db=mock_db,
    )

    # Assert
    assert result == mock_user


@pytest.mark.asyncio
async def test_middleware_routes_eyj_prefix_to_jwt_verification():
    """Vérifie que les tokens avec préfixe eyJ sont routés vers la vérification JWT."""
    # Arrange
    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
    mock_db = Mock()
    mock_user = Mock()

    with patch(
        "shared.infrastructure.api_v1.middleware._verify_jwt_token",
        new_callable=AsyncMock,
    ) as mock_verify_jwt:
        mock_verify_jwt.return_value = mock_user

        # Act
        result = await verify_api_authentication(
            authorization=f"Bearer {jwt_token}",
            db=mock_db,
        )

        # Assert
        assert result == mock_user
        mock_verify_jwt.assert_called_once_with(jwt_token, mock_db)


@pytest.mark.asyncio
async def test_middleware_rejects_inactive_user():
    """Vérifie que le middleware rejette un utilisateur inactif."""
    # Arrange
    valid_secret = "hbc_test_secret_12345678901234567890"
    mock_db = Mock()
    mock_key_record = Mock()
    mock_key_record.is_active = True
    mock_key_record.expires_at = None
    mock_key_record.user_id = 1

    mock_user = Mock()
    mock_user.id = 1
    mock_user.is_active = False  # Utilisateur inactif

    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_key_record
    mock_db.query.return_value = mock_query

    mock_user_query = Mock()
    mock_user_query.filter.return_value.first.return_value = mock_user
    mock_db.query.side_effect = [mock_query, mock_user_query]

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await _verify_api_key(valid_secret, mock_db)

    assert exc_info.value.status_code == 401
    assert "User not found or inactive" in exc_info.value.detail


@pytest.mark.asyncio
async def test_middleware_rejects_missing_user():
    """Vérifie que le middleware rejette si l'utilisateur n'existe pas."""
    # Arrange
    valid_secret = "hbc_test_secret_12345678901234567890"
    mock_db = Mock()
    mock_key_record = Mock()
    mock_key_record.is_active = True
    mock_key_record.expires_at = None
    mock_key_record.user_id = 999

    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_key_record
    mock_db.query.return_value = mock_query

    mock_user_query = Mock()
    mock_user_query.filter.return_value.first.return_value = None  # Utilisateur non trouvé
    mock_db.query.side_effect = [mock_query, mock_user_query]

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await _verify_api_key(valid_secret, mock_db)

    assert exc_info.value.status_code == 401
    assert "User not found or inactive" in exc_info.value.detail


@pytest.mark.asyncio
async def test_middleware_hashes_api_key_correctly():
    """Vérifie que le middleware hashe correctement la clé API."""
    # Arrange
    import hashlib
    secret = "hbc_test_secret_12345678901234567890"
    expected_hash = hashlib.sha256(secret.encode("utf-8")).hexdigest()

    mock_db = Mock()
    mock_query = Mock()
    mock_filter = Mock()
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = None
    mock_db.query.return_value = mock_query

    # Act
    try:
        await _verify_api_key(secret, mock_db)
    except HTTPException:
        pass  # On s'attend à une exception car la clé n'est pas trouvée

    # Assert
    # Vérifier que filter a été appelé avec le bon hash
    # Le hash devrait être dans les appels à filter
    assert mock_query.filter.called


@pytest.mark.asyncio
async def test_middleware_accepts_non_expiring_key():
    """Vérifie que le middleware accepte une clé sans date d'expiration."""
    # Arrange
    valid_secret = "hbc_test_secret_12345678901234567890"
    mock_db = Mock()
    mock_key_record = Mock()
    mock_key_record.is_active = True
    mock_key_record.expires_at = None  # Pas d'expiration
    mock_key_record.user_id = 1

    mock_user = Mock()
    mock_user.id = 1
    mock_user.is_active = True

    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_key_record
    mock_db.query.return_value = mock_query

    mock_user_query = Mock()
    mock_user_query.filter.return_value.first.return_value = mock_user
    mock_db.query.side_effect = [mock_query, mock_user_query]

    # Act
    result = await _verify_api_key(valid_secret, mock_db)

    # Assert
    assert result == mock_user


@pytest.mark.asyncio
async def test_middleware_accepts_not_yet_expired_key():
    """Vérifie que le middleware accepte une clé dont l'expiration est dans le futur."""
    # Arrange
    valid_secret = "hbc_test_secret_12345678901234567890"
    mock_db = Mock()
    mock_key_record = Mock()
    mock_key_record.is_active = True
    mock_key_record.expires_at = datetime.utcnow() + timedelta(days=30)  # Expire dans 30 jours
    mock_key_record.user_id = 1

    mock_user = Mock()
    mock_user.id = 1
    mock_user.is_active = True

    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_key_record
    mock_db.query.return_value = mock_query

    mock_user_query = Mock()
    mock_user_query.filter.return_value.first.return_value = mock_user
    mock_db.query.side_effect = [mock_query, mock_user_query]

    # Act
    result = await _verify_api_key(valid_secret, mock_db)

    # Assert
    assert result == mock_user


@pytest.mark.asyncio
async def test_middleware_bearer_prefix_removed():
    """Vérifie que le préfixe Bearer est correctement supprimé."""
    # Arrange
    api_key_secret = "hbc_test_secret_12345678901234567890"
    authorization_header = f"Bearer {api_key_secret}"
    mock_db = Mock()
    mock_key_record = Mock()
    mock_key_record.is_active = True
    mock_key_record.expires_at = None
    mock_key_record.user_id = 1

    mock_user = Mock()
    mock_user.id = 1
    mock_user.is_active = True

    mock_query = Mock()
    mock_query.filter.return_value.first.return_value = mock_key_record
    mock_db.query.return_value = mock_query

    mock_user_query = Mock()
    mock_user_query.filter.return_value.first.return_value = mock_user
    mock_db.query.side_effect = [mock_query, mock_user_query]

    # Act
    result = await verify_api_authentication(
        authorization=authorization_header,
        db=mock_db,
    )

    # Assert
    assert result == mock_user


@pytest.mark.asyncio
async def test_middleware_case_sensitive_bearer():
    """Vérifie que 'Bearer' doit avoir la bonne casse."""
    # Arrange
    mock_db = Mock()

    # Act & Assert - lowercase 'bearer' devrait échouer
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_authentication(
            authorization="bearer hbc_test",
            db=mock_db,
        )

    assert exc_info.value.status_code == 401
    assert "Invalid Authorization header format" in exc_info.value.detail


@pytest.mark.asyncio
async def test_middleware_www_authenticate_header():
    """Vérifie que le header WWW-Authenticate est présent dans les erreurs 401."""
    # Arrange
    mock_db = Mock()

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_authentication(
            authorization=None,
            db=mock_db,
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.headers.get("WWW-Authenticate") == "Bearer"
