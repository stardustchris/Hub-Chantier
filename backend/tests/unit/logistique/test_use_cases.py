"""Tests des Use Cases du module Logistique.

CDC Section 11 - LOG-01 a LOG-18.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, MagicMock

from modules.logistique.domain.entities import Ressource, Reservation
from modules.logistique.domain.value_objects import TypeRessource, StatutReservation
from modules.logistique.application.use_cases.ressource_use_cases import (
    CreateRessourceUseCase,
    GetRessourceUseCase,
    ListRessourcesUseCase,
    UpdateRessourceUseCase,
    DeleteRessourceUseCase,
    ActivateRessourceUseCase,
    RessourceNotFoundError,
    RessourceCodeAlreadyExistsError,
    AccessDeniedError,
)
from modules.logistique.application.use_cases.reservation_use_cases import (
    CreateReservationUseCase,
    GetReservationUseCase,
    ListReservationsUseCase,
    ValidateReservationUseCase,
    RefuseReservationUseCase,
    CancelReservationUseCase,
    GetPlanningRessourceUseCase,
    GetPendingReservationsUseCase,
    CheckConflitsUseCase,
    ReservationNotFoundError,
    RessourceNotFoundError as ReservationRessourceNotFoundError,
    ConflitReservationError,
    AccessDeniedError as ReservationAccessDeniedError,
    InvalidStatusTransitionError,
)
from modules.logistique.application.dtos import (
    CreateRessourceDTO,
    UpdateRessourceDTO,
    CreateReservationDTO,
    ValidateReservationDTO,
    RefuseReservationDTO,
    ReservationFiltersDTO,
)


# ====================
# RESSOURCE USE CASES
# ====================


class TestCreateRessourceUseCase:
    """Tests pour CreateRessourceUseCase (LOG-01)."""

    def test_create_ressource_success_admin(self):
        """Creation de ressource reussie par admin."""
        mock_repo = Mock()
        mock_repo.find_by_code.return_value = None

        saved_ressource = Ressource(
            id=1,
            code="GRU001",
            nom="Grue mobile 50T",
            type_ressource=TypeRessource.LEVAGE,
        )
        mock_repo.save.return_value = saved_ressource

        use_case = CreateRessourceUseCase(ressource_repository=mock_repo)

        dto = CreateRessourceDTO(
            code="GRU001",
            nom="Grue mobile 50T",
            type_ressource="levage",
            description="Grue pour chantier",
            validation_requise=True,
        )

        result = use_case.execute(dto, user_role="admin")

        assert result.id == 1
        assert result.code == "GRU001"
        assert result.nom == "Grue mobile 50T"
        assert result.type_ressource == "levage"
        mock_repo.find_by_code.assert_called_once_with("GRU001")
        mock_repo.save.assert_called_once()

    def test_create_ressource_access_denied_non_admin(self):
        """Erreur si l'utilisateur n'est pas admin (LOG-01)."""
        mock_repo = Mock()
        use_case = CreateRessourceUseCase(ressource_repository=mock_repo)

        dto = CreateRessourceDTO(
            code="GRU001",
            nom="Grue mobile",
            type_ressource="levage",
        )

        with pytest.raises(AccessDeniedError, match="administrateurs"):
            use_case.execute(dto, user_role="compagnon")

        with pytest.raises(AccessDeniedError, match="administrateurs"):
            use_case.execute(dto, user_role="chef_chantier")

        with pytest.raises(AccessDeniedError, match="administrateurs"):
            use_case.execute(dto, user_role="conducteur")

    def test_create_ressource_code_already_exists(self):
        """Erreur si le code existe deja."""
        mock_repo = Mock()
        mock_repo.find_by_code.return_value = Ressource(
            id=1,
            code="GRU001",
            nom="Grue existante",
        )

        use_case = CreateRessourceUseCase(ressource_repository=mock_repo)

        dto = CreateRessourceDTO(
            code="GRU001",
            nom="Nouvelle grue",
            type_ressource="levage",
        )

        with pytest.raises(RessourceCodeAlreadyExistsError, match="GRU001"):
            use_case.execute(dto, user_role="admin")

    def test_create_ressource_with_all_fields(self):
        """Creation avec tous les champs."""
        mock_repo = Mock()
        mock_repo.find_by_code.return_value = None

        def save_side_effect(ressource):
            ressource.id = 1
            return ressource

        mock_repo.save.side_effect = save_side_effect

        use_case = CreateRessourceUseCase(ressource_repository=mock_repo)

        dto = CreateRessourceDTO(
            code="NAC001",
            nom="Nacelle articulee",
            type_ressource="levage",
            description="Nacelle 20m",
            photo_url="https://example.com/nacelle.jpg",
            couleur="#FF5733",
            plage_horaire_debut="07:00",
            plage_horaire_fin="19:00",
            validation_requise=True,
        )

        result = use_case.execute(dto, user_role="admin")

        assert result.nom == "Nacelle articulee"
        assert result.plage_horaire_debut == "07:00"
        assert result.plage_horaire_fin == "19:00"


class TestGetRessourceUseCase:
    """Tests pour GetRessourceUseCase (LOG-02)."""

    def test_get_ressource_success(self):
        """Recuperation reussie."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = Ressource(
            id=1,
            code="GRU001",
            nom="Grue mobile",
            type_ressource=TypeRessource.LEVAGE,
        )

        use_case = GetRessourceUseCase(ressource_repository=mock_repo)
        result = use_case.execute(1)

        assert result.id == 1
        assert result.code == "GRU001"
        assert result.nom == "Grue mobile"
        mock_repo.find_by_id.assert_called_once_with(1)

    def test_get_ressource_not_found(self):
        """Erreur si ressource non trouvee."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        use_case = GetRessourceUseCase(ressource_repository=mock_repo)

        with pytest.raises(RessourceNotFoundError, match="999"):
            use_case.execute(999)


class TestListRessourcesUseCase:
    """Tests pour ListRessourcesUseCase."""

    def test_list_ressources_success(self):
        """Liste des ressources reussie."""
        mock_repo = Mock()
        ressources = [
            Ressource(id=1, code="GRU001", nom="Grue 1", type_ressource=TypeRessource.LEVAGE),
            Ressource(id=2, code="NAC001", nom="Nacelle 1", type_ressource=TypeRessource.LEVAGE),
        ]
        mock_repo.find_all.return_value = ressources
        mock_repo.count.return_value = 2

        use_case = ListRessourcesUseCase(ressource_repository=mock_repo)
        result = use_case.execute()

        assert len(result.ressources) == 2
        assert result.total == 2
        assert result.skip == 0
        assert result.limit == 50

    def test_list_ressources_filter_by_type(self):
        """Liste filtree par type."""
        mock_repo = Mock()
        ressources = [
            Ressource(id=1, code="GRU001", nom="Grue", type_ressource=TypeRessource.LEVAGE),
        ]
        mock_repo.find_all.return_value = ressources
        mock_repo.count.return_value = 1

        use_case = ListRessourcesUseCase(ressource_repository=mock_repo)
        result = use_case.execute(type_ressource="levage")

        assert len(result.ressources) == 1
        mock_repo.find_all.assert_called_once_with(
            type_ressource="levage",
            is_active=True,
            skip=0,
            limit=50,
        )

    def test_list_ressources_filter_by_active(self):
        """Liste filtree par statut actif."""
        mock_repo = Mock()
        mock_repo.find_all.return_value = []
        mock_repo.count.return_value = 0

        use_case = ListRessourcesUseCase(ressource_repository=mock_repo)
        result = use_case.execute(is_active=False)

        mock_repo.find_all.assert_called_once_with(
            type_ressource=None,
            is_active=False,
            skip=0,
            limit=50,
        )

    def test_list_ressources_with_pagination(self):
        """Liste avec pagination."""
        mock_repo = Mock()
        mock_repo.find_all.return_value = []
        mock_repo.count.return_value = 100

        use_case = ListRessourcesUseCase(ressource_repository=mock_repo)
        result = use_case.execute(skip=20, limit=10)

        assert result.skip == 20
        assert result.limit == 10
        assert result.total == 100
        mock_repo.find_all.assert_called_once_with(
            type_ressource=None,
            is_active=True,
            skip=20,
            limit=10,
        )


class TestUpdateRessourceUseCase:
    """Tests pour UpdateRessourceUseCase."""

    def test_update_ressource_success(self):
        """Mise a jour reussie."""
        mock_repo = Mock()
        ressource = Ressource(id=1, code="GRU001", nom="Ancien nom")
        mock_repo.find_by_id.return_value = ressource
        mock_repo.save.return_value = ressource

        use_case = UpdateRessourceUseCase(ressource_repository=mock_repo)

        dto = UpdateRessourceDTO(id=1, nom="Nouveau nom")
        result = use_case.execute(dto, user_role="admin")

        assert result.nom == "Nouveau nom"
        mock_repo.save.assert_called_once()

    def test_update_ressource_access_denied(self):
        """Erreur si non admin."""
        mock_repo = Mock()
        use_case = UpdateRessourceUseCase(ressource_repository=mock_repo)

        dto = UpdateRessourceDTO(id=1, nom="Test")

        with pytest.raises(AccessDeniedError):
            use_case.execute(dto, user_role="compagnon")

    def test_update_ressource_not_found(self):
        """Erreur si ressource non trouvee."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        use_case = UpdateRessourceUseCase(ressource_repository=mock_repo)

        dto = UpdateRessourceDTO(id=999, nom="Test")

        with pytest.raises(RessourceNotFoundError):
            use_case.execute(dto, user_role="admin")

    def test_update_ressource_type(self):
        """Mise a jour du type de ressource."""
        mock_repo = Mock()
        ressource = Ressource(
            id=1,
            code="GRU001",
            nom="Test",
            type_ressource=TypeRessource.OUTILLAGE,
        )
        mock_repo.find_by_id.return_value = ressource
        mock_repo.save.return_value = ressource

        use_case = UpdateRessourceUseCase(ressource_repository=mock_repo)

        dto = UpdateRessourceDTO(id=1, type_ressource="levage")
        result = use_case.execute(dto, user_role="admin")

        assert result.type_ressource == "levage"


class TestDeleteRessourceUseCase:
    """Tests pour DeleteRessourceUseCase."""

    def test_delete_ressource_success(self):
        """Suppression (soft delete) reussie."""
        mock_repo = Mock()
        ressource = Ressource(id=1, code="GRU001", nom="Test")
        mock_repo.find_by_id.return_value = ressource
        mock_repo.save.return_value = ressource

        use_case = DeleteRessourceUseCase(ressource_repository=mock_repo)
        use_case.execute(1, user_role="admin")

        # Verifier que supprimer a ete appele
        assert ressource.is_deleted is True
        mock_repo.save.assert_called_once()

    def test_delete_ressource_access_denied(self):
        """Erreur si non admin."""
        mock_repo = Mock()
        use_case = DeleteRessourceUseCase(ressource_repository=mock_repo)

        with pytest.raises(AccessDeniedError):
            use_case.execute(1, user_role="compagnon")

    def test_delete_ressource_not_found(self):
        """Erreur si ressource non trouvee."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        use_case = DeleteRessourceUseCase(ressource_repository=mock_repo)

        with pytest.raises(RessourceNotFoundError):
            use_case.execute(999, user_role="admin")


class TestActivateRessourceUseCase:
    """Tests pour ActivateRessourceUseCase."""

    def test_activate_ressource_success(self):
        """Activation reussie."""
        mock_repo = Mock()
        ressource = Ressource(id=1, code="GRU001", nom="Test", is_active=False)
        mock_repo.find_by_id.return_value = ressource
        mock_repo.save.return_value = ressource

        use_case = ActivateRessourceUseCase(ressource_repository=mock_repo)
        result = use_case.execute(1, is_active=True, user_role="admin")

        assert result.is_active is True

    def test_deactivate_ressource_success(self):
        """Desactivation reussie."""
        mock_repo = Mock()
        ressource = Ressource(id=1, code="GRU001", nom="Test", is_active=True)
        mock_repo.find_by_id.return_value = ressource
        mock_repo.save.return_value = ressource

        use_case = ActivateRessourceUseCase(ressource_repository=mock_repo)
        result = use_case.execute(1, is_active=False, user_role="admin")

        assert result.is_active is False

    def test_activate_ressource_access_denied(self):
        """Erreur si non admin."""
        mock_repo = Mock()
        use_case = ActivateRessourceUseCase(ressource_repository=mock_repo)

        with pytest.raises(AccessDeniedError):
            use_case.execute(1, is_active=True, user_role="compagnon")

    def test_activate_ressource_not_found(self):
        """Erreur si ressource non trouvee."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        use_case = ActivateRessourceUseCase(ressource_repository=mock_repo)

        with pytest.raises(RessourceNotFoundError):
            use_case.execute(999, is_active=True, user_role="admin")


# ====================
# RESERVATION USE CASES
# ====================


class TestCreateReservationUseCase:
    """Tests pour CreateReservationUseCase (LOG-07)."""

    def test_create_reservation_success_validation_requise(self):
        """Creation avec validation requise -> statut EN_ATTENTE."""
        mock_reservation_repo = Mock()
        mock_ressource_repo = Mock()

        ressource = Ressource(
            id=1,
            code="GRU001",
            nom="Grue",
            validation_requise=True,
        )
        mock_ressource_repo.find_by_id.return_value = ressource
        mock_reservation_repo.find_conflits.return_value = []

        def save_side_effect(reservation):
            reservation.id = 1
            return reservation

        mock_reservation_repo.save.side_effect = save_side_effect

        use_case = CreateReservationUseCase(
            reservation_repository=mock_reservation_repo,
            ressource_repository=mock_ressource_repo,
        )

        today = date.today()
        dto = CreateReservationDTO(
            ressource_id=1,
            chantier_id=2,
            demandeur_id=3,
            date_debut=today,
            date_fin=today,
            heure_debut="08:00",
            heure_fin="12:00",
        )

        result = use_case.execute(dto)

        assert result.id == 1
        assert result.statut == "en_attente"
        mock_ressource_repo.find_by_id.assert_called_once_with(1)
        mock_reservation_repo.find_conflits.assert_called_once()
        mock_reservation_repo.save.assert_called_once()

    def test_create_reservation_success_validation_non_requise(self):
        """Creation sans validation requise -> statut VALIDEE direct (LOG-11)."""
        mock_reservation_repo = Mock()
        mock_ressource_repo = Mock()

        ressource = Ressource(
            id=1,
            code="VEH001",
            nom="Vehicule",
            type_ressource=TypeRessource.VEHICULE,
            validation_requise=False,
        )
        mock_ressource_repo.find_by_id.return_value = ressource
        mock_reservation_repo.find_conflits.return_value = []

        def save_side_effect(reservation):
            reservation.id = 1
            return reservation

        mock_reservation_repo.save.side_effect = save_side_effect

        use_case = CreateReservationUseCase(
            reservation_repository=mock_reservation_repo,
            ressource_repository=mock_ressource_repo,
        )

        today = date.today()
        dto = CreateReservationDTO(
            ressource_id=1,
            chantier_id=2,
            demandeur_id=3,
            date_debut=today,
            date_fin=today,
            heure_debut="08:00",
            heure_fin="12:00",
        )

        result = use_case.execute(dto)

        assert result.statut == "validee"

    def test_create_reservation_ressource_not_found(self):
        """Erreur si ressource non trouvee."""
        mock_reservation_repo = Mock()
        mock_ressource_repo = Mock()
        mock_ressource_repo.find_by_id.return_value = None

        use_case = CreateReservationUseCase(
            reservation_repository=mock_reservation_repo,
            ressource_repository=mock_ressource_repo,
        )

        today = date.today()
        dto = CreateReservationDTO(
            ressource_id=999,
            chantier_id=2,
            demandeur_id=3,
            date_debut=today,
            date_fin=today,
            heure_debut="08:00",
            heure_fin="12:00",
        )

        with pytest.raises(ReservationRessourceNotFoundError, match="999"):
            use_case.execute(dto)

    def test_create_reservation_conflit_detecte(self):
        """Erreur si conflit detecte (LOG-17)."""
        mock_reservation_repo = Mock()
        mock_ressource_repo = Mock()

        ressource = Ressource(id=1, code="GRU001", nom="Grue")
        mock_ressource_repo.find_by_id.return_value = ressource

        # Simule un conflit
        today = date.today()
        conflit = Reservation(
            id=10,
            ressource_id=1,
            chantier_id=5,
            demandeur_id=6,
            date_debut=today,
            date_fin=today,
            heure_debut="08:00",
            heure_fin="12:00",
            statut=StatutReservation.VALIDEE,
        )
        mock_reservation_repo.find_conflits.return_value = [conflit]

        use_case = CreateReservationUseCase(
            reservation_repository=mock_reservation_repo,
            ressource_repository=mock_ressource_repo,
        )

        dto = CreateReservationDTO(
            ressource_id=1,
            chantier_id=2,
            demandeur_id=3,
            date_debut=today,
            date_fin=today,
            heure_debut="08:00",
            heure_fin="12:00",
        )

        with pytest.raises(ConflitReservationError) as exc_info:
            use_case.execute(dto)

        assert len(exc_info.value.conflits) == 1

    def test_create_reservation_with_note(self):
        """Creation avec note."""
        mock_reservation_repo = Mock()
        mock_ressource_repo = Mock()

        ressource = Ressource(id=1, code="GRU001", nom="Grue", validation_requise=True)
        mock_ressource_repo.find_by_id.return_value = ressource
        mock_reservation_repo.find_conflits.return_value = []

        def save_side_effect(reservation):
            reservation.id = 1
            return reservation

        mock_reservation_repo.save.side_effect = save_side_effect

        use_case = CreateReservationUseCase(
            reservation_repository=mock_reservation_repo,
            ressource_repository=mock_ressource_repo,
        )

        today = date.today()
        dto = CreateReservationDTO(
            ressource_id=1,
            chantier_id=2,
            demandeur_id=3,
            date_debut=today,
            date_fin=today,
            heure_debut="08:00",
            heure_fin="12:00",
            note="Besoin urgent pour levage materiel",
        )

        result = use_case.execute(dto)

        assert result.note == "Besoin urgent pour levage materiel"


class TestGetReservationUseCase:
    """Tests pour GetReservationUseCase."""

    def test_get_reservation_success(self):
        """Recuperation reussie."""
        mock_repo = Mock()
        today = date.today()
        reservation = Reservation(
            id=1,
            ressource_id=2,
            chantier_id=3,
            demandeur_id=4,
            date_debut=today,
            date_fin=today,
        )
        mock_repo.find_by_id.return_value = reservation

        use_case = GetReservationUseCase(reservation_repository=mock_repo)
        result = use_case.execute(1)

        assert result.id == 1
        assert result.ressource_id == 2
        mock_repo.find_by_id.assert_called_once_with(1)

    def test_get_reservation_not_found(self):
        """Erreur si reservation non trouvee."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        use_case = GetReservationUseCase(reservation_repository=mock_repo)

        with pytest.raises(ReservationNotFoundError, match="999"):
            use_case.execute(999)

    def test_get_reservation_with_enrichment(self):
        """Recuperation avec enrichissement (noms utilisateurs/chantier)."""
        mock_repo = Mock()
        today = date.today()
        reservation = Reservation(
            id=1,
            ressource_id=2,
            chantier_id=3,
            demandeur_id=4,
            valideur_id=5,
            date_debut=today,
            date_fin=today,
        )
        mock_repo.find_by_id.return_value = reservation

        def get_user_name(user_id):
            names = {4: "Jean Dupont", 5: "Marie Martin"}
            return names.get(user_id)

        def get_chantier_name(chantier_id):
            return "Chantier Exemple" if chantier_id == 3 else None

        use_case = GetReservationUseCase(
            reservation_repository=mock_repo,
            get_user_name=get_user_name,
            get_chantier_name=get_chantier_name,
        )

        result = use_case.execute(1)

        assert result.demandeur_nom == "Jean Dupont"
        assert result.valideur_nom == "Marie Martin"
        assert result.chantier_nom == "Chantier Exemple"


class TestListReservationsUseCase:
    """Tests pour ListReservationsUseCase."""

    def test_list_reservations_success(self):
        """Liste des reservations reussie."""
        mock_repo = Mock()
        today = date.today()
        reservations = [
            Reservation(id=1, ressource_id=1, chantier_id=1, demandeur_id=1, date_debut=today, date_fin=today),
            Reservation(id=2, ressource_id=2, chantier_id=1, demandeur_id=1, date_debut=today, date_fin=today),
        ]
        mock_repo.find_all.return_value = reservations
        mock_repo.count.return_value = 2

        use_case = ListReservationsUseCase(reservation_repository=mock_repo)

        filters = ReservationFiltersDTO()
        result = use_case.execute(filters)

        assert len(result.reservations) == 2
        assert result.total == 2

    def test_list_reservations_filter_by_ressource(self):
        """Liste filtree par ressource."""
        mock_repo = Mock()
        mock_repo.find_all.return_value = []
        mock_repo.count.return_value = 0

        use_case = ListReservationsUseCase(reservation_repository=mock_repo)

        filters = ReservationFiltersDTO(ressource_id=5)
        use_case.execute(filters)

        mock_repo.find_all.assert_called_once()
        call_kwargs = mock_repo.find_all.call_args[1]
        assert call_kwargs["ressource_id"] == 5

    def test_list_reservations_filter_by_chantier(self):
        """Liste filtree par chantier."""
        mock_repo = Mock()
        mock_repo.find_all.return_value = []
        mock_repo.count.return_value = 0

        use_case = ListReservationsUseCase(reservation_repository=mock_repo)

        filters = ReservationFiltersDTO(chantier_id=10)
        use_case.execute(filters)

        call_kwargs = mock_repo.find_all.call_args[1]
        assert call_kwargs["chantier_id"] == 10

    def test_list_reservations_filter_by_statut(self):
        """Liste filtree par statut."""
        mock_repo = Mock()
        mock_repo.find_all.return_value = []
        mock_repo.count.return_value = 0

        use_case = ListReservationsUseCase(reservation_repository=mock_repo)

        filters = ReservationFiltersDTO(statut="en_attente")
        use_case.execute(filters)

        call_kwargs = mock_repo.find_all.call_args[1]
        assert call_kwargs["statut"] == "en_attente"

    def test_list_reservations_with_pagination(self):
        """Liste avec pagination."""
        mock_repo = Mock()
        mock_repo.find_all.return_value = []
        mock_repo.count.return_value = 100

        use_case = ListReservationsUseCase(reservation_repository=mock_repo)

        filters = ReservationFiltersDTO(skip=20, limit=10)
        result = use_case.execute(filters)

        assert result.skip == 20
        assert result.limit == 10
        assert result.total == 100


class TestValidateReservationUseCase:
    """Tests pour ValidateReservationUseCase (LOG-11)."""

    def test_validate_reservation_success_admin(self):
        """Validation reussie par admin."""
        mock_repo = Mock()
        today = date.today()
        reservation = Reservation(
            id=1,
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            date_debut=today,
            date_fin=today,
            statut=StatutReservation.EN_ATTENTE,
        )
        mock_repo.find_by_id.return_value = reservation
        mock_repo.save.return_value = reservation

        use_case = ValidateReservationUseCase(reservation_repository=mock_repo)

        dto = ValidateReservationDTO(reservation_id=1, valideur_id=5)
        result = use_case.execute(dto, user_role="admin")

        assert result.statut == "validee"
        mock_repo.save.assert_called_once()

    def test_validate_reservation_success_conducteur(self):
        """Validation reussie par conducteur."""
        mock_repo = Mock()
        today = date.today()
        reservation = Reservation(
            id=1,
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            date_debut=today,
            date_fin=today,
            statut=StatutReservation.EN_ATTENTE,
        )
        mock_repo.find_by_id.return_value = reservation
        mock_repo.save.return_value = reservation

        use_case = ValidateReservationUseCase(reservation_repository=mock_repo)

        dto = ValidateReservationDTO(reservation_id=1, valideur_id=5)
        result = use_case.execute(dto, user_role="conducteur")

        assert result.statut == "validee"

    def test_validate_reservation_success_chef_chantier(self):
        """Validation reussie par chef de chantier."""
        mock_repo = Mock()
        today = date.today()
        reservation = Reservation(
            id=1,
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            date_debut=today,
            date_fin=today,
            statut=StatutReservation.EN_ATTENTE,
        )
        mock_repo.find_by_id.return_value = reservation
        mock_repo.save.return_value = reservation

        use_case = ValidateReservationUseCase(reservation_repository=mock_repo)

        dto = ValidateReservationDTO(reservation_id=1, valideur_id=5)
        result = use_case.execute(dto, user_role="chef_chantier")

        assert result.statut == "validee"

    def test_validate_reservation_access_denied_compagnon(self):
        """Erreur si compagnon essaie de valider."""
        mock_repo = Mock()
        use_case = ValidateReservationUseCase(reservation_repository=mock_repo)

        dto = ValidateReservationDTO(reservation_id=1, valideur_id=5)

        with pytest.raises(ReservationAccessDeniedError, match="chefs.*conducteurs"):
            use_case.execute(dto, user_role="compagnon")

    def test_validate_reservation_not_found(self):
        """Erreur si reservation non trouvee."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        use_case = ValidateReservationUseCase(reservation_repository=mock_repo)

        dto = ValidateReservationDTO(reservation_id=999, valideur_id=5)

        with pytest.raises(ReservationNotFoundError):
            use_case.execute(dto, user_role="admin")

    def test_validate_reservation_invalid_transition(self):
        """Erreur si transition de statut invalide."""
        mock_repo = Mock()
        today = date.today()
        reservation = Reservation(
            id=1,
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            date_debut=today,
            date_fin=today,
            statut=StatutReservation.VALIDEE,  # Deja validee
        )
        mock_repo.find_by_id.return_value = reservation

        use_case = ValidateReservationUseCase(reservation_repository=mock_repo)

        dto = ValidateReservationDTO(reservation_id=1, valideur_id=5)

        with pytest.raises(InvalidStatusTransitionError):
            use_case.execute(dto, user_role="admin")


class TestRefuseReservationUseCase:
    """Tests pour RefuseReservationUseCase (LOG-11, LOG-16)."""

    def test_refuse_reservation_success_with_motif(self):
        """Refus reussi avec motif (LOG-16)."""
        mock_repo = Mock()
        today = date.today()
        reservation = Reservation(
            id=1,
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            date_debut=today,
            date_fin=today,
            statut=StatutReservation.EN_ATTENTE,
        )
        mock_repo.find_by_id.return_value = reservation
        mock_repo.save.return_value = reservation

        use_case = RefuseReservationUseCase(reservation_repository=mock_repo)

        dto = RefuseReservationDTO(
            reservation_id=1,
            valideur_id=5,
            motif="Ressource indisponible cette semaine",
        )
        result = use_case.execute(dto, user_role="admin")

        assert result.statut == "refusee"
        assert result.motif_refus == "Ressource indisponible cette semaine"

    def test_refuse_reservation_success_without_motif(self):
        """Refus reussi sans motif."""
        mock_repo = Mock()
        today = date.today()
        reservation = Reservation(
            id=1,
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            date_debut=today,
            date_fin=today,
            statut=StatutReservation.EN_ATTENTE,
        )
        mock_repo.find_by_id.return_value = reservation
        mock_repo.save.return_value = reservation

        use_case = RefuseReservationUseCase(reservation_repository=mock_repo)

        dto = RefuseReservationDTO(reservation_id=1, valideur_id=5)
        result = use_case.execute(dto, user_role="conducteur")

        assert result.statut == "refusee"

    def test_refuse_reservation_access_denied(self):
        """Erreur si compagnon essaie de refuser."""
        mock_repo = Mock()
        use_case = RefuseReservationUseCase(reservation_repository=mock_repo)

        dto = RefuseReservationDTO(reservation_id=1, valideur_id=5)

        with pytest.raises(ReservationAccessDeniedError):
            use_case.execute(dto, user_role="compagnon")

    def test_refuse_reservation_invalid_transition(self):
        """Erreur si transition de statut invalide."""
        mock_repo = Mock()
        today = date.today()
        reservation = Reservation(
            id=1,
            ressource_id=1,
            chantier_id=1,
            demandeur_id=1,
            date_debut=today,
            date_fin=today,
            statut=StatutReservation.VALIDEE,
        )
        mock_repo.find_by_id.return_value = reservation

        use_case = RefuseReservationUseCase(reservation_repository=mock_repo)

        dto = RefuseReservationDTO(reservation_id=1, valideur_id=5)

        with pytest.raises(InvalidStatusTransitionError):
            use_case.execute(dto, user_role="admin")


class TestCancelReservationUseCase:
    """Tests pour CancelReservationUseCase."""

    def test_cancel_reservation_en_attente_success(self):
        """Annulation d'une reservation en attente par le demandeur."""
        mock_repo = Mock()
        today = date.today()
        reservation = Reservation(
            id=1,
            ressource_id=1,
            chantier_id=1,
            demandeur_id=5,  # Le demandeur
            date_debut=today,
            date_fin=today,
            statut=StatutReservation.EN_ATTENTE,
        )
        mock_repo.find_by_id.return_value = reservation
        mock_repo.save.return_value = reservation

        use_case = CancelReservationUseCase(reservation_repository=mock_repo)
        result = use_case.execute(reservation_id=1, user_id=5)  # Meme user

        assert result.statut == "annulee"

    def test_cancel_reservation_validee_success(self):
        """Annulation d'une reservation validee par le demandeur."""
        mock_repo = Mock()
        today = date.today()
        reservation = Reservation(
            id=1,
            ressource_id=1,
            chantier_id=1,
            demandeur_id=5,
            date_debut=today,
            date_fin=today,
            statut=StatutReservation.VALIDEE,
        )
        mock_repo.find_by_id.return_value = reservation
        mock_repo.save.return_value = reservation

        use_case = CancelReservationUseCase(reservation_repository=mock_repo)
        result = use_case.execute(reservation_id=1, user_id=5)

        assert result.statut == "annulee"

    def test_cancel_reservation_access_denied_not_demandeur(self):
        """Erreur si utilisateur n'est pas le demandeur."""
        mock_repo = Mock()
        today = date.today()
        reservation = Reservation(
            id=1,
            ressource_id=1,
            chantier_id=1,
            demandeur_id=5,  # Demandeur
            date_debut=today,
            date_fin=today,
            statut=StatutReservation.EN_ATTENTE,
        )
        mock_repo.find_by_id.return_value = reservation

        use_case = CancelReservationUseCase(reservation_repository=mock_repo)

        with pytest.raises(ReservationAccessDeniedError, match="demandeur"):
            use_case.execute(reservation_id=1, user_id=10)  # Autre user

    def test_cancel_reservation_not_found(self):
        """Erreur si reservation non trouvee."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        use_case = CancelReservationUseCase(reservation_repository=mock_repo)

        with pytest.raises(ReservationNotFoundError):
            use_case.execute(reservation_id=999, user_id=5)

    def test_cancel_reservation_invalid_transition(self):
        """Erreur si transition invalide (depuis REFUSEE)."""
        mock_repo = Mock()
        today = date.today()
        reservation = Reservation(
            id=1,
            ressource_id=1,
            chantier_id=1,
            demandeur_id=5,
            date_debut=today,
            date_fin=today,
            statut=StatutReservation.REFUSEE,
        )
        mock_repo.find_by_id.return_value = reservation

        use_case = CancelReservationUseCase(reservation_repository=mock_repo)

        with pytest.raises(InvalidStatusTransitionError):
            use_case.execute(reservation_id=1, user_id=5)


class TestGetPlanningRessourceUseCase:
    """Tests pour GetPlanningRessourceUseCase (LOG-03)."""

    def test_get_planning_success(self):
        """Recuperation du planning reussie."""
        mock_reservation_repo = Mock()
        mock_ressource_repo = Mock()

        ressource = Ressource(id=1, code="GRU001", nom="Grue")
        mock_ressource_repo.find_by_id.return_value = ressource

        today = date.today()
        monday = today - timedelta(days=today.weekday())  # Lundi
        reservations = [
            Reservation(
                id=1,
                ressource_id=1,
                chantier_id=1,
                demandeur_id=1,
                date_debut=monday,
                date_fin=monday,
                statut=StatutReservation.VALIDEE,
            ),
            Reservation(
                id=2,
                ressource_id=1,
                chantier_id=2,
                demandeur_id=2,
                date_debut=monday + timedelta(days=2),
                date_fin=monday + timedelta(days=2),
                statut=StatutReservation.EN_ATTENTE,
            ),
        ]
        mock_reservation_repo.find_all.return_value = reservations

        use_case = GetPlanningRessourceUseCase(
            reservation_repository=mock_reservation_repo,
            ressource_repository=mock_ressource_repo,
        )

        result = use_case.execute(ressource_id=1, semaine_debut=monday)

        assert result.ressource.id == 1
        assert len(result.reservations) == 2
        assert result.semaine_debut == monday.isoformat()
        assert result.semaine_fin == (monday + timedelta(days=6)).isoformat()

    def test_get_planning_exclut_reservations_refusees_annulees(self):
        """Planning exclut les reservations refusees et annulees."""
        mock_reservation_repo = Mock()
        mock_ressource_repo = Mock()

        ressource = Ressource(id=1, code="GRU001", nom="Grue")
        mock_ressource_repo.find_by_id.return_value = ressource

        today = date.today()
        monday = today - timedelta(days=today.weekday())
        reservations = [
            Reservation(
                id=1, ressource_id=1, chantier_id=1, demandeur_id=1,
                date_debut=monday, date_fin=monday,
                statut=StatutReservation.VALIDEE,
            ),
            Reservation(
                id=2, ressource_id=1, chantier_id=2, demandeur_id=2,
                date_debut=monday, date_fin=monday,
                statut=StatutReservation.REFUSEE,  # Exclue
            ),
            Reservation(
                id=3, ressource_id=1, chantier_id=3, demandeur_id=3,
                date_debut=monday, date_fin=monday,
                statut=StatutReservation.ANNULEE,  # Exclue
            ),
        ]
        mock_reservation_repo.find_all.return_value = reservations

        use_case = GetPlanningRessourceUseCase(
            reservation_repository=mock_reservation_repo,
            ressource_repository=mock_ressource_repo,
        )

        result = use_case.execute(ressource_id=1, semaine_debut=monday)

        # Seule la reservation VALIDEE doit etre incluse
        assert len(result.reservations) == 1
        assert result.reservations[0].statut == "validee"

    def test_get_planning_ressource_not_found(self):
        """Erreur si ressource non trouvee."""
        mock_reservation_repo = Mock()
        mock_ressource_repo = Mock()
        mock_ressource_repo.find_by_id.return_value = None

        use_case = GetPlanningRessourceUseCase(
            reservation_repository=mock_reservation_repo,
            ressource_repository=mock_ressource_repo,
        )

        today = date.today()

        with pytest.raises(ReservationRessourceNotFoundError, match="999"):
            use_case.execute(ressource_id=999, semaine_debut=today)


class TestGetPendingReservationsUseCase:
    """Tests pour GetPendingReservationsUseCase."""

    def test_get_pending_reservations_success(self):
        """Liste des reservations en attente reussie."""
        mock_repo = Mock()
        today = date.today()
        reservations = [
            Reservation(
                id=1, ressource_id=1, chantier_id=1, demandeur_id=1,
                date_debut=today, date_fin=today,
                statut=StatutReservation.EN_ATTENTE,
            ),
        ]
        mock_repo.find_all.return_value = reservations
        mock_repo.count.return_value = 1

        use_case = GetPendingReservationsUseCase(reservation_repository=mock_repo)
        result = use_case.execute()

        assert len(result.reservations) == 1
        assert result.total == 1

        # Verifier que le filtre statut=EN_ATTENTE est applique
        call_kwargs = mock_repo.find_all.call_args[1]
        assert call_kwargs["statut"] == "en_attente"

    def test_get_pending_reservations_filter_by_ressource(self):
        """Liste filtree par ressource."""
        mock_repo = Mock()
        mock_repo.find_all.return_value = []
        mock_repo.count.return_value = 0

        use_case = GetPendingReservationsUseCase(reservation_repository=mock_repo)
        use_case.execute(ressource_id=5)

        call_kwargs = mock_repo.find_all.call_args[1]
        assert call_kwargs["ressource_id"] == 5
        assert call_kwargs["statut"] == "en_attente"


class TestCheckConflitsUseCase:
    """Tests pour CheckConflitsUseCase (LOG-17)."""

    def test_check_conflits_no_conflict(self):
        """Pas de conflit detecte."""
        mock_repo = Mock()
        mock_repo.find_conflits.return_value = []

        use_case = CheckConflitsUseCase(reservation_repository=mock_repo)

        today = date.today()
        dto = CreateReservationDTO(
            ressource_id=1,
            chantier_id=2,
            demandeur_id=3,
            date_debut=today,
            date_fin=today,
            heure_debut="08:00",
            heure_fin="12:00",
        )

        result = use_case.execute(dto)

        assert result is None

    def test_check_conflits_with_conflicts(self):
        """Conflits detectes."""
        mock_repo = Mock()
        today = date.today()
        conflit = Reservation(
            id=10,
            ressource_id=1,
            chantier_id=5,
            demandeur_id=6,
            date_debut=today,
            date_fin=today,
            heure_debut="08:00",
            heure_fin="12:00",
            statut=StatutReservation.VALIDEE,
        )
        mock_repo.find_conflits.return_value = [conflit]

        use_case = CheckConflitsUseCase(reservation_repository=mock_repo)

        dto = CreateReservationDTO(
            ressource_id=1,
            chantier_id=2,
            demandeur_id=3,
            date_debut=today,
            date_fin=today,
            heure_debut="10:00",
            heure_fin="14:00",
        )

        result = use_case.execute(dto)

        assert result is not None
        assert len(result.reservations_en_conflit) == 1
        assert "1 reservation" in result.message
