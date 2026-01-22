"""Use Case GetNonPlanifies - Recuperation des utilisateurs non planifies."""

from datetime import date
from typing import List, Optional, Callable

from ...domain.repositories import AffectationRepository


class GetNonPlanifiesUseCase:
    """
    Cas d'utilisation : Recuperation des utilisateurs non planifies.

    Identifie les utilisateurs actifs qui n'ont pas d'affectation
    sur une periode donnee.

    Selon CDC Section 5 - Planning Operationnel (PLN-10).

    Attributes:
        affectation_repo: Repository pour acceder aux affectations.
        get_active_user_ids: Fonction pour recuperer les IDs des utilisateurs actifs.
    """

    def __init__(
        self,
        affectation_repo: AffectationRepository,
        get_active_user_ids: Optional[Callable[[], List[int]]] = None,
    ):
        """
        Initialise le use case.

        Args:
            affectation_repo: Repository affectations (interface).
            get_active_user_ids: Fonction pour recuperer les utilisateurs actifs.
        """
        self.affectation_repo = affectation_repo
        self.get_active_user_ids = get_active_user_ids

    def execute(self, date_debut: date, date_fin: date) -> List[int]:
        """
        Execute la recuperation des utilisateurs non planifies.

        Args:
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Liste des IDs utilisateurs sans affectation sur la periode.

        Raises:
            ValueError: Si la plage de dates est invalide.

        Example:
            >>> user_ids = use_case.execute(
            ...     date(2026, 1, 20),
            ...     date(2026, 1, 24)
            ... )
            >>> print(f"{len(user_ids)} utilisateurs non planifies")
        """
        # Valider les dates
        if date_fin < date_debut:
            raise ValueError(
                f"La date de fin ({date_fin}) doit etre posterieure "
                f"ou egale a la date de debut ({date_debut})"
            )

        # Utiliser la methode du repository si disponible
        non_planifies = self.affectation_repo.find_non_planifies(date_debut, date_fin)

        # Si la methode repository retourne quelque chose, l'utiliser
        if non_planifies:
            return non_planifies

        # Sinon, calculer manuellement si on a acces aux utilisateurs actifs
        if self.get_active_user_ids:
            return self._calculate_non_planifies(date_debut, date_fin)

        return []

    def _calculate_non_planifies(self, date_debut: date, date_fin: date) -> List[int]:
        """
        Calcule manuellement les utilisateurs non planifies.

        Args:
            date_debut: Date de debut de la periode.
            date_fin: Date de fin de la periode.

        Returns:
            Liste des IDs utilisateurs sans affectation.
        """
        # Recuperer tous les utilisateurs actifs
        all_active_ids = set(self.get_active_user_ids())

        # Recuperer toutes les affectations de la periode
        affectations = self.affectation_repo.find_by_date_range(date_debut, date_fin)

        # Extraire les utilisateurs qui ont au moins une affectation
        planifies_ids = set(a.utilisateur_id for a in affectations)

        # Retourner la difference
        non_planifies = all_active_ids - planifies_ids

        return list(non_planifies)

    def execute_for_day(self, target_date: date) -> List[int]:
        """
        Recupere les utilisateurs non planifies pour une journee.

        Methode de commodite pour le cas d'usage courant.

        Args:
            target_date: La date cible.

        Returns:
            Liste des IDs utilisateurs disponibles ce jour.

        Example:
            >>> user_ids = use_case.execute_for_day(date(2026, 1, 22))
        """
        return self.execute(target_date, target_date)
