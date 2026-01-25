"""Configuration pytest et fixtures partagées."""

import pytest
import sys
import os

# P2-1: Activer DEBUG pour les tests (avant import des modules)
os.environ.setdefault("DEBUG", "true")

# Ajouter le dossier backend au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from modules.auth.domain.entities import User
from modules.auth.domain.value_objects import Email, PasswordHash, Role
from modules.auth.infrastructure.persistence import Base


def pytest_configure(config):
    """Hook pytest pour charger tous les modèles SQLAlchemy avant les tests."""
    # Importer tous les modèles une seule fois pour que SQLAlchemy puisse résoudre les relations
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
    from modules.interventions.infrastructure.persistence import InterventionModel, AffectationInterventionModel, InterventionMessageModel, SignatureInterventionModel  # noqa: F401
    from modules.planning_charge.infrastructure.persistence import BesoinChargeModel  # noqa: F401


@pytest.fixture(scope="function")
def db_session():
    """
    Crée une session de base de données en mémoire pour les tests.

    Chaque test obtient une DB fraîche.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()


@pytest.fixture
def test_user():
    """User de test standard."""
    return User(
        id=1,
        email=Email("test@example.com"),
        password_hash=PasswordHash("$2b$12$hashed_password_here"),
        nom="DUPONT",
        prenom="Jean",
        role=Role.EMPLOYE,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def admin_user():
    """User admin de test."""
    return User(
        id=2,
        email=Email("admin@example.com"),
        password_hash=PasswordHash("$2b$12$hashed_password_here"),
        nom="ADMIN",
        prenom="Super",
        role=Role.ADMIN,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def chef_chantier_user():
    """User chef de chantier de test."""
    return User(
        id=3,
        email=Email("chef@example.com"),
        password_hash=PasswordHash("$2b$12$hashed_password_here"),
        nom="CHEF",
        prenom="Pierre",
        role=Role.CHEF_CHANTIER,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
