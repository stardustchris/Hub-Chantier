"""Tests d'integration pour l'API Signalements.

Ces tests verifient les endpoints FastAPI avec une vraie DB SQLite.
Selon CDC Section 10 - Signalements (SIG-01 a SIG-20).
"""

import pytest
from datetime import datetime, timedelta


class TestSignalementCreate:
    """Tests d'integration pour la creation de signalements (SIG-01)."""

    def test_create_signalement_success(self, client, auth_headers, sample_chantier_data):
        """Test creation reussie d'un signalement."""
        # D'abord creer un chantier
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        assert chantier_response.status_code == 201
        chantier_id = chantier_response.json()["id"]

        # Creer un signalement
        signalement_data = {
            "chantier_id": chantier_id,
            "titre": "Fuite d'eau detectee",
            "description": "Fuite au niveau du sous-sol, zone B",
            "priorite": "haute",
        }
        response = client.post(
            "/api/signalements", json=signalement_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["titre"] == "Fuite d'eau detectee"
        assert data["priorite"] == "haute"
        assert data["statut"] == "ouvert"
        assert data["chantier_id"] == chantier_id
        assert "id" in data

    def test_create_signalement_with_all_fields(self, client, auth_headers, sample_chantier_data):
        """Test creation avec tous les champs optionnels."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        date_resolution = (datetime.now() + timedelta(days=2)).isoformat()
        signalement_data = {
            "chantier_id": chantier_id,
            "titre": "Probleme electrique",
            "description": "Court-circuit tableau principal",
            "priorite": "critique",
            "date_resolution_souhaitee": date_resolution,
            "photo_url": "https://example.com/photo.jpg",
            "localisation": "Batiment A, Etage 2",
        }
        response = client.post(
            "/api/signalements", json=signalement_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["priorite"] == "critique"
        assert data["localisation"] == "Batiment A, Etage 2"
        assert data["photo_url"] == "https://example.com/photo.jpg"

    def test_create_signalement_invalid_priorite(self, client, auth_headers, sample_chantier_data):
        """Test creation avec priorite invalide."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        signalement_data = {
            "chantier_id": chantier_id,
            "titre": "Test",
            "description": "Description",
            "priorite": "invalide",
        }
        response = client.post(
            "/api/signalements", json=signalement_data, headers=auth_headers
        )

        assert response.status_code == 400

    def test_create_signalement_without_auth(self, client, sample_chantier_data):
        """Test creation sans authentification."""
        signalement_data = {
            "chantier_id": 1,
            "titre": "Test",
            "description": "Description",
        }
        response = client.post("/api/signalements", json=signalement_data)

        assert response.status_code == 401


class TestSignalementGet:
    """Tests d'integration pour la recuperation d'un signalement (SIG-02)."""

    def test_get_signalement_success(self, client, auth_headers, sample_chantier_data):
        """Test recuperation reussie."""
        # Creer un chantier et un signalement
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        create_response = client.post(
            "/api/signalements",
            json={
                "chantier_id": chantier_id,
                "titre": "Test signalement",
                "description": "Description test",
            },
            headers=auth_headers,
        )
        signalement_id = create_response.json()["id"]

        # Recuperer le signalement
        response = client.get(
            f"/api/signalements/{signalement_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == signalement_id
        assert data["titre"] == "Test signalement"

    def test_get_signalement_not_found(self, client, auth_headers):
        """Test recuperation signalement inexistant."""
        response = client.get("/api/signalements/99999", headers=auth_headers)

        assert response.status_code == 404


class TestSignalementList:
    """Tests d'integration pour la liste des signalements (SIG-03)."""

    def test_list_signalements_by_chantier(self, client, auth_headers, sample_chantier_data):
        """Test liste des signalements d'un chantier."""
        # Creer un chantier
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        # Creer plusieurs signalements
        for i in range(3):
            client.post(
                "/api/signalements",
                json={
                    "chantier_id": chantier_id,
                    "titre": f"Signalement {i}",
                    "description": f"Description {i}",
                },
                headers=auth_headers,
            )

        # Lister
        response = client.get(
            f"/api/signalements/chantier/{chantier_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["signalements"]) == 3

    def test_list_signalements_with_filter(self, client, auth_headers, sample_chantier_data):
        """Test liste avec filtres (statut, priorite)."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        # Creer des signalements avec differentes priorites
        client.post(
            "/api/signalements",
            json={
                "chantier_id": chantier_id,
                "titre": "Haute priorite",
                "description": "Desc",
                "priorite": "haute",
            },
            headers=auth_headers,
        )
        client.post(
            "/api/signalements",
            json={
                "chantier_id": chantier_id,
                "titre": "Basse priorite",
                "description": "Desc",
                "priorite": "basse",
            },
            headers=auth_headers,
        )

        # Filtrer par priorite haute
        response = client.get(
            f"/api/signalements/chantier/{chantier_id}",
            params={"priorite": "haute"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["signalements"][0]["priorite"] == "haute"


class TestSignalementSearch:
    """Tests d'integration pour la recherche de signalements (SIG-10, SIG-19, SIG-20)."""

    def test_search_signalements_global(self, client, auth_headers, sample_chantier_data):
        """Test recherche globale (vue Admin/Conducteur)."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        client.post(
            "/api/signalements",
            json={
                "chantier_id": chantier_id,
                "titre": "Fuite eau urgent",
                "description": "Description",
            },
            headers=auth_headers,
        )

        response = client.get(
            "/api/signalements",
            params={"query": "eau"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1


class TestSignalementUpdate:
    """Tests d'integration pour la mise a jour d'un signalement (SIG-04)."""

    def test_update_signalement_success(self, client, auth_headers, sample_chantier_data):
        """Test mise a jour reussie."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        create_response = client.post(
            "/api/signalements",
            json={
                "chantier_id": chantier_id,
                "titre": "Titre original",
                "description": "Description originale",
            },
            headers=auth_headers,
        )
        signalement_id = create_response.json()["id"]

        # Mettre a jour
        response = client.put(
            f"/api/signalements/{signalement_id}",
            json={
                "titre": "Titre modifie",
                "priorite": "haute",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["titre"] == "Titre modifie"
        assert data["priorite"] == "haute"

    def test_update_signalement_not_found(self, client, auth_headers):
        """Test mise a jour signalement inexistant."""
        response = client.put(
            "/api/signalements/99999",
            json={"titre": "Test"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestSignalementDelete:
    """Tests d'integration pour la suppression d'un signalement (SIG-05)."""

    def test_delete_signalement_as_admin(self, client, auth_headers, sample_chantier_data):
        """Test suppression en tant qu'admin."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        create_response = client.post(
            "/api/signalements",
            json={
                "chantier_id": chantier_id,
                "titre": "A supprimer",
                "description": "Description",
            },
            headers=auth_headers,
        )
        signalement_id = create_response.json()["id"]

        # Supprimer
        response = client.delete(
            f"/api/signalements/{signalement_id}", headers=auth_headers
        )

        assert response.status_code == 204

        # Verifier suppression
        get_response = client.get(
            f"/api/signalements/{signalement_id}", headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_delete_signalement_as_compagnon_forbidden(
        self, client, auth_headers, compagnon_auth_headers, sample_chantier_data
    ):
        """Test suppression en tant que compagnon (interdit)."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        create_response = client.post(
            "/api/signalements",
            json={
                "chantier_id": chantier_id,
                "titre": "Test",
                "description": "Description",
            },
            headers=auth_headers,
        )
        signalement_id = create_response.json()["id"]

        # Tenter de supprimer en tant que compagnon
        response = client.delete(
            f"/api/signalements/{signalement_id}", headers=compagnon_auth_headers
        )

        assert response.status_code == 403


class TestSignalementWorkflow:
    """Tests d'integration pour le workflow signalement (SIG-08, SIG-09)."""

    def test_workflow_ouvert_traite_cloture(self, client, auth_headers, sample_chantier_data):
        """Test workflow complet: Ouvert -> Traite -> Cloture."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        # Creer signalement (statut: ouvert)
        create_response = client.post(
            "/api/signalements",
            json={
                "chantier_id": chantier_id,
                "titre": "Workflow test",
                "description": "Description",
            },
            headers=auth_headers,
        )
        signalement_id = create_response.json()["id"]
        assert create_response.json()["statut"] == "ouvert"

        # Marquer comme traite (SIG-08)
        traite_response = client.post(
            f"/api/signalements/{signalement_id}/traiter",
            json={"commentaire": "Probleme resolu en remplacant le joint"},
            headers=auth_headers,
        )
        assert traite_response.status_code == 200
        assert traite_response.json()["statut"] == "traite"
        assert traite_response.json()["commentaire_traitement"] is not None

        # Cloturer (SIG-09)
        cloture_response = client.post(
            f"/api/signalements/{signalement_id}/cloturer",
            headers=auth_headers,
        )
        assert cloture_response.status_code == 200
        assert cloture_response.json()["statut"] == "cloture"

    def test_reouvrir_signalement(self, client, auth_headers, sample_chantier_data):
        """Test reouverture d'un signalement cloture."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        # Creer, traiter et cloturer
        create_response = client.post(
            "/api/signalements",
            json={
                "chantier_id": chantier_id,
                "titre": "Test reouvrir",
                "description": "Description",
            },
            headers=auth_headers,
        )
        signalement_id = create_response.json()["id"]

        client.post(
            f"/api/signalements/{signalement_id}/traiter",
            json={"commentaire": "Resolu"},
            headers=auth_headers,
        )
        client.post(
            f"/api/signalements/{signalement_id}/cloturer",
            headers=auth_headers,
        )

        # Reouvrir
        response = client.post(
            f"/api/signalements/{signalement_id}/reouvrir",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["statut"] == "ouvert"


class TestSignalementAssignation:
    """Tests d'integration pour l'assignation de signalements."""

    def test_assigner_signalement(self, client, auth_headers, sample_chantier_data, sample_user_data):
        """Test assignation d'un signalement a un utilisateur."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        # Creer un utilisateur a qui assigner
        user_response = client.post("/api/auth/register", json=sample_user_data)
        user_id = user_response.json()["user"]["id"]

        create_response = client.post(
            "/api/signalements",
            json={
                "chantier_id": chantier_id,
                "titre": "A assigner",
                "description": "Description",
            },
            headers=auth_headers,
        )
        signalement_id = create_response.json()["id"]

        # Assigner
        response = client.post(
            f"/api/signalements/{signalement_id}/assigner",
            params={"assigne_a": user_id},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["assigne_a"] == user_id


class TestSignalementReponses:
    """Tests d'integration pour les reponses aux signalements (SIG-06, SIG-07)."""

    def test_add_reponse(self, client, auth_headers, sample_chantier_data):
        """Test ajout d'une reponse a un signalement (SIG-07)."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        create_response = client.post(
            "/api/signalements",
            json={
                "chantier_id": chantier_id,
                "titre": "Test reponses",
                "description": "Description",
            },
            headers=auth_headers,
        )
        signalement_id = create_response.json()["id"]

        # Ajouter une reponse
        response = client.post(
            f"/api/signalements/{signalement_id}/reponses",
            json={
                "contenu": "J'ai verifie sur place, le probleme persiste",
                "photo_url": "https://example.com/photo_reponse.jpg",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["contenu"] == "J'ai verifie sur place, le probleme persiste"
        assert data["signalement_id"] == signalement_id

    def test_list_reponses(self, client, auth_headers, sample_chantier_data):
        """Test liste des reponses d'un signalement."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        create_response = client.post(
            "/api/signalements",
            json={
                "chantier_id": chantier_id,
                "titre": "Test list reponses",
                "description": "Description",
            },
            headers=auth_headers,
        )
        signalement_id = create_response.json()["id"]

        # Ajouter plusieurs reponses
        for i in range(3):
            client.post(
                f"/api/signalements/{signalement_id}/reponses",
                json={"contenu": f"Reponse {i}"},
                headers=auth_headers,
            )

        # Lister
        response = client.get(
            f"/api/signalements/{signalement_id}/reponses",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["reponses"]) == 3


class TestSignalementStatistiques:
    """Tests d'integration pour les statistiques (SIG-18)."""

    def test_get_statistiques(self, client, auth_headers, sample_chantier_data):
        """Test recuperation des statistiques."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        # Creer quelques signalements
        for priorite in ["haute", "moyenne", "basse"]:
            client.post(
                "/api/signalements",
                json={
                    "chantier_id": chantier_id,
                    "titre": f"Test stats {priorite}",
                    "description": "Description",
                    "priorite": priorite,
                },
                headers=auth_headers,
            )

        # Recuperer les statistiques
        response = client.get(
            "/api/signalements/stats/global",
            params={"chantier_id": chantier_id},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
        assert "par_priorite" in data
        assert "par_statut" in data


class TestSignalementAlertes:
    """Tests d'integration pour les alertes en retard (SIG-16)."""

    def test_get_signalements_en_retard(self, client, auth_headers, sample_chantier_data):
        """Test recuperation des signalements en retard."""
        chantier_response = client.post(
            "/api/chantiers", json=sample_chantier_data, headers=auth_headers
        )
        chantier_id = chantier_response.json()["id"]

        # Creer un signalement critique (delai 4h) sans date resolution
        client.post(
            "/api/signalements",
            json={
                "chantier_id": chantier_id,
                "titre": "Urgence critique",
                "description": "Description",
                "priorite": "critique",
            },
            headers=auth_headers,
        )

        # Recuperer les alertes
        response = client.get(
            "/api/signalements/alertes/en-retard",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # Le signalement critique devrait etre en retard apres 4h
        # Mais comme on vient de le creer, il ne devrait pas etre en retard
        assert "signalements" in data
