"""Interface du repository pour le suivi des couts main-d'oeuvre.

FIN-09: Suivi couts main-d'oeuvre - calculs a partir des pointages valides.
"""

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import List, Optional

from ..value_objects.cout_employe import CoutEmploye


class CoutMainOeuvreRepository(ABC):
    """Interface abstraite pour le calcul des couts main-d'oeuvre."""

    @abstractmethod
    def calculer_cout_chantier(
        self,
        chantier_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
    ) -> Decimal:
        """Calcule le cout total main-d'oeuvre d'un chantier.

        Somme de (heures * taux_horaire) pour les pointages valides.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (optionnel).
            date_fin: Date de fin de la periode (optionnel).

        Returns:
            Le cout total en Decimal.
        """
        pass

    @abstractmethod
    def calculer_cout_par_employe(
        self,
        chantier_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
    ) -> List[CoutEmploye]:
        """Calcule le cout main-d'oeuvre par employe.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (optionnel).
            date_fin: Date de fin de la periode (optionnel).

        Returns:
            Liste des couts par employe.
        """
        pass
