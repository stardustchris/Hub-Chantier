"""Tests d'integration pour l'API du Dashboard (Fil d'actualites).

Ces tests verifient les endpoints FastAPI avec une vraie DB SQLite.
Selon CDC Section 2 - Tableau de Bord (FEED-01 a FEED-20).
"""

import pytest


class TestDashboardFeed:
    """Tests d'integration pour le fil d'actualites (FEED-09, FEED-18)."""

    def test_get_feed_empty(self, client, auth_headers):
        """Test recuperation du feed vide."""
        response = client.get("/api/dashboard/feed", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["items"]) == 0

    def test_get_feed_unauthorized(self, client):
        """Test recuperation du feed sans authentification."""
        response = client.get("/api/dashboard/feed")

        assert response.status_code == 401

    def test_get_feed_with_posts(self, client, auth_headers):
        """Test recuperation du feed avec des posts."""
        # Creer quelques posts
        for i in range(3):
            client.post(
                "/api/dashboard/posts",
                json={"contenu": f"Post de test {i}"},
                headers=auth_headers,
            )

        response = client.get("/api/dashboard/feed", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
        assert len(data["items"]) >= 3

    def test_get_feed_pagination(self, client, auth_headers):
        """Test pagination du feed."""
        # Creer plusieurs posts
        for i in range(5):
            client.post(
                "/api/dashboard/posts",
                json={"contenu": f"Post pagination {i}"},
                headers=auth_headers,
            )

        # Recuperer la premiere page
        response = client.get(
            "/api/dashboard/feed",
            params={"page": 1, "size": 2},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 2


class TestDashboardPosts:
    """Tests d'integration pour les posts (FEED-01, FEED-03)."""

    def test_create_post_success(self, client, auth_headers):
        """Test creation de post reussie."""
        response = client.post(
            "/api/dashboard/posts",
            json={"contenu": "Mon premier post de test"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["contenu"] == "Mon premier post de test"
        assert data["type"] == "message"

    def test_create_post_unauthorized(self, client):
        """Test creation de post sans authentification."""
        response = client.post(
            "/api/dashboard/posts",
            json={"contenu": "Post non autorise"},
        )

        assert response.status_code == 401

    def test_create_post_empty_content(self, client, auth_headers):
        """Test creation de post avec contenu vide."""
        response = client.post(
            "/api/dashboard/posts",
            json={"contenu": ""},
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_create_post_whitespace_only(self, client, auth_headers):
        """Test creation de post avec espaces uniquement."""
        response = client.post(
            "/api/dashboard/posts",
            json={"contenu": "   "},
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_create_urgent_post(self, client, auth_headers):
        """Test creation de post urgent (FEED-03)."""
        response = client.post(
            "/api/dashboard/posts",
            json={"contenu": "URGENT: Alerte securite!", "is_urgent": True},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["is_urgent"] is True
        assert data["type"] == "urgent"

    def test_get_post_by_id(self, client, auth_headers):
        """Test recuperation d'un post par ID."""
        # Creer un post
        create_response = client.post(
            "/api/dashboard/posts",
            json={"contenu": "Post a recuperer"},
            headers=auth_headers,
        )
        post_id = create_response.json()["id"]

        # Recuperer le post
        response = client.get(
            f"/api/dashboard/posts/{post_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["id"] == post_id

    def test_get_post_not_found(self, client, auth_headers):
        """Test recuperation d'un post inexistant."""
        response = client.get(
            "/api/dashboard/posts/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_delete_post_success(self, client, auth_headers):
        """Test suppression de post par l'auteur."""
        # Creer un post
        create_response = client.post(
            "/api/dashboard/posts",
            json={"contenu": "Post a supprimer"},
            headers=auth_headers,
        )
        post_id = create_response.json()["id"]

        # Supprimer le post
        response = client.delete(
            f"/api/dashboard/posts/{post_id}",
            headers=auth_headers,
        )

        # Le endpoint peut retourner 204 (No Content) ou 200 avec confirmation
        assert response.status_code in [200, 204]

        # Verifier la suppression - le post ne devrait plus etre visible dans le feed
        feed_response = client.get("/api/dashboard/feed", headers=auth_headers)
        if feed_response.status_code == 200:
            feed_data = feed_response.json()
            post_ids = [item["id"] for item in feed_data.get("items", [])]
            assert post_id not in post_ids

    def test_delete_post_not_found(self, client, auth_headers):
        """Test suppression d'un post inexistant."""
        response = client.delete(
            "/api/dashboard/posts/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestDashboardComments:
    """Tests d'integration pour les commentaires (FEED-05)."""

    @pytest.fixture
    def post_id(self, client, auth_headers):
        """Cree un post et retourne son ID."""
        response = client.post(
            "/api/dashboard/posts",
            json={"contenu": "Post pour commentaires"},
            headers=auth_headers,
        )
        return response.json()["id"]

    def test_add_comment_success(self, client, auth_headers, post_id):
        """Test ajout de commentaire reussi."""
        response = client.post(
            f"/api/dashboard/posts/{post_id}/comments",
            json={"contenu": "Super post!"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        # Retourne le post avec les commentaires
        data = response.json()
        assert data["commentaires_count"] >= 1

    def test_add_comment_empty_content(self, client, auth_headers, post_id):
        """Test ajout de commentaire avec contenu vide."""
        response = client.post(
            f"/api/dashboard/posts/{post_id}/comments",
            json={"contenu": ""},
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_add_comment_post_not_found(self, client, auth_headers):
        """Test ajout de commentaire sur post inexistant."""
        response = client.post(
            "/api/dashboard/posts/99999/comments",
            json={"contenu": "Commentaire"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestDashboardLikes:
    """Tests d'integration pour les likes (FEED-04)."""

    @pytest.fixture
    def post_id(self, client, auth_headers):
        """Cree un post et retourne son ID."""
        response = client.post(
            "/api/dashboard/posts",
            json={"contenu": "Post pour likes"},
            headers=auth_headers,
        )
        return response.json()["id"]

    def test_like_post_success(self, client, auth_headers, post_id):
        """Test like de post reussi."""
        response = client.post(
            f"/api/dashboard/posts/{post_id}/like",
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["likes_count"] >= 1

    def test_like_post_already_liked(self, client, auth_headers, post_id):
        """Test double like (doit echouer)."""
        # Premier like
        client.post(
            f"/api/dashboard/posts/{post_id}/like",
            headers=auth_headers,
        )

        # Deuxieme like
        response = client.post(
            f"/api/dashboard/posts/{post_id}/like",
            headers=auth_headers,
        )

        assert response.status_code == 409

    def test_like_post_not_found(self, client, auth_headers):
        """Test like sur post inexistant."""
        response = client.post(
            "/api/dashboard/posts/99999/like",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_unlike_post_success(self, client, auth_headers, post_id):
        """Test unlike de post reussi."""
        # D'abord liker
        client.post(
            f"/api/dashboard/posts/{post_id}/like",
            headers=auth_headers,
        )

        # Puis unlike
        response = client.delete(
            f"/api/dashboard/posts/{post_id}/like",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["likes_count"] == 0

    def test_unlike_post_not_liked(self, client, auth_headers, post_id):
        """Test unlike d'un post non like."""
        response = client.delete(
            f"/api/dashboard/posts/{post_id}/like",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestDashboardPin:
    """Tests d'integration pour l'epinglage de posts (FEED-08)."""

    @pytest.fixture
    def post_id(self, client, auth_headers):
        """Cree un post et retourne son ID."""
        response = client.post(
            "/api/dashboard/posts",
            json={"contenu": "Post a epingler"},
            headers=auth_headers,
        )
        return response.json()["id"]

    def test_pin_post_success(self, client, auth_headers, post_id):
        """Test epinglage de post reussi."""
        response = client.post(
            f"/api/dashboard/posts/{post_id}/pin",
            params={"duration_hours": 24},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_pinned"] is True

    def test_pin_post_not_found(self, client, auth_headers):
        """Test epinglage d'un post inexistant."""
        response = client.post(
            "/api/dashboard/posts/99999/pin",
            params={"duration_hours": 24},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_unpin_post_success(self, client, auth_headers, post_id):
        """Test desepinglage de post."""
        # D'abord epingler
        client.post(
            f"/api/dashboard/posts/{post_id}/pin",
            params={"duration_hours": 24},
            headers=auth_headers,
        )

        # Puis desepingler
        response = client.delete(
            f"/api/dashboard/posts/{post_id}/pin",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_pinned"] is False
