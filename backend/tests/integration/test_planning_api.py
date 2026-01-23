"""Tests d'integration pour l'API du Planning Operationnel.

Ces tests verifient les endpoints FastAPI avec une vraie DB SQLite.
Selon CDC Section 5 - Planning Operationnel (PLN-01 a PLN-28).
"""

import pytest
from datetime import date, timedelta


@pytest.fixture
def conducteur_headers(client):
    """Cree un utilisateur conducteur et retourne les headers."""
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
def compagnon_headers(client):
    """Cree un utilisateur compagnon et retourne les headers."""
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


@pytest.fixture
def chantier_id(client, auth_headers):
    """Cree un chantier et retourne son ID."""
    response = client.post(
        "/api/chantiers",
        json={
            "nom": "Chantier Planning Test",
            "adresse": "123 Rue Planning",
            "code": "P001",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, f"Chantier creation failed: {response.json()}"
    # L'API retourne les IDs en string, convertir en int
    return int(response.json()["id"])


@pytest.fixture
def utilisateur_id(client, auth_headers):
    """Cree un utilisateur et retourne son ID."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "planifie@test.com",
            "password": "TestPassword123!",
            "nom": "Planifie",
            "prenom": "User",
            "role": "compagnon",
            "type_utilisateur": "employe",
        },
    )
    assert response.status_code == 201, f"User creation failed: {response.json()}"
    # L'API retourne les IDs en string, convertir en int
    return int(response.json()["user"]["id"])


@pytest.fixture
def monday_date():
    """Retourne la date du lundi de la semaine courante."""
    today = date.today()
    # Calculer le lundi (weekday() retourne 0 pour lundi)
    monday = today - timedelta(days=today.weekday())
    return monday


class TestPlanningGet:
    """Tests d'integration pour la recuperation du planning (PLN-01 a PLN-03)."""

    def test_get_planning_empty(self, client, auth_headers, monday_date):
        """Test recuperation d'un planning vide."""
        response = client.get(
            "/api/planning/affectations",
            params={
                "date_debut": monday_date.isoformat(),
                "date_fin": (monday_date + timedelta(days=6)).isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_planning_unauthorized(self, client, monday_date):
        """Test recuperation du planning sans authentification."""
        response = client.get(
            "/api/planning/affectations",
            params={
                "date_debut": monday_date.isoformat(),
                "date_fin": (monday_date + timedelta(days=6)).isoformat(),
            },
        )

        assert response.status_code == 401


class TestAffectationCreate:
    """Tests d'integration pour la creation d'affectation (PLN-04 a PLN-09)."""

    def test_create_affectation_success(
        self, client, auth_headers, chantier_id, utilisateur_id, monday_date
    ):
        """Test creation d'affectation reussie."""
        response = client.post(
            "/api/planning/affectations",
            json={
                "utilisateur_id": utilisateur_id,
                "chantier_id": chantier_id,
                "date": monday_date.isoformat(),
                "type_affectation": "unique",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201, f"Creation failed: {response.json()}"
        data = response.json()
        assert "id" in data
        assert data["utilisateur_id"] == utilisateur_id
        assert data["chantier_id"] == chantier_id

    def test_create_affectation_with_horaires(
        self, client, auth_headers, chantier_id, utilisateur_id, monday_date
    ):
        """Test creation d'affectation avec horaires."""
        response = client.post(
            "/api/planning/affectations",
            json={
                "utilisateur_id": utilisateur_id,
                "chantier_id": chantier_id,
                "date": (monday_date + timedelta(days=1)).isoformat(),
                "type_affectation": "unique",
                "heure_debut": "08:00",
                "heure_fin": "17:00",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["heure_debut"] == "08:00"
        assert data["heure_fin"] == "17:00"

    def test_create_affectation_with_note(
        self, client, auth_headers, chantier_id, utilisateur_id, monday_date
    ):
        """Test creation d'affectation avec note."""
        response = client.post(
            "/api/planning/affectations",
            json={
                "utilisateur_id": utilisateur_id,
                "chantier_id": chantier_id,
                "date": (monday_date + timedelta(days=2)).isoformat(),
                "type_affectation": "unique",
                "note": "Apporter les outils",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["note"] == "Apporter les outils"

    def test_create_affectation_unauthorized_role(
        self, client, compagnon_headers, chantier_id, utilisateur_id, monday_date
    ):
        """Test creation d'affectation avec role non autorise."""
        response = client.post(
            "/api/planning/affectations",
            json={
                "utilisateur_id": utilisateur_id,
                "chantier_id": chantier_id,
                "date": monday_date.isoformat(),
                "type_affectation": "unique",
            },
            headers=compagnon_headers,
        )

        assert response.status_code == 403

    def test_create_affectation_conducteur_success(
        self, client, conducteur_headers, chantier_id, utilisateur_id, monday_date
    ):
        """Test creation d'affectation par conducteur."""
        response = client.post(
            "/api/planning/affectations",
            json={
                "utilisateur_id": utilisateur_id,
                "chantier_id": chantier_id,
                "date": monday_date.isoformat(),
                "type_affectation": "unique",
            },
            headers=conducteur_headers,
        )

        assert response.status_code == 201


class TestAffectationUpdate:
    """Tests d'integration pour la mise a jour d'affectation (PLN-07, PLN-08)."""

    @pytest.fixture
    def affectation_id(
        self, client, auth_headers, chantier_id, utilisateur_id, monday_date
    ):
        """Cree une affectation et retourne son ID."""
        response = client.post(
            "/api/planning/affectations",
            json={
                "utilisateur_id": utilisateur_id,
                "chantier_id": chantier_id,
                "date": (monday_date + timedelta(days=3)).isoformat(),
                "type_affectation": "unique",
            },
            headers=auth_headers,
        )
        return response.json()["id"]

    def test_update_affectation_horaires(
        self, client, auth_headers, affectation_id
    ):
        """Test mise a jour des horaires."""
        response = client.put(
            f"/api/planning/affectations/{affectation_id}",
            json={
                "heure_debut": "09:00",
                "heure_fin": "18:00",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["heure_debut"] == "09:00"
        assert data["heure_fin"] == "18:00"

    def test_update_affectation_note(
        self, client, auth_headers, affectation_id
    ):
        """Test mise a jour de la note."""
        response = client.put(
            f"/api/planning/affectations/{affectation_id}",
            json={"note": "Nouvelle note"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["note"] == "Nouvelle note"

    def test_update_affectation_not_found(self, client, auth_headers):
        """Test mise a jour d'une affectation inexistante."""
        response = client.put(
            "/api/planning/affectations/99999",
            json={"note": "Test"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_update_affectation_unauthorized_role(
        self, client, compagnon_headers, affectation_id
    ):
        """Test mise a jour avec role non autorise."""
        response = client.put(
            f"/api/planning/affectations/{affectation_id}",
            json={"note": "Test"},
            headers=compagnon_headers,
        )

        assert response.status_code == 403


class TestAffectationDelete:
    """Tests d'integration pour la suppression d'affectation (PLN-09)."""

    @pytest.fixture
    def affectation_id(
        self, client, auth_headers, chantier_id, utilisateur_id, monday_date
    ):
        """Cree une affectation et retourne son ID."""
        response = client.post(
            "/api/planning/affectations",
            json={
                "utilisateur_id": utilisateur_id,
                "chantier_id": chantier_id,
                "date": (monday_date + timedelta(days=4)).isoformat(),
                "type_affectation": "unique",
            },
            headers=auth_headers,
        )
        return response.json()["id"]

    def test_delete_affectation_success(
        self, client, auth_headers, affectation_id
    ):
        """Test suppression d'affectation reussie."""
        response = client.delete(
            f"/api/planning/affectations/{affectation_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["deleted"] is True

    def test_delete_affectation_not_found(self, client, auth_headers):
        """Test suppression d'une affectation inexistante."""
        response = client.delete(
            "/api/planning/affectations/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_delete_affectation_unauthorized_role(
        self, client, compagnon_headers, affectation_id
    ):
        """Test suppression avec role non autorise."""
        response = client.delete(
            f"/api/planning/affectations/{affectation_id}",
            headers=compagnon_headers,
        )

        assert response.status_code == 403


class TestPlanningNonPlanifies:
    """Tests d'integration pour les utilisateurs non planifies (PLN-10)."""

    def test_get_non_planifies(self, client, auth_headers, monday_date):
        """Test recuperation des utilisateurs non planifies."""
        response = client.get(
            "/api/planning/non-planifies",
            params={
                "date_debut": monday_date.isoformat(),
                "date_fin": (monday_date + timedelta(days=6)).isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "utilisateur_ids" in data
        assert "count" in data

    def test_get_non_planifies_unauthorized_role(
        self, client, compagnon_headers, monday_date
    ):
        """Test non planifies avec role non autorise."""
        response = client.get(
            "/api/planning/non-planifies",
            params={
                "date_debut": monday_date.isoformat(),
                "date_fin": (monday_date + timedelta(days=6)).isoformat(),
            },
            headers=compagnon_headers,
        )

        assert response.status_code == 403


class TestPlanningByChantier:
    """Tests d'integration pour le planning par chantier."""

    def test_get_planning_by_chantier(
        self, client, auth_headers, chantier_id, monday_date
    ):
        """Test recuperation du planning par chantier."""
        response = client.get(
            f"/api/planning/chantiers/{chantier_id}/affectations",
            params={
                "date_debut": monday_date.isoformat(),
                "date_fin": (monday_date + timedelta(days=6)).isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestPlanningByUtilisateur:
    """Tests d'integration pour le planning par utilisateur."""

    def test_get_planning_by_utilisateur(
        self, client, auth_headers, utilisateur_id, monday_date
    ):
        """Test recuperation du planning par utilisateur."""
        response = client.get(
            f"/api/planning/utilisateurs/{utilisateur_id}/affectations",
            params={
                "date_debut": monday_date.isoformat(),
                "date_fin": (monday_date + timedelta(days=6)).isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
