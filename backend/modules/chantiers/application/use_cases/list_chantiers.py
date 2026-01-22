"""Use Case ListChantiers - Liste des chantiers avec filtres."""

from typing import Optional

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

    def __init__(self, chantier_repo: ChantierRepository):
        """
        Initialise le use case.

        Args:
            chantier_repo: Repository chantiers (interface).
        """
        self.chantier_repo = chantier_repo

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
        # Déterminer quel filtre appliquer (par ordre de priorité)
        if search:
            statut_obj = None
            if statut:
                statut_obj = StatutChantier.from_string(statut)
            chantiers = self.chantier_repo.search(
                query=search,
                statut=statut_obj,
                skip=skip,
                limit=limit,
            )
            total = len(chantiers)  # Approximation, idéalement count séparé

        elif responsable_id is not None:
            chantiers = self.chantier_repo.find_by_responsable(
                user_id=responsable_id,
                skip=skip,
                limit=limit,
            )
            total = len(chantiers)

        elif conducteur_id is not None:
            chantiers = self.chantier_repo.find_by_conducteur(
                conducteur_id=conducteur_id,
                skip=skip,
                limit=limit,
            )
            total = len(chantiers)

        elif chef_chantier_id is not None:
            chantiers = self.chantier_repo.find_by_chef_chantier(
                chef_id=chef_chantier_id,
                skip=skip,
                limit=limit,
            )
            total = len(chantiers)

        elif statut:
            statut_obj = StatutChantier.from_string(statut)
            chantiers = self.chantier_repo.find_by_statut(
                statut=statut_obj,
                skip=skip,
                limit=limit,
            )
            total = len(chantiers)

        elif actifs_uniquement:
            chantiers = self.chantier_repo.find_active(
                skip=skip,
                limit=limit,
            )
            total = len(chantiers)

        else:
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
