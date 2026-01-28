"""Injection de dépendance FastAPI pour l'Event Bus."""

from .event_bus import event_bus, EventBus


def get_event_bus() -> EventBus:
    """
    Dependency injection pour FastAPI.

    Retourne l'instance singleton de l'Event Bus.

    Usage dans un endpoint:
        ```python
        from fastapi import Depends
        from shared.infrastructure.event_bus.dependencies import get_event_bus
        from shared.infrastructure.event_bus import EventBus

        @router.post("/chantiers")
        async def create_chantier(
            data: ChantierCreate,
            event_bus: EventBus = Depends(get_event_bus)
        ):
            # Créer chantier
            new_chantier = ...
            db.commit()

            # Publier événement
            await event_bus.publish(ChantierCreatedEvent(...))

            return new_chantier
        ```

    Returns:
        EventBus: Instance singleton du bus d'événements
    """
    return event_bus
