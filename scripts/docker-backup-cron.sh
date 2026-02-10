#!/bin/bash
# =====================================================
# Hub Chantier - Backup Cron (pour conteneur Docker)
# =====================================================
# Ce script est execute par cron dans le conteneur backup-cron
# Il lance le backup et gere les logs

set -euo pipefail

# Configuration
LOG_FILE="/var/log/hub-chantier-backup.log"
MAX_LOG_SIZE_MB=10

# Rotation log si trop gros
if [ -f "$LOG_FILE" ]; then
    LOG_SIZE_KB=$(du -k "$LOG_FILE" | cut -f1)
    LOG_SIZE_MB=$((LOG_SIZE_KB / 1024))
    if [ "$LOG_SIZE_MB" -gt "$MAX_LOG_SIZE_MB" ]; then
        mv "$LOG_FILE" "$LOG_FILE.old"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Log rotate (ancien: $LOG_FILE.old)" > "$LOG_FILE"
    fi
fi

# Executer backup avec log
echo "==================================================" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Demarrage backup automatique" >> "$LOG_FILE"
echo "==================================================" >> "$LOG_FILE"

if /scripts/backup.sh --upload-s3 >> "$LOG_FILE" 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup termine avec succes" >> "$LOG_FILE"
    exit 0
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERREUR: Echec backup" >> "$LOG_FILE"
    exit 1
fi
