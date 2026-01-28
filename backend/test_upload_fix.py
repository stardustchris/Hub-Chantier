#!/usr/bin/env python3
"""Test de l'upload après correction du bug DocumentDTO."""

import requests
import io

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("TEST UPLOAD - Après correction DocumentDTO")
print("=" * 60)

# 1. Login
print("\n📝 1. CONNEXION")
print("-" * 40)
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    data={"username": "test@test.fr", "password": "Test123!"}
)

if response.status_code != 200:
    print(f"❌ Login échoué ({response.status_code})")
    print(f"   Réponse: {response.text}")
    exit(1)

data = response.json()
token = data["access_token"]
user = data["user"]

print(f"✅ Login réussi!")
print(f"   Utilisateur: {user['prenom']} {user['nom']}")
print(f"   Email: {user['email']}")
print(f"   Rôle: {user['role']}")

headers = {"Authorization": f"Bearer {token}"}

# 2. Créer un fichier de test
print("\n📄 2. CRÉATION FICHIER DE TEST")
print("-" * 40)
test_content = b"Test upload after DocumentDTO fix - " + b"A" * 1000
test_file = io.BytesIO(test_content)
test_file.name = "test_upload_fix.txt"

print(f"✅ Fichier créé: {len(test_content)} bytes")

# 3. Upload du fichier vers dossier 1
print("\n⬆️  3. UPLOAD")
print("-" * 40)
files = {
    "file": ("test_upload_fix.txt", test_file, "text/plain")
}

response = requests.post(
    f"{BASE_URL}/api/documents/dossiers/1/documents?chantier_id=1",
    headers=headers,
    files=files
)

print(f"Status: {response.status_code}")
if response.status_code == 201:
    result = response.json()
    print(f"✅ Upload réussi!")
    print(f"   Document ID: {result['id']}")
    print(f"   Nom: {result['nom']}")
    print(f"   Taille: {result['taille_formatee']}")
    print(f"   Type: {result['type_document']}")

    doc_id = result['id']

    # 4. Test téléchargement
    print("\n🔽 4. TÉLÉCHARGEMENT")
    print("-" * 40)
    response = requests.get(
        f"{BASE_URL}/api/documents/{doc_id}/download",
        headers=headers,
        stream=True
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        content_length = response.headers.get('content-length', 'unknown')
        content_type = response.headers.get('content-type', 'unknown')

        print(f"✅ Téléchargement OK!")
        print(f"   Content-Length: {content_length} bytes")
        print(f"   Content-Type: {content_type}")

        # Vérifier le contenu
        downloaded = response.content
        if downloaded == test_content:
            print(f"✅ Contenu vérifié: identique au fichier uploadé!")
        else:
            print(f"⚠️  Contenu différent!")
            print(f"   Attendu: {len(test_content)} bytes")
            print(f"   Reçu: {len(downloaded)} bytes")
    else:
        print(f"❌ Échec téléchargement")
        print(f"   Réponse: {response.text[:200]}")

elif response.status_code == 400:
    print(f"❌ Erreur de validation")
    print(f"   Réponse: {response.json()}")
elif response.status_code == 404:
    print(f"❌ Dossier non trouvé")
    print(f"   Réponse: {response.json()}")
else:
    print(f"❌ Erreur upload")
    print(f"   Réponse: {response.text[:500]}")

print("\n" + "=" * 60)
print("FIN DES TESTS")
print("=" * 60)
