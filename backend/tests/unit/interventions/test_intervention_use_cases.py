"""Tests unitaires pour les use cases du module Interventions.

Couvre: CreateIntervention, GetIntervention, ListInterventions,
UpdateIntervention, PlanifierIntervention, DemarrerIntervention,
TerminerIntervention, AnnulerIntervention, DeleteIntervention.
"""

import pytest
from datetime import date, time
from unittest.mock import MagicMock

from modules.interventions.domain.entities import Intervention
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
)


def _make_intervention(**overrides) -> Intervention:
    """Helper pour créer une intervention de test."""
    defaults = {
        "id": 1,
        "code": "INT-2026-0001",
        "type_intervention": TypeIntervention.DEPANNAGE,
        "client_nom": "Client Test",
        "client_adresse": "123 Rue Test",
        "description": "Description test",
        "created_by": 1,
        "statut": StatutIntervention.A_PLANIFIER,
        "priorite": PrioriteIntervention.NORMALE,
    }
    defaults.update(overrides)
    return Intervention(**defaults)


# ============ CREATE ============


class TestCreateInterventionUseCase:
    """Tests pour CreateInterventionUseCase."""

    def test_create_success(self):
        """Test: création réussie d'une intervention."""
        repo = MagicMock()

        def mock_save(intervention):
            intervention.id = 1
            intervention.code = "INT-2026-0001"
            return intervention

        repo.save.side_effect = mock_save

        use_case = CreateInterventionUseCase(repo)
        dto = CreateInterventionDTO(
            type_intervention=TypeIntervention.DEPANNAGE,
            client_nom="Client Test",
            client_adresse="123 Rue Test",
            description="Fuite eau chaude",
            date_souhaitee=date(2026, 3, 15),
            priorite=PrioriteIntervention.HAUTE,
        )

        result = use_case.execute(dto, created_by=5)

        assert result.id == 1
        assert result.client_nom == "Client Test"
        assert result.created_by == 5
        repo.save.assert_called_once()

    def test_create_with_chantier_origine(self):
        """Test: création liée à un chantier (SAV)."""
        repo = MagicMock()
        repo.save.side_effect = lambda i: setattr(i, "id", 2) or i

        use_case = CreateInterventionUseCase(repo)
        dto = CreateInterventionDTO(
            type_intervention=TypeIntervention.SAV,
            client_nom="Client SAV",
            client_adresse="456 Rue SAV",
            description="Problème post-livraison",
            chantier_origine_id=10,
        )

        result = use_case.execute(dto, created_by=3)
        assert result.chantier_origine_id == 10


# ============ GET ============


class TestGetInterventionUseCase:
    """Tests pour GetInterventionUseCase."""

    def test_get_found(self):
        """Test: intervention trouvée."""
        repo = MagicMock()
        intervention = _make_intervention()
        repo.get_by_id.return_value = intervention

        use_case = GetInterventionUseCase(repo)
        result = use_case.execute(1)

        assert result.id == 1
        repo.get_by_id.assert_called_once_with(1)

    def test_get_not_found(self):
        """Test: intervention non trouvée."""
        repo = MagicMock()
        repo.get_by_id.return_value = None

        use_case = GetInterventionUseCase(repo)
        result = use_case.execute(999)

        assert result is None

    def test_get_by_code(self):
        """Test: recherche par code."""
        repo = MagicMock()
        intervention = _make_intervention()
        repo.get_by_code.return_value = intervention

        use_case = GetInterventionUseCase(repo)
        result = use_case.by_code("INT-2026-0001")

        assert result.code == "INT-2026-0001"


# ============ LIST ============


class TestListInterventionsUseCase:
    """Tests pour ListInterventionsUseCase."""

    def test_list_with_filters(self):
        """Test: listing avec filtres."""
        repo = MagicMock()
        interventions = [_make_intervention(id=1), _make_intervention(id=2)]
        repo.list_all.return_value = interventions
        repo.count.return_value = 2

        use_case = ListInterventionsUseCase(repo)
        filters = InterventionFiltersDTO(
            statut=StatutIntervention.A_PLANIFIER,
            limit=10,
            offset=0,
        )

        result_list, total = use_case.execute(filters)

        assert len(result_list) == 2
        assert total == 2

    def test_list_empty(self):
        """Test: listing vide."""
        repo = MagicMock()
        repo.list_all.return_value = []
        repo.count.return_value = 0

        use_case = ListInterventionsUseCase(repo)
        filters = InterventionFiltersDTO(limit=10, offset=0)

        result_list, total = use_case.execute(filters)

        assert result_list == []
        assert total == 0


# ============ UPDATE ============


class TestUpdateInterventionUseCase:
    """Tests pour UpdateInterventionUseCase."""

    def test_update_success(self):
        """Test: mise à jour réussie."""
        repo = MagicMock()
        intervention = _make_intervention()
        repo.get_by_id.return_value = intervention
        repo.save.return_value = intervention

        use_case = UpdateInterventionUseCase(repo)
        dto = UpdateInterventionDTO(description="Nouvelle description")

        result = use_case.execute(1, dto)

        assert result is not None
        repo.save.assert_called_once()

    def test_update_not_found(self):
        """Test: intervention non trouvée."""
        repo = MagicMock()
        repo.get_by_id.return_value = None

        use_case = UpdateInterventionUseCase(repo)
        dto = UpdateInterventionDTO(description="test")

        result = use_case.execute(999, dto)
        assert result is None

    def test_update_non_modifiable_raises(self):
        """Test: erreur si intervention annulée (seul statut non-modifiable)."""
        repo = MagicMock()
        intervention = _make_intervention(statut=StatutIntervention.ANNULEE)
        repo.get_by_id.return_value = intervention

        use_case = UpdateInterventionUseCase(repo)
        dto = UpdateInterventionDTO(description="test")

        with pytest.raises(ValueError, match="ne peut plus etre modifiee"):
            use_case.execute(1, dto)


# ============ PLANIFIER ============


class TestPlanifierInterventionUseCase:
    """Tests pour PlanifierInterventionUseCase."""

    def test_planifier_success(self):
        """Test: planification réussie."""
        repo = MagicMock()
        affectation_repo = MagicMock()
        intervention = _make_intervention()
        repo.get_by_id.return_value = intervention
        repo.save.return_value = intervention
        affectation_repo.exists.return_value = False

        use_case = PlanifierInterventionUseCase(repo, affectation_repo)
        dto = PlanifierInterventionDTO(
            date_planifiee=date(2026, 3, 20),
            heure_debut=time(9, 0),
            heure_fin=time(17, 0),
            techniciens_ids=[5, 6],
        )

        result = use_case.execute(1, dto, planned_by=3)

        assert result is not None
        # 2 techniciens affectés
        assert affectation_repo.save.call_count == 2

    def test_planifier_not_found(self):
        """Test: intervention non trouvée."""
        repo = MagicMock()
        affectation_repo = MagicMock()
        repo.get_by_id.return_value = None

        use_case = PlanifierInterventionUseCase(repo, affectation_repo)
        dto = PlanifierInterventionDTO(
            date_planifiee=date(2026, 3, 20),
            techniciens_ids=[5],
        )

        result = use_case.execute(999, dto, planned_by=3)
        assert result is None

    def test_planifier_skip_already_assigned(self):
        """Test: ne duplique pas les affectations existantes."""
        repo = MagicMock()
        affectation_repo = MagicMock()
        intervention = _make_intervention()
        repo.get_by_id.return_value = intervention
        repo.save.return_value = intervention
        affectation_repo.exists.return_value = True  # déjà affecté

        use_case = PlanifierInterventionUseCase(repo, affectation_repo)
        dto = PlanifierInterventionDTO(
            date_planifiee=date(2026, 3, 20),
            techniciens_ids=[5],
        )

        use_case.execute(1, dto, planned_by=3)
        affectation_repo.save.assert_not_called()


# ============ DEMARRER ============


class TestDemarrerInterventionUseCase:
    """Tests pour DemarrerInterventionUseCase."""

    def test_demarrer_success(self):
        """Test: démarrage réussi."""
        repo = MagicMock()
        intervention = _make_intervention(statut=StatutIntervention.PLANIFIEE)
        repo.get_by_id.return_value = intervention
        repo.save.return_value = intervention

        use_case = DemarrerInterventionUseCase(repo)
        dto = DemarrerInterventionDTO(heure_debut_reelle=time(8, 30))

        result = use_case.execute(1, dto)
        assert result is not None

    def test_demarrer_not_found(self):
        """Test: intervention non trouvée."""
        repo = MagicMock()
        repo.get_by_id.return_value = None

        use_case = DemarrerInterventionUseCase(repo)
        dto = DemarrerInterventionDTO()

        result = use_case.execute(999, dto)
        assert result is None


# ============ TERMINER ============


class TestTerminerInterventionUseCase:
    """Tests pour TerminerInterventionUseCase."""

    def test_terminer_success(self):
        """Test: terminaison réussie."""
        repo = MagicMock()
        intervention = _make_intervention(statut=StatutIntervention.EN_COURS)
        repo.get_by_id.return_value = intervention
        repo.save.return_value = intervention

        use_case = TerminerInterventionUseCase(repo)
        dto = TerminerInterventionDTO(
            heure_fin_reelle=time(17, 30),
            travaux_realises="Remplacement joints",
            anomalies=None,
        )

        result = use_case.execute(1, dto)
        assert result is not None

    def test_terminer_not_found(self):
        """Test: intervention non trouvée."""
        repo = MagicMock()
        repo.get_by_id.return_value = None

        use_case = TerminerInterventionUseCase(repo)
        dto = TerminerInterventionDTO()

        result = use_case.execute(999, dto)
        assert result is None


# ============ ANNULER ============


class TestAnnulerInterventionUseCase:
    """Tests pour AnnulerInterventionUseCase."""

    def test_annuler_success(self):
        """Test: annulation réussie."""
        repo = MagicMock()
        intervention = _make_intervention()
        repo.get_by_id.return_value = intervention
        repo.save.return_value = intervention

        use_case = AnnulerInterventionUseCase(repo)
        result = use_case.execute(1)

        assert result is not None

    def test_annuler_not_found(self):
        """Test: intervention non trouvée."""
        repo = MagicMock()
        repo.get_by_id.return_value = None

        use_case = AnnulerInterventionUseCase(repo)
        result = use_case.execute(999)

        assert result is None


# ============ DELETE ============


class TestDeleteInterventionUseCase:
    """Tests pour DeleteInterventionUseCase."""

    def test_delete_success(self):
        """Test: suppression réussie."""
        repo = MagicMock()
        repo.delete.return_value = True

        use_case = DeleteInterventionUseCase(repo)
        result = use_case.execute(1, deleted_by=5)

        assert result is True
        repo.delete.assert_called_once_with(1, 5)

    def test_delete_not_found(self):
        """Test: intervention non trouvée."""
        repo = MagicMock()
        repo.delete.return_value = False

        use_case = DeleteInterventionUseCase(repo)
        result = use_case.execute(999, deleted_by=5)

        assert result is False
