"""Tests unitaires pour RappelReservationJob."""

import pytest
from datetime import date, timedelta, time as dt_time
from unittest.mock import Mock, patch, MagicMock

from shared.infrastructure.scheduler.jobs.rappel_reservation_job import (
    RappelReservationJob,
)


class TestRappelReservationJob:
    """Tests pour le job de rappel réservation."""

    def setup_method(self):
        self.mock_session_factory = Mock()
        self.mock_session = Mock()
        self.mock_session_factory.return_value = self.mock_session

    @patch("shared.infrastructure.scheduler.jobs.rappel_reservation_job.get_notification_service")
    def test_init(self, mock_get_notif):
        """Initialisation du job."""
        mock_get_notif.return_value = Mock()
        job = RappelReservationJob(self.mock_session_factory)
        assert job._db_session_factory is self.mock_session_factory

    @patch("shared.infrastructure.scheduler.jobs.rappel_reservation_job.get_notification_service")
    def test_execute_no_reservations(self, mock_get_notif):
        """Exécution sans réservations retourne stats vides."""
        mock_get_notif.return_value = Mock()
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []

        job = RappelReservationJob(self.mock_session_factory)
        stats = job.execute()

        assert stats["reservations_trouvees"] == 0
        assert stats["notifications_envoyees"] == 0
        assert stats["erreurs"] == 0
        self.mock_session.close.assert_called_once()

    @patch("shared.infrastructure.scheduler.jobs.rappel_reservation_job.get_notification_service")
    def test_execute_with_reservations(self, mock_get_notif):
        """Exécution avec réservations envoie des notifications."""
        mock_notif = Mock()
        mock_notif.send_to_token.return_value = True
        mock_get_notif.return_value = mock_notif

        # Créer une réservation mock
        mock_reservation = Mock()
        mock_reservation.id = 1
        mock_reservation.demandeur_id = 10
        mock_reservation.ressource_id = 5
        mock_reservation.date_reservation = date.today() + timedelta(days=1)
        mock_reservation.heure_debut = dt_time(8, 0)
        mock_reservation.heure_fin = dt_time(12, 0)
        mock_reservation.ressource = Mock()
        mock_reservation.ressource.nom = "Grue"

        # Mock user for _send_rappel
        mock_user = Mock()
        mock_user.id = 10
        mock_user.push_token = None

        # Single unified query mock that handles both reservation and user queries
        mock_query = Mock()
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_reservation]
        mock_query.first.return_value = mock_user
        self.mock_session.query.return_value = mock_query

        job = RappelReservationJob(self.mock_session_factory)
        stats = job.execute()

        assert stats["reservations_trouvees"] == 1
        assert stats["notifications_envoyees"] == 1

    @patch("shared.infrastructure.scheduler.jobs.rappel_reservation_job.get_notification_service")
    def test_execute_db_error(self, mock_get_notif):
        """Exécution avec erreur DB loggée."""
        mock_get_notif.return_value = Mock()
        self.mock_session_factory.side_effect = Exception("DB down")

        job = RappelReservationJob(self.mock_session_factory)
        stats = job.execute()

        assert stats["erreurs"] > 0

    @patch("shared.infrastructure.scheduler.jobs.rappel_reservation_job.get_notification_service")
    def test_send_rappel_user_not_found(self, mock_get_notif):
        """_send_rappel retourne False si utilisateur non trouvé."""
        mock_get_notif.return_value = Mock()

        mock_reservation = Mock()
        mock_reservation.demandeur_id = 99

        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        job = RappelReservationJob(self.mock_session_factory)
        result = job._send_rappel(mock_reservation, self.mock_session)

        assert result is False

    @patch("shared.infrastructure.scheduler.jobs.rappel_reservation_job.get_notification_service")
    def test_send_rappel_simulated(self, mock_get_notif):
        """_send_rappel en mode simulé (pas de push_token)."""
        mock_get_notif.return_value = Mock()

        mock_reservation = Mock()
        mock_reservation.id = 1
        mock_reservation.demandeur_id = 10
        mock_reservation.ressource_id = 5
        mock_reservation.date_reservation = date.today()
        mock_reservation.heure_debut = dt_time(8, 0)
        mock_reservation.heure_fin = dt_time(12, 0)
        mock_reservation.ressource = Mock()
        mock_reservation.ressource.nom = "Grue"

        mock_user = Mock()
        mock_user.id = 10
        mock_user.push_token = None  # Pas de token

        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user

        job = RappelReservationJob(self.mock_session_factory)
        result = job._send_rappel(mock_reservation, self.mock_session)

        assert result is True

    @patch("shared.infrastructure.scheduler.jobs.rappel_reservation_job.get_notification_service")
    def test_register(self, mock_get_notif):
        """register() enregistre le job dans le scheduler."""
        mock_get_notif.return_value = Mock()
        mock_scheduler = Mock()

        RappelReservationJob.register(mock_scheduler, self.mock_session_factory)

        mock_scheduler.add_cron_job.assert_called_once()
        call_kwargs = mock_scheduler.add_cron_job.call_args.kwargs
        assert call_kwargs["job_id"] == "rappel_reservation_j1"
        assert call_kwargs["hour"] == 18

    def test_job_constants(self):
        """Constantes du job."""
        assert RappelReservationJob.JOB_ID == "rappel_reservation_j1"
        assert RappelReservationJob.DEFAULT_HOUR == 18
        assert RappelReservationJob.DEFAULT_MINUTE == 0
