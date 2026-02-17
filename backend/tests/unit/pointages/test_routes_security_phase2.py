"""Tests unitaires pour les corrections de sécurité Phase 2 (GAPs critiques)."""

import pytest
from datetime import date
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from unittest.mock import Mock, MagicMock, patch

from modules.pointages.infrastructure.web.routes import (
    bulk_validate_pointages,
    get_monthly_recap,
    lock_monthly_period,
    BulkValidateRequest,
    LockPeriodRequest,
)


class TestBulkValidateSecurityP2_001:
    """
    Tests pour SEC-PTG-P2-001: Bypass autorisation /bulk-validate.

    Vérifie que seuls les chefs de chantier, conducteurs et admins
    peuvent utiliser la validation en masse.
    """

    def test_bulk_validate_compagnon_forbidden(self):
        """Un compagnon ne peut pas valider en masse."""
        # Arrange
        request = BulkValidateRequest(pointage_ids=[1, 2, 3])
        validateur_id = 7
        current_user_role = "compagnon"
        controller = MagicMock()

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            bulk_validate_pointages(
                request=request,
                validateur_id=validateur_id,
                current_user_role=current_user_role,
                controller=controller,
            )

        assert exc_info.value.status_code == 403
        assert "chefs de chantier, conducteurs et admins" in exc_info.value.detail
        controller.bulk_validate_pointages.assert_not_called()

    def test_bulk_validate_chef_success(self):
        """Un chef de chantier peut valider en masse."""
        # Arrange
        request = BulkValidateRequest(pointage_ids=[1, 2, 3])
        validateur_id = 4
        current_user_role = "chef_chantier"
        controller = MagicMock()
        db = MagicMock()
        # _get_chef_chantier_ids uses fetchall(), not scalars().all()
        db.execute.return_value.fetchall.return_value = [(1,), (2,), (3,)]

        # controller.get_pointage is called for each pointage_id to check chantier
        controller.get_pointage.return_value = {"chantier_id": 1}

        controller.bulk_validate_pointages.return_value = {
            "success_count": 3,
            "error_count": 0,
            "results": [
                {"pointage_id": 1, "success": True},
                {"pointage_id": 2, "success": True},
                {"pointage_id": 3, "success": True},
            ],
        }

        # Act
        result = bulk_validate_pointages(
            request=request,
            validateur_id=validateur_id,
            current_user_role=current_user_role,
            controller=controller,
            db=db,
        )

        # Assert
        controller.bulk_validate_pointages.assert_called_once_with([1, 2, 3], validateur_id)
        assert result["success_count"] == 3

    def test_bulk_validate_conducteur_success(self):
        """Un conducteur de travaux peut valider en masse."""
        # Arrange
        request = BulkValidateRequest(pointage_ids=[1, 2])
        validateur_id = 3
        current_user_role = "conducteur"
        controller = MagicMock()
        db = MagicMock()

        controller.bulk_validate_pointages.return_value = {
            "success_count": 2,
            "error_count": 0,
            "results": [],
        }

        # Act
        result = bulk_validate_pointages(
            request=request,
            validateur_id=validateur_id,
            current_user_role=current_user_role,
            controller=controller,
            db=db,
        )

        # Assert
        controller.bulk_validate_pointages.assert_called_once()
        assert result["success_count"] == 2

    def test_bulk_validate_admin_success(self):
        """Un admin peut valider en masse."""
        # Arrange
        request = BulkValidateRequest(pointage_ids=[1])
        validateur_id = 1
        current_user_role = "admin"
        controller = MagicMock()
        db = MagicMock()

        controller.bulk_validate_pointages.return_value = {
            "success_count": 1,
            "error_count": 0,
            "results": [],
        }

        # Act
        result = bulk_validate_pointages(
            request=request,
            validateur_id=validateur_id,
            current_user_role=current_user_role,
            controller=controller,
            db=db,
        )

        # Assert
        controller.bulk_validate_pointages.assert_called_once()
        assert result["success_count"] == 1


class TestMonthlyRecapSecurityP2_002:
    """
    Tests pour SEC-PTG-P2-002: Fuite données paie /recap.

    Vérifie qu'un compagnon ne peut consulter que son propre récapitulatif mensuel.
    """

    def test_monthly_recap_compagnon_own_data_allowed(self):
        """Un compagnon peut consulter son propre récapitulatif."""
        # Arrange
        utilisateur_id = 7
        current_user_id = 7
        current_user_role = "compagnon"
        controller = MagicMock()

        controller.generate_monthly_recap.return_value = {
            "utilisateur_id": 7,
            "year": 2026,
            "month": 1,
            "total_heures_normales": 151.5,
            "total_heures_supplementaires": 8.0,
        }

        # Act
        result = get_monthly_recap(
            utilisateur_id=utilisateur_id,
            year=2026,
            month=1,
            export_pdf=False,
            current_user_id=current_user_id,
            current_user_role=current_user_role,
            controller=controller,
        )

        # Assert
        controller.generate_monthly_recap.assert_called_once_with(7, 2026, 1, False)
        assert result["utilisateur_id"] == 7

    def test_monthly_recap_compagnon_other_data_forbidden(self):
        """Un compagnon ne peut pas consulter le récapitulatif d'un autre compagnon."""
        # Arrange
        utilisateur_id = 8  # Autre compagnon
        current_user_id = 7  # Compagnon connecté
        current_user_role = "compagnon"
        controller = MagicMock()

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_monthly_recap(
                utilisateur_id=utilisateur_id,
                year=2026,
                month=1,
                export_pdf=False,
                current_user_id=current_user_id,
                current_user_role=current_user_role,
                controller=controller,
            )

        assert exc_info.value.status_code == 403
        assert "votre propre récapitulatif mensuel" in exc_info.value.detail
        controller.generate_monthly_recap.assert_not_called()

    def test_monthly_recap_chef_can_view_all(self):
        """Un chef de chantier peut consulter n'importe quel récapitulatif."""
        # Arrange
        utilisateur_id = 7  # Compagnon
        current_user_id = 4  # Chef
        current_user_role = "chef_chantier"
        controller = MagicMock()

        controller.generate_monthly_recap.return_value = {
            "utilisateur_id": 7,
            "year": 2026,
            "month": 1,
            "total_heures_normales": 151.5,
        }

        # Act
        result = get_monthly_recap(
            utilisateur_id=utilisateur_id,
            year=2026,
            month=1,
            export_pdf=False,
            current_user_id=current_user_id,
            current_user_role=current_user_role,
            controller=controller,
        )

        # Assert
        controller.generate_monthly_recap.assert_called_once()
        assert result["utilisateur_id"] == 7

    def test_monthly_recap_conducteur_can_view_all(self):
        """Un conducteur peut consulter n'importe quel récapitulatif."""
        # Arrange
        utilisateur_id = 7
        current_user_id = 3
        current_user_role = "conducteur"
        controller = MagicMock()

        controller.generate_monthly_recap.return_value = {
            "utilisateur_id": 7,
            "year": 2026,
            "month": 1,
        }

        # Act
        result = get_monthly_recap(
            utilisateur_id=utilisateur_id,
            year=2026,
            month=1,
            export_pdf=False,
            current_user_id=current_user_id,
            current_user_role=current_user_role,
            controller=controller,
        )

        # Assert
        controller.generate_monthly_recap.assert_called_once()

    def test_monthly_recap_admin_can_view_all(self):
        """Un admin peut consulter n'importe quel récapitulatif."""
        # Arrange
        utilisateur_id = 7
        current_user_id = 1
        current_user_role = "admin"
        controller = MagicMock()

        controller.generate_monthly_recap.return_value = {
            "utilisateur_id": 7,
            "year": 2026,
            "month": 1,
        }

        # Act
        result = get_monthly_recap(
            utilisateur_id=utilisateur_id,
            year=2026,
            month=1,
            export_pdf=False,
            current_user_id=current_user_id,
            current_user_role=current_user_role,
            controller=controller,
        )

        # Assert
        controller.generate_monthly_recap.assert_called_once()


class TestLockPeriodSecurityP2_006:
    """
    Tests pour SEC-PTG-P2-006: Verrouillage périodes arbitraires.

    Vérifie que:
    1. On ne peut pas verrouiller une période future
    2. On ne peut pas verrouiller une période > 12 mois
    3. On ne peut pas re-verrouiller une période déjà verrouillée
    """

    @patch("modules.pointages.infrastructure.web.routes.date")
    def test_lock_period_future_forbidden(self, mock_date_class):
        """Interdire le verrouillage de périodes futures."""
        # Arrange: On est en janvier 2026
        mock_today = date(2026, 1, 31)
        mock_date_class.today.return_value = mock_today
        mock_date_class.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        request = LockPeriodRequest(year=2026, month=3)  # Mars 2026 = futur
        current_user_id = 1
        current_user_role = "admin"
        controller = MagicMock()

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            lock_monthly_period(
                request=request,
                current_user_id=current_user_id,
                current_user_role=current_user_role,
                controller=controller,
            )

        assert exc_info.value.status_code == 400
        assert "période future" in exc_info.value.detail
        controller.lock_monthly_period.assert_not_called()

    @patch("modules.pointages.infrastructure.web.routes.date")
    def test_lock_period_too_old_forbidden(self, mock_date_class):
        """Interdire le verrouillage de périodes > 12 mois."""
        # Arrange: On est en janvier 2026
        mock_today = date(2026, 1, 31)
        mock_date_class.today.return_value = mock_today
        mock_date_class.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        # 14 mois en arrière = novembre 2024 (> 12 mois)
        request = LockPeriodRequest(year=2024, month=11)
        current_user_id = 1
        current_user_role = "admin"
        controller = MagicMock()

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            lock_monthly_period(
                request=request,
                current_user_id=current_user_id,
                current_user_role=current_user_role,
                controller=controller,
            )

        assert exc_info.value.status_code == 400
        assert "plus de 12 mois" in exc_info.value.detail
        controller.lock_monthly_period.assert_not_called()

    @patch("modules.pointages.infrastructure.web.routes.PeriodePaie")
    @patch("modules.pointages.infrastructure.web.routes.date")
    def test_lock_period_already_locked_forbidden(self, mock_date_class, mock_periode_paie):
        """Interdire le re-verrouillage d'une période déjà verrouillée."""
        # Arrange: On est en février 2026
        mock_today = date(2026, 2, 15)
        mock_date_class.today.return_value = mock_today
        mock_date_class.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        # La période de décembre 2025 est déjà verrouillée
        mock_periode_paie.is_locked.return_value = True

        request = LockPeriodRequest(year=2025, month=12)
        current_user_id = 1
        current_user_role = "admin"
        controller = MagicMock()

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            lock_monthly_period(
                request=request,
                current_user_id=current_user_id,
                current_user_role=current_user_role,
                controller=controller,
            )

        assert exc_info.value.status_code == 409
        assert "déjà verrouillée" in exc_info.value.detail
        controller.lock_monthly_period.assert_not_called()

    @patch("modules.pointages.infrastructure.web.routes.PeriodePaie")
    @patch("modules.pointages.infrastructure.web.routes.date")
    def test_lock_period_valid_success(self, mock_date_class, mock_periode_paie):
        """Verrouillage valide d'une période récente non verrouillée."""
        # Arrange: On est en février 2026
        mock_today = date(2026, 2, 15)
        mock_date_class.today.return_value = mock_today
        mock_date_class.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        # La période de janvier 2026 n'est pas encore verrouillée
        mock_periode_paie.is_locked.return_value = False

        request = LockPeriodRequest(year=2026, month=1)
        current_user_id = 1
        current_user_role = "admin"
        controller = MagicMock()

        controller.lock_monthly_period.return_value = {
            "year": 2026,
            "month": 1,
            "locked": True,
            "locked_at": "2026-02-15T10:30:00",
            "locked_by": 1,
        }

        # Act
        result = lock_monthly_period(
            request=request,
            current_user_id=current_user_id,
            current_user_role=current_user_role,
            controller=controller,
        )

        # Assert
        controller.lock_monthly_period.assert_called_once_with(2026, 1, locked_by=1)
        assert result["locked"] is True

    @patch("modules.pointages.infrastructure.web.routes.PeriodePaie")
    @patch("modules.pointages.infrastructure.web.routes.date")
    def test_lock_period_current_month_allowed(self, mock_date_class, mock_periode_paie):
        """On peut verrouiller le mois en cours (cas de clôture anticipée)."""
        # Arrange: On est en janvier 2026
        mock_today = date(2026, 1, 25)
        mock_date_class.today.return_value = mock_today
        mock_date_class.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        # Le mois en cours n'est pas verrouillé
        mock_periode_paie.is_locked.return_value = False

        request = LockPeriodRequest(year=2026, month=1)
        current_user_id = 1
        current_user_role = "admin"
        controller = MagicMock()

        controller.lock_monthly_period.return_value = {
            "year": 2026,
            "month": 1,
            "locked": True,
        }

        # Act
        result = lock_monthly_period(
            request=request,
            current_user_id=current_user_id,
            current_user_role=current_user_role,
            controller=controller,
        )

        # Assert
        controller.lock_monthly_period.assert_called_once()
        assert result["locked"] is True

    def test_lock_period_non_admin_forbidden(self):
        """Seuls admin et conducteur peuvent verrouiller."""
        # Arrange
        request = LockPeriodRequest(year=2026, month=1)
        current_user_id = 4
        current_user_role = "chef_chantier"
        controller = MagicMock()

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            lock_monthly_period(
                request=request,
                current_user_id=current_user_id,
                current_user_role=current_user_role,
                controller=controller,
            )

        assert exc_info.value.status_code == 403
        assert "administrateurs et conducteurs" in exc_info.value.detail

    @patch("modules.pointages.infrastructure.web.routes.PeriodePaie")
    @patch("modules.pointages.infrastructure.web.routes.date")
    def test_lock_period_exactly_12_months_allowed(self, mock_date_class, mock_periode_paie):
        """Une période de exactement 12 mois en arrière est autorisée."""
        # Arrange: On est en janvier 2026
        mock_today = date(2026, 1, 31)
        mock_date_class.today.return_value = mock_today
        mock_date_class.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        # Janvier 2025 = exactement 12 mois avant
        mock_periode_paie.is_locked.return_value = False

        request = LockPeriodRequest(year=2025, month=1)
        current_user_id = 1
        current_user_role = "conducteur"
        controller = MagicMock()

        controller.lock_monthly_period.return_value = {
            "year": 2025,
            "month": 1,
            "locked": True,
        }

        # Act
        result = lock_monthly_period(
            request=request,
            current_user_id=current_user_id,
            current_user_role=current_user_role,
            controller=controller,
        )

        # Assert
        controller.lock_monthly_period.assert_called_once()
        assert result["locked"] is True
