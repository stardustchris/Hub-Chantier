"""Use Case ListUsers - Liste des utilisateurs avec pagination."""

from typing import Optional

from ...domain.repositories import UserRepository
from ...domain.value_objects import Role, TypeUtilisateur
from ..dtos import UserDTO, UserListDTO


class ListUsersUseCase:
    """
    Cas d'utilisation : Liste des utilisateurs avec pagination (USR-09).

    Permet de récupérer une liste paginée d'utilisateurs avec filtres optionnels.
    Supporte la navigation précédent/suivant.

    Attributes:
        user_repo: Repository pour accéder aux utilisateurs.
    """

    def __init__(self, user_repo: UserRepository):
        """
        Initialise le use case.

        Args:
            user_repo: Repository utilisateurs (interface).
        """
        self.user_repo = user_repo

    def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        role: Optional[str] = None,
        type_utilisateur: Optional[str] = None,
        active_only: bool = False,
    ) -> UserListDTO:
        """
        Récupère une liste paginée d'utilisateurs.

        Args:
            skip: Nombre d'éléments à sauter (pour la pagination).
            limit: Nombre maximum d'éléments à retourner.
            role: Filtrer par rôle (optionnel).
            type_utilisateur: Filtrer par type (optionnel).
            active_only: Ne retourner que les utilisateurs actifs.

        Returns:
            UserListDTO contenant la liste et les infos de pagination.
        """
        # Déterminer quelle méthode de repository utiliser selon les filtres
        if role:
            role_enum = Role.from_string(role)
            users = self.user_repo.find_by_role(role_enum, skip=skip, limit=limit)
            # Note: le count devrait être filtré aussi, mais on simplifie ici
            total = self.user_repo.count()
        elif type_utilisateur:
            type_enum = TypeUtilisateur.from_string(type_utilisateur)
            users = self.user_repo.find_by_type(type_enum, skip=skip, limit=limit)
            total = self.user_repo.count()
        elif active_only:
            users = self.user_repo.find_active(skip=skip, limit=limit)
            total = self.user_repo.count()
        else:
            users = self.user_repo.find_all(skip=skip, limit=limit)
            total = self.user_repo.count()

        # Convertir en DTOs
        user_dtos = [UserDTO.from_entity(u) for u in users]

        return UserListDTO(
            users=user_dtos,
            total=total,
            skip=skip,
            limit=limit,
        )


class GetUserByIdUseCase:
    """
    Cas d'utilisation : Récupérer un utilisateur par ID.

    Attributes:
        user_repo: Repository pour accéder aux utilisateurs.
    """

    def __init__(self, user_repo: UserRepository):
        """
        Initialise le use case.

        Args:
            user_repo: Repository utilisateurs (interface).
        """
        self.user_repo = user_repo

    def execute(self, user_id: int) -> Optional[UserDTO]:
        """
        Récupère un utilisateur par son ID.

        Args:
            user_id: ID de l'utilisateur.

        Returns:
            UserDTO ou None si non trouvé.
        """
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return None
        return UserDTO.from_entity(user)
