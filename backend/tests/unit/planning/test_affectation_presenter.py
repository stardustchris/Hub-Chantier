"""Tests unitaires pour AffectationPresenter.

Teste l'enrichissement des affectations avec les infos utilisateur/chantier.
"""

import pytest
from unittest.mock import Mock

from modules.planning.adapters.presenters import AffectationPresenter
from modules.planning.application.dtos import AffectationDTO
from shared.application.ports import EntityInfoService, UserBasicInfo, ChantierBasicInfo


class TestAffectationPresenter:
    """Tests pour AffectationPresenter."""

    @pytest.fixture
    def mock_entity_info(self):
        """Fixture pour le service EntityInfoService mocke."""
        service = Mock(spec=EntityInfoService)
        return service

    @pytest.fixture
    def presenter(self, mock_entity_info):
        """Fixture pour le presenter."""
        return AffectationPresenter(mock_entity_info)

    @pytest.fixture
    def sample_dto(self):
        """Fixture pour un DTO d'affectation."""
        return AffectationDTO(
            id=1,
            utilisateur_id=10,
            chantier_id=20,
            date="2026-01-24",
            heure_debut="08:00",
            heure_fin="17:00",
            type_affectation="unique",
            note="Test note",
            jours_recurrence=None,
            created_at="2026-01-24T10:00:00",
            updated_at="2026-01-24T10:00:00",
            created_by=1,
        )

    def test_present_enrichit_avec_infos_utilisateur(
        self, presenter, mock_entity_info, sample_dto
    ):
        """Test que present() ajoute les infos utilisateur."""
        mock_entity_info.get_user_info.return_value = UserBasicInfo(
            id=10,
            nom="Jean Dupont",
            couleur="#FF5733",
            metier="electricien",
        )
        mock_entity_info.get_chantier_info.return_value = ChantierBasicInfo(
            id=20,
            nom="Chantier A",
            couleur="#3498DB",
        )

        result = presenter.present(sample_dto)

        assert result["utilisateur_nom"] == "Jean Dupont"
        assert result["utilisateur_couleur"] == "#FF5733"
        assert result["utilisateur_metier"] == "electricien"

    def test_present_enrichit_avec_infos_chantier(
        self, presenter, mock_entity_info, sample_dto
    ):
        """Test que present() ajoute les infos chantier."""
        mock_entity_info.get_user_info.return_value = UserBasicInfo(
            id=10, nom="Jean Dupont"
        )
        mock_entity_info.get_chantier_info.return_value = ChantierBasicInfo(
            id=20,
            nom="Chantier A",
            couleur="#3498DB",
        )

        result = presenter.present(sample_dto)

        assert result["chantier_nom"] == "Chantier A"
        assert result["chantier_couleur"] == "#3498DB"

    def test_present_garde_champs_dto(self, presenter, mock_entity_info, sample_dto):
        """Test que present() garde les champs du DTO original."""
        mock_entity_info.get_user_info.return_value = None
        mock_entity_info.get_chantier_info.return_value = None

        result = presenter.present(sample_dto)

        assert result["id"] == 1
        assert result["utilisateur_id"] == 10
        assert result["chantier_id"] == 20
        assert result["date"] == "2026-01-24"
        assert result["heure_debut"] == "08:00"
        assert result["heure_fin"] == "17:00"
        assert result["note"] == "Test note"

    def test_present_gere_infos_manquantes(
        self, presenter, mock_entity_info, sample_dto
    ):
        """Test que present() gere les infos manquantes (None)."""
        mock_entity_info.get_user_info.return_value = None
        mock_entity_info.get_chantier_info.return_value = None

        result = presenter.present(sample_dto)

        assert result["utilisateur_nom"] is None
        assert result["utilisateur_couleur"] is None
        assert result["chantier_nom"] is None
        assert result["chantier_couleur"] is None

    def test_present_many_enrichit_toutes_affectations(
        self, presenter, mock_entity_info
    ):
        """Test que present_many() enrichit toutes les affectations."""
        dtos = [
            AffectationDTO(
                id=i,
                utilisateur_id=10 + i,
                chantier_id=20,
                date="2026-01-24",
                heure_debut="08:00",
                heure_fin="17:00",
                type_affectation="unique",
                note=None,
                jours_recurrence=None,
                created_at="2026-01-24T10:00:00",
                updated_at="2026-01-24T10:00:00",
                created_by=1,
            )
            for i in range(3)
        ]

        mock_entity_info.get_user_info.side_effect = lambda uid: UserBasicInfo(
            id=uid, nom=f"User {uid}"
        )
        mock_entity_info.get_chantier_info.return_value = ChantierBasicInfo(
            id=20, nom="Chantier A"
        )

        results = presenter.present_many(dtos)

        assert len(results) == 3
        assert results[0]["utilisateur_nom"] == "User 10"
        assert results[1]["utilisateur_nom"] == "User 11"
        assert results[2]["utilisateur_nom"] == "User 12"

    def test_present_many_utilise_cache(self, presenter, mock_entity_info):
        """Test que present_many() utilise le cache pour eviter les appels multiples."""
        # 3 affectations avec le meme utilisateur
        dtos = [
            AffectationDTO(
                id=i,
                utilisateur_id=10,  # Meme utilisateur
                chantier_id=20,  # Meme chantier
                date="2026-01-24",
                heure_debut="08:00",
                heure_fin="17:00",
                type_affectation="unique",
                note=None,
                jours_recurrence=None,
                created_at="2026-01-24T10:00:00",
                updated_at="2026-01-24T10:00:00",
                created_by=1,
            )
            for i in range(3)
        ]

        mock_entity_info.get_user_info.return_value = UserBasicInfo(
            id=10, nom="Jean Dupont"
        )
        mock_entity_info.get_chantier_info.return_value = ChantierBasicInfo(
            id=20, nom="Chantier A"
        )

        presenter.present_many(dtos)

        # Le service ne doit etre appele qu'une fois par ID unique
        assert mock_entity_info.get_user_info.call_count == 1
        assert mock_entity_info.get_chantier_info.call_count == 1

    def test_clear_cache_vide_le_cache(self, presenter, mock_entity_info, sample_dto):
        """Test que clear_cache() vide le cache."""
        mock_entity_info.get_user_info.return_value = UserBasicInfo(
            id=10, nom="Jean Dupont"
        )
        mock_entity_info.get_chantier_info.return_value = ChantierBasicInfo(
            id=20, nom="Chantier A"
        )

        # Premier appel - remplit le cache
        presenter.present(sample_dto)
        assert mock_entity_info.get_user_info.call_count == 1

        # Deuxieme appel - utilise le cache
        presenter.present(sample_dto)
        assert mock_entity_info.get_user_info.call_count == 1

        # Vider le cache
        presenter.clear_cache()

        # Troisieme appel - doit re-appeler le service
        presenter.present(sample_dto)
        assert mock_entity_info.get_user_info.call_count == 2

    def test_present_formate_date_iso(self, presenter, mock_entity_info, sample_dto):
        """Test que present() formate la date en ISO."""
        mock_entity_info.get_user_info.return_value = None
        mock_entity_info.get_chantier_info.return_value = None

        result = presenter.present(sample_dto)

        assert result["date"] == "2026-01-24"
        assert isinstance(result["date"], str)

    def test_present_formate_datetime_iso(self, presenter, mock_entity_info, sample_dto):
        """Test que present() formate created_at/updated_at en ISO."""
        mock_entity_info.get_user_info.return_value = None
        mock_entity_info.get_chantier_info.return_value = None

        result = presenter.present(sample_dto)

        assert "2026-01-24" in result["created_at"]
        assert "2026-01-24" in result["updated_at"]
