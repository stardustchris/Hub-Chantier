#!/usr/bin/env python3
"""Test complet: Login, Upload, Download."""

import requests
import os

BASE_URL = "http://localhost:8000"

print("="*60)
print("TEST COMPLET - Hub Chantier")
print("="*60)

# 1. Login
print("\n📝 1. CONNEXION")
print("-" * 40)
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    data={"username": "admin@hubchantier.fr", "password": "Password123!"}
)

if response.status_code != 200:
    print(f"❌ Login échoué ({response.status_code})")
    print(f"   Réponse: {response.text}")
    print("\n⚠️  Vérifiez que l'utilisateur existe et que le mot de passe est correct")
    exit(1)

data = response.json()
token = data["access_token"]
user = data["user"]

print(f"✅ Login réussi!")
print(f"   Utilisateur: {user['prenom']} {user['nom']}")
print(f"   Email: {user['email']}")
print(f"   Rôle: {user['role']}")
print(f"   Token: {token[:30]}...")

headers = {"Authorization": f"Bearer {token}"}

# 2. Vérifier les chantiers
print("\n📋 2. CHANTIERS")
print("-" * 40)
response = requests.get(f"{BASE_URL}/api/chantiers", headers=headers)
if response.status_code == 200:
    chantiers = response.json()
    print(f"✅ {len(chantiers.get('items', []))} chantiers trouvés")
    if chantiers.get('items'):
        chantier = chantiers['items'][0]
        print(f"   #{chantier['id']}: {chantier['code']} - {chantier['nom']}")
        chantier_id = chantier['id']
    else:
        print("⚠️  Aucun chantier, création nécessaire")
        chantier_id = 1
else:
    print(f"❌ Erreur chantiers: {response.status_code}")
    chantier_id = 1

# 3. Arborescence
print("\n📁 3. ARBORESCENCE")
print("-" * 40)
response = requests.get(
    f"{BASE_URL}/api/documents/arborescence",
    params={"chantier_id": chantier_id},
    headers=headers
)

if response.status_code == 200:
    arbo = response.json()
    nb_dossiers = len(arbo.get('dossiers', []))
    print(f"✅ Arborescence récupérée: {nb_dossiers} dossiers")

    if arbo.get('dossiers'):
        for dossier in arbo['dossiers'][:3]:
            print(f"   - {dossier['nom']} (id={dossier['id']}, accès={dossier['niveau_acces']})")
        dossier_id = arbo['dossiers'][0]['id']
    else:
        print("⚠️  Pas de dossiers dans l'arborescence")
        dossier_id = 1
else:
    print(f"❌ Erreur arborescence: {response.status_code}")
    dossier_id = 1

# 4. Documents existants
print("\n📄 4. DOCUMENTS EXISTANTS")
print("-" * 40)
response = requests.get(
    f"{BASE_URL}/api/documents",
    params={"dossier_id": dossier_id},
    headers=headers
)

if response.status_code == 200:
    docs = response.json()
    nb_docs = len(docs.get('documents', []))
    print(f"✅ {nb_docs} documents dans le dossier #{dossier_id}")

    if docs.get('documents'):
        for doc in docs['documents'][:3]:
            print(f"   - {doc['nom']} ({doc['taille_formatee']})")
            print(f"     ID: {doc['id']}, Mime: {doc['mime_type']}")

        # Test de téléchargement
        doc_id = docs['documents'][0]['id']
        doc_nom = docs['documents'][0]['nom']

        print(f"\n🔽 Test téléchargement: {doc_nom}")
        response = requests.get(
            f"{BASE_URL}/api/documents/{doc_id}/download",
            headers=headers,
            stream=True
        )

        if response.status_code == 200:
            content_length = response.headers.get('content-length', 'unknown')
            content_type = response.headers.get('content-type', 'unknown')
            content_disp = response.headers.get('content-disposition', 'unknown')

            print(f"✅ Téléchargement OK!")
            print(f"   Content-Length: {content_length} bytes")
            print(f"   Content-Type: {content_type}")
            print(f"   Content-Disposition: {content_disp}")
        else:
            print(f"❌ Échec téléchargement: {response.status_code}")
            print(f"   {response.text[:200]}")
    else:
        print("⚠️  Aucun document pour tester le téléchargement")
else:
    print(f"❌ Erreur documents: {response.status_code}")

print("\n" + "="*60)
print("FIN DES TESTS")
print("="*60)
