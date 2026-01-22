# Hub Chantier - Configuration Locale

Guide pour configurer un environnement de developpement local proche de la production.

## Prerequis

- **Docker** >= 24.0
- **Docker Compose** >= 2.20
- **Make** (optionnel, pour les raccourcis)

Verification:
```bash
docker --version
docker compose version
```

## Quick Start

### Mode Developpement (hot-reload)

```bash
# Demarrer tout l'environnement avec hot-reload
make dev

# Ou sans Make:
docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.development up --build
```

**URLs disponibles:**
| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Vite dev server avec HMR |
| API | http://localhost:8000 | FastAPI avec auto-reload |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Adminer | http://localhost:8080 | Interface DB web |

### Mode Production-like

```bash
# Demarrer en mode production-like
make prod

# Ou sans Make:
docker compose --env-file .env.production-local up --build
```

**URLs disponibles:**
| Service | URL | Description |
|---------|-----|-------------|
| Application | http://localhost | Frontend + API via nginx |
| API directe | http://localhost:8000 | FastAPI |
| Adminer | http://localhost:8080 | Interface DB web |

## Architecture Docker

```
                    Mode Dev                           Mode Prod-like
                    --------                           --------------

    :5173 ─────► Vite Dev Server            :80 ─────► nginx
                     │                                    │
                     │ proxy /api                         │ proxy /api
                     ▼                                    ▼
    :8000 ─────► FastAPI (uvicorn --reload)  :8000 ─────► FastAPI (uvicorn)
                     │                                    │
                     ▼                                    ▼
    :5432 ─────► PostgreSQL                  :5432 ─────► PostgreSQL

    :8080 ─────► Adminer                     :8080 ─────► Adminer
```

## Commandes Utiles

### Avec Makefile (recommande)

```bash
make help           # Affiche toutes les commandes disponibles

# Developpement
make dev            # Lance en mode dev (foreground)
make dev-d          # Lance en mode dev (background)
make dev-api        # Lance seulement DB + API (pour frontend local npm)

# Production-like
make prod           # Lance en mode prod-like
make prod-d         # Lance en mode prod-like (background)

# Gestion
make stop           # Arrete les containers
make stop-v         # Arrete et supprime les volumes (reset DB)
make logs           # Affiche les logs
make logs-api       # Logs de l'API seulement
make ps             # Liste les containers

# Base de donnees
make db-shell       # Ouvre psql dans le container
make db-reset       # Reset complet de la DB

# Tests
make test           # Lance les tests backend
make test-cov       # Tests avec rapport de couverture
make lint           # Verifie le code

# Nettoyage
make clean          # Nettoie caches et fichiers temporaires
make clean-docker   # Supprime les images Docker
```

### Sans Makefile

```bash
# Demarrer
docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.development up --build

# Arreter
docker compose -f docker-compose.yml -f docker-compose.dev.yml down

# Logs
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f api

# Shell PostgreSQL
docker compose exec db psql -U hubchantier -d hub_chantier

# Reset DB
docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v
```

## Configuration

### Fichiers d'environnement

| Fichier | Usage |
|---------|-------|
| `.env.development` | Developpement local avec hot-reload |
| `.env.production-local` | Test de config production en local |
| `backend/.env.example` | Template pour dev sans Docker |

### Variables importantes

```bash
# Application
APP_NAME="Hub Chantier"
DEBUG=true/false

# Database PostgreSQL
POSTGRES_USER=hubchantier
POSTGRES_PASSWORD=...
POSTGRES_DB=hub_chantier

# Securite
SECRET_KEY=...  # Min 32 caracteres
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost
```

## Developpement Hybride

Si vous preferez lancer le frontend en local (plus rapide):

```bash
# Terminal 1: DB + API via Docker
make dev-api

# Terminal 2: Frontend local
cd frontend && npm run dev
```

## Connexion a la Base de Donnees

### Via Adminer (interface web)

1. Ouvrir http://localhost:8080
2. Systeme: PostgreSQL
3. Serveur: `db`
4. Utilisateur: `hubchantier`
5. Mot de passe: `hubchantier_dev`
6. Base de donnees: `hub_chantier`

### Via psql (ligne de commande)

```bash
make db-shell

# Ou directement:
docker compose exec db psql -U hubchantier -d hub_chantier
```

### Via client externe (DBeaver, pgAdmin, etc.)

- Host: `localhost`
- Port: `5432`
- Database: `hub_chantier`
- User: `hubchantier`
- Password: `hubchantier_dev` (ou selon votre .env)

## Troubleshooting

### Port deja utilise

```bash
# Verifier quel process utilise le port
lsof -i :8000
lsof -i :5173
lsof -i :5432

# Tuer le process si necessaire
kill -9 <PID>
```

### Container ne demarre pas

```bash
# Voir les logs detailles
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs api

# Reconstruire les images
docker compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache
```

### Probleme de permissions

```bash
# Reset complet
make clean-docker
make dev
```

### Base de donnees corrompue

```bash
# Reset de la DB
make db-reset
make dev
```

## Differences Dev vs Prod-like

| Aspect | Dev | Prod-like |
|--------|-----|-----------|
| Frontend | Vite dev server (HMR) | nginx + build statique |
| Backend | uvicorn --reload | uvicorn (sans reload) |
| DEBUG | true | false |
| Token expire | 8h | 1h |
| Logs | Verbeux | Minimaux |
| Hot-reload | Oui | Non |
| Port principal | 5173 | 80 |
