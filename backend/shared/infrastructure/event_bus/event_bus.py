"""Event Bus central pour l'architecture événementielle."""

from typing import Dict, List, Callable, Optional
from collections import defaultdict
import asyncio
import logging

from .domain_event import DomainEvent

logger = logging.getLogger(__name__)


class EventBus:
    """
    Bus d'événements central (pattern Observer/Pub-Sub).

    Gère les abonnements et la publication d'événements de manière asynchrone.
    Tous les handlers sont exécutés en parallèle pour éviter les blocages.

    Features:
    - Pattern matching avec wildcards ('chantier.*', '*')
    - Exécution parallèle des handlers (asyncio.gather)
    - Gestion robuste des erreurs (un handler qui fail ne bloque pas les autres)
    - Historique des événements (debugging, limité à 1000)

    Example:
        >>> event_bus = EventBus()
        >>>
        >>> @event_bus.on('chantier.created')
        >>> async def handle_chantier_created(event):
        ...     print(f"Nouveau chantier: {event.data['nom']}")
        >>>
        >>> await event_bus.publish(DomainEvent(
        ...     event_type='chantier.created',
        ...     data={'nom': 'Test'}
        ... ))
    """

    def __init__(self):
        """Initialise le bus d'événements."""
        # Dict[event_type, List[handler]]
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)

        # Handlers universels écoutant TOUS les événements
        self._universal_subscribers: List[Callable] = []

        # Historique (pour debugging - limité à 1000 derniers événements)
        self._event_history: List[DomainEvent] = []
        self._max_history = 1000

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Enregistre un handler pour un type d'événement.

        Le handler peut être synchrone ou asynchrone.

        Args:
            event_type: Type d'événement ou pattern (ex: 'chantier.created', 'chantier.*', '*')
            handler: Fonction à appeler (signature: handler(event: DomainEvent) -> None)

        Example:
            >>> async def my_handler(event):
            ...     print(event.event_type)
            >>> event_bus.subscribe('chantier.*', my_handler)
        """
        self._subscribers[event_type].append(handler)
        logger.info(f"Handler {handler.__name__} souscrit à {event_type}")

    def on(self, event_type: str):
        """
        Décorateur pour enregistrer un handler.

        Args:
            event_type: Type d'événement ou pattern

        Example:
            >>> @event_bus.on('chantier.created')
            >>> async def handle_creation(event):
            ...     pass
        """
        def decorator(func: Callable):
            self.subscribe(event_type, func)
            return func
        return decorator

    def subscribe_all(self, handler: Callable) -> None:
        """
        Enregistre un handler pour TOUS les événements.

        Utile pour les services transversaux comme les webhooks qui doivent
        réagir à tous les événements du système.

        Args:
            handler: Fonction à appeler pour chaque événement (synchrone ou asynchrone)

        Example:
            >>> async def webhook_handler(event):
            ...     await deliver_webhook(event)
            >>> event_bus.subscribe_all(webhook_handler)
        """
        if handler not in self._universal_subscribers:
            self._universal_subscribers.append(handler)
            logger.info(f"Universal handler {handler.__name__} souscrit à TOUS les événements")

    async def publish(self, event: DomainEvent) -> None:
        """
        Publie un événement à tous les subscribers matchant.

        Tous les handlers sont exécutés en parallèle avec gestion d'erreurs.
        Un handler qui fail ne bloque pas les autres.

        Args:
            event: Événement à publier

        Example:
            >>> await event_bus.publish(DomainEvent(
            ...     event_type='chantier.created',
            ...     aggregate_id='123',
            ...     data={'nom': 'Nouveau chantier'}
            ... ))
        """
        # Sauvegarder dans l'historique
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        # Trouver handlers matchant (avec wildcards) + universal subscribers
        handlers = self._get_matching_handlers(event.event_type)
        all_handlers = handlers + self._universal_subscribers

        if not all_handlers:
            logger.debug(f"Aucun handler pour {event.event_type}")
            return

        # Exécuter tous handlers en parallèle
        tasks = []
        for handler in all_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    # Handler async
                    tasks.append(handler(event))
                else:
                    # Handler synchrone → run in executor
                    loop = asyncio.get_event_loop()
                    tasks.append(loop.run_in_executor(None, handler, event))
            except Exception as e:
                logger.error(
                    f"Erreur création task pour {handler.__name__}: {e}",
                    exc_info=True
                )

        # Attendre tous (parallèle) avec gestion erreurs
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Logger les erreurs
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    f"Erreur handler {all_handlers[i].__name__} pour {event.event_type}: {result}",
                    exc_info=result
                )

        success_count = len([r for r in results if not isinstance(r, Exception)])
        logger.info(
            f"Événement {event.event_type} publié à {len(all_handlers)} handlers "
            f"({success_count} succès, {len(all_handlers) - success_count} erreurs)"
        )

    def _get_matching_handlers(self, event_type: str) -> List[Callable]:
        """
        Trouve tous les handlers matchant un event_type.

        Supporte les wildcards :
        - 'chantier.*' match 'chantier.created', 'chantier.updated', etc.
        - '*' match tous les événements

        Args:
            event_type: Type d'événement à matcher

        Returns:
            List[Callable]: Liste des handlers matchant
        """
        handlers = []

        for pattern, pattern_handlers in self._subscribers.items():
            if self._event_matches(event_type, pattern):
                handlers.extend(pattern_handlers)

        return handlers

    @staticmethod
    def _event_matches(event_type: str, pattern: str) -> bool:
        """
        Vérifie si un event_type match un pattern.

        Exemples:
        - 'chantier.created' match 'chantier.created' (exact)
        - 'chantier.created' match 'chantier.*' (wildcard)
        - 'chantier.created' match '*' (catch-all)
        - 'chantier.created' ne match pas 'heures.*'

        Args:
            event_type: Type d'événement réel
            pattern: Pattern de souscription

        Returns:
            bool: True si match
        """
        # Catch-all
        if pattern == '*':
            return True

        # Match exact
        if pattern == event_type:
            return True

        # Wildcard (ex: 'chantier.*')
        if pattern.endswith('.*'):
            prefix = pattern[:-2]
            return event_type.startswith(prefix + '.')

        return False

    def get_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[DomainEvent]:
        """
        Retourne l'historique des événements (debugging).

        Args:
            event_type: Filtrer par type (optionnel, supporte wildcards)
            limit: Nombre maximum d'événements à retourner

        Returns:
            List[DomainEvent]: Événements récents
        """
        history = self._event_history[-limit:]

        if event_type:
            history = [e for e in history if self._event_matches(e.event_type, event_type)]

        return history

    def clear_history(self) -> None:
        """Vide l'historique des événements (utile pour tests)."""
        self._event_history.clear()

    def get_subscribers_count(self, event_type: Optional[str] = None) -> int:
        """
        Retourne le nombre de subscribers.

        Args:
            event_type: Type d'événement spécifique (optionnel)

        Returns:
            int: Nombre de handlers enregistrés
        """
        if event_type:
            return len(self._subscribers.get(event_type, []))
        return sum(len(handlers) for handlers in self._subscribers.values())


# Singleton global
event_bus = EventBus()


def event_handler(event_type: str):
    """
    Décorateur pour enregistrer un handler d'événement.

    Compatible avec l'ancien EventBus pour rétrocompatibilité.

    Args:
        event_type: Type d'événement ou pattern (ex: 'chantier.created', 'chantier.*')

    Returns:
        Le décorateur

    Example:
        >>> @event_handler('chantier.created')
        >>> async def handle_chantier_created(event):
        ...     print(f"Nouveau chantier: {event.data['nom']}")
    """
    def decorator(func: Callable):
        event_bus.subscribe(event_type, func)
        return func
    return decorator
