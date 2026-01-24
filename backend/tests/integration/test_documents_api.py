"""Tests d'integration pour l'API Documents (GED).

Ces tests verifient les endpoints FastAPI avec une vraie DB SQLite.
Selon CDC Section 9 - Gestion Documentaire (GED-01 a GED-17).
"""

import io


class TestDossierCreate:
    """Tests d'integration pour la creation de dossiers (GED-02)."""

    def test_create_dossier_success(self, client, auth_headers, sample_chantier_data):
        """Test creation reussie d'un dossier."""
        # Creer un chantier
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        assert chantier_response.status_code == 201
        chantier_id = chantier_response.json()["id"]

        # Creer un dossier
        dossier_data = {
            "chantier_id": chantier_id,
            "nom": "01 - Plans",
            "type_dossier": "plans",
            "niveau_acces": "compagnon",
        }
        response = client.post(
            "/api/documents/dossiers", json=dossier_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["nom"] == "01 - Plans"
        assert data["chantier_id"] == chantier_id
        assert data["niveau_acces"] == "compagnon"

    def test_create_dossier_with_parent(self, client, auth_headers, sample_chantier_data):
        """Test creation d'un sous-dossier."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        # Creer dossier parent
        parent_response = client.post(
            "/api/documents/dossiers",
            json={"chantier_id": chantier_id, "nom": "Plans"},
            headers=auth_headers,
        )
        parent_id = parent_response.json()["id"]

        # Creer sous-dossier
        response = client.post(
            "/api/documents/dossiers",
            json={
                "chantier_id": chantier_id,
                "nom": "Plans Beton",
                "parent_id": parent_id,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["parent_id"] == parent_id

    def test_create_dossier_duplicate_name(self, client, auth_headers, sample_chantier_data):
        """Test creation avec nom duplique (meme parent)."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        dossier_data = {"chantier_id": chantier_id, "nom": "Documents"}

        # Premier dossier
        client.post("/api/documents/dossiers", json=dossier_data, headers=auth_headers)

        # Deuxieme avec meme nom
        response = client.post(
            "/api/documents/dossiers", json=dossier_data, headers=auth_headers
        )

        assert response.status_code == 400


class TestDossierGet:
    """Tests d'integration pour la recuperation d'un dossier."""

    def test_get_dossier_success(self, client, auth_headers, sample_chantier_data):
        """Test recuperation reussie."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        create_response = client.post(
            "/api/documents/dossiers",
            json={"chantier_id": chantier_id, "nom": "Test Dossier"},
            headers=auth_headers,
        )
        dossier_id = create_response.json()["id"]

        response = client.get(
            f"/api/documents/dossiers/{dossier_id}", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["id"] == dossier_id
        assert response.json()["nom"] == "Test Dossier"

    def test_get_dossier_not_found(self, client, auth_headers):
        """Test recuperation dossier inexistant."""
        response = client.get("/api/documents/dossiers/99999", headers=auth_headers)

        assert response.status_code == 404


class TestDossierList:
    """Tests d'integration pour la liste des dossiers."""

    def test_list_dossiers_by_chantier(self, client, auth_headers, sample_chantier_data):
        """Test liste des dossiers d'un chantier."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        # Creer plusieurs dossiers
        for nom in ["Plans", "Documents Admin", "Securite"]:
            client.post(
                "/api/documents/dossiers",
                json={"chantier_id": chantier_id, "nom": nom},
                headers=auth_headers,
            )

        response = client.get(
            f"/api/documents/chantiers/{chantier_id}/dossiers", headers=auth_headers
        )

        assert response.status_code == 200
        assert len(response.json()) == 3


class TestDossierUpdate:
    """Tests d'integration pour la mise a jour d'un dossier."""

    def test_update_dossier_success(self, client, auth_headers, sample_chantier_data):
        """Test mise a jour reussie."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        create_response = client.post(
            "/api/documents/dossiers",
            json={"chantier_id": chantier_id, "nom": "Ancien Nom"},
            headers=auth_headers,
        )
        dossier_id = create_response.json()["id"]

        response = client.put(
            f"/api/documents/dossiers/{dossier_id}",
            json={"nom": "Nouveau Nom", "niveau_acces": "chef_chantier"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["nom"] == "Nouveau Nom"
        assert response.json()["niveau_acces"] == "chef_chantier"


class TestDossierDelete:
    """Tests d'integration pour la suppression d'un dossier."""

    def test_delete_dossier_empty(self, client, auth_headers, sample_chantier_data):
        """Test suppression dossier vide."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        create_response = client.post(
            "/api/documents/dossiers",
            json={"chantier_id": chantier_id, "nom": "A Supprimer"},
            headers=auth_headers,
        )
        dossier_id = create_response.json()["id"]

        response = client.delete(
            f"/api/documents/dossiers/{dossier_id}", headers=auth_headers
        )

        assert response.status_code == 204


class TestArborescence:
    """Tests d'integration pour l'arborescence (GED-02)."""

    def test_init_arborescence(self, client, auth_headers, sample_chantier_data):
        """Test initialisation arborescence type."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        response = client.post(
            f"/api/documents/chantiers/{chantier_id}/init-arborescence",
            headers=auth_headers,
        )

        assert response.status_code == 200
        dossiers = response.json()
        # Devrait creer plusieurs dossiers de base
        assert len(dossiers) >= 5
        noms = [d["nom"] for d in dossiers]
        assert any("Plan" in nom for nom in noms)

    def test_get_arborescence(self, client, auth_headers, sample_chantier_data):
        """Test recuperation arborescence complete."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        # Initialiser l'arborescence
        client.post(
            f"/api/documents/chantiers/{chantier_id}/init-arborescence",
            headers=auth_headers,
        )

        response = client.get(
            f"/api/documents/chantiers/{chantier_id}/arborescence",
            headers=auth_headers,
        )

        assert response.status_code == 200


class TestDocumentUpload:
    """Tests d'integration pour l'upload de documents (GED-06, GED-07, GED-08)."""

    def test_upload_document_success(self, client, auth_headers, sample_chantier_data):
        """Test upload reussi d'un document."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        dossier_response = client.post(
            "/api/documents/dossiers",
            json={"chantier_id": chantier_id, "nom": "Plans"},
            headers=auth_headers,
        )
        dossier_id = dossier_response.json()["id"]

        # Creer un fichier fictif
        file_content = b"Contenu du fichier PDF de test"
        files = {"file": ("test_plan.pdf", io.BytesIO(file_content), "application/pdf")}

        response = client.post(
            f"/api/documents/dossiers/{dossier_id}/documents",
            params={"chantier_id": chantier_id},
            files=files,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["nom"] == "test_plan.pdf"
        assert data["dossier_id"] == dossier_id


class TestDocumentGet:
    """Tests d'integration pour la recuperation d'un document."""

    def test_get_document_success(self, client, auth_headers, sample_chantier_data):
        """Test recuperation reussie d'un document."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        dossier_response = client.post(
            "/api/documents/dossiers",
            json={"chantier_id": chantier_id, "nom": "Test"},
            headers=auth_headers,
        )
        dossier_id = dossier_response.json()["id"]

        # Upload
        file_content = b"Test content"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        upload_response = client.post(
            f"/api/documents/dossiers/{dossier_id}/documents",
            params={"chantier_id": chantier_id},
            files=files,
            headers=auth_headers,
        )
        document_id = upload_response.json()["id"]

        # Get
        response = client.get(
            f"/api/documents/documents/{document_id}", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["id"] == document_id

    def test_get_document_not_found(self, client, auth_headers):
        """Test recuperation document inexistant."""
        response = client.get("/api/documents/documents/99999", headers=auth_headers)

        assert response.status_code == 404


class TestDocumentList:
    """Tests d'integration pour la liste des documents (GED-03)."""

    def test_list_documents_by_dossier(self, client, auth_headers, sample_chantier_data):
        """Test liste des documents d'un dossier."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        dossier_response = client.post(
            "/api/documents/dossiers",
            json={"chantier_id": chantier_id, "nom": "Test"},
            headers=auth_headers,
        )
        dossier_id = dossier_response.json()["id"]

        # Upload plusieurs documents
        for i in range(3):
            files = {"file": (f"doc{i}.txt", io.BytesIO(b"content"), "text/plain")}
            client.post(
                f"/api/documents/dossiers/{dossier_id}/documents",
                params={"chantier_id": chantier_id},
                files=files,
                headers=auth_headers,
            )

        response = client.get(
            f"/api/documents/dossiers/{dossier_id}/documents", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3


class TestDocumentSearch:
    """Tests d'integration pour la recherche de documents."""

    def test_search_documents(self, client, auth_headers, sample_chantier_data):
        """Test recherche de documents."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        dossier_response = client.post(
            "/api/documents/dossiers",
            json={"chantier_id": chantier_id, "nom": "Plans"},
            headers=auth_headers,
        )
        dossier_id = dossier_response.json()["id"]

        # Upload document
        files = {"file": ("plan_beton.pdf", io.BytesIO(b"content"), "application/pdf")}
        client.post(
            f"/api/documents/dossiers/{dossier_id}/documents",
            params={"chantier_id": chantier_id},
            files=files,
            headers=auth_headers,
        )

        response = client.get(
            f"/api/documents/chantiers/{chantier_id}/documents/search",
            params={"query": "beton"},
            headers=auth_headers,
        )

        assert response.status_code == 200


class TestDocumentUpdate:
    """Tests d'integration pour la mise a jour d'un document (GED-13)."""

    def test_update_document_success(self, client, auth_headers, sample_chantier_data):
        """Test mise a jour reussie."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        dossier_response = client.post(
            "/api/documents/dossiers",
            json={"chantier_id": chantier_id, "nom": "Test"},
            headers=auth_headers,
        )
        dossier_id = dossier_response.json()["id"]

        # Upload
        files = {"file": ("old_name.txt", io.BytesIO(b"content"), "text/plain")}
        upload_response = client.post(
            f"/api/documents/dossiers/{dossier_id}/documents",
            params={"chantier_id": chantier_id},
            files=files,
            headers=auth_headers,
        )
        document_id = upload_response.json()["id"]

        # Update
        response = client.put(
            f"/api/documents/documents/{document_id}",
            json={"nom": "new_name.txt", "description": "Description ajoutee"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["nom"] == "new_name.txt"
        assert response.json()["description"] == "Description ajoutee"


class TestDocumentDelete:
    """Tests d'integration pour la suppression d'un document (GED-13)."""

    def test_delete_document_success(self, client, auth_headers, sample_chantier_data):
        """Test suppression reussie."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        dossier_response = client.post(
            "/api/documents/dossiers",
            json={"chantier_id": chantier_id, "nom": "Test"},
            headers=auth_headers,
        )
        dossier_id = dossier_response.json()["id"]

        # Upload
        files = {"file": ("to_delete.txt", io.BytesIO(b"content"), "text/plain")}
        upload_response = client.post(
            f"/api/documents/dossiers/{dossier_id}/documents",
            params={"chantier_id": chantier_id},
            files=files,
            headers=auth_headers,
        )
        document_id = upload_response.json()["id"]

        # Delete
        response = client.delete(
            f"/api/documents/documents/{document_id}", headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(
            f"/api/documents/documents/{document_id}", headers=auth_headers
        )
        assert get_response.status_code == 404


class TestDocumentDownload:
    """Tests d'integration pour le telechargement de documents."""

    def test_download_document(self, client, auth_headers, sample_chantier_data):
        """Test telechargement d'un document."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        dossier_response = client.post(
            "/api/documents/dossiers",
            json={"chantier_id": chantier_id, "nom": "Test"},
            headers=auth_headers,
        )
        dossier_id = dossier_response.json()["id"]

        # Upload
        files = {"file": ("download_test.txt", io.BytesIO(b"content"), "text/plain")}
        upload_response = client.post(
            f"/api/documents/dossiers/{dossier_id}/documents",
            params={"chantier_id": chantier_id},
            files=files,
            headers=auth_headers,
        )
        document_id = upload_response.json()["id"]

        # Download
        response = client.get(
            f"/api/documents/documents/{document_id}/download", headers=auth_headers
        )

        assert response.status_code == 200
        assert "url" in response.json() or "filename" in response.json()


class TestDocumentPreview:
    """Tests d'integration pour la previsualisation (GED-17)."""

    def test_get_document_preview(self, client, auth_headers, sample_chantier_data):
        """Test recuperation info previsualisation."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        dossier_response = client.post(
            "/api/documents/dossiers",
            json={"chantier_id": chantier_id, "nom": "Test"},
            headers=auth_headers,
        )
        dossier_id = dossier_response.json()["id"]

        # Upload PDF
        files = {"file": ("preview_test.pdf", io.BytesIO(b"%PDF-1.4 content"), "application/pdf")}
        upload_response = client.post(
            f"/api/documents/dossiers/{dossier_id}/documents",
            params={"chantier_id": chantier_id},
            files=files,
            headers=auth_headers,
        )
        document_id = upload_response.json()["id"]

        # Preview info
        response = client.get(
            f"/api/documents/documents/{document_id}/preview", headers=auth_headers
        )

        assert response.status_code == 200
        assert "can_preview" in response.json()


class TestAutorisations:
    """Tests d'integration pour les autorisations (GED-04, GED-05, GED-10)."""

    def test_create_autorisation_dossier(
        self, client, auth_headers, sample_chantier_data, sample_user_data
    ):
        """Test creation autorisation sur dossier."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        dossier_response = client.post(
            "/api/documents/dossiers",
            json={"chantier_id": chantier_id, "nom": "Confidentiel"},
            headers=auth_headers,
        )
        dossier_id = dossier_response.json()["id"]

        # Creer utilisateur
        user_response = client.post("/api/auth/register", json=sample_user_data)
        user_id = user_response.json()["user"]["id"]

        # Creer autorisation
        response = client.post(
            "/api/documents/autorisations",
            json={
                "user_id": user_id,
                "type_autorisation": "lecture",
                "dossier_id": dossier_id,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["user_id"] == user_id
        assert response.json()["dossier_id"] == dossier_id

    def test_list_autorisations_dossier(
        self, client, auth_headers, sample_chantier_data, sample_user_data
    ):
        """Test liste autorisations d'un dossier."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        dossier_response = client.post(
            "/api/documents/dossiers",
            json={"chantier_id": chantier_id, "nom": "Test"},
            headers=auth_headers,
        )
        dossier_id = dossier_response.json()["id"]

        user_response = client.post("/api/auth/register", json=sample_user_data)
        user_id = user_response.json()["user"]["id"]

        # Creer autorisation
        client.post(
            "/api/documents/autorisations",
            json={
                "user_id": user_id,
                "type_autorisation": "lecture",
                "dossier_id": dossier_id,
            },
            headers=auth_headers,
        )

        response = client.get(
            f"/api/documents/dossiers/{dossier_id}/autorisations", headers=auth_headers
        )

        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_revoke_autorisation(
        self, client, auth_headers, sample_chantier_data, sample_user_data
    ):
        """Test revocation d'une autorisation."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        dossier_response = client.post(
            "/api/documents/dossiers",
            json={"chantier_id": chantier_id, "nom": "Test"},
            headers=auth_headers,
        )
        dossier_id = dossier_response.json()["id"]

        user_response = client.post("/api/auth/register", json=sample_user_data)
        user_id = user_response.json()["user"]["id"]

        # Creer autorisation
        auth_response = client.post(
            "/api/documents/autorisations",
            json={
                "user_id": user_id,
                "type_autorisation": "lecture",
                "dossier_id": dossier_id,
            },
            headers=auth_headers,
        )
        autorisation_id = auth_response.json()["id"]

        # Revoquer
        response = client.delete(
            f"/api/documents/autorisations/{autorisation_id}", headers=auth_headers
        )

        assert response.status_code == 204
