"""Value Object Role - Représente un rôle utilisateur."""

from enum import Enum


class Role(str, Enum):
    """
    Énumération des rôles utilisateur dans l'application.

    Selon CDC Section 3.3 - Matrice des roles et permissions:
    - ADMIN: Administrateur avec tous les droits (Web + Mobile)
    - CONDUCTEUR: Conducteur de travaux, gère plusieurs chantiers (Web + Mobile)
    - CHEF_CHANTIER: Chef de chantier, gère son équipe sur site (Mobile only)
    - COMPAGNON: Ouvrier de chantier (Mobile only)
    """

    ADMIN = "admin"
    CONDUCTEUR = "conducteur"
    CHEF_CHANTIER = "chef_chantier"
    COMPAGNON = "compagnon"

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
                "logistique:read", "logistique:write", "logistique:validate",
                "formulaires:read", "formulaires:write",
                "memos:read", "memos:write", "memos:delete",
                "taches:read", "taches:write",
                "feuilles_heures:read", "feuilles_heures:write", "feuilles_heures:validate",
            ],
            Role.CONDUCTEUR: [
                "users:read",
                "chantiers:read", "chantiers:write",
                "pointages:read", "pointages:validate",
                "planning:read", "planning:write",
                "documents:read", "documents:write",
                "reports:read", "reports:write",
                "logistique:read", "logistique:validate",
                "formulaires:read", "formulaires:write",
                "memos:read", "memos:write",
                "taches:read", "taches:write",
                "feuilles_heures:read", "feuilles_heures:write", "feuilles_heures:validate",
            ],
            Role.CHEF_CHANTIER: [
                "users:read",
                "chantiers:read",
                "pointages:read", "pointages:validate",
                "planning:read", "planning:write",
                "documents:read", "documents:write",
                "reports:read",
                "logistique:read", "logistique:validate",
                "formulaires:read", "formulaires:write",
                "memos:read", "memos:write",
                "taches:read", "taches:write",
                "feuilles_heures:read", "feuilles_heures:write",
            ],
            Role.COMPAGNON: [
                "chantiers:read",
                "pointages:read", "pointages:write",
                "planning:read",
                "documents:read",
                "formulaires:read", "formulaires:write",
                "memos:read",
                "taches:read",
                "feuilles_heures:read", "feuilles_heures:write",
            ],
        }
        return permission in permissions.get(self, [])

    def can_access_web(self) -> bool:
        """Vérifie si le rôle a accès à l'interface web."""
        return self in (Role.ADMIN, Role.CONDUCTEUR)

    def can_access_mobile(self) -> bool:
        """Vérifie si le rôle a accès à l'application mobile."""
        return True  # Tous les rôles ont accès au mobile

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
