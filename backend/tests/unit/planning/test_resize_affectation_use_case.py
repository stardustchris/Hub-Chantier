"""Tests unitaires pour ResizeAffectationUseCase."""

from datetime import date, timedelta
from unittest.mock import Mock

import pytest

from modules.planning.application.use_cases import (
    ResizeAffectationUseCase,
    AffectationNotFoundError,
    AffectationConflictError,
)
from modules.planning.domain.entities import Affectation
from modules.planning.domain.value_objects import TypeAffectation


@pytest.fixture
def mock_repo():
    """Mock du repository d'affectations."""
    return Mock()


@pytest.fixture
def use_case(mock_repo):
    """Instance du use case avec mock repository."""
    return ResizeAffectationUseCase(affectation_repo=mock_repo)


@pytest.fixture
def affectation_reference():
    """Affectation de référence pour les tests."""
    return Affectation(
        id=1,
        utilisateur_id=10,
        chantier_id=5,
        date=date(2026, 2, 15),
        heure_debut=None,
        heure_fin=None,
        note="Tâche test",
        type_affectation=TypeAffectation.UNIQUE,
        created_by=1,
    )


class TestResizeAffectationNotFound:
    """Tests pour le cas où l'affectation n'existe pas."""

    def test_should_raise_when_affectation_not_found(self, use_case, mock_repo):
        """Doit lever AffectationNotFoundError si affectation non trouvée."""
        mock_repo.find_by_id.return_value = None

        with pytest.raises(AffectationNotFoundError):
            use_case.execute(
                affectation_id=999,
                date_debut=date(2026, 2, 10),
                date_fin=date(2026, 2, 20),
                current_user_id=1,
            )

        mock_repo.find_by_id.assert_called_once_with(999)


class TestResizeExtendRight:
    """Tests pour l'extension vers la droite (après la date de référence)."""

    def test_should_extend_right_success(
        self, use_case, mock_repo, affectation_reference
    ):
        """Doit créer affectations pour dates après la référence."""
        mock_repo.find_by_id.return_value = affectation_reference
        mock_repo.find_by_utilisateur.return_value = [affectation_reference]
        mock_repo.exists_for_utilisateur_and_date.return_value = False

        # Nouvelles affectations créées
        new_aff_16 = Affectation(
            id=2,
            utilisateur_id=10,
            chantier_id=5,
            date=date(2026, 2, 16),
            type_affectation=TypeAffectation.UNIQUE,
            created_by=1,
        )
        new_aff_17 = Affectation(
            id=3,
            utilisateur_id=10,
            chantier_id=5,
            date=date(2026, 2, 17),
            type_affectation=TypeAffectation.UNIQUE,
            created_by=1,
        )
        mock_repo.save.side_effect = [new_aff_16, new_aff_17]

        # Affectations finales
        mock_repo.find_by_utilisateur.side_effect = [
            [affectation_reference],  # Première lecture (existantes)
            [affectation_reference, new_aff_16, new_aff_17],  # Finale
        ]

        result = use_case.execute(
            affectation_id=1,
            date_debut=date(2026, 2, 15),  # Même date
            date_fin=date(2026, 2, 17),  # Extension de 2 jours
            current_user_id=1,
        )

        assert len(result) == 3
        assert mock_repo.save.call_count == 2


class TestResizeExtendLeft:
    """Tests pour l'extension vers la gauche (avant la date de référence)."""

    def test_should_extend_left_success(
        self, use_case, mock_repo, affectation_reference
    ):
        """Doit créer affectations pour dates avant la référence."""
        mock_repo.find_by_id.return_value = affectation_reference
        mock_repo.find_by_utilisateur.return_value = [affectation_reference]
        mock_repo.exists_for_utilisateur_and_date.return_value = False

        new_aff_13 = Affectation(
            id=4,
            utilisateur_id=10,
            chantier_id=5,
            date=date(2026, 2, 13),
            type_affectation=TypeAffectation.UNIQUE,
            created_by=1,
        )
        new_aff_14 = Affectation(
            id=5,
            utilisateur_id=10,
            chantier_id=5,
            date=date(2026, 2, 14),
            type_affectation=TypeAffectation.UNIQUE,
            created_by=1,
        )
        mock_repo.save.side_effect = [new_aff_14, new_aff_13]

        mock_repo.find_by_utilisateur.side_effect = [
            [affectation_reference],
            [new_aff_13, new_aff_14, affectation_reference],
        ]

        result = use_case.execute(
            affectation_id=1,
            date_debut=date(2026, 2, 13),  # Extension de 2 jours avant
            date_fin=date(2026, 2, 15),  # Même date
            current_user_id=1,
        )

        assert len(result) == 3
        assert mock_repo.save.call_count == 2


class TestResizeExtendBothSides:
    """Tests pour l'extension des deux côtés simultanément."""

    def test_should_extend_both_sides(
        self, use_case, mock_repo, affectation_reference
    ):
        """Doit créer affectations avant ET après la référence."""
        mock_repo.find_by_id.return_value = affectation_reference
        mock_repo.find_by_utilisateur.return_value = [affectation_reference]
        mock_repo.exists_for_utilisateur_and_date.return_value = False

        # 2 avant + 2 après = 4 nouvelles
        new_affectations = [
            Affectation(id=i, utilisateur_id=10, chantier_id=5, date=d, created_by=1)
            for i, d in enumerate(
                [
                    date(2026, 2, 16),
                    date(2026, 2, 17),
                    date(2026, 2, 14),
                    date(2026, 2, 13),
                ],
                start=2,
            )
        ]
        mock_repo.save.side_effect = new_affectations

        mock_repo.find_by_utilisateur.side_effect = [
            [affectation_reference],
            [affectation_reference] + new_affectations,
        ]

        result = use_case.execute(
            affectation_id=1,
            date_debut=date(2026, 2, 13),
            date_fin=date(2026, 2, 17),
            current_user_id=1,
        )

        assert len(result) == 5  # 1 référence + 4 nouvelles
        assert mock_repo.save.call_count == 4


class TestResizeWithExistingDates:
    """Tests avec dates déjà existantes (doivent être ignorées)."""

    def test_should_skip_existing_dates(
        self, use_case, mock_repo, affectation_reference
    ):
        """Doit ignorer les dates qui ont déjà une affectation."""
        mock_repo.find_by_id.return_value = affectation_reference

        # Affectation du 16 existe déjà
        existing_16 = Affectation(
            id=2,
            utilisateur_id=10,
            chantier_id=5,
            date=date(2026, 2, 16),
            type_affectation=TypeAffectation.UNIQUE,
            created_by=1,
        )

        mock_repo.find_by_utilisateur.return_value = [
            affectation_reference,
            existing_16,
        ]
        mock_repo.exists_for_utilisateur_and_date.return_value = False

        # Seulement le 17 doit être créé
        new_aff_17 = Affectation(
            id=3,
            utilisateur_id=10,
            chantier_id=5,
            date=date(2026, 2, 17),
            type_affectation=TypeAffectation.UNIQUE,
            created_by=1,
        )
        mock_repo.save.return_value = new_aff_17

        mock_repo.find_by_utilisateur.side_effect = [
            [affectation_reference, existing_16],  # Existantes
            [affectation_reference, existing_16, new_aff_17],  # Finale
        ]

        result = use_case.execute(
            affectation_id=1,
            date_debut=date(2026, 2, 15),
            date_fin=date(2026, 2, 17),
            current_user_id=1,
        )

        assert len(result) == 3
        assert mock_repo.save.call_count == 1  # Seulement le 17


class TestResizeConflicts:
    """Tests pour la détection de conflits."""

    def test_should_raise_on_conflict(self, use_case, mock_repo, affectation_reference):
        """Doit lever AffectationConflictError en cas de conflit."""
        mock_repo.find_by_id.return_value = affectation_reference
        mock_repo.find_by_utilisateur.return_value = [affectation_reference]

        # Conflit sur le 16 (autre chantier)
        mock_repo.exists_for_utilisateur_and_date.return_value = True

        with pytest.raises(AffectationConflictError):
            use_case.execute(
                affectation_id=1,
                date_debut=date(2026, 2, 15),
                date_fin=date(2026, 2, 17),
                current_user_id=1,
            )


class TestResizeNoDatesToAdd:
    """Tests quand aucune date n'est à ajouter."""

    def test_should_return_only_existing_when_no_dates_to_add(
        self, use_case, mock_repo, affectation_reference
    ):
        """Doit retourner seulement l'existante si pas de dates à ajouter."""
        mock_repo.find_by_id.return_value = affectation_reference
        mock_repo.find_by_utilisateur.return_value = [affectation_reference]

        result = use_case.execute(
            affectation_id=1,
            date_debut=date(2026, 2, 15),  # Même date début et fin
            date_fin=date(2026, 2, 15),
            current_user_id=1,
        )

        assert len(result) == 1
        assert mock_repo.save.call_count == 0  # Aucune création


class TestResizeCopyAttributes:
    """Tests que les attributs sont bien copiés."""

    def test_should_copy_attributes_from_reference(
        self, use_case, mock_repo, affectation_reference
    ):
        """Doit copier heures et note de l'affectation de référence."""
        from modules.planning.domain.value_objects import HeureAffectation

        ref_with_hours = Affectation(
            id=1,
            utilisateur_id=10,
            chantier_id=5,
            date=date(2026, 2, 15),
            heure_debut=HeureAffectation(8, 0),
            heure_fin=HeureAffectation(17, 0),
            note="Note importante",
            type_affectation=TypeAffectation.UNIQUE,
            created_by=1,
        )

        mock_repo.find_by_id.return_value = ref_with_hours
        mock_repo.find_by_utilisateur.return_value = [ref_with_hours]
        mock_repo.exists_for_utilisateur_and_date.return_value = False

        # Capturer les arguments de save
        saved_affectations = []

        def save_side_effect(aff):
            saved_affectations.append(aff)
            return aff

        mock_repo.save.side_effect = save_side_effect
        mock_repo.find_by_utilisateur.side_effect = [
            [ref_with_hours],
            [ref_with_hours] + saved_affectations,
        ]

        use_case.execute(
            affectation_id=1,
            date_debut=date(2026, 2, 15),
            date_fin=date(2026, 2, 16),
            current_user_id=99,
        )

        # Vérifier que les attributs sont copiés
        assert len(saved_affectations) == 1
        new_aff = saved_affectations[0]
        assert new_aff.utilisateur_id == 10
        assert new_aff.chantier_id == 5
        assert new_aff.heure_debut == HeureAffectation(8, 0)
        assert new_aff.heure_fin == HeureAffectation(17, 0)
        assert new_aff.note == "Note importante"
        assert new_aff.created_by == 99  # Created by de l'utilisateur courant


class TestResizeFilterSameChantier:
    """Tests que seules les affectations du même chantier sont retournées."""

    def test_should_filter_same_chantier_only(
        self, use_case, mock_repo, affectation_reference
    ):
        """Doit retourner uniquement les affectations du même chantier."""
        mock_repo.find_by_id.return_value = affectation_reference

        # Affectations de 2 chantiers différents
        aff_chantier_5 = affectation_reference
        aff_chantier_99 = Affectation(
            id=2,
            utilisateur_id=10,
            chantier_id=99,  # Autre chantier
            date=date(2026, 2, 16),
            type_affectation=TypeAffectation.UNIQUE,
            created_by=1,
        )

        mock_repo.find_by_utilisateur.return_value = [
            aff_chantier_5,
            aff_chantier_99,
        ]
        mock_repo.exists_for_utilisateur_and_date.return_value = False

        mock_repo.find_by_utilisateur.side_effect = [
            [aff_chantier_5],  # Existantes même chantier
            [aff_chantier_5, aff_chantier_99],  # Finale (tous)
        ]

        result = use_case.execute(
            affectation_id=1,
            date_debut=date(2026, 2, 15),
            date_fin=date(2026, 2, 17),
            current_user_id=1,
        )

        # Doit filtrer et retourner seulement chantier 5
        assert all(aff.chantier_id == 5 for aff in result)
