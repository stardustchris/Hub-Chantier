#!/bin/bash
# =====================================================
# Hub Chantier - Backup PostgreSQL automatise
# =====================================================
# Usage:
#   ./scripts/backup.sh                 # Backup local uniquement
#   ./scripts/backup.sh --upload-s3     # Backup + upload S3
#
# Configuration S3 (optionnelle):
#   Definir dans .env.production:
#     S3_BACKUP_BUCKET=mon-bucket-backup
#     AWS_ACCESS_KEY_ID=...
#     AWS_SECRET_ACCESS_KEY=...
#     AWS_DEFAULT_REGION=fr-par (pour Scaleway Object Storage)
#     S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud (optionnel, pour Scaleway)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-$PROJECT_DIR/.env.production}"

# Charger variables d'environnement si disponibles
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/var/backups/hub-chantier}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILENAME="hub_chantier_backup_${TIMESTAMP}.sql.gz"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILENAME"
DB_NAME="${POSTGRES_DB:-hub_chantier}"
DB_USER="${POSTGRES_USER:-hubchantier}"
UPLOAD_S3=false

# Logger
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

error() {
    log "ERREUR: $*" >&2
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --upload-s3)
            UPLOAD_S3=true
            shift
            ;;
        *)
            error "Argument inconnu: $1"
            ;;
    esac
done

# ===========================================
# 1. Verifications
# ===========================================
log "Demarrage backup PostgreSQL..."

if ! command -v docker &> /dev/null; then
    error "Docker non installe"
fi

if ! docker compose -f "$PROJECT_DIR/$COMPOSE_FILE" --env-file "$ENV_FILE" ps db | grep -q "Up"; then
    error "Conteneur PostgreSQL non demarre"
fi

# Creer repertoire backup si necessaire
mkdir -p "$BACKUP_DIR"

# ===========================================
# 2. Execution pg_dump
# ===========================================
log "Creation du backup: $BACKUP_FILENAME"

if docker compose -f "$PROJECT_DIR/$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T db \
    pg_dump -U "$DB_USER" -d "$DB_NAME" \
    --verbose \
    --format=plain \
    --no-owner \
    --no-acl \
    2>/dev/null | gzip > "$BACKUP_PATH"; then

    BACKUP_SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
    log "Backup cree avec succes: $BACKUP_PATH ($BACKUP_SIZE)"
else
    error "Echec pg_dump"
fi

# Verifier taille minimum (securite)
BACKUP_SIZE_BYTES=$(stat -f%z "$BACKUP_PATH" 2>/dev/null || stat -c%s "$BACKUP_PATH" 2>/dev/null || echo "0")
if [ "$BACKUP_SIZE_BYTES" -lt 1024 ]; then
    error "Backup trop petit ($BACKUP_SIZE_BYTES octets) - possible corruption"
fi

# ===========================================
# 3. Rotation locale (garder N derniers jours)
# ===========================================
log "Rotation backups (conservation: $RETENTION_DAYS jours)"

# Compter backups avant rotation
BACKUP_COUNT_BEFORE=$(find "$BACKUP_DIR" -name "hub_chantier_backup_*.sql.gz" -type f | wc -l | tr -d ' ')

# Supprimer backups anciens
find "$BACKUP_DIR" -name "hub_chantier_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

# Compter apres rotation
BACKUP_COUNT_AFTER=$(find "$BACKUP_DIR" -name "hub_chantier_backup_*.sql.gz" -type f | wc -l | tr -d ' ')
DELETED=$((BACKUP_COUNT_BEFORE - BACKUP_COUNT_AFTER))

if [ "$DELETED" -gt 0 ]; then
    log "Supprimes: $DELETED ancien(s) backup(s)"
fi
log "Backups locaux actuels: $BACKUP_COUNT_AFTER"

# ===========================================
# 4. Upload S3 (optionnel)
# ===========================================
if [ "$UPLOAD_S3" = true ]; then
    if [ -z "${S3_BACKUP_BUCKET:-}" ]; then
        log "AVERTISSEMENT: S3_BACKUP_BUCKET non defini, skip upload S3"
    elif ! command -v aws &> /dev/null; then
        log "AVERTISSEMENT: AWS CLI non installe, skip upload S3"
        log "  Installation: pip3 install awscli"
    else
        log "Upload vers S3: s3://$S3_BACKUP_BUCKET/"

        AWS_ARGS=""
        if [ -n "${S3_ENDPOINT_URL:-}" ]; then
            AWS_ARGS="--endpoint-url $S3_ENDPOINT_URL"
        fi

        if aws s3 cp $AWS_ARGS "$BACKUP_PATH" "s3://$S3_BACKUP_BUCKET/backups/$(basename "$BACKUP_PATH")"; then
            log "Upload S3 reussi"

            # Rotation S3 (garder meme duree)
            CUTOFF_DATE=$(date -d "$RETENTION_DAYS days ago" +%Y%m%d 2>/dev/null || date -v-${RETENTION_DAYS}d +%Y%m%d 2>/dev/null)

            aws s3 ls $AWS_ARGS "s3://$S3_BACKUP_BUCKET/backups/" | \
            awk '{print $4}' | \
            grep -E "hub_chantier_backup_[0-9]{8}_[0-9]{6}\.sql\.gz" | \
            while read -r file; do
                FILE_DATE=$(echo "$file" | grep -oE "[0-9]{8}" | head -1)
                if [ "$FILE_DATE" -lt "$CUTOFF_DATE" ]; then
                    log "Suppression S3: $file"
                    aws s3 rm $AWS_ARGS "s3://$S3_BACKUP_BUCKET/backups/$file"
                fi
            done
        else
            log "AVERTISSEMENT: Echec upload S3 (backup local conserve)"
        fi
    fi
fi

# ===========================================
# 5. Resume
# ===========================================
log "Backup termine avec succes"
log "  Fichier: $BACKUP_PATH"
log "  Taille:  $BACKUP_SIZE"
log "  Backups locaux: $BACKUP_COUNT_AFTER"

exit 0
