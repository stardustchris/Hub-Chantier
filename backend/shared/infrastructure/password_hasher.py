"""Password Hasher - Wrapper pour BcryptPasswordService."""

from modules.auth.adapters.providers.bcrypt_password_service import BcryptPasswordService

# Alias pour compatibilité avec les anciens imports
PasswordHasher = BcryptPasswordService
