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
    Utilise une Base partagée pour que les ForeignKeys entre modules fonctionnent.
    """
    from .database_base import Base

    # Import des modèles pour les enregistrer dans la Base partagée
    from modules.auth.infrastructure.persistence import UserModel  # noqa: F401
    from modules.dashboard.infrastructure.persistence import PostModel, CommentModel, LikeModel, PostMediaModel  # noqa: F401
    from modules.chantiers.infrastructure.persistence import ChantierModel, ContactChantierModel, PhaseChantierModel  # noqa: F401
    from modules.pointages.infrastructure.persistence import PointageModel, FeuilleHeuresModel, VariablePaieModel  # noqa: F401
    from modules.taches.infrastructure.persistence import TacheModel, TemplateModeleModel, SousTacheModeleModel, FeuilleTacheModel  # noqa: F401
    from modules.formulaires.infrastructure.persistence import TemplateFormulaireModel, ChampTemplateModel, FormulaireRempliModel, ChampRempliModel, PhotoFormulaireModel  # noqa: F401
    from modules.signalements.infrastructure.persistence import SignalementModel, ReponseModel  # noqa: F401
    from modules.planning.infrastructure.persistence import AffectationModel  # noqa: F401
    from modules.documents.infrastructure.persistence import DossierModel, DocumentModel, AutorisationDocumentModel  # noqa: F401
    from modules.logistique.infrastructure.persistence import RessourceModel, ReservationModel  # noqa: F401

    # Crée toutes les tables en une seule fois avec la Base partagée
    Base.metadata.create_all(bind=engine)

    # Migration des donnees JSON vers tables de jointure (si necessaire)
    _migrate_chantier_responsables()


def _migrate_chantier_responsables() -> None:
    """
    Migre les donnees legacy JSON (conducteur_ids, chef_chantier_ids)
    vers les tables de jointure (chantier_conducteurs, chantier_chefs).

    Cette migration s'execute au demarrage et est idempotente.
    """
    from modules.chantiers.infrastructure.persistence import (
        ChantierModel,
        ChantierConducteurModel,
        ChantierChefModel,
    )

    db = SessionLocal()
    try:
        # Verifier si la migration est necessaire
        existing_count = db.query(ChantierConducteurModel).count()
        if existing_count > 0:
            # Deja migre, on skip
            return

        # Recuperer tous les chantiers avec leurs IDs JSON
        chantiers = db.query(ChantierModel).filter(
            ChantierModel.deleted_at.is_(None)
        ).all()

        migrated = 0
        for chantier in chantiers:
            # Migrer les conducteurs
            conducteur_ids = chantier.conducteur_ids or []
            for user_id in conducteur_ids:
                if user_id:
                    db.add(ChantierConducteurModel(
                        chantier_id=chantier.id,
                        user_id=user_id,
                    ))
                    migrated += 1

            # Migrer les chefs de chantier
            chef_ids = chantier.chef_chantier_ids or []
            for user_id in chef_ids:
                if user_id:
                    db.add(ChantierChefModel(
                        chantier_id=chantier.id,
                        user_id=user_id,
                    ))
                    migrated += 1

        if migrated > 0:
            db.commit()
            print(f"Migration tables jointure: {migrated} associations migrees")
        else:
            print("Migration tables jointure: aucune donnee a migrer")

    except Exception as e:
        db.rollback()
        print(f"Erreur migration tables jointure: {e}")
    finally:
        db.close()
