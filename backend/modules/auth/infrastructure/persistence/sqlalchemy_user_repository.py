"""Implementation SQLAlchemy du UserRepository."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from ...domain.entities import User
from ...domain.repositories import UserRepository
from ...domain.value_objects import Email, PasswordHash, Role, TypeUtilisateur, Couleur
from .user_model import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """
    Implementation du UserRepository utilisant SQLAlchemy.

    Fait le mapping entre l'entite User (Domain) et UserModel (Infrastructure).
    Implemente le soft delete: les utilisateurs supprimes ont deleted_at != None.

    Attributes:
        session: Session SQLAlchemy pour les operations DB.
    """

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy active.
        """
        self.session = session

    def _not_deleted(self):
        """Filtre pour exclure les enregistrements supprimes (soft delete)."""
        return UserModel.deleted_at.is_(None)

    def find_by_id(self, user_id: int) -> Optional[User]:
        """
        Trouve un utilisateur par son ID (excluant les supprimes).

        Args:
            user_id: L'identifiant unique.

        Returns:
            L'entite User ou None.
        """
        model = (
            self.session.query(UserModel)
            .filter(UserModel.id == user_id)
            .filter(self._not_deleted())
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_email(self, email: Email) -> Optional[User]:
        """
        Trouve un utilisateur par son email (excluant les supprimes).

        Args:
            email: L'adresse email (Value Object).

        Returns:
            L'entite User ou None.
        """
        model = (
            self.session.query(UserModel)
            .filter(UserModel.email == str(email))
            .filter(self._not_deleted())
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_code(self, code_utilisateur: str) -> Optional[User]:
        """
        Trouve un utilisateur par son code/matricule (excluant les supprimes).

        Args:
            code_utilisateur: Le code utilisateur (matricule).

        Returns:
            L'entite User ou None.
        """
        model = (
            self.session.query(UserModel)
            .filter(UserModel.code_utilisateur == code_utilisateur)
            .filter(self._not_deleted())
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
                model.metiers = user.metiers
                model.taux_horaire = user.taux_horaire
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
        Supprime un utilisateur (soft delete - marque deleted_at).

        L'utilisateur n'est pas supprime physiquement de la base de donnees,
        mais marque comme supprime. Cela permet de conserver l'historique
        et de respecter les exigences RGPD (droit a l'oubli avec tracabilite).

        Args:
            user_id: L'identifiant de l'utilisateur.

        Returns:
            True si supprime, False si non trouve ou deja supprime.
        """
        model = (
            self.session.query(UserModel)
            .filter(UserModel.id == user_id)
            .filter(self._not_deleted())
            .first()
        )
        if model:
            # Soft delete: marquer comme supprime au lieu de supprimer physiquement
            model.deleted_at = datetime.now()
            self.session.commit()
            return True
        return False

    def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Recupere tous les utilisateurs avec pagination (excluant les supprimes).

        Args:
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des entites User.
        """
        models = (
            self.session.query(UserModel)
            .filter(self._not_deleted())
            .order_by(UserModel.nom, UserModel.prenom)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def count(self) -> int:
        """
        Compte le nombre total d'utilisateurs (excluant les supprimes).

        Returns:
            Nombre total d'utilisateurs.
        """
        return self.session.query(UserModel).filter(self._not_deleted()).count()

    def find_by_role(self, role: Role, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Trouve les utilisateurs par role (excluant les supprimes).

        Args:
            role: Le role a filtrer.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des entites User avec ce role.
        """
        models = (
            self.session.query(UserModel)
            .filter(UserModel.role == role.value)
            .filter(self._not_deleted())
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
        Trouve les utilisateurs par type (employe/sous-traitant) excluant les supprimes.

        Args:
            type_utilisateur: Le type a filtrer.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des entites User de ce type.
        """
        models = (
            self.session.query(UserModel)
            .filter(UserModel.type_utilisateur == type_utilisateur.value)
            .filter(self._not_deleted())
            .order_by(UserModel.nom, UserModel.prenom)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_active(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Trouve les utilisateurs actifs (excluant les supprimes).

        Args:
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des entites User actifs.
        """
        models = (
            self.session.query(UserModel)
            .filter(UserModel.is_active == True)
            .filter(self._not_deleted())
            .order_by(UserModel.nom, UserModel.prenom)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def exists_by_email(self, email: Email) -> bool:
        """
        Verifie si un email existe (excluant les supprimes).

        Args:
            email: L'email a verifier.

        Returns:
            True si l'email existe.
        """
        return (
            self.session.query(UserModel)
            .filter(UserModel.email == str(email))
            .filter(self._not_deleted())
            .first()
            is not None
        )

    def exists_by_code(self, code_utilisateur: str) -> bool:
        """
        Verifie si un code utilisateur existe (excluant les supprimes).

        Args:
            code_utilisateur: Le code a verifier.

        Returns:
            True si le code existe.
        """
        return (
            self.session.query(UserModel)
            .filter(UserModel.code_utilisateur == code_utilisateur)
            .filter(self._not_deleted())
            .first()
            is not None
        )

    def search(
        self,
        query: Optional[str] = None,
        role: Optional[Role] = None,
        type_utilisateur: Optional[TypeUtilisateur] = None,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[User], int]:
        """
        Recherche des utilisateurs avec filtres multiples (excluant les supprimes).

        Args:
            query: Texte a rechercher dans nom, prenom, email.
            role: Filtrer par role (optionnel).
            type_utilisateur: Filtrer par type (optionnel).
            active_only: Filtrer les actifs uniquement.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Tuple (liste des utilisateurs, total count).
        """
        from sqlalchemy import or_

        base_query = self.session.query(UserModel).filter(self._not_deleted())

        # Appliquer les filtres
        if query:
            search_term = f"%{query}%"
            base_query = base_query.filter(
                or_(
                    UserModel.nom.ilike(search_term),
                    UserModel.prenom.ilike(search_term),
                    UserModel.email.ilike(search_term),
                )
            )

        if role:
            base_query = base_query.filter(UserModel.role == role.value)

        if type_utilisateur:
            base_query = base_query.filter(UserModel.type_utilisateur == type_utilisateur.value)

        if active_only:
            base_query = base_query.filter(UserModel.is_active == True)

        # Compter le total avant pagination
        total = base_query.count()

        # Appliquer pagination et tri
        models = (
            base_query
            .order_by(UserModel.nom, UserModel.prenom)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return [self._to_entity(m) for m in models], total

    def find_by_password_reset_token(self, token: str) -> Optional[User]:
        """
        Trouve un utilisateur par son token de réinitialisation de mot de passe.

        Args:
            token: Le token de réinitialisation.

        Returns:
            L'utilisateur trouvé ou None.
        """
        model = (
            self.session.query(UserModel)
            .filter(UserModel.password_reset_token == token)
            .filter(self._not_deleted())
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_invitation_token(self, token: str) -> Optional[User]:
        """
        Trouve un utilisateur par son token d'invitation.

        Args:
            token: Le token d'invitation.

        Returns:
            L'utilisateur trouvé ou None.
        """
        model = (
            self.session.query(UserModel)
            .filter(UserModel.invitation_token == token)
            .filter(self._not_deleted())
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_email_verification_token(self, token: str) -> Optional[User]:
        """
        Trouve un utilisateur par son token de vérification d'email.

        Args:
            token: Le token de vérification.

        Returns:
            L'utilisateur trouvé ou None.
        """
        model = (
            self.session.query(UserModel)
            .filter(UserModel.email_verification_token == token)
            .filter(self._not_deleted())
            .first()
        )
        return self._to_entity(model) if model else None

    def _extract_base_attributes(self, model: UserModel) -> dict:
        """Extrait les attributs de base du modèle."""
        return {
            "id": model.id,
            "email": Email(model.email),
            "password_hash": PasswordHash(model.password_hash),
            "nom": model.nom,
            "prenom": model.prenom,
            "role": Role.from_string(model.role),
            "type_utilisateur": TypeUtilisateur.from_string(model.type_utilisateur),
            "is_active": model.is_active,
            "couleur": Couleur(model.couleur) if model.couleur else Couleur.default(),
            "photo_profil": model.photo_profil,
            "code_utilisateur": model.code_utilisateur,
            "telephone": model.telephone,
            "metiers": model.metiers,
            "taux_horaire": model.taux_horaire,
            "contact_urgence_nom": model.contact_urgence_nom,
            "contact_urgence_tel": model.contact_urgence_tel,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }

    def _extract_security_attributes(self, model: UserModel) -> dict:
        """Extrait les attributs de sécurité et tokens du modèle."""
        return {
            "password_reset_token": model.password_reset_token,
            "password_reset_expires_at": model.password_reset_expires_at,
            "invitation_token": model.invitation_token,
            "invitation_expires_at": model.invitation_expires_at,
            "email_verified_at": model.email_verified_at,
            "email_verification_token": model.email_verification_token,
            "failed_login_attempts": model.failed_login_attempts,
            "last_failed_login_at": model.last_failed_login_at,
            "locked_until": model.locked_until,
        }

    def _to_entity(self, model: UserModel) -> User:
        """
        Convertit un modèle SQLAlchemy en entité Domain.

        Args:
            model: Le modèle SQLAlchemy.

        Returns:
            L'entité User.
        """
        attributes = {
            **self._extract_base_attributes(model),
            **self._extract_security_attributes(model),
        }
        return User(**attributes)

    def _prepare_base_model_data(self, user: User) -> dict:
        """Prépare les données de base pour le modèle."""
        return {
            "id": user.id,
            "email": str(user.email),
            "password_hash": user.password_hash.value,
            "nom": user.nom,
            "prenom": user.prenom,
            "role": user.role.value,
            "type_utilisateur": user.type_utilisateur.value,
            "is_active": user.is_active,
            "couleur": str(user.couleur) if user.couleur else Couleur.DEFAULT,
            "photo_profil": user.photo_profil,
            "code_utilisateur": user.code_utilisateur,
            "telephone": user.telephone,
            "metiers": user.metiers,
            "taux_horaire": user.taux_horaire,
            "contact_urgence_nom": user.contact_urgence_nom,
            "contact_urgence_tel": user.contact_urgence_tel,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

    def _prepare_security_model_data(self, user: User) -> dict:
        """Prépare les données de sécurité pour le modèle."""
        return {
            "password_reset_token": user.password_reset_token,
            "password_reset_expires_at": user.password_reset_expires_at,
            "invitation_token": user.invitation_token,
            "invitation_expires_at": user.invitation_expires_at,
            "email_verified_at": user.email_verified_at,
            "email_verification_token": user.email_verification_token,
            "failed_login_attempts": user.failed_login_attempts,
            "last_failed_login_at": user.last_failed_login_at,
            "locked_until": user.locked_until,
        }

    def _to_model(self, user: User) -> UserModel:
        """
        Convertit une entité Domain en modèle SQLAlchemy.

        Args:
            user: L'entité User.

        Returns:
            Le modèle UserModel.
        """
        model_data = {
            **self._prepare_base_model_data(user),
            **self._prepare_security_model_data(user),
        }
        return UserModel(**model_data)
