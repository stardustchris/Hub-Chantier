"""Tests unitaires pour les entités Comment, Like et PostMedia."""

import pytest
from datetime import datetime

from modules.dashboard.domain.entities.comment import Comment
from modules.dashboard.domain.entities.like import Like
from modules.dashboard.domain.entities.post_media import PostMedia, MediaType, MAX_FILE_SIZE_MB


class TestComment:
    """Tests pour l'entité Comment."""

    def test_create_comment_valid(self):
        """Test création commentaire valide."""
        comment = Comment(
            post_id=1,
            author_id=2,
            content="Super post!",
        )

        assert comment.post_id == 1
        assert comment.author_id == 2
        assert comment.content == "Super post!"
        assert comment.is_deleted is False
        assert comment.id is None

    def test_create_comment_content_trimmed(self):
        """Test que le contenu est trimé."""
        comment = Comment(
            post_id=1,
            author_id=2,
            content="  Contenu avec espaces  ",
        )

        assert comment.content == "Contenu avec espaces"

    def test_create_comment_empty_content_raises(self):
        """Test erreur si contenu vide."""
        with pytest.raises(ValueError, match="ne peut pas être vide"):
            Comment(post_id=1, author_id=2, content="")

    def test_create_comment_whitespace_content_raises(self):
        """Test erreur si contenu uniquement espaces."""
        with pytest.raises(ValueError, match="ne peut pas être vide"):
            Comment(post_id=1, author_id=2, content="   ")

    def test_update_content(self):
        """Test mise à jour du contenu."""
        comment = Comment(post_id=1, author_id=2, content="Original")
        original_updated_at = comment.updated_at

        comment.update_content("Nouveau contenu")

        assert comment.content == "Nouveau contenu"
        assert comment.updated_at >= original_updated_at

    def test_update_content_empty_raises(self):
        """Test erreur si nouveau contenu vide."""
        comment = Comment(post_id=1, author_id=2, content="Original")

        with pytest.raises(ValueError, match="ne peut pas être vide"):
            comment.update_content("")

    def test_delete_comment(self):
        """Test suppression commentaire."""
        comment = Comment(post_id=1, author_id=2, content="Test")

        assert comment.is_visible is True

        comment.delete()

        assert comment.is_deleted is True
        assert comment.is_visible is False

    def test_is_visible_true_when_not_deleted(self):
        """Test is_visible True si non supprimé."""
        comment = Comment(post_id=1, author_id=2, content="Test")

        assert comment.is_visible is True

    def test_equality_same_id(self):
        """Test égalité même ID."""
        c1 = Comment(id=1, post_id=1, author_id=1, content="A")
        c2 = Comment(id=1, post_id=2, author_id=2, content="B")

        assert c1 == c2

    def test_equality_different_id(self):
        """Test inégalité IDs différents."""
        c1 = Comment(id=1, post_id=1, author_id=1, content="A")
        c2 = Comment(id=2, post_id=1, author_id=1, content="A")

        assert c1 != c2

    def test_equality_none_id(self):
        """Test inégalité si un ID est None."""
        c1 = Comment(id=1, post_id=1, author_id=1, content="A")
        c2 = Comment(post_id=1, author_id=1, content="A")

        assert c1 != c2

    def test_equality_not_comment(self):
        """Test inégalité avec autre type."""
        c = Comment(id=1, post_id=1, author_id=1, content="A")

        assert c != "not a comment"

    def test_hash_with_id(self):
        """Test hash avec ID."""
        c = Comment(id=42, post_id=1, author_id=1, content="A")

        assert hash(c) == hash(42)

    def test_hash_without_id(self):
        """Test hash sans ID."""
        c = Comment(post_id=1, author_id=1, content="A")

        assert hash(c) is not None


class TestLike:
    """Tests pour l'entité Like."""

    def test_create_like_valid(self):
        """Test création like valide."""
        like = Like(post_id=1, user_id=2)

        assert like.post_id == 1
        assert like.user_id == 2
        assert like.id is None
        assert like.created_at is not None

    def test_equality_same_id(self):
        """Test égalité même ID."""
        l1 = Like(id=1, post_id=1, user_id=1)
        l2 = Like(id=1, post_id=2, user_id=2)

        assert l1 == l2

    def test_equality_different_id(self):
        """Test inégalité IDs différents."""
        l1 = Like(id=1, post_id=1, user_id=1)
        l2 = Like(id=2, post_id=1, user_id=1)

        assert l1 != l2

    def test_equality_no_id_same_post_user(self):
        """Test égalité sans ID mais même post_id/user_id."""
        l1 = Like(post_id=1, user_id=2)
        l2 = Like(post_id=1, user_id=2)

        assert l1 == l2

    def test_equality_no_id_different_post_user(self):
        """Test inégalité sans ID et différent post_id/user_id."""
        l1 = Like(post_id=1, user_id=2)
        l2 = Like(post_id=1, user_id=3)

        assert l1 != l2

    def test_equality_not_like(self):
        """Test inégalité avec autre type."""
        l = Like(id=1, post_id=1, user_id=1)

        assert l != "not a like"

    def test_hash(self):
        """Test hash basé sur post_id et user_id."""
        l1 = Like(post_id=1, user_id=2)
        l2 = Like(post_id=1, user_id=2)

        assert hash(l1) == hash(l2)
        assert hash(l1) == hash((1, 2))


class TestPostMedia:
    """Tests pour l'entité PostMedia."""

    def test_create_media_valid(self):
        """Test création média valide."""
        media = PostMedia(
            post_id=1,
            media_type=MediaType.IMAGE,
            file_url="https://example.com/image.jpg",
        )

        assert media.post_id == 1
        assert media.media_type == MediaType.IMAGE
        assert media.file_url == "https://example.com/image.jpg"
        assert media.position == 0
        assert media.id is None

    def test_create_media_empty_url_raises(self):
        """Test erreur si URL vide."""
        with pytest.raises(ValueError, match="URL du fichier ne peut pas être vide"):
            PostMedia(
                post_id=1,
                media_type=MediaType.IMAGE,
                file_url="",
            )

    def test_create_media_with_dimensions(self):
        """Test création avec dimensions."""
        media = PostMedia(
            post_id=1,
            media_type=MediaType.IMAGE,
            file_url="https://example.com/image.jpg",
            width=1920,
            height=1080,
            file_size_bytes=1024 * 1024,  # 1 MB
        )

        assert media.width == 1920
        assert media.height == 1080
        assert media.file_size_bytes == 1024 * 1024

    def test_file_size_mb(self):
        """Test calcul taille en MB."""
        media = PostMedia(
            post_id=1,
            media_type=MediaType.IMAGE,
            file_url="https://example.com/image.jpg",
            file_size_bytes=2 * 1024 * 1024,  # 2 MB
        )

        assert media.file_size_mb == 2.0

    def test_file_size_mb_none(self):
        """Test file_size_mb retourne None si pas de taille."""
        media = PostMedia(
            post_id=1,
            media_type=MediaType.IMAGE,
            file_url="https://example.com/image.jpg",
        )

        assert media.file_size_mb is None

    def test_is_over_size_limit_true(self):
        """Test is_over_size_limit True si > 2MB."""
        media = PostMedia(
            post_id=1,
            media_type=MediaType.IMAGE,
            file_url="https://example.com/image.jpg",
            file_size_bytes=3 * 1024 * 1024,  # 3 MB > 2 MB
        )

        assert media.is_over_size_limit is True

    def test_is_over_size_limit_false(self):
        """Test is_over_size_limit False si <= 2MB."""
        media = PostMedia(
            post_id=1,
            media_type=MediaType.IMAGE,
            file_url="https://example.com/image.jpg",
            file_size_bytes=1 * 1024 * 1024,  # 1 MB < 2 MB
        )

        assert media.is_over_size_limit is False

    def test_is_over_size_limit_no_size(self):
        """Test is_over_size_limit False si pas de taille."""
        media = PostMedia(
            post_id=1,
            media_type=MediaType.IMAGE,
            file_url="https://example.com/image.jpg",
        )

        assert media.is_over_size_limit is False

    def test_aspect_ratio(self):
        """Test calcul aspect ratio."""
        media = PostMedia(
            post_id=1,
            media_type=MediaType.IMAGE,
            file_url="https://example.com/image.jpg",
            width=1920,
            height=1080,
        )

        assert abs(media.aspect_ratio - 16/9) < 0.01

    def test_aspect_ratio_none_no_dimensions(self):
        """Test aspect_ratio None si pas de dimensions."""
        media = PostMedia(
            post_id=1,
            media_type=MediaType.IMAGE,
            file_url="https://example.com/image.jpg",
        )

        assert media.aspect_ratio is None

    def test_aspect_ratio_none_zero_height(self):
        """Test aspect_ratio None si height = 0."""
        media = PostMedia(
            post_id=1,
            media_type=MediaType.IMAGE,
            file_url="https://example.com/image.jpg",
            width=1920,
            height=0,
        )

        assert media.aspect_ratio is None

    def test_equality_same_id(self):
        """Test égalité même ID."""
        m1 = PostMedia(id=1, post_id=1, media_type=MediaType.IMAGE, file_url="a.jpg")
        m2 = PostMedia(id=1, post_id=2, media_type=MediaType.IMAGE, file_url="b.jpg")

        assert m1 == m2

    def test_equality_different_id(self):
        """Test inégalité IDs différents."""
        m1 = PostMedia(id=1, post_id=1, media_type=MediaType.IMAGE, file_url="a.jpg")
        m2 = PostMedia(id=2, post_id=1, media_type=MediaType.IMAGE, file_url="a.jpg")

        assert m1 != m2

    def test_equality_none_id(self):
        """Test inégalité si un ID est None."""
        m1 = PostMedia(id=1, post_id=1, media_type=MediaType.IMAGE, file_url="a.jpg")
        m2 = PostMedia(post_id=1, media_type=MediaType.IMAGE, file_url="a.jpg")

        assert m1 != m2

    def test_equality_not_media(self):
        """Test inégalité avec autre type."""
        m = PostMedia(id=1, post_id=1, media_type=MediaType.IMAGE, file_url="a.jpg")

        assert m != "not a media"

    def test_hash_with_id(self):
        """Test hash avec ID."""
        m = PostMedia(id=42, post_id=1, media_type=MediaType.IMAGE, file_url="a.jpg")

        assert hash(m) == hash(42)

    def test_hash_without_id(self):
        """Test hash sans ID."""
        m = PostMedia(post_id=1, media_type=MediaType.IMAGE, file_url="a.jpg")

        assert hash(m) is not None


class TestMediaType:
    """Tests pour MediaType."""

    def test_media_type_str(self):
        """Test conversion string."""
        assert str(MediaType.IMAGE) == "image"

    def test_max_file_size_constant(self):
        """Test constante MAX_FILE_SIZE_MB."""
        assert MAX_FILE_SIZE_MB == 2
