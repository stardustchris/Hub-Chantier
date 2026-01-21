"""Shared - Code partagé entre tous les modules.

- domain/         : Entités et Value Objects communs
- infrastructure/ : Config, Database, EventBus
- kernel/         : Utilitaires de base
"""

from .infrastructure import settings, get_db, init_db, EventBus

__all__ = ["settings", "get_db", "init_db", "EventBus"]
