"""Use Case ListFormulaires - Liste des formulaires (FOR-10)."""

from dataclasses import dataclass
from datetime import date
from typing import Optional, List

from ...domain.repositories import FormulaireRempliRepository
from ...domain.value_objects import StatutFormulaire
from ..dtos import FormulaireRempliDTO


@dataclass
class ListFormulairesResult:
    """Resultat de la liste des formulaires."""

    formulaires: List[FormulaireRempliDTO]
    total: int
    skip: int
    limit: int


class ListFormulairesUseCase:
    """
    Use Case pour lister les formulaires.

    Implemente FOR-10 - Liste par chantier.
    """

    def __init__(self, formulaire_repo: FormulaireRempliRepository):
        """
        Initialise le use case.

        Args:
            formulaire_repo: Repository des formulaires.
        """
        self._formulaire_repo = formulaire_repo

    def execute(
        self,
        chantier_id: Optional[int] = None,
        template_id: Optional[int] = None,
        user_id: Optional[int] = None,
        statut: Optional[str] = None,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> ListFormulairesResult:
        """
        Execute la liste des formulaires.

        Args:
            chantier_id: Filtrer par chantier (optionnel).
            template_id: Filtrer par template (optionnel).
            user_id: Filtrer par utilisateur (optionnel).
            statut: Filtrer par statut (optionnel).
            date_debut: Date de debut (optionnel).
            date_fin: Date de fin (optionnel).
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum d'elements.

        Returns:
            Le resultat de la recherche.
        """
        statut_enum = None
        if statut:
            statut_enum = StatutFormulaire.from_string(statut)

        formulaires, total = self._formulaire_repo.search(
            chantier_id=chantier_id,
            template_id=template_id,
            user_id=user_id,
            statut=statut_enum,
            date_debut=date_debut,
            date_fin=date_fin,
            skip=skip,
            limit=limit,
        )

        return ListFormulairesResult(
            formulaires=[FormulaireRempliDTO.from_entity(f) for f in formulaires],
            total=total,
            skip=skip,
            limit=limit,
        )

    def execute_by_chantier(
        self,
        chantier_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FormulaireRempliDTO]:
        """
        Liste les formulaires d'un chantier (FOR-10).

        Args:
            chantier_id: ID du chantier.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum d'elements.

        Returns:
            Liste des formulaires.
        """
        formulaires = self._formulaire_repo.find_by_chantier(
            chantier_id, skip, limit
        )
        return [FormulaireRempliDTO.from_entity(f) for f in formulaires]

    def execute_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FormulaireRempliDTO]:
        """
        Liste les formulaires d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum d'elements.

        Returns:
            Liste des formulaires.
        """
        formulaires = self._formulaire_repo.find_by_user(user_id, skip, limit)
        return [FormulaireRempliDTO.from_entity(f) for f in formulaires]

    def count_by_chantier(self, chantier_id: int) -> int:
        """
        Compte les formulaires d'un chantier.

        Args:
            chantier_id: ID du chantier.

        Returns:
            Nombre de formulaires.
        """
        return self._formulaire_repo.count_by_chantier(chantier_id)
