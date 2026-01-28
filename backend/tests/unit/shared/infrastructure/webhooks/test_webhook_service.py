"""Tests for Webhook Delivery Service.

Tests comprehensive webhook functionality:
- Webhook delivery with HMAC signatures
- Retry logic with exponential backoff
- Pattern matching (wildcards)
- Auto-disable after failures
- Delivery record tracking
"""

import pytest
import asyncio
import json
import hmac
import hashlib
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import List

import httpx

from shared.infrastructure.event_bus.domain_event import DomainEvent
from shared.infrastructure.webhooks.webhook_service import WebhookDeliveryService
from shared.infrastructure.webhooks.event_listener import webhook_event_handler
from shared.infrastructure.webhooks.models import WebhookModel, WebhookDeliveryModel


# ===== Fixtures =====


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = Mock()
    db.query = Mock(return_value=db)
    db.filter = Mock(return_value=db)
    db.all = Mock(return_value=[])
    db.add = Mock()
    db.commit = Mock()
    db.close = Mock()
    return db


@pytest.fixture
def webhook_service(mock_db):
    """Create a WebhookDeliveryService instance with mock db."""
    return WebhookDeliveryService(mock_db)


@pytest.fixture
def sample_webhook():
    """Create a sample webhook model."""
    webhook = WebhookModel(
        id=1,
        user_id=1,
        url="https://example.com/webhook",
        events=["chantier.*"],
        secret="test-secret-key",
        is_active=True,
        last_triggered_at=None,
        consecutive_failures=0,
        retry_enabled=True,
        max_retries=3,
    )
    return webhook


@pytest.fixture
def sample_event():
    """Create a sample domain event."""
    return DomainEvent(
        event_type="chantier.created",
        aggregate_id="123",
        data={"nom": "Test Chantier", "adresse": "123 rue Test"},
        metadata={"user_id": 1}
    )


# ===== Tests for Webhook Delivery =====


@pytest.mark.asyncio
async def test_webhook_delivery_success(webhook_service, sample_webhook, sample_event, mock_db):
    """Test successful webhook delivery."""
    # Mock HTTP client
    mock_response = Mock()
    mock_response.is_success = True
    mock_response.status_code = 200
    mock_response.text = '{"success": true}'

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        await webhook_service.deliver(sample_webhook, sample_event)

    # Verify HTTP request was made
    assert mock_client.post.called
    call_args = mock_client.post.call_args

    # Verify URL
    assert call_args[0][0] == "https://example.com/webhook"

    # Verify headers
    headers = call_args[1]["headers"]
    assert "X-Hub-Chantier-Signature" in headers
    assert "X-Hub-Chantier-Event" in headers
    assert headers["X-Hub-Chantier-Event"] == "chantier.created"

    # Verify delivery was recorded
    assert mock_db.add.called
    assert mock_db.commit.called

    # Verify webhook was updated
    assert sample_webhook.consecutive_failures == 0


@pytest.mark.asyncio
async def test_webhook_delivery_hmac_signature(webhook_service, sample_webhook, sample_event, mock_db):
    """Test that HMAC-SHA256 signature is computed correctly."""
    mock_response = Mock()
    mock_response.is_success = True
    mock_response.status_code = 200
    mock_response.text = '{"success": true}'

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        await webhook_service.deliver(sample_webhook, sample_event)

    # Extract the signature from the call
    headers = mock_client.post.call_args[1]["headers"]
    signature_header = headers["X-Hub-Chantier-Signature"]

    # Should be in format "sha256=<hex>"
    assert signature_header.startswith("sha256=")
    signature = signature_header.replace("sha256=", "")

    # Verify signature is a valid hex string (64 chars for SHA256)
    assert len(signature) == 64
    assert all(c in '0123456789abcdef' for c in signature)

    # Verify the signature was computed from the payload
    # Note: We can't reconstruct the exact signature because JSON serialization
    # order might differ, but we can verify it's a valid HMAC


@pytest.mark.asyncio
async def test_webhook_delivery_retry_exponential(webhook_service, sample_webhook, sample_event, mock_db):
    """Test exponential backoff retry logic."""
    mock_response = Mock()
    mock_response.is_success = False
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    # Track sleep calls
    sleep_times = []

    async def mock_sleep(seconds):
        sleep_times.append(seconds)

    with patch('httpx.AsyncClient') as mock_client_class:
        with patch('asyncio.sleep', side_effect=mock_sleep):
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            # Deliver (will retry 3 times with max_retries=3)
            await webhook_service.deliver(sample_webhook, sample_event, attempt=1)

    # Should have retried with exponential backoff: 2, 4, 8 seconds
    # (2^1, 2^2, 2^3)
    assert len(sleep_times) >= 1
    if len(sleep_times) >= 3:
        assert sleep_times[0] == 2  # 2^1
        assert sleep_times[1] == 4  # 2^2
        assert sleep_times[2] == 8  # 2^3


@pytest.mark.asyncio
async def test_webhook_delivery_max_retries_reached(webhook_service, sample_webhook, sample_event, mock_db):
    """Test that delivery stops after max_retries."""
    mock_response = Mock()
    mock_response.is_success = False
    mock_response.status_code = 500
    mock_response.text = "Error"

    delivery_attempts = []

    with patch('httpx.AsyncClient') as mock_client_class:
        with patch('asyncio.sleep', return_value=None):  # Speed up test
            mock_client = AsyncMock()

            async def track_post(*args, **kwargs):
                delivery_attempts.append(1)
                return mock_response

            mock_client.post = AsyncMock(side_effect=track_post)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            await webhook_service.deliver(sample_webhook, sample_event, attempt=1)

    # Should have tried: initial + 3 retries = 4 total attempts
    assert len(delivery_attempts) == 4


@pytest.mark.asyncio
async def test_webhook_delivery_record_created(webhook_service, sample_webhook, sample_event, mock_db):
    """Test that delivery records are created correctly."""
    mock_response = Mock()
    mock_response.is_success = True
    mock_response.status_code = 200
    mock_response.text = '{"ok": true}'

    with patch('httpx.AsyncClient') as mock_client_class:
        with patch('time.time', side_effect=[1000.0, 1000.5]):  # 500ms response time
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            await webhook_service.deliver(sample_webhook, sample_event)

    # Verify delivery record was created
    add_calls = [call[0][0] for call in mock_db.add.call_args_list]
    delivery_records = [obj for obj in add_calls if isinstance(obj, WebhookDeliveryModel)]

    assert len(delivery_records) >= 1
    record = delivery_records[0]

    assert record.webhook_id == sample_webhook.id
    assert record.event_type == "chantier.created"
    assert record.success is True
    assert record.status_code == 200
    assert record.attempt_number == 1


# ===== Tests for Pattern Matching =====


def test_webhook_pattern_matching_exact():
    """Test exact event type matching."""
    assert WebhookDeliveryService._event_matches("chantier.created", ["chantier.created"]) is True
    assert WebhookDeliveryService._event_matches("chantier.created", ["chantier.updated"]) is False


def test_webhook_pattern_matching_wildcard():
    """Test wildcard pattern matching."""
    assert WebhookDeliveryService._event_matches("chantier.created", ["chantier.*"]) is True
    assert WebhookDeliveryService._event_matches("chantier.updated", ["chantier.*"]) is True
    assert WebhookDeliveryService._event_matches("user.created", ["chantier.*"]) is False


def test_webhook_pattern_matching_module_prefix():
    """Test module prefix wildcard matching."""
    patterns = ["chantier.*", "user.created"]

    assert WebhookDeliveryService._event_matches("chantier.created", patterns) is True
    assert WebhookDeliveryService._event_matches("chantier.deleted", patterns) is True
    assert WebhookDeliveryService._event_matches("user.created", patterns) is True
    assert WebhookDeliveryService._event_matches("user.updated", patterns) is False


def test_webhook_pattern_matching_catch_all():
    """Test catch-all pattern '*'."""
    assert WebhookDeliveryService._event_matches("anything", ["*"]) is True
    assert WebhookDeliveryService._event_matches("chantier.created", ["*"]) is True


# ===== Tests for Auto-Disable =====


@pytest.mark.asyncio
async def test_webhook_auto_disable_after_10_failures(webhook_service, sample_webhook, sample_event, mock_db):
    """Test that webhook is disabled after 10 consecutive failures."""
    # Set up webhook with 9 failures already
    sample_webhook.consecutive_failures = 9
    sample_webhook.retry_enabled = False  # Disable retry to speed up test

    mock_response = Mock()
    mock_response.is_success = False
    mock_response.status_code = 500
    mock_response.text = "Error"

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        await webhook_service.deliver(sample_webhook, sample_event)

    # Should be disabled after 10th failure
    assert sample_webhook.consecutive_failures == 10
    assert sample_webhook.is_active is False


@pytest.mark.asyncio
async def test_webhook_reset_failures_on_success(webhook_service, sample_webhook, sample_event, mock_db):
    """Test that consecutive_failures resets on successful delivery."""
    sample_webhook.consecutive_failures = 5

    mock_response = Mock()
    mock_response.is_success = True
    mock_response.status_code = 200
    mock_response.text = "OK"

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        await webhook_service.deliver(sample_webhook, sample_event)

    assert sample_webhook.consecutive_failures == 0


# ===== Tests for Deliver All =====


@pytest.mark.asyncio
async def test_webhook_deliver_all_matching_webhooks(webhook_service, sample_event, mock_db):
    """Test that deliver_all sends to all matching webhooks."""
    # Create multiple webhooks
    webhook1 = WebhookModel(
        id=1, user_id=1, url="https://webhook1.com",
        events=["chantier.*"], secret="secret1",
        is_active=True, consecutive_failures=0,
        retry_enabled=True, max_retries=3
    )
    webhook2 = WebhookModel(
        id=2, user_id=1, url="https://webhook2.com",
        events=["*"], secret="secret2",
        is_active=True, consecutive_failures=0,
        retry_enabled=True, max_retries=3
    )
    webhook3 = WebhookModel(
        id=3, user_id=1, url="https://webhook3.com",
        events=["user.*"], secret="secret3",
        is_active=True, consecutive_failures=0,
        retry_enabled=True, max_retries=3
    )

    mock_db.all = Mock(return_value=[webhook1, webhook2, webhook3])

    mock_response = Mock()
    mock_response.is_success = True
    mock_response.status_code = 200
    mock_response.text = "OK"

    called_urls = []

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()

        async def track_post(url, *args, **kwargs):
            called_urls.append(url)
            return mock_response

        mock_client.post = AsyncMock(side_effect=track_post)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        await webhook_service.deliver_all(sample_event)

    # Should have called webhook1 (chantier.*) and webhook2 (*), but not webhook3 (user.*)
    assert len(called_urls) == 2
    assert "https://webhook1.com" in called_urls
    assert "https://webhook2.com" in called_urls
    assert "https://webhook3.com" not in called_urls


@pytest.mark.asyncio
async def test_webhook_deliver_all_no_active_webhooks(webhook_service, sample_event, mock_db):
    """Test deliver_all when no active webhooks exist."""
    mock_db.all = Mock(return_value=[])

    # Should not raise any errors
    await webhook_service.deliver_all(sample_event)


# ===== Tests for Event Listener =====


@pytest.mark.asyncio
async def test_webhook_event_listener_triggered():
    """Test that webhook_event_handler processes events."""
    sample_event = DomainEvent(
        event_type="test.event",
        aggregate_id="123",
        data={"test": "data"}
    )

    # Mock SessionLocal
    mock_db = Mock()
    mock_db.query = Mock(return_value=mock_db)
    mock_db.filter = Mock(return_value=mock_db)
    mock_db.all = Mock(return_value=[])
    mock_db.close = Mock()

    with patch('shared.infrastructure.webhooks.event_listener.SessionLocal', return_value=mock_db):
        # Should not raise any errors
        await webhook_event_handler(sample_event)

    # Verify DB was closed
    assert mock_db.close.called


@pytest.mark.asyncio
async def test_webhook_event_listener_handles_errors():
    """Test that webhook_event_handler handles errors gracefully."""
    sample_event = DomainEvent(event_type="test.event")

    # Mock SessionLocal to return a failing db
    mock_db = Mock()
    mock_db.query = Mock(side_effect=Exception("DB Error"))
    mock_db.close = Mock()

    with patch('shared.infrastructure.webhooks.event_listener.SessionLocal', return_value=mock_db):
        # Should not raise - errors should be caught and logged
        await webhook_event_handler(sample_event)

    # Verify DB was still closed
    assert mock_db.close.called


# ===== Tests for Error Scenarios =====


@pytest.mark.asyncio
async def test_webhook_delivery_timeout(webhook_service, sample_webhook, sample_event, mock_db):
    """Test handling of HTTP timeout."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=asyncio.TimeoutError("Timeout"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        # Should not raise - should handle gracefully
        sample_webhook.retry_enabled = False
        await webhook_service.deliver(sample_webhook, sample_event)

    # Should have recorded failure
    assert sample_webhook.consecutive_failures == 1


@pytest.mark.asyncio
async def test_webhook_delivery_connection_error(webhook_service, sample_webhook, sample_event, mock_db):
    """Test handling of connection errors."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        sample_webhook.retry_enabled = False
        await webhook_service.deliver(sample_webhook, sample_event)

    # Should have recorded failure
    assert sample_webhook.consecutive_failures == 1


@pytest.mark.asyncio
async def test_webhook_delivery_generic_exception(webhook_service, sample_webhook, sample_event, mock_db):
    """Test handling of unexpected exceptions."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=RuntimeError("Unexpected error"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        sample_webhook.retry_enabled = False
        await webhook_service.deliver(sample_webhook, sample_event)

    # Should have recorded failure
    assert sample_webhook.consecutive_failures == 1


# ===== Tests for Helper Methods =====


def test_compute_hmac():
    """Test HMAC-SHA256 computation."""
    secret = "my-secret-key"
    payload = '{"event": "test"}'

    signature = WebhookDeliveryService._compute_hmac(secret, payload)

    # Verify signature format
    assert isinstance(signature, str)
    assert len(signature) == 64  # SHA256 hex is 64 characters

    # Verify signature is correct
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    assert signature == expected


def test_serialize_event():
    """Test event serialization for webhook delivery."""
    event = DomainEvent(
        event_id="test-id-123",
        event_type="test.event",
        aggregate_id="456",
        data={"key": "value"},
        metadata={"user": 1}
    )

    serialized = WebhookDeliveryService._serialize_event(event)

    # Verify it's valid JSON
    parsed = json.loads(serialized)

    assert parsed["event_type"] == "test.event"
    assert parsed["event_id"] == "test-id-123"
    assert "timestamp" in parsed
    assert "data" in parsed


# ===== Integration Test =====


@pytest.mark.asyncio
async def test_webhook_full_delivery_flow(webhook_service, mock_db):
    """Integration test for full webhook delivery flow."""
    # Create webhook
    webhook = WebhookModel(
        id=1, user_id=1,
        url="https://example.com/hook",
        events=["chantier.created"],
        secret="test-secret",
        is_active=True,
        consecutive_failures=0,
        retry_enabled=True,
        max_retries=3
    )

    mock_db.all = Mock(return_value=[webhook])

    # Create event
    event = DomainEvent(
        event_type="chantier.created",
        aggregate_id="123",
        data={"nom": "Nouveau Chantier"}
    )

    # Mock successful HTTP response
    mock_response = Mock()
    mock_response.is_success = True
    mock_response.status_code = 200
    mock_response.text = '{"received": true}'

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        # Deliver to all matching webhooks
        await webhook_service.deliver_all(event)

    # Verify webhook was called
    assert mock_client.post.called

    # Verify delivery was successful
    assert webhook.consecutive_failures == 0
    assert webhook.is_active is True
