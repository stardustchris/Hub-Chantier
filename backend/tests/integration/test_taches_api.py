"""Tests d'integration pour l'API des taches.

Ces tests verifient les endpoints FastAPI avec une vraie DB SQLite.
Selon CDC Section 13 - Gestion des Taches (TAC-01 a TAC-20).
"""

import pytest


@pytest.fixture
def chantier_id(client, auth_headers):
    """Cree un chantier et retourne son ID."""
    response = client.post(
        "/api/chantiers",
        json={
            "nom": "Chantier pour Taches",
            "adresse": "456 Rue des Taches",
            "code": "X001",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, f"Chantier creation failed: {response.json()}"
    return response.json()["id"]


@pytest.fixture
def sample_tache_data(chantier_id):
    """Donnees de test pour une tache."""
    return {
        "chantier_id": chantier_id,
        "titre": "Tache de test integration",
        "description": "Description de la tache de test",
    }


class TestTacheCreate:
    """Tests d'integration pour la creation de tache (TAC-01)."""

    def test_create_tache_success(self, client, auth_headers, sample_tache_data):
        """Test creation de tache reussie."""
        response = client.post(
            "/api/taches",
            json=sample_tache_data,
            headers=auth_headers,
        )

        assert response.status_code == 201, f"Creation failed: {response.json()}"
        data = response.json()
        assert data["titre"] == sample_tache_data["titre"]
        # L'ID peut etre int ou string selon l'API
        assert str(data["chantier_id"]) == str(sample_tache_data["chantier_id"])
        assert "id" in data

    def test_create_tache_unauthorized(self, client, sample_tache_data):
        """Test creation sans authentification."""
        response = client.post("/api/taches", json=sample_tache_data)

        assert response.status_code == 401


class TestTacheGet:
    """Tests d'integration pour la recuperation de tache."""

    def test_get_tache_by_id(self, client, auth_headers, sample_tache_data):
        """Test recuperation par ID."""
        # Creer
        create_response = client.post(
            "/api/taches",
            json=sample_tache_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201, f"Creation failed: {create_response.json()}"
        tache_id = create_response.json()["id"]

        # Recuperer
        response = client.get(
            f"/api/taches/{tache_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        # ID peut etre int ou string
        assert str(response.json()["id"]) == str(tache_id)

    def test_get_tache_not_found(self, client, auth_headers):
        """Test recuperation tache inexistante."""
        response = client.get("/api/taches/99999", headers=auth_headers)

        assert response.status_code == 404


class TestTacheUpdate:
    """Tests d'integration pour la mise a jour de tache."""

    def test_update_tache_success(self, client, auth_headers, sample_tache_data):
        """Test mise a jour reussie."""
        # Creer
        create_response = client.post(
            "/api/taches",
            json=sample_tache_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201, f"Creation failed: {create_response.json()}"
        tache_id = create_response.json()["id"]

        # Mettre a jour
        response = client.put(
            f"/api/taches/{tache_id}",
            json={"titre": "Titre Modifie"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["titre"] == "Titre Modifie"

    def test_update_tache_not_found(self, client, auth_headers):
        """Test mise a jour tache inexistante."""
        response = client.put(
            "/api/taches/99999",
            json={"titre": "Test"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestTacheDelete:
    """Tests d'integration pour la suppression de tache."""

    def test_delete_tache_success(self, client, auth_headers, sample_tache_data):
        """Test suppression reussie."""
        # Creer
        create_response = client.post(
            "/api/taches",
            json=sample_tache_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201, f"Creation failed: {create_response.json()}"
        tache_id = create_response.json()["id"]

        # Supprimer
        response = client.delete(
            f"/api/taches/{tache_id}",
            headers=auth_headers,
        )

        # L'API peut retourner 200 ou 204
        assert response.status_code in [200, 204]

        # Verifier suppression
        get_response = client.get(f"/api/taches/{tache_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_tache_not_found(self, client, auth_headers):
        """Test suppression tache inexistante."""
        response = client.delete("/api/taches/99999", headers=auth_headers)

        assert response.status_code == 404
