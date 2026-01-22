"""Value Objects du module auth."""

from .email import Email
from .password_hash import PasswordHash
from .role import Role
from .type_utilisateur import TypeUtilisateur
from .couleur import Couleur

__all__ = ["Email", "PasswordHash", "Role", "TypeUtilisateur", "Couleur"]
