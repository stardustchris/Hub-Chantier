"""Module Interventions - Gestion des interventions ponctuelles.

CDC Section 12 - INT-01 a INT-17

Ce module gere les interventions ponctuelles distinctes des chantiers:
- SAV (Service Apres-Vente)
- Maintenance preventive et curative
- Depannages d'urgence
- Levee de reserves

Fonctionnalites principales:
- INT-01: Onglet dedie Planning (3eme onglet)
- INT-02: Liste des interventions avec filtres
- INT-03: Creation d'intervention
- INT-04: Fiche intervention complete
- INT-05: Gestion des statuts
- INT-06: Planning hebdomadaire
- INT-07: Blocs intervention colores
- INT-08: Multi-interventions par jour
- INT-10: Affectation techniciens
- INT-11: Fil d'actualite
- INT-12: Chat intervention
- INT-13: Signature client
- INT-14: Rapport PDF
- INT-15: Selection posts pour rapport
- INT-17: Affectation sous-traitants
"""

from .domain import (
    # Entities
    Intervention,
    TransitionStatutInvalideError,
    AffectationIntervention,
    InterventionMessage,
    TypeMessage,
    SignatureIntervention,
    TypeSignataire,
    # Value Objects
    StatutIntervention,
    PrioriteIntervention,
    TypeIntervention,
    # Repositories
    InterventionRepository,
    AffectationInterventionRepository,
    InterventionMessageRepository,
    SignatureInterventionRepository,
)
from .infrastructure.web import router

__all__ = [
    # Entities
    "Intervention",
    "TransitionStatutInvalideError",
    "AffectationIntervention",
    "InterventionMessage",
    "TypeMessage",
    "SignatureIntervention",
    "TypeSignataire",
    # Value Objects
    "StatutIntervention",
    "PrioriteIntervention",
    "TypeIntervention",
    # Repositories
    "InterventionRepository",
    "AffectationInterventionRepository",
    "InterventionMessageRepository",
    "SignatureInterventionRepository",
    # Router
    "router",
]
