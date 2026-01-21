#!/bin/bash
# Script de génération d'un nouveau module Clean Architecture

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <nom_module>"
    echo "Exemple: $0 pointages"
    exit 1
fi

MODULE_NAME=$1
MODULE_PATH="backend/modules/$MODULE_NAME"

# Vérifier si le module existe déjà
if [ -d "$MODULE_PATH" ]; then
    echo "Erreur: Le module '$MODULE_NAME' existe déjà"
    exit 1
fi

echo "Création du module: $MODULE_NAME"

# Créer la structure
mkdir -p "$MODULE_PATH"/{domain/{entities,value_objects,repositories,events,services},application/{use_cases,dtos,ports},adapters/{controllers,presenters,providers},infrastructure/{persistence,web}}

# Créer les fichiers __init__.py
find "$MODULE_PATH" -type d -exec touch {}/__init__.py \;

# Créer le __init__.py principal du module
cat > "$MODULE_PATH/__init__.py" << EOF
"""Module $MODULE_NAME.

Ce module suit Clean Architecture avec 4 layers :
- domain/      : Entités, Value Objects, Interfaces (PURE)
- application/ : Use Cases, DTOs, Ports
- adapters/    : Controllers, Providers
- infrastructure/ : SQLAlchemy, FastAPI
"""
EOF

# Créer le __init__.py du domain
cat > "$MODULE_PATH/domain/__init__.py" << EOF
"""Domain Layer du module $MODULE_NAME.

RÈGLE : Aucune dépendance vers des frameworks externes.
"""
EOF

# Créer le __init__.py de l'application
cat > "$MODULE_PATH/application/__init__.py" << EOF
"""Application Layer du module $MODULE_NAME.

RÈGLE : Dépend uniquement du Domain, pas de l'Infrastructure.
"""
EOF

# Créer le __init__.py des adapters
cat > "$MODULE_PATH/adapters/__init__.py" << EOF
"""Adapters Layer du module $MODULE_NAME.

RÈGLE : Dépend de Application et Domain, pas directement de l'Infrastructure.
"""
EOF

# Créer le __init__.py de l'infrastructure
cat > "$MODULE_PATH/infrastructure/__init__.py" << EOF
"""Infrastructure Layer du module $MODULE_NAME.

RÈGLE : Cette couche dépend de toutes les autres.
"""
EOF

# Créer le dossier de tests
mkdir -p "backend/tests/unit/$MODULE_NAME"
touch "backend/tests/unit/$MODULE_NAME/__init__.py"

echo ""
echo "Module '$MODULE_NAME' créé avec succès !"
echo ""
echo "Structure créée:"
find "$MODULE_PATH" -type d | sed 's/^/  /'
echo ""
echo "Prochaines étapes:"
echo "  1. Créer les entités dans domain/entities/"
echo "  2. Créer les use cases dans application/use_cases/"
echo "  3. Écrire les tests dans tests/unit/$MODULE_NAME/"
echo "  4. Créer l'infrastructure (repository, routes)"
echo ""
echo "Référez-vous au module 'auth' comme exemple."
