"""Use Case ListChantiers - Liste des chantiers avec filtres."""

import logging
from typing import Optional, List

from ...domain.entities import Chantier

logger = logging.getLogger(__name__)
from ...domain.repositories import ChantierRepository
from ...domain.value_objects import StatutChantier
from ..dtos import ChantierDTO, ChantierListDTO


class ListChantiersUseCase:
    """
    Cas d'utilisation : Liste des chantiers avec pagination et filtres.

    Permet de lister tous les chantiers ou de filtrer par statut,
    conducteur, chef de chantier, ou recherche textuelle.

    Attributes:
        chantier_repo: Repository pour accéder aux chantiers.
    """

    def __init__(self, chantier_repo: ChantierRepository) -> None:
        """
        Initialise le use case.

        Args:
            chantier_repo: Repository chantiers (interface).
        """
        self.chantier_repo = chantier_repo

    def _paginate(
        self, all_items: List[Chantier], skip: int, limit: int
    ) -> tuple[List[Chantier], int]:
        """
        Pagine une liste de chantiers et retourne le total.

        Args:
            all_items: Liste complète des chantiers.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum d'éléments à retourner.

        Returns:
            Tuple (chantiers_paginés, total).
        """
        total = len(all_items)
        paginated = all_items[skip : skip + limit]
        return paginated, total

    def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        statut: Optional[str] = None,
        conducteur_id: Optional[int] = None,
        chef_chantier_id: Optional[int] = None,
        responsable_id: Optional[int] = None,
        actifs_uniquement: bool = False,
        search: Optional[str] = None,
    ) -> ChantierListDTO:
        """
        Liste les chantiers avec filtres optionnels.

        Args:
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum d'éléments à retourner.
            statut: Filtre par statut (ouvert, en_cours, receptionne, ferme).
            conducteur_id: Filtre par ID du conducteur.
            chef_chantier_id: Filtre par ID du chef de chantier.
            responsable_id: Filtre par ID du responsable (conducteur OU chef).
            actifs_uniquement: Si True, ne retourne que les chantiers actifs.
            search: Recherche textuelle par nom ou code.

        Returns:
            ChantierListDTO avec la liste paginée.
        """
        # Logging structured (GAP-CHT-006)
        logger.info(
            "Use case execution started",
            extra={
                "event": "chantier.use_case.started",
                "use_case": "ListChantiersUseCase",
                "operation": "list",
                "skip": skip,
                "limit": limit,
                "filters": {
                    "statut": statut,
                    "conducteur_id": conducteur_id,
                    "chef_chantier_id": chef_chantier_id,
                    "responsable_id": responsable_id,
                    "actifs_uniquement": actifs_uniquement,
                    "search": search,
                }
            }
        )

        try:
            # Cas par défaut: pas de filtre -> utiliser count() du repository
            if not (search or responsable_id or conducteur_id or chef_chantier_id or statut or actifs_uniquement):
                chantiers = self.chantier_repo.find_all(
                    skip=skip,
                    limit=limit,
                )
                total = self.chantier_repo.count()
                return ChantierListDTO(
                    chantiers=[ChantierDTO.from_entity(c) for c in chantiers],
                    total=total,
                    skip=skip,
                    limit=limit,
                )

            # Pour les filtres, récupérer tous les résultats puis paginer
            # Note: Acceptable pour le volume PME (<500 chantiers)
            # À optimiser si volume > 1000 avec count_* dans le repository
            max_results = 10000  # Limite de sécurité

            if search:
                statut_obj = None
                if statut:
                    statut_obj = StatutChantier.from_string(statut)
                all_results = self.chantier_repo.search(
                    query=search,
                    statut=statut_obj,
                    skip=0,
                    limit=max_results,
                )

            elif responsable_id is not None:
                all_results = self.chantier_repo.find_by_responsable(
                    user_id=responsable_id,
                    skip=0,
                    limit=max_results,
                )

            elif conducteur_id is not None:
                all_results = self.chantier_repo.find_by_conducteur(
                    conducteur_id=conducteur_id,
                    skip=0,
                    limit=max_results,
                )

            elif chef_chantier_id is not None:
                all_results = self.chantier_repo.find_by_chef_chantier(
                    chef_id=chef_chantier_id,
                    skip=0,
                    limit=max_results,
                )

            elif statut:
                statut_obj = StatutChantier.from_string(statut)
                all_results = self.chantier_repo.find_by_statut(
                    statut=statut_obj,
                    skip=0,
                    limit=max_results,
                )

            elif actifs_uniquement:
                all_results = self.chantier_repo.find_active(
                    skip=0,
                    limit=max_results,
                )

            else:
                all_results = []

            # Paginer les résultats
            chantiers, total = self._paginate(all_results, skip, limit)

            result = ChantierListDTO(
                chantiers=[ChantierDTO.from_entity(c) for c in chantiers],
                total=total,
                skip=skip,
                limit=limit,
            )

            logger.info(
                "Use case execution succeeded",
                extra={
                    "event": "chantier.use_case.succeeded",
                    "use_case": "ListChantiersUseCase",
                    "total_results": total,
                    "returned_count": len(chantiers),
                }
            )

            return result

        except Exception as e:
            logger.error(
                "Use case execution failed",
                extra={
                    "event": "chantier.use_case.failed",
                    "use_case": "ListChantiersUseCase",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
            )
            raise
