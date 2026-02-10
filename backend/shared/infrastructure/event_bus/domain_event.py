"""Backward compatibility - DomainEvent canonical location is shared.domain.events."""

# Re-export from canonical domain location
from shared.domain.events.domain_event import DomainEvent  # noqa: F401

__all__ = ["DomainEvent"]
