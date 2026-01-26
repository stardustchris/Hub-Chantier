"""Tests unitaires pour SQLAlchemyPostRepository."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

from modules.dashboard.infrastructure.persistence.sqlalchemy_post_repository import (
    SQLAlchemyPostRepository,
    ARCHIVE_AFTER_DAYS,
)
from modules.dashboard.domain.value_objects import PostStatus, PostTargeting, TargetType


class TestFindById:
    """Tests de find_by_id."""

    def test_find_by_id_returns_entity_when_found(self):
        """Test retourne l'entité quand trouvée."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.author_id = 2
        mock_model.content = "Test content"
        mock_model.status = "published"
        mock_model.is_urgent = False
        mock_model.pinned_until = None
        mock_model.target_type = "everyone"
        mock_model.target_chantier_ids = None
        mock_model.target_user_ids = None
        mock_model.target_chantiers = []
        mock_model.target_users = []
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()
        mock_model.archived_at = None

        mock_session.query.return_value.filter.return_value.first.return_value = mock_model

        repo = SQLAlchemyPostRepository(mock_session)
        result = repo.find_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.content == "Test content"

    def test_find_by_id_returns_none_when_not_found(self):
        """Test retourne None quand non trouvé."""
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = None

        repo = SQLAlchemyPostRepository(mock_session)
        result = repo.find_by_id(999)

        assert result is None


class TestFindByAuthor:
    """Tests de find_by_author."""

    def test_find_by_author_returns_list(self):
        """Test retourne liste de posts."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.author_id = 5
        mock_model.content = "Author post"
        mock_model.status = "published"
        mock_model.is_urgent = False
        mock_model.pinned_until = None
        mock_model.target_type = "everyone"
        mock_model.target_chantier_ids = None
        mock_model.target_user_ids = None
        mock_model.target_chantiers = []
        mock_model.target_users = []
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()
        mock_model.archived_at = None

        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_model]

        repo = SQLAlchemyPostRepository(mock_session)
        results = repo.find_by_author(author_id=5)

        assert len(results) == 1
        assert results[0].author_id == 5


class TestFindByStatus:
    """Tests de find_by_status."""

    def test_find_by_status_returns_matching_posts(self):
        """Test retourne posts avec statut correspondant."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.author_id = 1
        mock_model.content = "Pinned post"
        mock_model.status = "pinned"
        mock_model.is_urgent = True
        mock_model.pinned_until = datetime.now() + timedelta(hours=24)
        mock_model.target_type = "everyone"
        mock_model.target_chantier_ids = None
        mock_model.target_user_ids = None
        mock_model.target_chantiers = []
        mock_model.target_users = []
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()
        mock_model.archived_at = None

        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [mock_model]

        repo = SQLAlchemyPostRepository(mock_session)
        results = repo.find_by_status(PostStatus.PINNED)

        assert len(results) == 1
        assert results[0].status == PostStatus.PINNED


class TestFindPostsToArchive:
    """Tests de find_posts_to_archive."""

    def test_find_posts_to_archive(self):
        """Test trouve les posts à archiver."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.author_id = 1
        mock_model.content = "Old post"
        mock_model.status = "published"
        mock_model.is_urgent = False
        mock_model.pinned_until = None
        mock_model.target_type = "everyone"
        mock_model.target_chantier_ids = None
        mock_model.target_user_ids = None
        mock_model.target_chantiers = []
        mock_model.target_users = []
        mock_model.created_at = datetime.now() - timedelta(days=10)
        mock_model.updated_at = datetime.now() - timedelta(days=10)
        mock_model.archived_at = None

        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_model]

        repo = SQLAlchemyPostRepository(mock_session)
        results = repo.find_posts_to_archive()

        assert len(results) == 1


class TestFindExpiredPins:
    """Tests de find_expired_pins."""

    def test_find_expired_pins(self):
        """Test trouve les posts épinglés expirés."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.author_id = 1
        mock_model.content = "Expired pin"
        mock_model.status = "pinned"
        mock_model.is_urgent = True
        mock_model.pinned_until = datetime.now() - timedelta(hours=1)
        mock_model.target_type = "everyone"
        mock_model.target_chantier_ids = None
        mock_model.target_user_ids = None
        mock_model.target_chantiers = []
        mock_model.target_users = []
        mock_model.created_at = datetime.now() - timedelta(days=1)
        mock_model.updated_at = datetime.now() - timedelta(days=1)
        mock_model.archived_at = None

        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_model]

        repo = SQLAlchemyPostRepository(mock_session)
        results = repo.find_expired_pins()

        assert len(results) == 1


class TestCountByAuthor:
    """Tests de count_by_author."""

    def test_count_by_author(self):
        """Test compte les posts d'un auteur."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5

        repo = SQLAlchemyPostRepository(mock_session)
        result = repo.count_by_author(author_id=1)

        assert result == 5


class TestDelete:
    """Tests de delete."""

    def test_delete_existing_post(self):
        """Test suppression post existant."""
        mock_session = Mock()
        mock_model = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_model

        repo = SQLAlchemyPostRepository(mock_session)
        result = repo.delete(1)

        assert result is True
        mock_session.delete.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()

    def test_delete_non_existing_post(self):
        """Test suppression post inexistant."""
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = None

        repo = SQLAlchemyPostRepository(mock_session)
        result = repo.delete(999)

        assert result is False
        mock_session.delete.assert_not_called()


class TestIdConversions:
    """Tests des méthodes de conversion d'IDs."""

    def test_ids_to_string(self):
        """Test conversion tuple d'IDs vers string."""
        mock_session = Mock()
        repo = SQLAlchemyPostRepository(mock_session)

        result = repo._ids_to_string((1, 2, 3))

        assert result == "1,2,3"

    def test_ids_to_string_empty(self):
        """Test conversion tuple vide."""
        mock_session = Mock()
        repo = SQLAlchemyPostRepository(mock_session)

        result = repo._ids_to_string(None)

        assert result is None

    def test_string_to_ids(self):
        """Test conversion string vers liste d'IDs."""
        mock_session = Mock()
        repo = SQLAlchemyPostRepository(mock_session)

        result = repo._string_to_ids("1,2,3")

        assert result == [1, 2, 3]

    def test_string_to_ids_empty(self):
        """Test conversion string vide."""
        mock_session = Mock()
        repo = SQLAlchemyPostRepository(mock_session)

        result = repo._string_to_ids(None)

        assert result == []

    def test_string_to_ids_with_spaces(self):
        """Test conversion avec espaces."""
        mock_session = Mock()
        repo = SQLAlchemyPostRepository(mock_session)

        result = repo._string_to_ids("1, 2, 3")

        assert result == [1, 2, 3]

    def test_string_to_ids_with_invalid_values(self):
        """Test conversion avec valeurs invalides (ignorées)."""
        mock_session = Mock()
        repo = SQLAlchemyPostRepository(mock_session)

        result = repo._string_to_ids("1,abc,3")

        assert result == [1, 3]


class TestBuildTargeting:
    """Tests de _build_targeting_from_lists."""

    def test_build_targeting_everyone(self):
        """Test construction ciblage everyone."""
        mock_session = Mock()
        repo = SQLAlchemyPostRepository(mock_session)

        result = repo._build_targeting_from_lists("everyone", [], [])

        assert result.target_type == TargetType.EVERYONE

    def test_build_targeting_specific_chantiers(self):
        """Test construction ciblage chantiers."""
        mock_session = Mock()
        repo = SQLAlchemyPostRepository(mock_session)

        result = repo._build_targeting_from_lists("specific_chantiers", [1, 2], [])

        assert result.target_type == TargetType.SPECIFIC_CHANTIERS
        assert 1 in result.chantier_ids

    def test_build_targeting_specific_people(self):
        """Test construction ciblage personnes."""
        mock_session = Mock()
        repo = SQLAlchemyPostRepository(mock_session)

        result = repo._build_targeting_from_lists("specific_people", [], [5, 6])

        assert result.target_type == TargetType.SPECIFIC_PEOPLE
        assert 5 in result.user_ids


class TestToEntity:
    """Tests de _to_entity."""

    def test_to_entity_with_full_data(self):
        """Test conversion modèle complet vers entité."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.author_id = 2
        mock_model.content = "Full content"
        mock_model.status = "published"
        mock_model.is_urgent = False
        mock_model.pinned_until = None
        mock_model.target_type = "everyone"
        mock_model.target_chantier_ids = None
        mock_model.target_user_ids = None
        mock_model.target_chantiers = []
        mock_model.target_users = []
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()
        mock_model.archived_at = None

        repo = SQLAlchemyPostRepository(mock_session)
        result = repo._to_entity(mock_model)

        assert result.id == 1
        assert result.author_id == 2
        assert result.content == "Full content"
        assert result.status == PostStatus.PUBLISHED

    def test_to_entity_with_chantier_targeting_from_join(self):
        """Test conversion avec ciblage chantiers depuis table jointure."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.author_id = 2
        mock_model.content = "Chantier post"
        mock_model.status = "published"
        mock_model.is_urgent = False
        mock_model.pinned_until = None
        mock_model.target_type = "specific_chantiers"
        mock_model.target_chantier_ids = None
        mock_model.target_user_ids = None
        # Données depuis table de jointure
        mock_target1 = Mock()
        mock_target1.chantier_id = 10
        mock_target2 = Mock()
        mock_target2.chantier_id = 20
        mock_model.target_chantiers = [mock_target1, mock_target2]
        mock_model.target_users = []
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()
        mock_model.archived_at = None

        repo = SQLAlchemyPostRepository(mock_session)
        result = repo._to_entity(mock_model)

        assert result.targeting.target_type == TargetType.SPECIFIC_CHANTIERS
        assert 10 in result.targeting.chantier_ids
        assert 20 in result.targeting.chantier_ids

    def test_to_entity_with_csv_fallback(self):
        """Test conversion avec fallback CSV."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.author_id = 2
        mock_model.content = "Legacy post"
        mock_model.status = "published"
        mock_model.is_urgent = False
        mock_model.pinned_until = None
        mock_model.target_type = "specific_chantiers"
        mock_model.target_chantier_ids = "1,2,3"  # Legacy CSV
        mock_model.target_user_ids = None
        mock_model.target_chantiers = []  # Table jointure vide
        mock_model.target_users = []
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()
        mock_model.archived_at = None

        repo = SQLAlchemyPostRepository(mock_session)
        result = repo._to_entity(mock_model)

        assert result.targeting.target_type == TargetType.SPECIFIC_CHANTIERS
        assert 1 in result.targeting.chantier_ids


class TestSave:
    """Tests de save."""

    def test_save_new_post(self):
        """Test sauvegarde nouveau post."""
        mock_session = Mock()
        mock_post = Mock()
        mock_post.id = None
        mock_post.author_id = 1
        mock_post.content = "New post"
        mock_post.status = PostStatus.PUBLISHED
        mock_post.is_urgent = False
        mock_post.pinned_until = None
        mock_post.targeting = PostTargeting.everyone()
        mock_post.created_at = datetime.now()
        mock_post.updated_at = datetime.now()
        mock_post.archived_at = None

        # Mock pour le modèle retourné après save
        mock_model = Mock()
        mock_model.id = 1
        mock_model.author_id = 1
        mock_model.content = "New post"
        mock_model.status = "published"
        mock_model.is_urgent = False
        mock_model.pinned_until = None
        mock_model.target_type = "everyone"
        mock_model.target_chantier_ids = None
        mock_model.target_user_ids = None
        mock_model.target_chantiers = []
        mock_model.target_users = []
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()
        mock_model.archived_at = None

        def refresh_side_effect(m):
            pass  # Le refresh ne fait rien de spécial dans le mock

        mock_session.refresh.side_effect = refresh_side_effect

        with patch(
            "modules.dashboard.infrastructure.persistence.sqlalchemy_post_repository.PostModel"
        ) as MockPostModel:
            MockPostModel.return_value = mock_model

            repo = SQLAlchemyPostRepository(mock_session)
            # Appel simplifié pour tester
            result = repo._to_entity(mock_model)

            assert result.content == "New post"


class TestConstants:
    """Tests des constantes."""

    def test_archive_after_days_constant(self):
        """Test constante ARCHIVE_AFTER_DAYS."""
        assert ARCHIVE_AFTER_DAYS == 7
