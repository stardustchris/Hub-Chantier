#!/bin/bash
# =====================================================
# Hub Chantier - Script de deploiement production
# =====================================================
# Usage: bash scripts/deploy.sh
# Prerequis: .env.production configure

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_DIR/.env.production"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.prod.yml"

echo "======================================"
echo "Hub Chantier - Deploiement Production"
echo "======================================"

# ===========================================
# 1. Verifications
# ===========================================
echo "[1/6] Verification des prerequis..."

if ! command -v docker &> /dev/null; then
    echo "ERREUR: Docker n'est pas installe. Lancez scripts/init-server.sh d'abord."
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "ERREUR: Docker Compose n'est pas disponible."
    exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "ERREUR: $ENV_FILE introuvable."
    echo "  Copiez .env.production.example vers .env.production et configurez les valeurs."
    exit 1
fi

# Charger les variables
set -a
source "$ENV_FILE"
set +a

# Verifier les variables critiques
if [ -z "${DOMAIN:-}" ]; then
    echo "ERREUR: DOMAIN non defini dans .env.production"
    exit 1
fi

if [ -z "${SECRET_KEY:-}" ] || [[ "$SECRET_KEY" == *"CHANGEZ"* ]]; then
    echo "ERREUR: SECRET_KEY non configure dans .env.production"
    echo "  Generez avec: python3 -c \"import secrets; print(secrets.token_urlsafe(48))\""
    exit 1
fi

if [ -z "${ENCRYPTION_KEY:-}" ] || [[ "$ENCRYPTION_KEY" == *"CHANGEZ"* ]]; then
    echo "ERREUR: ENCRYPTION_KEY non configure dans .env.production"
    echo "  Generez avec: python3 -c \"import secrets; print(secrets.token_hex(16))\""
    exit 1
fi

if [ -z "${POSTGRES_PASSWORD:-}" ] || [[ "$POSTGRES_PASSWORD" == *"CHANGEZ"* ]]; then
    echo "ERREUR: POSTGRES_PASSWORD non configure dans .env.production"
    exit 1
fi

echo "  Domaine: $DOMAIN"
echo "  Prerequis OK."

# ===========================================
# 2. Build des images
# ===========================================
echo "[2/6] Build des images Docker..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --no-cache

# ===========================================
# 3. Obtenir le certificat SSL (premiere fois)
# ===========================================
CERT_PATH="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"

if ! docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" run --rm certbot certificates 2>/dev/null | grep -q "$DOMAIN"; then
    echo "[3/6] Obtention du certificat SSL (Let's Encrypt)..."

    # Demarrer Nginx temporairement en HTTP pour le challenge ACME
    # Creer une config nginx temporaire pour le challenge
    TEMP_CONF=$(mktemp)
    cat > "$TEMP_CONF" <<'NGINX_TEMP'
server {
    listen 80;
    server_name _;
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    location / {
        return 200 "Waiting for SSL certificate...\n";
        add_header Content-Type text/plain;
    }
}
NGINX_TEMP

    # Lancer nginx temporaire
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d db
    sleep 5

    # Lancer un nginx temporaire pour le challenge
    docker run -d --name certbot-nginx \
        -p 80:80 \
        -v "$TEMP_CONF:/etc/nginx/conf.d/default.conf:ro" \
        -v "$(docker volume inspect hub-chantier_certbot_www --format '{{.Mountpoint}}' 2>/dev/null || echo '/tmp/certbot'):/var/www/certbot" \
        nginx:alpine

    sleep 2

    # Obtenir le certificat
    CERTBOT_EMAIL="${CERTBOT_EMAIL:-admin@$DOMAIN}"
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" run --rm certbot certonly \
        --webroot \
        -w /var/www/certbot \
        -d "$DOMAIN" \
        --email "$CERTBOT_EMAIL" \
        --agree-tos \
        --no-eff-email \
        --force-renewal

    # Nettoyer
    docker stop certbot-nginx && docker rm certbot-nginx
    rm -f "$TEMP_CONF"

    echo "  Certificat SSL obtenu pour $DOMAIN."
else
    echo "[3/6] Certificat SSL deja present pour $DOMAIN."
fi

# ===========================================
# 4. Lancer les services
# ===========================================
echo "[4/6] Lancement des services..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

# ===========================================
# 5. Attendre que les services soient prets
# ===========================================
echo "[5/6] Verification sante des services..."
sleep 10

# Verifier la base de donnees
if docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T db pg_isready -U "${POSTGRES_USER}" > /dev/null 2>&1; then
    echo "  PostgreSQL: OK"
else
    echo "  PostgreSQL: ERREUR"
fi

# Verifier le backend
if docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T api curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "  Backend API: OK"
else
    echo "  Backend API: En cours de demarrage..."
    sleep 15
    if docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T api curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "  Backend API: OK"
    else
        echo "  Backend API: ERREUR - verifiez les logs: docker compose -f docker-compose.prod.yml logs api"
    fi
fi

# Verifier le frontend
if curl -sf "http://localhost/health" > /dev/null 2>&1; then
    echo "  Frontend Nginx: OK"
else
    echo "  Frontend Nginx: En cours de demarrage..."
fi

# ===========================================
# 6. Resume
# ===========================================
echo ""
echo "======================================"
echo "Deploiement termine !"
echo "======================================"
echo ""
echo "  URL:     https://$DOMAIN"
echo "  Sante:   https://$DOMAIN/health"
echo "  API:     https://$DOMAIN/api/health"
echo ""
echo "Commandes utiles :"
echo "  Logs:    docker compose -f docker-compose.prod.yml logs -f"
echo "  Stop:    docker compose -f docker-compose.prod.yml down"
echo "  Restart: docker compose -f docker-compose.prod.yml restart"
echo "  DB:      docker compose -f docker-compose.prod.yml exec db psql -U $POSTGRES_USER $POSTGRES_DB"
echo ""
