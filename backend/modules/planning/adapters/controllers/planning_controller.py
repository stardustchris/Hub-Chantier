"""PlanningController - Gestion des requetes de planning."""

import logging
from datetime import date
from typing import Dict, Any, List, Optional

from ...domain.entities import Affectation
from ...application.use_cases import (
    CreateAffectationUseCase,
    UpdateAffectationUseCase,
    DeleteAffectationUseCase,
    GetPlanningUseCase,
    DuplicateAffectationsUseCase,
    GetNonPlanifiesUseCase,
)
from ...application.dtos import (
    CreateAffectationDTO,
    UpdateAffectationDTO,
    PlanningFiltersDTO,
    DuplicateAffectationsDTO,
    AffectationDTO,
)
from .planning_schemas import (
    CreateAffectationRequest,
    UpdateAffectationRequest,
    PlanningFiltersRequest,
    DuplicateAffectationsRequest,
)
from ..presenters import AffectationPresenter


logger = logging.getLogger(__name__)


class PlanningController:
    """
    Controller pour les operations de planning.

    Fait le pont entre les requetes HTTP et les Use Cases.
    Convertit les donnees brutes en DTOs et formate les reponses.

    Selon CDC Section 5 - Planning Operationnel (PLN-01 a PLN-28).

    Attributes:
        create_affectation_uc: Use case de creation d'affectation.
        update_affectation_uc: Use case de mise a jour d'affectation.
        delete_affectation_uc: Use case de suppression d'affectation.
        get_planning_uc: Use case de recuperation du planning.
        duplicate_affectations_uc: Use case de duplication d'affectations.
        get_non_planifies_uc: Use case de recuperation des non planifies.
        presenter: Presenter pour enrichir les reponses (optionnel).
    """

    def __init__(
        self,
        create_affectation_uc: CreateAffectationUseCase,
        update_affectation_uc: UpdateAffectationUseCase,
        delete_affectation_uc: DeleteAffectationUseCase,
        get_planning_uc: GetPlanningUseCase,
        duplicate_affectations_uc: DuplicateAffectationsUseCase,
        get_non_planifies_uc: GetNonPlanifiesUseCase,
        presenter: Optional[AffectationPresenter] = None,
    ):
        """
        Initialise le controller.

        Args:
            create_affectation_uc: Use case de creation.
            update_affectation_uc: Use case de mise a jour.
            delete_affectation_uc: Use case de suppression.
            get_planning_uc: Use case de recuperation planning.
            duplicate_affectations_uc: Use case de duplication.
            get_non_planifies_uc: Use case des non planifies.
            presenter: Presenter pour enrichir les donnees (optionnel).
        """
        self.create_affectation_uc = create_affectation_uc
        self.update_affectation_uc = update_affectation_uc
        self.delete_affectation_uc = delete_affectation_uc
        self.get_planning_uc = get_planning_uc
        self.duplicate_affectations_uc = duplicate_affectations_uc
        self.get_non_planifies_uc = get_non_planifies_uc
        self.presenter = presenter

    def _dto_to_response(self, dto: AffectationDTO) -> Dict[str, Any]:
        """
        Convertit un AffectationDTO en dictionnaire de reponse.

        Args:
            dto: Le DTO a convertir.

        Returns:
            Dictionnaire compatible avec AffectationResponse.
        """
        return {
            "id": dto.id,
            "utilisateur_id": dto.utilisateur_id,
            "chantier_id": dto.chantier_id,
            "date": dto.date,
            "heure_debut": dto.heure_debut,
            "heure_fin": dto.heure_fin,
            "note": dto.note,
            "type_affectation": dto.type_affectation,
            "jours_recurrence": dto.jours_recurrence,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
            "created_by": dto.created_by,
            "utilisateur_nom": dto.utilisateur_nom,
            "utilisateur_couleur": dto.utilisateur_couleur,
            "utilisateur_metier": dto.utilisateur_metier,
            "chantier_nom": dto.chantier_nom,
            "chantier_couleur": dto.chantier_couleur,
        }

    def _entity_to_response(self, entity: Affectation) -> Dict[str, Any]:
        """
        Convertit une entite Affectation en dictionnaire de reponse.

        Args:
            entity: L'entite Affectation a convertir.

        Returns:
            Dictionnaire compatible avec AffectationResponse.
        """
        # Convertir les jours de recurrence en liste d'entiers
        jours_recurrence = None
        if entity.jours_recurrence:
            jours_recurrence = [jour.value for jour in entity.jours_recurrence]

        return {
            "id": entity.id,
            "utilisateur_id": entity.utilisateur_id,
            "chantier_id": entity.chantier_id,
            "date": entity.date.isoformat(),
            "heure_debut": str(entity.heure_debut) if entity.heure_debut else None,
            "heure_fin": str(entity.heure_fin) if entity.heure_fin else None,
            "note": entity.note,
            "type_affectation": entity.type_affectation.value,
            "jours_recurrence": jours_recurrence,
            "created_at": entity.created_at.isoformat() if entity.created_at else "",
            "updated_at": entity.updated_at.isoformat() if entity.updated_at else "",
            "created_by": entity.created_by,
            "utilisateur_nom": None,
            "utilisateur_couleur": None,
            "utilisateur_metier": None,
            "chantier_nom": None,
            "chantier_couleur": None,
        }

    def create(
        self,
        request: CreateAffectationRequest,
        current_user_id: int,
    ) -> Dict[str, Any]:
        """
        Cree une ou plusieurs affectations.

        Args:
            request: Donnees de creation.
            current_user_id: ID de l'utilisateur createur.

        Returns:
            Dictionnaire de la premiere affectation creee.

        Raises:
            AffectationConflictError: Si conflit avec affectation existante.
            InvalidDateRangeError: Si plage de dates invalide.
            ValueError: Si donnees invalides.

        Example:
            >>> result = controller.create(request, current_user_id=1)
        """
        logger.info(
            f"Creation affectation: user={request.utilisateur_id}, "
            f"chantier={request.chantier_id}, date={request.date}, "
            f"created_by={current_user_id}"
        )

        # Convertir la requete en DTO
        dto = CreateAffectationDTO(
            utilisateur_id=request.utilisateur_id,
            chantier_id=request.chantier_id,
            date=request.date,
            heure_debut=request.heure_debut,
            heure_fin=request.heure_fin,
            note=request.note,
            type_affectation=request.type_affectation,
            jours_recurrence=request.jours_recurrence,
            date_fin_recurrence=request.date_fin_recurrence,
        )

        # Executer le use case
        affectations = self.create_affectation_uc.execute(dto, current_user_id)

        logger.info(
            f"Affectation(s) creee(s): {len(affectations)} affectation(s), "
            f"premiere_id={affectations[0].id}"
        )

        # Retourner la premiere affectation (pour affectation unique)
        # ou la premiere d'une serie (pour recurrente)
        return self._entity_to_response(affectations[0])

    def create_many(
        self,
        request: CreateAffectationRequest,
        current_user_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Cree plusieurs affectations (pour recurrence).

        Args:
            request: Donnees de creation.
            current_user_id: ID de l'utilisateur createur.

        Returns:
            Liste des affectations creees.

        Example:
            >>> results = controller.create_many(request, current_user_id=1)
        """
        dto = CreateAffectationDTO(
            utilisateur_id=request.utilisateur_id,
            chantier_id=request.chantier_id,
            date=request.date,
            heure_debut=request.heure_debut,
            heure_fin=request.heure_fin,
            note=request.note,
            type_affectation=request.type_affectation,
            jours_recurrence=request.jours_recurrence,
            date_fin_recurrence=request.date_fin_recurrence,
        )

        affectations = self.create_affectation_uc.execute(dto, current_user_id)
        return [self._entity_to_response(a) for a in affectations]

    def update(
        self,
        affectation_id: int,
        request: UpdateAffectationRequest,
        current_user_id: int,
    ) -> Dict[str, Any]:
        """
        Met a jour une affectation.

        Args:
            affectation_id: ID de l'affectation a modifier.
            request: Donnees de mise a jour.
            current_user_id: ID de l'utilisateur modificateur.

        Returns:
            Dictionnaire de l'affectation mise a jour.

        Raises:
            AffectationNotFoundError: Si affectation non trouvee.
            ValueError: Si donnees invalides.

        Example:
            >>> result = controller.update(1, request, current_user_id=2)
        """
        logger.info(
            f"Mise a jour affectation: id={affectation_id}, "
            f"updated_by={current_user_id}"
        )

        dto = UpdateAffectationDTO(
            heure_debut=request.heure_debut,
            heure_fin=request.heure_fin,
            note=request.note,
            chantier_id=request.chantier_id,
        )

        affectation = self.update_affectation_uc.execute(
            affectation_id, dto, current_user_id
        )

        logger.info(f"Affectation mise a jour: id={affectation.id}")

        return self._entity_to_response(affectation)

    def delete(self, affectation_id: int, current_user_id: int) -> Dict[str, Any]:
        """
        Supprime une affectation.

        Args:
            affectation_id: ID de l'affectation a supprimer.
            current_user_id: ID de l'utilisateur suppresseur.

        Returns:
            Dictionnaire confirmant la suppression.

        Raises:
            AffectationNotFoundError: Si affectation non trouvee.

        Example:
            >>> result = controller.delete(1, current_user_id=2)
        """
        logger.info(
            f"Suppression affectation: id={affectation_id}, "
            f"deleted_by={current_user_id}"
        )

        success = self.delete_affectation_uc.execute(affectation_id, current_user_id)

        if success:
            logger.info(f"Affectation supprimee: id={affectation_id}")
        else:
            logger.warning(f"Echec suppression affectation: id={affectation_id}")

        return {"deleted": success, "id": affectation_id}

    def get_planning(
        self,
        filters: PlanningFiltersRequest,
        current_user_id: int,
        current_user_role: str,
    ) -> List[Dict[str, Any]]:
        """
        Recupere le planning filtre.

        Args:
            filters: Filtres a appliquer.
            current_user_id: ID de l'utilisateur demandeur.
            current_user_role: Role de l'utilisateur.

        Returns:
            Liste des affectations.

        Example:
            >>> results = controller.get_planning(filters, user_id=1, role="admin")
        """
        dto = PlanningFiltersDTO(
            date_debut=filters.date_debut,
            date_fin=filters.date_fin,
            utilisateur_ids=filters.utilisateur_ids,
            chantier_ids=filters.chantier_ids,
            metiers=filters.metiers,
            planifies_only=filters.planifies_only,
            non_planifies_only=filters.non_planifies_only,
        )

        dtos = self.get_planning_uc.execute(dto, current_user_id, current_user_role)
        return [self._dto_to_response(d) for d in dtos]

    def get_planning_by_chantier(
        self,
        chantier_id: int,
        date_debut: date,
        date_fin: date,
        current_user_id: int,
        current_user_role: str,
    ) -> List[Dict[str, Any]]:
        """
        Recupere les affectations pour un chantier.

        Args:
            chantier_id: ID du chantier.
            date_debut: Date de debut.
            date_fin: Date de fin.
            current_user_id: ID de l'utilisateur demandeur.
            current_user_role: Role de l'utilisateur.

        Returns:
            Liste des affectations du chantier.
        """
        dto = PlanningFiltersDTO(
            date_debut=date_debut,
            date_fin=date_fin,
            chantier_ids=[chantier_id],
        )

        dtos = self.get_planning_uc.execute(dto, current_user_id, current_user_role)
        return [self._dto_to_response(d) for d in dtos]

    def get_planning_by_utilisateur(
        self,
        utilisateur_id: int,
        date_debut: date,
        date_fin: date,
        current_user_id: int,
        current_user_role: str,
    ) -> List[Dict[str, Any]]:
        """
        Recupere les affectations pour un utilisateur.

        Args:
            utilisateur_id: ID de l'utilisateur.
            date_debut: Date de debut.
            date_fin: Date de fin.
            current_user_id: ID de l'utilisateur demandeur.
            current_user_role: Role de l'utilisateur.

        Returns:
            Liste des affectations de l'utilisateur.
        """
        dto = PlanningFiltersDTO(
            date_debut=date_debut,
            date_fin=date_fin,
            utilisateur_ids=[utilisateur_id],
        )

        dtos = self.get_planning_uc.execute(dto, current_user_id, current_user_role)
        return [self._dto_to_response(d) for d in dtos]

    def duplicate(
        self,
        request: DuplicateAffectationsRequest,
        current_user_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Duplique des affectations d'une periode vers une autre.

        Args:
            request: Donnees de duplication.
            current_user_id: ID de l'utilisateur createur.

        Returns:
            Liste des nouvelles affectations creees.

        Raises:
            NoAffectationsToDuplicateError: Si aucune affectation source.
            AffectationConflictError: Si conflit sur date cible.

        Example:
            >>> results = controller.duplicate(request, current_user_id=1)
        """
        logger.info(
            f"Duplication affectations: user={request.utilisateur_id}, "
            f"source={request.source_date_debut} -> {request.source_date_fin}, "
            f"target={request.target_date_debut}, created_by={current_user_id}"
        )

        dto = DuplicateAffectationsDTO(
            utilisateur_id=request.utilisateur_id,
            source_date_debut=request.source_date_debut,
            source_date_fin=request.source_date_fin,
            target_date_debut=request.target_date_debut,
        )

        affectations = self.duplicate_affectations_uc.execute(dto, current_user_id)

        logger.info(
            f"Affectations dupliquees: {len(affectations)} affectation(s) creee(s)"
        )

        return [self._entity_to_response(a) for a in affectations]

    def get_non_planifies(
        self,
        date_debut: date,
        date_fin: date,
    ) -> Dict[str, Any]:
        """
        Recupere les IDs des utilisateurs non planifies.

        Args:
            date_debut: Date de debut de la periode.
            date_fin: Date de fin de la periode.

        Returns:
            Dictionnaire avec les IDs et le compte.

        Example:
            >>> result = controller.get_non_planifies(date1, date2)
        """
        user_ids = self.get_non_planifies_uc.execute(date_debut, date_fin)
        return {
            "utilisateur_ids": user_ids,
            "date_debut": date_debut.isoformat(),
            "date_fin": date_fin.isoformat(),
            "count": len(user_ids),
        }
