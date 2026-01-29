"""AuthController - Gestion des requêtes d'authentification et utilisateurs."""

from typing import Dict, Any, Optional

from ...application.use_cases import (
    LoginUseCase,
    RegisterUseCase,
    GetCurrentUserUseCase,
    UpdateUserUseCase,
    DeactivateUserUseCase,
    ActivateUserUseCase,
    ListUsersUseCase,
    GetUserByIdUseCase,
)
from ...application.dtos import LoginDTO, RegisterDTO, UpdateUserDTO


class AuthController:
    """
    Controller pour les opérations d'authentification et gestion des utilisateurs.

    Fait le pont entre les requêtes HTTP et les Use Cases.
    Convertit les données brutes en DTOs et formate les réponses.
    Selon CDC Section 3 - Gestion des Utilisateurs (USR-01 à USR-13).
    """

    def __init__(
        self,
        login_use_case: LoginUseCase,
        register_use_case: RegisterUseCase,
        get_current_user_use_case: GetCurrentUserUseCase,
        update_user_use_case: UpdateUserUseCase = None,
        deactivate_user_use_case: DeactivateUserUseCase = None,
        activate_user_use_case: ActivateUserUseCase = None,
        list_users_use_case: ListUsersUseCase = None,
        get_user_by_id_use_case: GetUserByIdUseCase = None,
    ):
        """
        Initialise le controller.

        Args:
            login_use_case: Use case de connexion.
            register_use_case: Use case d'inscription.
            get_current_user_use_case: Use case de récupération utilisateur par token.
            update_user_use_case: Use case de mise à jour utilisateur.
            deactivate_user_use_case: Use case de désactivation.
            activate_user_use_case: Use case d'activation.
            list_users_use_case: Use case de liste des utilisateurs.
            get_user_by_id_use_case: Use case de récupération par ID.
        """
        self.login_use_case = login_use_case
        self.register_use_case = register_use_case
        self.get_current_user_use_case = get_current_user_use_case
        self.update_user_use_case = update_user_use_case
        self.deactivate_user_use_case = deactivate_user_use_case
        self.activate_user_use_case = activate_user_use_case
        self.list_users_use_case = list_users_use_case
        self.get_user_by_id_use_case = get_user_by_id_use_case

    def _user_dto_to_dict(self, user_dto) -> Dict[str, Any]:
        """Convertit un UserDTO en dictionnaire compatible frontend."""
        return {
            "id": str(user_dto.id),  # Converti en string pour frontend
            "email": user_dto.email,
            "nom": user_dto.nom,
            "prenom": user_dto.prenom,
            "nom_complet": user_dto.nom_complet,
            "initiales": user_dto.initiales,
            "role": user_dto.role,
            "type_utilisateur": user_dto.type_utilisateur,
            "is_active": user_dto.is_active,
            "couleur": user_dto.couleur,
            "photo_profil": user_dto.photo_profil,
            "code_utilisateur": user_dto.code_utilisateur,
            "telephone": user_dto.telephone,
            "metier": user_dto.metier,
            "contact_urgence_nom": user_dto.contact_urgence_nom,
            "contact_urgence_telephone": user_dto.contact_urgence_tel,  # Renommé pour frontend
            "created_at": user_dto.created_at,
            "updated_at": getattr(user_dto, 'updated_at', None),  # Ajouté pour frontend
        }

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
            "user": self._user_dto_to_dict(result.user),
            "access_token": result.token.access_token,
            "token_type": result.token.token_type,
        }

    def register(
        self,
        email: str,
        password: str,
        nom: str,
        prenom: str,
        type_utilisateur: Optional[str] = None,
        telephone: Optional[str] = None,
        metier: Optional[str] = None,
        code_utilisateur: Optional[str] = None,
        couleur: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Traite une requête d'inscription (USR-01).

        Le rôle est forcé à COMPAGNON côté serveur (sécurité).

        Args:
            email: Email du nouvel utilisateur.
            password: Mot de passe.
            nom: Nom de famille.
            prenom: Prénom.
            type_utilisateur: Type (optionnel, défaut: employe).
            telephone: Numéro de téléphone.
            metier: Métier/spécialité.
            code_utilisateur: Matricule.
            couleur: Couleur d'identification.

        Returns:
            Dictionnaire avec user et token.

        Raises:
            EmailAlreadyExistsError: Si email déjà utilisé.
            CodeAlreadyExistsError: Si code utilisateur déjà utilisé.
            WeakPasswordError: Si mot de passe trop faible.
        """
        dto = RegisterDTO(
            email=email,
            password=password,
            nom=nom,
            prenom=prenom,
            type_utilisateur=type_utilisateur,
            telephone=telephone,
            metier=metier,
            code_utilisateur=code_utilisateur,
            couleur=couleur,
        )
        result = self.register_use_case.execute(dto)

        return {
            "user": self._user_dto_to_dict(result.user),
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
        return self._user_dto_to_dict(result)

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
        if self.get_user_by_id_use_case:
            result = self.get_user_by_id_use_case.execute(user_id)
            if result:
                return self._user_dto_to_dict(result)
        # Fallback sur la méthode existante
        result = self.get_current_user_use_case.execute_from_id(user_id)
        return self._user_dto_to_dict(result)

    def update_user(
        self,
        user_id: int,
        nom: Optional[str] = None,
        prenom: Optional[str] = None,
        telephone: Optional[str] = None,
        metier: Optional[str] = None,
        couleur: Optional[str] = None,
        photo_profil: Optional[str] = None,
        contact_urgence_nom: Optional[str] = None,
        contact_urgence_tel: Optional[str] = None,
        role: Optional[str] = None,
        type_utilisateur: Optional[str] = None,
        code_utilisateur: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Met à jour un utilisateur.

        Args:
            user_id: ID de l'utilisateur.
            nom: Nouveau nom.
            prenom: Nouveau prénom.
            telephone: Nouveau téléphone.
            metier: Nouveau métier.
            couleur: Nouvelle couleur.
            photo_profil: Nouvelle URL photo.
            contact_urgence_nom: Nouveau contact urgence nom.
            contact_urgence_tel: Nouveau contact urgence tel.
            role: Nouveau rôle.
            type_utilisateur: Nouveau type.
            code_utilisateur: Nouveau code.

        Returns:
            Dictionnaire avec l'utilisateur mis à jour.

        Raises:
            UserNotFoundError: Si utilisateur non trouvé.
            CodeAlreadyExistsError: Si le code est déjà utilisé.
        """
        dto = UpdateUserDTO(
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            metier=metier,
            couleur=couleur,
            photo_profil=photo_profil,
            contact_urgence_nom=contact_urgence_nom,
            contact_urgence_tel=contact_urgence_tel,
            role=role,
            type_utilisateur=type_utilisateur,
            code_utilisateur=code_utilisateur,
        )
        result = self.update_user_use_case.execute(user_id, dto)
        return self._user_dto_to_dict(result)

    def deactivate_user(self, user_id: int) -> Dict[str, Any]:
        """
        Désactive un utilisateur (USR-10).

        Args:
            user_id: ID de l'utilisateur.

        Returns:
            Dictionnaire avec l'utilisateur désactivé.

        Raises:
            UserNotFoundError: Si utilisateur non trouvé.
        """
        result = self.deactivate_user_use_case.execute(user_id)
        return self._user_dto_to_dict(result)

    def activate_user(self, user_id: int) -> Dict[str, Any]:
        """
        Active un utilisateur.

        Args:
            user_id: ID de l'utilisateur.

        Returns:
            Dictionnaire avec l'utilisateur activé.

        Raises:
            UserNotFoundError: Si utilisateur non trouvé.
        """
        result = self.activate_user_use_case.execute(user_id)
        return self._user_dto_to_dict(result)

    def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        role: Optional[str] = None,
        type_utilisateur: Optional[str] = None,
        active_only: bool = False,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Liste les utilisateurs avec pagination (USR-09).

        Args:
            skip: Offset.
            limit: Limite.
            role: Filtrer par rôle.
            type_utilisateur: Filtrer par type.
            active_only: Filtrer les actifs.
            search: Recherche textuelle.

        Returns:
            Dictionnaire avec la liste paginée.
        """
        result = self.list_users_use_case.execute(
            skip=skip,
            limit=limit,
            role=role,
            type_utilisateur=type_utilisateur,
            active_only=active_only,
            search=search,
        )
        return {
            "users": [self._user_dto_to_dict(u) for u in result.users],
            "total": result.total,
            "skip": result.skip,
            "limit": result.limit,
            "has_next": result.has_next,
            "has_previous": result.has_previous,
        }
