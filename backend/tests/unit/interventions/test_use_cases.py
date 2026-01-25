"""Tests unitaires pour les Use Cases du module Interventions."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date, time

from modules.interventions.domain.entities import (
    Intervention,
    AffectationIntervention,
    InterventionMessage,
    TypeMessage,
)
from modules.interventions.domain.value_objects import (
    StatutIntervention,
    PrioriteIntervention,
    TypeIntervention,
)
from modules.interventions.application.dtos import (
    CreateInterventionDTO,
    UpdateInterventionDTO,
    PlanifierInterventionDTO,
    DemarrerInterventionDTO,
    TerminerInterventionDTO,
    InterventionFiltersDTO,
    AffecterTechnicienDTO,
    CreateMessageDTO,
)
from modules.interventions.application.use_cases import (
    CreateInterventionUseCase,
    GetInterventionUseCase,
    ListInterventionsUseCase,
    UpdateInterventionUseCase,
    PlanifierInterventionUseCase,
    DemarrerInterventionUseCase,
    TerminerInterventionUseCase,
    AnnulerInterventionUseCase,
    DeleteInterventionUseCase,
    AffecterTechnicienUseCase,
    DesaffecterTechnicienUseCase,
    ListTechniciensInterventionUseCase,
    AddMessageUseCase,
    ListMessagesUseCase,
)


@pytest.fixture
def mock_intervention_repository():
    """Fixture pour un mock du repository Intervention."""
    return AsyncMock()


@pytest.fixture
def mock_affectation_repository():
    """Fixture pour un mock du repository Affectation."""
    return AsyncMock()


@pytest.fixture
def mock_message_repository():
    """Fixture pour un mock du repository Message."""
    return AsyncMock()


class TestCreateInterventionUseCase:
    """Tests pour CreateInterventionUseCase."""

    @pytest.mark.asyncio
    async def test_create_intervention_success(self, mock_intervention_repository):
        """Verifie la creation d'une intervention."""
        mock_intervention_repository.save.return_value = Intervention(
            id=1,
            code="INT-2026-0001",
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )

        use_case = CreateInterventionUseCase(mock_intervention_repository)

        dto = CreateInterventionDTO(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
        )

        result = await use_case.execute(dto, created_by=1)

        assert result.id == 1
        assert result.code == "INT-2026-0001"
        mock_intervention_repository.save.assert_called_once()


class TestGetInterventionUseCase:
    """Tests pour GetInterventionUseCase."""

    @pytest.mark.asyncio
    async def test_get_intervention_found(self, mock_intervention_repository):
        """Verifie la recuperation d'une intervention existante."""
        intervention = Intervention(
            id=1,
            code="INT-2026-0001",
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )
        mock_intervention_repository.get_by_id.return_value = intervention

        use_case = GetInterventionUseCase(mock_intervention_repository)
        result = await use_case.execute(1)

        assert result is not None
        assert result.id == 1
        mock_intervention_repository.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_intervention_not_found(self, mock_intervention_repository):
        """Verifie le cas ou l'intervention n'existe pas."""
        mock_intervention_repository.get_by_id.return_value = None

        use_case = GetInterventionUseCase(mock_intervention_repository)
        result = await use_case.execute(999)

        assert result is None


class TestListInterventionsUseCase:
    """Tests pour ListInterventionsUseCase."""

    @pytest.mark.asyncio
    async def test_list_interventions_empty(self, mock_intervention_repository):
        """Verifie le listage quand il n'y a pas d'interventions."""
        mock_intervention_repository.list_all.return_value = []
        mock_intervention_repository.count.return_value = 0

        use_case = ListInterventionsUseCase(mock_intervention_repository)
        filters = InterventionFiltersDTO()

        interventions, total = await use_case.execute(filters)

        assert interventions == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_list_interventions_with_filters(self, mock_intervention_repository):
        """Verifie le listage avec filtres."""
        interventions_list = [
            Intervention(
                id=1,
                code="INT-2026-0001",
                type_intervention=TypeIntervention.SAV,
                client_nom="Client 1",
                client_adresse="Adresse 1",
                description="Desc 1",
                created_by=1,
            ),
        ]
        mock_intervention_repository.list_all.return_value = interventions_list
        mock_intervention_repository.count.return_value = 1

        use_case = ListInterventionsUseCase(mock_intervention_repository)
        filters = InterventionFiltersDTO(
            statut=StatutIntervention.A_PLANIFIER,
            priorite=PrioriteIntervention.HAUTE,
        )

        interventions, total = await use_case.execute(filters)

        assert len(interventions) == 1
        assert total == 1
        mock_intervention_repository.list_all.assert_called_once()


class TestUpdateInterventionUseCase:
    """Tests pour UpdateInterventionUseCase."""

    @pytest.mark.asyncio
    async def test_update_intervention_success(self, mock_intervention_repository):
        """Verifie la mise a jour d'une intervention."""
        intervention = Intervention(
            id=1,
            code="INT-2026-0001",
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
        )
        mock_intervention_repository.get_by_id.return_value = intervention
        mock_intervention_repository.save.return_value = intervention

        use_case = UpdateInterventionUseCase(mock_intervention_repository)
        dto = UpdateInterventionDTO(
            priorite=PrioriteIntervention.URGENTE,
            description="Nouvelle description",
        )

        result = await use_case.execute(1, dto)

        assert result is not None
        assert result.priorite == PrioriteIntervention.URGENTE

    @pytest.mark.asyncio
    async def test_update_intervention_not_found(self, mock_intervention_repository):
        """Verifie le cas ou l'intervention n'existe pas."""
        mock_intervention_repository.get_by_id.return_value = None

        use_case = UpdateInterventionUseCase(mock_intervention_repository)
        dto = UpdateInterventionDTO(description="Nouvelle description")

        result = await use_case.execute(999, dto)

        assert result is None


class TestPlanifierInterventionUseCase:
    """Tests pour PlanifierInterventionUseCase."""

    @pytest.mark.asyncio
    async def test_planifier_intervention_success(
        self, mock_intervention_repository, mock_affectation_repository
    ):
        """Verifie la planification d'une intervention."""
        intervention = Intervention(
            id=1,
            code="INT-2026-0001",
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            statut=StatutIntervention.A_PLANIFIER,
        )
        mock_intervention_repository.get_by_id.return_value = intervention
        mock_intervention_repository.save.return_value = intervention
        mock_affectation_repository.exists.return_value = False
        mock_affectation_repository.save.return_value = AffectationIntervention(
            id=1,
            intervention_id=1,
            utilisateur_id=5,
            created_by=1,
        )

        use_case = PlanifierInterventionUseCase(
            mock_intervention_repository, mock_affectation_repository
        )
        dto = PlanifierInterventionDTO(
            date_planifiee=date(2026, 2, 15),
            heure_debut=time(9, 0),
            heure_fin=time(12, 0),
            techniciens_ids=[5],
        )

        result = await use_case.execute(1, dto, planned_by=1)

        assert result is not None
        assert result.statut == StatutIntervention.PLANIFIEE
        assert result.date_planifiee == date(2026, 2, 15)


class TestDemarrerInterventionUseCase:
    """Tests pour DemarrerInterventionUseCase."""

    @pytest.mark.asyncio
    async def test_demarrer_intervention_success(self, mock_intervention_repository):
        """Verifie le demarrage d'une intervention."""
        intervention = Intervention(
            id=1,
            code="INT-2026-0001",
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            statut=StatutIntervention.PLANIFIEE,
        )
        mock_intervention_repository.get_by_id.return_value = intervention
        mock_intervention_repository.save.return_value = intervention

        use_case = DemarrerInterventionUseCase(mock_intervention_repository)
        dto = DemarrerInterventionDTO(heure_debut_reelle=time(9, 15))

        result = await use_case.execute(1, dto)

        assert result is not None
        assert result.statut == StatutIntervention.EN_COURS


class TestTerminerInterventionUseCase:
    """Tests pour TerminerInterventionUseCase."""

    @pytest.mark.asyncio
    async def test_terminer_intervention_success(self, mock_intervention_repository):
        """Verifie la fin d'une intervention."""
        intervention = Intervention(
            id=1,
            code="INT-2026-0001",
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            statut=StatutIntervention.EN_COURS,
        )
        mock_intervention_repository.get_by_id.return_value = intervention
        mock_intervention_repository.save.return_value = intervention

        use_case = TerminerInterventionUseCase(mock_intervention_repository)
        dto = TerminerInterventionDTO(
            heure_fin_reelle=time(11, 30),
            travaux_realises="Travaux effectues",
        )

        result = await use_case.execute(1, dto)

        assert result is not None
        assert result.statut == StatutIntervention.TERMINEE


class TestAnnulerInterventionUseCase:
    """Tests pour AnnulerInterventionUseCase."""

    @pytest.mark.asyncio
    async def test_annuler_intervention_success(self, mock_intervention_repository):
        """Verifie l'annulation d'une intervention."""
        intervention = Intervention(
            id=1,
            code="INT-2026-0001",
            type_intervention=TypeIntervention.SAV,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Description test",
            created_by=1,
            statut=StatutIntervention.PLANIFIEE,
        )
        mock_intervention_repository.get_by_id.return_value = intervention
        mock_intervention_repository.save.return_value = intervention

        use_case = AnnulerInterventionUseCase(mock_intervention_repository)

        result = await use_case.execute(1)

        assert result is not None
        assert result.statut == StatutIntervention.ANNULEE


class TestDeleteInterventionUseCase:
    """Tests pour DeleteInterventionUseCase."""

    @pytest.mark.asyncio
    async def test_delete_intervention_success(self, mock_intervention_repository):
        """Verifie la suppression d'une intervention."""
        mock_intervention_repository.delete.return_value = True

        use_case = DeleteInterventionUseCase(mock_intervention_repository)

        result = await use_case.execute(1, deleted_by=1)

        assert result is True
        mock_intervention_repository.delete.assert_called_once_with(1, 1)

    @pytest.mark.asyncio
    async def test_delete_intervention_not_found(self, mock_intervention_repository):
        """Verifie le cas ou l'intervention n'existe pas."""
        mock_intervention_repository.delete.return_value = False

        use_case = DeleteInterventionUseCase(mock_intervention_repository)

        result = await use_case.execute(999, deleted_by=1)

        assert result is False


class TestAffecterTechnicienUseCase:
    """Tests pour AffecterTechnicienUseCase."""

    @pytest.mark.asyncio
    async def test_affecter_technicien_success(self, mock_affectation_repository):
        """Verifie l'affectation d'un technicien."""
        mock_affectation_repository.exists.return_value = False
        mock_affectation_repository.get_principal.return_value = None
        mock_affectation_repository.save.return_value = AffectationIntervention(
            id=1,
            intervention_id=1,
            utilisateur_id=5,
            est_principal=True,
            created_by=1,
        )

        use_case = AffecterTechnicienUseCase(mock_affectation_repository)
        dto = AffecterTechnicienDTO(utilisateur_id=5, est_principal=True)

        result = await use_case.execute(1, dto, created_by=1)

        assert result.utilisateur_id == 5
        assert result.est_principal is True

    @pytest.mark.asyncio
    async def test_affecter_technicien_deja_affecte(self, mock_affectation_repository):
        """Verifie qu'une erreur est levee si deja affecte."""
        mock_affectation_repository.exists.return_value = True

        use_case = AffecterTechnicienUseCase(mock_affectation_repository)
        dto = AffecterTechnicienDTO(utilisateur_id=5)

        with pytest.raises(ValueError, match="deja affecte"):
            await use_case.execute(1, dto, created_by=1)


class TestAddMessageUseCase:
    """Tests pour AddMessageUseCase."""

    @pytest.mark.asyncio
    async def test_add_commentaire_success(self, mock_message_repository):
        """Verifie l'ajout d'un commentaire."""
        mock_message_repository.save.return_value = InterventionMessage(
            id=1,
            intervention_id=1,
            auteur_id=2,
            type_message=TypeMessage.COMMENTAIRE,
            contenu="Test commentaire",
        )

        use_case = AddMessageUseCase(mock_message_repository)
        dto = CreateMessageDTO(type_message="commentaire", contenu="Test commentaire")

        result = await use_case.execute(1, dto, auteur_id=2)

        assert result.type_message == TypeMessage.COMMENTAIRE
        assert result.contenu == "Test commentaire"

    @pytest.mark.asyncio
    async def test_add_photo_success(self, mock_message_repository):
        """Verifie l'ajout d'une photo."""
        mock_message_repository.save.return_value = InterventionMessage(
            id=1,
            intervention_id=1,
            auteur_id=2,
            type_message=TypeMessage.PHOTO,
            contenu="Photo avant",
            photos_urls=["https://example.com/photo.jpg"],
        )

        use_case = AddMessageUseCase(mock_message_repository)
        dto = CreateMessageDTO(
            type_message="photo",
            contenu="Photo avant",
            photos_urls=["https://example.com/photo.jpg"],
        )

        result = await use_case.execute(1, dto, auteur_id=2)

        assert result.type_message == TypeMessage.PHOTO
        assert len(result.photos_urls) == 1


class TestListMessagesUseCase:
    """Tests pour ListMessagesUseCase."""

    @pytest.mark.asyncio
    async def test_list_messages_success(self, mock_message_repository):
        """Verifie le listage des messages."""
        messages = [
            InterventionMessage(
                id=1,
                intervention_id=1,
                auteur_id=2,
                type_message=TypeMessage.COMMENTAIRE,
                contenu="Message 1",
            ),
            InterventionMessage(
                id=2,
                intervention_id=1,
                auteur_id=2,
                type_message=TypeMessage.PHOTO,
                contenu="Photo",
                photos_urls=["https://example.com/photo.jpg"],
            ),
        ]
        mock_message_repository.list_by_intervention.return_value = messages
        mock_message_repository.count_by_intervention.return_value = 2

        use_case = ListMessagesUseCase(mock_message_repository)

        result_messages, count = await use_case.execute(1)

        assert len(result_messages) == 2
        assert count == 2
