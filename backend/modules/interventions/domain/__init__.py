"""Module Domain - Interventions.

Contient les entites, value objects et interfaces de repository
pour le module de gestion des interventions (INT-01 a INT-17).
"""

from .entities import (
    Intervention,
    TransitionStatutInvalideError,
    AffectationIntervention,
    InterventionMessage,
    TypeMessage,
    SignatureIntervention,
    TypeSignataire,
)
from .value_objects import (
    StatutIntervention,
    PrioriteIntervention,
    TypeIntervention,
)
from .repositories import (
    InterventionRepository,
    AffectationInterventionRepository,
    InterventionMessageRepository,
    SignatureInterventionRepository,
)
from .events import (
    InterventionCreee,
    InterventionPlanifiee,
    InterventionDemarree,
    InterventionTerminee,
    InterventionAnnulee,
    TechnicienAffecte,
    TechnicienDesaffecte,
    SignatureAjoutee,
    RapportGenere,
    MessageAjoute,
)

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
    # Events
    "InterventionCreee",
    "InterventionPlanifiee",
    "InterventionDemarree",
    "InterventionTerminee",
    "InterventionAnnulee",
    "TechnicienAffecte",
    "TechnicienDesaffecte",
    "SignatureAjoutee",
    "RapportGenere",
    "MessageAjoute",
]
