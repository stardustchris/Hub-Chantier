"""Tests d'integration pour l'API des formulaires.

Ces tests verifient les endpoints FastAPI avec une vraie DB SQLite.
Selon CDC Section 8 - Formulaires Chantier (FOR-01 a FOR-11).
"""

import pytest


@pytest.fixture
def chantier_id(client, auth_headers):
    """Cree un chantier et retourne son ID."""
    response = client.post(
        "/api/chantiers",
        json={
            "nom": "Chantier pour Formulaires",
            "adresse": "789 Rue des Formulaires",
            "code": "F001",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, f"Chantier creation failed: {response.json()}"
    return response.json()["id"]


@pytest.fixture
def sample_template_data():
    """Donnees de test pour un template."""
    return {
        "nom": "Template Test Integration",
        "categorie": "intervention",
        "description": "Template pour tests d'integration",
        "champs": [
            {
                "nom": "commentaire",
                "label": "Commentaire",
                "type_champ": "texte_long",
                "obligatoire": False,
                "ordre": 1,
            },
            {
                "nom": "date_intervention",
                "label": "Date",
                "type_champ": "auto_date",
                "obligatoire": True,
                "ordre": 0,
            },
        ],
    }


class TestTemplateCreate:
    """Tests d'integration pour la creation de template (FOR-01)."""

    def test_create_template_success(self, client, auth_headers, sample_template_data):
        """Test creation de template reussie."""
        response = client.post(
            "/api/templates-formulaires",
            json=sample_template_data,
            headers=auth_headers,
        )

        assert response.status_code == 201, f"Creation failed: {response.json()}"
        data = response.json()
        assert data["nom"] == sample_template_data["nom"]
        assert data["categorie"] == sample_template_data["categorie"]
        assert "id" in data
        assert len(data["champs"]) == 2

    def test_create_template_unauthorized(self, client, sample_template_data):
        """Test creation sans authentification."""
        response = client.post("/api/templates-formulaires", json=sample_template_data)

        assert response.status_code == 401

    def test_create_template_duplicate_name(
        self, client, auth_headers, sample_template_data
    ):
        """Test creation avec nom duplique."""
        # Creer un premier template
        response1 = client.post(
            "/api/templates-formulaires",
            json=sample_template_data,
            headers=auth_headers,
        )
        assert response1.status_code == 201

        # Tenter de creer un doublon
        response2 = client.post(
            "/api/templates-formulaires",
            json=sample_template_data,
            headers=auth_headers,
        )
        assert response2.status_code == 409


class TestTemplateGet:
    """Tests d'integration pour la recuperation de template."""

    def test_get_template_by_id(self, client, auth_headers, sample_template_data):
        """Test recuperation par ID."""
        # Creer
        create_response = client.post(
            "/api/templates-formulaires",
            json=sample_template_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        template_id = create_response.json()["id"]

        # Recuperer
        response = client.get(
            f"/api/templates-formulaires/{template_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert str(response.json()["id"]) == str(template_id)

    def test_get_template_not_found(self, client, auth_headers):
        """Test recuperation template inexistant."""
        response = client.get("/api/templates-formulaires/99999", headers=auth_headers)

        assert response.status_code == 404


class TestTemplateList:
    """Tests d'integration pour la liste des templates."""

    def test_list_templates(self, client, auth_headers, sample_template_data):
        """Test liste des templates."""
        # Creer un template
        client.post(
            "/api/templates-formulaires",
            json=sample_template_data,
            headers=auth_headers,
        )

        # Lister
        response = client.get(
            "/api/templates-formulaires",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert "total" in data

    def test_list_templates_filter_by_categorie(
        self, client, auth_headers, sample_template_data
    ):
        """Test liste filtree par categorie."""
        # Creer
        client.post(
            "/api/templates-formulaires",
            json=sample_template_data,
            headers=auth_headers,
        )

        # Lister avec filtre
        response = client.get(
            "/api/templates-formulaires?categorie=intervention",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert all(t["categorie"] == "intervention" for t in data["templates"])


class TestTemplateUpdate:
    """Tests d'integration pour la mise a jour de template."""

    def test_update_template_success(self, client, auth_headers, sample_template_data):
        """Test mise a jour reussie."""
        # Creer
        create_response = client.post(
            "/api/templates-formulaires",
            json=sample_template_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        template_id = create_response.json()["id"]

        # Mettre a jour
        response = client.put(
            f"/api/templates-formulaires/{template_id}",
            json={"nom": "Template Modifie", "description": "Nouvelle description"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["nom"] == "Template Modifie"

    def test_update_template_not_found(self, client, auth_headers):
        """Test mise a jour template inexistant."""
        response = client.put(
            "/api/templates-formulaires/99999",
            json={"nom": "Test"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestTemplateDelete:
    """Tests d'integration pour la suppression de template."""

    def test_delete_template_success(self, client, auth_headers, sample_template_data):
        """Test suppression reussie."""
        # Creer
        create_response = client.post(
            "/api/templates-formulaires",
            json=sample_template_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        template_id = create_response.json()["id"]

        # Supprimer
        response = client.delete(
            f"/api/templates-formulaires/{template_id}",
            headers=auth_headers,
        )

        assert response.status_code in [200, 204]

        # Verifier suppression
        get_response = client.get(
            f"/api/templates-formulaires/{template_id}", headers=auth_headers
        )
        assert get_response.status_code == 404


class TestFormulaireCreate:
    """Tests d'integration pour la creation de formulaire (FOR-11)."""

    def test_create_formulaire_success(
        self, client, auth_headers, chantier_id, sample_template_data
    ):
        """Test creation de formulaire reussie."""
        # Creer un template
        template_response = client.post(
            "/api/templates-formulaires",
            json=sample_template_data,
            headers=auth_headers,
        )
        assert template_response.status_code == 201
        template_id = template_response.json()["id"]

        # Creer un formulaire
        response = client.post(
            "/api/formulaires",
            json={
                "template_id": template_id,
                "chantier_id": chantier_id,
                "latitude": 48.8566,
                "longitude": 2.3522,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201, f"Creation failed: {response.json()}"
        data = response.json()
        assert str(data["template_id"]) == str(template_id)
        assert str(data["chantier_id"]) == str(chantier_id)
        assert data["statut"] == "brouillon"

    def test_create_formulaire_unauthorized(
        self, client, chantier_id, sample_template_data, auth_headers
    ):
        """Test creation sans authentification."""
        # Creer un template
        template_response = client.post(
            "/api/templates-formulaires",
            json=sample_template_data,
            headers=auth_headers,
        )
        template_id = template_response.json()["id"]

        # Tenter de creer sans auth
        response = client.post(
            "/api/formulaires",
            json={"template_id": template_id, "chantier_id": chantier_id},
        )

        assert response.status_code == 401


class TestFormulaireGet:
    """Tests d'integration pour la recuperation de formulaire."""

    def test_get_formulaire_by_id(
        self, client, auth_headers, chantier_id, sample_template_data
    ):
        """Test recuperation par ID."""
        # Creer template
        template_response = client.post(
            "/api/templates-formulaires",
            json=sample_template_data,
            headers=auth_headers,
        )
        template_id = template_response.json()["id"]

        # Creer formulaire
        create_response = client.post(
            "/api/formulaires",
            json={"template_id": template_id, "chantier_id": chantier_id},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        formulaire_id = create_response.json()["id"]

        # Recuperer
        response = client.get(
            f"/api/formulaires/{formulaire_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert str(response.json()["id"]) == str(formulaire_id)

    def test_get_formulaire_not_found(self, client, auth_headers):
        """Test recuperation formulaire inexistant."""
        response = client.get("/api/formulaires/99999", headers=auth_headers)

        assert response.status_code == 404


class TestFormulaireList:
    """Tests d'integration pour la liste des formulaires."""

    def test_list_formulaires_by_chantier(
        self, client, auth_headers, chantier_id, sample_template_data
    ):
        """Test liste par chantier (FOR-10)."""
        # Creer template et formulaire
        template_response = client.post(
            "/api/templates-formulaires",
            json=sample_template_data,
            headers=auth_headers,
        )
        template_id = template_response.json()["id"]

        client.post(
            "/api/formulaires",
            json={"template_id": template_id, "chantier_id": chantier_id},
            headers=auth_headers,
        )

        # Lister par chantier
        response = client.get(
            f"/api/formulaires/chantier/{chantier_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "formulaires" in data or isinstance(data, list)


class TestFormulaireSubmit:
    """Tests d'integration pour la soumission de formulaire (FOR-07)."""

    def test_submit_formulaire_success(
        self, client, auth_headers, chantier_id, sample_template_data
    ):
        """Test soumission avec horodatage."""
        # Setup
        template_response = client.post(
            "/api/templates-formulaires",
            json=sample_template_data,
            headers=auth_headers,
        )
        template_id = template_response.json()["id"]

        create_response = client.post(
            "/api/formulaires",
            json={"template_id": template_id, "chantier_id": chantier_id},
            headers=auth_headers,
        )
        formulaire_id = create_response.json()["id"]

        # Soumettre
        response = client.post(
            f"/api/formulaires/{formulaire_id}/submit",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 200, f"Submit failed: {response.json()}"
        data = response.json()
        assert data["statut"] == "soumis"
        assert data["soumis_at"] is not None


class TestFormulaireHistory:
    """Tests d'integration pour l'historique (FOR-08)."""

    def test_get_formulaire_history(
        self, client, auth_headers, chantier_id, sample_template_data
    ):
        """Test recuperation de l'historique."""
        # Setup
        template_response = client.post(
            "/api/templates-formulaires",
            json=sample_template_data,
            headers=auth_headers,
        )
        template_id = template_response.json()["id"]

        create_response = client.post(
            "/api/formulaires",
            json={"template_id": template_id, "chantier_id": chantier_id},
            headers=auth_headers,
        )
        formulaire_id = create_response.json()["id"]

        # Historique
        response = client.get(
            f"/api/formulaires/{formulaire_id}/history",
            headers=auth_headers,
        )

        assert response.status_code == 200
