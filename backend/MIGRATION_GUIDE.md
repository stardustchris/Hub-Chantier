# Migration Guide: Event Publishing Pattern for API Endpoints

## Overview

This guide documents the pattern for refactoring API endpoints to publish domain events after database commits. This enables reactive processing, notifications, webhooks, and system synchronization.

## Critical Pattern (4 Lines Added)

### Before
```python
@router.post("/resource")
def create_resource(
    request: CreateRequest,
    db: Session = Depends(get_db),
):
    # Create entity
    entity = Entity(**request.dict())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity
```

### After
```python
@router.post("/resource")
async def create_resource(  # ✅ STEP 1: Add async
    request: CreateRequest,
    db: Session = Depends(get_db),
    event_bus: EventBus = Depends(get_event_bus),  # ✅ STEP 2: Inject EventBus
    current_user = Depends(get_current_user),      # ✅ STEP 3: Inject user (if missing)
):
    # Create entity (logic unchanged)
    entity = Entity(**request.dict())
    db.add(entity)
    db.commit()
    db.refresh(entity)

    # ✅ STEP 4: Publish event AFTER commit
    await event_bus.publish(EntityCreatedEvent(
        entity_id=entity.id,
        user_id=current_user.id,
        # ... other relevant fields
    ))

    return entity
```

## Implementation Checklist

For each endpoint, follow these steps:

### 1. Function Signature Changes
- [ ] Add `async` keyword to function
- [ ] Add `event_bus: EventBus = Depends(get_event_bus)` to parameters
- [ ] Add `current_user = Depends(get_current_user)` if not present (for audit trail)

### 2. Imports
Add at the top of the file:
```python
from shared.infrastructure.event_bus.dependencies import get_event_bus
from shared.infrastructure.event_bus import EventBus
from ...domain.events import YourEntityCreatedEvent  # Domain event
```

### 3. Event Publishing
After DB commit, publish the event:
```python
await event_bus.publish(YourEntityCreatedEvent(
    entity_id=entity.id,
    # ... add all relevant metadata
))
```

### 4. Event Dataclass
Create in `domain/events/your_entity_events.py`:
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any

@dataclass(frozen=True)
class YourEntityCreatedEvent:
    """Event emitted when entity is created."""

    entity_id: int
    # ... other fields (use frozen=True for immutability)
    timestamp: datetime = field(default_factory=datetime.now)
```

## Key Principles

### 1. Timing: AFTER, Not Before
```python
# ❌ WRONG
await event_bus.publish(event)
db.commit()  # Event published before commit!

# ✅ CORRECT
db.commit()
await event_bus.publish(event)  # Event published after commit
```

### 2. No Breaking Changes
- Event publishing is **additive only**
- Business logic remains identical
- Return values unchanged
- Response models unchanged

### 3. Async/Await
- Endpoints with event publishing must be `async`
- Use `await event_bus.publish()` inside endpoint
- Event handlers run asynchronously without blocking the response

### 4. Data Consistency
- Always use **database-persisted IDs** in events, not generated/transient IDs
- Include user context for audit trails:
  ```python
  metadata={
      'user_id': current_user.id,
      'user_email': current_user.email,
      'timestamp': datetime.now().isoformat()
  }
  ```

## Events vs Commands vs Side Effects

### When to use events:
- ✅ After successful database modifications
- ✅ For notifications (email, SMS, webhook)
- ✅ For downstream synchronization (payroll, ERP)
- ✅ For audit logging
- ✅ For cache invalidation

### When NOT to use events:
- ❌ Before database commit
- ❌ For validation (happens before commit)
- ❌ For permission checks (happens before commit)
- ❌ For error handling (only publish on success)

## Pattern: Critical Paths That Trigger Synchronization

Some endpoints are marked as **CRITICAL** because they trigger downstream systems:

### Example: Pointages Validation (CRITICAL)
```python
@router.post("/{pointage_id}/validate")
async def validate_pointage(  # ← CRITICAL: Triggers payroll sync
    pointage_id: int,
    validateur_id: int = Depends(get_current_user_id),
    event_bus: EventBus = Depends(get_event_bus),
    controller: PointageController = Depends(get_controller),
):
    # ... validation logic ...
    pointage = controller.validate_pointage(pointage_id, validateur_id)

    # ✅ Publish event that triggers webhook to payroll system
    await event_bus.publish(HeuresValidatedEvent(
        feuille_id=pointage['feuille_id'],
        utilisateur_id=pointage['utilisateur_id'],
        heures_validees=pointage['total_heures'],
        timestamp=datetime.now()
    ))

    return pointage
```

## The 30+ Other Endpoints

For reference, other endpoints that should follow this pattern:

### Planning Module
- `PUT /affectations/{affectation_id}` → AffectationUpdatedEvent
- `DELETE /affectations/{affectation_id}` → AffectationDeletedEvent
- `POST /affectations/duplicate` → AffectationBulkCreatedEvent

### Pointages Module
- `POST /` (create pointage) → PointageCreatedEvent
- `PUT /{pointage_id}` (update) → PointageUpdatedEvent
- `POST /{pointage_id}/submit` → PointageSubmittedEvent

### Chantiers Module
- `PUT /chantiers/{chantier_id}` → ChantierUpdatedEvent
- `POST /chantiers/{chantier_id}/statut` → ChantierStatutChangedEvent
- `DELETE /chantiers/{chantier_id}` → ChantierDeletedEvent

### Signalements Module
- `PUT /signalements/{signalement_id}` → SignalementUpdatedEvent
- `POST /signalements/{signalement_id}/traiter` → SignalementStatusChangedEvent
- `DELETE /signalements/{signalement_id}` → SignalementDeletedEvent

### Documents Module
- `PUT /documents/{document_id}` → DocumentUpdatedEvent
- `DELETE /documents/{document_id}` → DocumentDeletedEvent
- `POST /autorisations` → AutorisationCreatedEvent

## Testing with Events

When testing endpoints that publish events, mock the event bus:

```python
# pytest fixture
@pytest.fixture
def mock_event_bus(mocker):
    return mocker.AsyncMock()

def test_create_resource(client, mock_event_bus):
    with patch('module.infrastructure.web.routes.get_event_bus', return_value=mock_event_bus):
        response = client.post("/resource", json={...})
        assert response.status_code == 201
        # Verify event was published
        mock_event_bus.publish.assert_called_once()
```

## Validation (Before Commit)

1. **Read endpoint file** before modifying
2. **Preserve signature** (only add parameters, don't remove)
3. **Verify commit is BEFORE publish** in code review
4. **Check type hints** are correct
5. **No import duplicates** after merge
6. **Test async compatibility** with FastAPI

## Rollback Safety

If a refactored endpoint causes issues:
1. Events published are **fire-and-forget** (async)
2. Removing event publishing doesn't affect database state
3. Simply remove the `await event_bus.publish()` line
4. Previous event handlers can ignore unknown events gracefully

## References

- Event Bus Implementation: `shared/infrastructure/event_bus/`
- Domain Events Pattern: `modules/{module}/domain/events/`
- Example: `modules/planning/infrastructure/web/planning_routes.py` (POST /affectations)

## Refactored Endpoints (Completed)

1. ✅ Planning: `POST /affectations` → AffectationCreatedEvent
2. ✅ Pointages: `POST /{pointage_id}/validate` → HeuresValidatedEvent
3. ✅ Chantiers: `POST /chantiers` → ChantierCreatedEvent
4. ✅ Signalements: `POST /signalements` → SignalementCreatedEvent
5. ✅ Documents: `POST /dossiers/{dossier_id}/documents` → DocumentUploadedEvent
