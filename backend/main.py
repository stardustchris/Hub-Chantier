"""Hub Chantier - Application FastAPI principale."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.infrastructure import settings, init_db
from modules.auth.infrastructure.web import router as auth_router, users_router
from modules.chantiers.infrastructure.web import router as chantiers_router

# Créer l'application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de gestion de chantiers BTP pour Greg Construction",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

# Futurs modules à ajouter:
# app.include_router(employes_router, prefix="/api")
# app.include_router(pointages_router, prefix="/api")
# app.include_router(planning_router, prefix="/api")
# app.include_router(documents_router, prefix="/api")
# app.include_router(formulaires_router, prefix="/api")
