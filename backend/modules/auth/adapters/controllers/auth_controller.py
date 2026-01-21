"""AuthController - Gestion des requêtes d'authentification."""

from typing import Dict, Any

from ...application.use_cases import (
    LoginUseCase,
    RegisterUseCase,
    GetCurrentUserUseCase,
)
from ...application.dtos import LoginDTO, RegisterDTO


class AuthController:
    """
    Controller pour les opérations d'authentification.

    Fait le pont entre les requêtes HTTP et les Use Cases.
    Convertit les données brutes en DTOs et formate les réponses.

    Attributes:
        login_use_case: Use case pour la connexion.
        register_use_case: Use case pour l'inscription.
        get_current_user_use_case: Use case pour récupérer l'utilisateur.
    """

    def __init__(
        self,
        login_use_case: LoginUseCase,
        register_use_case: RegisterUseCase,
        get_current_user_use_case: GetCurrentUserUseCase,
    ):
        """
        Initialise le controller.

        Args:
            login_use_case: Use case de connexion.
            register_use_case: Use case d'inscription.
            get_current_user_use_case: Use case de récupération utilisateur.
        """
        self.login_use_case = login_use_case
        self.register_use_case = register_use_case
        self.get_current_user_use_case = get_current_user_use_case

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Traite une requête de connexion.

        Args:
            email: Email de l'utilisateur.
            password: Mot de passe en clair.

        Returns:
            Dictionnaire avec user et token.

        Raises:
            InvalidCredentialsError: Si identifiants invalides.
            UserInactiveError: Si compte désactivé.
        """
        dto = LoginDTO(email=email, password=password)
        result = self.login_use_case.execute(dto)

        return {
            "user": {
                "id": result.user.id,
                "email": result.user.email,
                "nom": result.user.nom,
                "prenom": result.user.prenom,
                "role": result.user.role,
                "is_active": result.user.is_active,
            },
            "access_token": result.token.access_token,
            "token_type": result.token.token_type,
        }

    def register(
        self,
        email: str,
        password: str,
        nom: str,
        prenom: str,
        role: str = None,
    ) -> Dict[str, Any]:
        """
        Traite une requête d'inscription.

        Args:
            email: Email du nouvel utilisateur.
            password: Mot de passe.
            nom: Nom de famille.
            prenom: Prénom.
            role: Rôle (optionnel, défaut: employe).

        Returns:
            Dictionnaire avec user et token.

        Raises:
            EmailAlreadyExistsError: Si email déjà utilisé.
            WeakPasswordError: Si mot de passe trop faible.
        """
        dto = RegisterDTO(
            email=email,
            password=password,
            nom=nom,
            prenom=prenom,
            role=role,
        )
        result = self.register_use_case.execute(dto)

        return {
            "user": {
                "id": result.user.id,
                "email": result.user.email,
                "nom": result.user.nom,
                "prenom": result.user.prenom,
                "role": result.user.role,
                "is_active": result.user.is_active,
            },
            "access_token": result.token.access_token,
            "token_type": result.token.token_type,
        }

    def get_current_user(self, token: str) -> Dict[str, Any]:
        """
        Récupère l'utilisateur connecté.

        Args:
            token: Le JWT token.

        Returns:
            Dictionnaire avec les informations utilisateur.

        Raises:
            InvalidTokenError: Si token invalide.
            UserNotFoundError: Si utilisateur non trouvé.
        """
        result = self.get_current_user_use_case.execute(token)

        return {
            "id": result.id,
            "email": result.email,
            "nom": result.nom,
            "prenom": result.prenom,
            "role": result.role,
            "is_active": result.is_active,
        }

    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """
        Récupère un utilisateur par son ID.

        Args:
            user_id: L'ID de l'utilisateur.

        Returns:
            Dictionnaire avec les informations utilisateur.

        Raises:
            UserNotFoundError: Si utilisateur non trouvé.
        """
        result = self.get_current_user_use_case.execute_from_id(user_id)

        return {
            "id": result.id,
            "email": result.email,
            "nom": result.nom,
            "prenom": result.prenom,
            "role": result.role,
            "is_active": result.is_active,
        }
