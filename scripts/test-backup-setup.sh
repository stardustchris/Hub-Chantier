#!/bin/bash
# =====================================================
# Hub Chantier - Test Setup Backups
# =====================================================
# Ce script verifie que la configuration backup est correcte
# Usage: ./scripts/test-backup-setup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${ENV_FILE:-$PROJECT_DIR/.env.production}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteurs
PASSED=0
FAILED=0
WARNINGS=0

log_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

log_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

echo "=========================================="
echo "Hub Chantier - Test Configuration Backup"
echo "=========================================="
echo ""

# ===========================================
# 1. Verifications prerequis
# ===========================================
echo "[1/6] Prerequis systeme..."

if command -v docker &> /dev/null; then
    log_pass "Docker installe"
else
    log_fail "Docker non installe"
fi

if docker compose version &> /dev/null; then
    log_pass "Docker Compose disponible"
else
    log_fail "Docker Compose non disponible"
fi

# ===========================================
# 2. Fichiers et permissions
# ===========================================
echo ""
echo "[2/6] Scripts et fichiers..."

if [ -x "$SCRIPT_DIR/backup.sh" ]; then
    log_pass "backup.sh executable"
else
    log_fail "backup.sh manquant ou non executable"
fi

if [ -x "$SCRIPT_DIR/restore.sh" ]; then
    log_pass "restore.sh executable"
else
    log_fail "restore.sh manquant ou non executable"
fi

if [ -f "$PROJECT_DIR/docker/backup-cron/Dockerfile" ]; then
    log_pass "Dockerfile backup-cron present"
else
    log_fail "Dockerfile backup-cron manquant"
fi

# ===========================================
# 3. Configuration environnement
# ===========================================
echo ""
echo "[3/6] Configuration environnement..."

if [ -f "$ENV_FILE" ]; then
    log_pass ".env.production existe"

    # Charger variables
    set -a
    source "$ENV_FILE"
    set +a

    # Verifier variables base
    if [ -n "${POSTGRES_USER:-}" ]; then
        log_pass "POSTGRES_USER defini"
    else
        log_fail "POSTGRES_USER manquant"
    fi

    if [ -n "${POSTGRES_PASSWORD:-}" ]; then
        log_pass "POSTGRES_PASSWORD defini"
    else
        log_fail "POSTGRES_PASSWORD manquant"
    fi

    if [ -n "${POSTGRES_DB:-}" ]; then
        log_pass "POSTGRES_DB defini"
    else
        log_warn "POSTGRES_DB non defini (utilisera defaut: hub_chantier)"
    fi

    # Verifier S3 (optionnel)
    if [ -n "${S3_BACKUP_BUCKET:-}" ]; then
        log_pass "S3_BACKUP_BUCKET defini"

        if [ -n "${AWS_ACCESS_KEY_ID:-}" ]; then
            log_pass "AWS_ACCESS_KEY_ID defini"
        else
            log_warn "AWS_ACCESS_KEY_ID manquant (S3 non fonctionnel)"
        fi

        if [ -n "${AWS_SECRET_ACCESS_KEY:-}" ]; then
            log_pass "AWS_SECRET_ACCESS_KEY defini"
        else
            log_warn "AWS_SECRET_ACCESS_KEY manquant (S3 non fonctionnel)"
        fi
    else
        log_warn "S3_BACKUP_BUCKET non defini (backups locaux uniquement)"
    fi
else
    log_fail ".env.production introuvable"
fi

# ===========================================
# 4. Etat conteneurs Docker
# ===========================================
echo ""
echo "[4/6] Conteneurs Docker..."

COMPOSE_FILE="$PROJECT_DIR/docker-compose.prod.yml"

if docker compose -f "$COMPOSE_FILE" ps db 2>/dev/null | grep -q "Up"; then
    log_pass "Conteneur PostgreSQL demarre"

    # Tester connexion
    if docker compose -f "$COMPOSE_FILE" exec -T db pg_isready -U "${POSTGRES_USER:-hubchantier}" > /dev/null 2>&1; then
        log_pass "PostgreSQL repond"
    else
        log_fail "PostgreSQL ne repond pas"
    fi
else
    log_warn "Conteneur PostgreSQL arrete (normal si pas en prod)"
fi

# Verifier service backup-cron
if docker compose -f "$COMPOSE_FILE" ps backup-cron 2>/dev/null | grep -q "Up"; then
    log_pass "Service backup-cron actif"
else
    log_warn "Service backup-cron non actif (activer avec --profile backup)"
fi

# ===========================================
# 5. Repertoire backups
# ===========================================
echo ""
echo "[5/6] Repertoires et espace disque..."

BACKUP_DIR="${BACKUP_DIR:-/var/backups/hub-chantier}"

if [ -d "$BACKUP_DIR" ]; then
    log_pass "Repertoire backups existe: $BACKUP_DIR"

    # Verifier permissions ecriture
    if [ -w "$BACKUP_DIR" ]; then
        log_pass "Permissions ecriture OK"
    else
        log_fail "Pas de permission ecriture sur $BACKUP_DIR"
    fi

    # Espace disque
    AVAILABLE_GB=$(df -BG "$BACKUP_DIR" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$AVAILABLE_GB" -gt 5 ]; then
        log_pass "Espace disque suffisant: ${AVAILABLE_GB}G disponibles"
    else
        log_warn "Espace disque faible: ${AVAILABLE_GB}G disponibles"
    fi

    # Backups existants
    BACKUP_COUNT=$(find "$BACKUP_DIR" -name "hub_chantier_backup_*.sql.gz" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$BACKUP_COUNT" -gt 0 ]; then
        log_pass "Backups existants: $BACKUP_COUNT fichiers"
        LATEST=$(ls -t "$BACKUP_DIR"/hub_chantier_backup_*.sql.gz 2>/dev/null | head -1)
        LATEST_AGE_DAYS=$(find "$BACKUP_DIR" -name "$(basename "$LATEST")" -mtime +1 2>/dev/null | wc -l | tr -d ' ')
        if [ "$LATEST_AGE_DAYS" -eq 0 ]; then
            log_pass "Dernier backup recent (< 24h)"
        else
            log_warn "Dernier backup ancien (> 24h)"
        fi
    else
        log_warn "Aucun backup trouve (normal pour nouvelle installation)"
    fi
else
    log_warn "Repertoire backups inexistant (sera cree au premier backup)"
fi

# ===========================================
# 6. Test AWS CLI (si S3 configure)
# ===========================================
echo ""
echo "[6/6] Configuration S3..."

if [ -n "${S3_BACKUP_BUCKET:-}" ]; then
    if command -v aws &> /dev/null; then
        log_pass "AWS CLI installe"

        # Tester connexion S3
        AWS_ARGS=""
        if [ -n "${S3_ENDPOINT_URL:-}" ]; then
            AWS_ARGS="--endpoint-url $S3_ENDPOINT_URL"
        fi

        if aws s3 ls $AWS_ARGS "s3://$S3_BACKUP_BUCKET/" > /dev/null 2>&1; then
            log_pass "Connexion S3 bucket OK"
        else
            log_fail "Impossible de se connecter au bucket S3"
        fi
    else
        log_warn "AWS CLI non installe (requis pour S3)"
        echo "         Installation: pip3 install awscli"
    fi
else
    log_warn "S3 non configure (backups locaux uniquement)"
fi

# ===========================================
# Resume
# ===========================================
echo ""
echo "=========================================="
echo "Resume"
echo "=========================================="
echo -e "${GREEN}Reussis:${NC} $PASSED"
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}Avertissements:${NC} $WARNINGS"
fi
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Echecs:${NC} $FAILED"
fi
echo ""

# ===========================================
# Recommandations
# ===========================================
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Action requise:${NC} Corriger les echecs avant utilisation"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}Recommandations:${NC}"

    if [ -z "${S3_BACKUP_BUCKET:-}" ]; then
        echo "  • Configurer S3 pour backups externes (recommande production)"
        echo "    Voir: docs/BACKUP_QUICKSTART.md"
    fi

    if ! docker compose -f "$COMPOSE_FILE" ps backup-cron 2>/dev/null | grep -q "Up"; then
        echo "  • Activer backups automatiques:"
        echo "    docker compose -f docker-compose.prod.yml --profile backup up -d"
    fi

    echo ""
    echo "Configuration fonctionnelle avec limitations."
    exit 0
else
    echo -e "${GREEN}Configuration backup parfaite!${NC}"
    echo ""
    echo "Prochaines etapes:"
    echo "  • Tester backup manuel: ./scripts/backup.sh"
    echo "  • Activer backups auto: docker compose -f docker-compose.prod.yml --profile backup up -d"
    echo "  • Voir documentation: docs/BACKUP_QUICKSTART.md"
    exit 0
fi
