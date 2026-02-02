"""Port pour obtenir les informations basiques d'un chantier.

Permet au module financier d'acceder aux noms et statuts des chantiers
sans dependance directe sur le module chantiers.

Conforme Clean Architecture:
- Interface definie dans Application layer (shared)
- Implementation dans Infrastructure layer (shared)
- Aucun import de modules specifiques
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ChantierInfoDTO:
    """Informations basiques d'un chantier.

    Attributes:
        id: Identifiant unique du chantier.
        nom: Nom du chantier.
        statut: Statut du chantier (ex: "ouvert", "en_cours", "receptionne", "ferme").
    """

    id: int
    nom: str
    statut: str


class ChantierInfoPort(ABC):
    """Port pour obtenir les informations basiques des chantiers.

    Permet aux modules non-chantiers d'acceder aux noms et statuts
    sans import direct du module chantiers.
    """

    @abstractmethod
    def get_chantier_info(self, chantier_id: int) -> Optional[ChantierInfoDTO]:
        """Recupere les infos basiques d'un chantier.

        Args:
            chantier_id: ID du chantier.

        Returns:
            ChantierInfoDTO ou None si non trouve.
        """
        ...

    @abstractmethod
    def get_chantiers_info_batch(
        self, chantier_ids: list[int]
    ) -> Dict[int, ChantierInfoDTO]:
        """Recupere les infos de plusieurs chantiers en batch.

        Args:
            chantier_ids: Liste des IDs de chantiers.

        Returns:
            Dict mapping chantier_id -> ChantierInfoDTO.
        """
        ...
