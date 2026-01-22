"""Configuration de la base de données SQLAlchemy."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .config import settings

# Créer le dossier data s'il n'existe pas
os.makedirs("data", exist_ok=True)

# Configuration du moteur SQLAlchemy
# Pour SQLite, on désactive check_same_thread et on utilise StaticPool
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DEBUG,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
    )

# Factory de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Générateur de session pour l'injection de dépendances FastAPI.

    Yields:
        Session SQLAlchemy.

    Usage:
        @app.get("/")
        def route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialise la base de données (crée les tables).

    À appeler au démarrage de l'application.
    """
    from modules.auth.infrastructure.persistence import Base as AuthBase
    from modules.dashboard.infrastructure.persistence import Base as DashboardBase

    AuthBase.metadata.create_all(bind=engine)
    DashboardBase.metadata.create_all(bind=engine)
