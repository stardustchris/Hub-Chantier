"""Tests pour le scheduler de nettoyage des webhook deliveries (GDPR)."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from shared.infrastructure.webhooks.cleanup_scheduler import (
    cleanup_old_deliveries_job,
    start_cleanup_scheduler,
    stop_cleanup_scheduler,
    run_cleanup_now,
    RETENTION_DAYS,
)
from shared.infrastructure.webhooks.models import WebhookDeliveryModel


class TestCleanupScheduler:
    """Tests pour le scheduler de nettoyage GDPR."""

    def test_cleanup_job_deletes_old_deliveries(self, db_session: Session):
        """Doit supprimer les deliveries plus anciennes que RETENTION_DAYS jours."""
        # Arrange: Créer des deliveries anciennes (> 90 jours)
        old_date = datetime.utcnow() - timedelta(days=RETENTION_DAYS + 10)
        recent_date = datetime.utcnow() - timedelta(days=10)

        old_delivery = WebhookDeliveryModel(
            webhook_id="550e8400-e29b-41d4-a716-446655440000",
            event_type="test.old",
            attempt_number=1,
            success=True,
            delivered_at=old_date,
        )
        recent_delivery = WebhookDeliveryModel(
            webhook_id="550e8400-e29b-41d4-a716-446655440000",
            event_type="test.recent",
            attempt_number=1,
            success=True,
            delivered_at=recent_date,
        )

        db_session.add_all([old_delivery, recent_delivery])
        db_session.commit()

        initial_count = db_session.query(WebhookDeliveryModel).count()
        assert initial_count == 2

        # Act: Exécuter le job de nettoyage
        with patch('shared.infrastructure.webhooks.cleanup_scheduler.SessionLocal') as mock_session:
            mock_session.return_value = db_session
            cleanup_old_deliveries_job()

        # Assert: Seule l'ancienne delivery doit être supprimée
        remaining_count = db_session.query(WebhookDeliveryModel).count()
        assert remaining_count == 1

        remaining_delivery = db_session.query(WebhookDeliveryModel).first()
        assert remaining_delivery.event_type == "test.recent"
        assert remaining_delivery.delivered_at == recent_date

    def test_cleanup_job_preserves_recent_deliveries(self, db_session: Session):
        """Doit conserver toutes les deliveries récentes (< RETENTION_DAYS)."""
        # Arrange: Créer uniquement des deliveries récentes
        recent_dates = [
            datetime.utcnow() - timedelta(days=1),
            datetime.utcnow() - timedelta(days=30),
            datetime.utcnow() - timedelta(days=60),
            datetime.utcnow() - timedelta(days=RETENTION_DAYS - 1),
        ]

        for i, date in enumerate(recent_dates):
            delivery = WebhookDeliveryModel(
                webhook_id="550e8400-e29b-41d4-a716-446655440000",
                event_type=f"test.recent_{i}",
                attempt_number=1,
                success=True,
                delivered_at=date,
            )
            db_session.add(delivery)

        db_session.commit()

        initial_count = db_session.query(WebhookDeliveryModel).count()
        assert initial_count == 4

        # Act: Exécuter le nettoyage
        with patch('shared.infrastructure.webhooks.cleanup_scheduler.SessionLocal') as mock_session:
            mock_session.return_value = db_session
            cleanup_old_deliveries_job()

        # Assert: Toutes les deliveries doivent être conservées
        remaining_count = db_session.query(WebhookDeliveryModel).count()
        assert remaining_count == 4

    def test_cleanup_job_handles_empty_database(self, db_session: Session):
        """Doit gérer le cas où la base est vide sans erreur."""
        # Arrange: Base vide
        initial_count = db_session.query(WebhookDeliveryModel).count()
        assert initial_count == 0

        # Act: Exécuter le nettoyage
        with patch('shared.infrastructure.webhooks.cleanup_scheduler.SessionLocal') as mock_session:
            mock_session.return_value = db_session
            # Ne doit pas lever d'exception
            cleanup_old_deliveries_job()

        # Assert: Toujours vide, pas d'erreur
        final_count = db_session.query(WebhookDeliveryModel).count()
        assert final_count == 0

    def test_cleanup_job_rollback_on_error(self, db_session: Session):
        """Doit rollback la transaction en cas d'erreur."""
        # Arrange: Mock SessionLocal pour simuler une erreur
        mock_session_local = Mock()
        mock_db = Mock(spec=Session)

        # Simuler une erreur lors du delete
        mock_query = Mock()
        mock_query.filter.return_value.delete.side_effect = Exception("Database error")
        mock_db.query.return_value = mock_query

        mock_session_local.return_value = mock_db

        # Act: Exécuter le nettoyage (doit gérer l'erreur)
        with patch('shared.infrastructure.webhooks.cleanup_scheduler.SessionLocal', mock_session_local):
            # Ne doit pas lever d'exception (erreur loggée)
            cleanup_old_deliveries_job()

        # Assert: Rollback doit avoir été appelé
        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()

    def test_scheduler_starts_and_configures_job(self):
        """Doit démarrer le scheduler avec la configuration correcte."""
        # Arrange: Arrêter le scheduler global s'il existe
        stop_cleanup_scheduler()

        # Act: Démarrer le scheduler
        scheduler = start_cleanup_scheduler()

        # Assert: Scheduler doit être démarré
        assert scheduler is not None
        assert scheduler.running is True

        # Vérifier que le job est enregistré
        jobs = scheduler.get_jobs()
        assert len(jobs) >= 1

        cleanup_job = next(
            (job for job in jobs if job.id == 'webhook_deliveries_cleanup'),
            None
        )
        assert cleanup_job is not None
        assert cleanup_job.name == 'Cleanup Webhook Deliveries (GDPR)'
        assert cleanup_job.max_instances == 1  # Pas de parallélisme

        # Cleanup: Arrêter le scheduler
        stop_cleanup_scheduler()

    def test_scheduler_prevents_duplicate_jobs(self):
        """Doit empêcher le démarrage de plusieurs instances du scheduler."""
        # Arrange: Arrêter le scheduler global
        stop_cleanup_scheduler()

        # Act: Démarrer le scheduler deux fois
        scheduler1 = start_cleanup_scheduler()
        scheduler2 = start_cleanup_scheduler()  # 2ème appel

        # Assert: Doit retourner la même instance
        assert scheduler1 is scheduler2

        # Vérifier qu'il n'y a qu'un seul job
        jobs = scheduler1.get_jobs()
        cleanup_jobs = [j for j in jobs if j.id == 'webhook_deliveries_cleanup']
        assert len(cleanup_jobs) == 1

        # Cleanup
        stop_cleanup_scheduler()

    def test_manual_cleanup_execution(self, db_session: Session):
        """Doit permettre l'exécution manuelle du nettoyage."""
        # Arrange: Créer une delivery ancienne
        old_date = datetime.utcnow() - timedelta(days=RETENTION_DAYS + 5)
        old_delivery = WebhookDeliveryModel(
            webhook_id="550e8400-e29b-41d4-a716-446655440000",
            event_type="test.manual",
            attempt_number=1,
            success=True,
            delivered_at=old_date,
        )
        db_session.add(old_delivery)
        db_session.commit()

        assert db_session.query(WebhookDeliveryModel).count() == 1

        # Act: Exécuter manuellement
        with patch('shared.infrastructure.webhooks.cleanup_scheduler.SessionLocal') as mock_session:
            mock_session.return_value = db_session
            run_cleanup_now()

        # Assert: Delivery supprimée
        assert db_session.query(WebhookDeliveryModel).count() == 0

    def test_scheduler_stop_gracefully(self):
        """Doit arrêter le scheduler proprement."""
        # Arrange: Démarrer le scheduler
        stop_cleanup_scheduler()  # Reset
        scheduler = start_cleanup_scheduler()
        assert scheduler.running is True

        # Act: Arrêter le scheduler
        stop_cleanup_scheduler()

        # Assert: Scheduler doit être arrêté
        assert scheduler.running is False

        # Vérifier qu'on peut le redémarrer après
        new_scheduler = start_cleanup_scheduler()
        assert new_scheduler.running is True

        # Cleanup
        stop_cleanup_scheduler()


@pytest.fixture
def db_session():
    """Fixture pour créer une session de base de données de test."""
    from shared.infrastructure.database import SessionLocal, Base, engine

    # Créer les tables
    Base.metadata.create_all(bind=engine)

    # Créer une session
    session = SessionLocal()

    yield session

    # Cleanup: Supprimer toutes les deliveries de test
    session.query(WebhookDeliveryModel).delete()
    session.commit()
    session.close()
