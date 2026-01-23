"""
Module Formulaires - Gestion des formulaires terrain personnalisables.

Selon CDC Section 8 - Formulaires Chantier (FOR-01 a FOR-11).

Fonctionnalites implementees:
- FOR-01: Templates personnalises
- FOR-02: Remplissage mobile (infrastructure)
- FOR-03: Champs auto-remplis (date, heure, localisation, intervenant)
- FOR-04: Ajout photos horodatees
- FOR-05: Signature electronique
- FOR-06: Centralisation automatique (rattachement chantier)
- FOR-07: Horodatage automatique
- FOR-08: Historique complet
- FOR-09: Export PDF
- FOR-10: Liste par chantier
- FOR-11: Lien direct (Remplir le formulaire)
"""

from .domain import (
    # Entities
    TemplateFormulaire,
    ChampTemplate,
    FormulaireRempli,
    ChampRempli,
    PhotoFormulaire,
    # Value Objects
    TypeChamp,
    StatutFormulaire,
    CategorieFormulaire,
    # Repositories
    TemplateFormulaireRepository,
    FormulaireRempliRepository,
    # Events
    TemplateCreatedEvent,
    TemplateUpdatedEvent,
    TemplateDeletedEvent,
    FormulaireCreatedEvent,
    FormulaireSubmittedEvent,
    FormulaireValidatedEvent,
    FormulaireSignedEvent,
)

from .infrastructure import router, templates_router

__all__ = [
    # Domain - Entities
    "TemplateFormulaire",
    "ChampTemplate",
    "FormulaireRempli",
    "ChampRempli",
    "PhotoFormulaire",
    # Domain - Value Objects
    "TypeChamp",
    "StatutFormulaire",
    "CategorieFormulaire",
    # Domain - Repositories
    "TemplateFormulaireRepository",
    "FormulaireRempliRepository",
    # Domain - Events
    "TemplateCreatedEvent",
    "TemplateUpdatedEvent",
    "TemplateDeletedEvent",
    "FormulaireCreatedEvent",
    "FormulaireSubmittedEvent",
    "FormulaireValidatedEvent",
    "FormulaireSignedEvent",
    # Infrastructure - Routers
    "router",
    "templates_router",
]
