"""Exceptions du domaine authentification."""


class UserNotFoundError(Exception):
    """Exception levée quand un utilisateur n'est pas trouvé."""

    def __init__(self, message: str = "Utilisateur non trouvé"):
        self.message = message
        super().__init__(self.message)


class InvalidCredentialsError(Exception):
    """Exception levée quand les identifiants sont invalides."""

    def __init__(self, message: str = "Email ou mot de passe incorrect"):
        self.message = message
        super().__init__(self.message)


class UserInactiveError(Exception):
    """Exception levée quand le compte est désactivé."""

    def __init__(self, message: str = "Ce compte a été désactivé"):
        self.message = message
        super().__init__(self.message)


class EmailAlreadyExistsError(Exception):
    """Exception levée quand un email existe déjà."""

    def __init__(self, message: str = "Cet email est déjà utilisé"):
        self.message = message
        super().__init__(self.message)


class CodeAlreadyExistsError(Exception):
    """Exception levée quand un code utilisateur existe déjà."""

    def __init__(self, message: str = "Ce code utilisateur est déjà utilisé"):
        self.message = message
        super().__init__(self.message)


class WeakPasswordError(Exception):
    """Exception levée quand un mot de passe est trop faible."""

    def __init__(
        self,
        message: str = "Le mot de passe doit contenir au moins 8 caractères, "
        "une majuscule, une minuscule et un chiffre",
    ):
        self.message = message
        super().__init__(self.message)


class InvalidResetTokenError(Exception):
    """Exception levée quand un token de réinitialisation est invalide ou expiré."""

    def __init__(self, message: str = "Token de réinitialisation invalide ou expiré"):
        self.message = message
        super().__init__(self.message)


class InvalidInvitationTokenError(Exception):
    """Exception levée quand un token d'invitation est invalide ou expiré."""

    def __init__(self, message: str = "Token d'invitation invalide ou expiré"):
        self.message = message
        super().__init__(self.message)


class InvalidVerificationTokenError(Exception):
    """Exception levée quand un token de vérification d'email est invalide."""

    def __init__(self, message: str = "Token de vérification invalide"):
        self.message = message
        super().__init__(self.message)


class AccountLockedError(Exception):
    """Exception levée quand un compte est verrouillé suite à trop de tentatives échouées."""

    def __init__(self, message: str = "Compte temporairement verrouillé suite à trop de tentatives échouées"):
        self.message = message
        self.locked_until = None  # Peut être renseigné par le use case

        super().__init__(self.message)
