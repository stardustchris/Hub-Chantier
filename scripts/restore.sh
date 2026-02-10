#!/bin/bash
# =====================================================
# Hub Chantier - Restore PostgreSQL depuis backup
# =====================================================
# Usage:
#   ./scripts/restore.sh /path/to/backup.sql.gz
#   ./scripts/restore.sh --latest
#   ./scripts/restore.sh --from-s3 backup_20260208_030000.sql.gz
#
# ATTENTION: Cette operation ecrase la base de donnees existante.
#            Un backup automatique est cree avant la restauration.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-$PROJECT_DIR/.env.production}"

# Charger variables d'environnement
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

BACKUP_DIR="${BACKUP_DIR:-/var/backups/hub-chantier}"
DB_NAME="${POSTGRES_DB:-hub_chantier}"
DB_USER="${POSTGRES_USER:-hubchantier}"
BACKUP_FILE=""
FROM_S3=false
USE_LATEST=false

# Logger
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

error() {
    log "ERREUR: $*" >&2
    exit 1
}

# ===========================================
# Parse arguments
# ===========================================
if [ $# -eq 0 ]; then
    error "Usage: $0 <backup_file.sql.gz> | --latest | --from-s3 <filename>"
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --latest)
            USE_LATEST=true
            shift
            ;;
        --from-s3)
            FROM_S3=true
            shift
            if [ $# -eq 0 ]; then
                error "--from-s3 requiert un nom de fichier"
            fi
            S3_FILENAME="$1"
            shift
            ;;
        *)
            BACKUP_FILE="$1"
            shift
            ;;
    esac
done

# ===========================================
# 1. Determiner fichier backup
# ===========================================
if [ "$USE_LATEST" = true ]; then
    log "Recherche du dernier backup local..."
    BACKUP_FILE=$(find "$BACKUP_DIR" -name "hub_chantier_backup_*.sql.gz" -type f | sort -r | head -n 1)
    if [ -z "$BACKUP_FILE" ]; then
        error "Aucun backup trouve dans $BACKUP_DIR"
    fi
    log "Dernier backup trouve: $BACKUP_FILE"
elif [ "$FROM_S3" = true ]; then
    if [ -z "${S3_BACKUP_BUCKET:-}" ]; then
        error "S3_BACKUP_BUCKET non defini dans $ENV_FILE"
    fi
    if ! command -v aws &> /dev/null; then
        error "AWS CLI non installe. Installation: pip3 install awscli"
    fi

    log "Telechargement depuis S3: s3://$S3_BACKUP_BUCKET/backups/$S3_FILENAME"

    AWS_ARGS=""
    if [ -n "${S3_ENDPOINT_URL:-}" ]; then
        AWS_ARGS="--endpoint-url $S3_ENDPOINT_URL"
    fi

    BACKUP_FILE="$BACKUP_DIR/$S3_FILENAME"
    if ! aws s3 cp $AWS_ARGS "s3://$S3_BACKUP_BUCKET/backups/$S3_FILENAME" "$BACKUP_FILE"; then
        error "Echec telechargement S3"
    fi
    log "Fichier telecharge: $BACKUP_FILE"
fi

# Verifier existence
if [ ! -f "$BACKUP_FILE" ]; then
    error "Fichier backup introuvable: $BACKUP_FILE"
fi

# Verifier extension
if [[ ! "$BACKUP_FILE" =~ \.(sql|sql\.gz)$ ]]; then
    error "Format invalide. Formats acceptes: .sql ou .sql.gz"
fi

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
log "Backup a restaurer: $BACKUP_FILE ($BACKUP_SIZE)"

# ===========================================
# 2. Verification Docker
# ===========================================
if ! command -v docker &> /dev/null; then
    error "Docker non installe"
fi

if ! docker compose -f "$PROJECT_DIR/$COMPOSE_FILE" --env-file "$ENV_FILE" ps db | grep -q "Up"; then
    error "Conteneur PostgreSQL non demarre"
fi

# ===========================================
# 3. Confirmation utilisateur
# ===========================================
echo ""
echo "=========================================="
echo "AVERTISSEMENT: RESTAURATION BASE DONNEES"
echo "=========================================="
echo ""
echo "  Base de donnees: $DB_NAME"
echo "  Fichier backup:  $BACKUP_FILE"
echo "  Taille:          $BACKUP_SIZE"
echo ""
echo "Cette operation va:"
echo "  1. Creer un backup de securite de la base actuelle"
echo "  2. ECRASER toutes les donnees de '$DB_NAME'"
echo "  3. Restaurer depuis le backup"
echo ""
read -p "Continuer? (tapez 'OUI' en majuscules pour confirmer): " CONFIRMATION

if [ "$CONFIRMATION" != "OUI" ]; then
    log "Restauration annulee par l'utilisateur"
    exit 0
fi

# ===========================================
# 4. Backup de securite avant restore
# ===========================================
log "Creation backup de securite avant restauration..."

SAFETY_BACKUP="$BACKUP_DIR/pre_restore_safety_$(date +%Y%m%d_%H%M%S).sql.gz"

if docker compose -f "$PROJECT_DIR/$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T db \
    pg_dump -U "$DB_USER" -d "$DB_NAME" 2>/dev/null | gzip > "$SAFETY_BACKUP"; then
    SAFETY_SIZE=$(du -h "$SAFETY_BACKUP" | cut -f1)
    log "Backup de securite cree: $SAFETY_BACKUP ($SAFETY_SIZE)"
else
    log "AVERTISSEMENT: Echec backup de securite (on continue quand meme)"
fi

# ===========================================
# 5. Restauration
# ===========================================
log "Restauration en cours..."

# Determiner si fichier compresse
if [[ "$BACKUP_FILE" =~ \.gz$ ]]; then
    CAT_CMD="gunzip -c"
else
    CAT_CMD="cat"
fi

# Restaurer
if $CAT_CMD "$BACKUP_FILE" | docker compose -f "$PROJECT_DIR/$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T db \
    psql -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; then
    log "Restauration reussie!"
else
    error "Echec restauration. Backup de securite disponible: $SAFETY_BACKUP"
fi

# ===========================================
# 6. Verification post-restauration
# ===========================================
log "Verification integrite base de donnees..."

TABLE_COUNT=$(docker compose -f "$PROJECT_DIR/$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T db \
    psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null | tr -d ' ')

if [ -n "$TABLE_COUNT" ] && [ "$TABLE_COUNT" -gt 0 ]; then
    log "Verification OK: $TABLE_COUNT tables trouvees"
else
    log "AVERTISSEMENT: Impossible de verifier le nombre de tables"
fi

# ===========================================
# 7. Resume
# ===========================================
echo ""
echo "=========================================="
echo "Restauration terminee avec succes"
echo "=========================================="
echo ""
log "  Source:          $BACKUP_FILE"
log "  Base de donnees: $DB_NAME"
log "  Tables:          $TABLE_COUNT"
log "  Backup securite: $SAFETY_BACKUP"
echo ""
log "Redemarrez l'application si necessaire:"
echo "  docker compose -f $COMPOSE_FILE --env-file $ENV_FILE restart api"
echo ""

exit 0
