"""Tests unitaires pour UpdateConsentsUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.auth.application.use_cases.update_consents import UpdateConsentsUseCase


class TestUpdateConsentsUseCase:
    """Tests pour le use case de mise à jour des consentements RGPD."""

    def setup_method(self):
        self.mock_user_repo = Mock()
        self.use_case = UpdateConsentsUseCase(self.mock_user_repo)

    def test_update_all_consents(self):
        """Met à jour tous les consentements."""
        mock_user = Mock()
        mock_user.consent_geolocation = False
        mock_user.consent_notifications = False
        mock_user.consent_analytics = False
        mock_user.consent_timestamp = None
        mock_user.consent_ip_address = None
        mock_user.consent_user_agent = None
        self.mock_user_repo.find_by_id.return_value = mock_user

        result = self.use_case.execute(
            user_id=1,
            geolocation=True,
            notifications=True,
            analytics=False,
            ip_address="1.2.3.4",
            user_agent="Mozilla/5.0",
        )

        assert mock_user.consent_geolocation is True
        assert mock_user.consent_notifications is True
        assert mock_user.consent_analytics is False
        assert mock_user.consent_ip_address == "1.2.3.4"
        self.mock_user_repo.save.assert_called_once_with(mock_user)

    def test_partial_update(self):
        """Met à jour seulement certains consentements."""
        mock_user = Mock()
        mock_user.consent_geolocation = True
        mock_user.consent_notifications = False
        mock_user.consent_analytics = False
        mock_user.consent_timestamp = datetime(2026, 1, 1)
        mock_user.consent_ip_address = None
        mock_user.consent_user_agent = None
        self.mock_user_repo.find_by_id.return_value = mock_user

        self.use_case.execute(user_id=1, notifications=True)

        assert mock_user.consent_notifications is True
        # geolocation n'est pas modifié (None passé)

    def test_user_not_found_raises(self):
        """Lève ValueError si utilisateur non trouvé."""
        self.mock_user_repo.find_by_id.return_value = None

        with pytest.raises(ValueError, match="non trouvé"):
            self.use_case.execute(user_id=99)

    def test_returns_consent_dict(self):
        """Retourne un dictionnaire avec les consentements."""
        mock_user = Mock()
        mock_user.consent_geolocation = True
        mock_user.consent_notifications = False
        mock_user.consent_analytics = True
        mock_user.consent_timestamp = datetime(2026, 1, 15, 10, 30)
        mock_user.consent_ip_address = "1.2.3.4"
        mock_user.consent_user_agent = "Chrome"
        self.mock_user_repo.find_by_id.return_value = mock_user

        result = self.use_case.execute(user_id=1, geolocation=True)

        assert result["geolocation"] is True
        assert result["notifications"] is False
        assert result["analytics"] is True
        assert "ip_address" in result
        assert "user_agent" in result
        assert "timestamp" in result
