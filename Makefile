# Hub Chantier - Makefile
# Commandes utiles pour le developpement

.PHONY: help dev prod stop logs clean test lint db-shell

# Couleurs
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

help: ## Affiche cette aide
	@echo "$(CYAN)Hub Chantier - Commandes disponibles$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}'

# ===========================================
# Developpement (hot-reload)
# ===========================================

dev: ## Lance l'environnement de dev avec hot-reload
	@echo "$(CYAN)Demarrage en mode developpement...$(RESET)"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.development up --build

dev-d: ## Lance l'environnement de dev en arriere-plan
	@echo "$(CYAN)Demarrage en mode developpement (detached)...$(RESET)"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.development up --build -d

dev-api: ## Lance seulement la DB et l'API (pour frontend local)
	@echo "$(CYAN)Demarrage DB + API...$(RESET)"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.development up --build db api adminer

# ===========================================
# Production-like local
# ===========================================

prod: ## Lance l'environnement production-like
	@echo "$(CYAN)Demarrage en mode production-like...$(RESET)"
	docker compose --env-file .env.production-local up --build

prod-d: ## Lance l'environnement production-like en arriere-plan
	@echo "$(CYAN)Demarrage en mode production-like (detached)...$(RESET)"
	docker compose --env-file .env.production-local up --build -d

# ===========================================
# Gestion des containers
# ===========================================

stop: ## Arrete tous les containers
	@echo "$(YELLOW)Arret des containers...$(RESET)"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

stop-v: ## Arrete et supprime les volumes (reset DB)
	@echo "$(YELLOW)Arret et suppression des volumes...$(RESET)"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v

logs: ## Affiche les logs de tous les services
	docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

logs-api: ## Affiche les logs de l'API
	docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f api

logs-frontend: ## Affiche les logs du frontend
	docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f frontend

ps: ## Liste les containers en cours
	docker compose -f docker-compose.yml -f docker-compose.dev.yml ps

# ===========================================
# Base de donnees
# ===========================================

db-shell: ## Ouvre un shell PostgreSQL
	docker compose exec db psql -U hubchantier -d hub_chantier

db-reset: ## Reset la base de donnees (ATTENTION: perte de donnees!)
	@echo "$(YELLOW)Reset de la base de donnees...$(RESET)"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v
	docker volume rm hub-chantier_postgres_data 2>/dev/null || true
	@echo "$(GREEN)Base de donnees reset. Relancez 'make dev' pour recreer.$(RESET)"

# ===========================================
# Tests et qualite
# ===========================================

test: ## Lance les tests backend
	@echo "$(CYAN)Lancement des tests...$(RESET)"
	cd backend && pytest tests/ -v

test-cov: ## Lance les tests avec couverture
	@echo "$(CYAN)Lancement des tests avec couverture...$(RESET)"
	cd backend && pytest --cov=. --cov-report=html --cov-report=term

lint: ## Verifie le code (ruff + eslint)
	@echo "$(CYAN)Verification du code...$(RESET)"
	cd backend && ruff check .
	cd frontend && npm run lint

# ===========================================
# Nettoyage
# ===========================================

clean: ## Nettoie les fichiers temporaires et caches
	@echo "$(YELLOW)Nettoyage...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/dist 2>/dev/null || true
	rm -rf backend/htmlcov 2>/dev/null || true
	@echo "$(GREEN)Nettoyage termine.$(RESET)"

clean-docker: ## Supprime les images Docker du projet
	@echo "$(YELLOW)Suppression des images Docker...$(RESET)"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down --rmi local -v
	@echo "$(GREEN)Images Docker supprimees.$(RESET)"

# ===========================================
# Installation locale (sans Docker)
# ===========================================

install: ## Installe les dependances localement
	@echo "$(CYAN)Installation des dependances...$(RESET)"
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

local-api: ## Lance l'API localement (sans Docker)
	@echo "$(CYAN)Demarrage de l'API locale...$(RESET)"
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

local-frontend: ## Lance le frontend localement (sans Docker)
	@echo "$(CYAN)Demarrage du frontend local...$(RESET)"
	cd frontend && npm run dev
