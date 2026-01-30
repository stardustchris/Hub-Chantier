"""Use case pour supprimer complètement les données d'un utilisateur (RGPD)."""

from datetime import datetime
from typing import Optional

from ...domain.repositories import UserRepository
from ...domain.exceptions import UserNotFoundError


class DeleteUserDataUseCase:
    """
    Use case pour le droit à l'oubli RGPD (USR-14).

    Supprime définitivement toutes les données personnelles d'un utilisateur.
    Cette action est irréversible et conforme au RGPD Article 17.

    Attributes:
        user_repository: Repository pour la gestion des utilisateurs.
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialise le use case.

        Args:
            user_repository: Repository des utilisateurs.
        """
        self.user_repository = user_repository

    def execute(self, user_id: int, requester_id: int) -> dict[str, str]:
        """
        Supprime complètement les données d'un utilisateur.

        Seuls les administrateurs ou l'utilisateur lui-même peuvent effectuer
        cette opération. La suppression est définitive et irréversible.

        Args:
            user_id: ID de l'utilisateur à supprimer.
            requester_id: ID de l'utilisateur qui fait la demande.

        Returns:
            Message de confirmation de suppression.

        Raises:
            UserNotFoundError: Si l'utilisateur n'existe pas.
            PermissionError: Si le demandeur n'a pas les permissions.
        """
        # Vérifier que l'utilisateur existe
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Utilisateur #{user_id} introuvable")

        # Vérifier les permissions
        requester = self.user_repository.find_by_id(requester_id)
        if not requester:
            raise UserNotFoundError(f"Demandeur #{requester_id} introuvable")

        # Seul l'admin ou l'utilisateur lui-même peut supprimer
        is_admin = requester.role.value == "admin"
        is_self = user_id == requester_id

        if not (is_admin or is_self):
            raise PermissionError(
                "Vous n'avez pas la permission de supprimer cet utilisateur"
            )

        # Effectuer la suppression définitive (hard delete)
        self.user_repository.delete(user_id)

        return {
            "message": f"Utilisateur #{user_id} et toutes ses données ont été supprimés définitivement",
            "deleted_at": datetime.now().isoformat(),
            "gdpr_compliant": True,
        }
