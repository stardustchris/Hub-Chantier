"""Value Object pour le cout main-d'oeuvre par employe.

FIN-09: Suivi couts main-d'oeuvre.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CoutEmploye:
    """Represente le cout main-d'oeuvre d'un employe sur un chantier.

    Attributes:
        user_id: ID de l'employe.
        nom: Nom de famille.
        prenom: Prenom.
        heures_validees: Nombre d'heures validees (decimal).
        taux_horaire: Taux horaire en EUR.
        cout_total: Cout total = heures * taux.
    """

    user_id: int
    nom: str
    prenom: str
    heures_validees: Decimal
    taux_horaire: Decimal
    cout_total: Decimal
