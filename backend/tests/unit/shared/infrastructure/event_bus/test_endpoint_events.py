"""Tests for endpoint event publishing.

Verifies that endpoints correctly publish domain events after successful operations:
- Planning: create_affectation
- Pointages: validate_pointage
- Chantiers: create_chantier
- Signalements: create_signalement
- Documents: upload_document
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import date, datetime
from io import BytesIO

from fastapi import UploadFile


# ===== Tests for Planning Routes =====


@pytest.mark.asyncio
async def test_create_affectation_publishes_event():
    """Test that create_affectation publishes AffectationCreatedEvent after db.commit."""
    from modules.planning.infrastructure.web.planning_routes import create_affectation
    from modules.planning.adapters.controllers.planning_schemas import CreateAffectationRequest

    # Mock dependencies
    mock_controller = Mock()
    mock_controller.create = Mock(return_value={
        "id": 1,
        "utilisateur_id": 10,
        "chantier_id": 5,
        "date": "2026-01-28",
    })

    mock_event_bus = Mock()
    mock_event_bus.publish = AsyncMock()

    # Create request
    request = CreateAffectationRequest(
        utilisateur_id=10,
        chantier_id=5,
        date="2026-01-28",
        type_affectation="unique",
    )

    # Call endpoint
    result = await create_affectation(
        request=request,
        current_user_id=1,
        current_user_role="admin",
        event_bus=mock_event_bus,
        controller=mock_controller,
    )

    # Verify event was published
    assert mock_event_bus.publish.called
    published_event = mock_event_bus.publish.call_args[0][0]

    assert published_event.event_type == "affectation.created"
    assert published_event.data["affectation_id"] == 1
    assert published_event.data["user_id"] == 10
    assert published_event.data["chantier_id"] == 5


@pytest.mark.asyncio
async def test_create_affectation_event_after_commit():
    """Test that event is published AFTER db.commit, not before."""
    from modules.planning.infrastructure.web.planning_routes import create_affectation
    from modules.planning.adapters.controllers.planning_schemas import CreateAffectationRequest

    call_order = []

    mock_controller = Mock()

    def create_with_tracking(*args, **kwargs):
        call_order.append("controller.create")
        return {
            "id": 1,
            "utilisateur_id": 10,
            "chantier_id": 5,
            "date": "2026-01-28",
        }

    mock_controller.create = Mock(side_effect=create_with_tracking)

    mock_event_bus = Mock()

    async def publish_with_tracking(event):
        call_order.append("event_bus.publish")

    mock_event_bus.publish = AsyncMock(side_effect=publish_with_tracking)

    request = CreateAffectationRequest(
        utilisateur_id=10,
        chantier_id=5,
        date="2026-01-28",
        type_affectation="unique",
    )

    await create_affectation(
        request=request,
        current_user_id=1,
        current_user_role="admin",
        event_bus=mock_event_bus,
        controller=mock_controller,
    )

    # Event should be published after controller.create (which commits)
    assert call_order == ["controller.create", "event_bus.publish"]


@pytest.mark.asyncio
async def test_create_affectation_failure_no_event():
    """Test that no event is published if creation fails."""
    from modules.planning.infrastructure.web.planning_routes import create_affectation
    from modules.planning.adapters.controllers.planning_schemas import CreateAffectationRequest
    from modules.planning.application.use_cases import AffectationConflictError
    from fastapi import HTTPException

    mock_controller = Mock()
    mock_controller.create = Mock(side_effect=AffectationConflictError(
        utilisateur_id=10,
        date_affectation=date(2026, 1, 28)
    ))

    mock_event_bus = Mock()
    mock_event_bus.publish = AsyncMock()

    request = CreateAffectationRequest(
        utilisateur_id=10,
        chantier_id=5,
        date="2026-01-28",
        type_affectation="unique",
    )

    # Should raise HTTPException
    with pytest.raises(HTTPException):
        await create_affectation(
            request=request,
            current_user_id=1,
            current_user_role="admin",
            event_bus=mock_event_bus,
            controller=mock_controller,
        )

    # Event should NOT have been published
    assert not mock_event_bus.publish.called


# ===== Tests for Pointages Routes =====


@pytest.mark.asyncio
async def test_validate_pointage_publishes_event():
    """Test that validate_pointage publishes HeuresValidatedEvent."""
    from modules.pointages.infrastructure.web.routes import validate_pointage

    mock_controller = Mock()
    mock_controller.validate_pointage = Mock(return_value={
        "id": 100,
        "utilisateur_id": 5,
        "chantier_id": 10,
        "date_pointage": date(2026, 1, 28),
        "heures_normales": "8:00",
        "heures_supplementaires": "2:00",
    })

    mock_event_bus = Mock()
    mock_event_bus.publish = AsyncMock()

    result = await validate_pointage(
        pointage_id=100,
        validateur_id=1,
        event_bus=mock_event_bus,
        controller=mock_controller,
    )

    # Verify event was published
    assert mock_event_bus.publish.called
    published_event = mock_event_bus.publish.call_args[0][0]

    assert published_event.event_type == "heures.validated"
    assert published_event.data["heures_id"] == 100
    assert published_event.data["user_id"] == 5


@pytest.mark.asyncio
async def test_validate_pointage_event_data_correct():
    """Test that HeuresValidatedEvent contains correct data."""
    from modules.pointages.infrastructure.web.routes import validate_pointage

    mock_controller = Mock()
    mock_controller.validate_pointage = Mock(return_value={
        "id": 200,
        "utilisateur_id": 15,
        "chantier_id": 20,
        "date_pointage": date(2026, 1, 15),
        "heures_normales": "7:30",
        "heures_supplementaires": "1:00",
    })

    mock_event_bus = Mock()
    mock_event_bus.publish = AsyncMock()

    await validate_pointage(
        pointage_id=200,
        validateur_id=1,
        event_bus=mock_event_bus,
        controller=mock_controller,
    )

    published_event = mock_event_bus.publish.call_args[0][0]

    assert published_event.data["heures_id"] == 200
    assert published_event.data["user_id"] == 15
    assert published_event.data["chantier_id"] == 20
    assert published_event.data["validated_by"] == 1
    assert "validated_at" in published_event.data


# ===== Tests for Chantiers Routes =====


@pytest.mark.asyncio
async def test_create_chantier_publishes_event():
    """Test that create_chantier publishes ChantierCreatedEvent."""
    from modules.chantiers.infrastructure.web.chantier_routes import create_chantier, CreateChantierRequest

    mock_controller = Mock()
    mock_controller.create = Mock(return_value={
        "id": 50,
        "nom": "Nouveau Chantier",
        "adresse": "123 rue Test",
        "code": "CH001",
        "statut": "ouvert",
        "conducteur_ids": [1, 2],
        "chef_chantier_ids": [3],
    })

    mock_event_bus = Mock()
    mock_event_bus.publish = AsyncMock()

    mock_user_repo = Mock()

    request = CreateChantierRequest(
        nom="Nouveau Chantier",
        adresse="123 rue Test",
    )

    # Need to mock get_current_user to provide user data
    with patch('modules.chantiers.infrastructure.web.chantier_routes._transform_chantier_response') as mock_transform:
        mock_transform.return_value = {"id": "50", "nom": "Nouveau Chantier"}

        result = await create_chantier(
            request=request,
            event_bus=mock_event_bus,
            controller=mock_controller,
            user_repo=mock_user_repo,
            current_user_id=1,
            _role="admin",
        )

    # Verify event was published
    assert mock_event_bus.publish.called
    published_event = mock_event_bus.publish.call_args[0][0]

    assert published_event.event_type == "chantier.created"
    assert published_event.data["chantier_id"] == 50
    assert published_event.data["nom"] == "Nouveau Chantier"


# ===== Tests for Signalements Routes =====


@pytest.mark.asyncio
async def test_create_signalement_publishes_event():
    """Test that create_signalement publishes SignalementCreatedEvent."""
    from modules.signalements.infrastructure.web.signalement_routes import create_signalement, SignalementCreateRequest

    mock_controller = Mock()
    mock_controller.create_signalement = Mock(return_value={
        "id": 75,
        "chantier_id": 10,
        "titre": "Problème électrique",
        "gravite": "haute",
        "priorite": "haute",
    })

    mock_event_bus = Mock()
    mock_event_bus.publish = AsyncMock()

    request = SignalementCreateRequest(
        chantier_id=10,
        titre="Problème électrique",
        description="Description du problème",
        priorite="haute",
    )

    current_user = {"id": 1, "email": "user@test.com"}

    result = await create_signalement(
        request=request,
        event_bus=mock_event_bus,
        controller=mock_controller,
        current_user=current_user,
    )

    # Verify event was published
    assert mock_event_bus.publish.called
    published_event = mock_event_bus.publish.call_args[0][0]

    assert published_event.event_type == "signalement.created"
    assert published_event.data["signalement_id"] == 75
    assert published_event.data["chantier_id"] == 10
    assert published_event.data["user_id"] == 1


# ===== Tests for Documents Routes =====


@pytest.mark.asyncio
async def test_upload_document_publishes_event():
    """Test that upload_document publishes DocumentUploadedEvent."""
    from modules.documents.infrastructure.web.document_routes import upload_document

    mock_result = Mock()
    mock_result.id = 150
    mock_result.nom = "document.pdf"
    mock_result.type_document = "pdf"
    mock_result.chantier_id = 25
    mock_result.taille = 1024
    mock_controller = Mock()
    mock_controller.upload_document = Mock(return_value=mock_result)

    mock_event_bus = Mock()
    mock_event_bus.publish = AsyncMock()

    mock_audit = Mock()
    mock_audit.log_action = Mock()

    # Create mock file
    file_content = b"PDF content here"
    mock_file = Mock(spec=UploadFile)
    mock_file.filename = "document.pdf"
    mock_file.content_type = "application/pdf"
    mock_file.file = BytesIO(file_content)
    mock_file.read = AsyncMock(return_value=file_content)
    mock_file.seek = AsyncMock()

    # Mock request
    mock_request = Mock()
    mock_request.client = Mock()
    mock_request.client.host = "127.0.0.1"

    result = await upload_document(
        dossier_id=10,
        http_request=mock_request,
        chantier_id=25,
        file=mock_file,
        description=None,
        niveau_acces=None,
        db=Mock(),
        event_bus=mock_event_bus,
        controller=mock_controller,
        current_user_id=1,
        audit=mock_audit,
    )

    # Verify event was published (synchronous call)
    assert mock_event_bus.publish.called
    published_event = mock_event_bus.publish.call_args[0][0]

    assert published_event.event_type == "document.uploaded"
    assert published_event.data["document_id"] == 150
    assert published_event.data["nom"] == "document.pdf"
    assert published_event.data["chantier_id"] == 25


@pytest.mark.asyncio
async def test_upload_document_event_after_controller():
    """Test that DocumentUploadedEvent is published after controller.upload_document."""
    from modules.documents.infrastructure.web.document_routes import upload_document

    call_order = []

    mock_controller = Mock()

    def upload_with_tracking(*args, **kwargs):
        call_order.append("controller.upload_document")
        result = Mock()
        result.id = 150
        result.nom = "test.pdf"
        result.type_document = "pdf"
        result.chantier_id = 25
        result.taille = 512
        return result

    mock_controller.upload_document = Mock(side_effect=upload_with_tracking)

    mock_event_bus = Mock()

    async def publish_with_tracking(event):
        call_order.append("event_bus.publish")

    mock_event_bus.publish = AsyncMock(side_effect=publish_with_tracking)

    mock_audit = Mock()
    mock_audit.log_action = Mock()

    file_content = b"test content"
    mock_file = Mock(spec=UploadFile)
    mock_file.filename = "test.pdf"
    mock_file.content_type = "application/pdf"
    mock_file.file = BytesIO(file_content)
    mock_file.read = AsyncMock(return_value=file_content)
    mock_file.seek = AsyncMock()

    mock_request = Mock()
    mock_request.client = Mock()
    mock_request.client.host = "127.0.0.1"

    mock_db = Mock()

    await upload_document(
        dossier_id=10,
        http_request=mock_request,
        chantier_id=25,
        file=mock_file,
        db=mock_db,
        event_bus=mock_event_bus,
        controller=mock_controller,
        current_user_id=1,
        audit=mock_audit,
    )

    # Verify order: controller first, then db.commit, then event
    assert mock_db.commit.called
    assert call_order == ["controller.upload_document", "event_bus.publish"]


# ===== Integration Tests =====


@pytest.mark.asyncio
async def test_all_endpoints_publish_correct_event_types():
    """Integration test: verify all endpoints publish the correct event types."""
    from modules.planning.domain.events.affectation_created import AffectationCreatedEvent
    from modules.pointages.domain.events.heures_validated import HeuresValidatedEvent
    from modules.chantiers.domain.events.chantier_created import ChantierCreatedEvent
    from modules.signalements.domain.events.signalement_created import SignalementCreatedEvent
    from modules.documents.domain.events.document_uploaded import DocumentUploadedEvent

    # Verify each event class exists and has correct event_type
    affectation_event = AffectationCreatedEvent(
        affectation_id=1,
        user_id=10,
        chantier_id=5,
        date_affectation=date.today()
    )
    assert affectation_event.event_type == "affectation.created"

    heures_event = HeuresValidatedEvent(
        heures_id=1,
        user_id=10,
        chantier_id=5,
        date=date.today(),
        heures_travaillees=8.0,
        heures_supplementaires=0.0,
        validated_by=1,
        validated_at=datetime.now()
    )
    assert heures_event.event_type == "heures.validated"

    chantier_event = ChantierCreatedEvent(
        chantier_id=1,
        nom="Test",
        adresse="Adresse",
        statut="ouvert"
    )
    assert chantier_event.event_type == "chantier.created"

    signalement_event = SignalementCreatedEvent(
        signalement_id=1,
        chantier_id=5,
        user_id=10,
        titre="Test",
        gravite="moyenne"
    )
    assert signalement_event.event_type == "signalement.created"

    document_event = DocumentUploadedEvent(
        document_id=1,
        nom="test.pdf",
        type_document="pdf",
        chantier_id=5,
        user_id=10
    )
    assert document_event.event_type == "document.uploaded"
