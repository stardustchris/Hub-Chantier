"""Tests unitaires pour les helpers d'enrichissement DTO logistique."""

from unittest.mock import Mock, patch

from modules.logistique.application.helpers.dto_enrichment import (
    enrich_reservation_dto,
    enrich_reservations_list,
    get_ressource_info,
)


class TestEnrichReservationDto:
    """Tests pour enrich_reservation_dto."""

    def test_enrichit_avec_toutes_les_infos(self):
        """DTO enrichi avec ressource + demandeur + valideur."""
        reservation = Mock()
        ressource = Mock()
        ressource.nom = "Grue"
        ressource.code = "GRU-001"
        ressource.couleur = "#FF0000"

        demandeur = Mock()
        demandeur.prenom = "Jean"
        demandeur.nom = "Dupont"

        valideur = Mock()
        valideur.prenom = "Marie"
        valideur.nom = "Martin"

        with patch("modules.logistique.application.helpers.dto_enrichment.ReservationDTO") as MockDTO:
            MockDTO.from_entity.return_value = Mock()
            result = enrich_reservation_dto(reservation, ressource, demandeur, valideur)

            MockDTO.from_entity.assert_called_once_with(
                reservation,
                ressource_nom="Grue",
                ressource_code="GRU-001",
                ressource_couleur="#FF0000",
                demandeur_nom="Jean Dupont",
                valideur_nom="Marie Martin",
            )

    def test_enrichit_sans_ressource(self):
        """DTO enrichi sans ressource (None)."""
        reservation = Mock()

        with patch("modules.logistique.application.helpers.dto_enrichment.ReservationDTO") as MockDTO:
            MockDTO.from_entity.return_value = Mock()
            enrich_reservation_dto(reservation, None, None, None)

            MockDTO.from_entity.assert_called_once_with(
                reservation,
                ressource_nom=None,
                ressource_code=None,
                ressource_couleur=None,
                demandeur_nom=None,
                valideur_nom=None,
            )

    def test_enrichit_avec_demandeur_seul(self):
        """DTO enrichi avec demandeur mais pas de valideur."""
        reservation = Mock()
        demandeur = Mock()
        demandeur.prenom = "Jean"
        demandeur.nom = "Dupont"

        with patch("modules.logistique.application.helpers.dto_enrichment.ReservationDTO") as MockDTO:
            MockDTO.from_entity.return_value = Mock()
            enrich_reservation_dto(reservation, None, demandeur, None)

            call_kwargs = MockDTO.from_entity.call_args
            assert call_kwargs.kwargs["demandeur_nom"] == "Jean Dupont"
            assert call_kwargs.kwargs["valideur_nom"] is None


class TestEnrichReservationsList:
    """Tests pour enrich_reservations_list."""

    def test_enrichit_liste_vide(self):
        """Liste vide retourne liste vide."""
        mock_ressource_repo = Mock()
        result = enrich_reservations_list([], mock_ressource_repo)
        assert result == []

    def test_enrichit_avec_cache_ressources(self):
        """Utilise le cache pour éviter les requêtes multiples."""
        mock_ressource_repo = Mock()
        mock_ressource = Mock()
        mock_ressource.nom = "Grue"
        mock_ressource.code = "GRU-001"
        mock_ressource.couleur = "#FF0000"
        mock_ressource_repo.find_by_id.return_value = mock_ressource

        r1 = Mock()
        r1.ressource_id = 1
        r1.demandeur_id = 10
        r1.valideur_id = None

        r2 = Mock()
        r2.ressource_id = 1  # Même ressource
        r2.demandeur_id = 10
        r2.valideur_id = None

        with patch("modules.logistique.application.helpers.dto_enrichment.ReservationDTO") as MockDTO:
            MockDTO.from_entity.return_value = Mock()
            result = enrich_reservations_list([r1, r2], mock_ressource_repo)

        # La ressource ne doit être chargée qu'une fois grâce au cache
        mock_ressource_repo.find_by_id.assert_called_once_with(1)
        assert len(result) == 2

    def test_enrichit_avec_user_repository(self):
        """Charge les utilisateurs si user_repository fourni."""
        mock_ressource_repo = Mock()
        mock_ressource_repo.find_by_id.return_value = Mock(nom="R", code="R1", couleur="#FFF")

        mock_user_repo = Mock()
        mock_user = Mock(prenom="Jean", nom="D")
        mock_user_repo.find_by_id.return_value = mock_user

        r1 = Mock()
        r1.ressource_id = 1
        r1.demandeur_id = 10
        r1.valideur_id = 20

        with patch("modules.logistique.application.helpers.dto_enrichment.ReservationDTO") as MockDTO:
            MockDTO.from_entity.return_value = Mock()
            enrich_reservations_list([r1], mock_ressource_repo, mock_user_repo)

        # demandeur + valideur chargés
        assert mock_user_repo.find_by_id.call_count == 2


class TestGetRessourceInfo:
    """Tests pour get_ressource_info."""

    def test_retourne_ressource(self):
        """Retourne la ressource trouvée."""
        mock_repo = Mock()
        mock_ressource = Mock()
        mock_repo.find_by_id.return_value = mock_ressource

        result = get_ressource_info(1, mock_repo)

        assert result is mock_ressource
        mock_repo.find_by_id.assert_called_once_with(1)

    def test_retourne_none_si_non_trouvee(self):
        """Retourne None si ressource non trouvée."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        result = get_ressource_info(99, mock_repo)
        assert result is None
