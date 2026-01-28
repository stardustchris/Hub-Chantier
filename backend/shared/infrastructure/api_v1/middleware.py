"""Middleware d'authentification API v1 - Support JWT et API Key."""

import hashlib
from datetime import datetime
from typing import Optional

from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from modules.auth.infrastructure.persistence.api_key_model import APIKeyModel
from modules.auth.infrastructure.persistence.user_model import UserModel


async def verify_api_authentication(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Middleware d'authentification unifié pour l'API v1.

    Accepte deux types d'authentification:
    1. JWT Token (eyJ...) - Auth classique utilisateurs
    2. API Key (hbc_...) - Auth API publique

    Args:
        authorization: Header Authorization (Bearer <token>)
        db: Session SQLAlchemy

    Returns:
        User entity (compatible JWT et API Key)

    Raises:
        HTTPException: 401 si authentification échoue
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[7:]  # Enlever "Bearer "

    # Route 1 : API Key (commence par hbc_)
    if token.startswith("hbc_"):
        return await _verify_api_key(token, db)

    # Route 2 : JWT (commence par eyJ)
    elif token.startswith("eyJ"):
        return await _verify_jwt_token(token, db)

    # Format invalide
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid token format. Expected JWT (eyJ...) or API Key (hbc_...)",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def _verify_api_key(api_key: str, db: Session):
    """
    Vérifie une clé API.

    Process:
    1. Hash le secret avec SHA256
    2. Cherche le hash en DB
    3. Vérifie is_active et expiration
    4. Met à jour last_used_at
    5. Retourne l'utilisateur propriétaire

    Args:
        api_key: Secret API Key (hbc_xxxxx...)
        db: Session SQLAlchemy

    Returns:
        UserModel de l'utilisateur

    Raises:
        HTTPException: 401 si clé invalide/expirée/inactive
    """
    # 1. Hasher le secret (même algo que création)
    key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    # 2. Chercher en DB (index unique sur key_hash = très rapide)
    key_record = (
        db.query(APIKeyModel)
        .filter(
            APIKeyModel.key_hash == key_hash,
            APIKeyModel.is_active == True,  # Filtre clés révoquées
        )
        .first()
    )

    if not key_record:
        raise HTTPException(
            status_code=401,
            detail="Invalid or revoked API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Vérifier expiration
    if key_record.expires_at and datetime.utcnow() > key_record.expires_at:
        raise HTTPException(
            status_code=401,
            detail="API key expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Mettre à jour last_used_at (audit)
    key_record.last_used_at = datetime.utcnow()
    db.commit()

    # 5. Récupérer l'utilisateur propriétaire
    user = db.query(UserModel).filter(UserModel.id == key_record.user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def _verify_jwt_token(jwt_token: str, db: Session):
    """
    Vérifie un JWT token (rétrocompatibilité).

    Délègue à la fonction existante get_current_user du module auth.

    Args:
        jwt_token: Token JWT (eyJxxxx...)
        db: Session SQLAlchemy

    Returns:
        UserModel de l'utilisateur

    Raises:
        HTTPException: 401 si token invalide
    """
    # Import lazy pour éviter imports circulaires
    from modules.auth.infrastructure.web.dependencies import get_current_user

    # Vérifier JWT (logique existante)
    try:
        user = await get_current_user(jwt_token, db)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid JWT token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
