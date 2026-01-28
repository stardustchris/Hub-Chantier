#!/usr/bin/env python3
"""Script de débogage pour l'authentification."""

from shared.infrastructure.database import SessionLocal
from modules.auth.infrastructure.persistence.sqlalchemy_user_repository import SQLAlchemyUserRepository
from modules.auth.domain.value_objects import Email
from modules.auth.adapters.providers.bcrypt_password_service import BcryptPasswordService
from modules.auth.application.use_cases.login import LoginUseCase, LoginDTO
from modules.auth.adapters.providers.jwt_token_service import JWTTokenService
from shared.infrastructure import settings

def main():
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

    email = Email('admin@greg-construction.fr')
    user = repo.find_by_email(email)

    if user:
        print(f"✓ Utilisateur trouvé: {user.email}")
        print(f"  - Nom: {user.nom} {user.prenom}")
        print(f"  - Actif: {user.is_active}")
        print(f"  - Hash (50 premiers chars): {str(user.password_hash)[:50]}...")
    else:
        print("✗ Utilisateur non trouvé")
        return

    # Test 2: Vérifier le mot de passe directement
    print("\n" + "=" * 60)
    print("TEST 2: Vérification directe du mot de passe")
    print("=" * 60)

    passwords_to_test = ['Admin123!', 'Test123!', 'admin123']
    for pwd in passwords_to_test:
        result = pwd_service.verify(pwd, user.password_hash)
        status = "✓" if result else "✗"
        print(f"{status} Mot de passe '{pwd}': {result}")

    # Test 3: Tester le LoginUseCase
    print("\n" + "=" * 60)
    print("TEST 3: Test du LoginUseCase")
    print("=" * 60)

    try:
        dto = LoginDTO(email='admin@greg-construction.fr', password='Admin123!')
        print(f"DTO créé: email={dto.email}, password={'*' * len(dto.password)}")

        result = login_use_case.execute(dto)
        print("✓ Authentification réussie!")
        print(f"  - User ID: {result.user.id}")
        print(f"  - Email: {result.user.email}")
        print(f"  - Token (50 premiers chars): {result.token.access_token[:50]}...")

    except Exception as e:
        print(f"✗ Authentification échouée: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    db.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
