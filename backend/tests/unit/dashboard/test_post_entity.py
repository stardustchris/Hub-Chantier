"""Tests unitaires pour l'entité Post."""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from modules.dashboard.domain.entities.post import (
    Post,
    MAX_PHOTOS_PER_POST,
    URGENT_PIN_DURATION_HOURS,
    ARCHIVE_AFTER_DAYS,
)
from modules.dashboard.domain.value_objects import PostTargeting, PostStatus, TargetType


class TestPostCreation:
    """Tests de création d'un post."""

    def test_create_basic_post(self):
        """Test création d'un post basique."""
        post = Post(
            author_id=1,
            content="Test post content",
        )

        assert post.author_id == 1
        assert post.content == "Test post content"
        assert post.id is None
        assert post.status == PostStatus.PUBLISHED
        assert post.is_urgent is False

    def test_create_post_with_targeting(self):
        """Test création avec ciblage."""
        targeting = PostTargeting(
            target_type=TargetType.SPECIFIC_CHANTIERS,
            chantier_ids=[1, 2, 3],
        )
        post = Post(
            author_id=1,
            content="Targeted post",
            targeting=targeting,
        )

        assert post.targeting.target_type == TargetType.SPECIFIC_CHANTIERS
        assert 1 in post.targeting.chantier_ids

    def test_create_post_content_trimmed(self):
        """Test que le contenu est trimé."""
        post = Post(
            author_id=1,
            content="  Content with spaces  ",
        )

        assert post.content == "Content with spaces"

    def test_create_post_empty_content_raises_error(self):
        """Test erreur si contenu vide."""
        with pytest.raises(ValueError, match="ne peut pas être vide"):
            Post(author_id=1, content="")

    def test_create_post_whitespace_content_raises_error(self):
        """Test erreur si contenu uniquement espaces."""
        with pytest.raises(ValueError, match="ne peut pas être vide"):
            Post(author_id=1, content="   ")


class TestPostPinning:
    """Tests d'épinglage de post."""

    def test_pin_post_default_duration(self):
        """Test épinglage avec durée par défaut."""
        post = Post(author_id=1, content="Test")
        before = datetime.now()
        post.pin()
        after = datetime.now()

        assert post.status == PostStatus.PINNED
        assert post.is_urgent is True
        assert post.pinned_until is not None
        # Vérifie que pinned_until est à environ 48h dans le futur
        expected_min = before + timedelta(hours=URGENT_PIN_DURATION_HOURS)
        expected_max = after + timedelta(hours=URGENT_PIN_DURATION_HOURS)
        assert expected_min <= post.pinned_until <= expected_max

    def test_pin_post_custom_duration(self):
        """Test épinglage avec durée personnalisée."""
        post = Post(author_id=1, content="Test")
        before = datetime.now()
        post.pin(duration_hours=24)
        after = datetime.now()

        assert post.status == PostStatus.PINNED
        expected_min = before + timedelta(hours=24)
        expected_max = after + timedelta(hours=24)
        assert expected_min <= post.pinned_until <= expected_max

    def test_pin_post_max_duration_capped(self):
        """Test que la durée max est plafonnée à 48h."""
        post = Post(author_id=1, content="Test")
        before = datetime.now()
        post.pin(duration_hours=100)
        after = datetime.now()

        # Doit être plafonné à 48h même si on demande 100h
        expected_min = before + timedelta(hours=URGENT_PIN_DURATION_HOURS)
        expected_max = after + timedelta(hours=URGENT_PIN_DURATION_HOURS)
        assert expected_min <= post.pinned_until <= expected_max

    def test_is_pinned_true_when_pinned_and_not_expired(self):
        """Test is_pinned retourne True quand épinglé et non expiré."""
        post = Post(author_id=1, content="Test")
        post.pin()

        assert post.is_pinned is True

    def test_is_pinned_false_when_not_pinned_status(self):
        """Test is_pinned retourne False quand pas statut PINNED."""
        post = Post(author_id=1, content="Test")

        assert post.is_pinned is False

    def test_is_pinned_false_when_expired(self):
        """Test is_pinned retourne False quand expiré."""
        post = Post(author_id=1, content="Test")
        post.status = PostStatus.PINNED
        post.pinned_until = datetime.now() - timedelta(hours=1)

        assert post.is_pinned is False

    def test_unpin_post(self):
        """Test désépinglage d'un post."""
        post = Post(author_id=1, content="Test")
        post.pin()
        post.unpin()

        assert post.status == PostStatus.PUBLISHED
        assert post.is_urgent is False
        assert post.pinned_until is None

    def test_unpin_non_pinned_post_no_effect(self):
        """Test unpin sur post non épinglé ne fait rien."""
        post = Post(author_id=1, content="Test")
        original_status = post.status
        post.unpin()

        assert post.status == original_status


class TestPostArchiving:
    """Tests d'archivage de post."""

    def test_archive_post(self):
        """Test archivage d'un post."""
        post = Post(author_id=1, content="Test")
        post.archive()

        assert post.status == PostStatus.ARCHIVED
        assert post.archived_at is not None
        assert post.is_archived is True

    def test_should_archive_false_when_recent(self):
        """Test should_archive retourne False pour post récent."""
        post = Post(author_id=1, content="Test")

        assert post.should_archive is False

    def test_should_archive_true_when_old(self):
        """Test should_archive retourne True pour post de plus de 7 jours."""
        post = Post(author_id=1, content="Test")
        post.created_at = datetime.now() - timedelta(days=ARCHIVE_AFTER_DAYS + 1)

        assert post.should_archive is True

    def test_should_archive_false_when_already_archived(self):
        """Test should_archive retourne False si déjà archivé."""
        post = Post(author_id=1, content="Test")
        post.created_at = datetime.now() - timedelta(days=10)
        post.archive()

        assert post.should_archive is False


class TestPostDeletion:
    """Tests de suppression de post."""

    def test_delete_post(self):
        """Test suppression d'un post."""
        post = Post(author_id=1, content="Test")
        post.delete()

        assert post.status == PostStatus.DELETED


class TestPostUpdate:
    """Tests de mise à jour de post."""

    def test_update_content(self):
        """Test mise à jour du contenu."""
        post = Post(author_id=1, content="Original")
        original_updated_at = post.updated_at

        post.update_content("New content")

        assert post.content == "New content"
        assert post.updated_at >= original_updated_at

    def test_update_content_trimmed(self):
        """Test que le nouveau contenu est trimé."""
        post = Post(author_id=1, content="Original")
        post.update_content("  New content  ")

        assert post.content == "New content"

    def test_update_content_empty_raises_error(self):
        """Test erreur si nouveau contenu vide."""
        post = Post(author_id=1, content="Original")

        with pytest.raises(ValueError, match="ne peut pas être vide"):
            post.update_content("")

    def test_update_targeting(self):
        """Test mise à jour du ciblage."""
        post = Post(author_id=1, content="Test")
        new_targeting = PostTargeting(
            target_type=TargetType.SPECIFIC_PEOPLE,
            user_ids=[5, 6, 7],
        )

        post.update_targeting(new_targeting)

        assert post.targeting.target_type == TargetType.SPECIFIC_PEOPLE
        assert 5 in post.targeting.user_ids


class TestPostVisibility:
    """Tests de visibilité de post."""

    def test_is_visible_true_for_published(self):
        """Test visibilité pour post publié."""
        post = Post(author_id=1, content="Test")

        assert post.is_visible is True

    def test_is_visible_false_for_deleted(self):
        """Test invisibilité pour post supprimé."""
        post = Post(author_id=1, content="Test")
        post.delete()

        assert post.is_visible is False

    def test_is_visible_to_user_author_always_sees(self):
        """Test que l'auteur voit toujours son post."""
        post = Post(author_id=1, content="Test")
        targeting = PostTargeting(
            target_type=TargetType.SPECIFIC_PEOPLE,
            user_ids=[2, 3],  # L'auteur (1) n'est pas dans la liste
        )
        post.targeting = targeting

        assert post.is_visible_to_user(user_id=1) is True

    def test_is_visible_to_user_everyone_targeting(self):
        """Test visibilité pour ciblage everyone."""
        post = Post(author_id=1, content="Test")
        post.targeting = PostTargeting.everyone()

        assert post.is_visible_to_user(user_id=5) is True

    def test_is_visible_to_user_specific_people_included(self):
        """Test visibilité pour personne ciblée."""
        post = Post(author_id=1, content="Test")
        post.targeting = PostTargeting(
            target_type=TargetType.SPECIFIC_PEOPLE,
            user_ids=[2, 3, 5],
        )

        assert post.is_visible_to_user(user_id=5) is True

    def test_is_visible_to_user_specific_people_not_included(self):
        """Test invisibilité pour personne non ciblée."""
        post = Post(author_id=1, content="Test")
        post.targeting = PostTargeting(
            target_type=TargetType.SPECIFIC_PEOPLE,
            user_ids=[2, 3],
        )

        assert post.is_visible_to_user(user_id=5) is False

    def test_is_visible_to_user_specific_chantiers_included(self):
        """Test visibilité pour utilisateur du chantier ciblé."""
        post = Post(author_id=1, content="Test")
        post.targeting = PostTargeting(
            target_type=TargetType.SPECIFIC_CHANTIERS,
            chantier_ids=[10, 20],
        )

        assert post.is_visible_to_user(user_id=5, user_chantier_ids=[20, 30]) is True

    def test_is_visible_to_user_specific_chantiers_not_included(self):
        """Test invisibilité pour utilisateur hors chantiers ciblés."""
        post = Post(author_id=1, content="Test")
        post.targeting = PostTargeting(
            target_type=TargetType.SPECIFIC_CHANTIERS,
            chantier_ids=[10, 20],
        )

        assert post.is_visible_to_user(user_id=5, user_chantier_ids=[30, 40]) is False

    def test_is_visible_to_user_deleted_post(self):
        """Test invisibilité pour post supprimé."""
        post = Post(author_id=1, content="Test")
        post.delete()

        assert post.is_visible_to_user(user_id=5) is False


class TestPostEquality:
    """Tests d'égalité de posts."""

    def test_equal_posts_same_id(self):
        """Test égalité si même ID."""
        post1 = Post(author_id=1, content="Test 1", id=1)
        post2 = Post(author_id=2, content="Test 2", id=1)

        assert post1 == post2

    def test_not_equal_different_ids(self):
        """Test inégalité si IDs différents."""
        post1 = Post(author_id=1, content="Test 1", id=1)
        post2 = Post(author_id=1, content="Test 1", id=2)

        assert post1 != post2

    def test_not_equal_none_ids(self):
        """Test inégalité si un ID est None."""
        post1 = Post(author_id=1, content="Test 1", id=1)
        post2 = Post(author_id=1, content="Test 1", id=None)

        assert post1 != post2

    def test_not_equal_both_none_ids(self):
        """Test inégalité si les deux IDs sont None."""
        post1 = Post(author_id=1, content="Test 1", id=None)
        post2 = Post(author_id=1, content="Test 1", id=None)

        assert post1 != post2

    def test_not_equal_different_type(self):
        """Test inégalité avec type différent."""
        post = Post(author_id=1, content="Test", id=1)

        assert post != "not a post"

    def test_hash_with_id(self):
        """Test hash avec ID."""
        post = Post(author_id=1, content="Test", id=42)

        assert hash(post) == hash(42)

    def test_hash_without_id(self):
        """Test hash sans ID."""
        post = Post(author_id=1, content="Test")

        # Hash basé sur l'identité de l'objet
        assert hash(post) is not None


class TestPostTargetDisplay:
    """Tests d'affichage du ciblage."""

    def test_target_display_everyone(self):
        """Test affichage ciblage everyone."""
        post = Post(author_id=1, content="Test")
        post.targeting = PostTargeting.everyone()

        assert post.target_display is not None


class TestPostConstants:
    """Tests des constantes du module."""

    def test_max_photos_constant(self):
        """Test constante MAX_PHOTOS_PER_POST."""
        assert MAX_PHOTOS_PER_POST == 5

    def test_urgent_pin_duration_constant(self):
        """Test constante URGENT_PIN_DURATION_HOURS."""
        assert URGENT_PIN_DURATION_HOURS == 48

    def test_archive_after_days_constant(self):
        """Test constante ARCHIVE_AFTER_DAYS."""
        assert ARCHIVE_AFTER_DAYS == 7
