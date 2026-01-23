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


def init_db() -> None:
    """
    Initialise la base de données (crée les tables).

    À appeler au démarrage de l'application.
    """
    from sqlalchemy import text

    from modules.auth.infrastructure.persistence import Base as AuthBase
    from modules.dashboard.infrastructure.persistence import Base as DashboardBase
    from modules.chantiers.infrastructure.persistence import Base as ChantiersBase
    from modules.pointages.infrastructure.persistence import Base as PointagesBase
    from modules.taches.infrastructure.persistence import Base as TachesBase
    from modules.formulaires.infrastructure.persistence import Base as FormulairesBase
    from modules.signalements.infrastructure.persistence import Base as SignalementsBase

    AuthBase.metadata.create_all(bind=engine)
    DashboardBase.metadata.create_all(bind=engine)
    ChantiersBase.metadata.create_all(bind=engine)
    PointagesBase.metadata.create_all(bind=engine)
    TachesBase.metadata.create_all(bind=engine)
    FormulairesBase.metadata.create_all(bind=engine)
    SignalementsBase.metadata.create_all(bind=engine)

    # Creer la table affectations manuellement (module Planning)
    # car elle a des ForeignKey vers d'autres modules (users, chantiers)
    create_affectations = """
    CREATE TABLE IF NOT EXISTS affectations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        utilisateur_id INTEGER NOT NULL,
        chantier_id INTEGER NOT NULL,
        created_by INTEGER NOT NULL,
        date DATE NOT NULL,
        type_affectation VARCHAR(20) NOT NULL DEFAULT 'unique',
        heure_debut VARCHAR(5),
        heure_fin VARCHAR(5),
        note TEXT,
        jours_recurrence TEXT,
        date_fin DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    with engine.connect() as conn:
        conn.execute(text(create_affectations))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_affectations_utilisateur_id ON affectations(utilisateur_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_affectations_chantier_id ON affectations(chantier_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_affectations_date ON affectations(date)"))
        conn.commit()
