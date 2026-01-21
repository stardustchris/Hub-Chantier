#!/bin/bash
# Script de vérification de l'architecture Clean

set -e

echo "=== Vérification de l'architecture Clean ==="
echo ""

ERRORS=0
WARNINGS=0

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher une erreur
error() {
    echo -e "${RED}[ERREUR]${NC} $1"
    ((ERRORS++))
}

# Fonction pour afficher un warning
warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    ((WARNINGS++))
}

# Fonction pour afficher un succès
success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

# Vérification 1: Pas d'imports interdits dans domain/
echo "1. Vérification des imports dans domain/..."
FORBIDDEN_IMPORTS="fastapi|sqlalchemy|pydantic|requests|httpx"
DOMAIN_VIOLATIONS=$(grep -rn "from ${FORBIDDEN_IMPORTS}\|import ${FORBIDDEN_IMPORTS}" backend/modules/*/domain/ 2>/dev/null || true)

if [ -n "$DOMAIN_VIOLATIONS" ]; then
    error "Imports interdits trouvés dans domain/:"
    echo "$DOMAIN_VIOLATIONS"
else
    success "Aucun import interdit dans domain/"
fi

# Vérification 2: Use cases ne doivent pas importer directement de l'infrastructure
echo ""
echo "2. Vérification des imports dans application/use_cases/..."
INFRA_IN_USECASES=$(grep -rn "from.*infrastructure" backend/modules/*/application/use_cases/ 2>/dev/null || true)

if [ -n "$INFRA_IN_USECASES" ]; then
    error "Import direct d'infrastructure dans use_cases:"
    echo "$INFRA_IN_USECASES"
else
    success "Aucun import d'infrastructure dans use_cases/"
fi

# Vérification 3: Pas d'import direct entre modules (sauf events)
echo ""
echo "3. Vérification des imports inter-modules..."
INTER_MODULE_IMPORTS=$(grep -rn "from modules\." backend/modules/ 2>/dev/null | grep -v "domain/events" | grep -v "__pycache__" || true)

if [ -n "$INTER_MODULE_IMPORTS" ]; then
    warning "Imports inter-modules trouvés (vérifier qu'ils sont via events):"
    echo "$INTER_MODULE_IMPORTS"
else
    success "Pas d'import direct inter-modules suspect"
fi

# Vérification 4: Chaque use case a ses tests
echo ""
echo "4. Vérification des tests unitaires..."
for use_case_dir in backend/modules/*/application/use_cases/; do
    module=$(echo "$use_case_dir" | cut -d'/' -f3)

    # Compter les use cases (fichiers .py qui ne sont pas __init__)
    use_case_count=$(find "$use_case_dir" -name "*.py" ! -name "__init__.py" 2>/dev/null | wc -l)

    # Compter les tests
    test_dir="backend/tests/unit/$module/"
    if [ -d "$test_dir" ]; then
        test_count=$(find "$test_dir" -name "test_*.py" 2>/dev/null | wc -l)
    else
        test_count=0
    fi

    if [ "$use_case_count" -gt 0 ] && [ "$test_count" -eq 0 ]; then
        warning "Module $module: $use_case_count use cases, $test_count tests"
    elif [ "$use_case_count" -gt 0 ]; then
        success "Module $module: $use_case_count use cases, $test_count tests"
    fi
done

# Vérification 5: Structure des modules
echo ""
echo "5. Vérification de la structure des modules..."
REQUIRED_DIRS="domain application adapters infrastructure"

for module_dir in backend/modules/*/; do
    module=$(basename "$module_dir")
    if [ "$module" == "__pycache__" ]; then
        continue
    fi

    for dir in $REQUIRED_DIRS; do
        if [ ! -d "${module_dir}${dir}" ]; then
            error "Module $module: dossier $dir manquant"
        fi
    done
done

success "Structure des modules vérifiée"

# Résumé
echo ""
echo "=== Résumé ==="
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}$ERRORS erreur(s) trouvée(s)${NC}"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}$WARNINGS warning(s) trouvé(s)${NC}"
    exit 0
else
    echo -e "${GREEN}Architecture OK !${NC}"
    exit 0
fi
