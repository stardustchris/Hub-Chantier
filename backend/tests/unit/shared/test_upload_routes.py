"""Tests unitaires pour les routes d'upload."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException

from shared.infrastructure.web.upload_routes import (
    router,
    validate_file_size,
    get_file_service,
    UploadResponse,
    MultiUploadResponse,
    MAX_UPLOAD_SIZE_BYTES,
    MAX_PHOTOS_PER_POST,
)
from shared.infrastructure.files import FileService, FileUploadError


class TestValidateFileSize:
    """Tests de validation de taille de fichier."""

    @pytest.mark.asyncio
    async def test_valid_file_size(self):
        """Test fichier de taille valide."""
        content = b"x" * 1000  # 1 KB
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.read = AsyncMock(side_effect=[content, b""])

        result = await validate_file_size(mock_file)

        assert result == content

    @pytest.mark.asyncio
    async def test_file_too_large(self):
        """Test fichier trop volumineux."""
        # Simuler un fichier de 15 MB (> 10 MB limite)
        chunk = b"x" * (64 * 1024)  # 64 KB chunk

        mock_file = AsyncMock(spec=UploadFile)
        # Retourne des chunks jusqu'a depasser la limite
        mock_file.read = AsyncMock(side_effect=[chunk] * 200 + [b""])

        with pytest.raises(HTTPException) as exc_info:
            await validate_file_size(mock_file)

        assert exc_info.value.status_code == 413
        assert "trop volumineux" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_empty_file(self):
        """Test fichier vide."""
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.read = AsyncMock(return_value=b"")

        result = await validate_file_size(mock_file)

        assert result == b""

    @pytest.mark.asyncio
    async def test_custom_max_size_exceeds(self):
        """Test avec taille max personnalisee depassee."""
        content = b"x" * 1000

        mock_file = AsyncMock(spec=UploadFile)
        mock_file.read = AsyncMock(side_effect=[content, b""])

        with pytest.raises(HTTPException) as exc_info:
            await validate_file_size(mock_file, max_size=500)

        assert exc_info.value.status_code == 413


class TestUploadResponseModels:
    """Tests des modeles Pydantic."""

    def test_upload_response_basic(self):
        """Test UploadResponse basique."""
        response = UploadResponse(url="/uploads/test.jpg")

        assert response.url == "/uploads/test.jpg"
        assert response.thumbnail_url is None

    def test_upload_response_with_thumbnail(self):
        """Test UploadResponse avec thumbnail."""
        response = UploadResponse(
            url="/uploads/test.jpg",
            thumbnail_url="/uploads/thumb_test.jpg"
        )

        assert response.thumbnail_url == "/uploads/thumb_test.jpg"

    def test_multi_upload_response(self):
        """Test MultiUploadResponse."""
        files = [
            UploadResponse(url="/uploads/1.jpg"),
            UploadResponse(url="/uploads/2.jpg"),
        ]
        response = MultiUploadResponse(files=files)

        assert len(response.files) == 2


class TestUploadRoutesWithApp:
    """Tests d'integration des routes d'upload."""

    @pytest.fixture
    def mock_file_service(self, tmp_path):
        """Mock du FileService."""
        service = Mock(spec=FileService)
        service.upload_profile_photo.return_value = "/uploads/profiles/test.jpg"
        service.upload_post_media.return_value = (
            "/uploads/posts/test.jpg",
            "/uploads/thumbnails/thumb_test.jpg"
        )
        service.upload_chantier_photo.return_value = "/uploads/chantiers/test.jpg"
        return service

    @pytest.fixture
    def app(self, mock_file_service):
        """App FastAPI de test."""
        app = FastAPI()
        app.include_router(router)

        # Override dependencies
        def override_file_service():
            return mock_file_service

        def override_current_user():
            return 1

        app.dependency_overrides[get_file_service] = override_file_service

        # Mock get_current_user_id
        from shared.infrastructure.web.upload_routes import get_current_user_id
        app.dependency_overrides[get_current_user_id] = override_current_user

        return app

    @pytest.fixture
    def client(self, app):
        return TestClient(app)

    def test_upload_profile_photo_success(self, client, mock_file_service):
        """Test upload photo de profil reussi."""
        files = {"file": ("avatar.jpg", b"fake image content", "image/jpeg")}

        response = client.post("/uploads/profile", files=files)

        assert response.status_code == 200
        assert response.json()["url"] == "/uploads/profiles/test.jpg"

    def test_upload_profile_photo_error(self, client, mock_file_service):
        """Test erreur upload photo de profil."""
        mock_file_service.upload_profile_photo.side_effect = FileUploadError("Invalid image")

        files = {"file": ("bad.jpg", b"not an image", "image/jpeg")}

        response = client.post("/uploads/profile", files=files)

        assert response.status_code == 400
        assert "Invalid image" in response.json()["detail"]

    def test_upload_post_media_success(self, client, mock_file_service):
        """Test upload media post reussi."""
        files = [
            ("files", ("photo1.jpg", b"content1", "image/jpeg")),
            ("files", ("photo2.jpg", b"content2", "image/jpeg")),
        ]

        response = client.post("/uploads/posts/123", files=files)

        assert response.status_code == 200
        data = response.json()
        assert len(data["files"]) == 2

    def test_upload_post_media_too_many_files(self, client, mock_file_service):
        """Test limite max photos par post."""
        files = [
            ("files", (f"photo{i}.jpg", b"content", "image/jpeg"))
            for i in range(MAX_PHOTOS_PER_POST + 1)
        ]

        response = client.post("/uploads/posts/123", files=files)

        assert response.status_code == 400
        assert f"Maximum {MAX_PHOTOS_PER_POST}" in response.json()["detail"]

    def test_upload_chantier_photo_success(self, client, mock_file_service):
        """Test upload photo chantier reussi."""
        files = {"file": ("site.jpg", b"fake image", "image/jpeg")}

        response = client.post("/uploads/chantiers/456", files=files)

        assert response.status_code == 200
        assert response.json()["url"] == "/uploads/chantiers/test.jpg"


class TestGetUploadedFile:
    """Tests de la route de recuperation de fichiers."""

    @pytest.fixture
    def app_with_files(self, tmp_path):
        """App avec fichiers de test."""
        app = FastAPI()
        app.include_router(router)

        # Creer les repertoires et fichiers de test
        (tmp_path / "profiles").mkdir()
        (tmp_path / "posts").mkdir()
        (tmp_path / "thumbnails").mkdir()
        (tmp_path / "chantiers").mkdir()

        test_file = tmp_path / "profiles" / "test.jpg"
        test_file.write_bytes(b"fake jpeg content")

        # Patcher UPLOAD_DIR
        with patch("shared.infrastructure.web.upload_routes.UPLOAD_DIR", str(tmp_path)):
            yield app

    @pytest.fixture
    def client_files(self, app_with_files):
        return TestClient(app_with_files)

    def test_get_file_success(self, client_files, tmp_path):
        """Test recuperation fichier existant."""
        with patch("shared.infrastructure.web.upload_routes.UPLOAD_DIR", str(tmp_path)):
            response = client_files.get("/uploads/profiles/test.jpg")

        assert response.status_code == 200

    def test_get_file_invalid_category(self, client_files):
        """Test categorie invalide."""
        response = client_files.get("/uploads/invalid/test.jpg")

        assert response.status_code == 404
        assert "non trouvé" in response.json()["detail"]

    def test_get_file_path_traversal_blocked(self, client_files):
        """Test protection contre path traversal."""
        # Les URLs avec .. sont normalisees par le routeur FastAPI
        # Le test verifie que le fichier n'est pas accessible
        response = client_files.get("/uploads/profiles/../../../etc/passwd")

        # Peut etre 400 ou 404 selon le parsing de l'URL
        assert response.status_code in (400, 404)

    def test_get_file_double_dot_blocked(self, client_files):
        """Test blocage double point dans le nom."""
        response = client_files.get("/uploads/profiles/..test.jpg")

        # Peut etre 400 ou 404 selon le parsing
        assert response.status_code in (400, 404)

    def test_get_nonexistent_file(self, client_files, tmp_path):
        """Test fichier inexistant."""
        with patch("shared.infrastructure.web.upload_routes.UPLOAD_DIR", str(tmp_path)):
            response = client_files.get("/uploads/profiles/nonexistent.jpg")

        assert response.status_code == 404


class TestMimeTypes:
    """Tests des types MIME."""

    @pytest.fixture
    def app_mime(self, tmp_path):
        """App pour tester les types MIME."""
        app = FastAPI()
        app.include_router(router)

        # Creer fichiers de test
        for category in ["profiles", "posts", "thumbnails", "chantiers"]:
            (tmp_path / category).mkdir()

        return app, tmp_path

    def test_jpeg_mime_type(self, app_mime):
        """Test type MIME JPEG."""
        app, tmp_path = app_mime
        (tmp_path / "profiles" / "test.jpg").write_bytes(b"fake")

        with patch("shared.infrastructure.web.upload_routes.UPLOAD_DIR", str(tmp_path)):
            client = TestClient(app)
            response = client.get("/uploads/profiles/test.jpg")

        assert response.headers["content-type"] == "image/jpeg"

    def test_png_mime_type(self, app_mime):
        """Test type MIME PNG."""
        app, tmp_path = app_mime
        (tmp_path / "profiles" / "test.png").write_bytes(b"fake")

        with patch("shared.infrastructure.web.upload_routes.UPLOAD_DIR", str(tmp_path)):
            client = TestClient(app)
            response = client.get("/uploads/profiles/test.png")

        assert response.headers["content-type"] == "image/png"

    def test_gif_mime_type(self, app_mime):
        """Test type MIME GIF."""
        app, tmp_path = app_mime
        (tmp_path / "profiles" / "test.gif").write_bytes(b"fake")

        with patch("shared.infrastructure.web.upload_routes.UPLOAD_DIR", str(tmp_path)):
            client = TestClient(app)
            response = client.get("/uploads/profiles/test.gif")

        assert response.headers["content-type"] == "image/gif"

    def test_webp_mime_type(self, app_mime):
        """Test type MIME WebP."""
        app, tmp_path = app_mime
        (tmp_path / "profiles" / "test.webp").write_bytes(b"fake")

        with patch("shared.infrastructure.web.upload_routes.UPLOAD_DIR", str(tmp_path)):
            client = TestClient(app)
            response = client.get("/uploads/profiles/test.webp")

        assert response.headers["content-type"] == "image/webp"

    def test_unknown_extension_octet_stream(self, app_mime):
        """Test extension inconnue -> octet-stream."""
        app, tmp_path = app_mime
        (tmp_path / "profiles" / "test.xyz").write_bytes(b"fake")

        with patch("shared.infrastructure.web.upload_routes.UPLOAD_DIR", str(tmp_path)):
            client = TestClient(app)
            response = client.get("/uploads/profiles/test.xyz")

        assert response.headers["content-type"] == "application/octet-stream"
