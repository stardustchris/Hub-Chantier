"""Tests unitaires pour les Use Cases Evolution du module Financier.

FIN-17 Phase 2: Tests pour l'évolution financière temporelle.
Tests du use case GetEvolutionFinanciereUseCase avec calcul des courbes
prévu/engagé/réalisé cumulées par mois.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import Mock

from modules.financier.domain.entities import (
    Achat,
    Budget,
)
from modules.financier.domain.repositories import (
    BudgetRepository,
    AchatRepository,
)
from modules.financier.domain.value_objects import StatutAchat
from modules.financier.application.use_cases.evolution_use_cases import (
    GetEvolutionFinanciereUseCase,
)
from modules.financier.application.use_cases.budget_use_cases import (
    BudgetNotFoundError,
)


class TestGetEvolutionFinanciereUseCase:
    """Tests pour le use case d'évolution financière mensuelle."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.use_case = GetEvolutionFinanciereUseCase(
            budget_repository=self.mock_budget_repo,
            achat_repository=self.mock_achat_repo,
        )

    def test_evolution_nominal_success(self):
        """Test: calcul nominal avec 3 achats sur 2 mois différents."""
        # Arrange
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("10000"),
            montant_avenants_ht=Decimal("2000"),
            created_at=datetime(2026, 1, 1),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # 3 achats: 2 en janvier, 1 en février
        # Janvier: VALIDE (engage), COMMANDE (engage)
        # Février: FACTURE (engage et realise)
        achats = [
            Achat(
                id=1,
                chantier_id=100,
                libelle="Ciment",
                quantite=Decimal("10"),
                prix_unitaire_ht=Decimal("500"),
                statut=StatutAchat.VALIDE,
                created_at=datetime(2026, 1, 5),
            ),
            Achat(
                id=2,
                chantier_id=100,
                libelle="Sable",
                quantite=Decimal("5"),
                prix_unitaire_ht=Decimal("400"),
                statut=StatutAchat.COMMANDE,
                created_at=datetime(2026, 1, 10),
            ),
            Achat(
                id=3,
                chantier_id=100,
                libelle="Gravier",
                quantite=Decimal("8"),
                prix_unitaire_ht=Decimal("300"),
                statut=StatutAchat.FACTURE,
                created_at=datetime(2026, 2, 15),
            ),
        ]
        self.mock_achat_repo.find_by_chantier.return_value = achats

        # Act
        result = self.use_case.execute(chantier_id=100)

        # Assert
        assert result.chantier_id == 100
        assert len(result.points) == 2  # 2 mois: jan et fev 2026

        # Montant révisé: 10000 + 2000 = 12000
        # Par mois: 12000 / 2 = 6000
        point_jan = result.points[0]
        assert point_jan.mois == "01/2026"
        assert point_jan.prevu_cumule == "6000.00"
        # Janvier: 2 achats engagés (VALIDE + COMMANDE) = 5000 + 2000 = 7000
        assert point_jan.engage_cumule == "7000.00"
        # Janvier: aucun achat réalisé (FACTURE)
        assert point_jan.realise_cumule == "0.00"

        point_fev = result.points[1]
        assert point_fev.mois == "02/2026"
        assert point_fev.prevu_cumule == "12000.00"  # cumule
        # Février: nouveau mois avec 1 FACTURE = 2400 -> cumule: 7000 + 2400
        assert point_fev.engage_cumule == "9400.00"
        # Février: 1 FACTURE = 2400 -> cumule: 0 + 2400
        assert point_fev.realise_cumule == "2400.00"

    def test_evolution_budget_not_found(self):
        """Test: erreur si pas de budget pour le chantier."""
        # Arrange
        self.mock_budget_repo.find_by_chantier_id.return_value = None

        # Act & Assert
        with pytest.raises(BudgetNotFoundError):
            self.use_case.execute(chantier_id=999)

    def test_evolution_no_achats(self):
        """Test: retourne points avec prévu cumulé seulement, engagé/réalisé à 0."""
        # Arrange
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("5000"),
            montant_avenants_ht=Decimal("1000"),
            created_at=datetime(2026, 1, 1),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget
        self.mock_achat_repo.find_by_chantier.return_value = []

        # Act
        result = self.use_case.execute(chantier_id=100)

        # Assert
        assert result.chantier_id == 100
        # Budget créé en jan, aujourd'hui fév -> 2 mois
        assert len(result.points) == 2

        # Montant révisé: 5000 + 1000 = 6000
        # Par mois: 6000 / 2 = 3000
        point_jan = result.points[0]
        assert point_jan.mois == "01/2026"
        assert point_jan.prevu_cumule == "3000.00"
        assert point_jan.engage_cumule == "0.00"
        assert point_jan.realise_cumule == "0.00"

        point_fev = result.points[1]
        assert point_fev.mois == "02/2026"
        assert point_fev.prevu_cumule == "6000.00"  # cumulé
        assert point_fev.engage_cumule == "0.00"
        assert point_fev.realise_cumule == "0.00"

    def test_evolution_single_month(self):
        """Test: un seul mois retourne un seul point."""
        # Arrange
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("3000"),
            montant_avenants_ht=Decimal("0"),
            created_at=datetime(2026, 2, 1),  # Budget créé aujourd'hui
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        achat = [
            Achat(
                id=1,
                chantier_id=100,
                libelle="Outil",
                quantite=Decimal("1"),
                prix_unitaire_ht=Decimal("1000"),
                statut=StatutAchat.VALIDE,
                created_at=datetime(2026, 2, 1),
            ),
        ]
        self.mock_achat_repo.find_by_chantier.return_value = achat

        # Act
        result = self.use_case.execute(chantier_id=100)

        # Assert
        assert len(result.points) == 1
        point = result.points[0]
        assert point.mois == "02/2026"
        assert point.prevu_cumule == "3000.00"
        assert point.engage_cumule == "1000.00"
        assert point.realise_cumule == "0.00"

    def test_evolution_different_statuts(self):
        """Test: achats avec différents statuts (engagés vs réalisés)."""
        # Arrange
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("20000"),
            montant_avenants_ht=Decimal("0"),
            created_at=datetime(2026, 1, 1),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        # Achats avec différents statuts
        achats = [
            # DEMANDE - n'est pas engagé
            Achat(
                id=1,
                chantier_id=100,
                libelle="Achat DEMANDE",
                quantite=Decimal("1"),
                prix_unitaire_ht=Decimal("1000"),
                statut=StatutAchat.DEMANDE,
                created_at=datetime(2026, 1, 5),
            ),
            # VALIDE - est engagé
            Achat(
                id=2,
                chantier_id=100,
                libelle="Achat VALIDE",
                quantite=Decimal("1"),
                prix_unitaire_ht=Decimal("2000"),
                statut=StatutAchat.VALIDE,
                created_at=datetime(2026, 1, 5),
            ),
            # COMMANDE - est engagé
            Achat(
                id=3,
                chantier_id=100,
                libelle="Achat COMMANDE",
                quantite=Decimal("1"),
                prix_unitaire_ht=Decimal("3000"),
                statut=StatutAchat.COMMANDE,
                created_at=datetime(2026, 1, 5),
            ),
            # LIVRE - est engagé
            Achat(
                id=4,
                chantier_id=100,
                libelle="Achat LIVRE",
                quantite=Decimal("1"),
                prix_unitaire_ht=Decimal("4000"),
                statut=StatutAchat.LIVRE,
                created_at=datetime(2026, 1, 5),
            ),
            # FACTURE - est engagé ET réalisé
            Achat(
                id=5,
                chantier_id=100,
                libelle="Achat FACTURE",
                quantite=Decimal("1"),
                prix_unitaire_ht=Decimal("5000"),
                statut=StatutAchat.FACTURE,
                created_at=datetime(2026, 1, 5),
            ),
            # REFUSE - n'est pas engagé
            Achat(
                id=6,
                chantier_id=100,
                libelle="Achat REFUSE",
                quantite=Decimal("1"),
                prix_unitaire_ht=Decimal("1000"),
                statut=StatutAchat.REFUSE,
                created_at=datetime(2026, 1, 5),
            ),
        ]
        self.mock_achat_repo.find_by_chantier.return_value = achats

        # Act
        result = self.use_case.execute(chantier_id=100)

        # Assert
        # Budget créé en jan, aujourd'hui fév -> 2 mois
        assert len(result.points) == 2

        # Prévu: 20000 / 2 mois = 10000 par mois
        # Janvier: tous les achats sont en jan
        point_jan = result.points[0]
        assert point_jan.mois == "01/2026"
        assert point_jan.prevu_cumule == "10000.00"

        # Engagés: VALIDE + COMMANDE + LIVRE + FACTURE
        # = 2000 + 3000 + 4000 + 5000 = 14000
        assert point_jan.engage_cumule == "14000.00"

        # Réalisés: FACTURE uniquement = 5000
        assert point_jan.realise_cumule == "5000.00"

        # Février: cumul des mois précédents (pas d'achats en février)
        point_fev = result.points[1]
        assert point_fev.mois == "02/2026"
        assert point_fev.prevu_cumule == "20000.00"  # cumulé
        assert point_fev.engage_cumule == "14000.00"  # cumul, pas de nouveaux achats
        assert point_fev.realise_cumule == "5000.00"  # cumul, pas de nouveaux achats

    def test_evolution_achats_without_created_at(self):
        """Test: achats sans created_at sont ignorés."""
        # Arrange
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("5000"),
            montant_avenants_ht=Decimal("0"),
            created_at=datetime(2026, 1, 1),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        achats = [
            Achat(
                id=1,
                chantier_id=100,
                libelle="Avec date",
                quantite=Decimal("1"),
                prix_unitaire_ht=Decimal("2000"),
                statut=StatutAchat.VALIDE,
                created_at=datetime(2026, 1, 5),
            ),
            Achat(
                id=2,
                chantier_id=100,
                libelle="Sans date",
                quantite=Decimal("1"),
                prix_unitaire_ht=Decimal("3000"),
                statut=StatutAchat.VALIDE,
                created_at=None,
            ),
        ]
        self.mock_achat_repo.find_by_chantier.return_value = achats

        # Act
        result = self.use_case.execute(chantier_id=100)

        # Assert
        point = result.points[0]
        # Seul l'achat avec date est compté
        assert point.engage_cumule == "2000.00"
        assert point.realise_cumule == "0.00"

    def test_evolution_cumulation_multi_months(self):
        """Test: vérification de la cumulation correcte sur 3 mois."""
        # Arrange
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("30000"),
            montant_avenants_ht=Decimal("0"),
            created_at=datetime(2025, 12, 1),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        achats = [
            # Janvier: 5000 engagé, 0 réalisé
            Achat(
                id=1,
                chantier_id=100,
                libelle="Jan-1",
                quantite=Decimal("1"),
                prix_unitaire_ht=Decimal("5000"),
                statut=StatutAchat.VALIDE,
                created_at=datetime(2026, 1, 5),
            ),
            # Février: 6000 engagé, 3000 réalisé
            Achat(
                id=2,
                chantier_id=100,
                libelle="Feb-1",
                quantite=Decimal("1"),
                prix_unitaire_ht=Decimal("6000"),
                statut=StatutAchat.COMMANDE,
                created_at=datetime(2026, 2, 5),
            ),
            Achat(
                id=3,
                chantier_id=100,
                libelle="Feb-2",
                quantite=Decimal("1"),
                prix_unitaire_ht=Decimal("3000"),
                statut=StatutAchat.FACTURE,
                created_at=datetime(2026, 2, 10),
            ),
        ]
        self.mock_achat_repo.find_by_chantier.return_value = achats

        # Act
        result = self.use_case.execute(chantier_id=100)

        # Assert
        assert len(result.points) == 3

        # Décembre: aucun achat
        point_dec = result.points[0]
        assert point_dec.mois == "12/2025"
        assert point_dec.prevu_cumule == "10000.00"  # 30000 / 3 mois
        assert point_dec.engage_cumule == "0.00"
        assert point_dec.realise_cumule == "0.00"

        # Janvier: 5000 engagé
        point_jan = result.points[1]
        assert point_jan.mois == "01/2026"
        assert point_jan.prevu_cumule == "20000.00"  # cumule
        assert point_jan.engage_cumule == "5000.00"
        assert point_jan.realise_cumule == "0.00"

        # Février: cumulé engagé 14000, cumulé réalisé 3000
        point_fev = result.points[2]
        assert point_fev.mois == "02/2026"
        assert point_fev.prevu_cumule == "30000.00"  # cumule (total)
        # Janvier: 5000 engagé
        # Février: COMMANDE (6000) + FACTURE (3000) = 9000 engagé
        # Cumul: 5000 + 6000 + 3000 = 14000
        assert point_fev.engage_cumule == "14000.00"
        # Janvier: 0 réalisé
        # Février: FACTURE (3000) = 3000 réalisé
        # Cumul: 0 + 3000 = 3000
        assert point_fev.realise_cumule == "3000.00"
