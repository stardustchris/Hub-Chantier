"""Tests unitaires pour GetPlanningUseCase - filtrage par metiers."""

import pytest
from unittest.mock import Mock
from datetime import datetime, date, time

from modules.planning.domain.entities import Affectation
from modules.planning.domain.repositories import AffectationRepository
from modules.planning.application.use_cases import GetPlanningUseCase
from modules.planning.application.dtos import PlanningFiltersDTO


class TestGetPlanningMetiersFilter:
    """Tests pour le filtrage du planning par metiers (intersection)."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Mock
        self.mock_affectation_repo = Mock(spec=AffectationRepository)

        # Mock des fonctions de recuperation d'infos
        self.mock_get_user_info = Mock()
        self.mock_get_chantier_info = Mock()

        # Use case
        self.use_case = GetPlanningUseCase(
            affectation_repo=self.mock_affectation_repo,
            get_user_info=self.mock_get_user_info,
            get_chantier_info=self.mock_get_chantier_info,
        )

        # Affectations de test
        self.affectation_user1 = Affectation(
            id=1,
            utilisateur_id=1,
            chantier_id=1,
            date=date(2026, 2, 3),
            created_by=99,  # Admin qui cree
            heure_debut=time(8, 0),
            heure_fin=time(17, 0),
            created_at=datetime.now(),
        )

        self.affectation_user2 = Affectation(
            id=2,
            utilisateur_id=2,
            chantier_id=1,
            date=date(2026, 2, 3),
            created_by=99,
            heure_debut=time(8, 0),
            heure_fin=time(17, 0),
            created_at=datetime.now(),
        )

        self.affectation_user3 = Affectation(
            id=3,
            utilisateur_id=3,
            chantier_id=1,
            date=date(2026, 2, 3),
            created_by=99,
            heure_debut=time(8, 0),
            heure_fin=time(17, 0),
            created_at=datetime.now(),
        )

    def test_filter_by_single_metier_matches(self):
        """Test: filtre par metier unique - trouve les utilisateurs avec ce metier."""
        # Arrange
        self.mock_affectation_repo.find_by_date_range.return_value = [
            self.affectation_user1,
            self.affectation_user2,
        ]

        # User 1: macon + coffreur
        # User 2: electricien
        self.mock_get_user_info.side_effect = lambda uid: {
            1: {
                "nom": "User 1",
                "couleur": "#3498DB",
                "metiers": ["macon", "coffreur"],
            },
            2: {"nom": "User 2", "couleur": "#E74C3C", "metiers": ["electricien"]},
        }[uid]

        self.mock_get_chantier_info.return_value = {
            "nom": "Chantier A",
            "couleur": "#2ECC71",
        }

        filters = PlanningFiltersDTO(
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            metiers=["macon"],  # Filtrer les macons uniquement
        )

        # Act
        result = self.use_case.execute(
            filters=filters, current_user_id=99, current_user_role="admin"
        )

        # Assert - Seul User 1 doit etre retourne
        assert len(result) == 1
        assert result[0].utilisateur_id == 1
        assert "macon" in result[0].utilisateur_metiers

    def test_filter_by_multiple_metiers_union(self):
        """Test: filtre par plusieurs metiers - union (OR)."""
        # Arrange
        self.mock_affectation_repo.find_by_date_range.return_value = [
            self.affectation_user1,
            self.affectation_user2,
            self.affectation_user3,
        ]

        # User 1: macon + coffreur
        # User 2: electricien
        # User 3: plombier
        self.mock_get_user_info.side_effect = lambda uid: {
            1: {"nom": "User 1", "couleur": "#3498DB", "metiers": ["macon", "coffreur"]},
            2: {"nom": "User 2", "couleur": "#E74C3C", "metiers": ["electricien"]},
            3: {"nom": "User 3", "couleur": "#9B59B6", "metiers": ["plombier"]},
        }[uid]

        self.mock_get_chantier_info.return_value = {
            "nom": "Chantier A",
            "couleur": "#2ECC71",
        }

        filters = PlanningFiltersDTO(
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            metiers=["macon", "electricien"],  # macon OU electricien
        )

        # Act
        result = self.use_case.execute(
            filters=filters, current_user_id=99, current_user_role="admin"
        )

        # Assert - User 1 et User 2 doivent etre retournes
        assert len(result) == 2
        user_ids = [dto.utilisateur_id for dto in result]
        assert 1 in user_ids  # macon
        assert 2 in user_ids  # electricien
        assert 3 not in user_ids  # plombier exclus

    def test_filter_by_metier_intersection_with_user_metiers(self):
        """Test: intersection entre filtre metiers et user.metiers."""
        # Arrange
        self.mock_affectation_repo.find_by_date_range.return_value = [
            self.affectation_user1,
            self.affectation_user2,
        ]

        # User 1: macon + coffreur (a "coffreur" dans le filtre)
        # User 2: electricien (n'a pas de metier dans le filtre)
        self.mock_get_user_info.side_effect = lambda uid: {
            1: {"nom": "User 1", "couleur": "#3498DB", "metiers": ["macon", "coffreur"]},
            2: {"nom": "User 2", "couleur": "#E74C3C", "metiers": ["electricien"]},
        }[uid]

        self.mock_get_chantier_info.return_value = {
            "nom": "Chantier A",
            "couleur": "#2ECC71",
        }

        filters = PlanningFiltersDTO(
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            metiers=["coffreur", "plombier"],  # cherche coffreur OU plombier
        )

        # Act
        result = self.use_case.execute(
            filters=filters, current_user_id=99, current_user_role="admin"
        )

        # Assert - Seul User 1 a "coffreur"
        assert len(result) == 1
        assert result[0].utilisateur_id == 1

    def test_filter_metiers_handles_none_user_metiers(self):
        """Test: filtre metiers ignore les users avec metiers=None."""
        # Arrange
        self.mock_affectation_repo.find_by_date_range.return_value = [
            self.affectation_user1,
            self.affectation_user2,
        ]

        # User 1: metiers=None
        # User 2: electricien
        self.mock_get_user_info.side_effect = lambda uid: {
            1: {"nom": "User 1", "couleur": "#3498DB", "metiers": None},
            2: {"nom": "User 2", "couleur": "#E74C3C", "metiers": ["electricien"]},
        }[uid]

        self.mock_get_chantier_info.return_value = {
            "nom": "Chantier A",
            "couleur": "#2ECC71",
        }

        filters = PlanningFiltersDTO(
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            metiers=["electricien"],
        )

        # Act
        result = self.use_case.execute(
            filters=filters, current_user_id=99, current_user_role="admin"
        )

        # Assert - Seul User 2 (avec metiers non None)
        assert len(result) == 1
        assert result[0].utilisateur_id == 2

    def test_filter_metiers_handles_empty_user_metiers(self):
        """Test: filtre metiers ignore les users avec metiers=[]."""
        # Arrange
        self.mock_affectation_repo.find_by_date_range.return_value = [
            self.affectation_user1,
            self.affectation_user2,
        ]

        # User 1: metiers=[]
        # User 2: macon
        self.mock_get_user_info.side_effect = lambda uid: {
            1: {"nom": "User 1", "couleur": "#3498DB", "metiers": []},
            2: {"nom": "User 2", "couleur": "#E74C3C", "metiers": ["macon"]},
        }[uid]

        self.mock_get_chantier_info.return_value = {
            "nom": "Chantier A",
            "couleur": "#2ECC71",
        }

        filters = PlanningFiltersDTO(
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            metiers=["macon"],
        )

        # Act
        result = self.use_case.execute(
            filters=filters, current_user_id=99, current_user_role="admin"
        )

        # Assert - Seul User 2
        assert len(result) == 1
        assert result[0].utilisateur_id == 2

    def test_no_metier_filter_returns_all_users(self):
        """Test: sans filtre metier, tous les utilisateurs sont retournes."""
        # Arrange
        self.mock_affectation_repo.find_by_date_range.return_value = [
            self.affectation_user1,
            self.affectation_user2,
        ]

        self.mock_get_user_info.side_effect = lambda uid: {
            1: {"nom": "User 1", "couleur": "#3498DB", "metiers": ["macon"]},
            2: {"nom": "User 2", "couleur": "#E74C3C", "metiers": ["electricien"]},
        }[uid]

        self.mock_get_chantier_info.return_value = {
            "nom": "Chantier A",
            "couleur": "#2ECC71",
        }

        filters = PlanningFiltersDTO(
            date_debut=date(2026, 2, 1), date_fin=date(2026, 2, 28)
            # Pas de filtre metiers
        )

        # Act
        result = self.use_case.execute(
            filters=filters, current_user_id=99, current_user_role="admin"
        )

        # Assert - Tous les users retournes
        assert len(result) == 2

    def test_filter_metiers_combined_with_chantier_filter(self):
        """Test: filtre metiers combine avec filtre chantier."""
        # Arrange
        affectation_chantier1 = Affectation(
            id=1,
            utilisateur_id=1,
            chantier_id=1,
            date=date(2026, 2, 3),
            created_by=99,
            heure_debut=time(8, 0),
            heure_fin=time(17, 0),
            created_at=datetime.now(),
        )
        affectation_chantier2 = Affectation(
            id=2,
            utilisateur_id=2,
            chantier_id=2,
            date=date(2026, 2, 3),
            created_by=99,
            heure_debut=time(8, 0),
            heure_fin=time(17, 0),
            created_at=datetime.now(),
        )

        self.mock_affectation_repo.find_by_date_range.return_value = [
            affectation_chantier1,
            affectation_chantier2,
        ]

        # User 1 chantier 1: macon
        # User 2 chantier 2: macon (exclu par filtre chantier)
        self.mock_get_user_info.side_effect = lambda uid: {
            1: {"nom": "User 1", "couleur": "#3498DB", "metiers": ["macon"]},
            2: {"nom": "User 2", "couleur": "#E74C3C", "metiers": ["macon"]},
        }[uid]

        self.mock_get_chantier_info.side_effect = lambda cid: {
            1: {"nom": "Chantier A", "couleur": "#2ECC71"},
            2: {"nom": "Chantier B", "couleur": "#F39C12"},
        }[cid]

        filters = PlanningFiltersDTO(
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 28),
            chantier_ids=[1],  # Filtre chantier
            metiers=["macon"],  # Filtre metier
        )

        # Act
        result = self.use_case.execute(
            filters=filters, current_user_id=99, current_user_role="admin"
        )

        # Assert - Seul User 1 (chantier 1 + macon)
        assert len(result) == 1
        assert result[0].utilisateur_id == 1
        assert result[0].chantier_id == 1
