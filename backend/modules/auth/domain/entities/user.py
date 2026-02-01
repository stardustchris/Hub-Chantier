"""Entité User - Représente un utilisateur du système."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from ..value_objects import Email, PasswordHash, Role, TypeUtilisateur, Couleur


@dataclass
class User:
    """
    Entité représentant un utilisateur.

    L'utilisateur est identifié par son ID unique.
    Contient la logique métier liée à l'authentification et au profil.

    Selon CDC Section 3 - Gestion des Utilisateurs (USR-01 à USR-13).

    Attributes:
        id: Identifiant unique (None si non persisté).
        email: Adresse email professionnelle (USR-12).
        password_hash: Hash du mot de passe.
        nom: Nom de famille.
        prenom: Prénom.
        role: Rôle dans l'application (USR-06).
        type_utilisateur: Employé ou Sous-traitant (USR-05).
        is_active: Statut activé/désactivé (USR-04, USR-10).
        couleur: Couleur d'identification visuelle (USR-03).
        photo_profil: URL de la photo de profil (USR-02).
        code_utilisateur: Matricule pour export paie (USR-07).
        telephone: Numéro mobile (USR-08).
        metiers: Liste de métiers/spécialités (USR-11).
        taux_horaire: Taux horaire en EUR (FIN-09).
        contact_urgence_nom: Nom du contact d'urgence (USR-13).
        contact_urgence_tel: Téléphone du contact d'urgence (USR-13).
        created_at: Date de création.
        updated_at: Date de dernière modification.
    """

    # Champs obligatoires
    email: Email
    password_hash: PasswordHash
    nom: str
    prenom: str

    # Champs avec valeurs par défaut
    role: Role = Role.COMPAGNON
    type_utilisateur: TypeUtilisateur = TypeUtilisateur.EMPLOYE
    id: Optional[int] = None
    is_active: bool = True
    couleur: Optional[Couleur] = None
    photo_profil: Optional[str] = None
    code_utilisateur: Optional[str] = None
    telephone: Optional[str] = None
    metiers: Optional[List[str]] = None
    taux_horaire: Optional[Decimal] = None
    contact_urgence_nom: Optional[str] = None
    contact_urgence_tel: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Password reset
    password_reset_token: Optional[str] = None
    password_reset_expires_at: Optional[datetime] = None

    # Invitation
    invitation_token: Optional[str] = None
    invitation_expires_at: Optional[datetime] = None

    # Email verification
    email_verified_at: Optional[datetime] = None
    email_verification_token: Optional[str] = None

    # Account lockout (protection brute force)
    failed_login_attempts: int = 0
    last_failed_login_at: Optional[datetime] = None
    locked_until: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Valide les données à la création."""
        if not self.nom or not self.nom.strip():
            raise ValueError("Le nom ne peut pas être vide")
        if not self.prenom or not self.prenom.strip():
            raise ValueError("Le prénom ne peut pas être vide")

        # Validation taux horaire (FIN-09)
        if self.taux_horaire is not None:
            self._validate_taux_horaire(self.taux_horaire)

        # Normalisation
        self.nom = self.nom.strip().upper()
        self.prenom = self.prenom.strip().title()

        # Couleur par défaut si non spécifiée
        if self.couleur is None:
            self.couleur = Couleur.default()

    @staticmethod
    def _validate_taux_horaire(taux: Decimal) -> None:
        """
        Valide le taux horaire selon les règles métier.

        Règles (FIN-09) :
        - Minimum : 11.00 EUR/h (SMIC 2026)
        - Maximum : 200.00 EUR/h (cadre supérieur)
        - Précision : 2 décimales maximum

        Args:
            taux: Taux horaire à valider.

        Raises:
            ValueError: Si le taux horaire est invalide.
        """
        # Constantes métier
        SMIC_HORAIRE = Decimal("11.00")  # SMIC 2026 (ajuster annuellement)
        TAUX_MAX_CADRE = Decimal("200.00")  # Cadre supérieur

        if taux < SMIC_HORAIRE:
            raise ValueError(
                f"Le taux horaire ({taux} EUR/h) est inférieur au SMIC ({SMIC_HORAIRE} EUR/h)"
            )

        if taux > TAUX_MAX_CADRE:
            raise ValueError(
                f"Le taux horaire ({taux} EUR/h) dépasse le maximum autorisé ({TAUX_MAX_CADRE} EUR/h)"
            )

        # Vérifier précision (max 2 décimales)
        if taux.as_tuple().exponent < -2:
            raise ValueError(
                "Le taux horaire ne peut avoir plus de 2 décimales"
            )

    @property
    def nom_complet(self) -> str:
        """Retourne le nom complet de l'utilisateur."""
        return f"{self.prenom} {self.nom}"

    @property
    def initiales(self) -> str:
        """Retourne les initiales de l'utilisateur."""
        return f"{self.prenom[0]}{self.nom[0]}".upper()

    def has_permission(self, permission: str) -> bool:
        """
        Vérifie si l'utilisateur a une permission.

        Args:
            permission: La permission à vérifier.

        Returns:
            True si l'utilisateur a la permission et est actif.
        """
        if not self.is_active:
            return False
        return self.role.has_permission(permission)

    def can_access_web(self) -> bool:
        """Vérifie si l'utilisateur peut accéder à l'interface web."""
        return self.is_active and self.role.can_access_web()

    def can_access_mobile(self) -> bool:
        """Vérifie si l'utilisateur peut accéder à l'application mobile."""
        return self.is_active and self.role.can_access_mobile()

    def is_admin(self) -> bool:
        """Vérifie si l'utilisateur est administrateur."""
        return self.role == Role.ADMIN

    def is_conducteur(self) -> bool:
        """Vérifie si l'utilisateur est conducteur de travaux."""
        return self.role == Role.CONDUCTEUR

    def is_chef_chantier(self) -> bool:
        """Vérifie si l'utilisateur est chef de chantier."""
        return self.role == Role.CHEF_CHANTIER

    def is_compagnon(self) -> bool:
        """Vérifie si l'utilisateur est compagnon."""
        return self.role == Role.COMPAGNON

    def is_sous_traitant(self) -> bool:
        """Vérifie si l'utilisateur est un sous-traitant."""
        return self.type_utilisateur == TypeUtilisateur.SOUS_TRAITANT

    def deactivate(self) -> None:
        """Désactive le compte utilisateur (USR-10 - révocation instantanée)."""
        self.is_active = False
        self.updated_at = datetime.now()

    def activate(self) -> None:
        """Active le compte utilisateur."""
        self.is_active = True
        self.updated_at = datetime.now()

    def change_role(self, new_role: Role) -> None:
        """
        Change le rôle de l'utilisateur.

        Args:
            new_role: Le nouveau rôle.
        """
        self.role = new_role
        self.updated_at = datetime.now()

    def update_password(self, new_password_hash: PasswordHash) -> None:
        """
        Met à jour le mot de passe.

        Args:
            new_password_hash: Le nouveau hash du mot de passe.
        """
        self.password_hash = new_password_hash
        self.updated_at = datetime.now()
        # Reset des tokens de réinitialisation si existants
        self.password_reset_token = None
        self.password_reset_expires_at = None

    def set_password_reset_token(self, token: str, expires_at: datetime) -> None:
        """
        Définit le token de réinitialisation de mot de passe.

        Args:
            token: Le token de réinitialisation.
            expires_at: Date d'expiration du token.
        """
        self.password_reset_token = token
        self.password_reset_expires_at = expires_at
        self.updated_at = datetime.now()

    def is_password_reset_token_valid(self) -> bool:
        """Vérifie si le token de reset est valide (non expiré)."""
        if not self.password_reset_token or not self.password_reset_expires_at:
            return False
        return datetime.now() < self.password_reset_expires_at

    def set_invitation_token(self, token: str, expires_at: datetime) -> None:
        """
        Définit le token d'invitation.

        Args:
            token: Le token d'invitation.
            expires_at: Date d'expiration du token.
        """
        self.invitation_token = token
        self.invitation_expires_at = expires_at
        self.is_active = False  # Compte inactif tant que non accepté
        self.updated_at = datetime.now()

    def is_invitation_token_valid(self) -> bool:
        """Vérifie si le token d'invitation est valide (non expiré)."""
        if not self.invitation_token or not self.invitation_expires_at:
            return False
        return datetime.now() < self.invitation_expires_at

    def accept_invitation(self, password_hash: PasswordHash) -> None:
        """
        Accepte une invitation et active le compte.

        Args:
            password_hash: Hash du mot de passe choisi par l'utilisateur.
        """
        self.password_hash = password_hash
        self.invitation_token = None
        self.invitation_expires_at = None
        self.is_active = True
        self.updated_at = datetime.now()

    def verify_email(self) -> None:
        """Marque l'email comme vérifié."""
        self.email_verified_at = datetime.now()
        self.email_verification_token = None
        self.updated_at = datetime.now()

    def set_email_verification_token(self, token: str) -> None:
        """
        Définit le token de vérification d'email.

        Args:
            token: Le token de vérification.
        """
        self.email_verification_token = token
        self.updated_at = datetime.now()

    def is_email_verified(self) -> bool:
        """Vérifie si l'email a été vérifié."""
        return self.email_verified_at is not None

    def record_failed_login(self) -> None:
        """Enregistre une tentative de connexion échouée."""
        self.failed_login_attempts += 1
        self.last_failed_login_at = datetime.now()
        # Lock account après 5 tentatives échouées (15 minutes)
        if self.failed_login_attempts >= 5:
            from datetime import timedelta
            self.locked_until = datetime.now() + timedelta(minutes=15)

    def reset_failed_login_attempts(self) -> None:
        """Réinitialise les tentatives de connexion échouées."""
        self.failed_login_attempts = 0
        self.last_failed_login_at = None
        self.locked_until = None

    def is_locked(self) -> bool:
        """Vérifie si le compte est verrouillé."""
        if not self.locked_until:
            return False
        if datetime.now() >= self.locked_until:
            # Débloquer automatiquement si la période est passée
            self.reset_failed_login_attempts()
            return False
        return True

    def update_profile(
        self,
        nom: Optional[str] = None,
        prenom: Optional[str] = None,
        telephone: Optional[str] = None,
        metiers: Optional[List[str]] = None,
        taux_horaire: Optional[Decimal] = None,
        couleur: Optional[Couleur] = None,
        photo_profil: Optional[str] = None,
        contact_urgence_nom: Optional[str] = None,
        contact_urgence_tel: Optional[str] = None,
    ) -> None:
        """
        Met à jour les informations du profil.

        Args:
            nom: Nouveau nom (optionnel).
            prenom: Nouveau prénom (optionnel).
            telephone: Nouveau téléphone (optionnel).
            metiers: Nouvelle liste de métiers (optionnel).
            taux_horaire: Nouveau taux horaire (optionnel, admin only).
            couleur: Nouvelle couleur (optionnel).
            photo_profil: Nouvelle URL photo (optionnel).
            contact_urgence_nom: Nouveau contact urgence nom (optionnel).
            contact_urgence_tel: Nouveau contact urgence tel (optionnel).
        """
        if nom is not None:
            if not nom.strip():
                raise ValueError("Le nom ne peut pas être vide")
            self.nom = nom.strip().upper()

        if prenom is not None:
            if not prenom.strip():
                raise ValueError("Le prénom ne peut pas être vide")
            self.prenom = prenom.strip().title()

        if telephone is not None:
            self.telephone = telephone

        if metiers is not None:
            self.metiers = metiers

        if taux_horaire is not None:
            self._validate_taux_horaire(taux_horaire)
            self.taux_horaire = taux_horaire

        if couleur is not None:
            self.couleur = couleur

        if photo_profil is not None:
            self.photo_profil = photo_profil

        if contact_urgence_nom is not None:
            self.contact_urgence_nom = contact_urgence_nom

        if contact_urgence_tel is not None:
            self.contact_urgence_tel = contact_urgence_tel

        self.updated_at = datetime.now()

    def __eq__(self, other: object) -> bool:
        """Égalité basée sur l'ID (entité)."""
        if not isinstance(other, User):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
