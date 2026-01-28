#!/usr/bin/env python3
"""Test de l'API - Login et téléchargement."""

import requests

BASE_URL = "http://localhost:8000"

# 1. Login
print("📝 Connexion...")
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    data={"username": "admin@hubchantier.fr", "password": "Password123!"}
)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✅ Token récupéré: {token[:50]}...")

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Liste des chantiers
    print("\n📋 Chantiers:")
    response = requests.get(f"{BASE_URL}/api/chantiers", headers=headers)
    if response.status_code == 200:
        chantiers = response.json()
        print(f"✅ {len(chantiers.get('items', []))} chantiers trouvés")
        if chantiers.get('items'):
            print(f"   Premier: {chantiers['items'][0]['code']} - {chantiers['items'][0]['nom']}")

    # 3. Arborescence
    print("\n📁 Arborescence chantier 1:")
    response = requests.get(f"{BASE_URL}/api/documents/arborescence", params={"chantier_id": 1}, headers=headers)
    if response.status_code == 200:
        arbo = response.json()
        print(f"✅ {len(arbo.get('dossiers', []))} dossiers")
        for dossier in arbo.get('dossiers', []):
            print(f"   - {dossier['nom']} (id={dossier['id']})")
    elif response.status_code == 404:
        print("⚠️  Arborescence non trouvée (normal si pas encore créée)")
    else:
        print(f"❌ Erreur: {response.status_code} - {response.text}")

    # 4. Documents du dossier 1
    print("\n📄 Documents du dossier 1:")
    response = requests.get(f"{BASE_URL}/api/documents", params={"dossier_id": 1}, headers=headers)
    if response.status_code == 200:
        docs = response.json()
        print(f"✅ {len(docs.get('documents', []))} documents")
        for doc in docs.get('documents', []):
            print(f"   - {doc['nom']} ({doc['taille_formatee']})")
    else:
        print(f"❌ Erreur: {response.status_code} - {response.text}")

else:
    print(f"❌ Login échoué: {response.text}")
