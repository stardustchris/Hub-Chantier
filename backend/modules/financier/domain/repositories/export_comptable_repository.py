"""Interface du repository pour l'export comptable.

FIN-13: Export comptable CSV/Excel - requetes cross-tables
pour generer les ecritures comptables.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional


class ExportComptableRepository(ABC):
    """Interface abstraite pour les requetes d'export comptable.

    Utilise des requetes SQL brutes (text()) pour interroger
    les tables achats et factures_client.
    """

    @abstractmethod
    def get_achats_periode(
        self,
        chantier_id: Optional[int],
        date_debut: date,
        date_fin: date,
    ) -> List[dict]:
        """Recupere les achats factures sur une periode.

        Args:
            chantier_id: ID du chantier (optionnel, None = tous).
            date_debut: Date de debut de la periode.
            date_fin: Date de fin de la periode.

        Returns:
            Liste de dictionnaires avec les donnees des achats.
        """
        pass

    @abstractmethod
    def get_factures_periode(
        self,
        chantier_id: Optional[int],
        date_debut: date,
        date_fin: date,
    ) -> List[dict]:
        """Recupere les factures emises sur une periode.

        Args:
            chantier_id: ID du chantier (optionnel, None = tous).
            date_debut: Date de debut de la periode.
            date_fin: Date de fin de la periode.

        Returns:
            Liste de dictionnaires avec les donnees des factures.
        """
        pass
