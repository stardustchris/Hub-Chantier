"""Tests unitaires pour les value objects du module Dashboard."""

import pytest
from dataclasses import FrozenInstanceError

from modules.dashboard.domain.value_objects import PostStatus, TargetType
from modules.dashboard.domain.value_objects.post_targeting import PostTargeting


# ============================================================================
# Tests PostStatus
# ============================================================================


class TestPostStatus:
    """Tests pour PostStatus."""

    def test_str_returns_value(self):
        """Test __str__ retourne la valeur."""
        assert str(PostStatus.PUBLISHED) == "published"
        assert str(PostStatus.PINNED) == "pinned"
        assert str(PostStatus.ARCHIVED) == "archived"
        assert str(PostStatus.DELETED) == "deleted"

    def test_is_visible_published(self):
        """Test is_visible pour PUBLISHED."""
        assert PostStatus.PUBLISHED.is_visible() is True

    def test_is_visible_pinned(self):
        """Test is_visible pour PINNED."""
        assert PostStatus.PINNED.is_visible() is True

    def test_is_visible_archived(self):
        """Test is_visible pour ARCHIVED."""
        assert PostStatus.ARCHIVED.is_visible() is False

    def test_is_visible_deleted(self):
        """Test is_visible pour DELETED."""
        assert PostStatus.DELETED.is_visible() is False

    def test_is_consultable_published(self):
        """Test is_consultable pour PUBLISHED."""
        assert PostStatus.PUBLISHED.is_consultable() is True

    def test_is_consultable_archived(self):
        """Test is_consultable pour ARCHIVED."""
        assert PostStatus.ARCHIVED.is_consultable() is True

    def test_is_consultable_deleted(self):
        """Test is_consultable pour DELETED."""
        assert PostStatus.DELETED.is_consultable() is False

    def test_from_string_valid(self):
        """Test from_string avec valeur valide."""
        assert PostStatus.from_string("published") == PostStatus.PUBLISHED
        assert PostStatus.from_string("PUBLISHED") == PostStatus.PUBLISHED
        assert PostStatus.from_string("Pinned") == PostStatus.PINNED

    def test_from_string_invalid(self):
        """Test from_string avec valeur invalide."""
        with pytest.raises(ValueError, match="Statut invalide"):
            PostStatus.from_string("invalid_status")


# ============================================================================
# Tests TargetType
# ============================================================================


class TestTargetType:
    """Tests pour TargetType."""

    def test_str_returns_value(self):
        """Test __str__ retourne la valeur."""
        assert str(TargetType.EVERYONE) == "everyone"
        assert str(TargetType.SPECIFIC_CHANTIERS) == "specific_chantiers"
        assert str(TargetType.SPECIFIC_PEOPLE) == "specific_people"

    def test_values(self):
        """Test les valeurs de l'enum."""
        assert TargetType.EVERYONE.value == "everyone"
        assert TargetType.SPECIFIC_CHANTIERS.value == "specific_chantiers"
        assert TargetType.SPECIFIC_PEOPLE.value == "specific_people"


# ============================================================================
# Tests PostTargeting
# ============================================================================


class TestPostTargeting:
    """Tests pour PostTargeting."""

    def test_everyone_factory(self):
        """Test factory everyone."""
        targeting = PostTargeting.everyone()

        assert targeting.target_type == TargetType.EVERYONE
        assert targeting.chantier_ids is None
        assert targeting.user_ids is None

    def test_for_chantiers_factory(self):
        """Test factory for_chantiers."""
        targeting = PostTargeting.for_chantiers([1, 2, 3])

        assert targeting.target_type == TargetType.SPECIFIC_CHANTIERS
        assert targeting.chantier_ids == (1, 2, 3)
        assert targeting.user_ids is None

    def test_for_users_factory(self):
        """Test factory for_users."""
        targeting = PostTargeting.for_users([10, 20])

        assert targeting.target_type == TargetType.SPECIFIC_PEOPLE
        assert targeting.chantier_ids is None
        assert targeting.user_ids == (10, 20)

    def test_specific_chantiers_without_ids_raises(self):
        """Test SPECIFIC_CHANTIERS sans IDs lève ValueError."""
        with pytest.raises(ValueError, match="Au moins un chantier"):
            PostTargeting(target_type=TargetType.SPECIFIC_CHANTIERS)

    def test_specific_chantiers_with_empty_ids_raises(self):
        """Test SPECIFIC_CHANTIERS avec liste vide lève ValueError."""
        with pytest.raises(ValueError, match="Au moins un chantier"):
            PostTargeting(target_type=TargetType.SPECIFIC_CHANTIERS, chantier_ids=())

    def test_specific_people_without_ids_raises(self):
        """Test SPECIFIC_PEOPLE sans IDs lève ValueError."""
        with pytest.raises(ValueError, match="Au moins un utilisateur"):
            PostTargeting(target_type=TargetType.SPECIFIC_PEOPLE)

    def test_specific_people_with_empty_ids_raises(self):
        """Test SPECIFIC_PEOPLE avec liste vide lève ValueError."""
        with pytest.raises(ValueError, match="Au moins un utilisateur"):
            PostTargeting(target_type=TargetType.SPECIFIC_PEOPLE, user_ids=())

    def test_frozen_immutability(self):
        """Test que PostTargeting est immutable."""
        targeting = PostTargeting.everyone()

        with pytest.raises(FrozenInstanceError):
            targeting.target_type = TargetType.SPECIFIC_CHANTIERS

    def test_includes_chantier_everyone(self):
        """Test includes_chantier avec EVERYONE."""
        targeting = PostTargeting.everyone()

        assert targeting.includes_chantier(1) is True
        assert targeting.includes_chantier(999) is True

    def test_includes_chantier_specific_chantiers_true(self):
        """Test includes_chantier avec SPECIFIC_CHANTIERS inclus."""
        targeting = PostTargeting.for_chantiers([1, 2, 3])

        assert targeting.includes_chantier(1) is True
        assert targeting.includes_chantier(2) is True
        assert targeting.includes_chantier(3) is True

    def test_includes_chantier_specific_chantiers_false(self):
        """Test includes_chantier avec SPECIFIC_CHANTIERS non inclus."""
        targeting = PostTargeting.for_chantiers([1, 2, 3])

        assert targeting.includes_chantier(4) is False
        assert targeting.includes_chantier(999) is False

    def test_includes_chantier_specific_people(self):
        """Test includes_chantier avec SPECIFIC_PEOPLE retourne False."""
        targeting = PostTargeting.for_users([10, 20])

        assert targeting.includes_chantier(1) is False

    def test_includes_user_everyone(self):
        """Test includes_user avec EVERYONE."""
        targeting = PostTargeting.everyone()

        assert targeting.includes_user(1) is True
        assert targeting.includes_user(999) is True

    def test_includes_user_specific_people_true(self):
        """Test includes_user avec SPECIFIC_PEOPLE inclus."""
        targeting = PostTargeting.for_users([10, 20, 30])

        assert targeting.includes_user(10) is True
        assert targeting.includes_user(20) is True
        assert targeting.includes_user(30) is True

    def test_includes_user_specific_people_false(self):
        """Test includes_user avec SPECIFIC_PEOPLE non inclus."""
        targeting = PostTargeting.for_users([10, 20, 30])

        assert targeting.includes_user(40) is False
        assert targeting.includes_user(999) is False

    def test_includes_user_specific_chantiers(self):
        """Test includes_user avec SPECIFIC_CHANTIERS retourne False."""
        targeting = PostTargeting.for_chantiers([1, 2])

        assert targeting.includes_user(10) is False

    def test_get_display_text_everyone(self):
        """Test get_display_text pour EVERYONE."""
        targeting = PostTargeting.everyone()

        assert targeting.get_display_text() == "Tout le monde"

    def test_get_display_text_chantiers(self):
        """Test get_display_text pour SPECIFIC_CHANTIERS."""
        targeting = PostTargeting.for_chantiers([1, 2, 3])

        assert targeting.get_display_text() == "3 chantier(s)"

    def test_get_display_text_people(self):
        """Test get_display_text pour SPECIFIC_PEOPLE."""
        targeting = PostTargeting.for_users([10, 20])

        assert targeting.get_display_text() == "2 personne(s)"
