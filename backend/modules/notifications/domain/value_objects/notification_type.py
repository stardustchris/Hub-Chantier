"""Types de notifications."""

from enum import Enum


class NotificationType(Enum):
    """
    Types de notifications supportes.

    Chaque type correspond a une action specifique dans l'application.
    """

    # Feed / Dashboard
    COMMENT_ADDED = "comment_added"  # Quelqu'un a commente votre post
    MENTION = "mention"  # Quelqu'un vous a mentionne avec @
    LIKE_ADDED = "like_added"  # Quelqu'un a aime votre post

    # Documents
    DOCUMENT_ADDED = "document_added"  # Nouveau document sur un chantier

    # Chantiers
    CHANTIER_ASSIGNMENT = "chantier_assignment"  # Affecte a un chantier

    # Signalements
    SIGNALEMENT_CREATED = "signalement_created"  # Nouveau signalement
    SIGNALEMENT_RESOLVED = "signalement_resolved"  # Signalement resolu

    # Taches
    TACHE_ASSIGNED = "tache_assigned"  # Tache assignee
    TACHE_DUE = "tache_due"  # Tache bientot due

    # Systeme
    SYSTEM = "system"  # Notification systeme generale
