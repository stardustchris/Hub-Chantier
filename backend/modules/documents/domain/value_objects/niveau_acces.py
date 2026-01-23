"""Value Object NiveauAcces - Niveaux d'accès aux documents (GED-04)."""

from enum import Enum


class NiveauAcces(Enum):
    """
    Niveaux d'accès minimum pour un dossier ou document.

    Selon CDC Section 9.3 - Niveaux d'accès:
    - COMPAGNON: Tous utilisateurs du chantier (plans, consignes sécurité)
    - CHEF_CHANTIER: Chefs + Conducteurs + Admin (documents techniques)
    - CONDUCTEUR: Conducteurs + Admin (contrats, budgets)
    - ADMIN: Admin uniquement (documents confidentiels, RH)
    """

    COMPAGNON = "compagnon"
    CHEF_CHANTIER = "chef_chantier"
    CONDUCTEUR = "conducteur"
    ADMIN = "admin"

    @property
    def ordre(self) -> int:
        """Retourne l'ordre hiérarchique (plus élevé = plus restrictif)."""
        ordre_map = {
            NiveauAcces.COMPAGNON: 1,
            NiveauAcces.CHEF_CHANTIER: 2,
            NiveauAcces.CONDUCTEUR: 3,
            NiveauAcces.ADMIN: 4,
        }
        return ordre_map[self]

    @property
    def description(self) -> str:
        """Retourne la description du niveau d'accès."""
        descriptions = {
            NiveauAcces.COMPAGNON: "Tous les utilisateurs du chantier",
            NiveauAcces.CHEF_CHANTIER: "Chefs de chantier, Conducteurs et Admin",
            NiveauAcces.CONDUCTEUR: "Conducteurs et Admin uniquement",
            NiveauAcces.ADMIN: "Administrateurs uniquement",
        }
        return descriptions[self]

    def peut_acceder(self, role_utilisateur: str) -> bool:
        """
        Vérifie si un rôle utilisateur peut accéder à ce niveau.

        Args:
            role_utilisateur: Le rôle de l'utilisateur (admin, conducteur, chef_chantier, compagnon).

        Returns:
            True si l'utilisateur a accès.
        """
        role_ordre = {
            "admin": 4,
            "administrateur": 4,
            "conducteur": 3,
            "chef_chantier": 2,
            "chef": 2,
            "compagnon": 1,
        }
        niveau_utilisateur = role_ordre.get(role_utilisateur.lower(), 0)
        return niveau_utilisateur >= self.ordre

    @classmethod
    def from_string(cls, value: str) -> "NiveauAcces":
        """
        Crée un NiveauAcces depuis une chaîne.

        Args:
            value: La valeur en chaîne.

        Returns:
            L'enum correspondant.

        Raises:
            ValueError: Si la valeur n'est pas valide.
        """
        try:
            return cls(value.lower())
        except ValueError:
            valid = [n.value for n in cls]
            raise ValueError(f"Niveau d'accès invalide: {value}. Valeurs valides: {valid}")

    @classmethod
    def list_all(cls) -> list[dict]:
        """Retourne tous les niveaux d'accès avec leurs descriptions."""
        return [
            {"value": n.value, "description": n.description, "ordre": n.ordre}
            for n in cls
        ]
