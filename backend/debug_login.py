#!/usr/bin/env python3
"""Script de débogage pour l'authentification.

Usage:
    DEBUG_EMAIL=admin@greg-construction.fr DEBUG_PASSWORD=xxx python debug_login.py
"""

import os
import sys

from shared.infrastructure.database import SessionLocal
from modules.auth.infrastructure.persistence.sqlalchemy_user_repository import SQLAlchemyUserRepository
from modules.auth.domain.value_objects import Email
from modules.auth.adapters.providers.bcrypt_password_service import BcryptPasswordService
from modules.auth.application.use_cases.login import LoginUseCase, LoginDTO
from modules.auth.adapters.providers.jwt_token_service import JWTTokenService
from shared.infrastructure import settings


def main():
    debug_email = os.environ.get("DEBUG_EMAIL")
    debug_password = os.environ.get("DEBUG_PASSWORD")

    if not debug_email or not debug_password:
        print("Usage: DEBUG_EMAIL=xxx DEBUG_PASSWORD=xxx python debug_login.py")
        sys.exit(1)

    db = SessionLocal()

    # Créer les services
    repo = SQLAlchemyUserRepository(db)
    pwd_service = BcryptPasswordService()
    token_service = JWTTokenService(
        secret_key=settings.SECRET_KEY,
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Créer le use case
    login_use_case = LoginUseCase(
        user_repo=repo,
        password_service=pwd_service,
        token_service=token_service
    )

    # Test 1: Vérifier que l'utilisateur existe
    print("=" * 60)
    print("TEST 1: Vérification de l'utilisateur")
    print("=" * 60)

    email = Email(debug_email)
    user = repo.find_by_email(email)

    if user:
        print(f"Utilisateur trouvé: {user.email}")
        print(f"  - Nom: {user.nom} {user.prenom}")
        print(f"  - Actif: {user.is_active}")
    else:
        print("Utilisateur non trouvé")
        db.close()
        return

    # Test 2: Vérifier le mot de passe directement
    print("\n" + "=" * 60)
    print("TEST 2: Vérification directe du mot de passe")
    print("=" * 60)

    result = pwd_service.verify(debug_password, user.password_hash)
    status = "OK" if result else "ECHEC"
    print(f"Mot de passe: {status}")

    # Test 3: Tester le LoginUseCase
    print("\n" + "=" * 60)
    print("TEST 3: Test du LoginUseCase")
    print("=" * 60)

    try:
        dto = LoginDTO(email=debug_email, password=debug_password)
        result = login_use_case.execute(dto)
        print("Authentification réussie!")
        print(f"  - User ID: {result.user.id}")
        print(f"  - Email: {result.user.email}")

    except Exception as e:
        print(f"Authentification échouée: {type(e).__name__}: {e}")

    db.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
