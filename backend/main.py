"""Hub Chantier - Application FastAPI principale."""

import logging
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from shared.infrastructure import settings, init_db
from shared.infrastructure.database import SessionLocal

# P2-3: Configuration logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
from shared.infrastructure.rate_limiter import limiter
from shared.infrastructure.web.security_middleware import SecurityHeadersMiddleware
from shared.infrastructure.web.csrf_middleware import CSRFMiddleware
from shared.infrastructure.scheduler import get_scheduler
from shared.infrastructure.scheduler.jobs import RappelReservationJob
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
from modules.logistique.infrastructure.web import router as logistique_router
from modules.planning_charge.infrastructure import router as planning_charge_router
from modules.interventions.infrastructure.web import router as interventions_router
from modules.notifications.infrastructure.web import router as notifications_router
from modules.notifications.infrastructure.event_handlers import register_notification_handlers
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
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With", "X-CSRF-Token"],
)

# Middleware de securite HTTP (OWASP headers)
app.add_middleware(SecurityHeadersMiddleware)

# Middleware CSRF (M-01) - Protection contre attaques CSRF
app.add_middleware(CSRFMiddleware)


# P2-8: Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Gestionnaire global d'exceptions non gérées.

    Log l'erreur et retourne une réponse générique
    pour ne pas exposer de détails internes.
    """
    logger.error(
        f"Erreur non gérée: {type(exc).__name__}: {exc}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    # En mode debug, on peut exposer plus de détails
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "detail": f"{type(exc).__name__}: {str(exc)}",
                "path": request.url.path,
            },
        )

    # En production, message générique
    return JSONResponse(
        status_code=500,
        content={"detail": "Une erreur interne s'est produite"},
    )


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage."""
    logger.info(f"Démarrage de {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Mode DEBUG: {settings.DEBUG}")
    init_db()
    logger.info("Base de données initialisée")

    # Enregistrer les handlers de notifications
    register_notification_handlers()

    # Démarrer le scheduler et enregistrer les jobs
    scheduler = get_scheduler()
    RappelReservationJob.register(scheduler, SessionLocal)
    scheduler.start()
    logger.info("Scheduler démarré avec jobs planifiés")


@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt."""
    # Arrêter le scheduler
    scheduler = get_scheduler()
    scheduler.shutdown(wait=True)
    logger.info("Scheduler arrêté")
    logger.info("Arrêt de l'application")


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
    """
    Health check détaillé (P2-9).

    Vérifie réellement la connexion à la base de données.
    """
    db_status = "disconnected"
    db_latency_ms = None

    try:
        db = SessionLocal()
        start = datetime.now()
        db.execute(text("SELECT 1"))
        db_latency_ms = (datetime.now() - start).total_seconds() * 1000
        db_status = "connected"
        db.close()
    except Exception as e:
        logger.error(f"Health check DB failed: {e}")
        db_status = f"error: {type(e).__name__}"

    status = "healthy" if db_status == "connected" else "unhealthy"

    return {
        "status": status,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "database": {
                "status": db_status,
                "latency_ms": round(db_latency_ms, 2) if db_latency_ms else None,
            },
        },
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
app.include_router(logistique_router, prefix="/api")
app.include_router(planning_charge_router, prefix="/api")
app.include_router(interventions_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")

# Futurs modules à ajouter:
# app.include_router(employes_router, prefix="/api")
