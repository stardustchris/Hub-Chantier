"""Use Cases pour la gestion des réponses aux signalements."""

from typing import Optional, Callable

from ..dtos import (
    ReponseDTO,
    ReponseCreateDTO,
    ReponseUpdateDTO,
    ReponseListDTO,
)
from ...domain.entities import Reponse
from ...domain.repositories import SignalementRepository, ReponseRepository


class ReponseNotFoundError(Exception):
    """Erreur levée quand une réponse n'est pas trouvée."""

    pass


class SignalementNotFoundError(Exception):
    """Erreur levée quand un signalement n'est pas trouvé."""

    pass


class AccessDeniedError(Exception):
    """Erreur levée quand l'accès est refusé."""

    pass


# Type pour la fonction de récupération des noms d'utilisateurs
UserNameResolver = Callable[[int], Optional[str]]


class CreateReponseUseCase:
    """Use case pour créer une réponse à un signalement (SIG-07)."""

    def __init__(
        self,
        signalement_repository: SignalementRepository,
        reponse_repository: ReponseRepository,
        get_user_name: Optional[UserNameResolver] = None,
    ):
        self._signalement_repo = signalement_repository
        self._reponse_repo = reponse_repository
        self._get_user_name = get_user_name

    def execute(self, dto: ReponseCreateDTO) -> ReponseDTO:
        """
        Crée une nouvelle réponse.

        Args:
            dto: Données de création.

        Returns:
            La réponse créée.

        Raises:
            SignalementNotFoundError: Si le signalement n'existe pas.
        """
        # Vérifier que le signalement existe
        signalement = self._signalement_repo.find_by_id(dto.signalement_id)
        if not signalement:
            raise SignalementNotFoundError(
                f"Signalement {dto.signalement_id} non trouvé"
            )

        reponse = Reponse(
            signalement_id=dto.signalement_id,
            contenu=dto.contenu,
            auteur_id=dto.auteur_id,
            photo_url=dto.photo_url,
            est_resolution=dto.est_resolution,
        )

        reponse = self._reponse_repo.save(reponse)

        return self._to_dto(reponse)

    def _to_dto(self, rep: Reponse) -> ReponseDTO:
        """Convertit une entité en DTO."""
        auteur_nom = None
        if self._get_user_name:
            auteur_nom = self._get_user_name(rep.auteur_id)

        return ReponseDTO(
            id=rep.id,  # type: ignore
            signalement_id=rep.signalement_id,
            contenu=rep.contenu,
            auteur_id=rep.auteur_id,
            auteur_nom=auteur_nom,
            photo_url=rep.photo_url,
            created_at=rep.created_at,
            updated_at=rep.updated_at,
            est_resolution=rep.est_resolution,
        )


class ListReponsesUseCase:
    """Use case pour lister les réponses d'un signalement (SIG-07)."""

    def __init__(
        self,
        reponse_repository: ReponseRepository,
        get_user_name: Optional[UserNameResolver] = None,
    ):
        self._reponse_repo = reponse_repository
        self._get_user_name = get_user_name

    def execute(
        self,
        signalement_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> ReponseListDTO:
        """
        Liste les réponses d'un signalement.

        Args:
            signalement_id: ID du signalement.
            skip: Nombre à sauter.
            limit: Limite.

        Returns:
            Liste des réponses avec pagination.
        """
        reponses = self._reponse_repo.find_by_signalement(
            signalement_id, skip, limit
        )
        total = self._reponse_repo.count_by_signalement(signalement_id)

        dtos = [self._to_dto(rep) for rep in reponses]

        return ReponseListDTO(
            reponses=dtos,
            total=total,
            skip=skip,
            limit=limit,
        )

    def _to_dto(self, rep: Reponse) -> ReponseDTO:
        """Convertit une entité en DTO."""
        auteur_nom = None
        if self._get_user_name:
            auteur_nom = self._get_user_name(rep.auteur_id)

        return ReponseDTO(
            id=rep.id,  # type: ignore
            signalement_id=rep.signalement_id,
            contenu=rep.contenu,
            auteur_id=rep.auteur_id,
            auteur_nom=auteur_nom,
            photo_url=rep.photo_url,
            created_at=rep.created_at,
            updated_at=rep.updated_at,
            est_resolution=rep.est_resolution,
        )


class UpdateReponseUseCase:
    """Use case pour mettre à jour une réponse."""

    def __init__(
        self,
        reponse_repository: ReponseRepository,
        get_user_name: Optional[UserNameResolver] = None,
    ):
        self._reponse_repo = reponse_repository
        self._get_user_name = get_user_name

    def execute(
        self,
        reponse_id: int,
        dto: ReponseUpdateDTO,
        user_id: int,
        user_role: str,
    ) -> ReponseDTO:
        """
        Met à jour une réponse.

        Args:
            reponse_id: ID de la réponse.
            dto: Données de mise à jour.
            user_id: ID de l'utilisateur effectuant la modification.
            user_role: Rôle de l'utilisateur.

        Returns:
            La réponse mise à jour.

        Raises:
            ReponseNotFoundError: Si la réponse n'existe pas.
            AccessDeniedError: Si l'utilisateur n'a pas les droits.
        """
        reponse = self._reponse_repo.find_by_id(reponse_id)
        if not reponse:
            raise ReponseNotFoundError(f"Réponse {reponse_id} non trouvée")

        if not reponse.peut_modifier(user_id, user_role):
            raise AccessDeniedError(
                "Vous n'avez pas les droits pour modifier cette réponse"
            )

        if dto.contenu is not None:
            reponse.modifier(dto.contenu)

        if dto.photo_url is not None:
            reponse.photo_url = dto.photo_url

        reponse = self._reponse_repo.save(reponse)

        return self._to_dto(reponse)

    def _to_dto(self, rep: Reponse) -> ReponseDTO:
        """Convertit une entité en DTO."""
        auteur_nom = None
        if self._get_user_name:
            auteur_nom = self._get_user_name(rep.auteur_id)

        return ReponseDTO(
            id=rep.id,  # type: ignore
            signalement_id=rep.signalement_id,
            contenu=rep.contenu,
            auteur_id=rep.auteur_id,
            auteur_nom=auteur_nom,
            photo_url=rep.photo_url,
            created_at=rep.created_at,
            updated_at=rep.updated_at,
            est_resolution=rep.est_resolution,
        )


class DeleteReponseUseCase:
    """Use case pour supprimer une réponse."""

    def __init__(self, reponse_repository: ReponseRepository):
        self._reponse_repo = reponse_repository

    def execute(
        self,
        reponse_id: int,
        user_id: int,
        user_role: str,
    ) -> bool:
        """
        Supprime une réponse.

        Args:
            reponse_id: ID de la réponse.
            user_id: ID de l'utilisateur effectuant la suppression.
            user_role: Rôle de l'utilisateur.

        Returns:
            True si supprimée.

        Raises:
            ReponseNotFoundError: Si la réponse n'existe pas.
            AccessDeniedError: Si l'utilisateur n'a pas les droits.
        """
        reponse = self._reponse_repo.find_by_id(reponse_id)
        if not reponse:
            raise ReponseNotFoundError(f"Réponse {reponse_id} non trouvée")

        if not reponse.peut_supprimer(user_id, user_role):
            raise AccessDeniedError(
                "Vous n'avez pas les droits pour supprimer cette réponse"
            )

        return self._reponse_repo.delete(reponse_id)
