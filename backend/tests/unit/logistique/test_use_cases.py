"""Tests unitaires pour les Use Cases du module Logistique."""

import pytest
from datetime import date, time, datetime, timedelta
from unittest.mock import Mock, MagicMock

from modules.logistique.domain.entities import Ressource, Reservation
from modules.logistique.domain.value_objects import (
    CategorieRessource,
    StatutReservation,
    PlageHoraire,
)
from modules.logistique.application.use_cases import (
    CreateRessourceUseCase,
    UpdateRessourceUseCase,
    DeleteRessourceUseCase,
    GetRessourceUseCase,
    ListRessourcesUseCase,
    CreateReservationUseCase,
    ValiderReservationUseCase,
    RefuserReservationUseCase,
    AnnulerReservationUseCase,
    GetPlanningRessourceUseCase,
    ListReservationsEnAttenteUseCase,
)
from modules.logistique.application.use_cases.ressource_use_cases import (
    RessourceNotFoundError,
    RessourceCodeExistsError,
)
from modules.logistique.application.use_cases.reservation_use_cases import (
    ReservationNotFoundError,
    ReservationConflitError,
)
from modules.logistique.application.dtos import (
    RessourceCreateDTO,
    RessourceUpdateDTO,
    ReservationCreateDTO,
)


class TestCreateRessourceUseCase:
    """Tests pour CreateRessourceUseCase."""

    def test_create_ressource_success(
        self, mock_ressource_repository, mock_event_bus, sample_ressource
    ):
        """Test: création réussie d'une ressource."""
        mock_ressource_repository.find_by_code.return_value = None
        mock_ressource_repository.save.return_value = sample_ressource

        use_case = CreateRessourceUseCase(mock_ressource_repository, mock_event_bus)
        dto = RessourceCreateDTO(
            code="GRU001",
            nom="Grue mobile 50T",
            categorie=CategorieRessource.ENGIN_LEVAGE,
            couleur="#FF5733",
            heure_debut_defaut=time(7, 0),
            heure_fin_defaut=time(18, 0),
            validation_requise=True,
        )

        result = use_case.execute(dto, created_by=1)

        assert result is not None
        mock_ressource_repository.save.assert_called_once()
        mock_event_bus.publish.assert_called_once()

    def test_create_ressource_code_exists(
        self, mock_ressource_repository, mock_event_bus, sample_ressource
    ):
        """Test: erreur si le code existe déjà."""
        mock_ressource_repository.find_by_code.return_value = sample_ressource

        use_case = CreateRessourceUseCase(mock_ressource_repository, mock_event_bus)
        dto = RessourceCreateDTO(
            code="GRU001",
            nom="Autre grue",
            categorie=CategorieRessource.ENGIN_LEVAGE,
            couleur="#FF5733",
            heure_debut_defaut=time(7, 0),
            heure_fin_defaut=time(18, 0),
        )

        with pytest.raises(RessourceCodeExistsError):
            use_case.execute(dto, created_by=1)


class TestUpdateRessourceUseCase:
    """Tests pour UpdateRessourceUseCase."""

    def test_update_ressource_success(
        self, mock_ressource_repository, mock_event_bus, sample_ressource
    ):
        """Test: mise à jour réussie d'une ressource."""
        mock_ressource_repository.find_by_id.return_value = sample_ressource
        mock_ressource_repository.save.return_value = sample_ressource

        use_case = UpdateRessourceUseCase(mock_ressource_repository, mock_event_bus)
        dto = RessourceUpdateDTO(nom="Nouvelle Grue 80T")

        result = use_case.execute(ressource_id=1, dto=dto, updated_by=1)

        assert result is not None
        mock_ressource_repository.save.assert_called_once()
        mock_event_bus.publish.assert_called_once()

    def test_update_ressource_not_found(
        self, mock_ressource_repository, mock_event_bus
    ):
        """Test: erreur si ressource non trouvée."""
        mock_ressource_repository.find_by_id.return_value = None

        use_case = UpdateRessourceUseCase(mock_ressource_repository, mock_event_bus)
        dto = RessourceUpdateDTO(nom="Nouvelle Grue")

        with pytest.raises(RessourceNotFoundError):
            use_case.execute(ressource_id=999, dto=dto, updated_by=1)

    def test_update_ressource_code_conflict(
        self, mock_ressource_repository, mock_event_bus, sample_ressource
    ):
        """Test: erreur si le nouveau code existe déjà."""
        other_ressource = Ressource(
            id=2,
            code="GRU002",
            nom="Autre grue",
            categorie=CategorieRessource.ENGIN_LEVAGE,
            couleur="#000000",
            plage_horaire_defaut=PlageHoraire(heure_debut=time(8, 0), heure_fin=time(17, 0)),
            validation_requise=True,
            actif=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_ressource_repository.find_by_id.return_value = sample_ressource
        mock_ressource_repository.find_by_code.return_value = other_ressource

        use_case = UpdateRessourceUseCase(mock_ressource_repository, mock_event_bus)
        dto = RessourceUpdateDTO(code="GRU002")

        with pytest.raises(RessourceCodeExistsError):
            use_case.execute(ressource_id=1, dto=dto, updated_by=1)


class TestDeleteRessourceUseCase:
    """Tests pour DeleteRessourceUseCase."""

    def test_delete_ressource_success(
        self, mock_ressource_repository, mock_event_bus, sample_ressource
    ):
        """Test: suppression réussie."""
        mock_ressource_repository.find_by_id.return_value = sample_ressource
        mock_ressource_repository.delete.return_value = True

        use_case = DeleteRessourceUseCase(mock_ressource_repository, mock_event_bus)
        result = use_case.execute(ressource_id=1, deleted_by=1)

        assert result is True
        mock_ressource_repository.delete.assert_called_once_with(1)
        mock_event_bus.publish.assert_called_once()

    def test_delete_ressource_not_found(
        self, mock_ressource_repository, mock_event_bus
    ):
        """Test: erreur si ressource non trouvée."""
        mock_ressource_repository.find_by_id.return_value = None

        use_case = DeleteRessourceUseCase(mock_ressource_repository, mock_event_bus)

        with pytest.raises(RessourceNotFoundError):
            use_case.execute(ressource_id=999, deleted_by=1)


class TestGetRessourceUseCase:
    """Tests pour GetRessourceUseCase."""

    def test_get_ressource_success(self, mock_ressource_repository, sample_ressource):
        """Test: récupération réussie."""
        mock_ressource_repository.find_by_id.return_value = sample_ressource

        use_case = GetRessourceUseCase(mock_ressource_repository)
        result = use_case.execute(ressource_id=1)

        assert result is not None
        assert result.id == 1

    def test_get_ressource_not_found(self, mock_ressource_repository):
        """Test: erreur si ressource non trouvée."""
        mock_ressource_repository.find_by_id.return_value = None

        use_case = GetRessourceUseCase(mock_ressource_repository)

        with pytest.raises(RessourceNotFoundError):
            use_case.execute(ressource_id=999)


class TestListRessourcesUseCase:
    """Tests pour ListRessourcesUseCase."""

    def test_list_ressources_all(self, mock_ressource_repository, sample_ressource):
        """Test: liste toutes les ressources."""
        mock_ressource_repository.find_all.return_value = [sample_ressource]
        mock_ressource_repository.count.return_value = 1

        use_case = ListRessourcesUseCase(mock_ressource_repository)
        result = use_case.execute()

        assert result.total == 1
        assert len(result.items) == 1

    def test_list_ressources_by_category(
        self, mock_ressource_repository, sample_ressource
    ):
        """Test: filtrage par catégorie."""
        mock_ressource_repository.find_all.return_value = [sample_ressource]
        mock_ressource_repository.count.return_value = 1

        use_case = ListRessourcesUseCase(mock_ressource_repository)
        result = use_case.execute(categorie=CategorieRessource.ENGIN_LEVAGE)

        mock_ressource_repository.find_all.assert_called_once_with(
            categorie=CategorieRessource.ENGIN_LEVAGE,
            actif_seulement=True,
            limit=100,
            offset=0,
        )


class TestCreateReservationUseCase:
    """Tests pour CreateReservationUseCase."""

    def test_create_reservation_success(
        self,
        mock_reservation_repository,
        mock_ressource_repository,
        mock_event_bus,
        sample_ressource,
        sample_reservation,
    ):
        """Test: création réussie d'une réservation."""
        mock_ressource_repository.find_by_id.return_value = sample_ressource
        mock_reservation_repository.find_conflits.return_value = []
        mock_reservation_repository.save.return_value = sample_reservation

        use_case = CreateReservationUseCase(
            mock_reservation_repository, mock_ressource_repository, mock_event_bus
        )
        dto = ReservationCreateDTO(
            ressource_id=1,
            chantier_id=100,
            date_reservation=date.today(),
            heure_debut=time(9, 0),
            heure_fin=time(12, 0),
            commentaire="Test",
        )

        result = use_case.execute(dto, demandeur_id=10)

        assert result is not None
        mock_reservation_repository.save.assert_called_once()
        mock_event_bus.publish.assert_called()

    def test_create_reservation_ressource_not_found(
        self,
        mock_reservation_repository,
        mock_ressource_repository,
        mock_event_bus,
    ):
        """Test: erreur si ressource non trouvée."""
        mock_ressource_repository.find_by_id.return_value = None

        use_case = CreateReservationUseCase(
            mock_reservation_repository, mock_ressource_repository, mock_event_bus
        )
        dto = ReservationCreateDTO(
            ressource_id=999,
            chantier_id=100,
            date_reservation=date.today(),
            heure_debut=time(9, 0),
            heure_fin=time(12, 0),
        )

        with pytest.raises(RessourceNotFoundError):
            use_case.execute(dto, demandeur_id=10)

    def test_create_reservation_conflict(
        self,
        mock_reservation_repository,
        mock_ressource_repository,
        mock_event_bus,
        sample_ressource,
        validated_reservation,
    ):
        """Test: erreur en cas de conflit."""
        mock_ressource_repository.find_by_id.return_value = sample_ressource
        mock_reservation_repository.find_conflits.return_value = [validated_reservation]

        use_case = CreateReservationUseCase(
            mock_reservation_repository, mock_ressource_repository, mock_event_bus
        )
        dto = ReservationCreateDTO(
            ressource_id=1,
            chantier_id=100,
            date_reservation=date.today(),
            heure_debut=time(14, 0),  # Même horaire que validated_reservation
            heure_fin=time(17, 0),
        )

        with pytest.raises(ReservationConflitError):
            use_case.execute(dto, demandeur_id=10)


class TestValiderReservationUseCase:
    """Tests pour ValiderReservationUseCase."""

    def test_valider_reservation_success(
        self,
        mock_reservation_repository,
        mock_ressource_repository,
        mock_event_bus,
        sample_ressource,
        sample_reservation,
    ):
        """Test: validation réussie."""
        mock_reservation_repository.find_by_id.return_value = sample_reservation
        mock_ressource_repository.find_by_id.return_value = sample_ressource
        mock_reservation_repository.save.return_value = sample_reservation

        use_case = ValiderReservationUseCase(
            mock_reservation_repository, mock_ressource_repository, mock_event_bus
        )

        result = use_case.execute(reservation_id=1, valideur_id=5)

        assert result is not None
        mock_event_bus.publish.assert_called()


class TestRefuserReservationUseCase:
    """Tests pour RefuserReservationUseCase."""

    def test_refuser_reservation_success(
        self,
        mock_reservation_repository,
        mock_ressource_repository,
        mock_event_bus,
        sample_ressource,
        sample_reservation,
    ):
        """Test: refus réussi avec motif."""
        mock_reservation_repository.find_by_id.return_value = sample_reservation
        mock_ressource_repository.find_by_id.return_value = sample_ressource
        mock_reservation_repository.save.return_value = sample_reservation

        use_case = RefuserReservationUseCase(
            mock_reservation_repository, mock_ressource_repository, mock_event_bus
        )

        result = use_case.execute(
            reservation_id=1, valideur_id=5, motif="Ressource en maintenance"
        )

        assert result is not None
        mock_event_bus.publish.assert_called()


class TestAnnulerReservationUseCase:
    """Tests pour AnnulerReservationUseCase."""

    def test_annuler_reservation_success(
        self,
        mock_reservation_repository,
        mock_event_bus,
        validated_reservation,
    ):
        """Test: annulation réussie."""
        mock_reservation_repository.find_by_id.return_value = validated_reservation
        mock_reservation_repository.save.return_value = validated_reservation

        use_case = AnnulerReservationUseCase(mock_reservation_repository, mock_event_bus)

        result = use_case.execute(reservation_id=2, user_id=10)

        assert result is not None
        mock_event_bus.publish.assert_called()


class TestGetPlanningRessourceUseCase:
    """Tests pour GetPlanningRessourceUseCase."""

    def test_get_planning_success(
        self,
        mock_reservation_repository,
        mock_ressource_repository,
        sample_ressource,
        sample_reservation,
    ):
        """Test: récupération du planning."""
        mock_ressource_repository.find_by_id.return_value = sample_ressource
        mock_reservation_repository.find_by_ressource_and_date_range.return_value = [
            sample_reservation
        ]

        use_case = GetPlanningRessourceUseCase(
            mock_reservation_repository, mock_ressource_repository
        )

        result = use_case.execute(
            ressource_id=1,
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=7),
        )

        assert result is not None
        assert len(result.reservations) == 1


class TestListReservationsEnAttenteUseCase:
    """Tests pour ListReservationsEnAttenteUseCase."""

    def test_list_en_attente_success(
        self,
        mock_reservation_repository,
        mock_ressource_repository,
        sample_reservation,
        sample_ressource,
    ):
        """Test: liste des réservations en attente."""
        mock_reservation_repository.find_en_attente_validation.return_value = [sample_reservation]
        mock_reservation_repository.count_en_attente.return_value = 1  # H11
        mock_ressource_repository.find_by_id.return_value = sample_ressource

        use_case = ListReservationsEnAttenteUseCase(
            mock_reservation_repository, mock_ressource_repository
        )

        result = use_case.execute()

        assert result.total == 1
        assert len(result.items) == 1
