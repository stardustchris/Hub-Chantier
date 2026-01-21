"""Configuration de l'application."""

import os
from dataclasses import dataclass
from typing import Optional


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
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./data/hub_chantier.db"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    CORS_ORIGINS: list = None

    def __post_init__(self):
        """Charge les variables d'environnement."""
        self.APP_NAME = os.getenv("APP_NAME", self.APP_NAME)
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        self.DATABASE_URL = os.getenv("DATABASE_URL", self.DATABASE_URL)
        self.SECRET_KEY = os.getenv("SECRET_KEY", self.SECRET_KEY)
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(self.ACCESS_TOKEN_EXPIRE_MINUTES))
        )

        cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
        self.CORS_ORIGINS = [origin.strip() for origin in cors_origins.split(",")]


# Instance globale
settings = Settings()
