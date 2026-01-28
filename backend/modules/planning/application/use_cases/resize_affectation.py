"""Use Case ResizeAffectationUseCase - Redimensionner une affectation.

Extrait la logique métier de redimensionnement d'affectation depuis le controller
pour une meilleure séparation des responsabilités et testabilité.
"""

import logging
from datetime import date, timedelta
from typing import List

from ...domain.entities import Affectation
from ...domain.repositories import AffectationRepository
from ...domain.value_objects import TypeAffectation
from .exceptions import AffectationConflictError, AffectationNotFoundError


logger = logging.getLogger(__name__)


class ResizeAffectationUseCase:
    """
    Use case pour redimensionner une affectation.

    Permet d'étendre ou réduire la durée d'une affectation en créant
    de nouvelles affectations pour les jours manquants adjacents.

    Le resize ne fait QUE de l'extension (ajout de jours adjacents).
    Pour supprimer des affectations, l'utilisateur doit les supprimer
    manuellement. Cela évite les suppressions accidentelles.

    Attributes:
        affectation_repo: Repository des affectations.
    """

    def __init__(self, affectation_repo: AffectationRepository):
        """
        Initialise le use case.

        Args:
            affectation_repo: Repository des affectations (interface).
        """
        self.affectation_repo = affectation_repo

    def execute(
        self,
        affectation_id: int,
        date_debut: date,
        date_fin: date,
        current_user_id: int,
    ) -> List[Affectation]:
        """
        Redimensionne une affectation en ajoutant des jours adjacents.

        Étend ou réduit la plage d'une affectation. Crée de nouvelles
        affectations pour les jours manquants adjacents à l'affectation
        de référence.

        Args:
            affectation_id: ID de l'affectation de référence.
            date_debut: Nouvelle date de début de la plage.
            date_fin: Nouvelle date de fin de la plage.
            current_user_id: ID de l'utilisateur modificateur.

        Returns:
            Liste des affectations dans la nouvelle plage (même chantier).

        Raises:
            AffectationNotFoundError: Si l'affectation n'est pas trouvée.
            AffectationConflictError: Si conflit avec affectation existante.

        Example:
            >>> use_case = ResizeAffectationUseCase(affectation_repo)
            >>> affectations = use_case.execute(
            ...     affectation_id=1,
            ...     date_debut=date(2024, 1, 1),
            ...     date_fin=date(2024, 1, 5),
            ...     current_user_id=2,
            ... )
        """
        logger.info(
            f"Resize affectation: id={affectation_id}, "
            f"new_dates={date_debut} -> {date_fin}, "
            f"by={current_user_id}"
        )

        # Récupérer l'affectation de référence
        affectation = self.affectation_repo.find_by_id(affectation_id)
        if not affectation:
            raise AffectationNotFoundError(affectation_id)

        # Générer les dates à ajouter (uniquement adjacentes)
        dates_to_add = self._calculate_adjacent_dates(
            affectation.date,
            date_debut,
            date_fin,
        )

        # Récupérer les affectations existantes pour éviter les doublons
        existing_dates = self._get_existing_dates(
            affectation.utilisateur_id,
            affectation.chantier_id,
            min(date_debut, affectation.date),
            max(date_fin, affectation.date),
        )

        # Exclure les dates qui existent déjà
        dates_to_add = dates_to_add - existing_dates

        # Vérifier les conflits (autres chantiers)
        self._check_conflicts(affectation.utilisateur_id, dates_to_add)

        # Créer les nouvelles affectations
        created_count = self._create_affectations(
            affectation,
            dates_to_add,
            current_user_id,
        )

        # Récupérer toutes les affectations dans la nouvelle plage
        result_affectations = self._get_final_affectations(
            affectation.utilisateur_id,
            affectation.chantier_id,
            date_debut,
            date_fin,
        )

        logger.info(
            f"Resize complete: {created_count} created, "
            f"{len(result_affectations)} total in range"
        )

        return result_affectations

    def _calculate_adjacent_dates(
        self,
        affectation_date: date,
        date_debut: date,
        date_fin: date,
    ) -> set[date]:
        """
        Calcule les dates adjacentes à ajouter.

        Génère uniquement les dates ADJACENTES à l'affectation d'origine,
        pas tous les trous dans la plage.

        Args:
            affectation_date: Date de l'affectation de référence.
            date_debut: Nouvelle date de début.
            date_fin: Nouvelle date de fin.

        Returns:
            Ensemble des dates à ajouter.
        """
        dates_to_add = set()

        # Extension vers la droite (après l'affectation)
        if date_fin > affectation_date:
            current_date = affectation_date + timedelta(days=1)
            while current_date <= date_fin:
                dates_to_add.add(current_date)
                current_date += timedelta(days=1)

        # Extension vers la gauche (avant l'affectation)
        if date_debut < affectation_date:
            current_date = affectation_date - timedelta(days=1)
            while current_date >= date_debut:
                dates_to_add.add(current_date)
                current_date -= timedelta(days=1)

        return dates_to_add

    def _get_existing_dates(
        self,
        utilisateur_id: int,
        chantier_id: int,
        min_date: date,
        max_date: date,
    ) -> set[date]:
        """
        Récupère les dates déjà affectées pour un utilisateur/chantier.

        Args:
            utilisateur_id: ID de l'utilisateur.
            chantier_id: ID du chantier.
            min_date: Date minimale.
            max_date: Date maximale.

        Returns:
            Ensemble des dates déjà affectées.
        """
        existing_affectations = self.affectation_repo.find_by_utilisateur(
            utilisateur_id,
            min_date,
            max_date,
        )

        # Filtrer pour ne garder que celles du même chantier
        same_chantier_affectations = [
            a for a in existing_affectations
            if a.chantier_id == chantier_id
        ]

        return {a.date for a in same_chantier_affectations}

    def _check_conflicts(
        self,
        utilisateur_id: int,
        dates_to_check: set[date],
    ) -> None:
        """
        Vérifie les conflits sur les dates à ajouter.

        Lève une exception si l'utilisateur a déjà une affectation
        (sur un autre chantier) pour l'une des dates.

        Args:
            utilisateur_id: ID de l'utilisateur.
            dates_to_check: Dates à vérifier.

        Raises:
            AffectationConflictError: Si conflit détecté.
        """
        for date_to_add in dates_to_check:
            if self.affectation_repo.exists_for_utilisateur_and_date(
                utilisateur_id, date_to_add
            ):
                raise AffectationConflictError(utilisateur_id, date_to_add)

    def _create_affectations(
        self,
        reference_affectation: Affectation,
        dates_to_add: set[date],
        current_user_id: int,
    ) -> int:
        """
        Crée les nouvelles affectations pour les dates manquantes.

        Args:
            reference_affectation: Affectation de référence (pour copier les attributs).
            dates_to_add: Dates pour lesquelles créer des affectations.
            current_user_id: ID de l'utilisateur créateur.

        Returns:
            Nombre d'affectations créées.
        """
        created_count = 0

        for date_to_add in sorted(dates_to_add):
            new_affectation = Affectation(
                utilisateur_id=reference_affectation.utilisateur_id,
                chantier_id=reference_affectation.chantier_id,
                date=date_to_add,
                heure_debut=reference_affectation.heure_debut,
                heure_fin=reference_affectation.heure_fin,
                note=reference_affectation.note,
                type_affectation=TypeAffectation.UNIQUE,
                created_by=current_user_id,
            )
            self.affectation_repo.save(new_affectation)
            created_count += 1

        return created_count

    def _get_final_affectations(
        self,
        utilisateur_id: int,
        chantier_id: int,
        date_debut: date,
        date_fin: date,
    ) -> List[Affectation]:
        """
        Récupère toutes les affectations dans la plage finale.

        Args:
            utilisateur_id: ID de l'utilisateur.
            chantier_id: ID du chantier.
            date_debut: Date de début de la plage.
            date_fin: Date de fin de la plage.

        Returns:
            Liste des affectations du même chantier dans la plage.
        """
        final_affectations = self.affectation_repo.find_by_utilisateur(
            utilisateur_id,
            date_debut,
            date_fin,
        )

        # Filtrer pour ne garder que celles du même chantier
        return [
            a for a in final_affectations
            if a.chantier_id == chantier_id
        ]
