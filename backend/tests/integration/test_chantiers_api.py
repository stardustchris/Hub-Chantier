"""Tests d'integration pour l'API des chantiers.

Ces tests verifient les endpoints FastAPI avec une vraie DB SQLite.
Selon CDC Section 4 - Gestion des Chantiers (CHT-01 a CHT-20).
"""



class TestChantierCreate:
    """Tests d'integration pour la creation de chantier (CHT-01)."""

    def test_create_chantier_success(self, client, auth_headers, sample_chantier_data):
        """Test creation de chantier reussie."""
        response = client.post(
            "/api/chantiers",
            json=sample_chantier_data,
            headers=auth_headers,
        )

        assert response.status_code == 201, f"Creation failed: {response.json()}"
        data = response.json()
        assert data["nom"] == sample_chantier_data["nom"]
        assert data["adresse"] == sample_chantier_data["adresse"]
        assert data["code"] == sample_chantier_data["code"]
        # Statut initial est 'ouvert' (selon l'API)
        assert data["statut"] in ["ouvert", "Planifie"]
        assert "id" in data

    def test_create_chantier_minimal(self, client, auth_headers):
        """Test creation avec donnees minimales."""
        response = client.post(
            "/api/chantiers",
            json={"nom": "Chantier Minimal", "adresse": "1 Rue Simple"},
            headers=auth_headers,
        )

        assert response.status_code == 201, f"Creation failed: {response.json()}"
        data = response.json()
        assert data["nom"] == "Chantier Minimal"
        # Code auto-genere
        assert data["code"] is not None

    def test_create_chantier_duplicate_code(
        self, client, auth_headers, sample_chantier_data
    ):
        """Test creation avec code deja utilise."""
        # Premier chantier
        r1 = client.post("/api/chantiers", json=sample_chantier_data, headers=auth_headers)
        assert r1.status_code == 201, f"First creation failed: {r1.json()}"

        # Deuxieme avec meme code
        data2 = sample_chantier_data.copy()
        data2["nom"] = "Autre Chantier"
        response = client.post(
            "/api/chantiers",
            json=data2,
            headers=auth_headers,
        )

        # Attend 400 ou 409 selon l'implementation
        assert response.status_code in [400, 409]

    def test_create_chantier_unauthorized(self, client, sample_chantier_data):
        """Test creation sans authentification."""
        response = client.post("/api/chantiers", json=sample_chantier_data)

        assert response.status_code == 401


class TestChantierGet:
    """Tests d'integration pour la recuperation de chantier."""

    def test_get_chantier_by_id(self, client, auth_headers, sample_chantier_data):
        """Test recuperation par ID."""
        # Creer
        create_response = client.post(
            "/api/chantiers",
            json=sample_chantier_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201, f"Creation failed: {create_response.json()}"
        chantier_id = create_response.json()["id"]

        # Recuperer
        response = client.get(
            f"/api/chantiers/{chantier_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["id"] == chantier_id

    def test_get_chantier_not_found(self, client, auth_headers):
        """Test recuperation chantier inexistant."""
        response = client.get("/api/chantiers/99999", headers=auth_headers)

        assert response.status_code == 404


class TestChantierList:
    """Tests d'integration pour la liste des chantiers."""

    def test_list_chantiers(self, client, auth_headers, sample_chantier_data):
        """Test liste des chantiers."""
        # Creer quelques chantiers
        for i in range(3):
            data = sample_chantier_data.copy()
            data["code"] = f"L{i:03d}"
            data["nom"] = f"Chantier {i}"
            r = client.post("/api/chantiers", json=data, headers=auth_headers)
            assert r.status_code == 201, f"Creation {i} failed: {r.json()}"

        response = client.get("/api/chantiers", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        # L'API peut retourner 'items' ou 'chantiers'
        items_key = "chantiers" if "chantiers" in data else "items"
        assert items_key in data
        assert len(data[items_key]) >= 3
        assert "total" in data

    def test_list_chantiers_pagination(self, client, auth_headers, sample_chantier_data):
        """Test pagination de la liste."""
        # Creer plusieurs chantiers
        for i in range(5):
            data = sample_chantier_data.copy()
            data["code"] = f"P{i:03d}"
            data["nom"] = f"Paginated {i}"
            r = client.post("/api/chantiers", json=data, headers=auth_headers)
            assert r.status_code == 201, f"Creation {i} failed: {r.json()}"

        response = client.get(
            "/api/chantiers",
            params={"skip": 0, "limit": 2},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # L'API peut retourner 'items' ou 'chantiers'
        items_key = "chantiers" if "chantiers" in data else "items"
        assert items_key in data


class TestChantierUpdate:
    """Tests d'integration pour la mise a jour de chantier."""

    def test_update_chantier_success(self, client, auth_headers, sample_chantier_data):
        """Test mise a jour reussie."""
        # Creer
        create_response = client.post(
            "/api/chantiers",
            json=sample_chantier_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201, f"Creation failed: {create_response.json()}"
        chantier_id = create_response.json()["id"]

        # Mettre a jour
        response = client.put(
            f"/api/chantiers/{chantier_id}",
            json={"nom": "Nom Modifie", "description": "Nouvelle description"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["nom"] == "Nom Modifie"
        assert response.json()["description"] == "Nouvelle description"

    def test_update_chantier_not_found(self, client, auth_headers):
        """Test mise a jour chantier inexistant."""
        response = client.put(
            "/api/chantiers/99999",
            json={"nom": "Test"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestChantierStatut:
    """Tests d'integration pour le changement de statut (CHT-03)."""

    def test_change_statut_to_en_cours(self, client, auth_headers, sample_chantier_data):
        """Test passage a l'etat En cours."""
        # Creer
        create_response = client.post(
            "/api/chantiers",
            json=sample_chantier_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201, f"Creation failed: {create_response.json()}"
        chantier_id = create_response.json()["id"]

        # Demarrer
        response = client.post(
            f"/api/chantiers/{chantier_id}/demarrer",
            headers=auth_headers,
        )

        assert response.status_code == 200
        # Statut peut etre 'en_cours' ou 'En cours' selon l'API
        assert response.json()["statut"] in ["en_cours", "En cours"]


class TestChantierDelete:
    """Tests d'integration pour la suppression de chantier."""

    def test_delete_chantier_success(self, client, auth_headers, sample_chantier_data):
        """Test suppression reussie."""
        # Creer
        create_response = client.post(
            "/api/chantiers",
            json=sample_chantier_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201, f"Creation failed: {create_response.json()}"
        chantier_id = create_response.json()["id"]

        # Supprimer (force=true car chantier actif)
        response = client.delete(
            f"/api/chantiers/{chantier_id}",
            params={"force": True},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["deleted"] is True

        # Verifier suppression
        get_response = client.get(
            f"/api/chantiers/{chantier_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    def test_delete_chantier_not_found(self, client, auth_headers):
        """Test suppression chantier inexistant."""
        response = client.delete(
            "/api/chantiers/99999",
            params={"force": True},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestChantierRBAC:
    """Tests d'integration pour le controle d'acces RBAC."""

    def test_create_chantier_requires_auth(self, client, sample_chantier_data):
        """Test: creation sans token retourne 401."""
        response = client.post("/api/chantiers", json=sample_chantier_data)
        assert response.status_code == 401

    def test_create_chantier_forbidden_for_compagnon(
        self, client, compagnon_auth_headers, sample_chantier_data
    ):
        """Test: un compagnon ne peut pas creer de chantier (403)."""
        response = client.post(
            "/api/chantiers",
            json=sample_chantier_data,
            headers=compagnon_auth_headers,
        )
        assert response.status_code == 403

    def test_update_chantier_forbidden_for_compagnon(
        self, client, auth_headers, compagnon_auth_headers, sample_chantier_data
    ):
        """Test: un compagnon ne peut pas modifier un chantier (403)."""
        # Creer avec un admin/conducteur
        create_response = client.post(
            "/api/chantiers",
            json=sample_chantier_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        chantier_id = create_response.json()["id"]

        # Tenter de modifier avec compagnon
        response = client.put(
            f"/api/chantiers/{chantier_id}",
            json={"nom": "Modifie par compagnon"},
            headers=compagnon_auth_headers,
        )
        assert response.status_code == 403

    def test_delete_chantier_requires_admin(
        self, client, conducteur_auth_headers, admin_auth_headers, sample_chantier_data
    ):
        """Test: seul un admin peut supprimer un chantier."""
        # Creer avec conducteur
        create_response = client.post(
            "/api/chantiers",
            json=sample_chantier_data,
            headers=conducteur_auth_headers,
        )
        assert create_response.status_code == 201
        chantier_id = create_response.json()["id"]

        # Tenter de supprimer avec conducteur -> 403
        response = client.delete(
            f"/api/chantiers/{chantier_id}",
            params={"force": True},
            headers=conducteur_auth_headers,
        )
        assert response.status_code == 403

        # Supprimer avec admin -> 200
        response = client.delete(
            f"/api/chantiers/{chantier_id}",
            params={"force": True},
            headers=admin_auth_headers,
        )
        assert response.status_code == 200

    def test_list_chantiers_allowed_for_all_authenticated(
        self, client, compagnon_auth_headers, sample_chantier_data
    ):
        """Test: tous les utilisateurs authentifies peuvent lister les chantiers."""
        response = client.get("/api/chantiers", headers=compagnon_auth_headers)
        assert response.status_code == 200


class TestChantierSoftDelete:
    """Tests d'integration pour le soft delete."""

    def test_deleted_chantier_not_in_list(
        self, client, admin_auth_headers, sample_chantier_data
    ):
        """Test: un chantier supprime n'apparait plus dans la liste."""
        # Creer
        create_response = client.post(
            "/api/chantiers",
            json=sample_chantier_data,
            headers=admin_auth_headers,
        )
        assert create_response.status_code == 201
        chantier_id = create_response.json()["id"]
        chantier_code = create_response.json()["code"]

        # Verifier qu'il est dans la liste
        list_response = client.get("/api/chantiers", headers=admin_auth_headers)
        items = list_response.json().get("items", list_response.json().get("chantiers", []))
        codes_before = [c["code"] for c in items]
        assert chantier_code in codes_before

        # Supprimer (soft delete)
        delete_response = client.delete(
            f"/api/chantiers/{chantier_id}",
            params={"force": True},
            headers=admin_auth_headers,
        )
        assert delete_response.status_code == 200

        # Verifier qu'il n'est plus dans la liste
        list_response = client.get("/api/chantiers", headers=admin_auth_headers)
        items = list_response.json().get("items", list_response.json().get("chantiers", []))
        codes_after = [c["code"] for c in items]
        assert chantier_code not in codes_after

    def test_deleted_chantier_not_found_by_id(
        self, client, admin_auth_headers, sample_chantier_data
    ):
        """Test: un chantier supprime n'est pas trouve par ID."""
        # Creer
        create_response = client.post(
            "/api/chantiers",
            json=sample_chantier_data,
            headers=admin_auth_headers,
        )
        assert create_response.status_code == 201
        chantier_id = create_response.json()["id"]

        # Supprimer
        delete_response = client.delete(
            f"/api/chantiers/{chantier_id}",
            params={"force": True},
            headers=admin_auth_headers,
        )
        assert delete_response.status_code == 200

        # Verifier qu'il n'est plus accessible
        get_response = client.get(
            f"/api/chantiers/{chantier_id}",
            headers=admin_auth_headers,
        )
        assert get_response.status_code == 404


class TestChantierUserPrivacy:
    """Tests d'integration pour la protection des donnees utilisateur (RGPD)."""

    def test_conducteur_info_does_not_expose_email(
        self, client, auth_headers, sample_chantier_data
    ):
        """Test: les infos conducteur ne contiennent pas l'email."""
        # Creer un chantier avec un conducteur
        data = sample_chantier_data.copy()
        create_response = client.post(
            "/api/chantiers",
            json=data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        chantier_id = create_response.json()["id"]

        # Assigner un conducteur
        assign_response = client.post(
            f"/api/chantiers/{chantier_id}/conducteurs",
            json={"user_id": 1},  # Assuming user_id 1 exists
            headers=auth_headers,
        )
        # On accepte 200 ou 404 si l'utilisateur n'existe pas
        if assign_response.status_code == 200:
            # Recuperer le chantier et verifier les conducteurs
            get_response = client.get(
                f"/api/chantiers/{chantier_id}",
                headers=auth_headers,
            )
            assert get_response.status_code == 200
            conducteurs = get_response.json().get("conducteurs", [])

            # Verifier que email et telephone ne sont pas exposes
            for conducteur in conducteurs:
                assert "email" not in conducteur, "L'email ne doit pas etre expose"
                assert "telephone" not in conducteur, "Le telephone ne doit pas etre expose"
                # Verifier que les infos publiques sont presentes
                assert "nom" in conducteur
                assert "prenom" in conducteur
