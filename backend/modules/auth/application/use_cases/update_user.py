"""Use Case UpdateUser - Mise à jour d'un utilisateur."""

from typing import Callable, Optional

from ...domain.repositories import UserRepository
from ...domain.value_objects import Role, TypeUtilisateur, Couleur
from ...domain.events import UserUpdatedEvent
from ..dtos import UpdateUserDTO, UserDTO


class UserNotFoundError(Exception):
    """Exception levée quand l'utilisateur n'est pas trouvé."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.message = f"Utilisateur {user_id} non trouvé"
        super().__init__(self.message)


class CodeAlreadyExistsError(Exception):
    """Exception levée quand le code utilisateur est déjà utilisé."""

    def __init__(self, code: str):
        self.code = code
        self.message = f"Le code utilisateur {code} est déjà utilisé"
        super().__init__(self.message)


class UpdateUserUseCase:
    """
    Cas d'utilisation : Mise à jour d'un utilisateur.

    Permet de modifier les informations d'un utilisateur existant.
    Selon CDC Section 3 - Gestion des Utilisateurs.

    Attributes:
        user_repo: Repository pour accéder aux utilisateurs.
        event_publisher: Fonction pour publier les events (optionnel).
    """

    def __init__(
        self,
        user_repo: UserRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            user_repo: Repository utilisateurs (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.user_repo = user_repo
        self.event_publisher = event_publisher

    def execute(self, user_id: int, dto: UpdateUserDTO) -> UserDTO:
        """
        Exécute la mise à jour.

        Args:
            user_id: ID de l'utilisateur à mettre à jour.
            dto: Les données de mise à jour.

        Returns:
            UserDTO de l'utilisateur mis à jour.

        Raises:
            UserNotFoundError: Si l'utilisateur n'existe pas.
            CodeAlreadyExistsError: Si le nouveau code est déjà utilisé.
            ValueError: Si les données sont invalides.
        """
        # Récupérer l'utilisateur
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Vérifier le code utilisateur si modifié
        if dto.code_utilisateur and dto.code_utilisateur != user.code_utilisateur:
            if self.user_repo.exists_by_code(dto.code_utilisateur):
                raise CodeAlreadyExistsError(dto.code_utilisateur)
            user.code_utilisateur = dto.code_utilisateur

        # Mettre à jour les champs du profil
        couleur = None
        if dto.couleur:
            couleur = Couleur(dto.couleur)

        user.update_profile(
            nom=dto.nom,
            prenom=dto.prenom,
            telephone=dto.telephone,
            metiers=dto.metiers,
            taux_horaire=dto.taux_horaire,
            couleur=couleur,
            photo_profil=dto.photo_profil,
            contact_urgence_nom=dto.contact_urgence_nom,
            contact_urgence_tel=dto.contact_urgence_tel,
        )

        # Mettre à jour le rôle si spécifié
        if dto.role:
            new_role = Role.from_string(dto.role)
            user.change_role(new_role)

        # Mettre à jour le type utilisateur si spécifié
        if dto.type_utilisateur:
            user.type_utilisateur = TypeUtilisateur.from_string(dto.type_utilisateur)

        # Sauvegarder
        user = self.user_repo.save(user)

        # Publier l'event
        if self.event_publisher:
            event = UserUpdatedEvent(
                user_id=user.id,
                email=str(user.email),
                nom=user.nom,
                prenom=user.prenom,
            )
            self.event_publisher(event)

        return UserDTO.from_entity(user)
