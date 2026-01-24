"""Implementation du service EntityInfoService.

Ce module contient l'implementation concrete qui accede aux repositories
des autres modules. Les imports inter-modules sont CENTRALISES ici
plutot que disperses dans chaque module consommateur.

Note architecture:
- Ce fichier est le SEUL endroit ou les imports inter-modules sont autorises
- Il sert de facade pour eviter le couplage direct entre modules
- Si un module change, seul ce fichier doit etre modifie
"""

from typing import Optional, List
import logging

from sqlalchemy.orm import Session

from shared.application.ports import (
    EntityInfoService,
    UserBasicInfo,
    ChantierBasicInfo,
)

logger = logging.getLogger(__name__)


class SQLAlchemyEntityInfoService(EntityInfoService):
    """Implementation SQLAlchemy du service d'information des entites.

    Cette implementation utilise directement les modeles SQLAlchemy
    pour recuperer les informations. Les imports sont faits de maniere
    lazy pour eviter les problemes d'import circulaire.

    Args:
        session: Session SQLAlchemy active.
    """

    def __init__(self, session: Session):
        """Initialise le service avec une session DB.

        Args:
            session: Session SQLAlchemy.
        """
        self._session = session

    def get_user_info(self, user_id: int) -> Optional[UserBasicInfo]:
        """Recupere les informations de base d'un utilisateur.

        Args:
            user_id: Identifiant de l'utilisateur.

        Returns:
            UserBasicInfo si trouve, None sinon.
        """
        try:
            # Import lazy pour eviter les imports circulaires au demarrage
            from modules.auth.infrastructure.persistence import UserModel

            user = self._session.query(UserModel).filter(
                UserModel.id == user_id
            ).first()

            if user:
                nom = f"{user.prenom or ''} {user.nom or ''}".strip()
                return UserBasicInfo(
                    id=user.id,
                    nom=nom or f"User {user.id}",
                    couleur=user.couleur,
                    metier=user.metier,
                )
        except Exception as e:
            logger.warning(f"Erreur recuperation user {user_id}: {e}")

        return None

    def get_chantier_info(self, chantier_id: int) -> Optional[ChantierBasicInfo]:
        """Recupere les informations de base d'un chantier.

        Args:
            chantier_id: Identifiant du chantier.

        Returns:
            ChantierBasicInfo si trouve, None sinon.
        """
        try:
            from modules.chantiers.infrastructure.persistence import ChantierModel

            chantier = self._session.query(ChantierModel).filter(
                ChantierModel.id == chantier_id
            ).first()

            if chantier:
                return ChantierBasicInfo(
                    id=chantier.id,
                    nom=chantier.nom or f"Chantier {chantier.id}",
                    couleur=chantier.couleur,
                )
        except Exception as e:
            logger.warning(f"Erreur recuperation chantier {chantier_id}: {e}")

        return None

    def get_active_user_ids(self) -> List[int]:
        """Recupere les IDs de tous les utilisateurs actifs.

        Returns:
            Liste des IDs des utilisateurs actifs.
        """
        try:
            from modules.auth.infrastructure.persistence import UserModel

            users = self._session.query(UserModel.id).filter(
                UserModel.is_active.is_(True)
            ).all()

            return [u.id for u in users]
        except Exception as e:
            logger.warning(f"Erreur recuperation users actifs: {e}")

        return []

    def get_user_chantier_ids(self, user_id: int) -> List[int]:
        """Recupere les IDs des chantiers dont l'utilisateur est responsable.

        Args:
            user_id: Identifiant de l'utilisateur.

        Returns:
            Liste des IDs des chantiers.
        """
        try:
            from modules.chantiers.infrastructure.persistence import ChantierModel

            # Cherche les chantiers ou l'utilisateur est conducteur ou chef
            chantiers = self._session.query(ChantierModel.id).filter(
                (ChantierModel.conducteur_id == user_id) |
                (ChantierModel.chef_chantier_id == user_id)
            ).all()

            return [c.id for c in chantiers]
        except Exception as e:
            logger.warning(f"Erreur recuperation chantiers user {user_id}: {e}")

        return []


def get_entity_info_service(session: Session) -> EntityInfoService:
    """Factory pour creer le service d'information des entites.

    Args:
        session: Session SQLAlchemy.

    Returns:
        Instance du service.
    """
    return SQLAlchemyEntityInfoService(session)
