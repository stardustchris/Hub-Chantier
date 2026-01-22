"""Use Case Register - Inscription d'un nouvel utilisateur."""

from ...domain.entities import User
from ...domain.repositories import UserRepository
from ...domain.services import PasswordService
from ...domain.value_objects import Email, Role, TypeUtilisateur, Couleur
from ...domain.events import UserCreatedEvent
from ..ports import TokenService
from ..dtos import RegisterDTO, AuthResponseDTO, UserDTO, TokenDTO


class EmailAlreadyExistsError(Exception):
    """Exception levée quand l'email est déjà utilisé."""

    def __init__(self, email: str):
        self.email = email
        self.message = f"L'email {email} est déjà utilisé"
        super().__init__(self.message)


class CodeAlreadyExistsError(Exception):
    """Exception levée quand le code utilisateur est déjà utilisé."""

    def __init__(self, code: str):
        self.code = code
        self.message = f"Le code utilisateur {code} est déjà utilisé"
        super().__init__(self.message)


class WeakPasswordError(Exception):
    """Exception levée quand le mot de passe est trop faible."""

    def __init__(
        self,
        message: str = "Le mot de passe doit contenir au moins 8 caractères, "
        "une majuscule, une minuscule et un chiffre",
    ):
        self.message = message
        super().__init__(self.message)


class RegisterUseCase:
    """
    Cas d'utilisation : Inscription d'un nouvel utilisateur.

    Crée un compte utilisateur et retourne un token JWT.
    Selon CDC Section 3 - Gestion des Utilisateurs (USR-01 à USR-13).

    Attributes:
        user_repo: Repository pour accéder aux utilisateurs.
        password_service: Service pour hasher les mots de passe.
        token_service: Service pour générer les tokens.
        event_publisher: Fonction pour publier les events (optionnel).
    """

    def __init__(
        self,
        user_repo: UserRepository,
        password_service: PasswordService,
        token_service: TokenService,
        event_publisher: callable = None,
    ):
        """
        Initialise le use case.

        Args:
            user_repo: Repository utilisateurs (interface).
            password_service: Service de hash (interface).
            token_service: Service de tokens (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.user_repo = user_repo
        self.password_service = password_service
        self.token_service = token_service
        self.event_publisher = event_publisher

    def execute(self, dto: RegisterDTO) -> AuthResponseDTO:
        """
        Exécute l'inscription.

        Args:
            dto: Les données d'inscription.

        Returns:
            AuthResponseDTO contenant le user et le token.

        Raises:
            EmailAlreadyExistsError: Si l'email est déjà utilisé.
            CodeAlreadyExistsError: Si le code utilisateur est déjà utilisé.
            WeakPasswordError: Si le mot de passe est trop faible.
            ValueError: Si les données sont invalides.
        """
        # Valider l'email
        email = Email(dto.email)

        # Vérifier que l'email n'existe pas
        if self.user_repo.exists_by_email(email):
            raise EmailAlreadyExistsError(dto.email)

        # Vérifier que le code utilisateur n'existe pas (si fourni)
        if dto.code_utilisateur and self.user_repo.exists_by_code(dto.code_utilisateur):
            raise CodeAlreadyExistsError(dto.code_utilisateur)

        # Valider la force du mot de passe
        if not self.password_service.validate_strength(dto.password):
            raise WeakPasswordError()

        # Hasher le mot de passe
        password_hash = self.password_service.hash(dto.password)

        # Déterminer le rôle (défaut: COMPAGNON)
        role = Role.COMPAGNON
        if dto.role:
            role = Role.from_string(dto.role)

        # Déterminer le type utilisateur (défaut: EMPLOYE)
        type_utilisateur = TypeUtilisateur.EMPLOYE
        if dto.type_utilisateur:
            type_utilisateur = TypeUtilisateur.from_string(dto.type_utilisateur)

        # Déterminer la couleur (défaut: bleu clair)
        couleur = Couleur.default()
        if dto.couleur:
            couleur = Couleur(dto.couleur)

        # Créer l'utilisateur avec tous les champs CDC
        user = User(
            email=email,
            password_hash=password_hash,
            nom=dto.nom,
            prenom=dto.prenom,
            role=role,
            type_utilisateur=type_utilisateur,
            couleur=couleur,
            telephone=dto.telephone,
            metier=dto.metier,
            code_utilisateur=dto.code_utilisateur,
        )

        # Sauvegarder
        user = self.user_repo.save(user)

        # Générer le token
        access_token = self.token_service.generate(user)

        # Publier l'event
        if self.event_publisher:
            event = UserCreatedEvent(
                user_id=user.id,
                email=str(user.email),
                nom=user.nom,
                prenom=user.prenom,
                role=user.role,
            )
            self.event_publisher(event)

        # Retourner la réponse
        return AuthResponseDTO(
            user=UserDTO.from_entity(user),
            token=TokenDTO(access_token=access_token),
        )
