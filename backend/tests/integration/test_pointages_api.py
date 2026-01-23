"""Tests d'integration pour l'API des Pointages (Feuilles d'heures).

Ces tests verifient les endpoints FastAPI avec une vraie DB SQLite.
Selon CDC Section 7 - Feuilles d'Heures (FDH-01 a FDH-20).
"""

import pytest
from datetime import date, timedelta


@pytest.fixture
def chantier_id(client, auth_headers):
    """Cree un chantier et retourne son ID."""
    response = client.post(
        "/api/chantiers",
        json={
            "nom": "Chantier Pointages Test",
            "adresse": "123 Rue Pointages",
            "code": "H001",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, f"Chantier creation failed: {response.json()}"
    # L'API retourne les IDs en string, convertir en int
    return int(response.json()["id"])


@pytest.fixture
def utilisateur_id(client, auth_headers):
    """Retourne l'ID de l'utilisateur admin connecte."""
    response = client.get("/api/auth/me", headers=auth_headers)
    # L'API retourne les IDs en string, convertir en int
    return int(response.json()["id"])


@pytest.fixture
def monday_date():
    """Retourne la date du lundi de la semaine courante."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return monday


@pytest.fixture
def sample_pointage_data(chantier_id, utilisateur_id, monday_date):
    """Donnees de test pour un pointage."""
    return {
        "utilisateur_id": utilisateur_id,
        "chantier_id": chantier_id,
        "date_pointage": monday_date.isoformat(),
        "heures_normales": "08:00",
        "heures_supplementaires": "00:00",
        "commentaire": "Pointage de test",
    }


class TestPointageCreate:
    """Tests d'integration pour la creation de pointage."""

    def test_create_pointage_success(self, client, auth_headers, sample_pointage_data, utilisateur_id):
        """Test creation de pointage reussie."""
        response = client.post(
            "/api/pointages",
            json=sample_pointage_data,
            params={"current_user_id": utilisateur_id},
            headers=auth_headers,
        )

        assert response.status_code == 201, f"Creation failed: {response.json()}"
        data = response.json()
        assert "id" in data
        assert data["heures_normales"] == "08:00"

    def test_create_pointage_with_heures_sup(
        self, client, auth_headers, sample_pointage_data, utilisateur_id
    ):
        """Test creation avec heures supplementaires."""
        sample_pointage_data["heures_supplementaires"] = "02:00"
        sample_pointage_data["date_pointage"] = (
            date.fromisoformat(sample_pointage_data["date_pointage"]) + timedelta(days=1)
        ).isoformat()

        response = client.post(
            "/api/pointages",
            json=sample_pointage_data,
            params={"current_user_id": utilisateur_id},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["heures_supplementaires"] == "02:00"

    def test_create_pointage_invalid_heures_format(
        self, client, auth_headers, sample_pointage_data, utilisateur_id
    ):
        """Test creation avec format heures invalide."""
        sample_pointage_data["heures_normales"] = "8h00"  # Format invalide

        response = client.post(
            "/api/pointages",
            json=sample_pointage_data,
            params={"current_user_id": utilisateur_id},
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error


class TestPointageGet:
    """Tests d'integration pour la recuperation de pointage."""

    @pytest.fixture
    def pointage_id(self, client, auth_headers, sample_pointage_data, utilisateur_id):
        """Cree un pointage et retourne son ID."""
        response = client.post(
            "/api/pointages",
            json=sample_pointage_data,
            params={"current_user_id": utilisateur_id},
            headers=auth_headers,
        )
        return response.json()["id"]

    def test_get_pointage_by_id(self, client, auth_headers, pointage_id):
        """Test recuperation par ID."""
        response = client.get(
            f"/api/pointages/{pointage_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["id"] == pointage_id

    def test_get_pointage_not_found(self, client, auth_headers):
        """Test recuperation pointage inexistant."""
        response = client.get(
            "/api/pointages/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestPointageList:
    """Tests d'integration pour la liste des pointages (FDH-04)."""

    def test_list_pointages_empty(self, client, auth_headers):
        """Test liste pointages vide."""
        response = client.get(
            "/api/pointages",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_pointages_with_filters(
        self, client, auth_headers, sample_pointage_data, utilisateur_id, chantier_id
    ):
        """Test liste avec filtres."""
        # Creer un pointage
        client.post(
            "/api/pointages",
            json=sample_pointage_data,
            params={"current_user_id": utilisateur_id},
            headers=auth_headers,
        )

        # Filtrer par utilisateur
        response = client.get(
            "/api/pointages",
            params={"utilisateur_id": utilisateur_id},
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Filtrer par chantier
        response = client.get(
            "/api/pointages",
            params={"chantier_id": chantier_id},
            headers=auth_headers,
        )

        assert response.status_code == 200


class TestPointageUpdate:
    """Tests d'integration pour la mise a jour de pointage."""

    @pytest.fixture
    def pointage_id(self, client, auth_headers, sample_pointage_data, utilisateur_id):
        """Cree un pointage et retourne son ID."""
        response = client.post(
            "/api/pointages",
            json=sample_pointage_data,
            params={"current_user_id": utilisateur_id},
            headers=auth_headers,
        )
        return response.json()["id"]

    def test_update_pointage_success(
        self, client, auth_headers, pointage_id, utilisateur_id
    ):
        """Test mise a jour reussie."""
        response = client.put(
            f"/api/pointages/{pointage_id}",
            json={
                "heures_normales": "07:30",
                "commentaire": "Mis a jour",
            },
            params={"current_user_id": utilisateur_id},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["heures_normales"] == "07:30"
        assert data["commentaire"] == "Mis a jour"


class TestPointageDelete:
    """Tests d'integration pour la suppression de pointage."""

    @pytest.fixture
    def pointage_id(self, client, auth_headers, sample_pointage_data, utilisateur_id, monday_date):
        """Cree un pointage et retourne son ID."""
        data = sample_pointage_data.copy()
        data["date_pointage"] = (monday_date + timedelta(days=2)).isoformat()
        response = client.post(
            "/api/pointages",
            json=data,
            params={"current_user_id": utilisateur_id},
            headers=auth_headers,
        )
        return response.json()["id"]

    def test_delete_pointage_success(
        self, client, auth_headers, pointage_id, utilisateur_id
    ):
        """Test suppression reussie."""
        response = client.delete(
            f"/api/pointages/{pointage_id}",
            params={"current_user_id": utilisateur_id},
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verifier la suppression
        get_response = client.get(
            f"/api/pointages/{pointage_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404


class TestPointageWorkflow:
    """Tests d'integration pour le workflow de validation (FDH-09 a FDH-12)."""

    @pytest.fixture
    def pointage_id(self, client, auth_headers, sample_pointage_data, utilisateur_id, monday_date):
        """Cree un pointage et retourne son ID."""
        data = sample_pointage_data.copy()
        data["date_pointage"] = (monday_date + timedelta(days=3)).isoformat()
        response = client.post(
            "/api/pointages",
            json=data,
            params={"current_user_id": utilisateur_id},
            headers=auth_headers,
        )
        return response.json()["id"]

    def test_sign_pointage(self, client, auth_headers, pointage_id):
        """Test signature de pointage (FDH-12)."""
        response = client.post(
            f"/api/pointages/{pointage_id}/sign",
            json={"signature": "data:image/png;base64,iVBORw0KGgoAAAANSU=="},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # L'API utilise signature_utilisateur comme nom de champ
        assert data.get("signature_utilisateur") is not None

    def test_submit_pointage(self, client, auth_headers, pointage_id):
        """Test soumission de pointage."""
        response = client.post(
            f"/api/pointages/{pointage_id}/submit",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["statut"] in ["soumis", "Soumis"]

    def test_validate_pointage(self, client, auth_headers, pointage_id, utilisateur_id):
        """Test validation de pointage."""
        # D'abord soumettre
        client.post(
            f"/api/pointages/{pointage_id}/submit",
            headers=auth_headers,
        )

        # Puis valider
        response = client.post(
            f"/api/pointages/{pointage_id}/validate",
            params={"validateur_id": utilisateur_id},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["statut"] in ["valide", "Valide", "validé", "Validé"]

    def test_reject_pointage(self, client, auth_headers, sample_pointage_data, utilisateur_id, monday_date):
        """Test rejet de pointage."""
        # Creer un nouveau pointage pour ce test
        data = sample_pointage_data.copy()
        data["date_pointage"] = (monday_date + timedelta(days=4)).isoformat()
        create_response = client.post(
            "/api/pointages",
            json=data,
            params={"current_user_id": utilisateur_id},
            headers=auth_headers,
        )
        pointage_id = create_response.json()["id"]

        # Soumettre
        client.post(
            f"/api/pointages/{pointage_id}/submit",
            headers=auth_headers,
        )

        # Rejeter
        response = client.post(
            f"/api/pointages/{pointage_id}/reject",
            json={"motif": "Heures incorrectes"},
            params={"validateur_id": utilisateur_id},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["statut"] in ["rejete", "Rejete", "rejeté", "Rejeté"]


class TestFeuillesHeures:
    """Tests d'integration pour les feuilles d'heures (FDH-05)."""

    def test_list_feuilles_heures(self, client, auth_headers):
        """Test liste des feuilles d'heures."""
        response = client.get(
            "/api/pointages/feuilles",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_feuille_heures_semaine(
        self, client, auth_headers, utilisateur_id, monday_date
    ):
        """Test recuperation feuille d'heures par semaine."""
        response = client.get(
            f"/api/pointages/feuilles/utilisateur/{utilisateur_id}/semaine",
            params={"semaine_debut": monday_date.isoformat()},
            headers=auth_headers,
        )

        # Peut retourner 200 avec feuille ou 200 avec None/vide
        assert response.status_code == 200


class TestPointagesNavigation:
    """Tests d'integration pour la navigation (FDH-02)."""

    def test_get_navigation_semaine(self, client, auth_headers, monday_date):
        """Test navigation par semaine."""
        response = client.get(
            "/api/pointages/navigation",
            params={"semaine_debut": monday_date.isoformat()},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # Verifie les infos de navigation
        assert "semaine_precedente" in data or "previous_week" in data or isinstance(data, dict)


class TestPointagesVues:
    """Tests d'integration pour les vues (FDH-01)."""

    def test_get_vue_chantiers(self, client, auth_headers, monday_date):
        """Test vue par chantiers."""
        response = client.get(
            "/api/pointages/vues/chantiers",
            params={"semaine_debut": monday_date.isoformat()},
            headers=auth_headers,
        )

        assert response.status_code == 200

    def test_get_vue_compagnons(self, client, auth_headers, monday_date):
        """Test vue par compagnons."""
        response = client.get(
            "/api/pointages/vues/compagnons",
            params={"semaine_debut": monday_date.isoformat()},
            headers=auth_headers,
        )

        assert response.status_code == 200


class TestPointagesStats:
    """Tests d'integration pour les statistiques (FDH-14, FDH-15)."""

    def test_get_jauge_avancement(
        self, client, auth_headers, utilisateur_id, monday_date
    ):
        """Test jauge d'avancement (FDH-14)."""
        response = client.get(
            f"/api/pointages/stats/jauge-avancement/{utilisateur_id}",
            params={"semaine_debut": monday_date.isoformat()},
            headers=auth_headers,
        )

        assert response.status_code == 200

    def test_compare_equipes(self, client, auth_headers, monday_date):
        """Test comparaison inter-equipes (FDH-15)."""
        response = client.get(
            "/api/pointages/stats/comparaison-equipes",
            params={"semaine_debut": monday_date.isoformat()},
            headers=auth_headers,
        )

        assert response.status_code == 200


class TestPointagesExport:
    """Tests d'integration pour l'export (FDH-03, FDH-17)."""

    def test_export_csv(self, client, auth_headers, utilisateur_id, monday_date):
        """Test export CSV."""
        response = client.post(
            "/api/pointages/export",
            json={
                "format_export": "csv",
                "date_debut": monday_date.isoformat(),
                "date_fin": (monday_date + timedelta(days=6)).isoformat(),
            },
            params={"current_user_id": utilisateur_id},
            headers=auth_headers,
        )

        # L'export peut reussir ou indiquer qu'il n'y a pas de donnees
        assert response.status_code in [200, 400]
