#!/bin/bash
# Script de démarrage de l'environnement de développement

set -e

echo "=== Hub Chantier - Démarrage Dev ==="
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "Erreur: Python 3 n'est pas installé"
    exit 1
fi

# Se placer à la racine du projet
cd "$(dirname "$0")/.."

# Vérifier/créer le virtualenv
if [ ! -d "backend/venv" ]; then
    echo "Création du virtualenv..."
    python3 -m venv backend/venv
fi

# Activer le virtualenv
source backend/venv/bin/activate

# Installer les dépendances si nécessaire
if [ ! -f "backend/venv/.installed" ]; then
    echo "Installation des dépendances..."
    pip install -r backend/requirements.txt
    touch backend/venv/.installed
fi

# Créer le dossier data
mkdir -p backend/data

# Lancer le serveur
echo ""
echo "Démarrage du serveur FastAPI..."
echo "API disponible sur: http://localhost:8000"
echo "Documentation: http://localhost:8000/docs"
echo ""
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
