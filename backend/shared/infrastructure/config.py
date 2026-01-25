"""Configuration de l'application."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()


@dataclass
class Settings:
    """
    Configuration globale de l'application.

    Les valeurs sont lues depuis les variables d'environnement
    avec des valeurs par défaut pour le développement.
    """

    # Application
    APP_NAME: str = "Hub Chantier"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False  # P2-1: False par défaut (sécurité)

    # Database
    DATABASE_URL: str = "sqlite:///./data/hub_chantier.db"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    CORS_ORIGINS: list = None

    # Cookie settings (HttpOnly for security)
    COOKIE_SECURE: bool = True  # True in production (HTTPS)
    COOKIE_SAMESITE: str = "lax"  # Protect against CSRF
    COOKIE_DOMAIN: str = None  # None = current domain

    # Encryption (RGPD Art. 32)
    ENCRYPTION_KEY: str = "dev-encryption-key-change-in-production-32ch"

    def __post_init__(self):
        """Charge les variables d'environnement."""
        self.APP_NAME = os.getenv("APP_NAME", self.APP_NAME)
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"  # P2-1: false par défaut
        self.DATABASE_URL = os.getenv("DATABASE_URL", self.DATABASE_URL)
        self.SECRET_KEY = os.getenv("SECRET_KEY", self.SECRET_KEY)
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(self.ACCESS_TOKEN_EXPIRE_MINUTES))
        )

        cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
        self.CORS_ORIGINS = [origin.strip() for origin in cors_origins.split(",")]

        # Cookie settings
        self.COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"
        self.COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")
        self.COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", None)

        # Encryption key (must be 32 bytes for AES-256)
        self.ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", self.ENCRYPTION_KEY)

        # Validation sécurité en production (P0 - CRITIQUE)
        self._validate_production_security()

    def _validate_production_security(self) -> None:
        """
        Valide que les clés secrètes sont configurées en production.

        Raises:
            RuntimeError: Si les clés par défaut sont utilisées en production.
        """
        if not self.DEBUG:
            if self.SECRET_KEY.startswith("dev-"):
                raise RuntimeError(
                    "ERREUR CRITIQUE DE SECURITE: SECRET_KEY ne doit pas utiliser "
                    "la valeur par défaut en production. "
                    "Définissez la variable d'environnement SECRET_KEY avec une "
                    "clé sécurisée d'au moins 32 caractères."
                )
            if self.ENCRYPTION_KEY.startswith("dev-"):
                raise RuntimeError(
                    "ERREUR CRITIQUE DE SECURITE: ENCRYPTION_KEY ne doit pas utiliser "
                    "la valeur par défaut en production. "
                    "Définissez la variable d'environnement ENCRYPTION_KEY avec une "
                    "clé de 32 caractères exactement pour le chiffrement AES-256."
                )
            if len(self.SECRET_KEY) < 32:
                raise RuntimeError(
                    "ERREUR CRITIQUE DE SECURITE: SECRET_KEY doit contenir au moins "
                    "32 caractères pour assurer la sécurité des tokens JWT."
                )
            if len(self.ENCRYPTION_KEY) != 32:
                raise RuntimeError(
                    "ERREUR CRITIQUE DE SECURITE: ENCRYPTION_KEY doit contenir exactement "
                    "32 caractères pour le chiffrement AES-256 (RGPD Art. 32)."
                )


# Instance globale
settings = Settings()
