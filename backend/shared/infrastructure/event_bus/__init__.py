"""Event Bus - Architecture événementielle pour Hub Chantier."""

from .domain_event import DomainEvent
from .event_bus import EventBus as EventBusImpl, event_bus, event_handler
from .dependencies import get_event_bus


# Wrapper statique pour compatibilité avec l'ancienne API
class EventBus:
    """
    Interface statique pour le bus d'événements.

    Cela permet la compatibilité avec le code existant qui utilise EventBus.publish()
    tandis qu'on utilise en arrière-plan une implémentation asynchrone (event_bus).

    Note:
        EventBus.publish() ne peut pas attendre les handlers asynchrones depuis
        un contexte synchrone. Utilisez event_bus (l'instance) directement pour
        les opérations asynchrones dans les context FastAPI async.
    """

    # Référence à la fonction qui sera appelée
    @staticmethod
    def publish(event: DomainEvent) -> None:
        """
        Publie un événement de manière synchrone.

        En arrière-plan, lance une tâche asynchrone via event_bus.
        Les handlers asynchrones seront exécutés en parallèle mais sans attendre
        le retour dans le contexte actuel.

        Args:
            event: L'événement à publier
        """
        # Importer asyncio seulement quand nécessaire
        import asyncio

        try:
            # Essayer d'obtenir l'event loop actuel
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # On est dans un contexte async (ex: route FastAPI)
                # Créer une tâche pour ne pas bloquer
                asyncio.create_task(event_bus.publish(event))
            else:
                # On est dans un contexte sync mais il y a un event loop
                # Utiliser run_until_complete pour exécuter la publication
                loop.run_until_complete(event_bus.publish(event))
        except RuntimeError:
            # Pas d'event loop, probablement un contexte sync pur (test, CLI)
            # On doit créer une nouvelle boucle
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                new_loop.run_until_complete(event_bus.publish(event))
            finally:
                new_loop.close()


__all__ = [
    'DomainEvent',
    'EventBus',
    'event_bus',
    'EventBusImpl',
    'event_handler',
    'get_event_bus',
]
