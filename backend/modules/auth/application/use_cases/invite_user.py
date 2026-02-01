"""Use case pour inviter un utilisateur."""

import secrets
from datetime import datetime, timedelta
from typing import Optional, List
from decimal import Decimal

from ...domain.repositories.user_repository import UserRepository
from ...domain.entities import User
from ...domain.value_objects import Email, PasswordHash, Role, TypeUtilisateur
from ...domain.exceptions import EmailAlreadyExistsError, CodeAlreadyExistsError
from shared.infrastructure.email_service import email_service


class InviteUserUseCase:
    """
    Use case pour inviter un nouvel utilisateur.

    Crée un compte pré-rempli avec un token d'invitation et envoie un email.
    """

    def __init__(self, user_repository: UserRepository) -> None:
        """
        Initialise le use case.

        Args:
            user_repository: Repository des utilisateurs.
        """
        self.user_repository = user_repository

    def execute(
        self,
        email: str,
        nom: str,
        prenom: str,
        role: Role,
        type_utilisateur: TypeUtilisateur = TypeUtilisateur.EMPLOYE,
        code_utilisateur: Optional[str] = None,
        metiers: Optional[List[str]] = None,
        taux_horaire: Optional[Decimal] = None,
        inviter_name: str = "L'équipe Hub Chantier",
    ) -> User:
        """
        Invite un nouvel utilisateur.

        Args:
            email: Email de l'utilisateur invité.
            nom: Nom de famille.
            prenom: Prénom.
            role: Rôle assigné.
            type_utilisateur: Type (employé ou sous-traitant).
            code_utilisateur: Code/matricule optionnel.
            metiers: Liste de métiers/spécialités optionnel.
            taux_horaire: Taux horaire en EUR (optionnel, module financier).
            inviter_name: Nom de la personne qui invite.

        Returns:
            L'utilisateur créé.

        Raises:
            EmailAlreadyExistsError: Si l'email existe déjà.
            CodeAlreadyExistsError: Si le code utilisateur existe déjà.
        """
        # Vérifier que l'email n'existe pas déjà
        email_obj = Email(email)
        if self.user_repository.exists_by_email(email_obj):
            raise EmailAlreadyExistsError(f"L'email {email} est déjà utilisé")

        # Vérifier que le code utilisateur n'existe pas déjà (si fourni)
        if code_utilisateur and self.user_repository.exists_by_code(code_utilisateur):
            raise CodeAlreadyExistsError(
                f"Le code utilisateur {code_utilisateur} est déjà utilisé"
            )

        # Générer un token d'invitation sécurisé
        invitation_token = secrets.token_urlsafe(32)
        invitation_expires_at = datetime.now() + timedelta(days=7)

        # Créer l'utilisateur avec un mot de passe temporaire
        # (sera remplacé lors de l'acceptation de l'invitation)
        temporary_password_hash = PasswordHash("TEMPORARY_HASH_WILL_BE_REPLACED")

        user = User(
            email=email_obj,
            password_hash=temporary_password_hash,
            nom=nom,
            prenom=prenom,
            role=role,
            type_utilisateur=type_utilisateur,
            code_utilisateur=code_utilisateur,
            metiers=metiers,
            taux_horaire=taux_horaire,
            is_active=False,  # Inactif tant que l'invitation n'est pas acceptée
        )

        # Définir le token d'invitation
        user.set_invitation_token(invitation_token, invitation_expires_at)

        # Sauvegarder l'utilisateur
        saved_user = self.user_repository.save(user)

        # Envoyer l'email d'invitation
        email_service.send_invitation_email(
            to=email,
            token=invitation_token,
            user_name=user.nom_complet,
            inviter_name=inviter_name,
            role=role.value,
        )

        return saved_user
