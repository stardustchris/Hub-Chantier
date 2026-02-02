"""Adapter pour ChantierInfoPort.

Implementation concrete utilisant le ChantierRepository.
Les imports cross-module sont autorises dans Infrastructure layer.
"""

import logging
from typing import Dict, Optional

from shared.application.ports.chantier_info_port import ChantierInfoPort, ChantierInfoDTO

# Cross-module import autorise en couche Infrastructure
from modules.chantiers.domain.repositories import ChantierRepository

logger = logging.getLogger(__name__)


class ChantierInfoAdapter(ChantierInfoPort):
    """Implementation concrete du port d'information chantier.

    Utilise le ChantierRepository pour acceder aux noms et statuts.
    Les imports cross-module sont ici dans la couche Infrastructure,
    conformement a Clean Architecture.

    Attributes:
        _chantier_repo: Repository chantiers (interface).
    """

    def __init__(self, chantier_repo: ChantierRepository) -> None:
        """Initialise l'adapter.

        Args:
            chantier_repo: Repository chantiers (interface).
        """
        self._chantier_repo = chantier_repo

    def get_chantier_info(self, chantier_id: int) -> Optional[ChantierInfoDTO]:
        """Recupere les infos basiques d'un chantier.

        Args:
            chantier_id: ID du chantier.

        Returns:
            ChantierInfoDTO ou None si non trouve.
        """
        chantier = self._chantier_repo.find_by_id(chantier_id)
        if chantier is None:
            return None
        return ChantierInfoDTO(
            id=chantier.id,
            nom=chantier.nom,
            statut=str(chantier.statut),
        )

    def get_chantiers_info_batch(
        self, chantier_ids: list[int]
    ) -> Dict[int, ChantierInfoDTO]:
        """Recupere les infos de plusieurs chantiers en batch.

        Args:
            chantier_ids: Liste des IDs de chantiers.

        Returns:
            Dict mapping chantier_id -> ChantierInfoDTO.
        """
        result: Dict[int, ChantierInfoDTO] = {}
        for cid in chantier_ids:
            info = self.get_chantier_info(cid)
            if info is not None:
                result[cid] = info
        return result
