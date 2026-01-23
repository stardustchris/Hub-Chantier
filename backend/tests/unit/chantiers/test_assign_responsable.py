"""Tests unitaires pour AssignResponsableUseCase."""

import pytest
from unittest.mock import Mock

from modules.chantiers.domain.entities import Chantier
from modules.chantiers.domain.value_objects import CodeChantier, StatutChantier
from modules.chantiers.domain.repositories import ChantierRepository
from modules.chantiers.application.use_cases.assign_responsable import (
    AssignResponsableUseCase,
    InvalidRoleTypeError,
)
from modules.chantiers.application.use_cases.get_chantier import ChantierNotFoundError
from modules.chantiers.application.dtos import AssignResponsableDTO


class TestAssignResponsableUseCase:
    """Tests pour le use case d'assignation de responsable."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_chantier_repo = Mock(spec=ChantierRepository)
        self.use_case = AssignResponsableUseCase(chantier_repo=self.mock_chantier_repo)

        self.chantier = Chantier(
            id=1,
            nom="Chantier Test",
            code=CodeChantier("A001"),
            adresse="1 Rue Test",
            statut=StatutChantier.ouvert(),
        )

    def test_assign_conducteur_success(self):
        """Test: assignation réussie d'un conducteur."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier
        self.mock_chantier_repo.save.return_value = self.chantier

        dto = AssignResponsableDTO(user_id=10, role_type="conducteur")

        result = self.use_case.execute(1, dto)

        self.mock_chantier_repo.save.assert_called_once()

    def test_assign_chef_chantier_success(self):
        """Test: assignation réussie d'un chef de chantier."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier
        self.mock_chantier_repo.save.return_value = self.chantier

        dto = AssignResponsableDTO(user_id=20, role_type="chef_chantier")

        result = self.use_case.execute(1, dto)

        self.mock_chantier_repo.save.assert_called_once()

    def test_assign_chef_alias_success(self):
        """Test: assignation avec alias 'chef'."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier
        self.mock_chantier_repo.save.return_value = self.chantier

        dto = AssignResponsableDTO(user_id=20, role_type="chef")

        result = self.use_case.execute(1, dto)

        self.mock_chantier_repo.save.assert_called_once()

    def test_assign_chantier_not_found(self):
        """Test: échec si chantier non trouvé."""
        self.mock_chantier_repo.find_by_id.return_value = None

        dto = AssignResponsableDTO(user_id=10, role_type="conducteur")

        with pytest.raises(ChantierNotFoundError):
            self.use_case.execute(999, dto)

    def test_assign_invalid_role_type(self):
        """Test: échec si type de rôle invalide."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier

        dto = AssignResponsableDTO(user_id=10, role_type="invalid_role")

        with pytest.raises(InvalidRoleTypeError) as exc_info:
            self.use_case.execute(1, dto)

        assert exc_info.value.role_type == "invalid_role"

    def test_assigner_conducteur_shortcut(self):
        """Test: raccourci assigner_conducteur."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier
        self.mock_chantier_repo.save.return_value = self.chantier

        result = self.use_case.assigner_conducteur(1, user_id=10)

        self.mock_chantier_repo.save.assert_called_once()

    def test_assigner_chef_chantier_shortcut(self):
        """Test: raccourci assigner_chef_chantier."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier
        self.mock_chantier_repo.save.return_value = self.chantier

        result = self.use_case.assigner_chef_chantier(1, user_id=20)

        self.mock_chantier_repo.save.assert_called_once()

    def test_retirer_conducteur_success(self):
        """Test: retrait réussi d'un conducteur."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier
        self.mock_chantier_repo.save.return_value = self.chantier

        result = self.use_case.retirer_conducteur(1, user_id=10)

        self.mock_chantier_repo.save.assert_called_once()

    def test_retirer_conducteur_not_found(self):
        """Test: échec retrait si chantier non trouvé."""
        self.mock_chantier_repo.find_by_id.return_value = None

        with pytest.raises(ChantierNotFoundError):
            self.use_case.retirer_conducteur(999, user_id=10)

    def test_retirer_chef_chantier_success(self):
        """Test: retrait réussi d'un chef de chantier."""
        self.mock_chantier_repo.find_by_id.return_value = self.chantier
        self.mock_chantier_repo.save.return_value = self.chantier

        result = self.use_case.retirer_chef_chantier(1, user_id=20)

        self.mock_chantier_repo.save.assert_called_once()

    def test_retirer_chef_chantier_not_found(self):
        """Test: échec retrait chef si chantier non trouvé."""
        self.mock_chantier_repo.find_by_id.return_value = None

        with pytest.raises(ChantierNotFoundError):
            self.use_case.retirer_chef_chantier(999, user_id=20)

    def test_assign_publishes_conducteur_event(self):
        """Test: publication event ConducteurAssigneEvent."""
        mock_publisher = Mock()
        use_case = AssignResponsableUseCase(
            chantier_repo=self.mock_chantier_repo,
            event_publisher=mock_publisher,
        )

        self.mock_chantier_repo.find_by_id.return_value = self.chantier
        self.mock_chantier_repo.save.return_value = self.chantier

        dto = AssignResponsableDTO(user_id=10, role_type="conducteur")

        use_case.execute(1, dto)

        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.chantier_id == 1
        assert event.conducteur_id == 10

    def test_assign_publishes_chef_event(self):
        """Test: publication event ChefChantierAssigneEvent."""
        mock_publisher = Mock()
        use_case = AssignResponsableUseCase(
            chantier_repo=self.mock_chantier_repo,
            event_publisher=mock_publisher,
        )

        self.mock_chantier_repo.find_by_id.return_value = self.chantier
        self.mock_chantier_repo.save.return_value = self.chantier

        dto = AssignResponsableDTO(user_id=20, role_type="chef_chantier")

        use_case.execute(1, dto)

        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.chantier_id == 1
        assert event.chef_id == 20
