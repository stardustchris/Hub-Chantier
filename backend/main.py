"""Hub Chantier - Application FastAPI principale."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from shared.infrastructure import settings, init_db
from shared.infrastructure.rate_limiter import limiter
from shared.infrastructure.web.security_middleware import SecurityHeadersMiddleware
from modules.auth.infrastructure.web import router as auth_router, users_router
from modules.chantiers.infrastructure.web import router as chantiers_router
from modules.dashboard.infrastructure.web import dashboard_router
from modules.taches.infrastructure.web import router as taches_router
from modules.planning.infrastructure.web import router as planning_router
from modules.pointages.infrastructure.web import router as pointages_router
from modules.formulaires.infrastructure.web import router as formulaires_router
from modules.formulaires.infrastructure.web import templates_router as templates_formulaires_router
from modules.signalements.infrastructure.web import router as signalements_router
from modules.documents.infrastructure.web import router as documents_router
from shared.infrastructure.web.upload_routes import router as upload_router

# Créer l'application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de gestion de chantiers BTP pour Greg Construction",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configurer le rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configuration CORS - restrictive (pas de wildcards)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
)

# Middleware de securite HTTP (OWASP headers)
app.add_middleware(SecurityHeadersMiddleware)


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage."""
    print(f"Démarrage de {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    print("Base de données initialisée")


@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt."""
    print("Arrêt de l'application")


# Routes
@app.get("/", tags=["health"])
async def root():
    """Endpoint de santé."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check détaillé."""
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.APP_VERSION,
    }


# Inclure les routers des modules
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(chantiers_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(taches_router, prefix="/api")
app.include_router(planning_router, prefix="/api")
app.include_router(pointages_router, prefix="/api")
app.include_router(formulaires_router, prefix="/api")
app.include_router(templates_formulaires_router, prefix="/api")
app.include_router(signalements_router, prefix="/api")
app.include_router(documents_router, prefix="/api")

# Futurs modules à ajouter:
# app.include_router(employes_router, prefix="/api")
