"""Value Object Role - Représente un rôle utilisateur."""

from enum import Enum


class Role(str, Enum):
    """
    Énumération des rôles utilisateur dans l'application.

    Attributes:
        ADMIN: Administrateur avec tous les droits.
        CHEF_CHANTIER: Chef de chantier, gère son équipe.
        EMPLOYE: Employé standard.
    """

    ADMIN = "admin"
    CHEF_CHANTIER = "chef_chantier"
    EMPLOYE = "employe"

    def __str__(self) -> str:
        """Retourne la valeur du rôle."""
        return self.value

    def has_permission(self, permission: str) -> bool:
        """
        Vérifie si le rôle a une permission donnée.

        Args:
            permission: La permission à vérifier.

        Returns:
            True si le rôle a la permission.
        """
        permissions = {
            Role.ADMIN: [
                "users:read", "users:write", "users:delete",
                "chantiers:read", "chantiers:write", "chantiers:delete",
                "pointages:read", "pointages:write", "pointages:validate",
                "planning:read", "planning:write",
                "documents:read", "documents:write", "documents:delete",
                "reports:read", "reports:write",
            ],
            Role.CHEF_CHANTIER: [
                "users:read",
                "chantiers:read",
                "pointages:read", "pointages:validate",
                "planning:read", "planning:write",
                "documents:read", "documents:write",
                "reports:read",
            ],
            Role.EMPLOYE: [
                "chantiers:read",
                "pointages:read", "pointages:write",
                "planning:read",
                "documents:read",
            ],
        }
        return permission in permissions.get(self, [])

    @classmethod
    def from_string(cls, value: str) -> "Role":
        """
        Crée un Role à partir d'une string.

        Args:
            value: La valeur string du rôle.

        Returns:
            L'instance Role correspondante.

        Raises:
            ValueError: Si la valeur ne correspond à aucun rôle.
        """
        try:
            return cls(value.lower())
        except ValueError:
            valid_roles = [r.value for r in cls]
            raise ValueError(
                f"Rôle invalide: {value}. Rôles valides: {valid_roles}"
            )
