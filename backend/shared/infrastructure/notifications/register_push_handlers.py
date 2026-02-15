"""Enregistrement des handlers de notifications push dans l'EventBus.

SIG-13 : Push à la création d'un signalement
SIG-17 : Push lors des escalades
FEED-17 : Push nouvelle publication dans le feed
PLN-23 : Push nouvelle affectation planning
"""

import logging

from shared.infrastructure.event_bus import event_bus

logger = logging.getLogger(__name__)


def register_push_notification_handlers() -> None:
    """Enregistre tous les handlers de notifications push dans l'EventBus.

    Appelé au démarrage de l'application dans main.py.
    """
    from .handlers.signalement_notification_handler import (
        SignalementNotificationHandler,
    )
    from .handlers.feed_notification_handler import FeedNotificationHandler
    from .handlers.planning_notification_handler import PlanningNotificationHandler

    # SIG-13 : Notification à la création d'un signalement
    sig_handler = SignalementNotificationHandler()
    event_bus.subscribe(
        "signalement.created",
        sig_handler.handle_signalement_created,
    )
    logger.info("Handler push SIG-13 (signalement.created) enregistré")

    # SIG-17 : Notification lors des escalades
    event_bus.subscribe(
        "signalement.escaladed",
        sig_handler.handle_signalement_escaladed,
    )
    logger.info("Handler push SIG-17 (signalement.escaladed) enregistré")

    # FEED-17 : Notification nouvelle publication
    feed_handler = FeedNotificationHandler()
    event_bus.subscribe(
        "feed.post_published",
        feed_handler.handle_post_published,
    )
    logger.info("Handler push FEED-17 (feed.post_published) enregistré")

    # PLN-23 : Notification nouvelle affectation
    planning_handler = PlanningNotificationHandler()
    event_bus.subscribe(
        "planning.affectation_created",
        planning_handler.handle_affectation_created,
    )
    logger.info("Handler push PLN-23 (planning.affectation_created) enregistré")
