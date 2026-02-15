#!/bin/bash
# Script de génération automatique de types TypeScript depuis le schéma OpenAPI
# Usage: ./scripts/generate-api-types.sh
# Ou depuis le frontend: npm run generate:types

set -e  # Arrêt immédiat en cas d'erreur

# ===== CONFIGURATION =====
API_URL="http://localhost:8000"
OPENAPI_ENDPOINT="${API_URL}/openapi.json"
OUTPUT_FILE="./frontend/src/types/generated/api.ts"
TEMP_SCHEMA="/tmp/hub-chantier-openapi.json"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ===== FONCTIONS =====
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ===== VÉRIFICATIONS =====
log_info "Vérification de l'environnement..."

# 1. Vérifier que l'API est accessible
if ! curl -s -f "${API_URL}/api/health" > /dev/null 2>&1; then
    log_error "L'API n'est pas accessible à ${API_URL}"
    log_error "Vérifiez que Docker Compose est démarré:"
    echo ""
    echo "  docker compose up -d"
    echo "  docker compose ps"
    echo ""
    exit 1
fi

log_success "API accessible à ${API_URL}"

# 2. Vérifier que le dossier frontend existe
if [ ! -d "${PROJECT_ROOT}/frontend" ]; then
    log_error "Le dossier frontend n'existe pas: ${PROJECT_ROOT}/frontend"
    exit 1
fi

# 3. Vérifier que openapi-typescript est installé
if [ ! -f "${PROJECT_ROOT}/frontend/node_modules/.bin/openapi-typescript" ]; then
    log_error "openapi-typescript n'est pas installé"
    log_error "Exécutez: cd frontend && npm install --save-dev openapi-typescript"
    exit 1
fi

log_success "Dépendances vérifiées"

# ===== GÉNÉRATION =====
log_info "Téléchargement du schéma OpenAPI depuis ${OPENAPI_ENDPOINT}..."

# Télécharger le schéma OpenAPI
if ! curl -s -f "${OPENAPI_ENDPOINT}" -o "${TEMP_SCHEMA}"; then
    log_error "Impossible de télécharger le schéma OpenAPI"
    exit 1
fi

# Vérifier que le fichier téléchargé est valide
if ! jq empty "${TEMP_SCHEMA}" 2>/dev/null; then
    log_error "Le schéma téléchargé n'est pas un JSON valide"
    cat "${TEMP_SCHEMA}"
    rm -f "${TEMP_SCHEMA}"
    exit 1
fi

log_success "Schéma OpenAPI téléchargé ($(du -h "${TEMP_SCHEMA}" | cut -f1))"

# Créer le dossier de sortie si nécessaire
mkdir -p "$(dirname "${PROJECT_ROOT}/${OUTPUT_FILE}")"

log_info "Génération des types TypeScript..."

# Générer les types TypeScript
cd "${PROJECT_ROOT}/frontend"
npx openapi-typescript "${TEMP_SCHEMA}" \
    --output "${PROJECT_ROOT}/${OUTPUT_FILE}" \
    --additional-properties=alphabetize \
    2>&1 | grep -v "Warning: using --additional-properties" || true

if [ ! -f "${PROJECT_ROOT}/${OUTPUT_FILE}" ]; then
    log_error "La génération a échoué: fichier de sortie manquant"
    rm -f "${TEMP_SCHEMA}"
    exit 1
fi

# Nettoyer le fichier temporaire
rm -f "${TEMP_SCHEMA}"

# ===== RÉSUMÉ =====
log_success "Types générés avec succès!"
echo ""
log_info "Résumé:"

# Compter les types générés (approximatif via nombre de 'interface' et 'type' dans le fichier)
INTERFACE_COUNT=$(grep -c "^export interface" "${PROJECT_ROOT}/${OUTPUT_FILE}" || echo 0)
TYPE_COUNT=$(grep -c "^export type" "${PROJECT_ROOT}/${OUTPUT_FILE}" || echo 0)
FILE_SIZE=$(du -h "${PROJECT_ROOT}/${OUTPUT_FILE}" | cut -f1)
LINES=$(wc -l < "${PROJECT_ROOT}/${OUTPUT_FILE}")

echo "  - Fichier: ${OUTPUT_FILE}"
echo "  - Taille: ${FILE_SIZE} (${LINES} lignes)"
echo "  - Interfaces: ${INTERFACE_COUNT}"
echo "  - Types: ${TYPE_COUNT}"
echo ""
log_warning "NE MODIFIEZ PAS ce fichier manuellement!"
log_info "Pour regénérer: npm run generate:types (depuis le dossier frontend)"
echo ""
