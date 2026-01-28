# Event Publishing Refactoring - Detailed Changes

## Quick Reference

| Module | Endpoint | Event | Status |
|--------|----------|-------|--------|
| Planning | POST /affectations | AffectationCreatedEvent | ✅ Complete |
| Pointages | POST /{pointage_id}/validate | HeuresValidatedEvent | ✅ Complete (⚡CRITICAL) |
| Chantiers | POST /chantiers | ChantierCreatedEvent | ✅ Complete |
| Signalements | POST /signalements | SignalementCreated | ✅ Complete |
| Documents | POST /dossiers/{dossier_id}/documents | DocumentUploadedEvent | ✅ Complete |

---

## 1. Planning Module: create_affectation

### File
`backend/modules/planning/infrastructure/web/planning_routes.py`

### Changes

**Import Section** (Added 3 lines):
```python
from ...domain.events.affectation_events import AffectationCreatedEvent
from shared.infrastructure.event_bus.dependencies import get_event_bus
from shared.infrastructure.event_bus import EventBus
```

**Function Signature** (Line 51):
```python
# BEFORE
def create_affectation(
    request: CreateAffectationRequest,
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    controller: PlanningController = Depends(get_planning_controller),
):

# AFTER
async def create_affectation(
    request: CreateAffectationRequest,
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    event_bus: EventBus = Depends(get_event_bus),  # ← ADDED
    controller: PlanningController = Depends(get_planning_controller),
):
```

**Event Publishing** (After db.commit, before return):
```python
try:
    result = controller.create(request, current_user_id)

    # ← ADDED: Publish event after database commit
    await event_bus.publish(AffectationCreatedEvent(
        affectation_id=result["id"],
        utilisateur_id=result["utilisateur_id"],
        chantier_id=result["chantier_id"],
        date=result["date"],
        created_by=current_user_id,
    ))

    return result
except ...
```

### Impact
- Handlers can react to new assignments (notifications, webhooks)
- 0 breaking changes
- Async-compatible with FastAPI

---

## 2. Pointages Module: validate_pointage ⚡ CRITICAL

### File
`backend/modules/pointages/infrastructure/web/routes.py`

### Changes

**Import Section** (Added 1 line):
```python
from ...domain.events.heures_validated import HeuresValidatedEvent
```

**Function Signature** (Line 446):
```python
# BEFORE
def validate_pointage(
    pointage_id: int,
    validateur_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):

# AFTER
async def validate_pointage(
    pointage_id: int,
    validateur_id: int = Depends(get_current_user_id),
    event_bus = Depends(get_event_bus),  # ← ADDED
    controller: PointageController = Depends(get_controller),
):
```

**Event Publishing** (After db.commit, before return):
```python
try:
    result = controller.validate_pointage(pointage_id, validateur_id)

    # ← ADDED: Publish event CRITICAL for payroll sync
    from datetime import datetime
    await event_bus.publish(HeuresValidatedEvent(
        heures_id=result.get("id", pointage_id),
        user_id=result.get("utilisateur_id"),
        chantier_id=result.get("chantier_id"),
        date=result.get("date_pointage") if isinstance(result.get("date_pointage"), date) else date.today(),
        heures_travaillees=float(result.get("heures_normales", "0:0").split(":")[0]) if isinstance(result.get("heures_normales"), str) else float(result.get("heures_normales", 0)),
        heures_supplementaires=float(result.get("heures_supplementaires", "0:0").split(":")[0]) if isinstance(result.get("heures_supplementaires"), str) else float(result.get("heures_supplementaires", 0)),
        validated_by=validateur_id,
        validated_at=datetime.now(),
        metadata={
            'user_id': validateur_id,
            'pointage_id': pointage_id,
        }
    ))

    return result
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

### Impact
⚡ **CRITICAL**: This event triggers automatic synchronization with the payroll system:
- Webhook is called to sync validated hours to payroll provider
- Essential for accurate payment processing
- Real-time data consistency between Hub-Chantier and payroll system

---

## 3. Chantiers Module: create_chantier

### File
`backend/modules/chantiers/infrastructure/web/chantier_routes.py`

### Changes

**Import Section** (Added 3 lines):
```python
from ...domain.events.chantier_events import ChantierCreatedEvent
from shared.infrastructure.event_bus.dependencies import get_event_bus
from shared.infrastructure.event_bus import EventBus
```

**Function Signature** (Line 236):
```python
# BEFORE
def create_chantier(
    request: CreateChantierRequest,
    controller: ChantierController = Depends(get_chantier_controller),
    user_repo: UserRepository = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),
):

# AFTER
async def create_chantier(
    request: CreateChantierRequest,
    event_bus: EventBus = Depends(get_event_bus),  # ← ADDED
    controller: ChantierController = Depends(get_chantier_controller),
    user_repo: UserRepository = Depends(get_user_repository),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_conducteur_or_admin),
):
```

**Event Publishing**:
```python
try:
    # ... existing logic ...
    result = controller.create(...)

    # ← ADDED: Publish event after database commit
    await event_bus.publish(ChantierCreatedEvent(
        chantier_id=result["id"],
        code=result.get("code", ""),
        nom=result.get("nom", ""),
        statut=result.get("statut", "ouvert"),
        conducteur_ids=tuple(result.get("conducteur_ids", [])),
        chef_chantier_ids=tuple(result.get("chef_chantier_ids", [])),
    ))

    return _transform_chantier_response(result, controller, user_repo)
except ...
```

### Impact
- Handlers can react to new work sites (create folders, initialize data)
- 0 breaking changes
- Backward compatible

---

## 4. Signalements Module: create_signalement

### File
`backend/modules/signalements/infrastructure/web/signalement_routes.py`

### Changes

**Import Section** (Added 3 lines):
```python
from ...domain.events.signalement_events import SignalementCreated
from shared.infrastructure.event_bus.dependencies import get_event_bus
from shared.infrastructure.event_bus import EventBus
```

**Function Signature** (Line 170):
```python
# BEFORE
def create_signalement(
    request: SignalementCreateRequest,
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):

# AFTER
async def create_signalement(
    request: SignalementCreateRequest,
    event_bus: EventBus = Depends(get_event_bus),  # ← ADDED
    controller: SignalementController = Depends(get_signalement_controller),
    current_user: dict = Depends(get_current_user),
):
```

**Event Publishing**:
```python
try:
    dto = SignalementCreateDTO(...)
    result = controller.create_signalement(dto)

    # ← ADDED: Publish event after database commit
    await event_bus.publish(SignalementCreated(
        signalement_id=result["id"],
        chantier_id=result["chantier_id"],
        titre=result["titre"],
        priorite=result.get("priorite", "moyenne"),
        cree_par=current_user["id"],
    ))

    return result
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

### Impact
- Handlers can notify assignees (email, SMS, push notifications)
- Can trigger escalation workflows
- 0 breaking changes

---

## 5. Documents Module: upload_document

### File
`backend/modules/documents/infrastructure/web/document_routes.py`

### Changes

**Import Section** (Added 3 lines):
```python
from ...domain.events.document_uploaded import DocumentUploadedEvent
from shared.infrastructure.event_bus.dependencies import get_event_bus
from shared.infrastructure.event_bus import EventBus
```

**Function Signature** (Line 283):
```python
# BEFORE (already async)
async def upload_document(
    dossier_id: int,
    http_request: Request,
    chantier_id: int = Query(...),
    file: UploadFile = File(...),
    description: Optional[str] = Query(None),
    niveau_acces: Optional[str] = Query(None),
    controller: DocumentController = Depends(get_document_controller),
    current_user_id: int = Depends(get_current_user_id),
    audit: AuditService = Depends(get_audit_service),
):

# AFTER
async def upload_document(
    dossier_id: int,
    http_request: Request,
    chantier_id: int = Query(...),
    file: UploadFile = File(...),
    description: Optional[str] = Query(None),
    niveau_acces: Optional[str] = Query(None),
    event_bus: EventBus = Depends(get_event_bus),  # ← ADDED
    controller: DocumentController = Depends(get_document_controller),
    current_user_id: int = Depends(get_current_user_id),
    audit: AuditService = Depends(get_audit_service),
):
```

**Event Publishing** (After audit logging, before return):
```python
try:
    # ... existing logic ...
    result = controller.upload_document(...)
    
    # Audit Trail (existing)
    audit.log_action(...)

    # ← ADDED: Publish event after database commit
    await event_bus.publish(DocumentUploadedEvent(
        document_id=result.get("id"),
        nom=result.get("nom", file.filename or "document"),
        type_document=result.get("type_document", "autre"),
        chantier_id=chantier_id,
        user_id=current_user_id,
    ))

    return result
except ...
```

### Impact
- Handlers can index documents for search
- Can generate previews/thumbnails
- Can notify interested parties
- 0 breaking changes

---

## Pattern Summary

All 5 refactored endpoints follow identical pattern:

### 1. Async Function
```python
# Add async keyword
async def endpoint(...):
```

### 2. Inject EventBus
```python
event_bus: EventBus = Depends(get_event_bus)
```

### 3. Import Event
```python
from ...domain.events.xxx_events import XxxEvent
from shared.infrastructure.event_bus import EventBus
from shared.infrastructure.event_bus.dependencies import get_event_bus
```

### 4. Publish After Commit
```python
result = controller.create(...)  # DB commit inside controller
await event_bus.publish(Event(...))  # Publish AFTER commit
return result
```

---

## Testing Changes

### Before
```python
def test_create_affectation():
    response = client.post("/affectations", json={...})
    assert response.status_code == 201
```

### After
```python
@pytest.mark.asyncio
async def test_create_affectation(mocker):
    mock_event_bus = mocker.AsyncMock()
    with patch('module.routes.get_event_bus', return_value=mock_event_bus):
        response = client.post("/affectations", json={...})
        assert response.status_code == 201
        # Verify event was published
        mock_event_bus.publish.assert_called_once()
        # Verify event content
        call_args = mock_event_bus.publish.call_args[0][0]
        assert isinstance(call_args, AffectationCreatedEvent)
        assert call_args.affectation_id == response.json()["id"]
```

---

## Deployment Checklist

- [ ] Code review approved
- [ ] All 5 files pass syntax check
- [ ] Async endpoints tested with asyncio
- [ ] Event bus is running/configured
- [ ] No event handlers registered yet (events will be queued/logged)
- [ ] Backward compatibility verified
- [ ] Database migrations not required (schema unchanged)
- [ ] Rollback plan documented
- [ ] Monitoring/logging configured for event publishing
- [ ] Merge to main branch

---

## Rollback Plan

If issues arise:

1. **Immediate**: Remove `await event_bus.publish(...)` lines
2. **Git**: `git revert <commit>`
3. **Impact**: 
   - Database state unaffected (events are fire-and-forget)
   - API responses identical
   - Business logic unchanged

---

## Timeline

- **Completed**: January 28, 2026
- **5 Critical Endpoints**: Refactored
- **Migration Guide**: Created (`MIGRATION_GUIDE.md`)
- **Documentation**: Complete (`REFACTORING_SUMMARY.md`)
- **Ready for**: Event handler implementation

---

## References

- Event Bus: `/backend/shared/infrastructure/event_bus/`
- Domain Events Pattern: `/backend/modules/*/domain/events/`
- Migration Guide: `/backend/MIGRATION_GUIDE.md`
- Summary: `/backend/REFACTORING_SUMMARY.md`
