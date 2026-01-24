"""Use cases pour la gestion des ressources.

CDC Section 11 - LOG-01, LOG-02.
"""
from typing import Optional, List

from ..dtos import (
    CreateRessourceDTO,
    UpdateRessourceDTO,
    RessourceDTO,
    RessourceListDTO,
)
from ...domain.entities import Ressource
from ...domain.value_objects import TypeRessource
from ...domain.repositories import RessourceRepository


class RessourceNotFoundError(Exception):
    """Exception levee quand une ressource n'existe pas."""
    pass


class RessourceCodeAlreadyExistsError(Exception):
    """Exception levee quand le code ressource existe deja."""
    pass


class AccessDeniedError(Exception):
    """Exception levee pour acces refuse."""
    pass


class CreateRessourceUseCase:
    """Use case pour creer une ressource (LOG-01).

    Note: Seuls les administrateurs peuvent creer des ressources.
    """

    def __init__(self, ressource_repository: RessourceRepository):
        """Initialise le use case.

        Args:
            ressource_repository: Repository des ressources.
        """
        self._repo = ressource_repository

    def execute(self, dto: CreateRessourceDTO, user_role: str) -> RessourceDTO:
        """Execute le use case.

        Args:
            dto: Donnees de creation.
            user_role: Role de l'utilisateur.

        Returns:
            La ressource creee.

        Raises:
            AccessDeniedError: Si l'utilisateur n'est pas admin.
            RessourceCodeAlreadyExistsError: Si le code existe deja.
        """
        if user_role != "admin":
            raise AccessDeniedError(
                "Seuls les administrateurs peuvent creer des ressources (LOG-01)"
            )

        # Verifier unicite du code
        existing = self._repo.find_by_code(dto.code)
        if existing:
            raise RessourceCodeAlreadyExistsError(
                f"Le code ressource '{dto.code}' existe deja"
            )

        ressource = Ressource(
            code=dto.code,
            nom=dto.nom,
            description=dto.description,
            type_ressource=TypeRessource(dto.type_ressource),
            photo_url=dto.photo_url,
            couleur=dto.couleur,
            plage_horaire_debut=dto.plage_horaire_debut,
            plage_horaire_fin=dto.plage_horaire_fin,
            validation_requise=dto.validation_requise,
        )

        saved = self._repo.save(ressource)
        return RessourceDTO.from_entity(saved)


class GetRessourceUseCase:
    """Use case pour obtenir une ressource (LOG-02)."""

    def __init__(self, ressource_repository: RessourceRepository):
        self._repo = ressource_repository

    def execute(self, ressource_id: int) -> RessourceDTO:
        """Execute le use case.

        Args:
            ressource_id: ID de la ressource.

        Returns:
            La ressource.

        Raises:
            RessourceNotFoundError: Si la ressource n'existe pas.
        """
        ressource = self._repo.find_by_id(ressource_id)
        if not ressource:
            raise RessourceNotFoundError(f"Ressource {ressource_id} non trouvee")

        return RessourceDTO.from_entity(ressource)


class ListRessourcesUseCase:
    """Use case pour lister les ressources."""

    def __init__(self, ressource_repository: RessourceRepository):
        self._repo = ressource_repository

    def execute(
        self,
        type_ressource: Optional[str] = None,
        is_active: Optional[bool] = True,
        skip: int = 0,
        limit: int = 50,
    ) -> RessourceListDTO:
        """Execute le use case.

        Args:
            type_ressource: Filtrer par type.
            is_active: Filtrer par statut actif.
            skip: Offset de pagination.
            limit: Limite de pagination.

        Returns:
            Liste paginee des ressources.
        """
        ressources = self._repo.find_all(
            type_ressource=type_ressource,
            is_active=is_active,
            skip=skip,
            limit=limit,
        )
        total = self._repo.count(type_ressource=type_ressource, is_active=is_active)

        return RessourceListDTO(
            ressources=[RessourceDTO.from_entity(r) for r in ressources],
            total=total,
            skip=skip,
            limit=limit,
        )


class UpdateRessourceUseCase:
    """Use case pour mettre a jour une ressource."""

    def __init__(self, ressource_repository: RessourceRepository):
        self._repo = ressource_repository

    def execute(self, dto: UpdateRessourceDTO, user_role: str) -> RessourceDTO:
        """Execute le use case.

        Args:
            dto: Donnees de mise a jour.
            user_role: Role de l'utilisateur.

        Returns:
            La ressource mise a jour.

        Raises:
            AccessDeniedError: Si l'utilisateur n'est pas admin.
            RessourceNotFoundError: Si la ressource n'existe pas.
        """
        if user_role != "admin":
            raise AccessDeniedError(
                "Seuls les administrateurs peuvent modifier des ressources"
            )

        ressource = self._repo.find_by_id(dto.id)
        if not ressource:
            raise RessourceNotFoundError(f"Ressource {dto.id} non trouvee")

        # Convertir type_ressource si fourni
        type_ressource = None
        if dto.type_ressource:
            type_ressource = TypeRessource(dto.type_ressource)

        ressource.update(
            nom=dto.nom,
            description=dto.description,
            type_ressource=type_ressource,
            photo_url=dto.photo_url,
            couleur=dto.couleur,
            plage_horaire_debut=dto.plage_horaire_debut,
            plage_horaire_fin=dto.plage_horaire_fin,
            validation_requise=dto.validation_requise,
        )

        saved = self._repo.save(ressource)
        return RessourceDTO.from_entity(saved)


class DeleteRessourceUseCase:
    """Use case pour supprimer une ressource (soft delete)."""

    def __init__(self, ressource_repository: RessourceRepository):
        self._repo = ressource_repository

    def execute(self, ressource_id: int, user_role: str) -> None:
        """Execute le use case.

        Args:
            ressource_id: ID de la ressource.
            user_role: Role de l'utilisateur.

        Raises:
            AccessDeniedError: Si l'utilisateur n'est pas admin.
            RessourceNotFoundError: Si la ressource n'existe pas.
        """
        if user_role != "admin":
            raise AccessDeniedError(
                "Seuls les administrateurs peuvent supprimer des ressources"
            )

        ressource = self._repo.find_by_id(ressource_id)
        if not ressource:
            raise RessourceNotFoundError(f"Ressource {ressource_id} non trouvee")

        ressource.supprimer()
        self._repo.save(ressource)


class ActivateRessourceUseCase:
    """Use case pour activer/desactiver une ressource."""

    def __init__(self, ressource_repository: RessourceRepository):
        self._repo = ressource_repository

    def execute(
        self, ressource_id: int, is_active: bool, user_role: str
    ) -> RessourceDTO:
        """Execute le use case.

        Args:
            ressource_id: ID de la ressource.
            is_active: Nouveau statut actif.
            user_role: Role de l'utilisateur.

        Returns:
            La ressource mise a jour.

        Raises:
            AccessDeniedError: Si l'utilisateur n'est pas admin.
            RessourceNotFoundError: Si la ressource n'existe pas.
        """
        if user_role != "admin":
            raise AccessDeniedError(
                "Seuls les administrateurs peuvent modifier le statut des ressources"
            )

        ressource = self._repo.find_by_id(ressource_id)
        if not ressource:
            raise RessourceNotFoundError(f"Ressource {ressource_id} non trouvee")

        if is_active:
            ressource.activer()
        else:
            ressource.desactiver()

        saved = self._repo.save(ressource)
        return RessourceDTO.from_entity(saved)
