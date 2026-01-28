#!/bin/bash
# Test de connexion et récupération du token

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hubchantier.fr","password":"admin123"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $TOKEN"

# Tester la liste des chantiers
echo -e "\nChantiers:"
curl -s http://localhost:8000/api/chantiers \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -30

# Tester l'arborescence
echo -e "\nArborescence chantier 1:"
curl -s "http://localhost:8000/api/documents/arborescence?chantier_id=1" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
