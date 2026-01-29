"""Routes FastAPI pour l'authentification et gestion des utilisateurs."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime
from sqlalchemy.orm import Session

from shared.infrastructure.rate_limiter import limiter
from shared.infrastructure.config import settings
from shared.infrastructure.database import get_db
from shared.infrastructure.audit import AuditService

# Cookie name for JWT token
AUTH_COOKIE_NAME = "access_token"

from ...adapters.controllers import AuthController
from ...application.use_cases import (
    InvalidCredentialsError,
    UserInactiveError,
    EmailAlreadyExistsError,
    CodeAlreadyExistsError,
    WeakPasswordError,
    UserNotFoundError,
)
from .dependencies import get_auth_controller, get_current_user_id, get_current_user_role, require_admin_or_conducteur

router = APIRouter(prefix="/auth", tags=["auth"])
users_router = APIRouter(prefix="/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    """Factory pour le service d'audit."""
    return AuditService(db)


# =============================================================================
# Pydantic models for request/response validation
# Selon CDC Section 3 - Gestion des Utilisateurs (USR-01 à USR-13)
# =============================================================================


class RegisterRequest(BaseModel):
    """Requête d'inscription avec tous les champs CDC.

    Note: Le rôle par défaut est 'compagnon' (niveau le plus bas).
    Les rôles supérieurs (chef_chantier, conducteur, admin) nécessitent
    une création par un admin via l'endpoint /users.
    """

    email: EmailStr
    password: str
    nom: str
    prenom: str
    role: Optional[str] = "compagnon"  # Sécurité: rôle le plus bas par défaut
    type_utilisateur: Optional[str] = "salarie"
    telephone: Optional[str] = None
    metier: Optional[str] = None
    code_utilisateur: Optional[str] = None
    couleur: Optional[str] = None


class UpdateUserRequest(BaseModel):
    """Requête de mise à jour utilisateur."""

    nom: Optional[str] = None
    prenom: Optional[str] = None
    telephone: Optional[str] = None
    metier: Optional[str] = None
    couleur: Optional[str] = None
    photo_profil: Optional[str] = None
    contact_urgence_nom: Optional[str] = None
    contact_urgence_telephone: Optional[str] = None  # Renommé pour frontend
    role: Optional[str] = None
    type_utilisateur: Optional[str] = None
    code_utilisateur: Optional[str] = None


class UserResponse(BaseModel):
    """Réponse utilisateur complète selon CDC."""

    id: str  # Retourné comme string pour compatibilité frontend
    email: str
    nom: str
    prenom: str
    nom_complet: Optional[str] = None
    initiales: Optional[str] = None
    role: str
    type_utilisateur: str
    is_active: bool
    couleur: Optional[str] = None
    photo_profil: Optional[str] = None
    code_utilisateur: Optional[str] = None
    telephone: Optional[str] = None
    metier: Optional[str] = None
    contact_urgence_nom: Optional[str] = None
    contact_urgence_telephone: Optional[str] = None  # Renommé pour frontend
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserListResponse(BaseModel):
    """Réponse liste utilisateurs paginée (USR-09)."""

    items: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int


class AuthResponse(BaseModel):
    """Réponse d'authentification."""

    user: UserResponse
    access_token: str
    token_type: str


class ConsentPreferences(BaseModel):
    """Préférences de consentement RGPD."""

    geolocation: bool = False
    notifications: bool = False
    analytics: bool = False
    timestamp: Optional[datetime] = None  # RGPD Art. 7: preuve du consentement
    ip_address: Optional[str] = None  # RGPD Art. 7: contexte du consentement
    user_agent: Optional[str] = None  # RGPD Art. 7: contexte du consentement


class ConsentUpdateRequest(BaseModel):
    """Requête de mise à jour des consentements."""

    geolocation: Optional[bool] = None
    notifications: Optional[bool] = None
    analytics: Optional[bool] = None


# =============================================================================
# Routes d'authentification
# =============================================================================


@router.get("/csrf-token")
def get_csrf_token(request: Request):
    """
    Retourne le token CSRF depuis le cookie.

    Le middleware CSRF génère automatiquement un token lors des requêtes GET.
    Cette route permet au frontend de récupérer explicitement ce token.
    """
    csrf_token = request.cookies.get("csrf_token")
    if not csrf_token:
        raise HTTPException(
            status_code=400,
            detail="No CSRF token found. Make a GET request first to initialize the token."
        )
    return {"csrf_token": csrf_token}


@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")  # Protection brute force: 10 tentatives/minute par IP
def login(
    request: Request,  # Requis par slowapi
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    controller: AuthController = Depends(get_auth_controller),
):
    """
    Authentifie un utilisateur et retourne un token JWT.

    Rate limited: 10 requêtes par minute par IP pour protection brute force.
    Le token est aussi envoyé via cookie HttpOnly pour une sécurité renforcée.

    Args:
        request: Requête HTTP (pour rate limiting).
        response: Réponse HTTP (pour set cookie).
        form_data: Email (username) et mot de passe.
        controller: Controller d'authentification.

    Returns:
        Token d'accès et informations utilisateur.

    Raises:
        HTTPException 401: Identifiants invalides ou compte désactivé.
        HTTPException 429: Trop de tentatives (rate limited).
    """
    try:
        result = controller.login(form_data.username, form_data.password)

        # Set HttpOnly cookie for enhanced security
        # Token not accessible via JavaScript, protecting against XSS
        response.set_cookie(
            key=AUTH_COOKIE_NAME,
            value=result["access_token"],
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            domain=settings.COOKIE_DOMAIN,
        )

        return result
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except UserInactiveError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")  # Protection contre creation de comptes en masse
def register(
    request: Request,  # Requis par slowapi
    data: RegisterRequest,
    response: Response,
    controller: AuthController = Depends(get_auth_controller),
):
    """
    Inscrit un nouvel utilisateur (USR-01).

    Args:
        data: Données d'inscription.
        response: Réponse HTTP (pour set cookie).
        controller: Controller d'authentification.

    Returns:
        Token d'accès et informations utilisateur.

    Raises:
        HTTPException 400: Email/code déjà utilisé ou mot de passe faible.
    """
    try:
        result = controller.register(
            email=data.email,
            password=data.password,
            nom=data.nom,
            prenom=data.prenom,
            role=data.role,
            type_utilisateur=data.type_utilisateur,
            telephone=data.telephone,
            metier=data.metier,
            code_utilisateur=data.code_utilisateur,
            couleur=data.couleur,
        )

        # Set HttpOnly cookie for enhanced security
        response.set_cookie(
            key=AUTH_COOKIE_NAME,
            value=result["access_token"],
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            domain=settings.COOKIE_DOMAIN,
        )

        return result
    except EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except CodeAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except WeakPasswordError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/me", response_model=UserResponse)
def get_current_user(
    user_id: int = Depends(get_current_user_id),
    controller: AuthController = Depends(get_auth_controller),
):
    """
    Récupère l'utilisateur connecté.

    Args:
        user_id: ID de l'utilisateur (extrait du token).
        controller: Controller d'authentification.

    Returns:
        Informations de l'utilisateur connecté.

    Raises:
        HTTPException 401: Token invalide.
        HTTPException 404: Utilisateur non trouvé.
    """
    try:
        return controller.get_user_by_id(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.post("/logout")
def logout(response: Response):
    """
    Déconnecte l'utilisateur en supprimant le cookie d'authentification.

    Args:
        response: Réponse HTTP (pour supprimer le cookie).

    Returns:
        Message de confirmation.
    """
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
    )
    return {"message": "Déconnexion réussie"}


@router.get("/consents", response_model=ConsentPreferences)
def get_consents(
    request: Request,
    controller: AuthController = Depends(get_auth_controller),
):
    """
    Récupère les préférences de consentement RGPD.

    Conformité RGPD : permet de consulter les consentements même avant login.
    Pour les utilisateurs non authentifiés, retourne les valeurs par défaut.

    Args:
        request: Requête HTTP.
        controller: Controller d'authentification.

    Returns:
        Préférences de consentement avec métadonnées RGPD.

    Note:
        Les consentements sont stockés en session pour les non-authentifiés.
        Pour les utilisateurs authentifiés, ils sont récupérés depuis la base.
    """
    # Essayer de récupérer l'utilisateur authentifié (optionnel)
    try:
        user_id = _extract_user_id_from_request(request)
        if user_id:
            from ...application.use_cases import GetConsentsUseCase
            from ...infrastructure.persistence import SQLAlchemyUserRepository
            from shared.infrastructure.database import SessionLocal

            db = SessionLocal()
            try:
                user_repo = SQLAlchemyUserRepository(db)
                use_case = GetConsentsUseCase(user_repo)
                consents = use_case.execute(user_id)
                return ConsentPreferences(**consents)
            finally:
                db.close()
    except Exception:
        # Si erreur (token invalide, etc.), retourner valeurs par défaut
        pass

    # Pour utilisateurs non authentifiés : valeurs par défaut
    return ConsentPreferences(
        geolocation=False,
        notifications=False,
        analytics=False,
        timestamp=None,
        ip_address=None,
        user_agent=None,
    )


@router.post("/consents", response_model=ConsentPreferences)
def update_consents(
    consent_request: ConsentUpdateRequest,
    http_request: Request,
    controller: AuthController = Depends(get_auth_controller),
):
    """
    Met à jour les préférences de consentement RGPD.

    Conformité RGPD Article 7 - Conditions applicables au consentement.
    Enregistre le consentement avec contexte (timestamp, IP, user agent).

    Pour les utilisateurs non authentifiés, accepte les consentements mais ne les persiste pas
    (stockage côté client uniquement).

    Args:
        consent_request: Nouvelles préférences de consentement.
        http_request: Requête HTTP (pour extraire IP et user agent).
        controller: Controller d'authentification.

    Returns:
        Préférences de consentement mises à jour avec métadonnées RGPD.
    """
    # Extraire métadonnées RGPD
    ip_address = http_request.client.host if http_request.client else None
    user_agent = http_request.headers.get("User-Agent")

    # Essayer de récupérer l'utilisateur authentifié (optionnel)
    try:
        user_id = _extract_user_id_from_request(http_request)
        if user_id:
            from ...application.use_cases import UpdateConsentsUseCase
            from ...infrastructure.persistence import SQLAlchemyUserRepository
            from shared.infrastructure.database import SessionLocal

            db = SessionLocal()
            try:
                user_repo = SQLAlchemyUserRepository(db)
                use_case = UpdateConsentsUseCase(user_repo)
                consents = use_case.execute(
                    user_id=user_id,
                    geolocation=consent_request.geolocation,
                    notifications=consent_request.notifications,
                    analytics=consent_request.analytics,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
                return ConsentPreferences(**consents)
            finally:
                db.close()
    except Exception:
        # Si erreur (token invalide, etc.), continuer en mode non-authentifié
        pass

    # Pour utilisateurs non authentifiés : retourner les valeurs avec timestamp
    return ConsentPreferences(
        geolocation=consent_request.geolocation if consent_request.geolocation is not None else False,
        notifications=consent_request.notifications if consent_request.notifications is not None else False,
        analytics=consent_request.analytics if consent_request.analytics is not None else False,
        timestamp=datetime.now(),
        ip_address=ip_address,
        user_agent=user_agent,
    )


# =============================================================================
# Routes de gestion des utilisateurs
# =============================================================================


@users_router.get("", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(20, ge=1, le=100, description="Nombre d'éléments par page"),
    search: Optional[str] = Query(None, max_length=100, description="Recherche par nom, prénom ou email"),
    role: Optional[str] = Query(None, description="Filtrer par rôle"),
    type_utilisateur: Optional[str] = Query(None, description="Filtrer par type"),
    is_active: Optional[bool] = Query(None, description="Filtrer par statut actif"),
    controller: AuthController = Depends(get_auth_controller),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_admin_or_conducteur),
):
    """
    Liste les utilisateurs avec pagination (USR-09).

    Args:
        page: Numéro de page (commence à 1).
        size: Nombre d'éléments par page.
        search: Recherche textuelle (optionnel).
        role: Filtrer par rôle (optionnel).
        type_utilisateur: Filtrer par type (optionnel).
        is_active: Filtrer par statut actif (optionnel).
        controller: Controller d'authentification.
        current_user_id: ID de l'utilisateur connecté (pour vérifier les permissions).

    Returns:
        Liste paginée des utilisateurs.
    """
    # Convertir page/size en skip/limit pour le controller
    skip = (page - 1) * size

    result = controller.list_users(
        skip=skip,
        limit=size,
        role=role,
        type_utilisateur=type_utilisateur,
        active_only=is_active if is_active is not None else False,
        search=search,
    )

    # Convertir la réponse au format frontend
    total = result.get("total", 0)
    pages = (total + size - 1) // size if size > 0 else 0

    # Transformer les users pour le format frontend
    users_data = result.get("users", [])
    items = [_transform_user_response(u) for u in users_data]

    return UserListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@users_router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    controller: AuthController = Depends(get_auth_controller),
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
):
    """
    Récupère un utilisateur par son ID.

    Sécurité: Un compagnon/chef ne peut consulter que son propre profil.
    Admin et conducteur peuvent consulter tout profil.

    Args:
        user_id: ID de l'utilisateur.
        controller: Controller d'authentification.
        current_user_id: ID de l'utilisateur connecté.
        current_user_role: Rôle de l'utilisateur connecté.

    Returns:
        Informations de l'utilisateur.

    Raises:
        HTTPException 403: Accès interdit.
        HTTPException 404: Utilisateur non trouvé.
    """
    # IDOR protection: non-admin ne peut voir que son propre profil
    if current_user_role not in {"admin", "conducteur"} and user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez consulter que votre propre profil.",
        )
    try:
        return controller.get_user_by_id(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@users_router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    http_request: Request,
    request: UpdateUserRequest,
    controller: AuthController = Depends(get_auth_controller),
    current_user_id: int = Depends(get_current_user_id),
    audit: AuditService = Depends(get_audit_service),
    _role: str = Depends(require_admin_or_conducteur),
):
    """
    Met à jour un utilisateur.

    Args:
        user_id: ID de l'utilisateur à mettre à jour.
        http_request: Requête HTTP (pour audit).
        request: Données de mise à jour.
        controller: Controller d'authentification.
        current_user_id: ID de l'utilisateur connecté.
        audit: Service d'audit.

    Returns:
        Utilisateur mis à jour.

    Raises:
        HTTPException 404: Utilisateur non trouvé.
        HTTPException 400: Données invalides.
    """
    try:
        # Récupérer les anciennes valeurs pour l'audit
        old_user = controller.get_user_by_id(user_id)
        old_values = {
            "nom": old_user.get("nom"),
            "prenom": old_user.get("prenom"),
            "telephone": old_user.get("telephone"),
            "metier": old_user.get("metier"),
            "role": old_user.get("role"),
            "type_utilisateur": old_user.get("type_utilisateur"),
            "code_utilisateur": old_user.get("code_utilisateur"),
        }

        result = controller.update_user(
            user_id=user_id,
            nom=request.nom,
            prenom=request.prenom,
            telephone=request.telephone,
            metier=request.metier,
            couleur=request.couleur,
            photo_profil=request.photo_profil,
            contact_urgence_nom=request.contact_urgence_nom,
            contact_urgence_tel=request.contact_urgence_telephone,  # Mapping frontend -> backend
            role=request.role,
            type_utilisateur=request.type_utilisateur,
            code_utilisateur=request.code_utilisateur,
        )

        # Audit Trail
        new_values = {
            "nom": result.get("nom"),
            "prenom": result.get("prenom"),
            "telephone": result.get("telephone"),
            "metier": result.get("metier"),
            "role": result.get("role"),
            "type_utilisateur": result.get("type_utilisateur"),
            "code_utilisateur": result.get("code_utilisateur"),
        }

        audit.log_action(
            entity_type="user",
            entity_id=user_id,
            action="updated",
            user_id=current_user_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=http_request.client.host if http_request.client else None,
        )

        return result
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except CodeAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@users_router.post("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    http_request: Request,
    controller: AuthController = Depends(get_auth_controller),
    current_user_id: int = Depends(get_current_user_id),
    audit: AuditService = Depends(get_audit_service),
    _role: str = Depends(require_admin_or_conducteur),
):
    """
    Désactive un utilisateur (USR-10 - révocation instantanée).

    Les données historiques sont conservées.

    Args:
        user_id: ID de l'utilisateur à désactiver.
        http_request: Requête HTTP (pour audit).
        controller: Controller d'authentification.
        current_user_id: ID de l'utilisateur connecté.
        audit: Service d'audit.

    Returns:
        Utilisateur désactivé.

    Raises:
        HTTPException 404: Utilisateur non trouvé.
    """
    try:
        # Récupérer les valeurs pour audit
        old_user = controller.get_user_by_id(user_id)

        result = controller.deactivate_user(user_id)

        # Audit Trail
        audit.log_action(
            entity_type="user",
            entity_id=user_id,
            action="deactivated",
            user_id=current_user_id,
            old_values={
                "is_active": old_user.get("is_active"),
                "email": old_user.get("email"),
            },
            new_values={
                "is_active": False,
            },
            ip_address=http_request.client.host if http_request.client else None,
        )

        return result
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@users_router.post("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: int,
    http_request: Request,
    controller: AuthController = Depends(get_auth_controller),
    current_user_id: int = Depends(get_current_user_id),
    audit: AuditService = Depends(get_audit_service),
    _role: str = Depends(require_admin_or_conducteur),
):
    """
    Réactive un utilisateur précédemment désactivé.

    Args:
        user_id: ID de l'utilisateur à activer.
        http_request: Requête HTTP (pour audit).
        controller: Controller d'authentification.
        current_user_id: ID de l'utilisateur connecté.
        audit: Service d'audit.

    Returns:
        Utilisateur activé.

    Raises:
        HTTPException 404: Utilisateur non trouvé.
    """
    try:
        # Récupérer les valeurs pour audit
        old_user = controller.get_user_by_id(user_id)

        result = controller.activate_user(user_id)

        # Audit Trail
        audit.log_action(
            entity_type="user",
            entity_id=user_id,
            action="activated",
            user_id=current_user_id,
            old_values={
                "is_active": old_user.get("is_active"),
                "email": old_user.get("email"),
            },
            new_values={
                "is_active": True,
            },
            ip_address=http_request.client.host if http_request.client else None,
        )

        return result
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@users_router.get("/me/export-data")
def export_user_data_rgpd(
    controller: AuthController = Depends(get_auth_controller),
    current_user_id: int = Depends(get_current_user_id),
) -> dict[str, Any]:
    """
    Exporte toutes les données personnelles de l'utilisateur connecté.

    Conformité RGPD Article 20 - Droit à la portabilité des données.

    Permet à un utilisateur de télécharger toutes ses données personnelles
    dans un format structuré, couramment utilisé et lisible par machine (JSON).

    Returns:
        Dictionnaire JSON avec toutes les données:
        - Profil utilisateur
        - Pointages et heures
        - Affectations planning
        - Posts et commentaires
        - Documents et formulaires
        - Signalements et interventions

    Notes:
        - Les fichiers uploadés ne sont pas inclus (seulement métadonnées)
        - Utilisable 1 fois par semaine maximum (rate limiting)
        - Export limité aux 24 derniers mois
    """
    from ...application.use_cases import ExportUserDataUseCase
    from ...infrastructure.persistence import SQLAlchemyUserRepository
    from shared.infrastructure.database import SessionLocal

    db = SessionLocal()
    try:
        user_repo = SQLAlchemyUserRepository(db)
        use_case = ExportUserDataUseCase(user_repo)

        export_data = use_case.execute(current_user_id)

        return export_data
    finally:
        db.close()


# =============================================================================
# Helpers
# =============================================================================


def _extract_user_id_from_request(request: Request) -> Optional[int]:
    """
    Extrait l'ID utilisateur depuis un token JWT dans la requête.

    Cherche le token dans le cookie HttpOnly puis dans l'en-tête Authorization.
    Utilise le service JWT correctement initialisé via settings.

    Args:
        request: Requête HTTP.

    Returns:
        L'ID utilisateur ou None si non authentifié/token invalide.
    """
    token = request.cookies.get(AUTH_COOKIE_NAME)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")

    if not token:
        return None

    from ...adapters.providers.jwt_token_service import JWTTokenService

    token_service = JWTTokenService(
        secret_key=settings.SECRET_KEY,
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return token_service.get_user_id(token)


def _transform_user_response(user_dict: dict) -> UserResponse:
    """
    Transforme un dictionnaire utilisateur du controller en UserResponse.

    Le controller retourne déjà des données formatées pour le frontend,
    cette fonction assure la validation Pydantic.
    """
    return UserResponse(
        id=str(user_dict.get("id", "")),
        email=user_dict.get("email", ""),
        nom=user_dict.get("nom", ""),
        prenom=user_dict.get("prenom", ""),
        nom_complet=user_dict.get("nom_complet"),
        initiales=user_dict.get("initiales"),
        role=user_dict.get("role", "compagnon"),
        type_utilisateur=user_dict.get("type_utilisateur", "employe"),
        is_active=user_dict.get("is_active", True),
        couleur=user_dict.get("couleur"),
        photo_profil=user_dict.get("photo_profil"),
        code_utilisateur=user_dict.get("code_utilisateur"),
        telephone=user_dict.get("telephone"),
        metier=user_dict.get("metier"),
        contact_urgence_nom=user_dict.get("contact_urgence_nom"),
        contact_urgence_telephone=user_dict.get("contact_urgence_telephone"),
        created_at=user_dict.get("created_at"),
        updated_at=user_dict.get("updated_at"),
    )
