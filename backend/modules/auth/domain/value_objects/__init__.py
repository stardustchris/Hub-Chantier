"""Value Objects du module auth."""

from .email import Email
from .password_hash import PasswordHash
from .role import Role
from .type_utilisateur import TypeUtilisateur

# Couleur est maintenant dans shared pour éviter les imports inter-modules
from shared.domain.value_objects import Couleur

__all__ = ["Email", "PasswordHash", "Role", "TypeUtilisateur", "Couleur"]
