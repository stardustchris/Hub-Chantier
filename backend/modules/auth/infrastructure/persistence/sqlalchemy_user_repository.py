"""Implémentation SQLAlchemy du UserRepository."""

from typing import Optional, List

from sqlalchemy.orm import Session

from ...domain.entities import User
from ...domain.repositories import UserRepository
from ...domain.value_objects import Email, PasswordHash, Role
from .user_model import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """
    Implémentation du UserRepository utilisant SQLAlchemy.

    Fait le mapping entre l'entité User (Domain) et UserModel (Infrastructure).

    Attributes:
        session: Session SQLAlchemy pour les opérations DB.
    """

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy active.
        """
        self.session = session

    def find_by_id(self, user_id: int) -> Optional[User]:
        """
        Trouve un utilisateur par son ID.

        Args:
            user_id: L'identifiant unique.

        Returns:
            L'entité User ou None.
        """
        model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(model) if model else None

    def find_by_email(self, email: Email) -> Optional[User]:
        """
        Trouve un utilisateur par son email.

        Args:
            email: L'adresse email (Value Object).

        Returns:
            L'entité User ou None.
        """
        model = (
            self.session.query(UserModel)
            .filter(UserModel.email == str(email))
            .first()
        )
        return self._to_entity(model) if model else None

    def save(self, user: User) -> User:
        """
        Persiste un utilisateur (création ou mise à jour).

        Args:
            user: L'entité User à sauvegarder.

        Returns:
            L'entité User avec ID (si création).
        """
        if user.id:
            # Update
            model = self.session.query(UserModel).filter(UserModel.id == user.id).first()
            if model:
                model.email = str(user.email)
                model.password_hash = user.password_hash.value
                model.nom = user.nom
                model.prenom = user.prenom
                model.role = user.role.value
                model.is_active = user.is_active
                model.updated_at = user.updated_at
        else:
            # Create
            model = self._to_model(user)
            self.session.add(model)

        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def delete(self, user_id: int) -> bool:
        """
        Supprime un utilisateur.

        Args:
            user_id: L'identifiant de l'utilisateur.

        Returns:
            True si supprimé, False si non trouvé.
        """
        model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Récupère tous les utilisateurs avec pagination.

        Args:
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des entités User.
        """
        models = (
            self.session.query(UserModel)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def exists_by_email(self, email: Email) -> bool:
        """
        Vérifie si un email existe.

        Args:
            email: L'email à vérifier.

        Returns:
            True si l'email existe.
        """
        return (
            self.session.query(UserModel)
            .filter(UserModel.email == str(email))
            .first()
            is not None
        )

    def _to_entity(self, model: UserModel) -> User:
        """
        Convertit un modèle SQLAlchemy en entité Domain.

        Args:
            model: Le modèle SQLAlchemy.

        Returns:
            L'entité User.
        """
        return User(
            id=model.id,
            email=Email(model.email),
            password_hash=PasswordHash(model.password_hash),
            nom=model.nom,
            prenom=model.prenom,
            role=Role.from_string(model.role),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, user: User) -> UserModel:
        """
        Convertit une entité Domain en modèle SQLAlchemy.

        Args:
            user: L'entité User.

        Returns:
            Le modèle UserModel.
        """
        return UserModel(
            id=user.id,
            email=str(user.email),
            password_hash=user.password_hash.value,
            nom=user.nom,
            prenom=user.prenom,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
