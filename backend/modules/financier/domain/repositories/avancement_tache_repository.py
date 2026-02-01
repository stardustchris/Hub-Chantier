"""Interface du repository pour l'avancement des taches (cross-module).

FIN-03: Suivi croise avancement physique vs financier.
Utilise raw SQL pour interroger le module taches sans import direct.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..value_objects.avancement_tache import AvancementTache


class AvancementTacheRepository(ABC):
    """Interface abstraite pour lire l'avancement des taches.

    Ce repository utilise des requetes SQL brutes (text()) pour
    interroger les tables du module taches sans importer ses modeles.
    """

    @abstractmethod
    def get_avancements_chantier(
        self, chantier_id: int
    ) -> List[AvancementTache]:
        """Recupere l'avancement de toutes les taches d'un chantier.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Liste des avancements par tache.
        """
        pass

    @abstractmethod
    def get_avancement_tache(
        self, tache_id: int
    ) -> Optional[AvancementTache]:
        """Recupere l'avancement d'une tache specifique.

        Args:
            tache_id: L'ID de la tache.

        Returns:
            L'avancement de la tache ou None si non trouvee.
        """
        pass
