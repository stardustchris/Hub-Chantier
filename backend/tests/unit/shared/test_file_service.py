"""Tests unitaires pour FileService."""

import pytest
import io
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

from shared.infrastructure.files.file_service import FileService, FileUploadError


class TestFileServiceInit:
    """Tests d'initialisation du FileService."""

    def test_init_creates_directories(self, tmp_path):
        """Test que l'init cree les repertoires necessaires."""
        upload_dir = tmp_path / "uploads"
        service = FileService(upload_dir=str(upload_dir))

        assert (upload_dir / "profiles").exists()
        assert (upload_dir / "posts").exists()
        assert (upload_dir / "chantiers").exists()
        assert (upload_dir / "thumbnails").exists()

    def test_init_with_existing_directory(self, tmp_path):
        """Test init avec repertoire existant."""
        upload_dir = tmp_path / "uploads"
        upload_dir.mkdir()
        (upload_dir / "profiles").mkdir()

        service = FileService(upload_dir=str(upload_dir))
        assert service.upload_dir == upload_dir


class TestGenerateFilename:
    """Tests de generation de noms de fichiers."""

    def test_generate_unique_filename(self, tmp_path):
        """Test que les noms generes sont uniques."""
        service = FileService(upload_dir=str(tmp_path))

        name1 = service._generate_filename("photo.jpg")
        name2 = service._generate_filename("photo.jpg")

        assert name1 != name2
        assert name1.endswith(".jpg")
        assert name2.endswith(".jpg")

    def test_preserves_extension(self, tmp_path):
        """Test que l'extension est preservee."""
        service = FileService(upload_dir=str(tmp_path))

        assert service._generate_filename("image.png").endswith(".png")
        assert service._generate_filename("photo.JPEG").endswith(".jpeg")
        assert service._generate_filename("file.GIF").endswith(".gif")


class TestValidateImage:
    """Tests de validation d'images."""

    @pytest.fixture
    def service(self, tmp_path):
        return FileService(upload_dir=str(tmp_path))

    @pytest.fixture
    def valid_image_bytes(self):
        """Cree une image valide en bytes."""
        img = Image.new("RGB", (100, 100), color="red")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        return buffer.getvalue()

    def test_validate_valid_image(self, service, valid_image_bytes):
        """Test validation d'une image valide."""
        service._validate_image(valid_image_bytes, "photo.jpg")

    def test_reject_invalid_extension(self, service, valid_image_bytes):
        """Test rejet d'extension non autorisee."""
        with pytest.raises(FileUploadError) as exc_info:
            service._validate_image(valid_image_bytes, "document.pdf")

        assert "Extension non autorisée" in str(exc_info.value)

    def test_reject_invalid_image_content(self, service):
        """Test rejet de contenu non-image."""
        fake_content = b"This is not an image"

        with pytest.raises(FileUploadError) as exc_info:
            service._validate_image(fake_content, "fake.jpg")

        assert "n'est pas une image valide" in str(exc_info.value)

    def test_accept_all_valid_extensions(self, service, valid_image_bytes):
        """Test acceptation de toutes les extensions valides."""
        for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            service._validate_image(valid_image_bytes, f"photo{ext}")


class TestCompressImage:
    """Tests de compression d'images."""

    @pytest.fixture
    def service(self, tmp_path):
        return FileService(upload_dir=str(tmp_path))

    @pytest.fixture
    def large_image_bytes(self):
        """Cree une grande image."""
        img = Image.new("RGB", (3000, 3000), color="blue")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=100)
        return buffer.getvalue()

    @pytest.fixture
    def rgba_image_bytes(self):
        """Cree une image RGBA."""
        img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def test_compress_large_image(self, service, large_image_bytes):
        """Test compression d'une grande image."""
        compressed = service._compress_image(large_image_bytes)

        # Verifier que l'image est redimensionnee
        img = Image.open(io.BytesIO(compressed))
        assert max(img.size) <= service.MAX_IMAGE_DIMENSION

    def test_compress_to_max_size(self, service, large_image_bytes):
        """Test compression jusqu'a la taille max."""
        max_size = 100 * 1024  # 100 KB
        compressed = service._compress_image(large_image_bytes, max_size_bytes=max_size)

        assert len(compressed) <= max_size

    def test_convert_rgba_to_rgb(self, service, rgba_image_bytes):
        """Test conversion RGBA vers RGB."""
        compressed = service._compress_image(rgba_image_bytes)

        img = Image.open(io.BytesIO(compressed))
        assert img.mode == "RGB"

    def test_compress_p_mode_image(self, service):
        """Test compression d'image en mode P (palette)."""
        img = Image.new("P", (100, 100))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        p_image_bytes = buffer.getvalue()

        compressed = service._compress_image(p_image_bytes)
        result_img = Image.open(io.BytesIO(compressed))
        assert result_img.mode == "RGB"


class TestCreateThumbnail:
    """Tests de creation de miniatures."""

    @pytest.fixture
    def service(self, tmp_path):
        return FileService(upload_dir=str(tmp_path))

    @pytest.fixture
    def image_bytes(self):
        """Cree une image standard."""
        img = Image.new("RGB", (800, 600), color="green")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        return buffer.getvalue()

    def test_create_thumbnail(self, service, image_bytes):
        """Test creation de miniature."""
        thumbnail = service._create_thumbnail(image_bytes)

        img = Image.open(io.BytesIO(thumbnail))
        assert img.size[0] <= service.THUMBNAIL_SIZE[0]
        assert img.size[1] <= service.THUMBNAIL_SIZE[1]

    def test_thumbnail_preserves_aspect_ratio(self, service, image_bytes):
        """Test que le ratio est preserve."""
        thumbnail = service._create_thumbnail(image_bytes)

        img = Image.open(io.BytesIO(thumbnail))
        # L'image originale est 800x600 (4:3)
        # La miniature doit garder ce ratio
        original_ratio = 800 / 600
        thumb_ratio = img.size[0] / img.size[1]
        assert abs(original_ratio - thumb_ratio) < 0.1


class TestUploadProfilePhoto:
    """Tests d'upload de photo de profil."""

    @pytest.fixture
    def service(self, tmp_path):
        return FileService(upload_dir=str(tmp_path))

    @pytest.fixture
    def valid_image_bytes(self):
        img = Image.new("RGB", (500, 500), color="red")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        return buffer.getvalue()

    def test_upload_profile_photo_success(self, service, valid_image_bytes):
        """Test upload reussi de photo de profil."""
        url = service.upload_profile_photo(valid_image_bytes, "avatar.jpg", user_id=42)

        assert url.startswith("/uploads/profiles/")
        assert "user_42_" in url
        assert url.endswith(".jpg")

    def test_upload_creates_file(self, service, valid_image_bytes, tmp_path):
        """Test que le fichier est cree sur disque."""
        url = service.upload_profile_photo(valid_image_bytes, "avatar.jpg", user_id=1)

        filename = url.split("/")[-1]
        file_path = tmp_path / "profiles" / filename
        assert file_path.exists()

    def test_upload_converts_png_to_jpg(self, service):
        """Test conversion PNG vers JPG."""
        img = Image.new("RGB", (100, 100), color="blue")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")

        url = service.upload_profile_photo(buffer.getvalue(), "avatar.png", user_id=1)
        assert url.endswith(".jpg")


class TestUploadPostMedia:
    """Tests d'upload de medias pour posts."""

    @pytest.fixture
    def service(self, tmp_path):
        return FileService(upload_dir=str(tmp_path))

    @pytest.fixture
    def valid_image_bytes(self):
        img = Image.new("RGB", (800, 600), color="green")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        return buffer.getvalue()

    def test_upload_post_media_returns_tuple(self, service, valid_image_bytes):
        """Test que upload retourne URL et thumbnail."""
        url, thumb_url = service.upload_post_media(valid_image_bytes, "photo.jpg", post_id=123)

        assert url.startswith("/uploads/posts/")
        assert thumb_url.startswith("/uploads/thumbnails/")

    def test_upload_post_media_creates_both_files(self, service, valid_image_bytes, tmp_path):
        """Test creation des deux fichiers."""
        url, thumb_url = service.upload_post_media(valid_image_bytes, "photo.jpg", post_id=1)

        main_filename = url.split("/")[-1]
        thumb_filename = thumb_url.split("/")[-1]

        assert (tmp_path / "posts" / main_filename).exists()
        assert (tmp_path / "thumbnails" / thumb_filename).exists()


class TestUploadChantierPhoto:
    """Tests d'upload de photo de chantier."""

    @pytest.fixture
    def service(self, tmp_path):
        return FileService(upload_dir=str(tmp_path))

    @pytest.fixture
    def valid_image_bytes(self):
        img = Image.new("RGB", (1000, 800), color="yellow")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        return buffer.getvalue()

    def test_upload_chantier_photo_success(self, service, valid_image_bytes):
        """Test upload reussi de photo de chantier."""
        url = service.upload_chantier_photo(valid_image_bytes, "site.jpg", chantier_id=99)

        assert url.startswith("/uploads/chantiers/")
        assert "chantier_99_" in url

    def test_upload_creates_file(self, service, valid_image_bytes, tmp_path):
        """Test que le fichier est cree."""
        url = service.upload_chantier_photo(valid_image_bytes, "site.jpg", chantier_id=5)

        filename = url.split("/")[-1]
        assert (tmp_path / "chantiers" / filename).exists()


class TestDeleteFile:
    """Tests de suppression de fichiers."""

    @pytest.fixture
    def service(self, tmp_path):
        return FileService(upload_dir=str(tmp_path))

    def test_delete_existing_file(self, service, tmp_path):
        """Test suppression d'un fichier existant."""
        # Creer un fichier
        test_file = tmp_path / "profiles" / "test.jpg"
        test_file.write_bytes(b"test content")

        result = service.delete_file("/uploads/profiles/test.jpg")

        assert result is True
        assert not test_file.exists()

    def test_delete_nonexistent_file(self, service):
        """Test suppression d'un fichier inexistant."""
        result = service.delete_file("/uploads/profiles/nonexistent.jpg")
        assert result is False

    def test_delete_invalid_url(self, service):
        """Test avec URL invalide."""
        result = service.delete_file("/invalid/path/file.jpg")
        assert result is False

    def test_delete_file_path_traversal_blocked(self, service, tmp_path):
        """Test que le path traversal est bloque."""
        # Creer un fichier en dehors du repertoire uploads
        outside_file = tmp_path / "secret.txt"
        outside_file.write_text("secret")

        # Tenter de supprimer via path traversal
        result = service.delete_file("/uploads/../secret.txt")

        # Le fichier ne doit pas etre supprime
        assert outside_file.exists()


class TestFileUploadError:
    """Tests de l'exception FileUploadError."""

    def test_error_message(self):
        """Test du message d'erreur."""
        error = FileUploadError("Test error message")
        assert error.message == "Test error message"
        assert str(error) == "Test error message"
