"""Tests unitaires pour les repositories SQLAlchemy du module Dashboard."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from modules.dashboard.infrastructure.persistence.sqlalchemy_comment_repository import (
    SQLAlchemyCommentRepository,
)
from modules.dashboard.infrastructure.persistence.sqlalchemy_like_repository import (
    SQLAlchemyLikeRepository,
)
from modules.dashboard.infrastructure.persistence.sqlalchemy_media_repository import (
    SQLAlchemyPostMediaRepository,
)
from modules.dashboard.domain.entities import Comment, Like, PostMedia
from modules.dashboard.domain.entities.post_media import MediaType


# ============================================================================
# Tests SQLAlchemyCommentRepository
# ============================================================================


class TestSQLAlchemyCommentRepository:
    """Tests pour SQLAlchemyCommentRepository."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.session = Mock()
        self.repo = SQLAlchemyCommentRepository(self.session)

    def _create_mock_comment_model(
        self,
        comment_id=1,
        post_id=10,
        author_id=5,
        content="Test comment",
        is_deleted=False,
    ):
        """Helper pour créer un mock de CommentModel."""
        mock = Mock()
        mock.id = comment_id
        mock.post_id = post_id
        mock.author_id = author_id
        mock.content = content
        mock.is_deleted = is_deleted
        mock.created_at = datetime.now()
        mock.updated_at = datetime.now()
        return mock

    def test_save_create_new_comment(self):
        """Test création d'un nouveau commentaire."""
        comment = Comment(
            post_id=10,
            author_id=5,
            content="Nouveau commentaire",
        )

        mock_model = self._create_mock_comment_model(comment_id=1)
        self.session.refresh = Mock(side_effect=lambda m: setattr(m, "id", 1))

        with patch(
            "modules.dashboard.infrastructure.persistence.sqlalchemy_comment_repository.CommentModel"
        ) as MockModel:
            MockModel.return_value = mock_model

            result = self.repo.save(comment)

            self.session.add.assert_called_once()
            self.session.commit.assert_called_once()
            assert result.post_id == 10

    def test_save_update_existing_comment(self):
        """Test mise à jour d'un commentaire existant."""
        comment = Comment(
            id=1,
            post_id=10,
            author_id=5,
            content="Commentaire modifié",
        )

        mock_model = self._create_mock_comment_model()
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_model
        self.session.query.return_value = query_mock

        result = self.repo.save(comment)

        assert mock_model.content == "Commentaire modifié"
        self.session.commit.assert_called_once()

    def test_find_by_id_found(self):
        """Test recherche commentaire trouvé."""
        mock_model = self._create_mock_comment_model()
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_model
        self.session.query.return_value = query_mock

        result = self.repo.find_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.content == "Test comment"

    def test_find_by_id_not_found(self):
        """Test recherche commentaire non trouvé."""
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        self.session.query.return_value = query_mock

        result = self.repo.find_by_id(999)

        assert result is None

    def test_find_by_post(self):
        """Test recherche commentaires par post."""
        mock_models = [
            self._create_mock_comment_model(comment_id=i, post_id=10)
            for i in range(1, 4)
        ]
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.all.return_value = mock_models
        self.session.query.return_value = query_mock

        result = self.repo.find_by_post(post_id=10)

        assert len(result) == 3
        assert all(c.post_id == 10 for c in result)

    def test_find_by_post_include_deleted(self):
        """Test recherche commentaires avec supprimés."""
        mock_models = [
            self._create_mock_comment_model(comment_id=1, is_deleted=False),
            self._create_mock_comment_model(comment_id=2, is_deleted=True),
        ]
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.all.return_value = mock_models
        self.session.query.return_value = query_mock

        result = self.repo.find_by_post(post_id=10, include_deleted=True)

        assert len(result) == 2

    def test_find_by_author(self):
        """Test recherche commentaires par auteur."""
        mock_models = [
            self._create_mock_comment_model(comment_id=i, author_id=5)
            for i in range(1, 3)
        ]
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.all.return_value = mock_models
        self.session.query.return_value = query_mock

        result = self.repo.find_by_author(author_id=5)

        assert len(result) == 2
        assert all(c.author_id == 5 for c in result)

    def test_count_by_post(self):
        """Test comptage commentaires par post."""
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.count.return_value = 5
        self.session.query.return_value = query_mock

        result = self.repo.count_by_post(post_id=10)

        assert result == 5

    def test_delete_success(self):
        """Test suppression commentaire réussie."""
        mock_model = self._create_mock_comment_model()
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_model
        self.session.query.return_value = query_mock

        result = self.repo.delete(1)

        assert result is True
        self.session.delete.assert_called_once_with(mock_model)
        self.session.commit.assert_called_once()

    def test_delete_not_found(self):
        """Test suppression commentaire non trouvé."""
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        self.session.query.return_value = query_mock

        result = self.repo.delete(999)

        assert result is False
        self.session.delete.assert_not_called()


# ============================================================================
# Tests SQLAlchemyLikeRepository
# ============================================================================


class TestSQLAlchemyLikeRepository:
    """Tests pour SQLAlchemyLikeRepository."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.session = Mock()
        self.repo = SQLAlchemyLikeRepository(self.session)

    def _create_mock_like_model(self, like_id=1, post_id=10, user_id=5):
        """Helper pour créer un mock de LikeModel."""
        mock = Mock()
        mock.id = like_id
        mock.post_id = post_id
        mock.user_id = user_id
        mock.created_at = datetime.now()
        return mock

    def test_save_like(self):
        """Test création d'un like."""
        like = Like(post_id=10, user_id=5)

        mock_model = self._create_mock_like_model()
        self.session.refresh = Mock(side_effect=lambda m: setattr(m, "id", 1))

        with patch(
            "modules.dashboard.infrastructure.persistence.sqlalchemy_like_repository.LikeModel"
        ) as MockModel:
            MockModel.return_value = mock_model

            result = self.repo.save(like)

            self.session.add.assert_called_once()
            self.session.commit.assert_called_once()
            assert result.post_id == 10

    def test_find_by_id_found(self):
        """Test recherche like trouvé."""
        mock_model = self._create_mock_like_model()
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_model
        self.session.query.return_value = query_mock

        result = self.repo.find_by_id(1)

        assert result is not None
        assert result.id == 1

    def test_find_by_id_not_found(self):
        """Test recherche like non trouvé."""
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        self.session.query.return_value = query_mock

        result = self.repo.find_by_id(999)

        assert result is None

    def test_find_by_post_and_user_found(self):
        """Test recherche like par post et user trouvé."""
        mock_model = self._create_mock_like_model()
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_model
        self.session.query.return_value = query_mock

        result = self.repo.find_by_post_and_user(post_id=10, user_id=5)

        assert result is not None
        assert result.post_id == 10
        assert result.user_id == 5

    def test_find_by_post_and_user_not_found(self):
        """Test recherche like par post et user non trouvé."""
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        self.session.query.return_value = query_mock

        result = self.repo.find_by_post_and_user(post_id=10, user_id=999)

        assert result is None

    def test_find_by_post(self):
        """Test recherche likes par post."""
        mock_models = [
            self._create_mock_like_model(like_id=i, post_id=10, user_id=i)
            for i in range(1, 4)
        ]
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.all.return_value = mock_models
        self.session.query.return_value = query_mock

        result = self.repo.find_by_post(post_id=10)

        assert len(result) == 3
        assert all(like.post_id == 10 for like in result)

    def test_find_user_ids_by_post(self):
        """Test récupération IDs utilisateurs ayant liké."""
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [(1,), (2,), (3,)]
        self.session.query.return_value = query_mock

        result = self.repo.find_user_ids_by_post(post_id=10)

        assert result == [1, 2, 3]

    def test_count_by_post(self):
        """Test comptage likes par post."""
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.count.return_value = 10
        self.session.query.return_value = query_mock

        result = self.repo.count_by_post(post_id=10)

        assert result == 10

    def test_delete_success(self):
        """Test suppression like réussie."""
        mock_model = self._create_mock_like_model()
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_model
        self.session.query.return_value = query_mock

        result = self.repo.delete(1)

        assert result is True
        self.session.delete.assert_called_once_with(mock_model)
        self.session.commit.assert_called_once()

    def test_delete_not_found(self):
        """Test suppression like non trouvé."""
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        self.session.query.return_value = query_mock

        result = self.repo.delete(999)

        assert result is False
        self.session.delete.assert_not_called()

    def test_delete_by_post_and_user_success(self):
        """Test suppression like par post et user réussie."""
        mock_model = self._create_mock_like_model()
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_model
        self.session.query.return_value = query_mock

        result = self.repo.delete_by_post_and_user(post_id=10, user_id=5)

        assert result is True
        self.session.delete.assert_called_once_with(mock_model)

    def test_delete_by_post_and_user_not_found(self):
        """Test suppression like par post et user non trouvé."""
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        self.session.query.return_value = query_mock

        result = self.repo.delete_by_post_and_user(post_id=10, user_id=999)

        assert result is False


# ============================================================================
# Tests SQLAlchemyPostMediaRepository
# ============================================================================


class TestSQLAlchemyPostMediaRepository:
    """Tests pour SQLAlchemyPostMediaRepository."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.session = Mock()
        self.repo = SQLAlchemyPostMediaRepository(self.session)

    def _create_mock_media_model(
        self,
        media_id=1,
        post_id=10,
        media_type="image",
        file_url="https://example.com/image.jpg",
    ):
        """Helper pour créer un mock de PostMediaModel."""
        mock = Mock()
        mock.id = media_id
        mock.post_id = post_id
        mock.media_type = media_type
        mock.file_url = file_url
        mock.thumbnail_url = None
        mock.original_filename = "image.jpg"
        mock.file_size_bytes = 1024
        mock.mime_type = "image/jpeg"
        mock.width = 800
        mock.height = 600
        mock.position = 0
        mock.created_at = datetime.now()
        return mock

    def test_save_media(self):
        """Test création d'un média."""
        media = PostMedia(
            post_id=10,
            media_type=MediaType.IMAGE,
            file_url="https://example.com/image.jpg",
        )

        mock_model = self._create_mock_media_model()
        self.session.refresh = Mock(side_effect=lambda m: setattr(m, "id", 1))

        with patch(
            "modules.dashboard.infrastructure.persistence.sqlalchemy_media_repository.PostMediaModel"
        ) as MockModel:
            MockModel.return_value = mock_model

            result = self.repo.save(media)

            self.session.add.assert_called_once()
            self.session.commit.assert_called_once()
            assert result.post_id == 10

    def test_save_all_medias(self):
        """Test création de plusieurs médias."""
        medias = [
            PostMedia(
                post_id=10,
                media_type=MediaType.IMAGE,
                file_url=f"https://example.com/image{i}.jpg",
            )
            for i in range(3)
        ]

        mock_models = [self._create_mock_media_model(media_id=i) for i in range(3)]

        with patch(
            "modules.dashboard.infrastructure.persistence.sqlalchemy_media_repository.PostMediaModel"
        ) as MockModel:
            MockModel.side_effect = mock_models

            result = self.repo.save_all(medias)

            self.session.add_all.assert_called_once()
            self.session.commit.assert_called_once()
            assert len(result) == 3

    def test_find_by_id_found(self):
        """Test recherche média trouvé."""
        mock_model = self._create_mock_media_model()
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_model
        self.session.query.return_value = query_mock

        result = self.repo.find_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.media_type == MediaType.IMAGE

    def test_find_by_id_not_found(self):
        """Test recherche média non trouvé."""
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        self.session.query.return_value = query_mock

        result = self.repo.find_by_id(999)

        assert result is None

    def test_find_by_post(self):
        """Test recherche médias par post."""
        mock_models = [
            self._create_mock_media_model(media_id=i, post_id=10, file_url=f"url{i}")
            for i in range(1, 4)
        ]
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.all.return_value = mock_models
        self.session.query.return_value = query_mock

        result = self.repo.find_by_post(post_id=10)

        assert len(result) == 3
        assert all(m.post_id == 10 for m in result)

    def test_count_by_post(self):
        """Test comptage médias par post."""
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.count.return_value = 5
        self.session.query.return_value = query_mock

        result = self.repo.count_by_post(post_id=10)

        assert result == 5

    def test_delete_success(self):
        """Test suppression média réussie."""
        mock_model = self._create_mock_media_model()
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_model
        self.session.query.return_value = query_mock

        result = self.repo.delete(1)

        assert result is True
        self.session.delete.assert_called_once_with(mock_model)
        self.session.commit.assert_called_once()

    def test_delete_not_found(self):
        """Test suppression média non trouvé."""
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        self.session.query.return_value = query_mock

        result = self.repo.delete(999)

        assert result is False
        self.session.delete.assert_not_called()

    def test_delete_by_post(self):
        """Test suppression tous médias d'un post."""
        query_mock = Mock()
        query_mock.filter.return_value = query_mock
        query_mock.delete.return_value = 3
        self.session.query.return_value = query_mock

        result = self.repo.delete_by_post(post_id=10)

        assert result == 3
        self.session.commit.assert_called_once()
