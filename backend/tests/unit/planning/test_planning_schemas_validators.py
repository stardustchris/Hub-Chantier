"""Tests unitaires pour les validators des schemas Planning.

Ce fichier teste les validators Pydantic dans planning_schemas.py:
- validate_heures_prevues: validation NaN/Infinity
- validate_jours_recurrence: validation des jours 0-6
- validate_date_fin: validation date_fin >= date_debut
- validate_source_date_fin: validation date_fin source
- validate_target_date_debut: validation date cible
"""

import pytest
from datetime import date
import math

from modules.planning.adapters.controllers.planning_schemas import (
    CreateAffectationRequest,
    PlanningFiltersRequest,
    DuplicateAffectationsRequest,
    ResizeAffectationRequest,
)
from pydantic import ValidationError


# =============================================================================
# Tests: validate_heures_prevues (CreateAffectationRequest)
# =============================================================================

class TestValidateHeuresPrevues:
    """Tests du validator validate_heures_prevues."""

    def test_should_accept_valid_float_8_hours(self):
        """Test: accepte 8.0 heures valide."""
        request = CreateAffectationRequest(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            heures_prevues=8.0,
        )
        assert request.heures_prevues == 8.0

    def test_should_accept_valid_float_7_5_hours(self):
        """Test: accepte 7.5 heures valide."""
        request = CreateAffectationRequest(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            heures_prevues=7.5,
        )
        assert request.heures_prevues == 7.5

    def test_should_accept_minimum_value_greater_than_zero(self):
        """Test: accepte 0.1 heures (minimum > 0)."""
        request = CreateAffectationRequest(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            heures_prevues=0.1,
        )
        assert request.heures_prevues == 0.1

    def test_should_accept_maximum_value_24_hours(self):
        """Test: accepte 24.0 heures (maximum)."""
        request = CreateAffectationRequest(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            heures_prevues=24.0,
        )
        assert request.heures_prevues == 24.0

    def test_should_reject_nan_value(self):
        """Test: rejette NaN."""
        with pytest.raises(ValidationError) as exc_info:
            CreateAffectationRequest(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                heures_prevues=math.nan,
            )

        errors = exc_info.value.errors()
        assert len(errors) >= 1
        assert any("heures_prevues" in err["loc"] for err in errors)
        # NaN/Inf peuvent etre rejetes soit par le validator, soit par les contraintes Pydantic
        # L'important est que la validation echoue

    def test_should_reject_positive_infinity(self):
        """Test: rejette Infinity positive."""
        with pytest.raises(ValidationError) as exc_info:
            CreateAffectationRequest(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                heures_prevues=math.inf,
            )

        errors = exc_info.value.errors()
        assert len(errors) >= 1
        assert any("heures_prevues" in err["loc"] for err in errors)
        # Infinity peut etre rejete soit par le validator, soit par le=24

    def test_should_reject_negative_infinity(self):
        """Test: rejette Infinity negative."""
        with pytest.raises(ValidationError) as exc_info:
            CreateAffectationRequest(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                heures_prevues=-math.inf,
            )

        errors = exc_info.value.errors()
        assert len(errors) >= 1
        # Peut echouer soit sur le validator, soit sur gt=0
        assert any("heures_prevues" in err["loc"] for err in errors)

    def test_should_reject_zero_hours(self):
        """Test: rejette 0.0 heures (gt=0)."""
        with pytest.raises(ValidationError) as exc_info:
            CreateAffectationRequest(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                heures_prevues=0.0,
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "heures_prevues" in errors[0]["loc"]
        assert "greater than 0" in errors[0]["msg"]

    def test_should_reject_negative_hours(self):
        """Test: rejette -5.0 heures (gt=0)."""
        with pytest.raises(ValidationError) as exc_info:
            CreateAffectationRequest(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                heures_prevues=-5.0,
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "heures_prevues" in errors[0]["loc"]

    def test_should_reject_above_24_hours(self):
        """Test: rejette 25.0 heures (le=24)."""
        with pytest.raises(ValidationError) as exc_info:
            CreateAffectationRequest(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                heures_prevues=25.0,
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "heures_prevues" in errors[0]["loc"]
        assert "less than or equal to 24" in errors[0]["msg"]


# =============================================================================
# Tests: validate_jours_recurrence (CreateAffectationRequest)
# =============================================================================

class TestValidateJoursRecurrence:
    """Tests du validator validate_jours_recurrence."""

    def test_should_accept_valid_single_day(self):
        """Test: accepte un jour valide [1]."""
        request = CreateAffectationRequest(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            jours_recurrence=[1],
        )
        assert request.jours_recurrence == [1]

    def test_should_accept_valid_multiple_days(self):
        """Test: accepte plusieurs jours valides [0, 2, 4]."""
        request = CreateAffectationRequest(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            jours_recurrence=[0, 2, 4],
        )
        assert request.jours_recurrence == [0, 2, 4]

    def test_should_accept_all_days(self):
        """Test: accepte tous les jours [0, 1, 2, 3, 4, 5, 6]."""
        request = CreateAffectationRequest(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            jours_recurrence=[0, 1, 2, 3, 4, 5, 6],
        )
        assert request.jours_recurrence == [0, 1, 2, 3, 4, 5, 6]

    def test_should_accept_monday_day_0(self):
        """Test: accepte jour 0 (Lundi)."""
        request = CreateAffectationRequest(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            jours_recurrence=[0],
        )
        assert request.jours_recurrence == [0]

    def test_should_accept_sunday_day_6(self):
        """Test: accepte jour 6 (Dimanche)."""
        request = CreateAffectationRequest(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            jours_recurrence=[6],
        )
        assert request.jours_recurrence == [6]

    def test_should_accept_none_value(self):
        """Test: accepte None (pas de recurrence)."""
        request = CreateAffectationRequest(
            utilisateur_id=1,
            chantier_id=2,
            date=date(2026, 1, 22),
            jours_recurrence=None,
        )
        assert request.jours_recurrence is None

    def test_should_reject_negative_day(self):
        """Test: rejette jour negatif [-1]."""
        with pytest.raises(ValidationError) as exc_info:
            CreateAffectationRequest(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                jours_recurrence=[-1],
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "jours_recurrence" in errors[0]["loc"]
        assert "invalide" in errors[0]["msg"]

    def test_should_reject_day_above_6(self):
        """Test: rejette jour > 6 [7]."""
        with pytest.raises(ValidationError) as exc_info:
            CreateAffectationRequest(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                jours_recurrence=[7],
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "jours_recurrence" in errors[0]["loc"]
        assert "invalide" in errors[0]["msg"]

    def test_should_reject_mixed_valid_invalid(self):
        """Test: rejette liste avec jour invalide [1, 2, 8]."""
        with pytest.raises(ValidationError) as exc_info:
            CreateAffectationRequest(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                jours_recurrence=[1, 2, 8],
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "jours_recurrence" in errors[0]["loc"]

    def test_should_reject_string_value(self):
        """Test: rejette valeur string au lieu d'int."""
        with pytest.raises(ValidationError) as exc_info:
            CreateAffectationRequest(
                utilisateur_id=1,
                chantier_id=2,
                date=date(2026, 1, 22),
                jours_recurrence=["lundi"],
            )

        errors = exc_info.value.errors()
        assert len(errors) >= 1


# =============================================================================
# Tests: validate_date_fin (PlanningFiltersRequest)
# =============================================================================

class TestValidateDateFinFilters:
    """Tests du validator validate_date_fin dans PlanningFiltersRequest."""

    def test_should_accept_date_fin_after_date_debut(self):
        """Test: accepte date_fin > date_debut."""
        request = PlanningFiltersRequest(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 26),
        )
        assert request.date_fin == date(2026, 1, 26)

    def test_should_accept_date_fin_equal_date_debut(self):
        """Test: accepte date_fin == date_debut."""
        request = PlanningFiltersRequest(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 20),
        )
        assert request.date_fin == date(2026, 1, 20)

    def test_should_reject_date_fin_before_date_debut(self):
        """Test: rejette date_fin < date_debut."""
        with pytest.raises(ValidationError) as exc_info:
            PlanningFiltersRequest(
                date_debut=date(2026, 1, 20),
                date_fin=date(2026, 1, 19),
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "date_fin" in errors[0]["loc"]
        assert "posterieure ou egale" in errors[0]["msg"]


# =============================================================================
# Tests: validate_source_date_fin (DuplicateAffectationsRequest)
# =============================================================================

class TestValidateSourceDateFin:
    """Tests du validator validate_source_date_fin."""

    def test_should_accept_source_date_fin_after_debut(self):
        """Test: accepte source_date_fin > source_date_debut."""
        request = DuplicateAffectationsRequest(
            utilisateur_id=1,
            source_date_debut=date(2026, 1, 13),
            source_date_fin=date(2026, 1, 17),
            target_date_debut=date(2026, 1, 20),
        )
        assert request.source_date_fin == date(2026, 1, 17)

    def test_should_accept_source_date_fin_equal_debut(self):
        """Test: accepte source_date_fin == source_date_debut."""
        request = DuplicateAffectationsRequest(
            utilisateur_id=1,
            source_date_debut=date(2026, 1, 13),
            source_date_fin=date(2026, 1, 13),
            target_date_debut=date(2026, 1, 20),
        )
        assert request.source_date_fin == date(2026, 1, 13)

    def test_should_reject_source_date_fin_before_debut(self):
        """Test: rejette source_date_fin < source_date_debut."""
        with pytest.raises(ValidationError) as exc_info:
            DuplicateAffectationsRequest(
                utilisateur_id=1,
                source_date_debut=date(2026, 1, 13),
                source_date_fin=date(2026, 1, 12),
                target_date_debut=date(2026, 1, 20),
            )

        errors = exc_info.value.errors()
        assert len(errors) >= 1
        # Peut echouer sur source_date_fin ou target_date_debut
        assert any("date_fin" in str(err["loc"]) for err in errors)


# =============================================================================
# Tests: validate_target_date_debut (DuplicateAffectationsRequest)
# =============================================================================

class TestValidateTargetDateDebut:
    """Tests du validator validate_target_date_debut."""

    def test_should_accept_target_after_source_fin(self):
        """Test: accepte target_date_debut > source_date_fin."""
        request = DuplicateAffectationsRequest(
            utilisateur_id=1,
            source_date_debut=date(2026, 1, 13),
            source_date_fin=date(2026, 1, 17),
            target_date_debut=date(2026, 1, 20),
        )
        assert request.target_date_debut == date(2026, 1, 20)

    def test_should_reject_target_equal_source_fin(self):
        """Test: rejette target_date_debut == source_date_fin."""
        with pytest.raises(ValidationError) as exc_info:
            DuplicateAffectationsRequest(
                utilisateur_id=1,
                source_date_debut=date(2026, 1, 13),
                source_date_fin=date(2026, 1, 17),
                target_date_debut=date(2026, 1, 17),
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "target_date_debut" in errors[0]["loc"]
        assert "posterieure" in errors[0]["msg"]

    def test_should_reject_target_before_source_fin(self):
        """Test: rejette target_date_debut < source_date_fin."""
        with pytest.raises(ValidationError) as exc_info:
            DuplicateAffectationsRequest(
                utilisateur_id=1,
                source_date_debut=date(2026, 1, 13),
                source_date_fin=date(2026, 1, 17),
                target_date_debut=date(2026, 1, 16),
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "target_date_debut" in errors[0]["loc"]


# =============================================================================
# Tests: validate_date_fin (ResizeAffectationRequest)
# =============================================================================

class TestValidateDateFinResize:
    """Tests du validator validate_date_fin dans ResizeAffectationRequest."""

    def test_should_accept_resize_date_fin_after_debut(self):
        """Test: accepte date_fin > date_debut."""
        request = ResizeAffectationRequest(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 24),
        )
        assert request.date_fin == date(2026, 1, 24)

    def test_should_accept_resize_date_fin_equal_debut(self):
        """Test: accepte date_fin == date_debut."""
        request = ResizeAffectationRequest(
            date_debut=date(2026, 1, 20),
            date_fin=date(2026, 1, 20),
        )
        assert request.date_fin == date(2026, 1, 20)

    def test_should_reject_resize_date_fin_before_debut(self):
        """Test: rejette date_fin < date_debut."""
        with pytest.raises(ValidationError) as exc_info:
            ResizeAffectationRequest(
                date_debut=date(2026, 1, 20),
                date_fin=date(2026, 1, 19),
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "date_fin" in errors[0]["loc"]
        assert "posterieure ou egale" in errors[0]["msg"]
