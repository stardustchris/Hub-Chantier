"""Use Case GetPlanning - Recuperation du planning."""

from typing import List, Optional, Dict, Any, Callable

from ...domain.entities import Affectation
from ...domain.repositories import AffectationRepository
from ..dtos import AffectationDTO, PlanningFiltersDTO


class GetPlanningUseCase:
    """
    Cas d'utilisation : Recuperation du planning.

    Recupere les affectations selon des filtres et le role de l'utilisateur.
    - Admin/Conducteur : voient tout le planning.
    - Chef de chantier : voit ses chantiers uniquement.
    - Compagnon : voit uniquement son planning.

    Selon CDC Section 5 - Planning Operationnel (PLN-01 a PLN-03).

    Attributes:
        affectation_repo: Repository pour acceder aux affectations.
        get_user_info: Fonction pour recuperer les infos utilisateur.
        get_chantier_info: Fonction pour recuperer les infos chantier.
        get_user_chantiers: Fonction pour recuperer les chantiers d'un chef.
    """

    def __init__(
        self,
        affectation_repo: AffectationRepository,
        get_user_info: Optional[Callable[[int], Dict[str, Any]]] = None,
        get_chantier_info: Optional[Callable[[int], Dict[str, Any]]] = None,
        get_user_chantiers: Optional[Callable[[int], List[int]]] = None,
    ):
        """
        Initialise le use case.

        Args:
            affectation_repo: Repository affectations (interface).
            get_user_info: Fonction pour recuperer nom, couleur, metier d'un user.
            get_chantier_info: Fonction pour recuperer nom, couleur d'un chantier.
            get_user_chantiers: Fonction pour recuperer les IDs chantiers d'un chef.
        """
        self.affectation_repo = affectation_repo
        self.get_user_info = get_user_info
        self.get_chantier_info = get_chantier_info
        self.get_user_chantiers = get_user_chantiers

    def execute(
        self,
        filters: PlanningFiltersDTO,
        current_user_id: int,
        current_user_role: str,
    ) -> List[AffectationDTO]:
        """
        Execute la recuperation du planning.

        Args:
            filters: Les filtres a appliquer.
            current_user_id: ID de l'utilisateur qui consulte.
            current_user_role: Role de l'utilisateur (admin, conducteur, etc.).

        Returns:
            Liste des affectations sous forme de DTOs enrichis.

        Example:
            >>> dtos = use_case.execute(filters, user_id=1, role="admin")
            >>> for dto in dtos:
            ...     print(f"{dto.utilisateur_nom} -> {dto.chantier_nom}")
        """
        # Recuperer les affectations de base
        affectations = self._get_filtered_affectations(
            filters, current_user_id, current_user_role
        )

        # Enrichir avec les infos utilisateur et chantier
        dtos = self._enrich_affectations(affectations)

        # Filtrer par metier si demande
        if filters.has_metier_filter:
            dtos = [
                dto for dto in dtos
                if dto.utilisateur_metier in filters.metiers
            ]

        return dtos

    def _get_filtered_affectations(
        self,
        filters: PlanningFiltersDTO,
        current_user_id: int,
        current_user_role: str,
    ) -> List[Affectation]:
        """
        Recupere les affectations selon les filtres et le role.

        Args:
            filters: Les filtres a appliquer.
            current_user_id: ID de l'utilisateur courant.
            current_user_role: Role de l'utilisateur.

        Returns:
            Liste des affectations filtrees.
        """
        # Recuperer toutes les affectations de la periode
        all_affectations = self.affectation_repo.find_by_date_range(
            filters.date_debut, filters.date_fin
        )

        # Appliquer le filtre de role
        affectations = self._filter_by_role(
            all_affectations, current_user_id, current_user_role
        )

        # Appliquer le filtre utilisateur
        if filters.has_utilisateur_filter:
            affectations = [
                a for a in affectations
                if a.utilisateur_id in filters.utilisateur_ids
            ]

        # Appliquer le filtre chantier
        if filters.has_chantier_filter:
            affectations = [
                a for a in affectations
                if a.chantier_id in filters.chantier_ids
            ]

        return affectations

    def _filter_by_role(
        self,
        affectations: List[Affectation],
        current_user_id: int,
        current_user_role: str,
    ) -> List[Affectation]:
        """
        Filtre les affectations selon le role de l'utilisateur.

        Args:
            affectations: Liste des affectations a filtrer.
            current_user_id: ID de l'utilisateur courant.
            current_user_role: Role de l'utilisateur.

        Returns:
            Liste filtree selon les droits.
        """
        role_lower = current_user_role.lower()

        # Admin et conducteur voient tout
        if role_lower in ("admin", "administrateur", "conducteur", "conducteur_travaux"):
            return affectations

        # Chef de chantier voit ses chantiers
        if role_lower in ("chef_chantier", "chef_equipe"):
            if self.get_user_chantiers:
                chantier_ids = self.get_user_chantiers(current_user_id)
                return [a for a in affectations if a.chantier_id in chantier_ids]
            # Sans fonction, on retourne tout (fallback)
            return affectations

        # Compagnon voit uniquement son planning
        if role_lower in ("compagnon", "ouvrier"):
            return [a for a in affectations if a.utilisateur_id == current_user_id]

        # Role inconnu : ne voir que son planning (securite)
        return [a for a in affectations if a.utilisateur_id == current_user_id]

    def _enrich_affectations(
        self,
        affectations: List[Affectation],
    ) -> List[AffectationDTO]:
        """
        Enrichit les affectations avec les infos utilisateur et chantier.

        Args:
            affectations: Liste des affectations.

        Returns:
            Liste de DTOs enrichis.
        """
        # Cache pour eviter les appels multiples
        user_cache: Dict[int, Dict[str, Any]] = {}
        chantier_cache: Dict[int, Dict[str, Any]] = {}

        dtos = []
        for affectation in affectations:
            # Recuperer infos utilisateur
            user_info = self._get_cached_user_info(
                affectation.utilisateur_id, user_cache
            )

            # Recuperer infos chantier
            chantier_info = self._get_cached_chantier_info(
                affectation.chantier_id, chantier_cache
            )

            # Creer le DTO enrichi
            dto = AffectationDTO.from_entity(
                affectation,
                utilisateur_nom=user_info.get("nom"),
                utilisateur_couleur=user_info.get("couleur"),
                utilisateur_metier=user_info.get("metier"),
                chantier_nom=chantier_info.get("nom"),
                chantier_couleur=chantier_info.get("couleur"),
            )
            dtos.append(dto)

        return dtos

    def _get_cached_user_info(
        self,
        user_id: int,
        cache: Dict[int, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Recupere les infos utilisateur avec cache.

        Args:
            user_id: ID de l'utilisateur.
            cache: Cache des infos utilisateur.

        Returns:
            Dictionnaire avec nom, couleur, metier.
        """
        if user_id in cache:
            return cache[user_id]

        info = {}
        if self.get_user_info:
            info = self.get_user_info(user_id) or {}

        cache[user_id] = info
        return info

    def _get_cached_chantier_info(
        self,
        chantier_id: int,
        cache: Dict[int, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Recupere les infos chantier avec cache.

        Args:
            chantier_id: ID du chantier.
            cache: Cache des infos chantier.

        Returns:
            Dictionnaire avec nom, couleur.
        """
        if chantier_id in cache:
            return cache[chantier_id]

        info = {}
        if self.get_chantier_info:
            info = self.get_chantier_info(chantier_id) or {}

        cache[chantier_id] = info
        return info
