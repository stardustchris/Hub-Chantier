"""Value Object PostTargeting - Ciblage d'un post."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class TargetType(str, Enum):
    """
    Type de ciblage d'un post.

    Selon CDC Section 2 - FEED-03:
    - EVERYONE: Tous les utilisateurs
    - SPECIFIC_CHANTIERS: Chantiers spécifiques
    - SPECIFIC_PEOPLE: Personnes spécifiques
    """

    EVERYONE = "everyone"
    SPECIFIC_CHANTIERS = "specific_chantiers"
    SPECIFIC_PEOPLE = "specific_people"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PostTargeting:
    """
    Value Object représentant le ciblage d'un post.

    Un post peut cibler:
    - Tout le monde (TargetType.EVERYONE)
    - Des chantiers spécifiques (TargetType.SPECIFIC_CHANTIERS)
    - Des personnes spécifiques (TargetType.SPECIFIC_PEOPLE)

    Attributes:
        target_type: Le type de ciblage.
        chantier_ids: Liste des IDs de chantiers ciblés (si applicable).
        user_ids: Liste des IDs d'utilisateurs ciblés (si applicable).
    """

    target_type: TargetType
    chantier_ids: Optional[tuple] = None
    user_ids: Optional[tuple] = None

    def __post_init__(self) -> None:
        """Valide la cohérence du ciblage."""
        if self.target_type == TargetType.SPECIFIC_CHANTIERS:
            if not self.chantier_ids or len(self.chantier_ids) == 0:
                raise ValueError(
                    "Au moins un chantier doit être spécifié pour le ciblage SPECIFIC_CHANTIERS"
                )

        if self.target_type == TargetType.SPECIFIC_PEOPLE:
            if not self.user_ids or len(self.user_ids) == 0:
                raise ValueError(
                    "Au moins un utilisateur doit être spécifié pour le ciblage SPECIFIC_PEOPLE"
                )

    @classmethod
    def everyone(cls) -> "PostTargeting":
        """Crée un ciblage pour tous les utilisateurs."""
        return cls(target_type=TargetType.EVERYONE)

    @classmethod
    def for_chantiers(cls, chantier_ids: List[int]) -> "PostTargeting":
        """Crée un ciblage pour des chantiers spécifiques."""
        return cls(
            target_type=TargetType.SPECIFIC_CHANTIERS,
            chantier_ids=tuple(chantier_ids),
        )

    @classmethod
    def for_users(cls, user_ids: List[int]) -> "PostTargeting":
        """Crée un ciblage pour des utilisateurs spécifiques."""
        return cls(
            target_type=TargetType.SPECIFIC_PEOPLE,
            user_ids=tuple(user_ids),
        )

    def includes_chantier(self, chantier_id: int) -> bool:
        """Vérifie si le ciblage inclut un chantier donné."""
        if self.target_type == TargetType.EVERYONE:
            return True
        if self.target_type == TargetType.SPECIFIC_CHANTIERS:
            return self.chantier_ids is not None and chantier_id in self.chantier_ids
        return False

    def includes_user(self, user_id: int) -> bool:
        """Vérifie si le ciblage inclut un utilisateur donné."""
        if self.target_type == TargetType.EVERYONE:
            return True
        if self.target_type == TargetType.SPECIFIC_PEOPLE:
            return self.user_ids is not None and user_id in self.user_ids
        return False

    def get_display_text(self) -> str:
        """Retourne un texte lisible pour l'affichage du ciblage."""
        if self.target_type == TargetType.EVERYONE:
            return "Tout le monde"
        elif self.target_type == TargetType.SPECIFIC_CHANTIERS:
            count = len(self.chantier_ids) if self.chantier_ids else 0
            return f"{count} chantier(s)"
        else:
            count = len(self.user_ids) if self.user_ids else 0
            return f"{count} personne(s)"
