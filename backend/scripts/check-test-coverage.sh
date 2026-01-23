#!/bin/bash
# Script de verification de la couverture des tests
# A executer avant chaque commit pour verifier qu'aucun test ne manque

set -e

echo "=== Verification de la couverture des tests ==="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Modules backend complets (avec API REST)
COMPLETE_MODULES=("auth" "dashboard" "chantiers" "planning" "pointages" "taches")

# Verification des tests d'integration API
echo "1. Verification des tests d'integration API..."
echo "   ================================================"
MISSING_INTEGRATION=()

for module in "${COMPLETE_MODULES[@]}"; do
    # Nom du fichier de test attendu
    if [ "$module" == "auth" ]; then
        TEST_FILE="tests/integration/test_auth_api.py"
    elif [ "$module" == "pointages" ]; then
        TEST_FILE="tests/integration/test_pointages_api.py"
    else
        TEST_FILE="tests/integration/test_${module}_api.py"
    fi

    if [ -f "$TEST_FILE" ]; then
        echo -e "   ${GREEN}[OK]${NC} $module -> $TEST_FILE"
    else
        echo -e "   ${RED}[MANQUANT]${NC} $module -> $TEST_FILE"
        MISSING_INTEGRATION+=("$module")
    fi
done

echo ""

# Verification des tests unitaires par module
echo "2. Verification des tests unitaires..."
echo "   ===================================="

MISSING_UNIT=()

for module in "${COMPLETE_MODULES[@]}"; do
    MODULE_DIR="tests/unit/$module"

    if [ -d "$MODULE_DIR" ]; then
        TEST_COUNT=$(find "$MODULE_DIR" -name "test_*.py" | wc -l)
        if [ "$TEST_COUNT" -gt 0 ]; then
            echo -e "   ${GREEN}[OK]${NC} $module -> $TEST_COUNT fichiers de test"
        else
            echo -e "   ${YELLOW}[VIDE]${NC} $module -> Dossier existe mais pas de tests"
            MISSING_UNIT+=("$module")
        fi
    else
        echo -e "   ${RED}[MANQUANT]${NC} $module -> $MODULE_DIR n'existe pas"
        MISSING_UNIT+=("$module")
    fi
done

echo ""

# Execution des tests pour verifier qu'ils passent
echo "3. Execution des tests..."
echo "   ======================"

if python -m pytest tests/ -q --tb=no 2>/dev/null; then
    PASSED=$(python -m pytest tests/ -q --tb=no 2>&1 | tail -1)
    echo -e "   ${GREEN}[OK]${NC} $PASSED"
else
    echo -e "   ${RED}[ECHEC]${NC} Certains tests echouent!"
    echo "   Executez: python -m pytest tests/ -v pour plus de details"
fi

echo ""

# Resume
echo "=== RESUME ==="
echo ""

if [ ${#MISSING_INTEGRATION[@]} -eq 0 ] && [ ${#MISSING_UNIT[@]} -eq 0 ]; then
    echo -e "${GREEN}Tous les tests requis sont presents!${NC}"
    exit 0
else
    if [ ${#MISSING_INTEGRATION[@]} -gt 0 ]; then
        echo -e "${RED}Tests d'integration manquants:${NC}"
        for module in "${MISSING_INTEGRATION[@]}"; do
            echo "  - $module (creer tests/integration/test_${module}_api.py)"
        done
    fi

    if [ ${#MISSING_UNIT[@]} -gt 0 ]; then
        echo -e "${YELLOW}Tests unitaires incomplets:${NC}"
        for module in "${MISSING_UNIT[@]}"; do
            echo "  - $module"
        done
    fi

    echo ""
    echo -e "${RED}ATTENTION: Ne pas committer avant d'avoir ajoute les tests manquants!${NC}"
    exit 1
fi
