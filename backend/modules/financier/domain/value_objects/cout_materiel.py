"""Value Object pour le cout materiel par ressource.

FIN-10: Suivi couts materiel.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CoutMaterielItem:
    """Represente le cout materiel d'une ressource sur un chantier.

    Attributes:
        ressource_id: ID de la ressource.
        nom: Nom de la ressource.
        code: Code de la ressource.
        jours_reservation: Nombre de jours de reservation.
        tarif_journalier: Tarif journalier en EUR.
        cout_total: Cout total = jours * tarif.
    """

    ressource_id: int
    nom: str
    code: str
    jours_reservation: int
    tarif_journalier: Decimal
    cout_total: Decimal
