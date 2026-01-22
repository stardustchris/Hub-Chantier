"""Implémentation SQLAlchemy du UserRepository."""

from typing import Optional, List

from sqlalchemy.orm import Session

from ...domain.entities import User
from ...domain.repositories import UserRepository
from ...domain.value_objects import Email, PasswordHash, Role, TypeUtilisateur, Couleur
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

    def find_by_code(self, code_utilisateur: str) -> Optional[User]:
        """
        Trouve un utilisateur par son code/matricule.

        Args:
            code_utilisateur: Le code utilisateur (matricule).

        Returns:
            L'entité User ou None.
        """
        model = (
            self.session.query(UserModel)
            .filter(UserModel.code_utilisateur == code_utilisateur)
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
                model.type_utilisateur = user.type_utilisateur.value
                model.is_active = user.is_active
                model.couleur = str(user.couleur) if user.couleur else Couleur.DEFAULT
                model.photo_profil = user.photo_profil
                model.code_utilisateur = user.code_utilisateur
                model.telephone = user.telephone
                model.metier = user.metier
                model.contact_urgence_nom = user.contact_urgence_nom
                model.contact_urgence_tel = user.contact_urgence_tel
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
            .order_by(UserModel.nom, UserModel.prenom)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def count(self) -> int:
        """
        Compte le nombre total d'utilisateurs.

        Returns:
            Nombre total d'utilisateurs.
        """
        return self.session.query(UserModel).count()

    def find_by_role(self, role: Role, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Trouve les utilisateurs par rôle.

        Args:
            role: Le rôle à filtrer.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des entités User avec ce rôle.
        """
        models = (
            self.session.query(UserModel)
            .filter(UserModel.role == role.value)
            .order_by(UserModel.nom, UserModel.prenom)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_type(
        self, type_utilisateur: TypeUtilisateur, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        Trouve les utilisateurs par type (employé/sous-traitant).

        Args:
            type_utilisateur: Le type à filtrer.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des entités User de ce type.
        """
        models = (
            self.session.query(UserModel)
            .filter(UserModel.type_utilisateur == type_utilisateur.value)
            .order_by(UserModel.nom, UserModel.prenom)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_active(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Trouve les utilisateurs actifs.

        Args:
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des entités User actifs.
        """
        models = (
            self.session.query(UserModel)
            .filter(UserModel.is_active == True)
            .order_by(UserModel.nom, UserModel.prenom)
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

    def exists_by_code(self, code_utilisateur: str) -> bool:
        """
        Vérifie si un code utilisateur existe.

        Args:
            code_utilisateur: Le code à vérifier.

        Returns:
            True si le code existe.
        """
        return (
            self.session.query(UserModel)
            .filter(UserModel.code_utilisateur == code_utilisateur)
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
            type_utilisateur=TypeUtilisateur.from_string(model.type_utilisateur),
            is_active=model.is_active,
            couleur=Couleur(model.couleur) if model.couleur else Couleur.default(),
            photo_profil=model.photo_profil,
            code_utilisateur=model.code_utilisateur,
            telephone=model.telephone,
            metier=model.metier,
            contact_urgence_nom=model.contact_urgence_nom,
            contact_urgence_tel=model.contact_urgence_tel,
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
            type_utilisateur=user.type_utilisateur.value,
            is_active=user.is_active,
            couleur=str(user.couleur) if user.couleur else Couleur.DEFAULT,
            photo_profil=user.photo_profil,
            code_utilisateur=user.code_utilisateur,
            telephone=user.telephone,
            metier=user.metier,
            contact_urgence_nom=user.contact_urgence_nom,
            contact_urgence_tel=user.contact_urgence_tel,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
