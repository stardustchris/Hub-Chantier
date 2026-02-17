"""Tests unitaires pour les validations de permissions dans les routes pointages."""

import pytest
from datetime import date
from fastapi import HTTPException
from unittest.mock import Mock, MagicMock

from modules.pointages.infrastructure.web.routes import (
    validate_pointage,
    reject_pointage,
    export_feuilles_heures,
)
from modules.pointages.domain.services.permission_service import (
    PointagePermissionService,
)


class TestValidatePointagePermissions:
    """Tests pour les permissions de validation de pointages (SEC-PTG-003)."""

    def test_validate_pointage_compagnon_forbidden(self):
        """Un compagnon ne peut pas valider de pointages."""
        # Arrange
        pointage_id = 1
        validateur_id = 7
        current_user_role = "compagnon"
        event_bus = MagicMock()
        controller = MagicMock()

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            import asyncio

            asyncio.run(
                validate_pointage(
                    pointage_id=pointage_id,
                    validateur_id=validateur_id,
                    current_user_role=current_user_role,
                    event_bus=event_bus,
                    controller=controller,
                )
            )

        assert exc_info.value.status_code == 403
        assert (
            "permission de valider des pointages"
            in exc_info.value.detail.lower()
        )
        # Le controller ne doit pas être appelé
        controller.validate_pointage.assert_not_called()

    def test_validate_pointage_chef_success(self):
        """Un chef de chantier peut valider des pointages."""
        # Arrange
        pointage_id = 1
        validateur_id = 4
        current_user_role = "chef_chantier"
        event_bus = MagicMock()
        controller = MagicMock()
        db = MagicMock()

        # Mock du résultat du controller
        controller.validate_pointage.return_value = {
            "id": pointage_id,
            "utilisateur_id": 7,
            "chantier_id": 1,
            "date_pointage": date(2026, 1, 20),
            "heures_normales": "08:00",
            "heures_supplementaires": "00:00",
            "statut": "valide",
        }

        # Mock de l'event_bus.publish (async)
        async def mock_publish(event):
            pass

        event_bus.publish = mock_publish

        # Mock _get_chef_chantier_ids (uses fetchall(), not scalars().all())
        db.execute.return_value.fetchall.return_value = [(1,)]

        # Mock controller.get_pointage (called first to get chantier_id)
        controller.get_pointage.return_value = {"id": pointage_id, "chantier_id": 1, "utilisateur_id": 7}

        # Act
        import asyncio

        result = asyncio.run(
            validate_pointage(
                pointage_id=pointage_id,
                validateur_id=validateur_id,
                current_user_role=current_user_role,
                event_bus=event_bus,
                controller=controller,
                db=db,
            )
        )

        # Assert
        controller.validate_pointage.assert_called_once_with(
            pointage_id, validateur_id
        )
        assert result["statut"] == "valide"

    def test_validate_pointage_conducteur_success(self):
        """Un conducteur de travaux peut valider des pointages."""
        # Arrange
        pointage_id = 1
        validateur_id = 3
        current_user_role = "conducteur"
        event_bus = MagicMock()
        controller = MagicMock()
        db = MagicMock()

        controller.validate_pointage.return_value = {
            "id": pointage_id,
            "utilisateur_id": 7,
            "chantier_id": 1,
            "date_pointage": date(2026, 1, 20),
            "heures_normales": "08:00",
            "heures_supplementaires": "00:00",
            "statut": "valide",
        }

        async def mock_publish(event):
            pass

        event_bus.publish = mock_publish

        # Act
        import asyncio

        result = asyncio.run(
            validate_pointage(
                pointage_id=pointage_id,
                validateur_id=validateur_id,
                current_user_role=current_user_role,
                event_bus=event_bus,
                controller=controller,
                db=db,
            )
        )

        # Assert
        controller.validate_pointage.assert_called_once()
        assert result["statut"] == "valide"

    def test_validate_pointage_admin_success(self):
        """Un admin peut valider des pointages."""
        # Arrange
        pointage_id = 1
        validateur_id = 1
        current_user_role = "admin"
        event_bus = MagicMock()
        controller = MagicMock()
        db = MagicMock()

        controller.validate_pointage.return_value = {
            "id": pointage_id,
            "utilisateur_id": 7,
            "chantier_id": 1,
            "date_pointage": date(2026, 1, 20),
            "heures_normales": "08:00",
            "heures_supplementaires": "00:00",
            "statut": "valide",
        }

        async def mock_publish(event):
            pass

        event_bus.publish = mock_publish

        # Act
        import asyncio

        result = asyncio.run(
            validate_pointage(
                pointage_id=pointage_id,
                validateur_id=validateur_id,
                current_user_role=current_user_role,
                event_bus=event_bus,
                controller=controller,
                db=db,
            )
        )

        # Assert
        controller.validate_pointage.assert_called_once()
        assert result["statut"] == "valide"


class TestRejectPointagePermissions:
    """Tests pour les permissions de rejet de pointages (SEC-PTG-003)."""

    def test_reject_pointage_compagnon_forbidden(self):
        """Un compagnon ne peut pas rejeter de pointages."""
        # Arrange
        pointage_id = 1
        validateur_id = 7
        current_user_role = "compagnon"
        controller = MagicMock()

        from modules.pointages.infrastructure.web.routes import (
            RejectPointageRequest,
        )

        request = RejectPointageRequest(motif="Heures incorrectes")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            reject_pointage(
                pointage_id=pointage_id,
                request=request,
                validateur_id=validateur_id,
                current_user_role=current_user_role,
                controller=controller,
            )

        assert exc_info.value.status_code == 403
        assert (
            "permission de rejeter des pointages"
            in exc_info.value.detail.lower()
        )
        controller.reject_pointage.assert_not_called()

    def test_reject_pointage_chef_success(self):
        """Un chef de chantier peut rejeter des pointages."""
        # Arrange
        pointage_id = 1
        validateur_id = 4
        current_user_role = "chef_chantier"
        controller = MagicMock()
        db = MagicMock()

        from modules.pointages.infrastructure.web.routes import (
            RejectPointageRequest,
        )

        request = RejectPointageRequest(motif="Heures incorrectes")

        controller.reject_pointage.return_value = {
            "id": pointage_id,
            "statut": "rejete",
            "motif_rejet": "Heures incorrectes",
        }

        # Mock _get_chef_chantier_ids (uses fetchall(), not scalars().all())
        db.execute.return_value.fetchall.return_value = [(1,)]

        # Mock controller.get_pointage (called first to get chantier_id)
        controller.get_pointage.return_value = {"id": pointage_id, "chantier_id": 1}

        # Act
        result = reject_pointage(
            pointage_id=pointage_id,
            request=request,
            validateur_id=validateur_id,
            current_user_role=current_user_role,
            controller=controller,
            db=db,
        )

        # Assert
        controller.reject_pointage.assert_called_once_with(
            pointage_id, validateur_id, "Heures incorrectes"
        )
        assert result["statut"] == "rejete"

    def test_reject_pointage_conducteur_success(self):
        """Un conducteur de travaux peut rejeter des pointages."""
        # Arrange
        pointage_id = 1
        validateur_id = 3
        current_user_role = "conducteur"
        controller = MagicMock()

        from modules.pointages.infrastructure.web.routes import (
            RejectPointageRequest,
        )

        request = RejectPointageRequest(motif="Heures incorrectes")

        controller.reject_pointage.return_value = {
            "id": pointage_id,
            "statut": "rejete",
            "motif_rejet": "Heures incorrectes",
        }

        # Act
        result = reject_pointage(
            pointage_id=pointage_id,
            request=request,
            validateur_id=validateur_id,
            current_user_role=current_user_role,
            controller=controller,
        )

        # Assert
        controller.reject_pointage.assert_called_once()
        assert result["statut"] == "rejete"


class TestExportFeuilleHeuresPermissions:
    """Tests pour les permissions d'export (SEC-PTG-004)."""

    def test_export_compagnon_forbidden(self):
        """Un compagnon ne peut pas exporter."""
        # Arrange
        current_user_id = 7
        current_user_role = "compagnon"
        controller = MagicMock()

        from modules.pointages.infrastructure.web.routes import ExportRequest

        request = ExportRequest(
            format_export="csv",
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            export_feuilles_heures(
                request=request,
                current_user_id=current_user_id,
                current_user_role=current_user_role,
                controller=controller,
            )

        assert exc_info.value.status_code == 403
        assert (
            "permission d'exporter les feuilles d'heures"
            in exc_info.value.detail.lower()
        )
        controller.export_feuilles_heures.assert_not_called()

    def test_export_chef_forbidden(self):
        """Un chef de chantier ne peut pas exporter (restriction métier)."""
        # Arrange
        current_user_id = 4
        current_user_role = "chef_chantier"
        controller = MagicMock()

        from modules.pointages.infrastructure.web.routes import ExportRequest

        request = ExportRequest(
            format_export="csv",
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            export_feuilles_heures(
                request=request,
                current_user_id=current_user_id,
                current_user_role=current_user_role,
                controller=controller,
            )

        assert exc_info.value.status_code == 403
        assert "permission d'exporter" in exc_info.value.detail.lower()
        controller.export_feuilles_heures.assert_not_called()

    def test_export_conducteur_success(self):
        """Un conducteur de travaux peut exporter."""
        # Arrange
        current_user_id = 3
        current_user_role = "conducteur"
        controller = MagicMock()

        from modules.pointages.infrastructure.web.routes import ExportRequest

        request = ExportRequest(
            format_export="csv",
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        controller.export_feuilles_heures.return_value = {
            "success": True,
            "filename": "export.csv",
            "file_content": b"data",
        }

        # Act
        from fastapi import Response

        result = export_feuilles_heures(
            request=request,
            current_user_id=current_user_id,
            current_user_role=current_user_role,
            controller=controller,
        )

        # Assert
        controller.export_feuilles_heures.assert_called_once()
        # Le résultat doit être une Response avec le contenu du fichier
        assert isinstance(result, Response)

    def test_export_admin_success(self):
        """Un admin peut exporter."""
        # Arrange
        current_user_id = 1
        current_user_role = "admin"
        controller = MagicMock()

        from modules.pointages.infrastructure.web.routes import ExportRequest

        request = ExportRequest(
            format_export="csv",
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        controller.export_feuilles_heures.return_value = {
            "success": True,
            "filename": "export.csv",
            "file_content": b"data",
        }

        # Act
        from fastapi import Response

        result = export_feuilles_heures(
            request=request,
            current_user_id=current_user_id,
            current_user_role=current_user_role,
            controller=controller,
        )

        # Assert
        controller.export_feuilles_heures.assert_called_once()
        assert isinstance(result, Response)
