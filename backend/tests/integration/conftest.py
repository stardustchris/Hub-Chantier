"""Configuration des tests d'integration.

Ces tests utilisent la vraie application FastAPI avec une base SQLite en memoire.
"""

import pytest
import sys
import os

# Ajouter le dossier backend au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from sqlalchemy import text

from main import app
from shared.infrastructure.database import get_db
from modules.auth.infrastructure.persistence import Base as AuthBase
from modules.chantiers.infrastructure.persistence import Base as ChantiersBase
from modules.taches.infrastructure.persistence import Base as TachesBase
from modules.dashboard.infrastructure.persistence import Base as DashboardBase
from modules.pointages.infrastructure.persistence import Base as PointagesBase
from modules.planning.infrastructure.persistence.affectation_model import Base as PlanningBase
from modules.formulaires.infrastructure.persistence import Base as FormulairesBase
from modules.signalements.infrastructure.persistence import Base as SignalementsBase
from modules.documents.infrastructure.persistence.models import Base as DocumentsBase


@pytest.fixture(scope="function")
def test_db():
    """
    Cree une base de donnees SQLite en memoire pour les tests.

    Chaque test obtient une DB fraiche.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Creer les tables des modules sans dependances croisees
    AuthBase.metadata.create_all(bind=engine)
    ChantiersBase.metadata.create_all(bind=engine)
    TachesBase.metadata.create_all(bind=engine)
    DashboardBase.metadata.create_all(bind=engine)
    PointagesBase.metadata.create_all(bind=engine)
    FormulairesBase.metadata.create_all(bind=engine)

    # Pour le module Planning, on doit reflechir les tables users et chantiers
    # dans sa metadata avant de creer la table affectations
    # Cela permet a SQLAlchemy de resoudre les ForeignKey
    PlanningBase.metadata.reflect(bind=engine, only=['users', 'chantiers'])
    PlanningBase.metadata.create_all(bind=engine)

    # Modules Signalements et Documents (avec FK vers users et chantiers)
    SignalementsBase.metadata.reflect(bind=engine, only=['users', 'chantiers'])
    SignalementsBase.metadata.create_all(bind=engine)
    DocumentsBase.metadata.reflect(bind=engine, only=['users', 'chantiers'])
    DocumentsBase.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestingSessionLocal()

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(test_db):
    """Client de test FastAPI avec DB en memoire."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    """
    Cree un utilisateur admin et retourne les headers d'authentification.

    Returns:
        Dict avec le header Authorization.
    """
    # Creer un utilisateur admin
    response = client.post(
        "/api/auth/register",
        json={
            "email": "admin@test.com",
            "password": "TestPassword123!",
            "nom": "Admin",
            "prenom": "Test",
            "role": "admin",
            "type_utilisateur": "employe",
        },
    )
    assert response.status_code == 201, f"Registration failed: {response.json()}"

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_headers(client):
    """
    Cree un utilisateur standard et retourne les headers d'authentification.

    Returns:
        Dict avec le header Authorization.
    """
    # Creer un utilisateur standard
    response = client.post(
        "/api/auth/register",
        json={
            "email": "user@test.com",
            "password": "TestPassword123!",
            "nom": "User",
            "prenom": "Test",
            "role": "compagnon",
            "type_utilisateur": "employe",
        },
    )
    assert response.status_code == 201, f"Registration failed: {response.json()}"

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_chantier_data():
    """Donnees de test pour un chantier."""
    return {
        "nom": "Chantier Test Integration",
        "adresse": "123 Rue du Test, 75001 Paris",
        "code": "T001",  # Format valide: lettre + 3 chiffres
        "description": "Chantier de test pour les tests d'integration",
        "latitude": 48.8566,
        "longitude": 2.3522,
    }


@pytest.fixture
def sample_user_data():
    """Donnees de test pour un utilisateur."""
    return {
        "email": "nouveau@test.com",
        "password": "SecurePass123!",
        "nom": "Nouveau",
        "prenom": "Utilisateur",
        "role": "chef_chantier",
        "type_utilisateur": "employe",
        "telephone": "0612345678",
        "metier": "Macon",
    }


# =============================================================================
# Fixtures RBAC - Differents roles pour tester les permissions
# =============================================================================


@pytest.fixture
def admin_auth_headers(client):
    """
    Cree un utilisateur admin et retourne les headers d'authentification.
    Alias pour auth_headers pour la clarte des tests RBAC.
    """
    response = client.post(
        "/api/auth/register",
        json={
            "email": "admin_rbac@test.com",
            "password": "TestPassword123!",
            "nom": "Admin",
            "prenom": "RBAC",
            "role": "admin",
            "type_utilisateur": "employe",
        },
    )
    assert response.status_code == 201, f"Registration failed: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def conducteur_auth_headers(client):
    """
    Cree un utilisateur conducteur et retourne les headers d'authentification.
    Le conducteur peut creer/modifier des chantiers mais pas les supprimer.
    """
    response = client.post(
        "/api/auth/register",
        json={
            "email": "conducteur@test.com",
            "password": "TestPassword123!",
            "nom": "Conducteur",
            "prenom": "Test",
            "role": "conducteur",
            "type_utilisateur": "employe",
        },
    )
    assert response.status_code == 201, f"Registration failed: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def compagnon_auth_headers(client):
    """
    Cree un utilisateur compagnon et retourne les headers d'authentification.
    Le compagnon ne peut que lire les chantiers, pas les modifier.
    """
    response = client.post(
        "/api/auth/register",
        json={
            "email": "compagnon@test.com",
            "password": "TestPassword123!",
            "nom": "Compagnon",
            "prenom": "Test",
            "role": "compagnon",
            "type_utilisateur": "employe",
        },
    )
    assert response.status_code == 201, f"Registration failed: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
