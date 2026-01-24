"""Port pour recuperer les informations de base des entites.

Ce service permet aux modules de recuperer des informations basiques
sur les utilisateurs et chantiers SANS creer de dependances directes
entre modules.

Conforme Clean Architecture:
- Interface definie dans Application layer
- Implementation dans Infrastructure layer
- Aucun import de modules specifiques
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class UserBasicInfo:
    """Informations de base d'un utilisateur.

    Attributes:
        id: Identifiant unique.
        nom: Nom complet (prenom + nom).
        couleur: Couleur hex pour l'affichage.
        metier: Type de metier/role.
    """
    id: int
    nom: str
    couleur: Optional[str] = None
    metier: Optional[str] = None


@dataclass(frozen=True)
class ChantierBasicInfo:
    """Informations de base d'un chantier.

    Attributes:
        id: Identifiant unique.
        nom: Nom du chantier.
        couleur: Couleur hex pour l'affichage.
    """
    id: int
    nom: str
    couleur: Optional[str] = None


class EntityInfoService(ABC):
    """Service abstrait pour recuperer les infos de base des entites.

    Ce port permet de decoupler les modules qui ont besoin d'afficher
    des informations sur les utilisateurs/chantiers sans importer
    directement les repositories d'autres modules.

    Example:
        ```python
        class GetPlanningUseCase:
            def __init__(self, entity_info: EntityInfoService):
                self.entity_info = entity_info

            def execute(self):
                user_info = self.entity_info.get_user_info(user_id)
                if user_info:
                    print(f"User: {user_info.nom}")
        ```
    """

    @abstractmethod
    def get_user_info(self, user_id: int) -> Optional[UserBasicInfo]:
        """Recupere les informations de base d'un utilisateur.

        Args:
            user_id: Identifiant de l'utilisateur.

        Returns:
            UserBasicInfo si trouve, None sinon.
        """
        pass

    @abstractmethod
    def get_chantier_info(self, chantier_id: int) -> Optional[ChantierBasicInfo]:
        """Recupere les informations de base d'un chantier.

        Args:
            chantier_id: Identifiant du chantier.

        Returns:
            ChantierBasicInfo si trouve, None sinon.
        """
        pass

    @abstractmethod
    def get_active_user_ids(self) -> List[int]:
        """Recupere les IDs de tous les utilisateurs actifs.

        Returns:
            Liste des IDs des utilisateurs actifs.
        """
        pass

    @abstractmethod
    def get_user_chantier_ids(self, user_id: int) -> List[int]:
        """Recupere les IDs des chantiers dont l'utilisateur est responsable.

        Args:
            user_id: Identifiant de l'utilisateur.

        Returns:
            Liste des IDs des chantiers.
        """
        pass
