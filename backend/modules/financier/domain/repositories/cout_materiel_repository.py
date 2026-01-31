"""Interface du repository pour le suivi des couts materiel.

FIN-10: Suivi couts materiel - calculs a partir des reservations validees.
"""

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import List, Optional

from ..value_objects.cout_materiel import CoutMaterielItem


class CoutMaterielRepository(ABC):
    """Interface abstraite pour le calcul des couts materiel."""

    @abstractmethod
    def calculer_cout_chantier(
        self,
        chantier_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
    ) -> Decimal:
        """Calcule le cout total materiel d'un chantier.

        Somme de (jours_reservation * tarif_journalier) pour les reservations validees.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (optionnel).
            date_fin: Date de fin de la periode (optionnel).

        Returns:
            Le cout total en Decimal.
        """
        pass

    @abstractmethod
    def calculer_cout_par_ressource(
        self,
        chantier_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
    ) -> List[CoutMaterielItem]:
        """Calcule le cout materiel par ressource.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (optionnel).
            date_fin: Date de fin de la periode (optionnel).

        Returns:
            Liste des couts par ressource.
        """
        pass
