"""Tests d'integration pour l'API du planning de charge.

Ces tests verifient les endpoints FastAPI avec une vraie DB SQLite.
Selon CDC Section 6 - Planning de Charge (PDC-01 a PDC-17).
"""

import pytest
from datetime import datetime, timedelta


class TestPlanningChargeEndpoints:
    """Tests d'integration pour les endpoints du planning de charge."""

    def _get_current_week_code(self):
        """Retourne le code de la semaine courante au format SXX-YYYY."""
        today = datetime.now()
        week_number = today.isocalendar()[1]
        year = today.year
        return f"S{week_number:02d}-{year}"

    def _get_week_range(self, weeks_ahead=4):
        """Retourne les codes de debut et fin pour une plage de semaines."""
        today = datetime.now()
        week_start = today.isocalendar()[1]
        year_start = today.year

        # Fin = semaine courante + weeks_ahead
        end_date = today + timedelta(weeks=weeks_ahead)
        week_end = end_date.isocalendar()[1]
        year_end = end_date.year

        return (
            f"S{week_start:02d}-{year_start}",
            f"S{week_end:02d}-{year_end}",
        )

    def test_get_planning_charge_requires_auth(self, client):
        """Test: lecture du planning sans token retourne 401."""
        semaine_debut, semaine_fin = self._get_week_range()
        response = client.get(
            "/api/planning-charge",
            params={
                "semaine_debut": semaine_debut,
                "semaine_fin": semaine_fin,
            },
        )
        assert response.status_code == 401

    def test_get_planning_charge_forbidden_for_compagnon(
        self, client, compagnon_auth_headers
    ):
        """Test: un compagnon ne peut pas acceder au planning (403)."""
        semaine_debut, semaine_fin = self._get_week_range()
        response = client.get(
            "/api/planning-charge",
            params={
                "semaine_debut": semaine_debut,
                "semaine_fin": semaine_fin,
            },
            headers=compagnon_auth_headers,
        )
        assert response.status_code == 403

    def test_get_planning_charge_allowed_for_chef_chantier(
        self, client, chef_chantier_auth_headers
    ):
        """Test: un chef de chantier peut acceder au planning (200)."""
        semaine_debut, semaine_fin = self._get_week_range()
        response = client.get(
            "/api/planning-charge",
            params={
                "semaine_debut": semaine_debut,
                "semaine_fin": semaine_fin,
            },
            headers=chef_chantier_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "chantiers" in data
        assert "semaines" in data
        assert "footer" in data
        assert "total_chantiers" in data

    def test_get_planning_charge_allowed_for_conducteur(
        self, client, conducteur_auth_headers
    ):
        """Test: un conducteur peut acceder au planning (200)."""
        semaine_debut, semaine_fin = self._get_week_range()
        response = client.get(
            "/api/planning-charge",
            params={
                "semaine_debut": semaine_debut,
                "semaine_fin": semaine_fin,
            },
            headers=conducteur_auth_headers,
        )
        assert response.status_code == 200

    def test_get_planning_charge_allowed_for_admin(self, client, admin_auth_headers):
        """Test: un admin peut acceder au planning (200)."""
        semaine_debut, semaine_fin = self._get_week_range()
        response = client.get(
            "/api/planning-charge",
            params={
                "semaine_debut": semaine_debut,
                "semaine_fin": semaine_fin,
            },
            headers=admin_auth_headers,
        )
        assert response.status_code == 200


class TestBesoinCRUD:
    """Tests CRUD pour les besoins de charge."""

    def _get_current_week_code(self):
        """Retourne le code de la semaine courante au format SXX-YYYY."""
        today = datetime.now()
        week_number = today.isocalendar()[1]
        year = today.year
        return f"S{week_number:02d}-{year}"

    def _create_test_chantier(self, client, auth_headers):
        """Cree un chantier de test et retourne son ID."""
        import random
        code = f"P{random.randint(100, 999)}"
        response = client.post(
            "/api/chantiers",
            json={
                "nom": "Chantier Planning Test",
                "adresse": "123 Rue Test",
                "code": code,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201, f"Failed to create chantier: {response.json()}"
        return response.json()["id"]

    def test_create_besoin_requires_auth(self, client):
        """Test: creation de besoin sans token retourne 401."""
        response = client.post(
            "/api/planning-charge/besoins",
            json={
                "chantier_id": 1,
                "semaine_code": self._get_current_week_code(),
                "type_metier": "macon",
                "besoin_heures": 35.0,
            },
        )
        assert response.status_code == 401

    def test_create_besoin_forbidden_for_compagnon(
        self, client, compagnon_auth_headers, admin_auth_headers
    ):
        """Test: un compagnon ne peut pas creer de besoin (403)."""
        chantier_id = self._create_test_chantier(client, admin_auth_headers)

        response = client.post(
            "/api/planning-charge/besoins",
            json={
                "chantier_id": chantier_id,
                "semaine_code": self._get_current_week_code(),
                "type_metier": "macon",
                "besoin_heures": 35.0,
            },
            headers=compagnon_auth_headers,
        )
        assert response.status_code == 403

    def test_create_besoin_forbidden_for_chef_chantier(
        self, client, chef_chantier_auth_headers, admin_auth_headers
    ):
        """Test: un chef de chantier ne peut pas creer de besoin (403)."""
        chantier_id = self._create_test_chantier(client, admin_auth_headers)

        response = client.post(
            "/api/planning-charge/besoins",
            json={
                "chantier_id": chantier_id,
                "semaine_code": self._get_current_week_code(),
                "type_metier": "macon",
                "besoin_heures": 35.0,
            },
            headers=chef_chantier_auth_headers,
        )
        assert response.status_code == 403

    def test_create_besoin_allowed_for_conducteur(
        self, client, conducteur_auth_headers
    ):
        """Test: un conducteur peut creer un besoin (201)."""
        chantier_id = self._create_test_chantier(client, conducteur_auth_headers)

        response = client.post(
            "/api/planning-charge/besoins",
            json={
                "chantier_id": chantier_id,
                "semaine_code": self._get_current_week_code(),
                "type_metier": "macon",
                "besoin_heures": 35.0,
            },
            headers=conducteur_auth_headers,
        )
        assert response.status_code == 201, f"Creation failed: {response.json()}"
        data = response.json()
        # chantier_id can be returned as int or string depending on serialization
        assert str(data["chantier_id"]) == str(chantier_id)
        assert data["type_metier"] == "macon"
        assert data["besoin_heures"] == 35.0
        assert "id" in data

    def test_create_besoin_allowed_for_admin(self, client, admin_auth_headers):
        """Test: un admin peut creer un besoin (201)."""
        chantier_id = self._create_test_chantier(client, admin_auth_headers)

        response = client.post(
            "/api/planning-charge/besoins",
            json={
                "chantier_id": chantier_id,
                "semaine_code": self._get_current_week_code(),
                "type_metier": "coffreur",
                "besoin_heures": 70.0,
                "note": "Urgence pour phase gros oeuvre",
            },
            headers=admin_auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type_metier"] == "coffreur"
        assert data["besoin_heures"] == 70.0
        assert data["note"] == "Urgence pour phase gros oeuvre"

    def test_create_besoin_duplicate_returns_409(self, client, admin_auth_headers):
        """Test: creation d'un besoin en double retourne 409."""
        chantier_id = self._create_test_chantier(client, admin_auth_headers)
        week_code = self._get_current_week_code()

        # Premier besoin
        response1 = client.post(
            "/api/planning-charge/besoins",
            json={
                "chantier_id": chantier_id,
                "semaine_code": week_code,
                "type_metier": "electricien",
                "besoin_heures": 20.0,
            },
            headers=admin_auth_headers,
        )
        assert response1.status_code == 201

        # Deuxieme besoin identique
        response2 = client.post(
            "/api/planning-charge/besoins",
            json={
                "chantier_id": chantier_id,
                "semaine_code": week_code,
                "type_metier": "electricien",
                "besoin_heures": 30.0,
            },
            headers=admin_auth_headers,
        )
        assert response2.status_code == 409

    def test_create_besoin_invalid_semaine_returns_422(self, client, admin_auth_headers):
        """Test: code semaine invalide retourne 422 (validation error)."""
        chantier_id = self._create_test_chantier(client, admin_auth_headers)

        response = client.post(
            "/api/planning-charge/besoins",
            json={
                "chantier_id": chantier_id,
                "semaine_code": "INVALID",
                "type_metier": "macon",
                "besoin_heures": 35.0,
            },
            headers=admin_auth_headers,
        )
        # FastAPI returns 422 for validation errors
        assert response.status_code in [400, 422]

    def test_update_besoin_success(self, client, admin_auth_headers):
        """Test: mise a jour d'un besoin reussie."""
        chantier_id = self._create_test_chantier(client, admin_auth_headers)

        # Creer
        create_response = client.post(
            "/api/planning-charge/besoins",
            json={
                "chantier_id": chantier_id,
                "semaine_code": self._get_current_week_code(),
                "type_metier": "macon",
                "besoin_heures": 35.0,
            },
            headers=admin_auth_headers,
        )
        assert create_response.status_code == 201
        besoin_id = create_response.json()["id"]

        # Mettre a jour
        update_response = client.put(
            f"/api/planning-charge/besoins/{besoin_id}",
            json={
                "besoin_heures": 70.0,
                "note": "Doublement des effectifs",
            },
            headers=admin_auth_headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["besoin_heures"] == 70.0
        assert update_response.json()["note"] == "Doublement des effectifs"

    def test_update_besoin_not_found(self, client, admin_auth_headers):
        """Test: mise a jour d'un besoin inexistant retourne 404."""
        response = client.put(
            "/api/planning-charge/besoins/99999",
            json={"besoin_heures": 50.0},
            headers=admin_auth_headers,
        )
        assert response.status_code == 404

    def test_update_besoin_forbidden_for_chef_chantier(
        self, client, chef_chantier_auth_headers, admin_auth_headers
    ):
        """Test: un chef de chantier ne peut pas modifier un besoin (403)."""
        chantier_id = self._create_test_chantier(client, admin_auth_headers)

        # Creer avec admin
        create_response = client.post(
            "/api/planning-charge/besoins",
            json={
                "chantier_id": chantier_id,
                "semaine_code": self._get_current_week_code(),
                "type_metier": "macon",
                "besoin_heures": 35.0,
            },
            headers=admin_auth_headers,
        )
        assert create_response.status_code == 201
        besoin_id = create_response.json()["id"]

        # Tenter de modifier avec chef chantier
        update_response = client.put(
            f"/api/planning-charge/besoins/{besoin_id}",
            json={"besoin_heures": 70.0},
            headers=chef_chantier_auth_headers,
        )
        assert update_response.status_code == 403

    def test_delete_besoin_success(self, client, admin_auth_headers):
        """Test: suppression d'un besoin reussie (soft delete)."""
        chantier_id = self._create_test_chantier(client, admin_auth_headers)

        # Creer
        create_response = client.post(
            "/api/planning-charge/besoins",
            json={
                "chantier_id": chantier_id,
                "semaine_code": self._get_current_week_code(),
                "type_metier": "macon",
                "besoin_heures": 35.0,
            },
            headers=admin_auth_headers,
        )
        assert create_response.status_code == 201
        besoin_id = create_response.json()["id"]

        # Supprimer
        delete_response = client.delete(
            f"/api/planning-charge/besoins/{besoin_id}",
            headers=admin_auth_headers,
        )
        assert delete_response.status_code == 204

        # Verifier qu'on ne peut plus le modifier (soft deleted)
        update_response = client.put(
            f"/api/planning-charge/besoins/{besoin_id}",
            json={"besoin_heures": 70.0},
            headers=admin_auth_headers,
        )
        assert update_response.status_code == 404

    def test_delete_besoin_not_found(self, client, admin_auth_headers):
        """Test: suppression d'un besoin inexistant retourne 404."""
        response = client.delete(
            "/api/planning-charge/besoins/99999",
            headers=admin_auth_headers,
        )
        assert response.status_code == 404

    def test_delete_besoin_forbidden_for_chef_chantier(
        self, client, chef_chantier_auth_headers, admin_auth_headers
    ):
        """Test: un chef de chantier ne peut pas supprimer un besoin (403)."""
        chantier_id = self._create_test_chantier(client, admin_auth_headers)

        # Creer avec admin
        create_response = client.post(
            "/api/planning-charge/besoins",
            json={
                "chantier_id": chantier_id,
                "semaine_code": self._get_current_week_code(),
                "type_metier": "macon",
                "besoin_heures": 35.0,
            },
            headers=admin_auth_headers,
        )
        assert create_response.status_code == 201
        besoin_id = create_response.json()["id"]

        # Tenter de supprimer avec chef chantier
        delete_response = client.delete(
            f"/api/planning-charge/besoins/{besoin_id}",
            headers=chef_chantier_auth_headers,
        )
        assert delete_response.status_code == 403


class TestOccupationDetails:
    """Tests pour l'endpoint de details d'occupation (PDC-17)."""

    def _get_current_week_code(self):
        """Retourne le code de la semaine courante au format SXX-YYYY."""
        today = datetime.now()
        week_number = today.isocalendar()[1]
        year = today.year
        return f"S{week_number:02d}-{year}"

    def test_get_occupation_requires_auth(self, client):
        """Test: lecture des details d'occupation sans token retourne 401."""
        week_code = self._get_current_week_code()
        response = client.get(f"/api/planning-charge/occupation/{week_code}")
        assert response.status_code == 401

    def test_get_occupation_forbidden_for_compagnon(
        self, client, compagnon_auth_headers
    ):
        """Test: un compagnon ne peut pas voir les details d'occupation (403)."""
        week_code = self._get_current_week_code()
        response = client.get(
            f"/api/planning-charge/occupation/{week_code}",
            headers=compagnon_auth_headers,
        )
        assert response.status_code == 403

    def test_get_occupation_allowed_for_chef_chantier(
        self, client, chef_chantier_auth_headers
    ):
        """Test: un chef de chantier peut voir les details d'occupation (200)."""
        week_code = self._get_current_week_code()
        response = client.get(
            f"/api/planning-charge/occupation/{week_code}",
            headers=chef_chantier_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "semaine_code" in data
        assert "types" in data  # Details par type de metier
        assert "taux_global" in data

    def test_get_occupation_invalid_week_code(self, client, admin_auth_headers):
        """Test: code semaine invalide retourne 400."""
        response = client.get(
            "/api/planning-charge/occupation/INVALID",
            headers=admin_auth_headers,
        )
        assert response.status_code == 400


class TestBesoinsByChantier:
    """Tests pour l'endpoint de besoins par chantier."""

    def _get_current_week_code(self):
        """Retourne le code de la semaine courante au format SXX-YYYY."""
        today = datetime.now()
        week_number = today.isocalendar()[1]
        year = today.year
        return f"S{week_number:02d}-{year}"

    def _get_week_range(self, weeks_ahead=4):
        """Retourne les codes de debut et fin pour une plage de semaines."""
        today = datetime.now()
        week_start = today.isocalendar()[1]
        year_start = today.year

        end_date = today + timedelta(weeks=weeks_ahead)
        week_end = end_date.isocalendar()[1]
        year_end = end_date.year

        return (
            f"S{week_start:02d}-{year_start}",
            f"S{week_end:02d}-{year_end}",
        )

    def _create_test_chantier(self, client, auth_headers):
        """Cree un chantier de test et retourne son ID."""
        import random
        code = f"B{random.randint(100, 999)}"
        response = client.post(
            "/api/chantiers",
            json={
                "nom": "Chantier Besoins Test",
                "adresse": "456 Rue Test",
                "code": code,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201, f"Failed to create chantier: {response.json()}"
        return response.json()["id"]

    def test_get_besoins_by_chantier_requires_auth(self, client):
        """Test: lecture des besoins sans token retourne 401."""
        semaine_debut, semaine_fin = self._get_week_range()
        response = client.get(
            "/api/planning-charge/chantiers/1/besoins",
            params={
                "semaine_debut": semaine_debut,
                "semaine_fin": semaine_fin,
            },
        )
        assert response.status_code == 401

    def test_get_besoins_by_chantier_forbidden_for_compagnon(
        self, client, compagnon_auth_headers
    ):
        """Test: un compagnon ne peut pas voir les besoins d'un chantier (403)."""
        semaine_debut, semaine_fin = self._get_week_range()
        response = client.get(
            "/api/planning-charge/chantiers/1/besoins",
            params={
                "semaine_debut": semaine_debut,
                "semaine_fin": semaine_fin,
            },
            headers=compagnon_auth_headers,
        )
        assert response.status_code == 403

    def test_get_besoins_by_chantier_allowed_for_chef_chantier(
        self, client, chef_chantier_auth_headers, admin_auth_headers
    ):
        """Test: un chef de chantier peut voir les besoins d'un chantier (200)."""
        chantier_id = self._create_test_chantier(client, admin_auth_headers)
        semaine_debut, semaine_fin = self._get_week_range()

        response = client.get(
            f"/api/planning-charge/chantiers/{chantier_id}/besoins",
            params={
                "semaine_debut": semaine_debut,
                "semaine_fin": semaine_fin,
            },
            headers=chef_chantier_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_besoins_with_data(self, client, admin_auth_headers):
        """Test: lecture des besoins avec donnees retourne les besoins crees."""
        chantier_id = self._create_test_chantier(client, admin_auth_headers)
        semaine_debut, semaine_fin = self._get_week_range()

        # Creer quelques besoins
        for type_metier in ["macon", "coffreur", "ferrailleur"]:
            client.post(
                "/api/planning-charge/besoins",
                json={
                    "chantier_id": chantier_id,
                    "semaine_code": semaine_debut,
                    "type_metier": type_metier,
                    "besoin_heures": 35.0,
                },
                headers=admin_auth_headers,
            )

        # Lire les besoins
        response = client.get(
            f"/api/planning-charge/chantiers/{chantier_id}/besoins",
            params={
                "semaine_debut": semaine_debut,
                "semaine_fin": semaine_fin,
            },
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 3

    def test_get_besoins_with_pagination(self, client, admin_auth_headers):
        """Test: pagination des besoins fonctionne correctement."""
        chantier_id = self._create_test_chantier(client, admin_auth_headers)
        semaine_debut, semaine_fin = self._get_week_range()

        # Creer plusieurs besoins
        types_metier = ["macon", "coffreur", "ferrailleur", "grutier", "electricien"]
        for type_metier in types_metier:
            client.post(
                "/api/planning-charge/besoins",
                json={
                    "chantier_id": chantier_id,
                    "semaine_code": semaine_debut,
                    "type_metier": type_metier,
                    "besoin_heures": 35.0,
                },
                headers=admin_auth_headers,
            )

        # Lire avec pagination page 1
        response_page1 = client.get(
            f"/api/planning-charge/chantiers/{chantier_id}/besoins",
            params={
                "semaine_debut": semaine_debut,
                "semaine_fin": semaine_fin,
                "page": 1,
                "page_size": 2,
            },
            headers=admin_auth_headers,
        )
        assert response_page1.status_code == 200
        data_page1 = response_page1.json()
        assert len(data_page1["items"]) == 2
        assert data_page1["total"] == 5
        assert data_page1["page"] == 1
        assert data_page1["page_size"] == 2
        assert data_page1["total_pages"] == 3

        # Lire avec pagination page 2
        response_page2 = client.get(
            f"/api/planning-charge/chantiers/{chantier_id}/besoins",
            params={
                "semaine_debut": semaine_debut,
                "semaine_fin": semaine_fin,
                "page": 2,
                "page_size": 2,
            },
            headers=admin_auth_headers,
        )
        assert response_page2.status_code == 200
        data_page2 = response_page2.json()
        assert len(data_page2["items"]) == 2
        assert data_page2["page"] == 2

        # Lire avec pagination page 3 (derniere avec 1 element)
        response_page3 = client.get(
            f"/api/planning-charge/chantiers/{chantier_id}/besoins",
            params={
                "semaine_debut": semaine_debut,
                "semaine_fin": semaine_fin,
                "page": 3,
                "page_size": 2,
            },
            headers=admin_auth_headers,
        )
        assert response_page3.status_code == 200
        data_page3 = response_page3.json()
        assert len(data_page3["items"]) == 1
        assert data_page3["page"] == 3


class TestPlanningChargeIntegration:
    """Tests d'integration complets pour le planning de charge."""

    def _get_current_week_code(self):
        """Retourne le code de la semaine courante au format SXX-YYYY."""
        today = datetime.now()
        week_number = today.isocalendar()[1]
        year = today.year
        return f"S{week_number:02d}-{year}"

    def _get_week_range(self, weeks_ahead=4):
        """Retourne les codes de debut et fin pour une plage de semaines."""
        today = datetime.now()
        week_start = today.isocalendar()[1]
        year_start = today.year

        end_date = today + timedelta(weeks=weeks_ahead)
        week_end = end_date.isocalendar()[1]
        year_end = end_date.year

        return (
            f"S{week_start:02d}-{year_start}",
            f"S{week_end:02d}-{year_end}",
        )

    def _create_test_chantier(self, client, auth_headers, suffix=""):
        """Cree un chantier de test et retourne son ID."""
        import random
        code = f"I{random.randint(100, 999)}"
        response = client.post(
            "/api/chantiers",
            json={
                "nom": f"Chantier Integration Test {suffix}",
                "adresse": "789 Rue Test",
                "code": code,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201, f"Failed to create chantier: {response.json()}"
        return response.json()["id"]

    def test_planning_charge_full_workflow(self, client, admin_auth_headers):
        """Test: workflow complet - creation, lecture, mise a jour, suppression."""
        # 1. Creer un chantier
        chantier_id = self._create_test_chantier(client, admin_auth_headers, "WF")
        semaine_debut, semaine_fin = self._get_week_range()

        # 2. Creer des besoins pour ce chantier
        besoins_ids = []
        for type_metier in ["macon", "coffreur"]:
            response = client.post(
                "/api/planning-charge/besoins",
                json={
                    "chantier_id": chantier_id,
                    "semaine_code": semaine_debut,
                    "type_metier": type_metier,
                    "besoin_heures": 35.0,
                },
                headers=admin_auth_headers,
            )
            assert response.status_code == 201
            besoins_ids.append(response.json()["id"])

        # 3. Verifier que le planning contient le chantier
        planning_response = client.get(
            "/api/planning-charge",
            params={
                "semaine_debut": semaine_debut,
                "semaine_fin": semaine_fin,
            },
            headers=admin_auth_headers,
        )
        assert planning_response.status_code == 200
        planning_data = planning_response.json()
        assert planning_data["total_chantiers"] >= 1

        # 4. Mettre a jour un besoin
        update_response = client.put(
            f"/api/planning-charge/besoins/{besoins_ids[0]}",
            json={"besoin_heures": 70.0, "note": "Augmentation effectifs"},
            headers=admin_auth_headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["besoin_heures"] == 70.0

        # 5. Supprimer un besoin
        delete_response = client.delete(
            f"/api/planning-charge/besoins/{besoins_ids[1]}",
            headers=admin_auth_headers,
        )
        assert delete_response.status_code == 204

        # 6. Creer un nouveau besoin avec un type different (ferrailleur)
        # Note: l'unique constraint DB empeche de recreer un besoin identique (meme soft-deleted)
        create_new_response = client.post(
            "/api/planning-charge/besoins",
            json={
                "chantier_id": chantier_id,
                "semaine_code": semaine_debut,
                "type_metier": "ferrailleur",
                "besoin_heures": 40.0,
            },
            headers=admin_auth_headers,
        )
        assert create_new_response.status_code == 201

    def test_planning_charge_multiple_chantiers(
        self, client, admin_auth_headers, chef_chantier_auth_headers
    ):
        """Test: planning avec plusieurs chantiers."""
        semaine_debut, semaine_fin = self._get_week_range()

        # Creer plusieurs chantiers avec des besoins
        for i in range(3):
            chantier_id = self._create_test_chantier(
                client, admin_auth_headers, f"M{i}"
            )
            client.post(
                "/api/planning-charge/besoins",
                json={
                    "chantier_id": chantier_id,
                    "semaine_code": semaine_debut,
                    "type_metier": "macon",
                    "besoin_heures": 35.0 * (i + 1),
                },
                headers=admin_auth_headers,
            )

        # Verifier que le chef de chantier peut voir tous les chantiers
        response = client.get(
            "/api/planning-charge",
            params={
                "semaine_debut": semaine_debut,
                "semaine_fin": semaine_fin,
            },
            headers=chef_chantier_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_chantiers"] >= 3
