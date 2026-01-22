"""Use Case: Lister les feuilles d'heures avec filtres."""

from math import ceil
from typing import List

from ...domain.entities import FeuilleHeures
from ...domain.repositories import FeuilleHeuresRepository, PointageRepository
from ...domain.value_objects import StatutPointage
from ..dtos import FeuilleHeuresSearchDTO, FeuilleHeuresListDTO, FeuilleHeuresDTO


JOURS_SEMAINE = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


class ListFeuillesHeuresUseCase:
    """
    Liste les feuilles d'heures avec filtres et pagination.
    """

    def __init__(
        self,
        feuille_repo: FeuilleHeuresRepository,
        pointage_repo: PointageRepository,
    ):
        """
        Initialise le use case.

        Args:
            feuille_repo: Repository des feuilles d'heures.
            pointage_repo: Repository des pointages.
        """
        self.feuille_repo = feuille_repo
        self.pointage_repo = pointage_repo

    def execute(self, search_dto: FeuilleHeuresSearchDTO) -> FeuilleHeuresListDTO:
        """
        Exécute la recherche de feuilles d'heures.

        Args:
            search_dto: Les critères de recherche.

        Returns:
            La liste paginée des feuilles.
        """
        # Parse le statut si fourni
        statut = None
        if search_dto.statut:
            statut = StatutPointage.from_string(search_dto.statut)

        # Calcule skip pour la pagination
        skip = (search_dto.page - 1) * search_dto.page_size

        # Recherche
        feuilles, total = self.feuille_repo.search(
            utilisateur_id=search_dto.utilisateur_id,
            annee=search_dto.annee,
            numero_semaine=search_dto.numero_semaine,
            statut=statut,
            date_debut=search_dto.date_debut,
            date_fin=search_dto.date_fin,
            skip=skip,
            limit=search_dto.page_size,
        )

        # Calcule le nombre de pages
        total_pages = ceil(total / search_dto.page_size) if total > 0 else 1

        # Charge les pointages pour chaque feuille et convertit en DTOs
        items = []
        for feuille in feuilles:
            pointages = self.pointage_repo.find_by_utilisateur_and_semaine(
                utilisateur_id=feuille.utilisateur_id,
                semaine_debut=feuille.semaine_debut,
            )
            feuille.pointages = pointages
            items.append(self._to_dto(feuille))

        return FeuilleHeuresListDTO(
            items=items,
            total=total,
            page=search_dto.page,
            page_size=search_dto.page_size,
            total_pages=total_pages,
        )

    def _to_dto(self, feuille: FeuilleHeures) -> FeuilleHeuresDTO:
        """Convertit l'entité en DTO simplifié (sans détails des pointages)."""
        return FeuilleHeuresDTO(
            id=feuille.id,
            utilisateur_id=feuille.utilisateur_id,
            semaine_debut=feuille.semaine_debut,
            semaine_fin=feuille.semaine_fin,
            annee=feuille.annee,
            numero_semaine=feuille.numero_semaine,
            label_semaine=feuille.label_semaine,
            statut_global=feuille.calculer_statut_global().value,
            total_heures_normales=str(feuille.total_heures_normales),
            total_heures_supplementaires=str(feuille.total_heures_supplementaires),
            total_heures=str(feuille.total_heures),
            total_heures_decimal=feuille.total_heures_decimal,
            commentaire_global=feuille.commentaire_global,
            is_complete=feuille.is_complete,
            is_all_validated=feuille.is_all_validated,
            created_at=feuille.created_at,
            updated_at=feuille.updated_at,
            utilisateur_nom=feuille.utilisateur_nom,
            pointages=[],  # Simplifié pour la liste
            variables_paie=[],
            totaux_par_jour={},
            totaux_par_chantier={},
        )
