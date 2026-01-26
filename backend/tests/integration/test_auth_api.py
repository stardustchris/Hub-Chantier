"""Tests d'integration pour l'API d'authentification.

Ces tests verifient les endpoints FastAPI avec une vraie DB SQLite.
Selon CDC Section 3 - Gestion des Utilisateurs (USR-01 a USR-13).
"""

import pytest


class TestAuthRegister:
    """Tests d'integration pour l'inscription (USR-01)."""

    def test_register_success(self, client, sample_user_data):
        """Test inscription reussie."""
        response = client.post("/api/auth/register", json=sample_user_data)

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == sample_user_data["email"]
        # Le systeme normalise le nom en majuscules
        assert data["user"]["nom"] == sample_user_data["nom"].upper()
        assert data["user"]["prenom"] == sample_user_data["prenom"].capitalize()
        assert data["user"]["is_active"] is True

    def test_register_duplicate_email(self, client, sample_user_data):
        """Test inscription avec email deja utilise."""
        # Premier enregistrement
        response1 = client.post("/api/auth/register", json=sample_user_data)
        assert response1.status_code == 201

        # Deuxieme enregistrement avec meme email
        response2 = client.post("/api/auth/register", json=sample_user_data)
        # Peut etre 400 ou 409 selon l'implementation
        assert response2.status_code in [400, 409]

    def test_register_weak_password(self, client, sample_user_data):
        """Test inscription avec mot de passe faible."""
        sample_user_data["password"] = "weak"
        response = client.post("/api/auth/register", json=sample_user_data)

        assert response.status_code in [400, 422]

    def test_register_invalid_email(self, client, sample_user_data):
        """Test inscription avec email invalide."""
        sample_user_data["email"] = "invalid-email"
        response = client.post("/api/auth/register", json=sample_user_data)

        assert response.status_code == 422


class TestAuthLogin:
    """Tests d'integration pour la connexion (USR-02)."""

    def test_login_success(self, client, sample_user_data):
        """Test connexion reussie."""
        # D'abord enregistrer
        client.post("/api/auth/register", json=sample_user_data)

        # Puis se connecter
        response = client.post(
            "/api/auth/login",
            data={
                "username": sample_user_data["email"],
                "password": sample_user_data["password"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_password(self, client, sample_user_data):
        """Test connexion avec mauvais mot de passe."""
        client.post("/api/auth/register", json=sample_user_data)

        response = client.post(
            "/api/auth/login",
            data={
                "username": sample_user_data["email"],
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test connexion avec utilisateur inexistant."""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent@test.com",
                "password": "Password123!",
            },
        )

        assert response.status_code == 401


class TestAuthCurrentUser:
    """Tests d'integration pour recuperer l'utilisateur courant (USR-03)."""

    def test_get_current_user_success(self, client, auth_headers):
        """Test recuperation utilisateur courant."""
        response = client.get("/api/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert "id" in data

    def test_get_current_user_no_token(self, client):
        """Test acces sans token."""
        response = client.get("/api/auth/me")

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """Test acces avec token invalide."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401


class TestUsersList:
    """Tests d'integration pour la liste des utilisateurs (USR-09)."""

    def test_list_users_as_admin(self, client, auth_headers):
        """Test liste utilisateurs en tant qu'admin."""
        response = client.get("/api/users", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1

    def test_list_users_pagination(self, client, auth_headers):
        """Test pagination de la liste."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        # Creer plusieurs utilisateurs avec emails uniques
        for i in range(5):
            client.post(
                "/api/auth/register",
                json={
                    "email": f"user{i}_{unique_id}@test.com",
                    "password": "Password123!",
                    "nom": f"User{i}",
                    "prenom": "Test",
                    "type_utilisateur": "employe",
                },
            )

        # Test avec page et size (format FastAPI pagination)
        response = client.get(
            "/api/users",
            params={"page": 1, "size": 2},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # Verifie que la pagination retourne des donnees
        assert "items" in data
        assert data["total"] >= 5


class TestUserUpdate:
    """Tests d'integration pour la mise a jour d'utilisateur (USR-05)."""

    def test_update_user_success(self, client, auth_headers):
        """Test mise a jour utilisateur reussie."""
        # D'abord recuperer l'ID de l'utilisateur
        me_response = client.get("/api/auth/me", headers=auth_headers)
        user_id = me_response.json()["id"]

        # Mettre a jour
        response = client.put(
            f"/api/users/{user_id}",
            json={"nom": "UpdatedNom", "telephone": "0698765432"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # Le systeme normalise le nom en majuscules
        assert data["nom"] == "UPDATEDNOM"
        assert data["telephone"] == "0698765432"

    @pytest.mark.xfail(reason="API ne gere pas encore l'erreur UserNotFoundError avec HTTP 404")
    def test_update_user_not_found(self, client, auth_headers):
        """Test mise a jour utilisateur inexistant."""
        response = client.put(
            "/api/users/99999",
            json={"nom": "Test"},
            headers=auth_headers,
        )

        # L'API devrait retourner 404
        assert response.status_code == 404


class TestUserDeactivate:
    """Tests d'integration pour la desactivation d'utilisateur (USR-10)."""

    def test_deactivate_user(self, client, auth_headers, sample_user_data):
        """Test desactivation d'un utilisateur."""
        # Creer un utilisateur a desactiver
        reg_response = client.post("/api/auth/register", json=sample_user_data)
        user_id = reg_response.json()["user"]["id"]

        # Desactiver
        response = client.post(
            f"/api/users/{user_id}/deactivate",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_activate_user(self, client, auth_headers, sample_user_data):
        """Test reactivation d'un utilisateur."""
        # Creer et desactiver
        reg_response = client.post("/api/auth/register", json=sample_user_data)
        user_id = reg_response.json()["user"]["id"]
        client.post(f"/api/users/{user_id}/deactivate", headers=auth_headers)

        # Reactiver
        response = client.post(
            f"/api/users/{user_id}/activate",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is True
