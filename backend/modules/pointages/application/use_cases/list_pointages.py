"""Use Case: Lister les pointages avec filtres (FDH-04)."""

from math import ceil
from typing import Optional

from shared.application.ports.entity_info_service import EntityInfoService
from ...domain.entities import Pointage
from ...domain.repositories import PointageRepository
from ...domain.value_objects import StatutPointage
from ..dtos import PointageSearchDTO, PointageListDTO, PointageDTO


class ListPointagesUseCase:
    """
    Liste les pointages avec filtres et pagination.

    Implémente FDH-04: Filtre utilisateurs - Dropdown de sélection multi-critères.
    """

    def __init__(
        self,
        pointage_repo: PointageRepository,
        entity_info_service: Optional[EntityInfoService] = None,
    ):
        """
        Initialise le use case.

        Args:
            pointage_repo: Repository des pointages.
            entity_info_service: Service pour enrichir les données (noms utilisateurs/chantiers).
        """
        self.pointage_repo = pointage_repo
        self.entity_info_service = entity_info_service

    def execute(self, search_dto: PointageSearchDTO) -> PointageListDTO:
        """
        Exécute la recherche de pointages.

        Args:
            search_dto: Les critères de recherche.

        Returns:
            La liste paginée des pointages.
        """
        # Parse le statut si fourni
        statut = None
        if search_dto.statut:
            statut = StatutPointage.from_string(search_dto.statut)

        # Calcule skip pour la pagination
        skip = (search_dto.page - 1) * search_dto.page_size

        # Recherche
        pointages, total = self.pointage_repo.search(
            utilisateur_id=search_dto.utilisateur_id,
            chantier_id=search_dto.chantier_id,
            date_debut=search_dto.date_debut,
            date_fin=search_dto.date_fin,
            statut=statut,
            skip=skip,
            limit=search_dto.page_size,
        )

        # Enrichir les pointages avec les noms utilisateurs et chantiers
        if self.entity_info_service and pointages:
            self._enrich_pointages(pointages)

        # Calcule le nombre de pages
        total_pages = ceil(total / search_dto.page_size) if total > 0 else 1

        # Convertit en DTOs
        items = [self._to_dto(p) for p in pointages]

        return PointageListDTO(
            items=items,
            total=total,
            page=search_dto.page,
            page_size=search_dto.page_size,
            total_pages=total_pages,
        )

    def _to_dto(self, pointage: Pointage) -> PointageDTO:
        """Convertit l'entité en DTO."""
        return PointageDTO(
            id=pointage.id,
            utilisateur_id=pointage.utilisateur_id,
            chantier_id=pointage.chantier_id,
            date_pointage=pointage.date_pointage,
            heures_normales=str(pointage.heures_normales),
            heures_supplementaires=str(pointage.heures_supplementaires),
            total_heures=str(pointage.total_heures),
            total_heures_decimal=pointage.total_heures_decimal,
            statut=pointage.statut.value,
            commentaire=pointage.commentaire,
            signature_utilisateur=pointage.signature_utilisateur,
            signature_date=pointage.signature_date,
            validateur_id=pointage.validateur_id,
            validation_date=pointage.validation_date,
            motif_rejet=pointage.motif_rejet,
            affectation_id=pointage.affectation_id,
            created_by=pointage.created_by,
            created_at=pointage.created_at,
            updated_at=pointage.updated_at,
            utilisateur_nom=pointage.utilisateur_nom,
            chantier_nom=pointage.chantier_nom,
            chantier_couleur=pointage.chantier_couleur,
        )

    def _enrich_pointages(self, pointages: list) -> None:
        """Enrichit les pointages avec les noms utilisateurs et chantiers.

        Args:
            pointages: Liste des pointages à enrichir (modifiés in-place).
        """
        # Collecter les IDs uniques
        user_ids = {p.utilisateur_id for p in pointages}
        chantier_ids = {p.chantier_id for p in pointages}

        # Récupérer les infos en batch (cache local pour éviter requêtes répétées)
        user_infos = {}
        for uid in user_ids:
            info = self.entity_info_service.get_user_info(uid)
            if info:
                user_infos[uid] = info

        chantier_infos = {}
        for cid in chantier_ids:
            info = self.entity_info_service.get_chantier_info(cid)
            if info:
                chantier_infos[cid] = info

        # Enrichir chaque pointage
        for pointage in pointages:
            user_info = user_infos.get(pointage.utilisateur_id)
            if user_info:
                pointage.utilisateur_nom = user_info.nom

            chantier_info = chantier_infos.get(pointage.chantier_id)
            if chantier_info:
                pointage.chantier_nom = chantier_info.nom
                pointage.chantier_couleur = chantier_info.couleur
