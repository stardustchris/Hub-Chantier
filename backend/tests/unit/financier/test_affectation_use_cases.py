"""Tests unitaires pour les Use Cases d'affectation budget-tache.

FIN-03: Affectation budgets aux taches - tests CRUD et validation.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, MagicMock

from modules.financier.domain.entities.affectation_budget_tache import (
    AffectationBudgetTache,
)
from modules.financier.domain.repositories.affectation_repository import (
    AffectationBudgetTacheRepository,
)
from modules.financier.domain.repositories.lot_budgetaire_repository import (
    LotBudgetaireRepository,
)
from modules.financier.domain.entities import LotBudgetaire
from modules.financier.application.dtos.affectation_dtos import (
    CreateAffectationDTO,
    AffectationBudgetTacheDTO,
    AffectationAvecDetailsDTO,
)
from modules.financier.application.use_cases.affectation_use_cases import (
    CreateAffectationBudgetTacheUseCase,
    DeleteAffectationBudgetTacheUseCase,
    ListAffectationsByChantierUseCase,
    GetAffectationsByTacheUseCase,
    AffectationNotFoundError,
    AllocationDepasseError,
    LotBudgetaireIntrouvableError,
)


class TestCreateAffectationBudgetTacheUseCase:
    """Tests pour le use case de creation d'affectation."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_affectation_repo = Mock(spec=AffectationBudgetTacheRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)

        self.use_case = CreateAffectationBudgetTacheUseCase(
            affectation_repo=self.mock_affectation_repo,
            lot_repo=self.mock_lot_repo,
        )

    def _make_lot(self, lot_id=1, budget_id=10):
        """Helper pour creer un lot budgetaire."""
        return LotBudgetaire(
            id=lot_id,
            budget_id=budget_id,
            code_lot="LOT01",
            libelle="Gros oeuvre",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("100"),
        )

    def _make_affectation(self, aff_id=1, lot_id=1, tache_id=10, pct=Decimal("50")):
        """Helper pour creer une affectation."""
        return AffectationBudgetTache(
            id=aff_id,
            lot_budgetaire_id=lot_id,
            tache_id=tache_id,
            pourcentage_allocation=pct,
            created_at=datetime(2026, 2, 1),
            updated_at=datetime(2026, 2, 1),
        )

    def test_create_success(self):
        """Test: creation reussie d'une affectation."""
        # Arrange
        lot = self._make_lot()
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_affectation_repo.find_by_lot.return_value = []

        saved = self._make_affectation()
        self.mock_affectation_repo.save.return_value = saved

        dto = CreateAffectationDTO(
            lot_budgetaire_id=1,
            tache_id=10,
            pourcentage_allocation=Decimal("50"),
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert isinstance(result, AffectationBudgetTacheDTO)
        assert result.id == 1
        assert result.lot_budgetaire_id == 1
        assert result.tache_id == 10
        assert result.pourcentage_allocation == "50"
        self.mock_affectation_repo.save.assert_called_once()

    def test_create_lot_not_found(self):
        """Test: LotBudgetaireIntrouvableError si le lot n'existe pas."""
        # Arrange
        self.mock_lot_repo.find_by_id.return_value = None
        dto = CreateAffectationDTO(
            lot_budgetaire_id=999,
            tache_id=10,
            pourcentage_allocation=Decimal("50"),
        )

        # Act & Assert
        with pytest.raises(LotBudgetaireIntrouvableError):
            self.use_case.execute(dto)

    def test_create_allocation_depasse_100(self):
        """Test: AllocationDepasseError si somme > 100%."""
        # Arrange
        lot = self._make_lot()
        self.mock_lot_repo.find_by_id.return_value = lot

        # Affectation existante a 80%
        existing = self._make_affectation(pct=Decimal("80"))
        self.mock_affectation_repo.find_by_lot.return_value = [existing]

        dto = CreateAffectationDTO(
            lot_budgetaire_id=1,
            tache_id=20,
            pourcentage_allocation=Decimal("30"),  # 80 + 30 = 110 > 100
        )

        # Act & Assert
        with pytest.raises(AllocationDepasseError):
            self.use_case.execute(dto)

    def test_create_allocation_exactement_100(self):
        """Test: creation reussie si la somme atteint exactement 100%."""
        # Arrange
        lot = self._make_lot()
        self.mock_lot_repo.find_by_id.return_value = lot

        existing = self._make_affectation(pct=Decimal("70"))
        self.mock_affectation_repo.find_by_lot.return_value = [existing]

        saved = self._make_affectation(aff_id=2, tache_id=20, pct=Decimal("30"))
        self.mock_affectation_repo.save.return_value = saved

        dto = CreateAffectationDTO(
            lot_budgetaire_id=1,
            tache_id=20,
            pourcentage_allocation=Decimal("30"),  # 70 + 30 = 100
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result is not None
        self.mock_affectation_repo.save.assert_called_once()

    def test_create_multiple_existing_allocations(self):
        """Test: verification somme avec plusieurs affectations existantes."""
        # Arrange
        lot = self._make_lot()
        self.mock_lot_repo.find_by_id.return_value = lot

        # Affectations existantes: 30% + 40% = 70%
        existing = [
            self._make_affectation(aff_id=1, pct=Decimal("30")),
            self._make_affectation(aff_id=2, tache_id=20, pct=Decimal("40")),
        ]
        self.mock_affectation_repo.find_by_lot.return_value = existing

        # 70 + 35 = 105 > 100 -> erreur
        dto = CreateAffectationDTO(
            lot_budgetaire_id=1,
            tache_id=30,
            pourcentage_allocation=Decimal("35"),
        )

        # Act & Assert
        with pytest.raises(AllocationDepasseError):
            self.use_case.execute(dto)

    def test_create_no_existing_allocations(self):
        """Test: creation reussie quand aucune affectation existante."""
        # Arrange
        lot = self._make_lot()
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_affectation_repo.find_by_lot.return_value = []

        saved = self._make_affectation(pct=Decimal("100"))
        self.mock_affectation_repo.save.return_value = saved

        dto = CreateAffectationDTO(
            lot_budgetaire_id=1,
            tache_id=10,
            pourcentage_allocation=Decimal("100"),
        )

        # Act
        result = self.use_case.execute(dto)

        # Assert
        assert result.pourcentage_allocation == "100"


class TestDeleteAffectationBudgetTacheUseCase:
    """Tests pour le use case de suppression d'affectation."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_affectation_repo = Mock(spec=AffectationBudgetTacheRepository)
        self.use_case = DeleteAffectationBudgetTacheUseCase(
            affectation_repo=self.mock_affectation_repo,
        )

    def test_delete_success(self):
        """Test: suppression reussie."""
        # Arrange
        existing = AffectationBudgetTache(
            id=1, lot_budgetaire_id=1, tache_id=10,
            pourcentage_allocation=Decimal("50"),
        )
        self.mock_affectation_repo.find_by_id.return_value = existing

        # Act
        self.use_case.execute(affectation_id=1)

        # Assert
        self.mock_affectation_repo.delete.assert_called_once_with(1)

    def test_delete_not_found(self):
        """Test: AffectationNotFoundError si l'affectation n'existe pas."""
        # Arrange
        self.mock_affectation_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(AffectationNotFoundError):
            self.use_case.execute(affectation_id=999)

        self.mock_affectation_repo.delete.assert_not_called()


class TestListAffectationsByChantierUseCase:
    """Tests pour le use case de listing par chantier."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_affectation_repo = Mock(spec=AffectationBudgetTacheRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)

        self.use_case = ListAffectationsByChantierUseCase(
            affectation_repo=self.mock_affectation_repo,
            lot_repo=self.mock_lot_repo,
        )

    def test_list_empty(self):
        """Test: retourne une liste vide si pas d'affectations."""
        self.mock_affectation_repo.find_by_chantier.return_value = []

        result = self.use_case.execute(chantier_id=1)

        assert result == []

    def test_list_with_affectations(self):
        """Test: retourne les affectations avec details des lots."""
        # Arrange
        aff = AffectationBudgetTache(
            id=1, lot_budgetaire_id=10, tache_id=100,
            pourcentage_allocation=Decimal("50"),
            created_at=datetime(2026, 2, 1),
            updated_at=datetime(2026, 2, 1),
        )
        self.mock_affectation_repo.find_by_chantier.return_value = [aff]

        lot = LotBudgetaire(
            id=10, budget_id=1, code_lot="LOT01",
            libelle="Gros oeuvre",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("200"),
        )
        self.mock_lot_repo.find_by_id.return_value = lot

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], AffectationAvecDetailsDTO)
        assert result[0].code_lot == "LOT01"
        assert result[0].libelle_lot == "Gros oeuvre"
        assert result[0].total_prevu_ht == str(Decimal("100") * Decimal("200"))
        assert result[0].pourcentage_allocation == "50"

    def test_list_lot_not_found_uses_defaults(self):
        """Test: si le lot n'est pas trouve, valeurs par defaut."""
        # Arrange
        aff = AffectationBudgetTache(
            id=1, lot_budgetaire_id=999, tache_id=100,
            pourcentage_allocation=Decimal("50"),
            created_at=datetime(2026, 2, 1),
            updated_at=datetime(2026, 2, 1),
        )
        self.mock_affectation_repo.find_by_chantier.return_value = [aff]
        self.mock_lot_repo.find_by_id.return_value = None

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        assert len(result) == 1
        assert result[0].code_lot == ""
        assert result[0].libelle_lot == ""
        assert result[0].total_prevu_ht == str(Decimal("0"))

    def test_list_caches_lots(self):
        """Test: les lots sont mis en cache pour eviter les doublons."""
        # Arrange
        aff1 = AffectationBudgetTache(
            id=1, lot_budgetaire_id=10, tache_id=100,
            pourcentage_allocation=Decimal("30"),
        )
        aff2 = AffectationBudgetTache(
            id=2, lot_budgetaire_id=10, tache_id=200,
            pourcentage_allocation=Decimal("40"),
        )
        self.mock_affectation_repo.find_by_chantier.return_value = [aff1, aff2]

        lot = LotBudgetaire(
            id=10, budget_id=1, code_lot="LOT01",
            libelle="Gros oeuvre",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("200"),
        )
        self.mock_lot_repo.find_by_id.return_value = lot

        # Act
        result = self.use_case.execute(chantier_id=1)

        # Assert
        assert len(result) == 2
        # find_by_id appele une seule fois grace au cache
        self.mock_lot_repo.find_by_id.assert_called_once_with(10)


class TestGetAffectationsByTacheUseCase:
    """Tests pour le use case de recuperation par tache."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_affectation_repo = Mock(spec=AffectationBudgetTacheRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)

        self.use_case = GetAffectationsByTacheUseCase(
            affectation_repo=self.mock_affectation_repo,
            lot_repo=self.mock_lot_repo,
        )

    def test_get_by_tache_empty(self):
        """Test: retourne une liste vide si pas d'affectations pour la tache."""
        self.mock_affectation_repo.find_by_tache.return_value = []

        result = self.use_case.execute(tache_id=1)

        assert result == []

    def test_get_by_tache_with_affectations(self):
        """Test: retourne les affectations avec details des lots."""
        # Arrange
        aff = AffectationBudgetTache(
            id=1, lot_budgetaire_id=10, tache_id=100,
            pourcentage_allocation=Decimal("60"),
            created_at=datetime(2026, 2, 1),
            updated_at=datetime(2026, 2, 1),
        )
        self.mock_affectation_repo.find_by_tache.return_value = [aff]

        lot = LotBudgetaire(
            id=10, budget_id=1, code_lot="LOT02",
            libelle="Electricite",
            quantite_prevue=Decimal("50"),
            prix_unitaire_ht=Decimal("300"),
        )
        self.mock_lot_repo.find_by_id.return_value = lot

        # Act
        result = self.use_case.execute(tache_id=100)

        # Assert
        assert len(result) == 1
        assert result[0].code_lot == "LOT02"
        assert result[0].libelle_lot == "Electricite"
        assert result[0].total_prevu_ht == str(Decimal("50") * Decimal("300"))

    def test_get_by_tache_lot_not_found(self):
        """Test: valeurs par defaut si lot non trouve."""
        aff = AffectationBudgetTache(
            id=1, lot_budgetaire_id=999, tache_id=100,
            pourcentage_allocation=Decimal("50"),
        )
        self.mock_affectation_repo.find_by_tache.return_value = [aff]
        self.mock_lot_repo.find_by_id.return_value = None

        result = self.use_case.execute(tache_id=100)

        assert len(result) == 1
        assert result[0].code_lot == ""
        assert result[0].total_prevu_ht == str(Decimal("0"))

    def test_get_by_tache_multiple_lots(self):
        """Test: une tache peut avoir plusieurs lots affectes."""
        # Arrange
        aff1 = AffectationBudgetTache(
            id=1, lot_budgetaire_id=10, tache_id=100,
            pourcentage_allocation=Decimal("30"),
        )
        aff2 = AffectationBudgetTache(
            id=2, lot_budgetaire_id=20, tache_id=100,
            pourcentage_allocation=Decimal("50"),
        )
        self.mock_affectation_repo.find_by_tache.return_value = [aff1, aff2]

        lot1 = LotBudgetaire(
            id=10, budget_id=1, code_lot="LOT01",
            libelle="Gros oeuvre",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("100"),
        )
        lot2 = LotBudgetaire(
            id=20, budget_id=1, code_lot="LOT02",
            libelle="Electricite",
            quantite_prevue=Decimal("50"),
            prix_unitaire_ht=Decimal("200"),
        )
        self.mock_lot_repo.find_by_id.side_effect = lambda lid: lot1 if lid == 10 else lot2

        # Act
        result = self.use_case.execute(tache_id=100)

        # Assert
        assert len(result) == 2
        assert result[0].code_lot == "LOT01"
        assert result[1].code_lot == "LOT02"


class TestAffectationExceptions:
    """Tests pour les exceptions custom."""

    def test_affectation_not_found_error_default(self):
        """Test: message par defaut."""
        err = AffectationNotFoundError()
        assert err.message == "Affectation non trouvee"

    def test_affectation_not_found_error_custom(self):
        """Test: message personnalise."""
        err = AffectationNotFoundError("Affectation 42 non trouvee")
        assert "42" in err.message

    def test_allocation_depasse_error_default(self):
        """Test: message par defaut."""
        err = AllocationDepasseError()
        assert "100%" in err.message

    def test_lot_introuvable_error_default(self):
        """Test: message par defaut."""
        err = LotBudgetaireIntrouvableError()
        assert "Lot budgetaire" in err.message
