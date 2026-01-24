"""Module Logistique - Gestion du Materiel.

CDC Section 11 - LOG-01 a LOG-18.

Fonctionnalites:
- Referentiel materiel (ressources de l'entreprise)
- Reservations par chantier avec workflow de validation
- Planning par ressource (vue calendrier)
- Detection de conflits de reservation
"""
from .infrastructure.web import router

__all__ = ["router"]
