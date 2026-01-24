"""Module Logistique - Gestion du matériel et réservations.

Ce module gère:
- Le référentiel des ressources (engins, véhicules, équipements)
- Les réservations avec workflow de validation
- Le planning par ressource
- Les notifications et conflits
"""

from .infrastructure.web import router

__all__ = ["router"]
